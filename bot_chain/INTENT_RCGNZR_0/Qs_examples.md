# 🎯 30 וריאציות של שאילתות QUERY לבדיקת Intent Detector

## 📋 חיפושים בסיסיים (1-10)

1. **"החלטות ממשלה 37"**
   - Expected: `{intent_type: "QUERY", entities: {government_number: 37, operation: "search"}}`

2. **"כל ההחלטות בנושא חינוך"**
   - Expected: `{intent_type: "QUERY", entities: {topic: "חינוך", operation: "search"}}`

3. **"החלטות משרד הביטחון"**
   - Expected: `{intent_type: "QUERY", entities: {ministries: ["משרד הביטחון"], operation: "search"}}`

4. **"5 החלטות אחרונות"**
   - Expected: `{intent_type: "QUERY", entities: {limit: 5, operation: "search"}}`

5. **"הצג לי החלטות בנושא תחבורה"**
   - Expected: `{intent_type: "QUERY", entities: {topic: "תחבורה", operation: "search"}}`

6. **"תן לי את כל ההחלטות מינואר 2024"**
   - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2024-01-01", end: "2024-01-31"}, operation: "search"}}`

7. **"רשימת החלטות ממשלה שלושים ושבע"**
   - Expected: `{intent_type: "QUERY", entities: {government_number: 37, operation: "search"}}`

8. **"מצא החלטות על בריאות"**
   - Expected: `{intent_type: "QUERY", entities: {topic: "בריאות", operation: "search"}}`

9. **"החלטות בין 01/01/2024 ל-31/03/2024"**
   - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2024-01-01", end: "2024-03-31"}, operation: "search"}}`

10. **"החלטה 2983 של ממשלה 37"**
    - Expected: `{intent_type: "QUERY", entities: {government_number: 37, decision_number: 2983, operation: "search"}}`

## 🔢 שאילתות סטטיסטיות (11-20)

11. **"כמה החלטות יש בנושא חינוך?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "חינוך", operation: "count"}, route_flags: {is_statistical: true}}`

12. **"מספר ההחלטות של ממשלה 37"**
    - Expected: `{intent_type: "QUERY", entities: {government_number: 37, operation: "count"}, route_flags: {is_statistical: true}}`

13. **"כמה החלטות התקבלו השנה?"**
    - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2025-01-01", end: "2025-12-31"}, operation: "count"}, route_flags: {is_statistical: true}}`

14. **"מה מספר ההחלטות של משרד האוצר?"**
    - Expected: `{intent_type: "QUERY", entities: {ministries: ["משרד האוצר"], operation: "count"}, route_flags: {is_statistical: true}}`

15. **"כמה פעמים דנו בנושא דיור?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "דיור", operation: "count"}, route_flags: {is_statistical: true}}`

16. **"סה״כ החלטות בחודש האחרון"**
    - Expected: `{intent_type: "QUERY", entities: {date_range: {...}, operation: "count"}, route_flags: {is_statistical: true}}`

17. **"בסך הכל כמה החלטות בנושא ביטחון?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "ביטחון", operation: "count"}, route_flags: {is_statistical: true}}`

18. **"מספר החלטות משרד החינוך ומשרד הבריאות"**
    - Expected: `{intent_type: "QUERY", entities: {ministries: ["משרד החינוך", "משרד הבריאות"], operation: "count"}, route_flags: {is_statistical: true}}`

19. **"כמה החלטות עברו בממשלה עשרים ואחת?"**
    - Expected: `{intent_type: "QUERY", entities: {government_number: 21, operation: "count"}, route_flags: {is_statistical: true}}`

20. **"מה הכמות של החלטות בנושא כלכלה?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "כלכלה", operation: "count"}, route_flags: {is_statistical: true}}`

## 🔄 שאילתות השוואה (21-25)

21. **"השווה בין ממשלה 36 לממשלה 37"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", comparison_target: "governments:36,37"}, route_flags: {is_comparison: true}}`

22. **"מה ההבדל בין החלטות 2023 ל-2024?"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", comparison_target: "years:2023,2024"}, route_flags: {is_comparison: true}}`

