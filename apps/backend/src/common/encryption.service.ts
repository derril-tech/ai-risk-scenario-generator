import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as crypto from 'crypto';
import * as bcrypt from 'bcrypt';

@Injectable()
export class EncryptionService {
    private readonly algorithm = 'aes-256-gcm';
    private readonly keyLength = 32;
    private readonly ivLength = 16;
    private readonly tagLength = 16;
    private readonly saltRounds = 12;

    constructor(private configService: ConfigService) { }

    /**
     * Generate encryption key from master key and salt
     */
    private deriveKey(salt: Buffer): Buffer {
        const masterKey = this.configService.get<string>('ENCRYPTION_MASTER_KEY');
        if (!masterKey) {
            throw new Error('ENCRYPTION_MASTER_KEY not configured');
        }
        return crypto.pbkdf2Sync(masterKey, salt, 100000, this.keyLength, 'sha256');
    }

    /**
     * Encrypt sensitive data with AES-256-GCM
     */
    encrypt(plaintext: string, orgId?: string): string {
        try {
            const salt = crypto.randomBytes(16);
            const iv = crypto.randomBytes(this.ivLength);
            const key = this.deriveKey(salt);

            const cipher = crypto.createCipher(this.algorithm, key);
            cipher.setAAD(Buffer.from(orgId || 'global', 'utf8'));

            let encrypted = cipher.update(plaintext, 'utf8', 'hex');
            encrypted += cipher.final('hex');

            const tag = cipher.getAuthTag();

            // Combine salt, iv, tag, and encrypted data
            const combined = Buffer.concat([
                salt,
                iv,
                tag,
                Buffer.from(encrypted, 'hex')
            ]);

            return combined.toString('base64');
        } catch (error) {
            throw new Error(`Encryption failed: ${error.message}`);
        }
    }

    /**
     * Decrypt sensitive data
     */
    decrypt(encryptedData: string, orgId?: string): string {
        try {
            const combined = Buffer.from(encryptedData, 'base64');

            const salt = combined.subarray(0, 16);
            const iv = combined.subarray(16, 16 + this.ivLength);
            const tag = combined.subarray(16 + this.ivLength, 16 + this.ivLength + this.tagLength);
            const encrypted = combined.subarray(16 + this.ivLength + this.tagLength);

            const key = this.deriveKey(salt);

            const decipher = crypto.createDecipher(this.algorithm, key);
            decipher.setAAD(Buffer.from(orgId || 'global', 'utf8'));
            decipher.setAuthTag(tag);

            let decrypted = decipher.update(encrypted, null, 'utf8');
            decrypted += decipher.final('utf8');

            return decrypted;
        } catch (error) {
            throw new Error(`Decryption failed: ${error.message}`);
        }
    }

    /**
     * Hash password with bcrypt
     */
    async hashPassword(password: string): Promise<string> {
        return bcrypt.hash(password, this.saltRounds);
    }

    /**
     * Verify password against hash
     */
    async verifyPassword(password: string, hash: string): Promise<boolean> {
        return bcrypt.compare(password, hash);
    }

    /**
     * Generate secure random token
     */
    generateToken(length: number = 32): string {
        return crypto.randomBytes(length).toString('hex');
    }

    /**
     * Hash data for integrity verification
     */
    hash(data: string): string {
        return crypto.createHash('sha256').update(data).digest('hex');
    }

    /**
     * Create HMAC for data integrity
     */
    createHMAC(data: string, secret?: string): string {
        const hmacSecret = secret || this.configService.get<string>('HMAC_SECRET');
        if (!hmacSecret) {
            throw new Error('HMAC_SECRET not configured');
        }
        return crypto.createHmac('sha256', hmacSecret).update(data).digest('hex');
    }

    /**
     * Verify HMAC
     */
    verifyHMAC(data: string, signature: string, secret?: string): boolean {
        const expectedSignature = this.createHMAC(data, secret);
        return crypto.timingSafeEqual(
            Buffer.from(signature, 'hex'),
            Buffer.from(expectedSignature, 'hex')
        );
    }
}
