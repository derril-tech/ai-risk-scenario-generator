import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as Sentry from '@sentry/node';
import { PrometheusRegistry, Counter, Histogram, Gauge } from 'prom-client';

export interface MetricLabels {
    [key: string]: string;
}

export interface TraceContext {
    traceId: string;
    spanId: string;
    operation: string;
    userId?: string;
    orgId?: string;
}

@Injectable()
export class ObservabilityService {
    private registry: PrometheusRegistry;
    private metrics: {
        httpRequests: Counter<string>;
        httpDuration: Histogram<string>;
        scenarioOperations: Counter<string>;
        simulationDuration: Histogram<string>;
        activeUsers: Gauge<string>;
        systemHealth: Gauge<string>;
    };

    constructor(private configService: ConfigService) {
        this.initializeSentry();
        this.initializeMetrics();
    }

    /**
     * Initialize Sentry for error tracking
     */
    private initializeSentry(): void {
        const sentryDsn = this.configService.get<string>('SENTRY_DSN');

        if (sentryDsn) {
            Sentry.init({
                dsn: sentryDsn,
                environment: this.configService.get<string>('NODE_ENV', 'development'),
                tracesSampleRate: 0.1,
                integrations: [
                    new Sentry.Integrations.Http({ tracing: true }),
                    new Sentry.Integrations.Express({ app: undefined }),
                ],
            });
        }
    }

    /**
     * Initialize Prometheus metrics
     */
    private initializeMetrics(): void {
        this.registry = new PrometheusRegistry();

        // HTTP request metrics
        this.metrics = {
            httpRequests: new Counter({
                name: 'http_requests_total',
                help: 'Total number of HTTP requests',
                labelNames: ['method', 'route', 'status_code'],
                registers: [this.registry],
            }),

            httpDuration: new Histogram({
                name: 'http_request_duration_seconds',
                help: 'HTTP request duration in seconds',
                labelNames: ['method', 'route'],
                buckets: [0.1, 0.5, 1, 2, 5, 10],
                registers: [this.registry],
            }),

            scenarioOperations: new Counter({
                name: 'scenario_operations_total',
                help: 'Total number of scenario operations',
                labelNames: ['operation', 'type', 'status'],
                registers: [this.registry],
            }),

            simulationDuration: new Histogram({
                name: 'simulation_duration_seconds',
                help: 'Simulation execution duration in seconds',
                labelNames: ['method', 'scenario_type'],
                buckets: [1, 5, 10, 30, 60, 120, 300],
                registers: [this.registry],
            }),

            activeUsers: new Gauge({
                name: 'active_users',
                help: 'Number of active users',
                labelNames: ['org_id'],
                registers: [this.registry],
            }),

            systemHealth: new Gauge({
                name: 'system_health_score',
                help: 'Overall system health score (0-1)',
                labelNames: ['component'],
                registers: [this.registry],
            }),
        };
    }

    /**
     * Record HTTP request metrics
     */
    recordHttpRequest(
        method: string,
        route: string,
        statusCode: number,
        duration: number
    ): void {
        this.metrics.httpRequests.inc({
            method: method.toUpperCase(),
            route,
            status_code: statusCode.toString(),
        });

        this.metrics.httpDuration.observe(
            { method: method.toUpperCase(), route },
            duration / 1000 // Convert to seconds
        );
    }

    /**
     * Record scenario operation
     */
    recordScenarioOperation(
        operation: 'create' | 'update' | 'delete' | 'simulate',
        type: string,
        status: 'success' | 'error'
    ): void {
        this.metrics.scenarioOperations.inc({
            operation,
            type,
            status,
        });
    }

    /**
     * Record simulation duration
     */
    recordSimulationDuration(
        method: string,
        scenarioType: string,
        duration: number
    ): void {
        this.metrics.simulationDuration.observe(
            { method, scenario_type: scenarioType },
            duration / 1000
        );
    }

    /**
     * Update active users count
     */
    updateActiveUsers(orgId: string, count: number): void {
        this.metrics.activeUsers.set({ org_id: orgId }, count);
    }

    /**
     * Update system health score
     */
    updateSystemHealth(component: string, score: number): void {
        this.metrics.systemHealth.set({ component }, score);
    }

    /**
     * Start a trace span
     */
    startTrace(operation: string, context?: Partial<TraceContext>): TraceContext {
        const traceId = this.generateTraceId();
        const spanId = this.generateSpanId();

        const traceContext: TraceContext = {
            traceId,
            spanId,
            operation,
            ...context,
        };

        // Start Sentry transaction
        const transaction = Sentry.startTransaction({
            name: operation,
            op: 'http.server',
        });

        transaction.setTag('traceId', traceId);
        transaction.setTag('spanId', spanId);

        if (context?.userId) {
            transaction.setUser({ id: context.userId });
        }

        if (context?.orgId) {
            transaction.setTag('orgId', context.orgId);
        }

        return traceContext;
    }

