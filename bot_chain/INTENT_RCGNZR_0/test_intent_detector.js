/**
 * Test Suite for Intent Detector Engine
 * Tests all examples from Qs_examples.md
 */

import IntentDetector from './intent_detector.js';

class IntentDetectorTester {
  constructor() {
    this.detector = new IntentDetector();
    this.testResults = {
      passed: 0,
      failed: 0,
      total: 0,
      failures: []
    };
  }

  runAllTests() {
    console.log('🎯 Intent Detector Test Suite Starting...\n');
    
    this.testQueryExamples();
    this.testReferenceExamples();
    this.testEvalExamples();
    this.testEdgeCases();
    
    this.printResults();
  }

  testQueryExamples() {
    console.log('📋 Testing QUERY Examples (30 cases)...');
    
    const queryTests = [
      // Basic searches (1-10)
      {
        input: "החלטות ממשלה 37",
        expected: { intent_type: "QUERY", entities: { government_number: 37, operation: "search" } }
      },
      {
        input: "כל ההחלטות בנושא חינוך",
        expected: { intent_type: "QUERY", entities: { topic: "חינוך", operation: "search" } }
      },
      {
        input: "החלטות משרד הביטחון",
        expected: { intent_type: "QUERY", entities: { ministries: ["משרד הביטחון"], operation: "search" } }
      },
      {
        input: "5 החלטות אחרונות",
        expected: { intent_type: "QUERY", entities: { limit: 5, operation: "search" } }
      },
      {
        input: "הצג לי החלטות בנושא תחבורה",
        expected: { intent_type: "QUERY", entities: { topic: "תחבורה", operation: "search" } }
      },
      {
        input: "תן לי את כל ההחלטות מינואר 2024",
        expected: { intent_type: "QUERY", entities: { date_range: { start: "2024-01-01", end: "2024-01-31" }, operation: "search" } }
      },
      {
        input: "רשימת החלטות ממשלה שלושים ושבע",
        expected: { intent_type: "QUERY", entities: { government_number: 37, operation: "search" } }
      },
      {
        input: "מצא החלטות על בריאות",
        expected: { intent_type: "QUERY", entities: { topic: "בריאות", operation: "search" } }
      },
      {
        input: "החלטות בין 01/01/2024 ל-31/03/2024",
        expected: { intent_type: "QUERY", entities: { date_range: { start: "2024-01-01", end: "2024-03-31" }, operation: "search" } }
      },
      {
        input: "החלטה 2983 של ממשלה 37",
        expected: { intent_type: "QUERY", entities: { government_number: 37, decision_number: 2983, operation: "search" } }
      },

      // Statistical queries (11-20)
      {
        input: "כמה החלטות יש בנושא חינוך?",
        expected: { intent_type: "QUERY", entities: { topic: "חינוך", operation: "count" }, route_flags: { is_statistical: true } }
      },
      {
        input: "מספר ההחלטות של ממשלה 37",
        expected: { intent_type: "QUERY", entities: { government_number: 37, operation: "count" }, route_flags: { is_statistical: true } }
      },
      {
        input: "כמה החלטות התקבלו השנה?",
        expected: { intent_type: "QUERY", entities: { date_range: { start: "2025-01-01", end: "2025-12-31" }, operation: "count" }, route_flags: { is_statistical: true } }
      },
      {
        input: "מה מספר ההחלטות של משרד האוצר?",
        expected: { intent_type: "QUERY", entities: { ministries: ["משרד האוצר"], operation: "count" }, route_flags: { is_statistical: true } }
      },
      {
        input: "כמה פעמים דנו בנושא דיור?",
        expected: { intent_type: "QUERY", entities: { topic: "דיור", operation: "count" }, route_flags: { is_statistical: true } }
      },

      // Comparison queries (21-25)
      {
        input: "השווה בין ממשלה 36 לממשלה 37",
        expected: { intent_type: "QUERY", entities: { operation: "compare", comparison_target: "governments:36,37" }, route_flags: { is_comparison: true } }
      },
      {
        input: "מה ההבדל בין החלטות 2023 ל-2024?",
        expected: { intent_type: "QUERY", entities: { operation: "compare" }, route_flags: { is_comparison: true } }
      },
      {
        input: "השוואת החלטות משרד החינוך מול משרד הבריאות",
        expected: { intent_type: "QUERY", entities: { operation: "compare", ministries: ["משרד החינוך", "משרד הבריאות"] }, route_flags: { is_comparison: true } }
      },

      // Complex queries (26-30)
      {
        input: "החלטות ממשלה 37 בנושא חינוך מינואר 2024",
        expected: { intent_type: "QUERY", entities: { government_number: 37, topic: "חינוך", date_range: { start: "2024-01-01", end: "2024-01-31" }, operation: "search" } }
      },
      {
        input: "10 החלטות אחרונות של משרד הביטחון בנושא תקציב",
        expected: { intent_type: "QUERY", entities: { limit: 10, ministries: ["משרד הביטחון"], topic: "תקציב", operation: "search" } }
      }
    ];

    queryTests.forEach((test, index) => this.runTest(`QUERY-${index + 1}`, test));
  }

