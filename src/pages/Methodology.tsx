
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Methodology = () => {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">מתודולוגיית ניתוח החלטות</h1>
      
      <div className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>מהי המתודולוגיה?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p>
              מתודולוגיית הניתוח של CECI מבוססת על מחקר מקיף של דפוסי יישום החלטות ממשלה 
              בישראל לאורך העשורים האחרונים. המערכת מנתחת מגוון של פרמטרים כדי לחזות את 
              סיכויי היישום של החלטות.
            </p>
            <p>
              המתודולוגיה משלבת שיטות ניתוח כמותיות עם הבנה עמוקה של התהליכים הבירוקרטיים 
              והפוליטיים המשפיעים על יישום החלטות ממשלה.
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>פרמטרים מרכזיים</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-2">
              <li>הגדרה ברורה של גורם אחראי ליישום</li>
              <li>תקציב מוגדר וריאלי</li>
              <li>הגדרת לוחות זמנים</li>
              <li>מורכבות ההחלטה והיישום</li>
              <li>תיאום בין-משרדי נדרש</li>
              <li>תלות בחקיקה</li>
              <li>רמת התמיכה הפוליטית</li>
              <li>אינטרסים של בעלי עניין</li>
            </ul>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>תהליך הניתוח</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p>
              תהליך הניתוח מתבצע בארבעה שלבים עיקריים:
            </p>
            <ol className="list-decimal list-inside space-y-2">
              <li>איסוף וקידוד המידע הרלוונטי מההחלטה</li>
              <li>ניתוח השוואתי מול החלטות דומות מהעבר</li>
              <li>הערכת הסביבה הפוליטית והארגונית הנוכחית</li>
              <li>חישוב מדד סיכויי היישום והמלצות לשיפור</li>
            </ol>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>מודל החיזוי</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p>
              המודל המתמטי המשמש לחיזוי סיכויי היישום מבוסס על רגרסיה רב-משתנית 
              המשקללת את כל הפרמטרים הרלוונטיים. המודל כויל על סמך נתונים היסטוריים 
              של למעלה מ-1,000 החלטות ממשלה משנת 2000 ואילך.
            </p>
            <p>
              דיוק החיזוי עומד על כ-78% בהתבסס על בדיקת תיקוף צולבת.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Methodology;
