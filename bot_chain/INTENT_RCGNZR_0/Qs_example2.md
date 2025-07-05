אני אקרא את הקבצים שציינת ואז אעזור לך לנסח מאגר שאלות נרחב לבדיקת ה-INTENT RECOGNIZER.בהתבסס על הקבצים שקראתי והמידע שסופק, אעזור לך לנסח מאגר שאלות נרחב לבדיקת ה-INTENT RECOGNIZER. אני מבין שיש לך דוגמאות מהקובץ שצירפת ואתה רוצה שאנסח אותן בפורמט הנכון.

## 📋 מאגר שאלות לבדיקת Intent Recognizer

### חיפושים בסיסיים (1-30)

1. **"החלטות על אנרגיה סולארית משנת 2020 והלאה"**
   - Expected: `{intent_type: "QUERY", entities: {topic: "אנרגיה סולארית", date_range: {start: "2020-01-01"}, operation: "search"}}`

2. **"איזה החלטות נוגעות ל-AI ב-2024?"**
   - Expected: `{intent_type: "QUERY", entities: {topic: "AI", date_range: {start: "2024-01-01", end: "2024-12-31"}, operation: "search"}}`

3. **"תראה לי 5 החלטות בנושא חינוך מיוחד"**
   - Expected: `{intent_type: "QUERY", entities: {limit: 5, topic: "חינוך מיוחד", operation: "search"}}`

4. **"תן את התוכן המלא של החלטה 2081 מממשלת 37"**
   - Expected: `{intent_type: "QUERY", entities: {decision_number: 2081, government_number: 37, operation: "full_content"}}`

5. **"החלטות תחבורה ציבורית בין 2010-2015"**
   - Expected: `{intent_type: "QUERY", entities: {topic: "תחבורה ציבורית", date_range: {start: "2010-01-01", end: "2015-12-31"}, operation: "search"}}`

6. **"החלטות שאושרו על-ידי ועדת שרים לחקיקה ב-2023"**
   - Expected: `{intent_type: "QUERY", entities: {committee: "ועדת שרים לחקיקה", date_range: {start: "2023-01-01", end: "2023-12-31"}, operation: "search"}}`

7. **"החלטות של בנימין נתניהו משנת 2022"**
   - Expected: `{intent_type: "QUERY", entities: {proposer: "בנימין נתניהו", date_range: {start: "2022-01-01"}, operation: "search"}}`

8. **"החלטות ממשלה 35 בתחום בריאות"**
   - Expected: `{intent_type: "QUERY", entities: {government_number: 35, topic: "בריאות", operation: "search"}}`

9. **"תוכן מלא של החלטה מספר 784 (לא אכפת לי הממשלה)"**
   - Expected: `{intent_type: "QUERY", entities: {decision_number: 784, operation: "full_content"}}`

10. **"החלטות על מס הכנסה בשנים 2000-2005 (עד 10 תוצאות)"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "מס הכנסה", date_range: {start: "2000-01-01", end: "2005-12-31"}, limit: 10, operation: "search"}}`

11. **"החלטות קנאביס רפואי"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "קנאביס רפואי", operation: "search"}}`

12. **"איזו החלטה אחרונה יש על שכר מורים?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "שכר מורים", limit: 1, operation: "search"}}`

13. **"החלטות מגזר ערבי מאוגוסט 2021"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "מגזר ערבי", date_range: {start: "2021-08-01", end: "2021-08-31"}, operation: "search"}}`

14. **"החלטות בנושא ביטחון סייבר משנת 2017"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "ביטחון סייבר", date_range: {start: "2017-01-01"}, operation: "search"}}`

15. **"תן לי 3 החלטות רווחה מ-1999"**
    - Expected: `{intent_type: "QUERY", entities: {limit: 3, topic: "רווחה", date_range: {start: "1999-01-01", end: "1999-12-31"}, operation: "search"}}`

16. **"החלטות של ממשלה 33 בחודש יוני 2014"**
    - Expected: `{intent_type: "QUERY", entities: {government_number: 33, date_range: {start: "2014-06-01", end: "2014-06-30"}, operation: "search"}}`

