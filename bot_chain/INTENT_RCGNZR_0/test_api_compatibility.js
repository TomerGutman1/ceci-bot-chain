/**
 * Test script to verify Intent Recognizer API compatibility
 */

const http = require('http');

// Test cases
const testCases = [
  {
    name: "Simple search query",
    request: {
      text: "החלטות ממשלה 37 בנושא חינוך",
      conv_id: "test-123"
    },
    expected: {
      intent_type: "QUERY",
      entities: {
        government_number: 37,
        topic: "חינוך"
      }
    }
  },
  {
    name: "Statistical query",
    request: {
      text: "כמה החלטות יש בנושא בריאות?",
      conv_id: "test-456"
    },
    expected: {
      intent_type: "STATISTICAL",
      entities: {
        topic: "בריאות"
      }
    }
  },
  {
    name: "Eval query",
    request: {
      text: "נתח את החלטה 2948 לעומק",
      conv_id: "test-789"
    },
    expected: {
      intent_type: "EVAL",
      entities: {
        decision_number: 2948
      }
    }
  }
];

// Function to make HTTP request
function testEndpoint(testCase) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(testCase.request);
    
    const options = {
      hostname: 'localhost',
      port: 8011,
      path: '/intent',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };
    
    const req = http.request(options, (res) => {
      let responseData = '';
      
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        try {
          const response = JSON.parse(responseData);
          
          // Verify response structure
          const passed = 
            response.conv_id === testCase.request.conv_id &&
            response.intent_type === testCase.expected.intent_type &&
            response.entities &&
            response.confidence !== undefined &&
            response.route_flags &&
            response.timestamp &&
            response.layer === "1_MAIN_INTENT_BOT";
          
          console.log(`\nTest: ${testCase.name}`);
          console.log(`Status: ${passed ? '✅ PASSED' : '❌ FAILED'}`);
          console.log(`Response:`, JSON.stringify(response, null, 2));
          
          resolve({ testCase: testCase.name, passed, response });
        } catch (error) {
          console.error(`\nTest: ${testCase.name}`);
          console.error(`Status: ❌ FAILED - Invalid JSON response`);
          console.error(`Error:`, error.message);
          resolve({ testCase: testCase.name, passed: false, error: error.message });
        }
      });
    });
    
    req.on('error', (error) => {
      console.error(`\nTest: ${testCase.name}`);
      console.error(`Status: ❌ FAILED - Request error`);
      console.error(`Error:`, error.message);
      resolve({ testCase: testCase.name, passed: false, error: error.message });
    });
    
    req.write(data);
    req.end();
  });
}

// Test health endpoint
function testHealth() {
  return new Promise((resolve, reject) => {
    http.get('http://localhost:8011/health', (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const health = JSON.parse(data);
          console.log('\nHealth Check:');
          console.log(`Status: ${health.status === 'ok' ? '✅ OK' : '❌ FAILED'}`);
          console.log(`Response:`, JSON.stringify(health, null, 2));
          resolve({ passed: health.status === 'ok', health });
        } catch (error) {
          console.error('\nHealth Check: ❌ FAILED');
          console.error('Error:', error.message);
          resolve({ passed: false, error: error.message });
        }
      });
    }).on('error', (error) => {
      console.error('\nHealth Check: ❌ FAILED');
      console.error('Error:', error.message);
      resolve({ passed: false, error: error.message });
    });
  });
}

// Run all tests
async function runTests() {
  console.log('Testing Intent Recognizer API Compatibility');
  console.log('==========================================');
  
  // Test health endpoint first
  const healthResult = await testHealth();
  
  if (!healthResult.passed) {
    console.error('\n❌ Health check failed. Is the service running on port 8011?');
    process.exit(1);
  }
  
  // Run test cases
  const results = [];
  for (const testCase of testCases) {
    const result = await testEndpoint(testCase);
    results.push(result);
  }
  
  // Summary
  console.log('\n\nTest Summary');
  console.log('============');
  const passed = results.filter(r => r.passed).length;
  const total = results.length;
  console.log(`Total: ${total}`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${total - passed}`);
  console.log(`Success Rate: ${(passed / total * 100).toFixed(1)}%`);
  
  process.exit(passed === total ? 0 : 1);
}

// Check if service is ready
console.log('Waiting for service to be ready...');
setTimeout(runTests, 2000);
