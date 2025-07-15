const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  type: 'response' | 'error' | 'done';
  content?: string;
  metadata?: any;
  error?: string;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_activity: string;
  state: string;
  query_count: number;
  recent_queries: Array<{
    query_id: string;
    timestamp: string;
    original_query: string;
    response_type: string;
    has_results: boolean;
  }>;
}

export class ChatService {
  private static instance: ChatService;
  private sessionId: string | null = null;
  
  private constructor() {
    // Try to restore session from localStorage
    this.sessionId = localStorage.getItem('chat_session_id');
  }
  
  static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  getSessionId(): string | null {
    return this.sessionId;
  }

  setSessionId(sessionId: string | null): void {
    this.sessionId = sessionId;
    if (sessionId) {
      localStorage.setItem('chat_session_id', sessionId);
    } else {
      localStorage.removeItem('chat_session_id');
    }
  }

  async sendMessage(message: string, history: ChatMessage[] = []): Promise<string> {
    console.log('Sending message:', message);
    console.log('API URL:', `${API_BASE_URL}/chat`);
    
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          history,
          sessionId: this.sessionId
        }),
      });

      console.log('Response status:', response.status, response.ok);
      
      if (!response.ok) {
        throw new Error(`Chat API error: ${response.statusText}`);
      }

      // Read SSE stream
      const reader = response.body?.getReader();
      console.log('Reader created:', !!reader);
      const decoder = new TextDecoder();
      let result = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          console.log('Raw chunk received:', chunk);
          const lines = chunk.split('\n');

          for (const line of lines) {
            console.log('Processing line:', line);
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6)) as ChatResponse;
                console.log('Parsed data:', data);
                
                if (data.type === 'response' && data.content) {
                  result = data.content;
                  console.log('Received response chunk:', data.content.length, 'chars');
                  
                  // Update session ID if received
                  if (data.metadata?.session_id) {
                    this.setSessionId(data.metadata.session_id);
                  }
                } else if (data.type === 'error') {
                  throw new Error(data.error || 'Unknown error');
                } else if (data.type === 'done') {
                  console.log('Stream completed, total result:', result.length, 'chars');
                }
              } catch (e) {
                console.error('Error parsing JSON:', e, 'Line:', line);
              }
            }
          }
        }
      }

      return result;
    } catch (error) {
      console.error('Chat service error:', error);
      throw error;
    }
  }

  async checkHealth(): Promise<{
    status: string;
    services: {
      pandasai: { available: boolean; url: string };
      typescript: { available: boolean; loaded: boolean; decisions: number };
    };
    preferredService: string;
  }> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/health`);
      if (!response.ok) {
        throw new Error('Health check failed');
      }
      return await response.json();
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  async getSessionInfo(): Promise<SessionInfo | null> {
    if (!this.sessionId) {
      return null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/session/${this.sessionId}`);
      if (!response.ok) {
        if (response.status === 404) {
          // Session expired or not found
          this.setSessionId(null);
          return null;
        }
        throw new Error('Failed to get session info');
      }
      return await response.json();
    } catch (error) {
      console.error('Get session info error:', error);
      return null;
    }
  }

  async clearSession(): Promise<void> {
    this.setSessionId(null);
  }

  async getSessionStats(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/sessions/stats`);
      if (!response.ok) {
        throw new Error('Failed to get session stats');
      }
      return await response.json();
    } catch (error) {
      console.error('Get session stats error:', error);
      throw error;
    }
  }
}

export default ChatService.getInstance();
