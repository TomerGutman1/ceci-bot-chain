#\!/usr/bin/env node

const IntentDetector = require('./INTENT_RCGNZR_0/intent_detector.js');

// Final test cases
const testQueries = [
  "החלטות ב-2020",
  "החלטות השנה",
  "החלטות החודש",
  "כמה החלטות התקבלו בתחום הבריאות בין 2010 ל־2020?",
  "החלטות משנת 2015",
  "החלטות בין 2018-2022"
];

const detector = new IntentDetector();

console.log("Final Date Extraction Test Results:\n");

testQueries.forEach((query, index) => {
  const result = detector.detect(query);
  console.log(`Query ${index + 1}: "${query}"`);
  console.log(`Intent: ${result.intent_type}`);
  console.log(`Date Range: ${result.entities?.date_range ? JSON.stringify(result.entities.date_range) : 'None'}`);
  console.log('---');
});
