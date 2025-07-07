// Test the specific regex pattern
const query = 'כמה החלטות התקבלו בתחום הבריאות בין 2010 ל־2020?';

console.log('Query:', query);
console.log('Query charCodes:', [...query].map(c => c.charCodeAt(0)));
console.log('---');

// Test the exact pattern from intent_detector.js
const pattern = /בין\s+(\d{4})\s+ל[־\-–]?\s*(\d{4})/;
const match = query.match(pattern);

console.log('Pattern:', pattern);
console.log('Match:', match);

// Test with simpler pattern
const simplePattern = /בין\s+(\d{4})\s+ל/;
const simpleMatch = query.match(simplePattern);
console.log('---');
console.log('Simple pattern:', simplePattern);
console.log('Simple match:', simpleMatch);

// Check what's between 2010 and 2020
const betweenNumbers = query.substring(query.indexOf('2010'), query.indexOf('2020'));
console.log('---');
console.log('Between numbers:', betweenNumbers);
console.log('Between numbers charCodes:', [...betweenNumbers].map(c => c.charCodeAt(0)));

// Test if the maqaf character is what we expect
const maqafInQuery = query.includes('־');
console.log('---');
console.log('Contains Hebrew maqaf (־):', maqafInQuery);
console.log('Maqaf charCode:', '־'.charCodeAt(0));