17. **"תוכן מלא של החלטה עם המפתח 36_1002"**
    - Expected: `{intent_type: "QUERY", entities: {decision_key: "36_1002", operation: "full_content"}}`

18. **"החלטות על תשתיות מים בין 1990-1995"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "תשתיות מים", date_range: {start: "1990-01-01", end: "1995-12-31"}, operation: "search"}}`

19. **"החלטות דקלרטיביות בשנת 2023"**
    - Expected: `{intent_type: "QUERY", entities: {decision_type: "דקלרטיבית", date_range: {start: "2023-01-01", end: "2023-12-31"}, operation: "search"}}`

20. **"מה היו החלטות אקלים ב-COP27 (2022-11)?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "אקלים", context: "COP27", date_range: {start: "2022-11-01", end: "2022-11-30"}, operation: "search"}}`

21. **"החלטות על דיור בר-השגה בתקופת אולמרט"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "דיור בר-השגה", time_period: "תקופת אולמרט", operation: "search"}}`

22. **"החלטות אופרטיביות בנושא רכבת קלה"**
    - Expected: `{intent_type: "QUERY", entities: {decision_type: "אופרטיבית", topic: "רכבת קלה", operation: "search"}}`

23. **"תוכנית של הממשלה בנושא כלכלה דיגיטלית (תוכן מלא אם יש)"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "כלכלה דיגיטלית", operation: "full_content"}}`

24. **"החלטות על הייטק שהתקבלו ברבעון ראשון 2024"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "הייטק", date_range: {start: "2024-01-01", end: "2024-03-31"}, operation: "search"}}`

25. **"הצע לי 2 החלטות סביבה מלפני 2010"**
    - Expected: `{intent_type: "QUERY", entities: {limit: 2, topic: "סביבה", date_range: {end: "2009-12-31"}, operation: "search"}}`

26. **"החלטות בנושא חיסונים בזמן קורונה (2020-2021)"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "חיסונים", context: "קורונה", date_range: {start: "2020-01-01", end: "2021-12-31"}, operation: "search"}}`

27. **"החלטות של ממשלת המעבר (מס' 36) בתחום חקלאות"**
    - Expected: `{intent_type: "QUERY", entities: {government_number: 36, topic: "חקלאות", operation: "search"}}`

28. **"תן לי החלטות שינויי אקלים עם תווית משפט"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "שינויי אקלים", tag: "משפט", operation: "search"}}`

29. **"החלטות שאושרו בתאריך 2025-03-15"**
    - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2025-03-15", end: "2025-03-15"}, operation: "search"}}`

30. **"החלטות על בינה מלאכותית שעדיין בסטטוס בטיפול"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "בינה מלאכותית", status: "בטיפול", operation: "search"}}`

### 🔢 שאילתות סטטיסטיות (31-40)

31. **"כמה החלטות בנושא סביבה היו ב-2024?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "סביבה", date_range: {start: "2024-01-01", end: "2024-12-31"}, operation: "count"}, route_flags: {is_statistical: true}}`

32. **"כמה החלטות התקבלו בכל רבעון בשנת 2023?"**
    - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2023-01-01", end: "2023-12-31"}, group_by: "quarter", operation: "statistics"}, route_flags: {is_statistical: true}}`

33. **"איזו שנה הייתה עם הכי הרבה החלטות על שכר מורים?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "שכר מורים", operation: "max_year"}, route_flags: {is_statistical: true}}`

34. **"כמה החלטות מגזר ערבי התקבלו באוגוסט 2021?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "מגזר ערבי", date_range: {start: "2021-08-01", end: "2021-08-31"}, operation: "count"}, route_flags: {is_statistical: true}}`

35. **"כמה החלטות בתחום ביטחון סייבר התקבלו מאז 2017?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "ביטחון סייבר", date_range: {start: "2017-01-01"}, operation: "count"}, route_flags: {is_statistical: true}}`

36. **"כמה החלטות חקלאות התקבלו בממשלת המעבר (36)?"**
    - Expected: `{intent_type: "QUERY", entities: {government_number: 36, topic: "חקלאות", operation: "count"}, route_flags: {is_statistical: true}}`

