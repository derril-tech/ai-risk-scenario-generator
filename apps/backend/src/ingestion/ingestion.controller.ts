import { Controller, Post, Get, Body, UseGuards, UseInterceptors, UploadedFile } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiConsumes } from '@nestjs/swagger';
import { IngestionService } from './ingestion.service';
import { ConnectDataSourceDto } from './dto/connect-data-source.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('Data Ingestion')
@Controller('ingestion')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class IngestionController {
    constructor(private readonly ingestionService: IngestionService) { }

    @Post('connect')
    @ApiOperation({ summary: 'Connect to external data source' })
    connectDataSource(@Body() connectDataSourceDto: ConnectDataSourceDto) {
        return this.ingestionService.connectDataSource(connectDataSourceDto);
    }

    @Post('upload')
    @UseInterceptors(FileInterceptor('file'))
    @ApiConsumes('multipart/form-data')
    @ApiOperation({ summary: 'Upload CSV/Excel file for ingestion' })
    uploadFile(@UploadedFile() file: Express.Multer.File) {
        return this.ingestionService.processUploadedFile(file);
    }

    @Get('sources')
    @ApiOperation({ summary: 'Get connected data sources' })
    getDataSources() {
        return this.ingestionService.getDataSources();
    }
}
