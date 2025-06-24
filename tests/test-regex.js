// Test regex patterns
const pattern = /כמה\s+החלטות\s+בנושא\s+([\u0590-\u05FF\s]+?)\s+היו\s+מ([\u0590-\u05FF]+\s+\d{4})\s+עד\s+([\u0590-\u05FF]+\s+\d{4})/;

const testQueries = [
  "כמה החלטות בנושא רפואה היו מפברואר 2000 עד מרץ 2010?",
  "כמה החלטות בנושא חינוך היו מפברואר 2000 עד מרץ 2010?"
];

testQueries.forEach(query => {
  console.log(`\nTesting: "${query}"`);
  const match = query.match(pattern);
  if (match) {
    console.log("✅ MATCHED!");
    console.log("Topic:", match[1]);
    console.log("From date:", match[2]);
    console.log("To date:", match[3]);
  } else {
    console.log("❌ NO MATCH");
  }
});

// Test simpler pattern
const simplePattern = /כמה\s+החלטות\s+בנושא\s+([\u0590-\u05FF\s]+?)\s+היו\s+מ([\u0590-\u05FF\s0-9]+)\s+עד\s+([\u0590-\u05FF\s0-9]+)/;

console.log("\n\n=== Testing with simpler pattern ===");
testQueries.forEach(query => {
  console.log(`\nTesting: "${query}"`);
  const match = query.match(simplePattern);
  if (match) {
    console.log("✅ MATCHED!");
    console.log("Topic:", match[1]);
    console.log("From date:", match[2]);
    console.log("To date:", match[3]);
  } else {
    console.log("❌ NO MATCH");
  }
});
