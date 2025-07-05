/**
 * Comprehensive Test Suite - 80 Questions
 * Organized by Type, Route, and Complexity
 */

import IntentDetector from './intent_detector.js';

const detector = new IntentDetector();

// Test categories
const testSuite = {
  // Category 1: QUERY - Basic Search (20 questions)
  queryBasic: [
    {
      id: "QB01",
      complexity: "simple",
      input: "החלטות ממשלה 37",
      expected: { intent_type: "QUERY", entities: { government_number: 37, operation: "search" } }
    },
    {
      id: "QB02", 
      complexity: "simple",
      input: "החלטות בנושא חינוך",
      expected: { intent_type: "QUERY", entities: { topic: "חינוך", operation: "search" } }
    },
    {
      id: "QB03",
      complexity: "medium",
      input: "תראה לי 5 החלטות בנושא חינוך מיוחד",
      expected: { intent_type: "QUERY", entities: { limit: 5, topic: "חינוך מיוחד", operation: "search" } }
    },
    {
      id: "QB04",
      complexity: "medium", 
      input: "החלטות על אנרגיה סולארית משנת 2020 והלאה",
      expected: { intent_type: "QUERY", entities: { topic: "אנרגיה סולארית", operation: "search" } }
    },
    {
      id: "QB05",
      complexity: "medium",
      input: "איזה החלטות נוגעות ל-AI ב-2024?",
      expected: { intent_type: "QUERY", entities: { topic: "AI", operation: "search" } }
    },
    {
      id: "QB06",
      complexity: "complex",
      input: "אילו החלטות ממשלה עוסקות בהעלאת שכר המינימום מאז 2022?",
      expected: { intent_type: "QUERY", entities: { topic: "העלאת שכר המינימום", operation: "search" } }
    },
    {
      id: "QB07",
      complexity: "medium",
      input: "החלטות תחבורה ציבורית בין 2010-2015",
      expected: { intent_type: "QUERY", entities: { topic: "תחבורה ציבורית", operation: "search" } }
    },
    {
      id: "QB08",
      complexity: "simple",
      input: "החלטות משרד הביטחון",
      expected: { intent_type: "QUERY", entities: { ministries: ["משרד הביטחון"], operation: "search" } }
    },
    {
      id: "QB09",
      complexity: "medium",
      input: "37 החלטות של הממשלה",
      expected: { intent_type: "QUERY", entities: { limit: 37, operation: "search" } }
    },
    {
      id: "QB10",
      complexity: "complex",
      input: "החלטות שקשורות למשבר האקלים",
      expected: { intent_type: "QUERY", entities: { topic: "משבר האקלים", operation: "search" } }
    },
    {
      id: "QB11",
      complexity: "medium",
      input: "תן את התוכן המלא של החלטה 2081 מממשלת 37",
      expected: { intent_type: "QUERY", entities: { decision_number: 2081, government_number: 37, operation: "search" } }
    },
    {
      id: "QB12",
      complexity: "simple",
      input: "החלטות על בריאות",
      expected: { intent_type: "QUERY", entities: { topic: "בריאות", operation: "search" } }
    },
    {
      id: "QB13",
      complexity: "medium",
      input: "החלטות בתחום ביטחון",
      expected: { intent_type: "QUERY", entities: { topic: "ביטחון", operation: "search" } }
    },
    {
      id: "QB14",
      complexity: "simple",
      input: "החלטות משרד החינוך",
      expected: { intent_type: "QUERY", entities: { ministries: ["משרד החינוך"], operation: "search" } }
    },
    {
      id: "QB15",
      complexity: "medium",
      input: "תן לי 10 החלטות אחרונות",
      expected: { intent_type: "QUERY", entities: { limit: 10, operation: "search" } }
    },
    {
      id: "QB16",
      complexity: "complex",
      input: "החלטות עוסקות בתשתיות מים",
      expected: { intent_type: "QUERY", entities: { topic: "תשתיות מים", operation: "search" } }
    },
    {
      id: "QB17",
      complexity: "medium",
      input: "החלטות ממשלה שלושים ושבע",
      expected: { intent_type: "QUERY", entities: { government_number: 37, operation: "search" } }
    },
    {
      id: "QB18",
      complexity: "simple",
      input: "החלטות בנושא סביבה",
      expected: { intent_type: "QUERY", entities: { topic: "סביבה", operation: "search" } }
    },
    {
      id: "QB19",
      complexity: "medium",
      input: "החלטות על דיור בר השגה",
      expected: { intent_type: "QUERY", entities: { topic: "דיור בר השגה", operation: "search" } }
    },
    {
      id: "QB20",
      complexity: "complex",
      input: "החלטות שנוגעות לפריפריה",
      expected: { intent_type: "QUERY", entities: { topic: "פריפריה", operation: "search" } }
    }
  ],

  // Category 2: QUERY - Statistical (15 questions)
  queryStatistical: [
    {
      id: "QS01",
      complexity: "simple",
      input: "כמה החלטות יש בנושא חינוך?",
      expected: { intent_type: "QUERY", entities: { topic: "חינוך", operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS02",
      complexity: "simple", 
      input: "מספר ההחלטות של ממשלה 37",
      expected: { intent_type: "QUERY", entities: { government_number: 37, operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS03",
      complexity: "medium",
      input: "כמה החלטות בנושא סביבה היו ב-2024?",
      expected: { intent_type: "QUERY", entities: { topic: "סביבה", operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS04",
      complexity: "medium",
      input: "מה מספר ההחלטות של משרד האוצר?",
      expected: { intent_type: "QUERY", entities: { ministries: ["משרד האוצר"], operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS05",
      complexity: "medium",
      input: "כמה פעמים דנו בנושא דיור?",
      expected: { intent_type: "QUERY", entities: { topic: "דיור", operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS06",
      complexity: "complex",
      input: "כמה החלטות התקבלו השנה?",
      expected: { intent_type: "QUERY", entities: { operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS07",
      complexity: "medium",
      input: "בסך הכל כמה החלטות בנושא ביטחון?",
      expected: { intent_type: "QUERY", entities: { topic: "ביטחון", operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS08",
      complexity: "complex",
      input: "מה הכמות של החלטות בנושא כלכלה?", 
      expected: { intent_type: "QUERY", entities: { topic: "כלכלה", operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS09",
      complexity: "medium",
      input: "כמה החלטות משרד הבריאות השנה?",
      expected: { intent_type: "QUERY", entities: { ministries: ["משרד הבריאות"], operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS10",
      complexity: "complex",
      input: "כמה החלטות עברו בממשלה עשרים ואחת?",
      expected: { intent_type: "QUERY", entities: { government_number: 21, operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS11",
      complexity: "medium",
      input: "סה״כ החלטות בנושא תחבורה",
      expected: { intent_type: "QUERY", entities: { topic: "תחבורה", operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS12",
      complexity: "complex",
      input: "כמה החלטות יש על תשתיות מים?",
      expected: { intent_type: "QUERY", entities: { topic: "תשתיות מים", operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS13",
      complexity: "medium",
      input: "מספר החלטות משרד החוץ",
      expected: { intent_type: "QUERY", entities: { ministries: ["משרד החוץ"], operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS14",
      complexity: "complex",
      input: "כמה החלטות על אנרגיה מתחדשת?",
      expected: { intent_type: "QUERY", entities: { topic: "אנרגיה מתחדשת", operation: "count" }, route_flags: { is_statistical: true } }
    },
    {
      id: "QS15",
      complexity: "medium",
      input: "מה כמות ההחלטות בנושא רווחה?",
      expected: { intent_type: "QUERY", entities: { topic: "רווחה", operation: "count" }, route_flags: { is_statistical: true } }
    }
  ],

  // Category 3: QUERY - Comparison (15 questions)
  queryComparison: [
    {
      id: "QC01",
      complexity: "medium",
      input: "השווה בין ממשלה 36 לממשלה 37",
      expected: { intent_type: "QUERY", entities: { operation: "compare", comparison_target: "governments:36,37" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC02",
      complexity: "medium",
      input: "מה ההבדל בין החלטות 2023 ל-2024?",
      expected: { intent_type: "QUERY", entities: { operation: "compare" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC03",
      complexity: "complex",
      input: "השוואת החלטות משרד החינוך מול משרד הבריאות",
      expected: { intent_type: "QUERY", entities: { operation: "compare", ministries: ["משרד החינוך", "משרד הבריאות"] }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC04",
      complexity: "complex",
      input: "השווה בין כמות החלטות דקלרטיביות ואופרטיביות בשנת 2023",
      expected: { intent_type: "QUERY", entities: { operation: "compare" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC05",
      complexity: "medium",
      input: "החלטות בנושא תחבורה לעומת החלטות בנושא דיור",
      expected: { intent_type: "QUERY", entities: { operation: "compare" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC06",
      complexity: "medium",
      input: "ההבדלים בין ממשלה שלושים לממשלה ארבעים",
      expected: { intent_type: "QUERY", entities: { operation: "compare", comparison_target: "governments:30,40" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC07",
      complexity: "complex",
      input: "השווה החלטות סביבה בין 2020 ל-2024",
      expected: { intent_type: "QUERY", entities: { operation: "compare", topic: "סביבה" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC08",
      complexity: "medium",
      input: "ההבדל בין החלטות ביטחון לבריאות",
      expected: { intent_type: "QUERY", entities: { operation: "compare" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC09",
      complexity: "complex",
      input: "השווה את מספר החלטות חינוך מול תחבורה",
      expected: { intent_type: "QUERY", entities: { operation: "compare" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC10",
      complexity: "medium",
      input: "מה ההבדל בין ממשלה 35 ו-36?",
      expected: { intent_type: "QUERY", entities: { operation: "compare", comparison_target: "governments:35,36" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC11",
      complexity: "complex",
      input: "השווה החלטות משרד האוצר לעומת משרד הפנים",
      expected: { intent_type: "QUERY", entities: { operation: "compare", ministries: ["משרד האוצר", "משרד הפנים"] }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC12",
      complexity: "medium",
      input: "השוואה בין החלטות 2022 ו-2023",
      expected: { intent_type: "QUERY", entities: { operation: "compare" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC13",
      complexity: "complex",
      input: "השווה בין החלטות דיור ב-2020 לעומת 2024",
      expected: { intent_type: "QUERY", entities: { operation: "compare", topic: "דיור" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC14",
      complexity: "medium",
      input: "ההבדל בין החלטות כלכלה וחברה",
      expected: { intent_type: "QUERY", entities: { operation: "compare" }, route_flags: { is_comparison: true } }
    },
    {
      id: "QC15",
      complexity: "complex",
      input: "השווה החלטות אנרגיה בין ממשלות 34 ו-37",
      expected: { intent_type: "QUERY", entities: { operation: "compare", topic: "אנרגיה", comparison_target: "governments:34,37" }, route_flags: { is_comparison: true } }
    }
  ],

  // Category 4: EVAL - Analysis (10 questions)
  eval: [
    {
      id: "EV01",
      complexity: "simple",
      input: "נתח את החלטה 2983",
      expected: { intent_type: "EVAL", entities: { decision_number: 2983 } }
    },
    {
      id: "EV02",
      complexity: "medium",
      input: "ניתוח מעמיק של החלטה 1547",
      expected: { intent_type: "EVAL", entities: { decision_number: 1547 } }
    },
    {
      id: "EV03",
      complexity: "medium",
      input: "אני רוצה ניתוח של החלטה 660 ממשלה 37",
      expected: { intent_type: "EVAL", entities: { decision_number: 660, government_number: 37 } }
    },
    {
      id: "EV04",
      complexity: "medium",
      input: "תן לי ניתוח מפורט של החלטת ממשלה 2150",
      expected: { intent_type: "EVAL", entities: { decision_number: 2150 } }
    },
    {
      id: "EV05",
      complexity: "simple",
      input: "נתח לי את החלטה מספר 3421",
      expected: { intent_type: "EVAL", entities: { decision_number: 3421 } }
    },
    {
      id: "EV06",
      complexity: "medium",
      input: "ניתוח החלטת הממשלה 1823",
      expected: { intent_type: "EVAL", entities: { decision_number: 1823 } }
    },
    {
      id: "EV07",
      complexity: "simple",
      input: "בחן לעומק את החלטה 975",
      expected: { intent_type: "EVAL", entities: { decision_number: 975 } }
    },
    {
      id: "EV08",
      complexity: "medium",
      input: "ניתוח יסודי של החלטה 2641",
      expected: { intent_type: "EVAL", entities: { decision_number: 2641 } }
    },
    {
      id: "EV09",
      complexity: "simple",
      input: "הסבר לעומק את החלטה 1122",
      expected: { intent_type: "EVAL", entities: { decision_number: 1122 } }
    },
    {
      id: "EV10",
      complexity: "medium",
      input: "פרט באופן מעמיק על החלטה 3089",
      expected: { intent_type: "EVAL", entities: { decision_number: 3089 } }
    }
  ],

  // Category 5: REFERENCE - Context (10 questions)
  reference: [
    {
      id: "RF01",
      complexity: "simple",
      input: "ההחלטה ששלחת לי",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "last", reference_position: 1 }, route_flags: { needs_context: true } }
    },
    {
      id: "RF02",
      complexity: "medium",
      input: "מה היה בהחלטה האחרונה שהצגת?",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "last", reference_position: 1 }, route_flags: { needs_context: true } }
    },
    {
      id: "RF03",
      complexity: "medium",
      input: "תן לי עוד פרטים על ההחלטה הקודמת",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "previous", reference_position: 1 }, route_flags: { needs_context: true } }
    },
    {
      id: "RF04",
      complexity: "simple",
      input: "ההחלטה הראשונה ששלחת",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "specific", reference_position: 1 }, route_flags: { needs_context: true } }
    },
    {
      id: "RF05",
      complexity: "medium",
      input: "החלטה מספר 3 מהרשימה שנתת",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "specific", reference_position: 3 }, route_flags: { needs_context: true } }
    },
    {
      id: "RF06",
      complexity: "simple",
      input: "ההחלטה השנייה שהראית לי",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "specific", reference_position: 2 }, route_flags: { needs_context: true } }
    },
    {
      id: "RF07",
      complexity: "medium",
      input: "עוד החלטות כמו ששאלתי קודם",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "context" }, route_flags: { needs_context: true } }
    },
    {
      id: "RF08",
      complexity: "simple",
      input: "עוד כמו האחרונה",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "last", reference_position: 1 }, route_flags: { needs_context: true } }
    },
    {
      id: "RF09",
      complexity: "medium",
      input: "נתח את ההחלטה האחרונה ששלחת",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "last", reference_position: 1 }, route_flags: { needs_context: true } }
    },
    {
      id: "RF10",
      complexity: "complex",
      input: "אני רוצה ניתוח של ההחלטה השנייה ברשימה",
      expected: { intent_type: "REFERENCE", entities: { reference_type: "specific", reference_position: 2 }, route_flags: { needs_context: true } }
    }
  ],

  // Category 6: CLARIFICATION - Vague Queries (10 questions)
  clarification: [
    {
      id: "CL01",
      complexity: "simple",
      input: "מה?",
      expected: { intent_type: "CLARIFICATION" }
    },
    {
      id: "CL02",
      complexity: "simple",
      input: "החלטות",
      expected: { intent_type: "CLARIFICATION" }
    },
    {
      id: "CL03",
      complexity: "simple",
      input: "נתח",
      expected: { intent_type: "CLARIFICATION" }
    },
    {
      id: "CL04",
      complexity: "medium",
      input: "צריך משהו על חינוך",
      expected: { intent_type: "CLARIFICATION" }
    },
    {
      id: "CL05",
      complexity: "medium",
      input: "החלטה החדשה על מס",
      expected: { intent_type: "CLARIFICATION" }
    },
    {
      id: "CL06",
      complexity: "medium",
      input: "תן החלטות על דיור",
      expected: { intent_type: "CLARIFICATION" }
    },
    {
      id: "CL07",
      complexity: "simple",
      input: "איך?",
      expected: { intent_type: "CLARIFICATION" }
    },
    {
      id: "CL08",
      complexity: "simple",
      input: "למה?",
      expected: { intent_type: "CLARIFICATION" }
    },
    {
      id: "CL09",
      complexity: "medium",
      input: "מה עם ביטחון?",
      expected: { intent_type: "CLARIFICATION" }
    },
    {
      id: "CL10",
      complexity: "medium",
      input: "יש נתונים על רווחה?",
      expected: { intent_type: "CLARIFICATION" }
    }
  ]
};

// Flatten all tests for execution
const allTests = [
  ...testSuite.queryBasic,
  ...testSuite.queryStatistical,
  ...testSuite.queryComparison,
  ...testSuite.eval,
  ...testSuite.reference,
  ...testSuite.clarification
];

console.log('🧪 Comprehensive Intent Detector Test Suite - 80 Questions\n');
console.log(`📊 Test Distribution:`);
console.log(`   • QUERY Basic: ${testSuite.queryBasic.length} questions`);
console.log(`   • QUERY Statistical: ${testSuite.queryStatistical.length} questions`);
console.log(`   • QUERY Comparison: ${testSuite.queryComparison.length} questions`);
console.log(`   • EVAL: ${testSuite.eval.length} questions`);
console.log(`   • REFERENCE: ${testSuite.reference.length} questions`);
console.log(`   • CLARIFICATION: ${testSuite.clarification.length} questions`);
console.log(`   • Total: ${allTests.length} questions\n`);

// Run tests
let passed = 0;
let failed = 0;
const results = {
  queryBasic: { passed: 0, failed: 0 },
  queryStatistical: { passed: 0, failed: 0 },
  queryComparison: { passed: 0, failed: 0 },
  eval: { passed: 0, failed: 0 },
  reference: { passed: 0, failed: 0 },
  clarification: { passed: 0, failed: 0 }
};
const failures = [];

function runCategoryTests(categoryName, tests) {
  console.log(`\n🔸 Testing ${categoryName.toUpperCase()} (${tests.length} cases):`);
  
  tests.forEach(test => {
    const result = detector.detect(test.input);
    
    let testPassed = true;
    let failureReasons = [];

    // Check intent type
    if (result.intent_type !== test.expected.intent_type) {
      testPassed = false;
      failureReasons.push(`Intent: expected ${test.expected.intent_type}, got ${result.intent_type}`);
    }

    // Check entities if specified
    if (test.expected.entities) {
      for (const [key, expectedValue] of Object.entries(test.expected.entities)) {
        if (typeof expectedValue === 'object' && expectedValue !== null) {
          // Handle nested objects (like date_range)
          if (!result.entities[key]) {
            testPassed = false;
            failureReasons.push(`Entity ${key}: expected object, got undefined`);
          }
        } else if (!result.entities[key] || result.entities[key] !== expectedValue) {
          testPassed = false;
          failureReasons.push(`Entity ${key}: expected ${expectedValue}, got ${result.entities[key] || 'undefined'}`);
        }
      }
    }

    // Check route flags if specified
    if (test.expected.route_flags) {
      for (const [key, expectedValue] of Object.entries(test.expected.route_flags)) {
        if (!result.route_flags || result.route_flags[key] !== expectedValue) {
          testPassed = false;
          failureReasons.push(`Route flag ${key}: expected ${expectedValue}, got ${result.route_flags?.[key] || 'undefined'}`);
        }
      }
    }

    if (testPassed) {
      passed++;
      results[categoryName].passed++;
      console.log(`  ✅ ${test.id} [${test.complexity}]: "${test.input}"`);
    } else {
      failed++;
      results[categoryName].failed++;
      console.log(`  ❌ ${test.id} [${test.complexity}]: "${test.input}"`);
      console.log(`     Issues: ${failureReasons.join(', ')}`);
      failures.push({
        category: categoryName,
        ...test,
        actual: result,
        issues: failureReasons
      });
    }
  });
}

// Run all category tests
runCategoryTests('queryBasic', testSuite.queryBasic);
runCategoryTests('queryStatistical', testSuite.queryStatistical);
runCategoryTests('queryComparison', testSuite.queryComparison);
runCategoryTests('eval', testSuite.eval);
runCategoryTests('reference', testSuite.reference);
runCategoryTests('clarification', testSuite.clarification);

// Print final summary
console.log('\n📊 Final Results Summary:');
console.log('========================');
console.log(`Total Tests: ${allTests.length}`);
console.log(`Passed: ${passed} (${((passed / allTests.length) * 100).toFixed(1)}%)`);
console.log(`Failed: ${failed} (${((failed / allTests.length) * 100).toFixed(1)}%)`);

console.log('\n📈 Results by Category:');
Object.entries(results).forEach(([category, stats]) => {
  const total = stats.passed + stats.failed;
  const percentage = total > 0 ? ((stats.passed / total) * 100).toFixed(1) : '0.0';
  console.log(`  ${category}: ${stats.passed}/${total} (${percentage}%)`);
});

if (failures.length > 0) {
  console.log('\n❌ Failed Tests by Category:');
  const failuresByCategory = {};
  failures.forEach(failure => {
    if (!failuresByCategory[failure.category]) {
      failuresByCategory[failure.category] = [];
    }
    failuresByCategory[failure.category].push(failure);
  });

  Object.entries(failuresByCategory).forEach(([category, categoryFailures]) => {
    console.log(`\n${category.toUpperCase()} failures (${categoryFailures.length}):`);
    categoryFailures.forEach(failure => {
      console.log(`  • ${failure.id}: ${failure.issues.join(', ')}`);
    });
  });
}

export { allTests, results, failures };