23. **"השוואת החלטות משרד החינוך מול משרד הבריאות"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", ministries: ["משרד החינוך", "משרד הבריאות"]}, route_flags: {is_comparison: true}}`

24. **"החלטות בנושא תחבורה לעומת החלטות בנושא דיור"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", comparison_target: "topics:תחבורה,דיור"}, route_flags: {is_comparison: true}}`

25. **"ההבדלים בין ממשלה שלושים לממשלה ארבעים"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", comparison_target: "governments:30,40"}, route_flags: {is_comparison: true}}`

## 🔍 שאילתות מורכבות (26-30)

26. **"החלטות ממשלה 37 בנושא חינוך מינואר 2024"**
    - Expected: `{intent_type: "QUERY", entities: {government_number: 37, topic: "חינוך", date_range: {start: "2024-01-01", end: "2024-01-31"}, operation: "search"}}`

27. **"10 החלטות אחרונות של משרד הביטחון בנושא תקציב"**
    - Expected: `{intent_type: "QUERY", entities: {limit: 10, ministries: ["משרד הביטחון"], topic: "תקציב", operation: "search"}}`

28. **"כמה החלטות בנושא בריאות התקבלו בין ינואר למרץ 2024?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "בריאות", date_range: {start: "2024-01-01", end: "2024-03-31"}, operation: "count"}, route_flags: {is_statistical: true}}`

29. **"החלטות משרד החוץ ומשרד הביטחון השנה"**
    - Expected: `{intent_type: "QUERY", entities: {ministries: ["משרד החוץ", "משרד הביטחון"], date_range: {start: "2025-01-01", end: "2025-12-31"}, operation: "search"}}`

30. **"חפש לי 20 החלטות על נושא סביבה מממשלה 35 עד ממשלה 37"**
    - Expected: `{intent_type: "QUERY", entities: {limit: 20, topic: "סביבה", government_range: {start: 35, end: 37}, operation: "search"}}`

---

## 📝 הערות לבדיקה:

1. **כל השאילתות הללו צריכות להחזיר `intent_type: "QUERY"`**
2. **שאילתות 11-20 צריכות גם `route_flags.is_statistical: true`**
3. **שאילתות 21-25 צריכות גם `route_flags.is_comparison: true`**
4. **שים לב לנרמול של:**
   - מספרים בעברית (שלושים ושבע → 37)
   - שמות משרדים (הביטחון → משרד הביטחון)
   - תאריכים יחסיים (השנה → 2025-01-01 עד 2025-12-31)
5. **ה-operation field חשוב מאוד** - הוא מגדיר איך SQL Gen Bot יבנה את השאילתא



# 🔗 30 וריאציות של שאילתות REFERENCE לבדיקת Intent Detector

## 📌 התייחסות ישירה לתוכן שנשלח (1-10)

1. **"ההחלטה ששלחת לי"**
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last", reference_position: 1}, route_flags: {needs_context: true}}`

2. **"מה היה בהחלטה האחרונה שהצגת?"**
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last", reference_position: 1}, route_flags: {needs_context: true}}`

3. **"תן לי עוד פרטים על ההחלטה הקודמת"**
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "previous", reference_position: 1}, route_flags: {needs_context: true}}`

4. **"ההחלטה הראשונה ששלחת"**
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "specific", reference_position: 1}, route_flags: {needs_context: true}}`

5. **"החלטה מספר 3 מהרשימה שנתת"**
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "specific", reference_position: 3}, route_flags: {needs_context: true}}`

6. **"ההחלטה השנייה שהראית לי"**
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "specific", reference_position: 2}, route_flags: {needs_context: true}}`

7. **"אני רוצה לראות שוב את ההחלטה ששלחת"**
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last", reference_position: 1}, route_flags: {needs_context: true}}`

8. **"מה זה היה ההחלטה האחרונה?"**
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last", reference_position: 1}, route_flags: {needs_context: true}}`

9. **"ההחלטות שהבאת קודם"**
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "previous"}, route_flags: {needs_context: true}}`

10. **"התוצאה הרביעית ברשימה"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "specific", reference_position: 4}, route_flags: {needs_context: true}}`

