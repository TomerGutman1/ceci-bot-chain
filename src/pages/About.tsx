import { Button } from "@/components/ui/button";
import { CheckCircle } from "lucide-react";

const About = () => {
  return (
    <div className="flex-grow">
      <section className="py-16 px-4 bg-gradient-to-b from-ceci-lightGray to-white">
        <div className="container mx-auto">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">אודות CECI ai</h1>
            <p className="text-lg text-ceci-gray mb-8">
              הפלטפורמה המובילה בישראל לניתוח והערכת החלטות ממשלה באמצעות בינה מלאכותית
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">המשימה שלנו</h2>
              <p className="text-lg mb-6">
                אנו מאמינים כי באמצעות טכנולוגיה מתקדמת וניתוח נתונים חכם, ניתן לשפר באופן משמעותי את תהליך קבלת ההחלטות בממשלה ואת סיכויי היישום שלהן.
              </p>
              <p className="text-lg mb-6">
                המטרה שלנו היא לספק כלים אובייקטיביים, מבוססי נתונים, שיסייעו למקבלי החלטות, חוקרים וארגונים אזרחיים להעריך את ישימותן של החלטות ממשלה, לזהות חסמים אפשריים ולהציע דרכי פעולה אפקטיביות.
              </p>
              <div className="space-y-3">
                {[
                  "שיפור איכות ההחלטות הממשלתיות",
                  "העלאת אחוזי היישום של החלטות",
                  "יצירת שקיפות בתהליכי קבלת החלטות",
                  "העצמת גורמי מקצוע וארגונים אזרחיים",
                  "קידום מדיניות מבוססת נתונים"
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <CheckCircle className="h-5 w-5 text-ceci-blue flex-shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-ceci-lightGray p-8 rounded-2xl">
              <div className="text-center">
                <div className="inline-block p-4 rounded-full bg-ceci-blue text-white text-3xl mb-4">
                  📊
                </div>
                <h3 className="text-2xl font-bold mb-4">המספרים שלנו</h3>
              </div>
              <div className="grid grid-cols-2 gap-6">
                {[
                  { value: "1,500+", label: "החלטות ממשלה שנותחו" },
                  { value: "85%", label: "דיוק בחיזוי יכולת יישום" },
                  { value: "320+", label: "משתמשים פעילים" },
                  { value: "45+", label: "ארגונים וגופי ממשל" }
                ].map((stat, idx) => (
                  <div key={idx} className="text-center p-4 bg-white rounded-lg shadow-sm">
                    <p className="text-2xl md:text-3xl font-bold text-ceci-blue mb-2">{stat.value}</p>
                    <p className="text-sm text-gray-600">{stat.label}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 px-4 bg-ceci-dark text-white">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">הצוות שלנו</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                name: "מנהל מוצר בכיר",
                role: "מייסד ומנכ\"ל",
                bio: "8 שנות ניסיון בתחום ה-GovTech, מומחה בניתוח מדיניות וכלי סיוע לממשל"
              },
              {
                name: "מדען נתונים בכיר",
                role: "מייסד שותף וסמנכ\"ל טכנולוגיות",
                bio: "8 שנות ניסיון בפיתוח אלגוריתמים לניתוח טקסט, למידת מכונה ובינה מלאכותית"
              },
              {
                name: "מפתח בכיר",
                role: "מנהל פיתוח",
                bio: "12 שנות ניסיון בפיתוח תוכנה, מומחה בבניית מערכות מורכבות ופתרונות SaaS"
              },
              {
                name: "ד\"ר יועץ מומחה",
                role: "יועץ אסטרטגי",
                bio: "מנכ\"ל משרד ממשלתי לשעבר, מומחה בתהליכי קבלת החלטות ומדיניות ציבורית"
              }
            ].map((member, idx) => (
              <div key={idx} className="bg-white bg-opacity-5 p-6 rounded-xl backdrop-blur-sm">
                <div className="w-24 h-24 rounded-full bg-gradient-to-r from-ceci-blue to-blue-500 mx-auto mb-4 flex items-center justify-center">
                  <span className="text-3xl">👤</span>
                </div>
                <h3 className="text-xl font-bold text-center mb-1">{member.name}</h3>
                <p className="text-sm text-center text-blue-300 mb-4">{member.role}</p>
                <p className="text-sm text-gray-300 text-center">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-3xl font-bold mb-8 text-center">שאלות נפוצות</h2>
          <div className="space-y-6">
            {[
              {
                q: "כיצד CECI ai מנתחת החלטות ממשלה?",
                a: "המערכת משתמשת באלגוריתמי בינה מלאכותית מתקדמים וניתוח טקסט כדי לנתח החלטות ממשלה לפי פרמטרים רבים כגון בהירות המטרות, הגדרת גורם אחראי, לוח זמנים, תקצוב ועוד. בהתבסס על ניתוח של מאות החלטות קודמות ואחוזי היישום שלהן, המערכת יכולה לחזות את סיכויי ההצלחה של החלטות חדשות."
              },
              {
                q: "למי מיועדת המערכת?",
                a: "המערכת מיועדת לבעלי תפקידים בממשלה, חוקרים, אנליסטים של מדיניות ציבורית, ארגוני חברה אזרחית העוסקים במעקב אחר יישום מדיניות, וכל מי שעוסק בתחום המדיניות הציבורית וההחלטות הממשלתיות בישראל."
              },
              {
                q: "האם הניתוח של CECI ai מבוסס על נתונים אובייקטיביים?",
                a: "כן, הניתוח מבוסס על מאגר נתונים מקיף של החלטות ממשלה היסטוריות, יישומן בפועל, וניתוח הגורמים שהשפיעו על הצלחתן או כישלונן. האלגוריתם מזהה דפוסים ומגמות מתוך הנתונים האלה ומשתמש בהם לחיזוי יכולת היישום של החלטות חדשות."
              },
              {
                q: "האם ניתן להעלות טיוטת החלטת ממשלה למערכת לפני אישורה?",
                a: "בהחלט! אחת היכולות המרכזיות של CECI ai היא לנתח טיוטות של החלטות עוד לפני אישורן, לזהות נקודות תורפה ולהציע שיפורים שיגבירו את סיכויי היישום שלהן בהמשך."
              },
              {
                q: "איך ניתן להתחיל להשתמש במערכת?",
                a: "ניתן להירשם למערכת דרך האתר ולקבל גישה ניסיון של 14 יום. אנו מציעים חבילות שונות לפי היקף השימוש וסוג הארגון. לגופי ממשל וארגונים ללא מטרות רווח קיימות תוכניות מיוחדות."
              }
            ].map((faq, idx) => (
              <div key={idx} className="border-b border-gray-200 pb-6">
                <h3 className="text-xl font-bold mb-2">{faq.q}</h3>
                <p className="text-ceci-gray">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 px-4 bg-gradient-to-r from-ceci-blue to-blue-600 text-white">
        <div className="container mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold mb-6">מוכנים להתחיל?</h2>
          <p className="text-xl mb-8">
            הצטרפו למאות משתמשים שכבר משפרים את איכות ההחלטות הממשלתיות בישראל באמצעות CECI ai
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Button size="lg" className="bg-white text-ceci-blue hover:bg-gray-100 text-lg py-6">
              התחל תקופת ניסיון בחינם
            </Button>
            <Button variant="outline" size="lg" className="border-white text-white hover:bg-white/10 text-lg py-6">
              תיאום הדגמה
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
