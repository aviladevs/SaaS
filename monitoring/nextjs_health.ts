/**
 * Health Check and Monitoring Utilities for Next.js Applications
 * 
 * Installation:
 * npm install prom-client
 * 
 * Usage:
 * 1. Create pages/api/health.ts with the healthCheck handler
 * 2. Create pages/api/metrics.ts with the metricsHandler
 * 3. Import and use metric functions throughout your app
 */

import { NextApiRequest, NextApiResponse } from 'next';

// Prometheus client for metrics
let promClient: any;
let register: any;
let httpRequestDuration: any;
let httpRequestTotal: any;
let activeConnections: any;
let businessMetrics: any = {};

try {
  promClient = require('prom-client');
  register = new promClient.Registry();
  
  // Default metrics
  promClient.collectDefaultMetrics({ register });
  
  // HTTP request duration histogram
  httpRequestDuration = new promClient.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.01, 0.05, 0.1, 0.3, 0.5, 1, 2, 5],
    registers: [register]
  });
  
  // HTTP request counter
  httpRequestTotal = new promClient.Counter({
    name: 'http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'route', 'status_code'],
    registers: [register]
  });
  
  // Active connections gauge
  activeConnections = new promClient.Gauge({
    name: 'active_connections',
    help: 'Number of active connections',
    registers: [register]
  });
  
  // Business metrics
  businessMetrics = {
    userRegistrations: new promClient.Counter({
      name: 'saas_user_registrations_total',
      help: 'Total user registrations',
      labelNames: ['tenant'],
      registers: [register]
    }),
    
    userLogins: new promClient.Counter({
      name: 'saas_user_logins_total',
      help: 'Total user logins',
      labelNames: ['tenant'],
      registers: [register]
    }),
    
    activeUsers: new promClient.Gauge({
      name: 'saas_active_users_total',
      help: 'Number of active users',
      labelNames: ['tenant'],
      registers: [register]
    }),
    
    appointments: new promClient.Counter({
      name: 'saas_appointments_total',
      help: 'Total appointments scheduled',
      labelNames: ['tenant', 'status'],
      registers: [register]
    }),
    
    payments: new promClient.Counter({
      name: 'saas_payment_attempts_total',
      help: 'Total payment attempts',
      labelNames: ['tenant', 'status'],
      registers: [register]
    })
  };
  
} catch (error) {
  console.warn('prom-client not installed. Metrics will not be available.');
}

/**
 * Health check response type
 */
interface HealthCheck {
  status: 'healthy' | 'unhealthy';
  timestamp: number;
  service: string;
  version: string;
  environment: string;
  checks: {
    [key: string]: {
      status: 'pass' | 'fail';
      message: string;
    };
  };
  response_time_ms: number;
}

/**
 * Check database connectivity (example - adapt to your DB)
 */
async function checkDatabase(): Promise<[boolean, string]> {
  try {
    // Replace with your actual database check
    // Example: await prisma.$queryRaw`SELECT 1`
    return [true, 'Database connection OK'];
  } catch (error) {
    return [false, `Database error: ${error}`];
  }
}

/**
 * Check external API connectivity (example)
 */
async function checkExternalAPI(): Promise<[boolean, string]> {
  try {
    // Replace with your actual API health check
    return [true, 'External API OK'];
  } catch (error) {
    return [false, `External API error: ${error}`];
  }
}

/**
 * Health check endpoint handler
 * Usage: Create pages/api/health.ts and export this as default
 */
export async function healthCheck(
  req: NextApiRequest,
  res: NextApiResponse<HealthCheck>
): Promise<void> {
  const startTime = Date.now();
  
  const checks = {
    database: await checkDatabase(),
    // Add more checks as needed
    // externalAPI: await checkExternalAPI(),
  };
  
  const allHealthy = Object.values(checks).every(([status]) => status);
  
  const response: HealthCheck = {
    status: allHealthy ? 'healthy' : 'unhealthy',
    timestamp: Date.now(),
    service: process.env.SERVICE_NAME || 'clinica-system',
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    checks: Object.fromEntries(
      Object.entries(checks).map(([name, [status, message]]) => [
        name,
        {
          status: status ? 'pass' : 'fail',
          message
        }
      ])
    ),
    response_time_ms: Date.now() - startTime
  };
  
  res.status(allHealthy ? 200 : 503).json(response);
}

