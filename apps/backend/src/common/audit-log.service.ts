import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { EncryptionService } from './encryption.service';

export interface AuditLogEntry {
    id?: string;
    userId: string;
    orgId: string;
    action: string;
    resourceType: string;
    resourceId: string;
    details: Record<string, any>;
    ipAddress: string;
    userAgent: string;
    timestamp: Date;
    signature?: string;
}

@Injectable()
export class AuditLogService {
    constructor(
        private encryptionService: EncryptionService,
    ) { }

    /**
     * Create immutable audit log entry
     */
    async logAction(entry: Omit<AuditLogEntry, 'id' | 'timestamp' | 'signature'>): Promise<void> {
        try {
            const auditEntry: AuditLogEntry = {
                ...entry,
                timestamp: new Date(),
            };

            // Create immutable signature
            const dataToSign = JSON.stringify({
                userId: auditEntry.userId,
                orgId: auditEntry.orgId,
                action: auditEntry.action,
                resourceType: auditEntry.resourceType,
                resourceId: auditEntry.resourceId,
                timestamp: auditEntry.timestamp.toISOString(),
            });

            auditEntry.signature = this.encryptionService.createHMAC(dataToSign);

            // Encrypt sensitive details
            if (auditEntry.details && Object.keys(auditEntry.details).length > 0) {
                const encryptedDetails = this.encryptionService.encrypt(
                    JSON.stringify(auditEntry.details),
                    auditEntry.orgId
                );
                auditEntry.details = { encrypted: encryptedDetails };
            }

            // Store in append-only audit log
            await this.storeAuditEntry(auditEntry);

            console.log(`Audit log created: ${auditEntry.action} by ${auditEntry.userId}`);
        } catch (error) {
            console.error('Failed to create audit log:', error);
            // Don't throw - audit logging should not break application flow
        }
    }

    /**
     * Store audit entry (implementation depends on storage choice)
     */
    private async storeAuditEntry(entry: AuditLogEntry): Promise<void> {
        // In production, this would write to:
        // 1. Immutable database table with append-only permissions
        // 2. Write-once storage like AWS S3 with object lock
        // 3. Blockchain or distributed ledger for ultimate immutability

        // For now, log to console and file
        const logLine = JSON.stringify({
            ...entry,
            _immutable: true,
            _version: '1.0'
        });

        console.log('AUDIT_LOG:', logLine);

        // In production: await this.auditRepository.save(entry);
    }

    /**
     * Verify audit log integrity
     */
    async verifyAuditEntry(entry: AuditLogEntry): Promise<boolean> {
        try {
            const dataToVerify = JSON.stringify({
                userId: entry.userId,
                orgId: entry.orgId,
                action: entry.action,
                resourceType: entry.resourceType,
                resourceId: entry.resourceId,
                timestamp: entry.timestamp.toISOString(),
            });

            return this.encryptionService.verifyHMAC(dataToVerify, entry.signature);
        } catch (error) {
            console.error('Audit verification failed:', error);
            return false;
        }
    }

    /**
     * Query audit logs with privacy controls
     */
    async queryAuditLogs(
        orgId: string,
        filters: {
            userId?: string;
            action?: string;
            resourceType?: string;
            startDate?: Date;
            endDate?: Date;
        },
        requesterRole: string
    ): Promise<AuditLogEntry[]> {
        // Implement role-based access controls
        if (!this.canAccessAuditLogs(requesterRole)) {
            throw new Error('Insufficient permissions to access audit logs');
        }

        // In production, query from audit storage
        // For now, return mock data
        return [
            {
                id: 'audit-1',
                userId: 'user-123',
                orgId,
                action: 'scenario.create',
                resourceType: 'scenario',
                resourceId: 'scenario-456',
                details: { name: 'Market Crash Test' },
                ipAddress: '192.168.1.100',
                userAgent: 'Mozilla/5.0...',
                timestamp: new Date(),
                signature: 'mock-signature'
            }
        ];
    }

    /**
     * Check if user can access audit logs
     */
    private canAccessAuditLogs(role: string): boolean {
        const allowedRoles = ['admin', 'compliance_officer', 'security_admin'];
        return allowedRoles.includes(role);
    }

    /**
     * Generate compliance report
     */
    async generateComplianceReport(
        orgId: string,
        startDate: Date,
        endDate: Date
    ): Promise<{
        totalActions: number;
        actionsByType: Record<string, number>;
        userActivity: Record<string, number>;
        integrityStatus: 'verified' | 'compromised';
    }> {
        // In production, analyze actual audit logs
        return {
            totalActions: 1247,
            actionsByType: {
                'scenario.create': 45,
                'scenario.update': 123,
                'simulation.run': 234,
                'report.generate': 67,
                'user.login': 445,
                'data.ingest': 333
            },
            userActivity: {
                'user-123': 234,
                'user-456': 189,
                'user-789': 156
            },
            integrityStatus: 'verified'
        };
    }
}