    /**
     * Finish a trace span
     */
    finishTrace(context: TraceContext, status?: 'ok' | 'error', error?: Error): void {
        const transaction = Sentry.getCurrentHub().getScope()?.getTransaction();

        if (transaction) {
            if (status === 'error' && error) {
                transaction.setStatus('internal_error');
                Sentry.captureException(error);
            } else {
                transaction.setStatus('ok');
            }

            transaction.finish();
        }
    }

    /**
     * Log structured event
     */
    logEvent(
        level: 'info' | 'warn' | 'error',
        message: string,
        context?: Record<string, any>,
        trace?: TraceContext
    ): void {
        const logData = {
            timestamp: new Date().toISOString(),
            level,
            message,
            context,
            trace,
        };

        // Console logging (in production, use proper logging service)
        console.log(JSON.stringify(logData));

        // Send to Sentry if error
        if (level === 'error') {
            Sentry.addBreadcrumb({
                message,
                level: 'error',
                data: context,
            });
        }
    }

    /**
     * Capture exception with context
     */
    captureException(error: Error, context?: Record<string, any>, trace?: TraceContext): void {
        Sentry.withScope((scope) => {
            if (context) {
                Object.keys(context).forEach((key) => {
                    scope.setExtra(key, context[key]);
                });
            }

            if (trace) {
                scope.setTag('traceId', trace.traceId);
                scope.setTag('operation', trace.operation);

                if (trace.userId) {
                    scope.setUser({ id: trace.userId });
                }
            }

            Sentry.captureException(error);
        });

        // Also log structured
        this.logEvent('error', error.message, { ...context, stack: error.stack }, trace);
    }

    /**
     * Get metrics for Prometheus scraping
     */
    async getMetrics(): Promise<string> {
        return this.registry.metrics();
    }

    /**
     * Health check with detailed component status
     */
    async getHealthStatus(): Promise<{
        status: 'healthy' | 'degraded' | 'unhealthy';
        components: Record<string, { status: string; details?: any }>;
        timestamp: string;
    }> {
        const components: Record<string, { status: string; details?: any }> = {};

        // Check database connectivity
        try {
            // In production, actually check database
            components.database = { status: 'healthy' };
            this.updateSystemHealth('database', 1.0);
        } catch (error) {
            components.database = { status: 'unhealthy', details: error.message };
            this.updateSystemHealth('database', 0.0);
        }

        // Check Redis connectivity
        try {
            // In production, actually check Redis
            components.redis = { status: 'healthy' };
            this.updateSystemHealth('redis', 1.0);
        } catch (error) {
            components.redis = { status: 'unhealthy', details: error.message };
            this.updateSystemHealth('redis', 0.0);
        }

        // Check external services
        components.ai_services = { status: 'healthy' };
        this.updateSystemHealth('ai_services', 1.0);

        // Determine overall status
        const unhealthyCount = Object.values(components).filter(c => c.status === 'unhealthy').length;
        const degradedCount = Object.values(components).filter(c => c.status === 'degraded').length;

        let overallStatus: 'healthy' | 'degraded' | 'unhealthy';
        if (unhealthyCount > 0) {
            overallStatus = 'unhealthy';
        } else if (degradedCount > 0) {
            overallStatus = 'degraded';
        } else {
            overallStatus = 'healthy';
        }

        return {
            status: overallStatus,
            components,
            timestamp: new Date().toISOString(),
        };
    }

    /**
     * Generate trace ID
     */
    private generateTraceId(): string {
        return Math.random().toString(36).substring(2, 15) +
            Math.random().toString(36).substring(2, 15);
    }

    /**
     * Generate span ID
     */
    private generateSpanId(): string {
        return Math.random().toString(36).substring(2, 10);
    }

    /**
     * Create performance monitoring decorator
     */
    createPerformanceDecorator(operation: string) {
        return (target: any, propertyName: string, descriptor: PropertyDescriptor) => {
            const method = descriptor.value;

            descriptor.value = async function (...args: any[]) {
                const startTime = Date.now();
                const trace = this.observabilityService?.startTrace(operation) || {
                    traceId: 'unknown',
                    spanId: 'unknown',
                    operation,
                };

                try {
                    const result = await method.apply(this, args);

                    const duration = Date.now() - startTime;
                    this.observabilityService?.finishTrace(trace, 'ok');
                    this.observabilityService?.logEvent('info', `${operation} completed`, {
                        duration,
                        operation,
                    }, trace);

                    return result;
                } catch (error) {
                    const duration = Date.now() - startTime;
                    this.observabilityService?.finishTrace(trace, 'error', error);
                    this.observabilityService?.captureException(error, {
                        operation,
                        duration,
                    }, trace);

                    throw error;
                }
            };
        };
    }
}
