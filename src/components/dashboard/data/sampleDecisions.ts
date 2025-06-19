
import { DecisionData } from "../types/decision";

export const sampleDecisions: DecisionData[] = [
  {
    id: "1",
    title: "תוכנית לאומית להתייעלות אנרגטית",
    number: "4095",
    date: "12.10.2023",
    category: "אנרגיה וסביבה",
    feasibilityScore: 72,
    implementationStatus: 45,
    description: "החלטה על קידום תוכנית לאומית להתייעלות אנרגטית במטרה להפחית את צריכת האנרגיה במשק ב-17% עד שנת 2030.",
    budget: "750 מיליון ₪",
    responsibleParty: "משרד האנרגיה",
    timeline: "5 שנים",
    relatedDecisions: ["3786", "4125"],
    strengths: [
      "תקציב מוגדר",
      "לוח זמנים ריאלי",
      "גורם אחראי מוגדר"
    ],
    weaknesses: [
      "תלות בשיתוף פעולה בין-משרדי",
      "חסרה מתודולוגיית מדידה"
    ]
  },
  {
    id: "2",
    title: "רפורמה בתחום הדיור",
    number: "3982",
    date: "01.08.2023",
    category: "תשתיות",
    feasibilityScore: 58,
    implementationStatus: 25,
    description: "רפורמה בתחום הדיור הכוללת האצת הליכי תכנון ובנייה, הפשרת קרקעות לבנייה והגדלת היצע הדירות בשוק.",
    budget: "1.2 מיליארד ₪",
    responsibleParty: "משרד הבינוי והשיכון",
    timeline: "3 שנים",
    relatedDecisions: ["3675", "3912"],
    strengths: [
      "תיעדוף פוליטי גבוה",
      "תקציב משמעותי"
    ],
    weaknesses: [
      "חקיקה נדרשת מורכבת",
      "התנגדויות מצד בעלי עניין",
      "לוח זמנים לא ריאלי"
    ]
  },
  {
    id: "3",
    title: "התייעלות במערכת הבריאות",
    number: "4021",
    date: "23.09.2023",
    category: "בריאות",
    feasibilityScore: 84,
    implementationStatus: 60,
    description: "החלטה על תוכנית להתייעלות במערכת הבריאות הציבורית, כולל קיצור תורים, שיפור השירות וחיסכון בעלויות תפעול.",
    budget: "500 מיליון ₪",
    responsibleParty: "משרד הבריאות",
    timeline: "2 שנים",
    relatedDecisions: ["3890"],
    strengths: [
      "מטרות מדידות וברורות",
      "גורם אחראי מוגדר",
      "תקציב מוגדר"
    ],
    weaknesses: [
      "תלות בשינוי תרבות ארגונית"
    ]
  }
];
