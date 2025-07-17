
import { useState } from "react";
import ChatInterface from "@/components/chat/ChatInterface"; // Updated import path
import ExampleQueries from "@/components/chat/ExampleQueries";

const Index = () => {
  const [chatTriggerMessage, setChatTriggerMessage] = useState<{ text: string; timestamp: number } | null>(null);
  const [chatEditMessage, setChatEditMessage] = useState<{ text: string; timestamp: number } | null>(null);
  
  // Check if examples should be shown (default to true if not set)
  const showExamples = import.meta.env.VITE_SHOW_EXAMPLES !== 'false';

  return (
    <div className="max-w-5xl mx-auto w-full flex flex-col h-full px-4">
      {/* Header with logo and intro text */}
      <div className="flex flex-col items-center mt-8 mb-8" id="chat-description">
        {/* Logo positioned above the text */}
        <div className="flex-shrink-0 mb-6">
          <img 
            src="/lovable-uploads/0a1b47c5-9e0f-4aab-aaff-2e181127c201.png" 
            alt="Ceci.AI Logo" 
            className="h-32 w-auto object-contain"
          />
        </div>
        
        {/* Main content */}
        <div className="w-full max-w-4xl text-center">
          <h1 className="text-lg mb-4 text-ceci-dark">
            הי, אני <span className="text-ceci-blue">Ceci</span>, בוט AI, מבית המרכז להעצמת האזרח לסיוע בייעול עבודת ממשל. אז מה אני יודע לעשות?
          </h1>
          <p className="text-lg text-ceci-gray mb-4 text-justify">
            בהתבסס על מאגר הכולל מעל 25,000 החלטות ממשלה ו<a href="https://www.ceci.org.il/%d7%94%d7%9e%d7%95%d7%a0%d7%99%d7%98%d7%95%d7%a8/" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 underline">מאות דוחות מוניטור</a>, באפשרותי לספק סקירות לפי תחום עיסוק, לנתח החלטות דומות, ולאתר חסמים ומאפשרים בהחלטות קודמות. כך ניתן להפיק תובנות והמלצות אופרטיביות שיגדילו את סיכויי הביצוע של ההחלטה שברצונך לקדם.
          </p>
        </div>
      </div>

      <div id="chat-body" className="flex flex-col flex-grow">
        {/* ChatInterface replaces the old input - Aligned with login button */}
        <div className="w-full mt-auto mb-4 flex justify-center">
          <div className={`flex items-start gap-4 ${showExamples ? 'max-w-7xl' : 'max-w-3xl'} w-full`}>
            {/* Left Examples */}
            {showExamples && (
              <ExampleQueries 
                position="left" 
                onQueryClick={(query) => setChatTriggerMessage({ text: query, timestamp: Date.now() })}
                onQueryEdit={(query) => setChatEditMessage({ text: query, timestamp: Date.now() })}
              />
            )}
            
            {/* Chat Interface */}
            <div className="w-full max-w-3xl">
              <ChatInterface 
                externalMessage={chatTriggerMessage} 
                externalEditMessage={chatEditMessage}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
