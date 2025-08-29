import { IsString, IsNumber, IsOptional, Min, Max } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class RunSimulationDto {
    @ApiProperty({ example: 'scenario-uuid' })
    @IsString()
    scenarioId: string;

    @ApiProperty({ example: 10000, description: 'Number of Monte Carlo runs' })
    @IsNumber()
    @Min(1000)
    @Max(100000)
    runs: number;

    @ApiProperty({ example: 42, description: 'Random seed for reproducibility' })
    @IsNumber()
    @IsOptional()
    seed?: number;
}
