import { z } from 'zod';

export const postChatSchema = z.object({
    message: z.string(),
    history: z.array(z.any()).optional(),
    conversationId: z.string().optional(),
});