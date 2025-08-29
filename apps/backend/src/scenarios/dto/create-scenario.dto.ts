import { IsString, IsEnum, IsOptional, IsObject } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export enum ScenarioType {
    FINANCIAL = 'financial',
    SUPPLY_CHAIN = 'supply_chain',
    CYBER = 'cyber',
    OPERATIONAL = 'operational',
}

export class CreateScenarioDto {
    @ApiProperty({ example: 'Market Crash Scenario' })
    @IsString()
    name: string;

    @ApiProperty({ example: 'A severe market downturn affecting portfolio values' })
    @IsString()
    @IsOptional()
    description?: string;

    @ApiProperty({ enum: ScenarioType, example: ScenarioType.FINANCIAL })
    @IsEnum(ScenarioType)
    type: ScenarioType;

    @ApiProperty({
        example: {
            marketDrop: 30,
            duration: 6,
            sectors: ['tech', 'finance']
        }
    })
    @IsObject()
    @IsOptional()
    assumptions?: Record<string, any>;
}
