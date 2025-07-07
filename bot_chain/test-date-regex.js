const query = 'כמה החלטות התקבלו בתחום הבריאות בין 2010 ל־2020?';

// Test patterns
const patterns = [
  /בין\s+(\d{4})[־-](\d{4})/,
  /בין\s+(\d{4})\s+ל[־\-–]?\s*(\d{4})/,
  /בין\s+(\d{4})\s+ל\s+(\d{4})/,
  /ב[־-]?(\d{4})/,
  /משנת\s+(\d{4})/
];

console.log('Testing query:', query);
console.log('---');

patterns.forEach((pattern, index) => {
  const match = query.match(pattern);
  console.log(`Pattern ${index + 1}: ${pattern}`);
  console.log('Match:', match ? match[0] : 'No match');
  if (match && match[1]) {
    console.log('Groups:', match.slice(1));
  }
  console.log('---');
});

// Test the exact pattern from intent_detector.js
const exactPattern = /בין\s+(\d{4})\s+ל[־\-–]?\s*(\d{4})/;
console.log('Exact pattern test:', exactPattern);
console.log('Match:', query.match(exactPattern));