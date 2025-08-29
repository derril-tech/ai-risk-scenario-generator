import { IsEmail, IsString, MinLength, IsOptional } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class RegisterDto {
    @ApiProperty({ example: 'user@example.com' })
    @IsEmail()
    email: string;

    @ApiProperty({ example: 'password123' })
    @IsString()
    @MinLength(8)
    password: string;

    @ApiProperty({ example: 'John Doe' })
    @IsString()
    name: string;

    @ApiProperty({ example: 'company.com' })
    @IsString()
    @IsOptional()
    organizationDomain?: string;
}
