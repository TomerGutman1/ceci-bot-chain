#!/usr/bin/env node

const IntentDetector = require('./INTENT_RCGNZR_0/intent_detector.js');

// Test cases for date extraction
const testQueries = [
  "כמה החלטות התקבלו בתחום הבריאות בין 2010 ל־2020?",
  "כמה החלטות התקבלו בתחום הבריאות בין 2010 ל-2020?",
  "כמה החלטות התקבלו בתחום הבריאות בין 2010 ל 2020?",
  "החלטות ב-2020",
  "החלטות ב2020",
  "החלטות משנת 2020",
  "החלטות בין 2010-2020",
  "החלטות מ-2018 עד 2022",
  "כל ההחלטות של השנה",
  "החלטות החודש",
  "החלטות מאז 2015",
  "החלטות משנת 2019 והלאה",
  "החלטות בינואר 2023",
  "החלטות הבריאות ב-2023"
];

const detector = new IntentDetector();

console.log("Testing date extraction functionality:\n");

testQueries.forEach((query, index) => {
  console.log(`\nTest ${index + 1}: "${query}"`);
  
  // Test extractDateRange directly
  const dateRange = detector.extractDateRange(query);
  console.log("Direct extractDateRange result:", dateRange || "null");
  
  // Test through full detection
  const result = detector.detect(query);
  console.log("Full detection entities.date_range:", result.entities?.date_range || "undefined");
  console.log("Full detection result:", JSON.stringify(result, null, 2));
});

// Additional test to check if the hyphen character is the issue
console.log("\n\nChecking hyphen character codes:");
const query1 = "בין 2010 ל־2020"; // Hebrew maqaf
const query2 = "בין 2010 ל-2020"; // Regular hyphen
const query3 = "בין 2010 ל–2020"; // En-dash

console.log("Query 1 (Hebrew maqaf):", query1);
console.log("Character codes:", Array.from(query1).map(c => c.charCodeAt(0)));
console.log("Match result:", query1.match(/בין\s+(\d{4})\s+ל[־\-–]?\s*(\d{4})/));

console.log("\nQuery 2 (Regular hyphen):", query2);
console.log("Character codes:", Array.from(query2).map(c => c.charCodeAt(0)));
console.log("Match result:", query2.match(/בין\s+(\d{4})\s+ל[־\-–]?\s*(\d{4})/));

console.log("\nQuery 3 (En-dash):", query3);
console.log("Character codes:", Array.from(query3).map(c => c.charCodeAt(0)));
console.log("Match result:", query3.match(/בין\s+(\d{4})\s+ל[־\-–]?\s*(\d{4})/));

// Test specific regex patterns
console.log("\n\nTesting specific regex patterns:");
const testPattern = /בין\s+(\d{4})\s+ל[־\-–]?\s*(\d{4})/;
console.log("Pattern:", testPattern);
console.log("Test 'בין 2010 ל־2020':", testPattern.test("בין 2010 ל־2020"));
console.log("Test 'בין 2010 ל-2020':", testPattern.test("בין 2010 ל-2020"));
console.log("Test 'בין 2010 ל 2020':", testPattern.test("בין 2010 ל 2020"));