37. **"כמה החלטות אושרו בתאריך 2025-03-15?"**
    - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2025-03-15", end: "2025-03-15"}, operation: "count"}, route_flags: {is_statistical: true}}`

38. **"מה מספר ההחלטות של משרד החוץ בשנת 2023?"**
    - Expected: `{intent_type: "QUERY", entities: {ministries: ["משרד החוץ"], date_range: {start: "2023-01-01", end: "2023-12-31"}, operation: "count"}, route_flags: {is_statistical: true}}`

39. **"כמה החלטות יש בסך הכל בנושא תיירות?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "תיירות", operation: "count"}, route_flags: {is_statistical: true}}`

40. **"מה היחס בין החלטות תעסוקת צעירים שהושלמו לאלו שבטיפול כיום?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "תעסוקת צעירים", operation: "status_ratio"}, route_flags: {is_statistical: true}}`

### 🔄 שאילתות השוואה (41-54)

41. **"השווה בין כמות החלטות דקלרטיביות ואופרטיביות בשנת 2023"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", comparison_target: "decision_types:דקלרטיבית,אופרטיבית", date_range: {start: "2023-01-01", end: "2023-12-31"}}, route_flags: {is_comparison: true}}`

42. **"מה ההבדל בין החלטות אקלים ב-COP26 (2021-11) לבין COP27 (2022-11)?"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "אקלים", comparison_target: "periods:2021-11,2022-11", contexts: ["COP26", "COP27"]}, route_flags: {is_comparison: true}}`

43. **"השווה מספר החלטות דיור בר-השגה בין תקופת אולמרט ונתניהו"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "דיור בר-השגה", comparison_target: "periods:אולמרט,נתניהו"}, route_flags: {is_comparison: true}}`

44. **"השווה את קצב קבלת החלטות רכבת קלה ברבעון 1 לעומת 3 של 2024"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "רכבת קלה", comparison_target: "quarters:2024-Q1,2024-Q3"}, route_flags: {is_comparison: true}}`

45. **"השווה את סך ההחלטות בנושא כלכלה דיגיטלית בממשלות 34 ו-35"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "כלכלה דיגיטלית", comparison_target: "governments:34,35"}, route_flags: {is_comparison: true}}`

46. **"השווה בין מספר החלטות חיסונים ב-2020 לעומת 2021"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "חיסונים", comparison_target: "years:2020,2021"}, route_flags: {is_comparison: true}}`

47. **"השווה את סטטוס החלטות בינה מלאכותית (בטיפול ↔︎ הושלמו)"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "בינה מלאכותית", comparison_target: "status:בטיפול,הושלמו"}, route_flags: {is_comparison: true}}`

48. **"השווה את כמות החלטות דיור בר-השגה בין 2018 ל-2024"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "דיור בר-השגה", comparison_target: "years:2018,2024"}, route_flags: {is_comparison: true}}`

49. **"מה ההבדל בין החלטות אנרגיה מתחדשת בממשלות 34 ו-37?"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "אנרגיה מתחדשת", comparison_target: "governments:34,37"}, route_flags: {is_comparison: true}}`

50. **"השווה בין החלטות תמיכת עסקים קטנים לפני ואחרי משבר 2020"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "תמיכת עסקים קטנים", comparison_target: "periods:pre-2020,post-2020"}, route_flags: {is_comparison: true}}`

51. **"השווה את קצב החלטות סבסוד חקלאות בין Q1-2022 ו-Q1-2023"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "סבסוד חקלאות", comparison_target: "quarters:2022-Q1,2023-Q1"}, route_flags: {is_comparison: true}}`

52. **"השווה בין החלטות הפחתת פליטת מזהמים לשנים 2019 ו-2022"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "הפחתת פליטת מזהמים", comparison_target: "years:2019,2022"}, route_flags: {is_comparison: true}}`

53. **"השווה בין החלטות הטבות מס לעולים חדשים בממשלות 33 ו-36"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", topic: "הטבות מס לעולים חדשים", comparison_target: "governments:33,36"}, route_flags: {is_comparison: true}}`

