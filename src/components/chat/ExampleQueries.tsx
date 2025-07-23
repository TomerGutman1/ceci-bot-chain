import { useState } from "react";
import { ChevronLeft, ChevronRight, Lightbulb, Search, TrendingUp, FileText, BarChart3, History, Brain, Scale, Users, Calendar } from "lucide-react";

interface ExampleQuery {
  icon: JSX.Element;
  title: string;
  query: string;
  category: string;
}

interface ExampleQueriesProps {
  onQueryClick: (query: string) => void;
  onQueryEdit: (query: string) => void;
  position: "left" | "right";
}

const ExampleQueries = ({ onQueryClick, onQueryEdit, position }: ExampleQueriesProps) => {
  const [isExpanded, setIsExpanded] = useState(true);
  
  // Check if macro button should be shown (default to false)
  const showMacroButton = import.meta.env.VITE_SHOW_MACRO_BUTTON === 'true';

  // Filter to show only basic queries
  const basicQueries: ExampleQuery[] = [
    {
      icon: <Search className="w-5 h-5" />,
      title: "חיפוש פשוט",
      query: "החלטות בנושא מינהל ציבורי ושירות המדינה",
      category: "חיפוש"
    },
    {
      icon: <FileText className="w-5 h-5" />,
      title: "החלטה ספציפית",
      query: "נתח לי את החלטה 550",
      category: "ספציפי"
    },
    {
      icon: <BarChart3 className="w-5 h-5" />,
      title: "ספירת החלטות",
      query: "כמה החלטות בנושא ביטחון קיבלה ממשלה 37",
      category: "חיפוש"
    },
    {
      icon: <Calendar className="w-5 h-5" />,
      title: "החלטות אחרונות",
      query: "הראה החלטות אחרונות בנושא סביבה",
      category: "עדכני"
    },
    {
      icon: <FileText className="w-5 h-5" />,
      title: "החלטות לפי משרד",
      query: "החלטות של משרד החינוך",
      category: "חיפוש"
    },
    {
      icon: <Search className="w-5 h-5" />,
      title: "חיפוש לפי תאריך",
      query: "החלטות ממשלה ב2024 בנושא בריאות",
      category: "חיפוש"
    }
  ];

  // Use the same basic queries for both sides
  const examples: ExampleQuery[] = basicQueries;

  return (
    <div className={`relative transition-all duration-300 ${isExpanded ? 'w-80' : 'w-12'}`}>
      <div className={`absolute ${position === 'left' ? 'right-0' : 'left-0'} top-1/2 -translate-y-1/2 z-10`}>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="bg-white shadow-lg rounded-full p-2 hover:bg-gray-50 transition-colors border border-gray-200"
          aria-label={isExpanded ? "הסתר דוגמאות" : "הצג דוגמאות"}
        >
          {position === 'left' ? 
            (isExpanded ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />) :
            (isExpanded ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />)
          }
        </button>
      </div>

      {isExpanded && (
        <div className={`max-h-[80vh] bg-gradient-to-b from-blue-50 to-white rounded-lg shadow-sm border border-gray-200 p-4 ${position === 'left' ? 'mr-4' : 'ml-4'} flex flex-col`}>
          <h3 className="font-bold text-lg text-gray-800 mb-4 flex items-center gap-2 flex-shrink-0">
            <Lightbulb className="w-5 h-5 text-ceci-blue" />
            דוגמאות לשימוש
          </h3>
          
          <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 hover:scrollbar-thumb-gray-400 transition-colors pr-2">
            <div className="space-y-3">
              {examples.map((example, index) => (
                <div
                  key={index}
                  className="group bg-white rounded-lg p-3 hover:shadow-md transition-all duration-200 border border-transparent hover:border-ceci-blue"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-ceci-blue group-hover:text-white transition-colors">
                      {example.icon}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-semibold text-sm text-gray-800">{example.title}</h4>
                      </div>
                      
                      <p className="text-sm text-gray-600 leading-relaxed mb-2">
                        {example.query}
                      </p>
                      
                      <div className="flex gap-2">
                        <button
                          onClick={() => onQueryClick(example.query)}
                          className="text-xs bg-ceci-blue text-white px-3 py-1 rounded hover:bg-blue-600 transition-colors"
                          title="שלח שאלה"
                        >
                          📤 שלח
                        </button>
                        <button
                          onClick={() => onQueryEdit(example.query)}
                          className="text-xs bg-gray-200 text-gray-700 px-3 py-1 rounded hover:bg-gray-300 transition-colors"
                          title="העתק לעריכה"
                        >
                          ✏️ ערוך
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Macro View Button - Only show if enabled */}
          {showMacroButton && (
            <div className="mt-4">
              <a 
                href="/dashboard/statistics"
                className="block w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold py-3 px-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 text-center shadow-lg"
              >
                📊 מבט מאקרו
                <span className="block text-xs font-normal mt-1">סטטיסטיקות וניתוח מקיף</span>
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ExampleQueries;