## 🔄 המשך שיחה והרחבות (11-20)

11. **"עוד החלטות כמו ששאלתי קודם"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

12. **"בהמשך למה שביקשתי"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

13. **"עוד כמו האחרונה"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last", reference_position: 1}, route_flags: {needs_context: true}}`

14. **"דומות להחלטה ששלחת"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last", reference_position: 1}, route_flags: {needs_context: true}}`

15. **"באותו נושא כמו קודם"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

16. **"כמו שדיברנו עליו"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

17. **"עוד מאותה ממשלה"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

18. **"החלטות נוספות באותו תחום"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

19. **"כפי ששאלתי בהתחלה"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

20. **"בדיוק כמו הבקשה הקודמת שלי"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

## 🎯 REFERENCE שמוביל ל-EVAL (21-25)

21. **"נתח את ההחלטה האחרונה ששלחת"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last", reference_position: 1}, route_flags: {needs_context: true}}`
    - Note: Context Router יזהה שזה צריך להוביל ל-EVAL

22. **"אני רוצה ניתוח של ההחלטה השנייה ברשימה"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "specific", reference_position: 2}, route_flags: {needs_context: true}}`

23. **"הסבר לי את ההשלכות של ההחלטה הקודמת"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "previous", reference_position: 1}, route_flags: {needs_context: true}}`

24. **"ניתוח מעמיק של מה ששלחת"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last"}, route_flags: {needs_context: true}}`

25. **"פרט יותר על ההחלטה הראשונה"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "specific", reference_position: 1}, route_flags: {needs_context: true}}`

## 🌐 שאילתות עם הקשר זמני ומרחבי (26-30)

26. **"מה ששאלתי קודם על חינוך"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context", topic: "חינוך"}, route_flags: {needs_context: true}}`

27. **"ההחלטות מאתמול"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

28. **"כמו שביקשתי לפני כמה דקות"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}, route_flags: {needs_context: true}}`

29. **"חזור על התוצאות האחרונות"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last"}, route_flags: {needs_context: true}}`

30. **"הצג שוב את מה שמצאת"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last"}, route_flags: {needs_context: true}}`

---

## 📝 הערות חשובות לבדיקה:

### 1. **כל השאילתות חייבות להחזיר:**
- `intent_type: "REFERENCE"`
- `route_flags.needs_context: true`

### 2. **סוגי reference_type:**
- **"last"** - התייחסות לאחרון שנשלח
- **"previous"** - התייחסות לקודם (כללי)
- **"specific"** - התייחסות למיקום ספציפי (עם reference_position)
- **"context"** - התייחסות להקשר השיחה

### 3. **Context Router צריך לזהות:**
- האם זה REFERENCE שמוביל ל-QUERY (רוב המקרים)
- האם זה REFERENCE שמוביל ל-EVAL (שאילתות 21-25)

### 4. **מילות מפתח קריטיות לזיהוי:**
```javascript
const CRITICAL_KEYWORDS = [
  "ששלחת", "שהצגת", "שהראית", "שנתת",
  "האחרונה", "הקודמת", "הראשונה", "השנייה",
  "קודם", "מקודם", "לפני",
  "כמו ש", "כפי ש", "בהמשך ל",
  "עוד כמו", "דומות ל", "באותו"
];
```

### 5. **Edge Cases לשים לב:**
- "עוד" בתחילת משפט - כמעט תמיד REFERENCE
- מספרים סידוריים (ראשונה, שנייה) - בדוק אם יש הקשר
- "מה ש..." - לרוב מצביע על REFERENCE

### 6. **Validation:**
- REFERENCE תמיד דורש session context
- אם אין היסטוריה - צריך להפוך ל-CLARIFICATION
- Context Router חייב להיות מופעל



# 🔬 30 וריאציות של שאילתות EVAL לבדיקת Intent Detector

## 🎯 ניתוח החלטות ספציפיות (1-10)

1. **"נתח את החלטה 2983"**
   - Expected: `{intent_type: "EVAL", entities: {decision_number: 2983}}`

