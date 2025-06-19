import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";

const Rankings = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");

  const topRankingDecisions = [
    { id: 1, title: "החלטה 4356: תכנית לאומית לפיתוח תשתיות", score: 92, category: "תשתיות" },
    { id: 2, title: "החלטה 1275: רפורמה במערכת הבריאות", score: 87, category: "בריאות" },
    { id: 3, title: "החלטה 5680: תוכנית חומש לחינוך", score: 85, category: "חינוך" },
    { id: 4, title: "החלטה 3421: יישום הסכמי אקלים", score: 82, category: "איכות סביבה" },
    { id: 5, title: "החלטה 7823: תכנית לאומית לדיור", score: 80, category: "דיור" },
  ];

  return (
    <div className="max-w-5xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-2">דירוגי החלטות הממשלה</h1>
        <p className="text-gray-600">דירוג החלטות ממשלה לפי סיכויי יישום וקריטריונים נוספים</p>
      </header>

      <div className="bg-white p-6 rounded-lg shadow-sm mb-8">
        <h2 className="text-xl font-semibold mb-4">סינון וחיפוש</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-sm text-gray-500 block mb-1">חיפוש לפי מילות מפתח</label>
            <Input placeholder="הקלד מילות חיפוש..." className="w-full" />
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">סינון לפי קטגוריה</label>
            <select className="w-full p-2 border rounded-md">
              <option>כל הקטגוריות</option>
              <option>בריאות</option>
              <option>חינוך</option>
              <option>תשתיות</option>
              <option>דיור</option>
              <option>איכות סביבה</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-500 block mb-1">מיון לפי</label>
            <select className="w-full p-2 border rounded-md">
              <option>דירוג - מהגבוה לנמוך</option>
              <option>דירוג - מהנמוך לגבוה</option>
              <option>תאריך - מהחדש לישן</option>
              <option>תאריך - מהישן לחדש</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-semibold mb-4">החלטות מובילות</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-right">
                <th className="py-3 px-4 border-b">מס׳</th>
                <th className="py-3 px-4 border-b">החלטה</th>
                <th className="py-3 px-4 border-b">קטגוריה</th>
                <th className="py-3 px-4 border-b">ציון יישום</th>
                <th className="py-3 px-4 border-b">פעולות</th>
              </tr>
            </thead>
            <tbody>
              {topRankingDecisions.map((decision) => (
                <tr key={decision.id} className="hover:bg-gray-50">
                  <td className="py-3 px-4 border-b">{decision.id}</td>
                  <td className="py-3 px-4 border-b font-medium">{decision.title}</td>
                  <td className="py-3 px-4 border-b">{decision.category}</td>
                  <td className="py-3 px-4 border-b">
                    <div className="flex items-center">
                      <div className="w-16 h-3 rounded-full bg-gray-200 mr-2">
                        <div 
                          className={`h-full rounded-full ${
                            decision.score >= 90 ? 'bg-green-500' : 
                            decision.score >= 80 ? 'bg-blue-500' : 
                            decision.score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                          }`} 
                          style={{ width: `${decision.score}%` }}
                        />
                      </div>
                      <span className="font-medium">{decision.score}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 border-b">
                    <Button variant="outline" size="sm">פרטים נוספים</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-6 flex justify-center">
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((page) => (
              <Button 
                key={page} 
                variant={page === 1 ? "default" : "outline"} 
                size="sm"
                className="w-8 h-8 p-0"
              >
                {page}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Rankings;
