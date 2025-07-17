import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, FileText } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import chatService from "@/services/chat.service";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { DecisionGuideModal } from "@/components/decision-guide/DecisionGuideModal";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  externalMessage?: { text: string; timestamp: number } | null;
  externalEditMessage?: { text: string; timestamp: number } | null;
}

const ChatInterface = ({ externalMessage, externalEditMessage }: ChatInterfaceProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "שלום! אני העוזר החכם של CECI. אני יכול לעזור לך למצוא החלטות ממשלה, לנתח את רמת היישום של ההחלטות, או לענות על שאלות לגבי פעילות הממשלה. במה אוכל לעזור?",
      timestamp: new Date(),
    },
  ]);
  
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isDecisionGuideOpen, setIsDecisionGuideOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const processNewMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Get response from backend
      const response = await chatService.sendMessage(text);
      
      // Add assistant response
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: response,
        timestamp: new Date(),
      }]);
    } catch (error) {
      console.error('Error calling chat service:', error);
      toast({
        title: "שגיאה",
        description: "אירעה שגיאה בחיבור לשרת. אנא נסה שוב.",
        variant: "destructive",
      });
      
      // Add error message
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: "מצטער, אירעה שגיאה טכנית. אנא נסה שוב.",
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;
    processNewMessage(inputMessage);
    setInputMessage("");
  };

  useEffect(() => {
    if (externalMessage && externalMessage.text) {
      processNewMessage(externalMessage.text);
    }
  }, [externalMessage]);

  useEffect(() => {
    if (externalEditMessage && externalEditMessage.text) {
      setInputMessage(externalEditMessage.text);
    }
  }, [externalEditMessage]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("he-IL", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Render markdown content with proper formatting
  const formatMessageContent = (content: string, isUser: boolean = false) => {
    // For user messages, keep simple text
    if (isUser) {
      return <span>{content}</span>;
    }
    
    // For assistant messages, render markdown
    return (
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]}
        className="prose prose-sm max-w-none"
        components={{
          // Custom table styling
          table: ({node, ...props}) => (
            <table className="min-w-full divide-y divide-gray-300 my-2" {...props} />
          ),
          th: ({node, ...props}) => (
            <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50" {...props} />
          ),
          td: ({node, ...props}) => (
            <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-900 border-t" {...props} />
          ),
          // Custom heading styles
          h1: ({node, ...props}) => (
            <h1 className="text-xl font-bold mb-2 text-gray-900" {...props} />
          ),
          h2: ({node, ...props}) => (
            <h2 className="text-lg font-semibold mb-2 text-gray-800" {...props} />
          ),
          h3: ({node, ...props}) => (
            <h3 className="text-base font-semibold mb-1 text-gray-700" {...props} />
          ),
          // Links
          a: ({node, ...props}) => (
            <a className="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer" {...props} />
          ),
          // Lists
          ul: ({node, ...props}) => (
            <ul className="list-disc list-inside space-y-1 my-2" {...props} />
          ),
          ol: ({node, ...props}) => (
            <ol className="list-decimal list-inside space-y-1 my-2" {...props} />
          ),
          // Strong text
          strong: ({node, ...props}) => (
            <strong className="font-bold text-gray-900" {...props} />
          ),
          // Code blocks
          code: ({node, inline, ...props}) => (
            inline ? 
              <code className="bg-gray-100 rounded px-1 py-0.5 text-sm" {...props} /> :
              <code className="block bg-gray-100 rounded p-2 text-sm overflow-x-auto my-2" {...props} />
          ),
          // Horizontal rule
          hr: ({node, ...props}) => (
            <hr className="my-4 border-gray-300" {...props} />
          ),
          // Blockquote
          blockquote: ({node, ...props}) => (
            <blockquote className="border-r-4 border-gray-300 pr-4 my-2 text-gray-600" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  // Keep the old URL conversion function as backup
  const formatSimpleContent = (content: string, isUser: boolean = false) => {
    // Regular expression to match URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    
    const elements: JSX.Element[] = [];
    let lastIndex = 0;
    let match;
    
    // Find all URLs in the content
    while ((match = urlRegex.exec(content)) !== null) {
      // Add text before URL
      if (match.index > lastIndex) {
        elements.push(<span key={`text-${lastIndex}`}>{content.slice(lastIndex, match.index)}</span>);
      }
      
      // Clean the URL (remove trailing punctuation)
      let url = match[0];
      let trailingChars = '';
      
      // Remove trailing punctuation but keep it for display
      const punctuationMatch = url.match(/[,.!?;:]+$/);
      if (punctuationMatch) {
        trailingChars = punctuationMatch[0];
        url = url.slice(0, -trailingChars.length);
      }
      
      // Check if this is a government decision URL
      const isGovDecisionUrl = url.includes('gov.il') && (url.includes('/dec') || url.includes('/pages/dec'));
      
      // Add the URL as a link
      elements.push(
        <a
          key={`url-${match.index}`}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className={`underline hover:opacity-80 ${
            isUser ? 'text-blue-200' : 'text-blue-600'
          }`}
          onClick={(e) => e.stopPropagation()}
        >
          {isGovDecisionUrl ? 'לחצו להחלטה המלאה' : url}
        </a>
      );
      
      // Add trailing punctuation if any
      if (trailingChars) {
        elements.push(<span key={`punct-${match.index}`}>{trailingChars}</span>);
      }
      
      lastIndex = urlRegex.lastIndex;
    }
    
    // Add remaining text
    if (lastIndex < content.length) {
      elements.push(<span key={`text-end`}>{content.slice(lastIndex)}</span>);
    }
    
    return <>{elements}</>;
  };

  // Check service status on mount
  // useEffect(() => {
  //   chatService.checkHealth().then(health => {
  //     console.log('Chat service health:', health);
  //     if (health.services?.botChain?.available) {
  //       console.log('Using Bot Chain service');
  //     } else if (health.services?.pandasai?.available) {
  //       console.log('Using PandasAI service');
  //     } else {
  //       console.log('Using TypeScript fallback service');
  //     }
  //   }).catch(err => {
  //     console.error('Failed to check service health:', err);
  //   });
  // }, []);

  return (
    <div className="flex flex-col h-[700px] bg-white rounded-xl shadow-sm border border-gray-200 w-full">
      <div className="p-4 border-b border-gray-200">
        <h2 className="font-bold text-lg">יועץ ה-AI של <span className="text-ceci-blue">המרכז להעצמת האזרח</span></h2>
        <p className="text-sm text-gray-500">שאל שאלות על החלטות ממשלה וקבל תשובות בזמן אמת</p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-start flex-row-reverse" : "justify-start"
            }`}
          >
            <div
              className={`flex flex-col max-w-[80%] ${
                message.role === "user"
                  ? "bg-ceci-blue text-white rounded-s-2xl rounded-se-2xl"
                  : "bg-gray-100 text-gray-800 rounded-e-2xl rounded-es-2xl"
              } p-3`}
            >
              <div className="text-sm">
                {formatMessageContent(message.content, message.role === "user")}
              </div>
              <span className="text-xs opacity-70 mt-1 self-end">
                {formatTime(message.timestamp)}
              </span>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 rounded-e-2xl rounded-es-2xl p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "0ms" }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "150ms" }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "300ms" }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Decision Guide Button */}
      <div className="px-4 pb-2">
        <Button
          onClick={() => setIsDecisionGuideOpen(true)}
          variant="outline"
          className="w-full justify-center gap-2 text-primary hover:text-primary"
        >
          <FileText className="h-4 w-4" />
          צריך עזרה בניסוח החלטה
        </Button>
      </div>
      
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 flex gap-2">
        <Input
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="הקלד את שאלתך כאן..."
          className="flex-1"
          disabled={isLoading}
        />
        <Button 
          type="submit" 
          size="icon" 
          className="bg-ceci-blue hover:bg-blue-700"
          disabled={isLoading || !inputMessage.trim()}
        >
          <Send className="h-4 w-4" />
        </Button>
      </form>
      
      {/* Decision Guide Modal */}
      <DecisionGuideModal
        isOpen={isDecisionGuideOpen}
        onClose={() => setIsDecisionGuideOpen(false)}
      />
    </div>
  );
};

export default ChatInterface;
