# Decision Guide Bot Consistency Test Instructions

## Test Objective
Verify that the Decision Guide Bot now produces consistent scores when analyzing the same document multiple times.

## Fix Applied
- Changed temperature from 0.3 to 0.0 in `bot_chain/DECISION_GUIDE_BOT/main.py`
- Added consistency instructions to the prompt

## Manual Test Steps

1. Go to https://ceci-ai.ceci.org.il
2. Click on "מדריך החלטות" (Decision Guide) in the UI
3. Use this test text:

```
החלטת ממשלה מס' 1234 בנושא שיפור החינוך

הממשלה מחליטה:

1. להקים צוות בין-משרדי בראשות מנכ"ל משרד החינוך
2. להקצות סך של 50 מיליון ש"ח מתקציב המדינה
3. הצוות יגיש דו"ח תוך 6 חודשים מיום קבלת ההחלטה
4. משרד החינוך יפעל בשיתוף משרד הכלכלה
5. יוקם מנגנון מעקב רבעוני
```

4. Submit the analysis
5. Note down the scores for these key criteria:
   - לוח זמנים מחייב
   - משאבים נדרשים
   - מנגנון דיווח/בקרה

6. Repeat steps 3-5 at least 3 times

## Expected Result
All three tests should produce **identical scores** for each criterion.

## Previous Issue
With temperature=0.3, the scores would vary between tests (e.g., sometimes 3, sometimes 4 for the same criterion).

## Current Status
- Fix has been deployed to production
- Bot is running and processing requests
- Temperature set to 0.0 for deterministic output