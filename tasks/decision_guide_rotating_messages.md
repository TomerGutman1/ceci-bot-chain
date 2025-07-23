# Decision Guide Bot - Rotating Messages Implementation

## Summary of Changes

### 1. Added Rotating Messages Array
- Created an array of 6 status messages in Hebrew that indicate different stages of the analysis process
- Messages are formal and informative, following the requirements

### 2. Implemented Message Rotation Logic
- Added `currentMessageIndex` state to track which message to display
- Created a `useEffect` hook that:
  - Shows the first message immediately when analysis starts
  - Rotates through messages every 10 seconds
  - Loops back to messages 2-5 after showing all messages (as specified)
  - Resets to first message when analysis completes

### 3. Updated UI to Display Messages
- Added a loading state section that appears during analysis
- Includes a spinner animation for visual feedback
- Displays the current rotating message below the spinner
- Styled with gray background for visibility

### 4. Updated Error Handling
- Changed error message to: "אירעה שגיאה זמנית. מומלץ לנסות שוב בעוד כמה דקות."
- Maintains formal tone as required

### 5. Button State Management
- Cancel button is now disabled during analysis
- Submit button shows "מעבד..." during analysis (instead of the rotating messages)
- This keeps the button text concise while detailed messages appear above

## Implementation Details

The rotating messages are:
1. הטיוטה התקבלה. מתחילים בניתוח.
2. בודקים את מבנה הטיוטה ותקינות הנתונים.
3. מזהים קריטריונים רלוונטיים לציון.
4. מחשבים מדדי הערכה לפי מתודולוגיית המשרד.
5. מכינים דו״ח מסכם להצגה.
6. עוד רגע – מבצעים אימות סופי.

The implementation follows all requirements:
- No emojis or casual language
- No percentage or time estimates
- Formal, government-appropriate Hebrew
- RTL support maintained
- Messages rotate every 10 seconds
- Error fallback shows appropriate message

## File Modified
- `/src/components/decision-guide/DecisionGuideModal.tsx`

## Testing Recommendation
To test the implementation:
1. Upload a document or paste text
2. Click "שלח לניתוח"
3. Observe the rotating messages changing every 10 seconds
4. Verify the spinner animation is visible
5. Test error scenarios to ensure proper error message display