54. **"השווה סובסידיות מים לחקלאים מול ציוד חקלאי (2018-2021)"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "compare", comparison_target: "topics:סובסידיות מים לחקלאים,ציוד חקלאי", date_range: {start: "2018-01-01", end: "2021-12-31"}}, route_flags: {is_comparison: true}}`

### 🔍 שאילתות נוספות למקרי קצה (55-84)

55. **"אילו החלטות ממשלה עוסקות בהעלאת שכר המינימום מאז 2022?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "העלאת שכר המינימום", date_range: {start: "2022-01-01"}, operation: "search"}}`

56. **"תוכן מלא של החלטה מס' 3012 מממשלת 36"**
    - Expected: `{intent_type: "QUERY", entities: {decision_number: 3012, government_number: 36, operation: "full_content"}}`

57. **"כמה החלטות על הרחבת תחבורה ציבורית התקבלו ברבעון השני של 2023?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "הרחבת תחבורה ציבורית", date_range: {start: "2023-04-01", end: "2023-06-30"}, operation: "count"}, route_flags: {is_statistical: true}}`

58. **"אילו החלטות מתייחסות לשיפור שירותי בריאות בפריפריה?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "שיפור שירותי בריאות בפריפריה", operation: "search"}}`

59. **"כמה החלטות בנושא בטיחות בדרכים התקבלו ב-2021?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "בטיחות בדרכים", date_range: {start: "2021-01-01", end: "2021-12-31"}, operation: "count"}, route_flags: {is_statistical: true}}`

60. **"תוכן מלא של החלטה עם קוד 37_455"**
    - Expected: `{intent_type: "QUERY", entities: {decision_key: "37_455", operation: "full_content"}}`

61. **"החלטות שעוסקות בחינוך טכנולוגי לילדי יסודי"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "חינוך טכנולוגי", context: "ילדי יסודי", operation: "search"}}`

62. **"כמה החלטות רפורמת מס פורסמו במהלך 2024?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "רפורמת מס", date_range: {start: "2024-01-01", end: "2024-12-31"}, operation: "count"}, route_flags: {is_statistical: true}}`

63. **"תן 3 החלטות אופרטיביות בנושא שיקום נחלים"**
    - Expected: `{intent_type: "QUERY", entities: {limit: 3, decision_type: "אופרטיבית", topic: "שיקום נחלים", operation: "search"}}`

64. **"תוכן מלא של החלטה מ-2020 על הארכת חופשת לידה"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "הארכת חופשת לידה", date_range: {start: "2020-01-01", end: "2020-12-31"}, operation: "full_content"}}`

65. **"אילו החלטות על שימור אתרים היסטוריים התקבלו בשנה האחרונה?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "שימור אתרים היסטוריים", date_range: {start: "2024-07-02", end: "2025-07-02"}, operation: "search"}}`

66. **"כמה החלטות רווחה קשישי התקבלו בין 2015-2019?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "רווחה קשישי", date_range: {start: "2015-01-01", end: "2019-12-31"}, operation: "count"}, route_flags: {is_statistical: true}}`

67. **"הצג את התוכן המלא של ההחלטה האחרונה בנושא מניעת אלימות במשפחה"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "מניעת אלימות במשפחה", limit: 1, operation: "full_content"}}`

68. **"תוכן מלא של החלטה בנושא שירות אזרחי בממשלת 35"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "שירות אזרחי", government_number: 35, operation: "full_content"}}`

69. **"כמה החלטות על תשתיות מים התקבלו בקיץ 2023?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "תשתיות מים", date_range: {start: "2023-06-21", end: "2023-09-23"}, operation: "count"}, route_flags: {is_statistical: true}}`

70. **"החלטות על הגנת סייבר במגזר הציבורי שעדיין ממתינות ליישום"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "הגנת סייבר במגזר הציבורי", status: "ממתין ליישום", operation: "search"}}`

71. **"החלטות על פריסת רשת 5G בפריפריה שעדיין בסטטוס בטיפול"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "פריסת רשת 5G בפריפריה", status: "בטיפול", operation: "search"}}`

72. **"37 החלטות של הממשלה"**
    - Expected: `{intent_type: "QUERY", entities: {limit: 37, operation: "search"}}`

