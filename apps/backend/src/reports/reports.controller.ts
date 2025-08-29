import { Controller, Post, Get, Param, Body, UseGuards, Res } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { Response } from 'express';
import { ReportsService } from './reports.service';
import { GenerateReportDto } from './dto/generate-report.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('Reports')
@Controller('reports')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class ReportsController {
    constructor(private readonly reportsService: ReportsService) { }

    @Post('generate')
    @ApiOperation({ summary: 'Generate a risk assessment report' })
    generateReport(@Body() generateReportDto: GenerateReportDto) {
        return this.reportsService.generateReport(generateReportDto);
    }

    @Get(':id/download')
    @ApiOperation({ summary: 'Download report as PDF' })
    async downloadReport(@Param('id') id: string, @Res() res: Response) {
        const report = await this.reportsService.getReportFile(id);
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `attachment; filename="risk-report-${id}.pdf"`);
        return res.send(report);
    }
}