  testReferenceExamples() {
    console.log('\n🔗 Testing REFERENCE Examples (30 cases)...');
    
    const referenceTests = [
      // Direct references (1-10)
      {
        input: "ההחלטה ששלחת לי",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "last", reference_position: 1 }, route_flags: { needs_context: true } }
      },
      {
        input: "מה היה בהחלטה האחרונה שהצגת?",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "last", reference_position: 1 }, route_flags: { needs_context: true } }
      },
      {
        input: "תן לי עוד פרטים על ההחלטה הקודמת",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "previous", reference_position: 1 }, route_flags: { needs_context: true } }
      },
      {
        input: "ההחלטה הראשונה ששלחת",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "specific", reference_position: 1 }, route_flags: { needs_context: true } }
      },
      {
        input: "החלטה מספר 3 מהרשימה שנתת",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "specific", reference_position: 3 }, route_flags: { needs_context: true } }
      },
      {
        input: "ההחלטה השנייה שהראית לי",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "specific", reference_position: 2 }, route_flags: { needs_context: true } }
      },

      // Continuity references (11-20)
      {
        input: "עוד החלטות כמו ששאלתי קודם",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "context" }, route_flags: { needs_context: true } }
      },
      {
        input: "בהמשך למה שביקשתי",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "context" }, route_flags: { needs_context: true } }
      },
      {
        input: "עוד כמו האחרונה",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "last", reference_position: 1 }, route_flags: { needs_context: true } }
      },
      {
        input: "דומות להחלטה ששלחת",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "last", reference_position: 1 }, route_flags: { needs_context: true } }
      },

      // Reference leading to EVAL (21-25)
      {
        input: "נתח את ההחלטה האחרונה ששלחת",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "last", reference_position: 1 }, route_flags: { needs_context: true } }
      },
      {
        input: "אני רוצה ניתוח של ההחלטה השנייה ברשימה",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "specific", reference_position: 2 }, route_flags: { needs_context: true } }
      },

      // Temporal references (26-30)
      {
        input: "מה ששאלתי קודם על חינוך",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "context", topic: "חינוך" }, route_flags: { needs_context: true } }
      },
      {
        input: "כמו שביקשתי לפני כמה דקות",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "context" }, route_flags: { needs_context: true } }
      },
      {
        input: "חזור על התוצאות האחרונות",
        expected: { intent_type: "REFERENCE", entities: { reference_type: "last" }, route_flags: { needs_context: true } }
      }
    ];

    referenceTests.forEach((test, index) => this.runTest(`REFERENCE-${index + 1}`, test));
  }

  testEvalExamples() {
    console.log('\n🔬 Testing EVAL Examples (10 cases)...');
    
    const evalTests = [
      {
        input: "נתח את החלטה 2983",
        expected: { intent_type: "EVAL", entities: { decision_number: 2983 } }
      },
      {
        input: "ניתוח מעמיק של החלטה 1547",
        expected: { intent_type: "EVAL", entities: { decision_number: 1547 } }
      },
      {
        input: "אני רוצה ניתוח של החלטה 660 ממשלה 37",
        expected: { intent_type: "EVAL", entities: { decision_number: 660, government_number: 37 } }
      },
      {
        input: "תן לי ניתוח מפורט של החלטת ממשלה 2150",
        expected: { intent_type: "EVAL", entities: { decision_number: 2150 } }
      },
      {
        input: "נתח לי את החלטה מספר 3421",
        expected: { intent_type: "EVAL", entities: { decision_number: 3421 } }
      },
      {
        input: "ניתוח החלטת הממשלה 1823",
        expected: { intent_type: "EVAL", entities: { decision_number: 1823 } }
      },
      {
        input: "בחן לעומק את החלטה 975",
        expected: { intent_type: "EVAL", entities: { decision_number: 975 } }
      },
      {
        input: "ניתוח יסודי של החלטה 2641",
        expected: { intent_type: "EVAL", entities: { decision_number: 2641 } }
      },
      {
        input: "הסבר לעומק את החלטה 1122",
        expected: { intent_type: "EVAL", entities: { decision_number: 1122 } }
      },
      {
        input: "פרט באופן מעמיק על החלטה 3089",
        expected: { intent_type: "EVAL", entities: { decision_number: 3089 } }
      }
    ];

    evalTests.forEach((test, index) => this.runTest(`EVAL-${index + 1}`, test));
  }

  testEdgeCases() {
    console.log('\n🎭 Testing Edge Cases...');
    
    const edgeCases = [
      // Should be CLARIFICATION
      {
        input: "מה?",
        expected: { intent_type: "CLARIFICATION" }
      },
      {
        input: "החלטות",
        expected: { intent_type: "CLARIFICATION" }
      },
      {
        input: "נתח",
        expected: { intent_type: "CLARIFICATION" }
      },
      // Should be QUERY, not EVAL
      {
        input: "נתח את כל ההחלטות",
        expected: { intent_type: "QUERY", entities: { operation: "search" } }
      },
      {
        input: "נתח את 3 ההחלטות האחרונות בנושא ביטחון",
        expected: { intent_type: "QUERY", entities: { limit: 3, topic: "ביטחון", operation: "search" } }
      }
    ];

    edgeCases.forEach((test, index) => this.runTest(`EDGE-${index + 1}`, test));
  }

  runTest(testName, test) {
    this.testResults.total++;
    
    const startTime = process.hrtime.bigint();
    const result = this.detector.detect(test.input);
    const endTime = process.hrtime.bigint();
    
    const responseTime = Number(endTime - startTime) / 1000000; // Convert to milliseconds
    
    let passed = true;
    let failures = [];

    // Check intent_type
    if (result.intent_type !== test.expected.intent_type) {
      passed = false;
      failures.push(`Intent: expected ${test.expected.intent_type}, got ${result.intent_type}`);
    }

    // Check entities
    if (test.expected.entities) {
      for (const [key, expectedValue] of Object.entries(test.expected.entities)) {
        if (key === 'operation') {
          if (result.entities[key] !== expectedValue) {
            passed = false;
            failures.push(`Entity ${key}: expected ${expectedValue}, got ${result.entities[key]}`);
          }
        } else if (key === 'ministries' && Array.isArray(expectedValue)) {
          if (!result.entities[key] || !this.arraysEqual(result.entities[key], expectedValue)) {
            passed = false;
            failures.push(`Entity ${key}: expected ${JSON.stringify(expectedValue)}, got ${JSON.stringify(result.entities[key])}`);
          }
        } else if (key === 'date_range' && typeof expectedValue === 'object') {
          if (!result.entities[key] || 
              result.entities[key].start !== expectedValue.start || 
              result.entities[key].end !== expectedValue.end) {
            passed = false;
            failures.push(`Entity ${key}: expected ${JSON.stringify(expectedValue)}, got ${JSON.stringify(result.entities[key])}`);
          }
        } else if (result.entities[key] !== expectedValue) {
          passed = false;
          failures.push(`Entity ${key}: expected ${expectedValue}, got ${result.entities[key]}`);
        }
      }
    }

    // Check route_flags
    if (test.expected.route_flags) {
      for (const [key, expectedValue] of Object.entries(test.expected.route_flags)) {
        if (result.route_flags[key] !== expectedValue) {
          passed = false;
          failures.push(`Route flag ${key}: expected ${expectedValue}, got ${result.route_flags[key]}`);
        }
      }
    }

    if (passed) {
      this.testResults.passed++;
      console.log(`✅ ${testName}: PASSED (${responseTime.toFixed(3)}ms)`);
    } else {
      this.testResults.failed++;
      console.log(`❌ ${testName}: FAILED (${responseTime.toFixed(3)}ms)`);
      console.log(`   Input: "${test.input}"`);
      console.log(`   Failures: ${failures.join(', ')}`);
      console.log(`   Got: ${JSON.stringify(result, null, 2)}`);
      
      this.testResults.failures.push({
        testName,
        input: test.input,
        expected: test.expected,
        actual: result,
        failures
      });
    }

    // Performance check
    if (responseTime > 1.0) {
      console.log(`⚠️  Performance warning: ${testName} took ${responseTime.toFixed(3)}ms (>1ms)`);
    }
  }

  arraysEqual(arr1, arr2) {
    if (!arr1 || !arr2) return false;
    if (arr1.length !== arr2.length) return false;
    return arr1.every((val, index) => val === arr2[index]);
  }

  printResults() {
    console.log('\n📊 Test Results Summary:');
    console.log('========================');
    console.log(`Total Tests: ${this.testResults.total}`);
    console.log(`Passed: ${this.testResults.passed}`);
    console.log(`Failed: ${this.testResults.failed}`);
    console.log(`Success Rate: ${((this.testResults.passed / this.testResults.total) * 100).toFixed(1)}%`);

    if (this.testResults.failed > 0) {
      console.log('\n❌ Failed Tests:');
      this.testResults.failures.forEach(failure => {
        console.log(`\n${failure.testName}:`);
        console.log(`  Input: "${failure.input}"`);
        console.log(`  Issues: ${failure.failures.join(', ')}`);
      });
    }

    if (this.testResults.passed === this.testResults.total) {
      console.log('\n🎉 ALL TESTS PASSED! Intent Detector is working correctly.');
    } else {
      console.log(`\n⚠️  ${this.testResults.failed} tests failed. Please review and fix.`);
    }
  }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new IntentDetectorTester();
  tester.runAllTests();
}

export default IntentDetectorTester;