2. **"ניתוח מעמיק של החלטה 1547"**
   - Expected: `{intent_type: "EVAL", entities: {decision_number: 1547}}`

3. **"אני רוצה ניתוח של החלטה 660 ממשלה 37"**
   - Expected: `{intent_type: "EVAL", entities: {decision_number: 660, government_number: 37}}`

4. **"תן לי ניתוח מפורט של החלטת ממשלה 2150"**
   - Expected: `{intent_type: "EVAL", entities: {decision_number: 2150}}`

5. **"נתח לי את החלטה מספר 3421"**
   - Expected: `{intent_type: "EVAL", entities: {decision_number: 3421}}`

6. **"ניתוח החלטת הממשלה 1823"**
   - Expected: `{intent_type: "EVAL", entities: {decision_number: 1823}}`

7. **"בחן לעומק את החלטה 975"**
   - Expected: `{intent_type: "EVAL", entities: {decision_number: 975}}`

8. **"ניתוח יסודי של החלטה 2641"**
   - Expected: `{intent_type: "EVAL", entities: {decision_number: 2641}}`

9. **"הסבר לעומק את החלטה 1122"**
   - Expected: `{intent_type: "EVAL", entities: {decision_number: 1122}}`

10. **"פרט באופן מעמיק על החלטה 3089"**
    - Expected: `{intent_type: "EVAL", entities: {decision_number: 3089}}`




# 🔀 30 שאילתות משולבות - מסלולים מעורבים

## 🔄 QUERY → REFERENCE → EVAL (1-5)

1. **שלב 1:** "החלטות ממשלה 37 בנושא חינוך"
   - Expected: `{intent_type: "QUERY", entities: {government_number: 37, topic: "חינוך"}}`
   
   **שלב 2:** "נתח את ההחלטה השנייה ששלחת"
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "specific", reference_position: 2}}`
   - Context Router → EVAL

2. **שלב 1:** "5 החלטות אחרונות בנושא בריאות"
   - Expected: `{intent_type: "QUERY", entities: {limit: 5, topic: "בריאות"}}`
   
   **שלב 2:** "אני רוצה ניתוח מעמיק של האחרונה"
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "last"}}`
   - Context Router → EVAL

3. **שלב 1:** "כמה החלטות יש בנושא תחבורה?"
   - Expected: `{intent_type: "QUERY", entities: {topic: "תחבורה", operation: "count"}}`
   
   **שלב 2:** "תן לי את כולן"
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}}`
   - Context Router → QUERY

## ❓ CLARIFICATION → QUERY → EVAL (6-10)

4. **שלב 1:** "חינוך"
   - Expected: `{intent_type: "CLARIFICATION"}`
   
   **שלב 2:** "החלטות בנושא חינוך מהשנה האחרונה"
   - Expected: `{intent_type: "QUERY", entities: {topic: "חינוך", date_range: {...}}}`
   
   **שלב 3:** "נתח את הראשונה"
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "specific", reference_position: 1}}`

5. **שלב 1:** "מה?"
   - Expected: `{intent_type: "CLARIFICATION"}`
   
   **שלב 2:** "מה ההחלטות האחרונות?"
   - Expected: `{intent_type: "QUERY", entities: {operation: "search"}}`

## 📊 QUERY (Statistical) → QUERY (Search) → EVAL (11-15)

6. **שלב 1:** "כמה החלטות של משרד הביטחון השנה?"
   - Expected: `{intent_type: "QUERY", entities: {ministries: ["משרד הביטחון"], operation: "count"}}`
   
   **שלב 2:** "הראה לי את כולן"
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}}`
   
   **שלב 3:** "נתח את החשובה ביותר"
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}}`

