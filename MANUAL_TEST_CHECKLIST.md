# Manual Testing Checklist for Context Handling Improvements

**Date**: ________________  
**Tester**: ________________  
**Environment**: ________________ (Dev/Staging/Prod)

## Pre-Test Setup

- [ ] All services running (`docker compose up`)
- [ ] Backend health check passing
- [ ] Context router health check passing
- [ ] Database has test data (decisions 1000-3000)
- [ ] Browser console open for debugging
- [ ] Network tab open to monitor API calls

## 1. Cache Safety Tests

### Entity Persistence Prevention
- [ ] Query "החלטה 2989"
- [ ] Query "החלטה 1234" 
- [ ] ✅ Verify second query doesn't return 2989 data
- [ ] ✅ Check response times (both should be similar)

### Context-Dependent Cache Bypass
- [ ] Query "תן לי את זה" twice
- [ ] ✅ Verify both queries process fresh (no cache speedup)
- [ ] Query "ההחלטה האחרונה" twice
- [ ] ✅ Verify no caching occurs

### Safe Query Caching
- [ ] Query "החלטות אחרונות" twice
- [ ] ✅ Verify second query is significantly faster
- [ ] Check browser network tab for cache indicators

## 2. Hebrew UI Testing

### Clarification Display
- [ ] Query "מה?"
- [ ] ✅ Verify Hebrew clarification text displays correctly
- [ ] ✅ Check RTL alignment is proper
- [ ] ✅ Verify no encoding issues (�� characters)

### Multi-line Responses
- [ ] Query for analysis of a decision
- [ ] ✅ Verify Hebrew formatting preserved
- [ ] ✅ Check line breaks render correctly
- [ ] ✅ Verify lists and bullets display properly

## 3. Multi-Device Session Testing

### Cross-Device Isolation
- [ ] Open app on Device/Browser A
- [ ] Query "החלטה 1000" on Device A
- [ ] Open app on Device/Browser B
- [ ] Query "החלטה 2000" on Device B
- [ ] Query "תן לי את זה" on both devices
- [ ] ✅ Device A should reference 1000
- [ ] ✅ Device B should reference 2000

### Mobile Responsiveness
- [ ] Test on mobile device/emulator
- [ ] ✅ Verify touch interactions work
- [ ] ✅ Check text is readable
- [ ] ✅ Verify input field works with Hebrew keyboard

## 4. Browser Behavior Tests

### Page Refresh
- [ ] Make several queries building context
- [ ] Refresh the page (F5)
- [ ] Query "תן לי את זה"
- [ ] ✅ Should ask for clarification (context lost)

### Back/Forward Navigation
- [ ] Make query sequence
- [ ] Use browser back button
- [ ] Use browser forward button
- [ ] ✅ Verify app state remains consistent

### Multiple Tabs
- [ ] Open app in Tab 1
- [ ] Query "החלטה 1500" in Tab 1
- [ ] Open app in Tab 2
- [ ] Query "החלטה 2500" in Tab 2
- [ ] Switch tabs and test references
- [ ] ✅ Each tab maintains separate context

## 5. Network Resilience Tests

### Slow Connection
- [ ] Enable network throttling (3G)
- [ ] Make complex query
- [ ] ✅ Verify loading indicators appear
- [ ] ✅ Verify no duplicate requests
- [ ] ✅ Check timeout handling

### Connection Loss
- [ ] Start a query
- [ ] Disconnect network mid-request
- [ ] ✅ Verify error message appears
- [ ] ✅ Verify error is in Hebrew
- [ ] Reconnect and retry
- [ ] ✅ Verify recovery works

## 6. Edge Case UI Tests

### Very Long Queries
- [ ] Paste 500+ character query
- [ ] ✅ Verify input field handles it
- [ ] ✅ Check submission works
- [ ] ✅ Verify UI doesn't break

### Special Characters
- [ ] Query with emojis: "😀 החלטות שמחות"
- [ ] Query with punctuation: "!!!מה???"
- [ ] Query with mixed Hebrew/English
- [ ] ✅ All should handle gracefully

### Rapid Queries
- [ ] Send 5 queries rapidly
- [ ] ✅ Verify all get responses
- [ ] ✅ Check order is maintained
- [ ] ✅ Verify no UI freezing

## 7. Accessibility Tests

### Keyboard Navigation
- [ ] Tab through all elements
- [ ] ✅ Verify focus indicators visible
- [ ] ✅ Check enter key submits query
- [ ] ✅ Verify escape key works as expected

### Screen Reader (if available)
- [ ] Enable screen reader
- [ ] Navigate through responses
- [ ] ✅ Verify Hebrew content is read correctly
- [ ] ✅ Check ARIA labels work

## 8. Performance Perception Tests

### Loading States
- [ ] Make various query types
- [ ] ✅ Simple queries feel fast (<3s)
- [ ] ✅ Analysis queries show progress
- [ ] ✅ No "frozen" UI moments

### Smooth Scrolling
- [ ] Get long response list
- [ ] Scroll through results
- [ ] ✅ Verify smooth scrolling
- [ ] ✅ Check no jank/stuttering

## 9. Error Handling Tests

### API Errors
- [ ] Stop backend service
- [ ] Try to make query
- [ ] ✅ Friendly error message appears
- [ ] ✅ Error is in Hebrew
- [ ] ✅ Retry option available

### Invalid Responses
- [ ] Query for non-existent decision (99999)
- [ ] ✅ Appropriate "not found" message
- [ ] ✅ Suggestions for next steps
- [ ] ✅ No technical error details exposed

## 10. Conversation Flow Tests

### Natural Progression
- [ ] "החלטות בנושא חינוך"
- [ ] "כמה יש?"
- [ ] "תן לי את הראשונה"
- [ ] "מה התקציב שלה?"
- [ ] "יש החלטות דומות?"
- [ ] ✅ Each step maintains context
- [ ] ✅ Responses feel connected

### Context Switching
- [ ] Discuss decision A
- [ ] Switch to decision B
- [ ] Ask "השווה ביניהם"
- [ ] ✅ System recognizes both contexts
- [ ] ✅ Comparison is accurate

## Sign-off

**All tests completed**: ☐  
**Issues found**: ________________  
**Overall assessment**: ☐ Pass / ☐ Pass with issues / ☐ Fail

**Tester signature**: ________________  
**Date**: ________________

## Notes Section

_Use this space to document any observations, issues, or suggestions:_

_______________________________________________
_______________________________________________
_______________________________________________
_______________________________________________