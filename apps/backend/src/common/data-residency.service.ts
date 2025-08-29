import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

export interface DataResidencyRule {
    orgId: string;
    region: string;
    dataTypes: string[];
    restrictions: {
        allowedRegions: string[];
        prohibitedRegions: string[];
        requiresEncryption: boolean;
        retentionPeriodDays: number;
    };
}

export interface DataClassification {
    level: 'public' | 'internal' | 'confidential' | 'restricted';
    categories: string[];
    personalData: boolean;
    financialData: boolean;
    healthData: boolean;
}

@Injectable()
export class DataResidencyService {
    private residencyRules: Map<string, DataResidencyRule> = new Map();

    constructor(private configService: ConfigService) {
        this.initializeDefaultRules();
    }

    /**
     * Initialize default data residency rules
     */
    private initializeDefaultRules(): void {
        // EU/GDPR Rules
        this.residencyRules.set('EU', {
            orgId: '*',
            region: 'EU',
            dataTypes: ['personal', 'financial', 'health'],
            restrictions: {
                allowedRegions: ['EU', 'EEA'],
                prohibitedRegions: ['US', 'CN', 'RU'],
                requiresEncryption: true,
                retentionPeriodDays: 2555 // 7 years
            }
        });

        // US Rules
        this.residencyRules.set('US', {
            orgId: '*',
            region: 'US',
            dataTypes: ['financial', 'health'],
            restrictions: {
                allowedRegions: ['US', 'CA'],
                prohibitedRegions: ['CN', 'RU', 'IR'],
                requiresEncryption: true,
                retentionPeriodDays: 2555
            }
        });

        // Financial Services Rules (SOX, Basel)
        this.residencyRules.set('FINANCIAL', {
            orgId: '*',
            region: 'GLOBAL',
            dataTypes: ['financial', 'trading', 'risk'],
            restrictions: {
                allowedRegions: ['US', 'EU', 'UK', 'CA', 'AU', 'SG'],
                prohibitedRegions: ['CN', 'RU', 'IR', 'KP'],
                requiresEncryption: true,
                retentionPeriodDays: 2555
            }
        });
    }

    /**
     * Register organization-specific residency rules
     */
    async registerOrgRules(orgId: string, rules: DataResidencyRule): Promise<void> {
        this.residencyRules.set(`ORG_${orgId}`, rules);
        console.log(`Data residency rules registered for org: ${orgId}`);
    }

    /**
     * Check if data operation is allowed
     */
    async validateDataOperation(
        orgId: string,
        dataType: string,
        operation: 'store' | 'process' | 'transfer',
        targetRegion: string,
        classification: DataClassification
    ): Promise<{
        allowed: boolean;
        reason?: string;
        requirements: string[];
    }> {
        try {
            const applicableRules = this.getApplicableRules(orgId, dataType, classification);

            for (const rule of applicableRules) {
                // Check region restrictions
                if (rule.restrictions.prohibitedRegions.includes(targetRegion)) {
                    return {
                        allowed: false,
                        reason: `Data transfer to ${targetRegion} is prohibited by ${rule.region} regulations`,
                        requirements: []
                    };
                }

                if (rule.restrictions.allowedRegions.length > 0 &&
                    !rule.restrictions.allowedRegions.includes(targetRegion)) {
                    return {
                        allowed: false,
                        reason: `Data transfer to ${targetRegion} is not in allowed regions: ${rule.restrictions.allowedRegions.join(', ')}`,
                        requirements: []
                    };
                }
            }

            // Determine requirements
            const requirements: string[] = [];

            for (const rule of applicableRules) {
                if (rule.restrictions.requiresEncryption) {
                    requirements.push('Data must be encrypted at rest and in transit');
                }

                if (classification.personalData) {
                    requirements.push('Personal data processing requires explicit consent');
                }

                if (classification.level === 'restricted') {
                    requirements.push('Restricted data requires additional access controls');
                }
            }

            return {
                allowed: true,
                requirements: [...new Set(requirements)] // Remove duplicates
            };

        } catch (error) {
            console.error('Data residency validation failed:', error);
            return {
                allowed: false,
                reason: 'Data residency validation failed',
                requirements: []
            };
        }
    }