73. **"הבא לי כל החלטה שקשורה למים וחקלאות יחד"**
    - Expected: `{intent_type: "QUERY", entities: {topics: ["מים", "חקלאות"], operation: "search"}}`

74. **"מה קורה עם תקציב הביטחון בשנתיים האחרונות?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "תקציב הביטחון", date_range: {start: "2023-07-02", end: "2025-07-02"}, operation: "search"}}`

75. **"החלטות עם תקציב מעל מיליארד שקל"**
    - Expected: `{intent_type: "QUERY", entities: {budget_threshold: 1000000000, operation: "search"}}`

76. **"כל ההחלטות שהתקבלו ביום חמישי"**
    - Expected: `{intent_type: "QUERY", entities: {day_of_week: "חמישי", operation: "search"}}`

77. **"החלטות דחופות מהחודש האחרון"**
    - Expected: `{intent_type: "QUERY", entities: {urgency: "דחוף", date_range: {start: "2025-06-02", end: "2025-07-02"}, operation: "search"}}`

78. **"איזה החלטות בוטלו השנה?"**
    - Expected: `{intent_type: "QUERY", entities: {status: "בוטל", date_range: {start: "2025-01-01", end: "2025-12-31"}, operation: "search"}}`

79. **"רשימת כל השרים שהציעו החלטות בנושא חינוך"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "חינוך", operation: "list_proposers"}, route_flags: {is_statistical: true}}`

80. **"איזה נושאים הכי פופולריים בממשלה 37?"**
    - Expected: `{intent_type: "QUERY", entities: {government_number: 37, operation: "top_topics"}, route_flags: {is_statistical: true}}`

81. **"החלטות שעברו פה אחד"**
    - Expected: `{intent_type: "QUERY", entities: {voting: "פה אחד", operation: "search"}}`

82. **"תן לי דוגמאות להחלטות על נושאים חברתיים"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "נושאים חברתיים", operation: "search"}}`

83. **"מה ההחלטה הכי חדשה?"**
    - Expected: `{intent_type: "QUERY", entities: {limit: 1, operation: "search"}}`

84. **"החלטות שקשורות גם לחינוך וגם לתקציב"**
    - Expected: `{intent_type: "QUERY", entities: {topics: ["חינוך", "תקציב"], operation: "search"}}`

### 🤔 שאילתות הבהרה (85-94) - התבסס על הדוגמאות שסיפקת

85. **"צריך משהו על חינוך"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_topic: "חינוך"}, route_flags: {needs_clarification: true}}`

86. **"החלטה החדשה על מס"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_topic: "מס", time_reference: "החדשה"}, route_flags: {needs_clarification: true}}`

87. **"כמה החלטות יש על ביטחון?"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_topic: "ביטחון", operation: "count"}, route_flags: {needs_clarification: true}}`

88. **"השווה החלטות סביבה"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_topic: "סביבה", operation: "compare"}, route_flags: {needs_clarification: true}}`

89. **"תן החלטות על דיור"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_topic: "דיור"}, route_flags: {needs_clarification: true}}`

90. **"רוצה לראות את ההחלטה על החוק החדש"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_reference: "החוק החדש"}, route_flags: {needs_clarification: true}}`

91. **"מה עם תחבורה ברבעון האחרון?"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_topic: "תחבורה", time_reference: "רבעון האחרון"}, route_flags: {needs_clarification: true}}`

92. **"יש נתונים על רווחה?"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_topic: "רווחה"}, route_flags: {needs_clarification: true}}`

93. **"השווה החלטות תמיכה"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_topic: "תמיכה", operation: "compare"}, route_flags: {needs_clarification: true}}`

94. **"תן לי החלטות על אנרגיה"**
    - Expected: `{intent_type: "CLARIFICATION", entities: {unclear_topic: "אנרגיה"}, route_flags: {needs_clarification: true}}`

### 🎯 שאילתות מורכבות ומקרי קצה (95-110)

95. **"כל ההחלטות מהשבוע שעבר שקשורות לתשתיות או לתחבורה אבל לא לרכבות"**
    - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2025-06-25", end: "2025-07-01"}, topics: ["תשתיות", "תחבורה"], exclude_topics: ["רכבות"], operation: "search"}}`

