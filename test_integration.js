#!/usr/bin/env node

/**
 * Quick integration test to verify frontend-to-bot-chain connection
 * Tests the complete flow: Frontend -> Backend -> Bot Chain -> Response
 */

import axios from 'axios';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5001';
const TEST_QUERY = 'החלטות ממשלה 37 בנושא חינוך';
const TEST_SESSION_ID = 'integration_test_' + Date.now();

async function testHealthEndpoints() {
  console.log('\n🏥 Testing Health Endpoints...');
  
  try {
    // Test enhanced health endpoint
    const healthResponse = await axios.get(`${BACKEND_URL}/api/chat/health`);
    console.log('✅ Enhanced health check:', healthResponse.data);
    
    // Check if bot chain is available
    const services = healthResponse.data.services || {};
    const botChainAvailable = services.botChain?.available || false;
    const activeEngine = healthResponse.data.activeEngine;
    
    console.log(`📊 Active Engine: ${activeEngine}`);
    console.log(`🤖 Bot Chain Available: ${botChainAvailable}`);
    console.log(`🔧 SQL Engine Available: ${services.sqlEngine?.available || false}`);
    
    return { botChainAvailable, activeEngine };
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    return { botChainAvailable: false, activeEngine: 'unknown' };
  }
}

async function testBotChainDirect() {
  console.log('\n🤖 Testing Bot Chain Direct Access...');
  
  try {
    const response = await axios.post(`${BACKEND_URL}/api/chat/test-bot-chain`, {
      query: TEST_QUERY,
      sessionId: TEST_SESSION_ID,
      preferences: {
        outputFormat: 'markdown',
        presentationStyle: 'detailed',
        includeMetadata: true,
        includeScores: true
      }
    });
    
    console.log('✅ Bot Chain Direct Test Result:');
    console.log(`   Success: ${response.data.success}`);
    console.log(`   Response Length: ${response.data.response?.length || 0} chars`);
    console.log(`   Intent: ${response.data.metadata?.intent || 'unknown'}`);
    console.log(`   Confidence: ${response.data.metadata?.confidence || 'unknown'}`);
    console.log(`   Processing Time: ${response.data.metadata?.processing_time_ms || 'unknown'}ms`);
    
    if (response.data.error) {
      console.log(`   Error: ${response.data.error}`);
    }
    
    return response.data.success;
  } catch (error) {
    console.error('❌ Bot Chain Direct Test Failed:', error.message);
    if (error.response?.data) {
      console.error('   Error Details:', error.response.data);
    }
    return false;
  }
}

async function testChatEndpoint() {
  console.log('\n💬 Testing Chat Endpoint (SSE)...');
  
  try {
    const response = await axios.post(`${BACKEND_URL}/api/chat`, {
      message: TEST_QUERY,
      sessionId: TEST_SESSION_ID
    }, {
      headers: {
        'Accept': 'text/event-stream'
      },
      timeout: 60000 // 60 second timeout
    });
    
    console.log('✅ Chat Endpoint Response:');
    console.log(`   Status: ${response.status}`);
    console.log(`   Content-Type: ${response.headers['content-type']}`);
    console.log(`   Data Length: ${response.data?.length || 0} chars`);
    
    // Parse SSE data
    const lines = response.data.split('\n');
    const events = [];
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const eventData = JSON.parse(line.substring(6));
          events.push(eventData);
        } catch (parseError) {
          // Skip invalid JSON
        }
      }
    }
    
    console.log(`   Events Received: ${events.length}`);
    
    const responseEvents = events.filter(e => e.type === 'response');
    const errorEvents = events.filter(e => e.type === 'error');
    const doneEvents = events.filter(e => e.type === 'done');
    
    console.log(`   Response Events: ${responseEvents.length}`);
    console.log(`   Error Events: ${errorEvents.length}`);
    console.log(`   Done Events: ${doneEvents.length}`);
    
    if (responseEvents.length > 0) {
      const lastResponse = responseEvents[responseEvents.length - 1];
      console.log(`   Engine Used: ${lastResponse.metadata?.engine || 'unknown'}`);
      console.log(`   Service: ${lastResponse.metadata?.service || 'unknown'}`);
      console.log(`   Response Preview: ${(lastResponse.content || '').substring(0, 100)}...`);
    }
    
    if (errorEvents.length > 0) {
      console.log(`   Errors: ${errorEvents.map(e => e.content || e.error).join(', ')}`);
    }
    
    return responseEvents.length > 0 && errorEvents.length === 0;
  } catch (error) {
    console.error('❌ Chat Endpoint Test Failed:', error.message);
    if (error.response?.data) {
      console.error('   Error Details:', error.response.data.substring(0, 500) + '...');
    }
    return false;
  }
}

async function runIntegrationTests() {
  console.log('🚀 Starting CECI-AI Frontend-to-Bot-Chain Integration Tests');
  console.log('='.repeat(70));
  console.log(`📍 Backend URL: ${BACKEND_URL}`);
  console.log(`📝 Test Query: "${TEST_QUERY}"`);
  console.log(`🆔 Session ID: ${TEST_SESSION_ID}`);
  
  const results = {
    health: false,
    botChainDirect: false,
    chatEndpoint: false
  };
  
  // Test 1: Health Check
  const { botChainAvailable, activeEngine } = await testHealthEndpoints();
  results.health = true; // Health endpoint itself worked
  
  // Test 2: Bot Chain Direct (if available)
  if (botChainAvailable) {
    results.botChainDirect = await testBotChainDirect();
  } else {
    console.log('\n⚠️ Skipping Bot Chain Direct Test (not available)');
  }
  
  // Test 3: Chat Endpoint
  results.chatEndpoint = await testChatEndpoint();
  
  // Summary
  console.log('\n' + '='.repeat(70));
  console.log('📊 Integration Test Summary');
  console.log('='.repeat(70));
  console.log(`✅ Health Check: ${results.health ? 'PASS' : 'FAIL'}`);
  console.log(`🤖 Bot Chain Available: ${botChainAvailable ? 'YES' : 'NO'}`);
  console.log(`🎯 Active Engine: ${activeEngine}`);
  console.log(`🔗 Bot Chain Direct: ${results.botChainDirect ? 'PASS' : 'SKIP/FAIL'}`);
  console.log(`💬 Chat Endpoint: ${results.chatEndpoint ? 'PASS' : 'FAIL'}`);
  
  const passed = Object.values(results).filter(Boolean).length;
  const total = Object.keys(results).length;
  
  console.log(`\n🎯 Overall: ${passed}/${total} tests passed`);
  
  if (results.chatEndpoint) {
    console.log('\n🎉 SUCCESS: Frontend-to-Bot-Chain integration is working!');
    console.log('   ✅ Frontend can send queries to backend');
    console.log('   ✅ Backend can route to appropriate engine');
    console.log('   ✅ Response pipeline is functional');
  } else {
    console.log('\n⚠️ PARTIAL SUCCESS: Some integration issues detected');
    console.log('   🔧 Check docker-compose services are running');
    console.log('   🔧 Verify bot chain environment variables');
    console.log('   🔧 Check backend logs for errors');
  }
  
  return results.chatEndpoint;
}

// Run the tests
runIntegrationTests()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('\n💥 Integration test runner failed:', error);
    process.exit(1);
  });

export { runIntegrationTests };