    /**
     * Get applicable rules for data operation
     */
    private getApplicableRules(
        orgId: string,
        dataType: string,
        classification: DataClassification
    ): DataResidencyRule[] {
        const rules: DataResidencyRule[] = [];

        // Check org-specific rules first
        const orgRule = this.residencyRules.get(`ORG_${orgId}`);
        if (orgRule && orgRule.dataTypes.includes(dataType)) {
            rules.push(orgRule);
        }

        // Check global rules
        for (const [key, rule] of this.residencyRules.entries()) {
            if (key.startsWith('ORG_')) continue; // Skip org-specific rules

            if (rule.dataTypes.includes(dataType) ||
                this.matchesClassification(rule, classification)) {
                rules.push(rule);
            }
        }

        return rules;
    }

    /**
     * Check if rule matches data classification
     */
    private matchesClassification(rule: DataResidencyRule, classification: DataClassification): boolean {
        // Financial data rules
        if (classification.financialData && rule.dataTypes.includes('financial')) {
            return true;
        }

        // Personal data rules (GDPR, etc.)
        if (classification.personalData && rule.dataTypes.includes('personal')) {
            return true;
        }

        // Health data rules (HIPAA, etc.)
        if (classification.healthData && rule.dataTypes.includes('health')) {
            return true;
        }

        return false;
    }

    /**
     * Classify data based on content
     */
    classifyData(data: Record<string, any>): DataClassification {
        let level: DataClassification['level'] = 'internal';
        const categories: string[] = [];
        let personalData = false;
        let financialData = false;
        let healthData = false;

        // Check for personal identifiers
        const personalFields = ['email', 'phone', 'ssn', 'passport', 'name', 'address'];
        for (const field of personalFields) {
            if (this.hasField(data, field)) {
                personalData = true;
                categories.push('personal');
                level = 'confidential';
                break;
            }
        }

        // Check for financial data
        const financialFields = ['account', 'balance', 'transaction', 'payment', 'credit', 'portfolio'];
        for (const field of financialFields) {
            if (this.hasField(data, field)) {
                financialData = true;
                categories.push('financial');
                level = 'confidential';
                break;
            }
        }

        // Check for health data
        const healthFields = ['medical', 'diagnosis', 'treatment', 'prescription', 'health'];
        for (const field of healthFields) {
            if (this.hasField(data, field)) {
                healthData = true;
                categories.push('health');
                level = 'restricted';
                break;
            }
        }

        // Check for risk/security data
        const riskFields = ['vulnerability', 'threat', 'incident', 'breach', 'attack'];
        for (const field of riskFields) {
            if (this.hasField(data, field)) {
                categories.push('security');
                if (level === 'internal') level = 'confidential';
                break;
            }
        }

        return {
            level,
            categories,
            personalData,
            financialData,
            healthData
        };
    }

    /**
     * Check if data contains field (case-insensitive, nested)
     */
    private hasField(data: any, field: string): boolean {
        if (typeof data !== 'object' || data === null) return false;

        const lowerField = field.toLowerCase();

        for (const [key, value] of Object.entries(data)) {
            if (key.toLowerCase().includes(lowerField)) {
                return true;
            }

            if (typeof value === 'object' && value !== null) {
                if (this.hasField(value, field)) {
                    return true;
                }
            }
        }

        return false;
    }

    /**
     * Get data retention period
     */
    getRetentionPeriod(orgId: string, dataType: string): number {
        const rules = this.getApplicableRules(orgId, dataType, {
            level: 'internal',
            categories: [dataType],
            personalData: false,
            financialData: false,
            healthData: false
        });

        if (rules.length === 0) {
            return 2555; // Default 7 years
        }

        // Return the most restrictive (shortest) retention period
        return Math.min(...rules.map(rule => rule.restrictions.retentionPeriodDays));
    }

    /**
     * Generate data residency compliance report
     */
    async generateComplianceReport(orgId: string): Promise<{
        orgId: string;
        applicableRules: string[];
        dataTypes: string[];
        complianceStatus: 'compliant' | 'non_compliant' | 'unknown';
        violations: string[];
        recommendations: string[];
    }> {
        const orgRule = this.residencyRules.get(`ORG_${orgId}`);
        const applicableRules = Array.from(this.residencyRules.keys())
            .filter(key => !key.startsWith('ORG_') || key === `ORG_${orgId}`);

        return {
            orgId,
            applicableRules,
            dataTypes: orgRule?.dataTypes || ['financial', 'personal', 'operational'],
            complianceStatus: 'compliant',
            violations: [],
            recommendations: [
                'Implement data encryption at rest and in transit',
                'Regular compliance audits and monitoring',
                'Staff training on data residency requirements',
                'Automated data classification and handling'
            ]
        };
    }
}