96. **"תן לי סיכום של כל ההחלטות החשובות מהחודש האחרון"**
    - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2025-06-02", end: "2025-07-02"}, importance: "high", operation: "summary"}}`

97. **"איזה משרדי ממשלה הכי פעילים בהצעת החלטות?"**
    - Expected: `{intent_type: "QUERY", entities: {operation: "ministry_activity_ranking"}, route_flags: {is_statistical: true}}`

98. **"החלטות שהתקבלו בלילה או בסוף השבוע"**
    - Expected: `{intent_type: "QUERY", entities: {time_filter: "night_or_weekend", operation: "search"}}`

99. **"מה אחוז ההחלטות שעוסקות בפריפריה מתוך כלל ההחלטות?"**
    - Expected: `{intent_type: "QUERY", entities: {topic: "פריפריה", operation: "percentage"}, route_flags: {is_statistical: true}}`

100. **"תראה לי את ההתפתחות של נושא הסביבה לאורך השנים"**
     - Expected: `{intent_type: "QUERY", entities: {topic: "סביבה", operation: "trend_analysis"}, route_flags: {is_statistical: true}}`

101. **"החלטות שמשפיעות על יותר ממיליון אזרחים"**
     - Expected: `{intent_type: "QUERY", entities: {impact_threshold: 1000000, operation: "search"}}`

102. **"כל ההחלטות שיש להן דדליין בחודש הקרוב"**
     - Expected: `{intent_type: "QUERY", entities: {deadline_range: {start: "2025-07-02", end: "2025-08-02"}, operation: "search"}}`

103. **"החלטות שקיבלו התנגדות מהאופוזיציה"**
     - Expected: `{intent_type: "QUERY", entities: {opposition: true, operation: "search"}}`

104. **"מה ההחלטה עם התקציב הכי גבוה השנה?"**
     - Expected: `{intent_type: "QUERY", entities: {date_range: {start: "2025-01-01", end: "2025-12-31"}, operation: "max_budget"}, route_flags: {is_statistical: true}}`

105. **"החלטות שעדיין לא יושמו למרות שעבר המועד"**
     - Expected: `{intent_type: "QUERY", entities: {status: "לא יושם", overdue: true, operation: "search"}}`

106. **"תן לי ניתוח של כל ההחלטות שקשורות למשבר האקלים"**
     - Expected: `{intent_type: "EVAL", entities: {topic: "משבר האקלים", operation: "analyze"}}`

107. **"איך התקדמות החלטות הדיגיטציה בממשלה?"**
     - Expected: `{intent_type: "QUERY", entities: {topic: "דיגיטציה", operation: "progress_report"}}`

108. **"החלטות שהועברו מממשלה קודמת ועדיין רלוונטיות"**
     - Expected: `{intent_type: "QUERY", entities: {transferred: true, status: "רלוונטי", operation: "search"}}`

109. **"מה קורה עם כל ההבטחות הקואליציוניות?"**
     - Expected: `{intent_type: "QUERY", entities: {category: "הבטחות קואליציוניות", operation: "status_check"}}`

110. **"תראה לי החלטות שגרמו למחלוקת ציבורית"**
     - Expected: `{intent_type: "QUERY", entities: {public_controversy: true, operation: "search"}}`

## 📊 סיכום המאגר

**סה"כ 110 שאלות לבדיקה המכסות:**
- ✅ 30 חיפושים בסיסיים
- ✅ 10 שאילתות סטטיסטיות  
- ✅ 14 שאילתות השוואה
- ✅ 30 שאלות נוספות למקרי קצה
- ✅ 10 שאילתות הבהרה (CLARIFICATION)
- ✅ 16 שאילתות מורכבות ומקרי קצה

המאגר מכסה מגוון רחב של:
- סוגי Intent (QUERY, STATISTICAL, EVAL, COMPARISON, CLARIFICATION)
- סוגי Operation (search, full_content, count, statistics, compare, analyze)
- שדות entities (topic, date_range, government_number, limit, ministries, status, וכו')
- Route flags (is_statistical, is_comparison, needs_clarification)
- מקרי קצה ושילובים מורכבים