/**
 * Readiness check for Kubernetes
 */
export async function readyCheck(
  req: NextApiRequest,
  res: NextApiResponse
): Promise<void> {
  const [dbOk] = await checkDatabase();
  
  if (dbOk) {
    res.status(200).json({
      status: 'ready',
      timestamp: Date.now()
    });
  } else {
    res.status(503).json({
      status: 'not_ready',
      timestamp: Date.now()
    });
  }
}

/**
 * Liveness check for Kubernetes
 */
export function liveCheck(
  req: NextApiRequest,
  res: NextApiResponse
): void {
  res.status(200).json({
    status: 'alive',
    timestamp: Date.now()
  });
}

/**
 * Metrics endpoint handler
 * Usage: Create pages/api/metrics.ts and export this as default
 */
export async function metricsHandler(
  req: NextApiRequest,
  res: NextApiResponse
): Promise<void> {
  if (!register) {
    res.status(501).send('Metrics not available');
    return;
  }
  
  res.setHeader('Content-Type', register.contentType);
  res.send(await register.metrics());
}

/**
 * Middleware to track HTTP requests
 * Usage: Wrap your API routes or use in _app.tsx
 */
export function trackRequest(
  method: string,
  route: string,
  statusCode: number,
  duration: number
): void {
  if (httpRequestDuration && httpRequestTotal) {
    httpRequestDuration.labels(method, route, statusCode.toString()).observe(duration / 1000);
    httpRequestTotal.labels(method, route, statusCode.toString()).inc();
  }
}

/**
 * Business metric helpers
 */
export const metrics = {
  recordUserRegistration(tenant: string = 'default') {
    businessMetrics.userRegistrations?.labels(tenant).inc();
  },
  
  recordUserLogin(tenant: string = 'default') {
    businessMetrics.userLogins?.labels(tenant).inc();
  },
  
  setActiveUsers(count: number, tenant: string = 'default') {
    businessMetrics.activeUsers?.labels(tenant).set(count);
  },
  
  recordAppointment(status: string, tenant: string = 'default') {
    businessMetrics.appointments?.labels(tenant, status).inc();
  },
  
  recordPayment(status: string, tenant: string = 'default') {
    businessMetrics.payments?.labels(tenant, status).inc();
  },
  
  setActiveConnections(count: number) {
    activeConnections?.set(count);
  }
};

/**
 * Example: Request timing middleware for Next.js API routes
 * 
 * Usage in pages/api/[route].ts:
 * 
 * import { withMetrics } from '@/monitoring/nextjs_health';
 * 
 * async function handler(req, res) {
 *   // Your API logic
 * }
 * 
 * export default withMetrics(handler);
 */
export function withMetrics(handler: any) {
  return async (req: NextApiRequest, res: NextApiResponse) => {
    const startTime = Date.now();
    const originalJson = res.json;
    
    // Override res.json to capture status code
    res.json = function(data: any) {
      const duration = Date.now() - startTime;
      trackRequest(req.method || 'GET', req.url || '/', res.statusCode, duration);
      return originalJson.call(this, data);
    };
    
    try {
      await handler(req, res);
    } catch (error) {
      const duration = Date.now() - startTime;
      trackRequest(req.method || 'GET', req.url || '/', 500, duration);
      throw error;
    }
  };
}

/**
 * Example usage in pages/api/health.ts:
 * 
 * import { healthCheck } from '@/monitoring/nextjs_health';
 * export default healthCheck;
 */

/**
 * Example usage in pages/api/metrics.ts:
 * 
 * import { metricsHandler } from '@/monitoring/nextjs_health';
 * export default metricsHandler;
 */

/**
 * Example usage in pages/api/ready.ts:
 * 
 * import { readyCheck } from '@/monitoring/nextjs_health';
 * export default readyCheck;
 */

/**
 * Example usage in pages/api/live.ts:
 * 
 * import { liveCheck } from '@/monitoring/nextjs_health';
 * export default liveCheck;
 */
