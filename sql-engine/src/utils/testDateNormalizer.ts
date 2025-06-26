// Test file for dateNormalizer
import { normalizeDateString } from './dateNormalizer';

// Test cases
const tests = [
  { input: '15/03/2023', expected: '2023-03-15' },
  { input: '1.1.2023', expected: '2023-01-01' },
  { input: 'מרץ 2023', expected: '2023-03-01' },
  { input: '01/01/2023', expected: '2023-01-01' },
  { input: '31.12.2023', expected: '2023-12-31' },
];

console.log('Testing dateNormalizer...\n');

tests.forEach(({ input, expected }) => {
  const result = normalizeDateString(input);
  const passed = result === expected;
  console.log(`Input: "${input}"`);
  console.log(`Expected: ${expected}`);
  console.log(`Got: ${result}`);
  console.log(`Status: ${passed ? '✓ PASS' : '✗ FAIL'}\n`);
});
