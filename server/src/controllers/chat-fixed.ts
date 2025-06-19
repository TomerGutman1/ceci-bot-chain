import {
  ResponseFunctionToolCall,
  ResponseOutputMessage,
  ResponseStreamEvent} from 'openai/resources/responses/responses'
import { Request, Response, NextFunction } from 'express'
import { callFunction, getAssistantResponse } from '../api/openai'
import { ChatEvent, ChatEventType, OpenAIEventType } from '../types/streams'
import { Stream } from 'openai/streaming'

export const chatController = async (
  req: Request,
  res: Response,
  next: NextFunction,
) => {
  console.log('\n🔴🔴🔴 CHAT CONTROLLER CALLED 🔴🔴🔴');
  console.log('Time:', new Date().toISOString());
  console.log('Message:', req.body.newMessageContent);
  console.log('🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴\n');
  
  const { newMessageContent, conversationId } = req.body as {
    conversationId: string
    newMessageContent: string
  }

  const responseStream = await getAssistantResponse({
    newInput: [{ role: 'user', content: newMessageContent }],
    promptId: 'ASSISTANT_PROMPT',
    conversationId,
  })

  res.setHeader('Content-Type', 'application/jsonl; charset=utf-8')
  res.setHeader('Cache-Control', 'no-cache')
  
  await processLlmResponse(req, res, next, responseStream)
  
  res.end()
}

async function processLlmResponse(
  req: Request,
  res: Response,
  next: NextFunction,
  responseStream: Stream<ResponseStreamEvent>,
) {
  const chunkPromises = []
  try {
    for await (const responsePart of responseStream) {
      chunkPromises.push(processChunk(responsePart))
    }
    await Promise.all(chunkPromises)
  } catch (error) {
    next(error)
  }

  async function processChunk(responsePart: ResponseStreamEvent): Promise<boolean> {
    return new Promise(async (resolve) => {
      let chatEvent: ChatEvent
      let message: ResponseOutputMessage
      let evaluation: string | undefined
      let error: Error | undefined
      let toolCall: ResponseFunctionToolCall
  
      const streamResult = (obj: Object) => {
        res.write(JSON.stringify(obj) + '\n')
      }
  
      switch (responsePart.type) {
        case OpenAIEventType.ResponseCreated:
          req.body.conversationId = responsePart.response.id
          chatEvent = {
            type: ChatEventType.MessageCreated,
            conversationId: req.body.conversationId,
          }
          streamResult(chatEvent)
          break
        case OpenAIEventType.ResponseOutputItemAdded:
          if (responsePart.item.type === 'function_call') {
            toolCall = responsePart.item as ResponseFunctionToolCall
            // FOR SEARCH_DECISIONS - Don't show "evaluating" message
            if (toolCall.name !== 'search_decisions') {
              chatEvent = {
                type: ChatEventType.MessageAdded,
                message: {
                  id: toolCall.call_id,
                  role: 'assistant',
                  content: 'רק רגע, אני מנסה להעריך את ההחלטה ששלחת לי',
                },
              }
              streamResult(chatEvent)
            }
          } else if (responsePart.item.type === 'message') {
            message = responsePart.item as ResponseOutputMessage
            chatEvent = {
              type: ChatEventType.MessageAdded,
              message: {
                id: message.id,
                role: message.role,
                content: message.content.join(),
              },
            }
            streamResult(chatEvent)
          }
          break
        case OpenAIEventType.ResponseOutputTextDelta:
          chatEvent = {
            type: ChatEventType.MessageDelta,
            delta: responsePart.delta,
          }
          streamResult(chatEvent)
          break
        case OpenAIEventType.ResponseOutputTextDone:
          chatEvent = {
            type: ChatEventType.MessageCompleted,
            text: responsePart.text,
          }
          streamResult(chatEvent)
          break
        case OpenAIEventType.ResponseOutputItemDone:
          if (responsePart.item.type === 'function_call') {
            try {
              toolCall = responsePart.item as ResponseFunctionToolCall
              
              // Parse arguments & Evaluate decision
              [error, evaluation] = await callFunction(toolCall)
              if (error) {
                next(error)
                break
              }
              
              // DON'T send the raw tool response directly!
              // Instead, let the Assistant format it nicely
              
              const inputs = [
                {
                  type: 'function_call_output' as const,
                  call_id: toolCall.call_id,
                  output: evaluation as string,
                },
              ]
              const assistantRes = await getAssistantResponse({
                newInput: inputs,
                promptId: 'ASSISTANT_PROMPT',
                conversationId: req.body.conversationId,
              })
              
              // Process the Assistant's formatted response
              await processLlmResponse(req, res, next, assistantRes)
            } catch (error) {
              next(error)
            }
          }
          break
        // case 'response.completed':
        // has a lot of data
      }
      resolve(true)
    })
  }
}
