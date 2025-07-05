#!/usr/bin/env node

/**
 * Test Token Reporting in Bot Chain
 * This script tests that token usage is properly reported for each bot
 */

const axios = require('axios');
const colors = require('colors/safe');

// Configuration
const API_URL = 'http://localhost:5001/api/chat';
const TEST_QUERIES = [
  {
    name: "Simple topic search",
    query: "החלטות בנושא חינוך",
    expected_bots: ["REWRITE", "INTENT", "SQLGEN", "FORMATTER"]
  },
  {
    name: "Government + topic search",
    query: "החלטות ממשלה 37 בנושא בריאות",
    expected_bots: ["REWRITE", "INTENT", "SQLGEN", "FORMATTER"]
  },
  {
    name: "Limited results search",
    query: "3 החלטות אחרונות בנושא תחבורה",
    expected_bots: ["REWRITE", "INTENT", "SQLGEN", "RANKER", "FORMATTER"]
  }
];

// Helper to format currency
function formatUSD(amount) {
  return `$${amount.toFixed(4)}`;
}

// Helper to make API call
async function testQuery(testCase) {
  console.log(colors.blue(`\n${'='.repeat(60)}`));
  console.log(colors.blue(`Testing: ${testCase.name}`));
  console.log(colors.blue(`Query: "${testCase.query}"`));
  console.log(colors.blue(`${'='.repeat(60)}\n`));

  try {
    const startTime = Date.now();
    
    // Make the API call
    const response = await axios.post(API_URL, {
      message: testCase.query,
      sessionId: `test-token-${Date.now()}`
    }, {
      headers: {
        'Content-Type': 'application/json'
      },
      // Need to handle SSE response
      responseType: 'text'
    });

    const duration = Date.now() - startTime;
    
    // Parse SSE response
    const lines = response.data.split('\n');
    let finalData = null;
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.substring(6));
          if (data.final) {
            finalData = data;
          }
        } catch (e) {
          // Skip non-JSON lines
        }
      }
    }

    if (!finalData) {
      console.error(colors.red('❌ No final response received'));
      return;
    }

    // Check if we have metadata with token usage
    if (!finalData.metadata) {
      console.error(colors.red('❌ No metadata in response'));
      return;
    }

    if (!finalData.metadata.token_usage) {
      console.error(colors.red('❌ No token_usage in metadata'));
      console.log('Metadata:', JSON.stringify(finalData.metadata, null, 2));
      return;
    }

    const tokenUsage = finalData.metadata.token_usage;
    
    // Display token usage summary
    console.log(colors.green('✅ Token Usage Summary:'));
    console.log(`   Total Tokens: ${colors.yellow(tokenUsage.total_tokens)}`);
    console.log(`   Prompt Tokens: ${tokenUsage.prompt_tokens}`);
    console.log(`   Completion Tokens: ${tokenUsage.completion_tokens}`);
    console.log(`   Estimated Cost: ${colors.yellow(formatUSD(tokenUsage.estimated_cost_usd))}`);
    console.log(`   Processing Time: ${duration}ms`);
    
    // Display breakdown by bot
    if (tokenUsage.bot_breakdown) {
      console.log(colors.green('\n📊 Token Usage by Bot:'));
      const breakdown = tokenUsage.bot_breakdown;
      
      // Sort bots by token usage
      const sortedBots = Object.entries(breakdown)
        .sort((a, b) => b[1].tokens - a[1].tokens);
      
      for (const [botName, usage] of sortedBots) {
        const percentage = ((usage.tokens / tokenUsage.total_tokens) * 100).toFixed(1);
        console.log(`   ${colors.cyan(botName.padEnd(15))} ${usage.tokens.toString().padStart(6)} tokens (${percentage.padStart(5)}%) ${colors.yellow(formatUSD(usage.cost_usd))}`);
      }
      
      // Check if expected bots reported tokens
      console.log(colors.green('\n🔍 Bot Coverage Check:'));
      for (const expectedBot of testCase.expected_bots) {
        if (breakdown[expectedBot]) {
          console.log(`   ✅ ${expectedBot}: ${breakdown[expectedBot].tokens} tokens`);
        } else {
          console.log(`   ❌ ${expectedBot}: No token usage reported`);
        }
      }
    } else {
      console.error(colors.red('❌ No bot_breakdown in token_usage'));
    }
    
    // Display query metadata
    console.log(colors.green('\n📋 Query Metadata:'));
    console.log(`   Intent: ${finalData.metadata.intent}`);
    console.log(`   Confidence: ${finalData.metadata.confidence}`);
    console.log(`   Service: ${finalData.metadata.service}`);
    
    // Show result count
    const resultCount = (finalData.response.match(/## \d+\./g) || []).length;
    console.log(`   Results Found: ${resultCount}`);
    
  } catch (error) {
    console.error(colors.red(`\n❌ Test failed: ${error.message}`));
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

// Main test runner
async function runTests() {
  console.log(colors.bold.green('\n🚀 Starting Token Reporting Tests\n'));
  
  // Check if API is available
  try {
    await axios.get('http://localhost:5001/api/chat/health');
    console.log(colors.green('✅ API is healthy\n'));
  } catch (error) {
    console.error(colors.red('❌ API health check failed. Is the server running?'));
    process.exit(1);
  }
  
  // Run each test case
  for (const testCase of TEST_QUERIES) {
    await testQuery(testCase);
    
    // Wait a bit between tests
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  console.log(colors.bold.green('\n✅ All tests completed!\n'));
  
  // Summary recommendations
  console.log(colors.yellow('💡 Optimization Tips:'));
  console.log('   - If REWRITE uses many tokens, consider shortening prompts');
  console.log('   - If SQLGEN uses GPT instead of templates, add more templates');
  console.log('   - If RANKER is expensive, consider skipping for simple queries');
  console.log('   - Monitor which bots contribute most to costs');
}

// Run the tests
runTests().catch(console.error);
