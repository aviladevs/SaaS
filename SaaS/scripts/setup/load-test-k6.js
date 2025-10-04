// Ávila DevOps SaaS - Load Testing Script (k6)
// Tests system capacity under high load scenarios
// Target: 1000+ concurrent requests per second

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const failureRate = new Rate('failed_requests');
const responseTimeTrend = new Trend('response_time');
const successfulRequests = new Counter('successful_requests');
const failedRequests = new Counter('failed_requests_counter');

// Test configuration
export const options = {
  stages: [
    // Warm-up phase
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '3m', target: 300 },   // Ramp up to 300 users
    
    // Baseline test
    { duration: '5m', target: 500 },   // Ramp up to 500 users
    { duration: '10m', target: 500 },  // Stay at 500 users
    
    // Peak load test
    { duration: '3m', target: 1000 },  // Ramp up to 1000 users
    { duration: '10m', target: 1000 }, // Stay at 1000 users (main test)
    
    // Stress test (optional - stretch goal)
    { duration: '2m', target: 1500 },  // Push to 1500 users
    { duration: '5m', target: 1500 },  // Stay at 1500 users
    
    // Cool down
    { duration: '3m', target: 100 },   // Ramp down
    { duration: '1m', target: 0 },     // Stop
  ],
  
  thresholds: {
    // Success criteria
    'http_req_duration': ['p(95)<300', 'p(99)<500'],  // 95% < 300ms, 99% < 500ms
    'http_req_failed': ['rate<0.01'],                  // Error rate < 1%
    'failed_requests': ['rate<0.01'],                  // Custom failure rate < 1%
    'http_reqs': ['rate>1000'],                        // Target: 1000+ req/s
  },
  
  // Global settings
  noConnectionReuse: false,
  userAgent: 'k6-load-test/1.0',
};

// Base URL - configure for your environment
const BASE_URL = __ENV.BASE_URL || 'https://aviladevops.com.br';

// Test scenarios
const scenarios = {
  // Landing page - high traffic
  landingPage: {
    url: `${BASE_URL}/`,
    weight: 30,
  },
  
  // API endpoints - medium traffic
  apiList: {
    url: `${BASE_URL}/api/services/`,
    weight: 25,
  },
  
  apiDetail: {
    url: `${BASE_URL}/api/services/1/`,
    weight: 15,
  },
  
  // Sistema de Reciclagem - medium traffic
  recyclingDashboard: {
    url: `${BASE_URL}/sistema/dashboard/`,
    weight: 10,
  },
  
  // Fiscal system - low traffic
  fiscalDashboard: {
    url: `${BASE_URL}/fiscal/dashboard/`,
    weight: 8,
  },
  
  // Static resources - high traffic
  staticCSS: {
    url: `${BASE_URL}/static/css/main.css`,
    weight: 7,
  },
  
  staticJS: {
    url: `${BASE_URL}/static/js/app.js`,
    weight: 5,
  },
};

// Get random scenario based on weights
function getRandomScenario() {
  const scenarios_array = Object.entries(scenarios);
  const totalWeight = scenarios_array.reduce((sum, [_, s]) => sum + s.weight, 0);
  let random = Math.random() * totalWeight;
  
  for (const [name, scenario] of scenarios_array) {
    random -= scenario.weight;
    if (random <= 0) {
      return scenario;
    }
  }
  
  return scenarios_array[0][1];
}

// Main test function
export default function() {
  const scenario = getRandomScenario();
  
  group('Load Test - Mixed Traffic', () => {
    const params = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/html',
        'X-Test-Run': 'k6-load-test',
      },
      timeout: '30s',
    };
    
    const response = http.get(scenario.url, params);
    
    // Record metrics
    responseTimeTrend.add(response.timings.duration);
    
    // Validate response
    const success = check(response, {
      'status is 200-299': (r) => r.status >= 200 && r.status < 300,
      'response time < 300ms': (r) => r.timings.duration < 300,
      'response time < 500ms': (r) => r.timings.duration < 500,
      'response time < 1000ms': (r) => r.timings.duration < 1000,
      'has content': (r) => r.body.length > 0,
    });
    
    if (success) {
      successfulRequests.add(1);
    } else {
      failedRequests.add(1);
      failureRate.add(1);
    }
    
    if (!success) {
      failureRate.add(1);
    } else {
      failureRate.add(0);
    }
  });
  
  // Realistic user behavior - small random delay between requests
  sleep(Math.random() * 0.5);
}

// Specific scenario tests
export function testLandingPage() {
  group('Landing Page Test', () => {
    const response = http.get(`${BASE_URL}/`);
    check(response, {
      'landing page loads': (r) => r.status === 200,
      'contains title': (r) => r.body.includes('Ávila DevOps'),
    });
  });
}

