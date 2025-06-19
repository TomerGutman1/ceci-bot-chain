
export enum OpenAIEventType {
    ResponseCreated = 'response.created',
    ResponseInProgress = 'response.in_progress',
    ResponseOutputItemAdded = 'response.output_item.added',
    ResponseContentPartAdded = 'response.content_part.added',
    ResponseOutputTextDelta = 'response.output_text.delta',
    ResponseOutputTextDone = 'response.output_text.done',
    ResponseOutputItemDone = 'response.output_item.done',
    ResponseContentPartDone = 'response.content_part.done',
    ResponseCompleted = 'response.completed',
}

export enum ChatEventType {
    MessageCreated = 'message-created',
    MessageAdded = 'message-added',
    MessageDelta = 'message-delta',
    MessageCompleted = 'message-completed',
    MessageStreamCompleted = 'message-stream-completed',
}

export interface ChatEventBase {
    type: ChatEventType;
}

export interface StreamResponseCreatedEvent extends ChatEventBase {
    type: ChatEventType.MessageCreated;
    conversationId: string;
}

export interface StreamResponseOutputItemAddedEvent extends ChatEventBase {
    type: ChatEventType.MessageAdded;
    message: {
        id: string;
        role: 'user' | 'assistant' | 'system';
        content: string;
    };
}
export interface StreamResponseOutputTextDeltaEvent extends ChatEventBase {
    type: ChatEventType.MessageDelta;
    delta: string;
}
export interface StreamResponseOutputTextDoneEvent extends ChatEventBase {
    type: ChatEventType.MessageCompleted;
    text: string;
}

export type ChatEvent =
    | StreamResponseCreatedEvent
    | StreamResponseOutputItemAddedEvent
    | StreamResponseOutputTextDeltaEvent
    | StreamResponseOutputTextDoneEvent;