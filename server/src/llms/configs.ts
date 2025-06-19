import OpenAI from "openai"
import prompts from "./prompts"
import tools from "./tools"
import { LLMReqParams } from "../types/prompts"

export const getAssistantConfig = ({
  newInput,
  promptId,
  conversationId,
}: LLMReqParams): OpenAI.Responses.ResponseCreateParamsStreaming => {
  const config: OpenAI.Responses.ResponseCreateParamsStreaming = {
    model: 'gpt-4o-mini-2024-07-18',
    temperature: 1,
    top_p: 1,
    instructions: prompts[promptId],
    input: newInput,
    tools: [
      tools.evaluate_existing_decision,
      tools.evaluate_decision,
      tools.search_decisions,
    ],
    stream: true,
    store: true,
  };
  
  // Only add previous_response_id if conversationId exists and is not empty
  if (conversationId && conversationId.trim() !== '') {
    config.previous_response_id = conversationId;
  }
  
  return config;
}

export const getEvaluatorConfig = ({
  newInput,
  promptId,
}: LLMReqParams): OpenAI.Responses.ResponseCreateParamsNonStreaming => {
  return {
    model: 'gpt-4o-mini-2024-07-18',
    temperature: 1,
    top_p: 1,
    instructions: prompts[promptId],
    input: newInput,
    tools: [],
  }
}
