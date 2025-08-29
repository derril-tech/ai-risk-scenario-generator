import { IsString, IsEnum, IsObject, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export enum DataSourceType {
    SAP = 'sap',
    ORACLE = 'oracle',
    NETSUITE = 'netsuite',
    COUPA = 'coupa',
    SIEM = 'siem',
    EDR = 'edr',
    CSV_UPLOAD = 'csv_upload',
    API = 'api',
}

export class ConnectDataSourceDto {
    @ApiProperty({ example: 'SAP Production Environment' })
    @IsString()
    name: string;

    @ApiProperty({ enum: DataSourceType, example: DataSourceType.SAP })
    @IsEnum(DataSourceType)
    type: DataSourceType;

    @ApiProperty({
        example: {
            host: 'sap.company.com',
            username: 'api_user',
            database: 'PROD'
        }
    })
    @IsObject()
    @IsOptional()
    connectionConfig?: Record<string, any>;
}
