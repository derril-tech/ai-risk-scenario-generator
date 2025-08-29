import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CacheModule } from '@nestjs/cache-manager';
import { ThrottlerModule } from '@nestjs/throttler';
import { EventEmitterModule } from '@nestjs/event-emitter';
import * as redisStore from 'cache-manager-redis-store';

import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AuthModule } from './auth/auth.module';
import { ScenariosModule } from './scenarios/scenarios.module';
import { SimulationsModule } from './simulations/simulations.module';
import { ReportsModule } from './reports/reports.module';
import { IngestionModule } from './ingestion/ingestion.module';

@Module({
    imports: [
        // Configuration
        ConfigModule.forRoot({
            isGlobal: true,
            envFilePath: '.env',
        }),

        // Database
        TypeOrmModule.forRootAsync({
            imports: [ConfigModule],
            useFactory: (configService: ConfigService) => ({
                type: 'postgres',
                url: configService.get('DATABASE_URL'),
                autoLoadEntities: true,
                synchronize: process.env.NODE_ENV !== 'production',
                logging: process.env.NODE_ENV === 'development',
            }),
            inject: [ConfigService],
        }),

        // Cache (Redis)
        CacheModule.registerAsync({
            imports: [ConfigModule],
            useFactory: async (configService: ConfigService) => ({
                store: redisStore,
                url: configService.get('REDIS_URL'),
                ttl: 300, // 5 minutes default
            }),
            inject: [ConfigService],
            isGlobal: true,
        }),

        // Rate limiting
        ThrottlerModule.forRoot([
            {
                ttl: 60000, // 1 minute
                limit: 100, // 100 requests per minute
            },
        ]),

        // Event emitter
        EventEmitterModule.forRoot(),

        // Feature modules
        AuthModule,
        ScenariosModule,
        SimulationsModule,
        ReportsModule,
        IngestionModule,
    ],
    controllers: [AppController],
    providers: [AppService],
})
export class AppModule { }
