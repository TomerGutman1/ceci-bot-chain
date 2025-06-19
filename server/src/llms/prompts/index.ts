import EVALUATION_PROMPT from './EVALUATION_PROMPT';
import ASSISTANT_PROMPT from './ASSISTANT_PROMPT';
import { PromptId } from '../../types/prompts';

const prompts: Record<PromptId, string> = {
  EVALUATION_PROMPT,
  ASSISTANT_PROMPT,
}

export default prompts;