export function testAPIEndpoints() {
  group('API Endpoints Test', () => {
    // Test API list
    const listResponse = http.get(`${BASE_URL}/api/services/`);
    check(listResponse, {
      'API list returns 200': (r) => r.status === 200,
      'API response is JSON': (r) => r.headers['Content-Type'].includes('application/json'),
    });
    
    // Test API detail
    const detailResponse = http.get(`${BASE_URL}/api/services/1/`);
    check(detailResponse, {
      'API detail returns 200 or 404': (r) => r.status === 200 || r.status === 404,
    });
  });
}

export function testAuthFlow() {
  group('Authentication Flow Test', () => {
    // Test login page
    const loginPage = http.get(`${BASE_URL}/admin/login/`);
    check(loginPage, {
      'login page loads': (r) => r.status === 200,
    });
    
    // Note: Actual login test would require credentials
    // This is a placeholder for authentication testing
  });
}

export function testStaticResources() {
  group('Static Resources Test', () => {
    const batch = http.batch([
      ['GET', `${BASE_URL}/static/css/main.css`],
      ['GET', `${BASE_URL}/static/js/app.js`],
      ['GET', `${BASE_URL}/static/images/logo.png`],
    ]);
    
    batch.forEach((response) => {
      check(response, {
        'static resource loads': (r) => r.status === 200 || r.status === 404,
        'has cache headers': (r) => r.headers['Cache-Control'] !== undefined,
      });
    });
  });
}

// Setup function - runs once before all tests
export function setup() {
  console.log('🚀 Starting load test...');
  console.log(`📊 Target: 1000+ req/s`);
  console.log(`🎯 Success criteria: <300ms p95, <1% error rate`);
  console.log(`🌐 Base URL: ${BASE_URL}`);
  
  // Health check
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    console.warn('⚠️  Health check failed - system may not be ready');
  } else {
    console.log('✅ Health check passed - system is ready');
  }
  
  return { startTime: Date.now() };
}

// Teardown function - runs once after all tests
export function teardown(data) {
  const duration = (Date.now() - data.startTime) / 1000 / 60;
  console.log(`\n✅ Load test completed in ${duration.toFixed(2)} minutes`);
  console.log('📈 Check the results for performance metrics');
}

// Handle summary - custom output
export function handleSummary(data) {
  const timestamp = new Date().toISOString();
  
  return {
    'stdout': textSummary(data, { indent: '  ', enableColors: true }),
    [`load-test-results-${timestamp}.json`]: JSON.stringify(data, null, 2),
  };
}

function textSummary(data, options) {
  const indent = options.indent || '';
  const enableColors = options.enableColors || false;
  
  let summary = '\n' + indent + '='.repeat(60) + '\n';
  summary += indent + '📊 LOAD TEST SUMMARY\n';
  summary += indent + '='.repeat(60) + '\n\n';
  
  // Basic stats
  summary += indent + '📈 Request Statistics:\n';
  summary += indent + `  Total Requests: ${data.metrics.http_reqs.values.count}\n`;
  summary += indent + `  Request Rate: ${data.metrics.http_reqs.values.rate.toFixed(2)} req/s\n`;
  summary += indent + `  Failed Requests: ${data.metrics.http_req_failed.values.count}\n`;
  summary += indent + `  Failure Rate: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%\n\n`;
  
  // Response times
  summary += indent + '⏱️  Response Times:\n';
  summary += indent + `  Average: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
  summary += indent + `  Median (p50): ${data.metrics.http_req_duration.values.med.toFixed(2)}ms\n`;
  summary += indent + `  p95: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
  summary += indent + `  p99: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms\n`;
  summary += indent + `  Max: ${data.metrics.http_req_duration.values.max.toFixed(2)}ms\n\n`;
  
  // Success criteria
  summary += indent + '✅ Success Criteria:\n';
  const p95 = data.metrics.http_req_duration.values['p(95)'];
  const errorRate = data.metrics.http_req_failed.values.rate;
  const reqRate = data.metrics.http_reqs.values.rate;
  
  summary += indent + `  p95 < 300ms: ${p95 < 300 ? '✅ PASS' : '❌ FAIL'} (${p95.toFixed(2)}ms)\n`;
  summary += indent + `  Error rate < 1%: ${errorRate < 0.01 ? '✅ PASS' : '❌ FAIL'} (${(errorRate * 100).toFixed(2)}%)\n`;
  summary += indent + `  Rate > 1000 req/s: ${reqRate > 1000 ? '✅ PASS' : '❌ FAIL'} (${reqRate.toFixed(2)} req/s)\n\n`;
  
  summary += indent + '='.repeat(60) + '\n';
  
  return summary;
}
