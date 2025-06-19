import { ResponseInput } from "openai/resources/responses/responses"

export type PromptId = 'EVALUATION_PROMPT' | 'ASSISTANT_PROMPT'

export interface LLMReqParams {
  newInput: ResponseInput
  promptId: PromptId
  conversationId?: string
}
