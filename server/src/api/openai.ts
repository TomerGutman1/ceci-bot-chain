import OpenAI from 'openai'
import { Stream } from 'openai/streaming'
import { getAssistantConfig, getEvaluatorConfig } from '../llms/configs'
import { LLMReqParams } from '../types/prompts'
import { ResponseFunctionToolCall } from 'openai/resources/responses/responses'
import { ToolName } from '../llms/tools'

const openai = new OpenAI()

export async function getAssistantResponse(
  llmReqParams: LLMReqParams,
): Promise<Stream<OpenAI.Responses.ResponseStreamEvent>> {
  const promptConfig = getAssistantConfig(llmReqParams)
  console.log('[OpenAI] Assistant request with tools:', promptConfig.tools?.map(t => (t as any).function?.name || 'unknown'));
  console.log('[OpenAI] User message:', llmReqParams.newInput);
  const result = await openai.responses.create(promptConfig)

  return result
}

export async function getEvaluatorResponse(
  llmReqParams: LLMReqParams,
): Promise<OpenAI.Responses.Response> {
  const promptConfig = getEvaluatorConfig(llmReqParams)
  const result = await openai.responses.create(promptConfig)

  return result
}

export async function callFunction(
  toolCall: ResponseFunctionToolCall,
): Promise<[Error] | [undefined, string]> {
  try {
    const toolName = toolCall.name as ToolName;
    const toolArgs = JSON.parse(toolCall.arguments);
    
    console.log('\n========== TOOL CALL ==========');
    console.log('[callFunction] Tool name:', toolName);
    console.log('[callFunction] Tool args:', toolArgs);
    console.log('===============================\n');
    
    // Handle search_decisions tool - NOT SUPPORTED ANYMORE
    if (toolName === 'search_decisions') {
      return [undefined, 'חיפוש החלטות נעשה כעת דרך PandasAI. אנא השתמש בממשק הצ\'אט הראשי.'];
    }

    // Handle evaluation tools (existing code)
    if (toolName === 'evaluate_existing_decision') {
      // Search for evaluation via decision & gov number
      // If exists - return existing evaluation
      // Else -
      // Evaluate decision, return it
      // return
    }
  
    // Else - evaluate draft and return it
    const evaluationRes = await getEvaluatorResponse({
      newInput: [{ role: 'user', content: toolArgs.decision_text }],
      promptId: 'EVALUATION_PROMPT',
    })
  
    return [undefined, evaluationRes.output_text]
  } catch (error) {
    return [error as Error]
  }
}
