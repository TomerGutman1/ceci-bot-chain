// Test script to directly check decision search functionality
import dotenv from 'dotenv';
import path from 'path';
import { getDecisionSearchService } from './src/services/decisionSearchService';

// Load environment variables
dotenv.config({ path: path.join(__dirname, '.env.local') });

console.log('=== Decision Search Service Test ===');
console.log(`Time: ${new Date().toISOString()}`);
console.log('Environment variables loaded:', {
  SUPABASE_URL: process.env.SUPABASE_URL ? '✓' : '✗',
  SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY ? '✓' : '✗'
});

async function testService() {
  try {
    // Initialize service
    console.log('\n1. Initializing service...');
    const service = getDecisionSearchService();
    
    // Load decisions
    console.log('2. Loading decisions from Supabase...');
    const startTime = Date.now();
    await service.loadDecisions();
    const loadTime = (Date.now() - startTime) / 1000;
    
    // Get status
    const status = service.getStatus();
    console.log(`3. Service status:`, status);
    console.log(`   Load time: ${loadTime}s`);
    
    // Test searches
    const testQueries = [
      'חינוך',
      'בריאות',
      'תקציב',
      'קורונה',
      'דיור'
    ];
    
    console.log('\n4. Testing searches:');
    for (const query of testQueries) {
      const results = await service.search(query, 3);
      console.log(`   "${query}": ${results.length} results`);
      if (results.length > 0) {
        console.log(`      First result: ${results[0].title.substring(0, 50)}...`);
      }
    }
    
    console.log('\n✅ All tests passed!');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error);
  }
}

// Run test
testService().then(() => {
  console.log('\nTest completed');
  process.exit(0);
}).catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