7. **שלב 1:** "השווה בין ממשלה 36 ל-37 בנושא כלכלה"
   - Expected: `{intent_type: "QUERY", entities: {operation: "compare", comparison_target: "governments:36,37", topic: "כלכלה"}}`
   
   **שלב 2:** "מה ההבדלים העיקריים?"
   - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}}`

## 🎯 שאילתות מורכבות עם מעברים מרובים (16-20)

8. **"נתח את 3 ההחלטות האחרונות בנושא ביטחון"**
   - Expected: `{intent_type: "QUERY", entities: {limit: 3, topic: "ביטחון"}}`
   - Note: למרות המילה "נתח", זה QUERY כי אין החלטה ספציפית

9. **"כמה החלטות יש ותן לי ניתוח של האחרונה"**
   - Expected: `{intent_type: "CLARIFICATION"}`
   - Reason: שאילתא מורכבת מדי, צריך לפצל

10. **"החלטות ממשלה בנושא שדיברנו עליו"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}}`
    - Context Router → QUERY

## 🔗 Edge Cases ושילובים מיוחדים (21-25)

11. **"נתח"**
    - Expected: `{intent_type: "CLARIFICATION"}`
    - Reason: חסר מידע - איזו החלטה?

12. **"עוד"**
    - Expected: `{intent_type: "CLARIFICATION"}`
    - Reason: עמום מדי, אבל אם יש הקשר → REFERENCE

13. **"החלטה 123 או אולי 456"**
    - Expected: `{intent_type: "CLARIFICATION"}`
    - Reason: לא ברור איזו החלטה

14. **"כל מה שקשור לחינוך וגם ניתוח של החשובות"**
    - Expected: `{intent_type: "CLARIFICATION"}`
    - Reason: בקשה מורכבת מדי

15. **"מה ההבדל בין מה ששאלתי קודם למה שאני שואל עכשיו?"**
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}}`
    - Very complex reference

## 🎭 תרחישי שיחה מלאים (26-30)

16. **תרחיש 1: חיפוש → ספירה → ניתוח**
    - User: "החלטות על סביבה"
    - Bot: [מחזיר 20 תוצאות]
    - User: "כמה מהן מ-2024?"
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}}`
    - User: "נתח את הכי חדשה"
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}}`

17. **תרחיש 2: לא ברור → הבהרה → חיפוש → ניתוח**
    - User: "ביטחון"
    - Expected: `{intent_type: "CLARIFICATION"}`
    - Bot: "האם התכוונת להחלטות בנושא ביטחון?"
    - User: "כן, מהשנה האחרונה"
    - Expected: `{intent_type: "QUERY", entities: {topic: "ביטחון", date_range: {...}}}`

18. **תרחיש 3: השוואה מורכבת**
    - User: "השווה בין כל הממשלות בנושא חינוך"
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "חינוך"}}`
    - User: "איזו ממשלה הכי פעילה?"
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context"}}`

19. **תרחיש 4: ניתוח מרובה**
    - User: "נתח את כל ההחלטות של היום"
    - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2025-07-01", end: "2025-07-01"}}}`
    - Note: "נתח את כל" → QUERY, לא EVAL

20. **תרחיש 5: Reference chains**
    - User: "החלטות ממשלה 37"
    - User: "עוד כמו אלה"
    - Expected: `{intent_type: "REFERENCE"}`
    - User: "אבל רק מ-2024"
    - Expected: `{intent_type: "REFERENCE", entities: {reference_type: "context", date_range: {...}}}`

---

## 📝 כללי זיהוי קריטיים:

### 1. **"נתח" לא תמיד EVAL:**
- "נתח את החלטה 123" → EVAL ✓
- "נתח את כל ההחלטות" → QUERY ✗
- "נתח את התוצאות" → REFERENCE

### 2. **Context מכריע:**
- "עוד" בלי הקשר → CLARIFICATION
- "עוד" עם הקשר → REFERENCE

### 3. **שאילתות מורכבות:**
- יותר משני מסלולים → CLARIFICATION
- בקשות סותרות → CLARIFICATION

### 4. **Priority Order:**
```
REFERENCE (אם יש הקשר) > 
EVAL (אם יש החלטה ספציפית) > 
QUERY (ברירת מחדל לחיפושים) > 
CLARIFICATION (כשלא ברור)
```

### 5. **Statistical vs EVAL:**
- "כמה החלטות" → QUERY (statistical)
- "נתח כמה החלטות יש" → QUERY (לא EVAL!)