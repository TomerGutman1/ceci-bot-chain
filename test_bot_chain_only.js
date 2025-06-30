#!/usr/bin/env node

import axios from 'axios';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5001';

async function testBotChainAPI() {
  console.log('🤖 Testing Bot Chain API');
  console.log('=' .repeat(50));
  
  try {
    // 1. Health Check
    console.log('\n1️⃣ Health Check...');
    const health = await axios.get(`${BACKEND_URL}/api/chat/health`);
    console.log('✅ Health Response:', JSON.stringify(health.data, null, 2));
    
    if (!health.data.services?.botChain?.available) {
      console.error('❌ Bot chain is not available!');
      return false;
    }
    
    if (!health.data.services?.botChain?.enabled) {
      console.error('❌ Bot chain is not enabled! Set BOT_CHAIN_ENABLED=true');
      return false;
    }
    
    // 2. Direct Bot Chain Test
    console.log('\n2️⃣ Direct Bot Chain Test...');
    const testQuery = 'החלטות ממשלה 37 בנושא חינוך';
    
    const testResponse = await axios.post(`${BACKEND_URL}/api/chat/test-bot-chain`, {
      query: testQuery,
      sessionId: 'test_' + Date.now(),
      preferences: {
        outputFormat: 'markdown',
        includeMetadata: true
      }
    });
    
    console.log('✅ Bot Chain Response:');
    console.log('   Success:', testResponse.data.success);
    console.log('   Response Length:', testResponse.data.response?.length || 0);
    console.log('   Intent:', testResponse.data.metadata?.intent);
    console.log('   Confidence:', testResponse.data.metadata?.confidence);
    
    if (!testResponse.data.success) {
      console.error('❌ Bot chain test failed:', testResponse.data.error);
      return false;
    }
    
    // 3. Chat Endpoint Test (SSE)
    console.log('\n3️⃣ Chat Endpoint Test (Main API)...');
    
    const chatResponse = await axios.post(`${BACKEND_URL}/api/chat`, {
      message: testQuery,
      sessionId: 'chat_test_' + Date.now()
    }, {
      headers: {
        'Accept': 'text/event-stream'
      },
      timeout: 30000
    });
    
    // Parse SSE response
    const lines = chatResponse.data.split('\n');
    let responseFound = false;
    let errorFound = false;
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const event = JSON.parse(line.substring(6));
          if (event.type === 'response') {
            responseFound = true;
            console.log('✅ Chat Response Received');
            console.log('   Engine:', event.metadata?.engine);
            console.log('   Content Preview:', event.content.substring(0, 100) + '...');
          }
          if (event.type === 'error') {
            errorFound = true;
            console.error('❌ Error:', event.error);
          }
        } catch (e) {
          // Skip invalid JSON
        }
      }
    }
    
    if (!responseFound || errorFound) {
      console.error('❌ Chat endpoint test failed');
      return false;
    }
    
    console.log('\n✅ All tests passed! Bot chain is working correctly.');
    return true;
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    if (error.response) {
      console.error('Response:', error.response.data);
    }
    return false;
  }
}

// Run the test
testBotChainAPI()
  .then(success => {
    console.log('\n' + '='.repeat(50));
    if (success) {
      console.log('🎉 Bot Chain Integration: WORKING');
    } else {
      console.log('❌ Bot Chain Integration: FAILED');
      console.log('\nTroubleshooting:');
      console.log('1. Ensure BOT_CHAIN_ENABLED=true in environment');
      console.log('2. Start bot chain services: docker compose up -d');
      console.log('3. Check bot URLs in environment variables');
    }
    process.exit(success ? 0 : 1);
  })
  .catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });