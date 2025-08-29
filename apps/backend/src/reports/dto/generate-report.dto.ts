import { IsString, IsEnum, IsArray, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export enum ReportFormat {
    PDF = 'pdf',
    JSON = 'json',
    CSV = 'csv',
}

export enum ReportSection {
    EXECUTIVE_SUMMARY = 'executive_summary',
    SCENARIO_DETAILS = 'scenario_details',
    SIMULATION_RESULTS = 'simulation_results',
    RISK_MATRIX = 'risk_matrix',
    MITIGATION_STRATEGIES = 'mitigation_strategies',
    APPENDICES = 'appendices',
}

export class GenerateReportDto {
    @ApiProperty({ example: 'scenario-uuid' })
    @IsString()
    scenarioId: string;

    @ApiProperty({ enum: ReportFormat, example: ReportFormat.PDF })
    @IsEnum(ReportFormat)
    format: ReportFormat;

    @ApiProperty({
        enum: ReportSection,
        isArray: true,
        example: [ReportSection.EXECUTIVE_SUMMARY, ReportSection.SIMULATION_RESULTS]
    })
    @IsArray()
    @IsEnum(ReportSection, { each: true })
    sections: ReportSection[];

    @ApiProperty({ example: 'Executive Risk Assessment Q4 2024' })
    @IsString()
    @IsOptional()
    title?: string;
}
