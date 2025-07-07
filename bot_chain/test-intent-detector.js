const { IntentDetector } = require('./INTENT_RCGNZR_0/intent_detector.js');

const detector = new IntentDetector();
const query = 'כמה החלטות התקבלו בתחום הבריאות בין 2010 ל־2020?';

console.log('Testing query:', query);
console.log('---');

// Test extractDateRange directly
const dateRange = detector.extractDateRange(query);
console.log('extractDateRange result:', dateRange);
console.log('---');

// Test extractEntities
const entities = detector.extractEntities(query);
console.log('extractEntities result:', JSON.stringify(entities, null, 2));
console.log('---');

// Test full detect
const result = detector.detect(query);
console.log('detect result:', JSON.stringify(result, null, 2));