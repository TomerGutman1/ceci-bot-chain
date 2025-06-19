
import { CheckCircle } from "lucide-react";

const features = [
  {
    title: "ניתוח החלטות מבוסס AI",
    description: "ניתוח אוטומטי של החלטות ממשלה והערכת יכולת היישום שלהן בהתבסס על נתונים היסטוריים וסטטיסטיקה",
    icon: "🤖",
  },
  {
    title: "תחזיות הצלחה",
    description: "חיזוי אחוזי הצלחה של החלטות ממשלה בהתבסס על האלגוריתם הייחודי שלנו",
    icon: "📊",
  },
  {
    title: "בינה מלאכותית שיחתית",
    description: "ממשק שיחתי אינטראקטיבי המאפשר לשאול שאלות וקבלת תשובות מפורטות על החלטות ממשלה",
    icon: "💬",
  },
  {
    title: "דירוג וניתוח השוואתי",
    description: "השוואת החלטות שונות והצגת דירוג יכולת הביצוע שלהן ביחס להחלטות אחרות",
    icon: "🏆",
  },
  {
    title: "זיהוי חולשות ביישום",
    description: "איתור קשיים אפשריים ביישום החלטות וזיהוי מראש אתגרים שעשויים להקשות על הביצוע",
    icon: "🔍",
  },
  {
    title: "נגישות לכל הגורמים",
    description: "נגישות לחוקרים, מקבלי החלטות, ארגונים אזרחיים וגופי ממשל מכל מקום ובכל זמן",
    icon: "🔓",
  },
];

const Features = () => {
  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-ceci-dark mb-4">
            יכולות הפלטפורמה
          </h2>
          <p className="text-lg text-ceci-gray max-w-2xl mx-auto">
            CECI ai מספקת כלים מתקדמים לניתוח, הערכה וחיזוי ישימות החלטות ממשלה בישראל
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:border-ceci-blue hover:shadow-md transition-all"
            >
              <div className="text-3xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-bold mb-3 text-ceci-dark">{feature.title}</h3>
              <p className="text-ceci-gray">{feature.description}</p>
            </div>
          ))}
        </div>

        <div className="mt-20 bg-gradient-to-r from-ceci-blue to-blue-500 rounded-2xl p-8 md:p-12 text-white shadow-lg">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="md:w-2/3">
              <h3 className="text-2xl md:text-3xl font-bold mb-4">
                שפר את איכות ההחלטות הממשלתיות עם CECI ai
              </h3>
              <p className="text-lg mb-6">
                הצטרף למאות מקבלי החלטות, חוקרים וארגונים שכבר משתמשים בפלטפורמה שלנו כדי לשפר את איכות וישימות ההחלטות הממשלתיות בישראל.
              </p>
              
              <ul className="space-y-2 mb-6">
                {[
                  "גישה לניתוחים מעמיקים בלחיצת כפתור",
                  "תמיכת AI מתקדמת בעברית",
                  "חיסכון בזמן ושיפור איכות ההחלטות",
                  "ניבוי קשיים עוד לפני היישום"
                ].map((item, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="md:w-1/3 flex justify-center">
              <div className="bg-white bg-opacity-10 p-6 rounded-xl backdrop-blur-sm border border-white border-opacity-20">
                <div className="text-center">
                  <h4 className="text-xl font-bold mb-1">התחל להשתמש עכשיו</h4>
                  <p className="text-sm text-blue-100 mb-4">ללא התחייבות, 14 יום ניסיון</p>
                  <button className="w-full bg-white text-ceci-blue py-3 px-6 rounded-md font-bold hover:bg-blue-50 transition-colors">
                    הירשם בחינם
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;
