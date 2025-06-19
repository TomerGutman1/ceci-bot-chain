
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const Hero = () => {
  return (
    <section className="py-20 px-4">
      <div className="container mx-auto">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 text-ceci-dark">
            ניתוח והערכת החלטות ממשלה באמצעות בינה מלאכותית
          </h1>
          <p className="text-xl md:text-2xl text-ceci-gray mb-10 max-w-3xl mx-auto">
            פלטפורמה מתקדמת המנתחת, מעריכה וחוזה את ישימות החלטות הממשלה בישראל באמצעות אלגוריתמים מבוססי נתונים
          </p>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Button size="lg" className="bg-ceci-blue hover:bg-blue-700 text-lg py-6 px-8">
              התחל עכשיו
            </Button>
            <Link to="/methodology">
              <Button variant="outline" size="lg" className="text-lg py-6 px-8">
                איך זה עובד
              </Button>
            </Link>
          </div>
        </div>
      </div>

      <div className="mt-24 max-w-5xl mx-auto bg-ceci-lightGray rounded-2xl p-6 md:p-8 shadow-md">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-ceci-dark mb-2">כיצד אוכל לסייע לך היום?</h2>
          <p className="text-ceci-gray">
            אני יועץ ה-AI של המרכז להצמצת ההחלטה. אז מה אני יודע לעשות?
          </p>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { title: "יש לי שאלה על החלטה", icon: "❓" },
            { title: "העלאת קובץ החלטה", icon: "📄" },
            { title: "יש לי מספר החלטה", icon: "🔢" },
            { title: "יש לי דוגמה להחלטה", icon: "📋" },
            { title: "לפי תחום עניין", icon: "🏛️" },
          ].map((item, idx) => (
            <div 
              key={idx} 
              className="flex items-center gap-3 p-4 bg-white rounded-md border border-gray-200 hover:border-ceci-blue cursor-pointer transition-all"
            >
              <span className="text-2xl">{item.icon}</span>
              <span className="font-medium">{item.title}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Hero;
