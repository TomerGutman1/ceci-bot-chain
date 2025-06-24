import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export interface IntentResult {
  intent: 'DATA_QUERY' | 'GENERAL_QUESTION' | 'UNCLEAR';
  confidence: number;
  correctedQuery?: string;
  guidance?: string;
  metadata?: {
    detectedSpellingErrors?: string[];
    questionType?: string;
    suggestedTools?: string[];
  };
}

const INTENT_DETECTION_PROMPT = `אתה עוזר AI של מערכת CECI לחיפוש החלטות ממשלה.
תפקידך לנתח הודעות משתמשים ולזהות את הכוונה שלהם.

סוגי כוונות:
1. DATA_QUERY - המשתמש רוצה לחפש או לנתח החלטות ממשלה
   דוגמאות: "הבא לי החלטות בנושא חינוך", "כמה החלטות יש משנת 2020", "החלטה 660"
   
2. GENERAL_QUESTION - שאלות כלליות על המערכת או היכולות שלה
   דוגמאות: "מה אתה יודע לעשות?", "איך אני מחפש?", "מה המערכת הזו?"
   
3. UNCLEAR - הבקשה לא ברורה ודורשת הבהרה
   דוגמאות: "xyzabc", "????", טקסט קצר מאוד ללא הקשר

תיקוני שגיאות כתיב נפוצות:
- "הבא ליי" → "הבא לי"
- "החלתה" → "החלטה" 
- "ממשלע" → "ממשלה"
- "בנושה" → "בנושא"

החזר תשובה בפורמט JSON:
{
  "intent": "DATA_QUERY" | "GENERAL_QUESTION" | "UNCLEAR",
  "confidence": 0.0-1.0,
  "correctedQuery": "השאילתה המתוקנת (אם יש תיקונים)",
  "guidance": "הנחיה למשתמש (רק אם intent=UNCLEAR)",
  "metadata": {
    "detectedSpellingErrors": ["שגיאה1", "שגיאה2"],
    "questionType": "capabilities" | "how_to" | "about" | null,
    "suggestedTools": ["PANDAS_AI"]
  }
}`;

export async function detectIntentWithGPT(
  message: string,
  _sessionId?: string
): Promise<IntentResult> {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo',
      messages: [
        { role: 'system', content: INTENT_DETECTION_PROMPT },
        { role: 'user', content: message }
      ],
      temperature: 0.2,
      response_format: { type: "json_object" },
      max_tokens: 500
    });

    const result = JSON.parse(response.choices[0].message.content || '{}');
    
    // Validate and provide defaults
    return {
      intent: result.intent || 'UNCLEAR',
      confidence: result.confidence || 0.5,
      correctedQuery: result.correctedQuery,
      guidance: result.guidance,
      metadata: result.metadata
    };
    
  } catch (error) {
    console.error('[Intent Detection] Error:', error);
    
    // Fallback to simple pattern matching
    return fallbackIntentDetection(message);
  }
}

function fallbackIntentDetection(message: string): IntentResult {
  const lowerMessage = message.toLowerCase();
  
  // Check for data query patterns
  const dataPatterns = [
    'הבא לי', 'חפש', 'מצא', 'תן לי', 'הראה לי',
    'החלטות', 'החלטה', 'ממשלה', 'משרד',
    'בנושא', 'סטטיסטיקה', 'כמה', 'מתי'
  ];
  
  const isDataQuery = dataPatterns.some(pattern => lowerMessage.includes(pattern));
  
  // Check for general questions
  const generalPatterns = [
    'מה אתה', 'איך אתה', 'מה המערכת', 'איך מחפשים',
    'מה אפשר', 'מה ניתן', 'יכולות', 'תכונות'
  ];
  
  const isGeneralQuestion = generalPatterns.some(pattern => lowerMessage.includes(pattern));
  
  // Very short or meaningless messages
  if (message.trim().length < 3 || /^[^א-ת]+$/.test(message)) {
    return {
      intent: 'UNCLEAR',
      confidence: 0.9,
      guidance: 'הבקשה קצרה מדי או לא ברורה. אנא פרט יותר על מה שאתה מחפש.'
    };
  }
  
  if (isDataQuery) {
    return {
      intent: 'DATA_QUERY',
      confidence: 0.7
    };
  }
  
  if (isGeneralQuestion) {
    return {
      intent: 'GENERAL_QUESTION',
      confidence: 0.7,
      metadata: {
        questionType: 'capabilities'
      }
    };
  }
  
  return {
    intent: 'UNCLEAR',
    confidence: 0.5,
    guidance: 'לא הבנתי את הבקשה. אני יכול לעזור לך למצוא החלטות ממשלה לפי נושא, תאריך, מספר ועוד.'
  };
}

// Helper function to generate system responses
export async function generateSystemResponse(questionType: string): Promise<string> {
  const responses: Record<string, string> = {
    capabilities: `אני העוזר החכם של CECI ואני יכול לעזור לך ב:

🔍 **חיפוש החלטות** - לפי נושא, תאריך, מספר החלטה, ממשלה ועוד
📊 **ניתוח וסטטיסטיקה** - כמה החלטות בנושא מסוים, התפלגות לפי שנים
📋 **הצגת פרטים** - תוכן מלא של החלטה, תקציר, תגיות
🔗 **קישורים** - גישה ישירה להחלטות באתר הממשלה

פשוט שאל אותי מה שמעניין אותך!`,
    
    how_to: `כך תוכל לחפש החלטות:

• **לפי נושא**: "הבא לי החלטות בנושא חינוך"
• **לפי תאריך**: "החלטות מ-2023", "החלטות מהחודש האחרון"
• **לפי מספר**: "החלטה 660", "החלטה מספר 1234"
• **לפי ממשלה**: "החלטות של ממשלה 36", "החלטות הממשלה הנוכחית"
• **שילובים**: "3 החלטות בנושא בריאות מ-2022"

מה תרצה לחפש?`,
    
    about: `CECI (המרכז להעצמת האזרח) הוא ארגון שמטרתו להנגיש מידע ממשלתי לציבור.

המערכת שלנו מכילה מעל 24,000 החלטות ממשלה ומאפשרת:
• חיפוש חכם בעברית טבעית
• ניתוח מגמות וסטטיסטיקות
• גישה מהירה למידע ממשלתי

המידע מתעדכן באופן שוטף מאתר הממשלה הרשמי.`,
    
    general: `אני כאן לעזור לך למצוא החלטות ממשלה! 

תוכל לשאול אותי על נושאים שונים, תאריכים, מספרי החלטות ועוד.
איך אוכל לסייע לך היום?`
  };
  
  return responses[questionType] || responses.general;
}