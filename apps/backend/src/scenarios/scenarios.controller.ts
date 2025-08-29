import { Controller, Get, Post, Body, Param, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { ScenariosService } from './scenarios.service';
import { CreateScenarioDto } from './dto/create-scenario.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('Scenarios')
@Controller('scenarios')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class ScenariosController {
    constructor(private readonly scenariosService: ScenariosService) { }

    @Post()
    @ApiOperation({ summary: 'Create a new risk scenario' })
    create(@Body() createScenarioDto: CreateScenarioDto) {
        return this.scenariosService.create(createScenarioDto);
    }

    @Get()
    @ApiOperation({ summary: 'Get all scenarios' })
    findAll() {
        return this.scenariosService.findAll();
    }

    @Get(':id')
    @ApiOperation({ summary: 'Get scenario by ID' })
    findOne(@Param('id') id: string) {
        return this.scenariosService.findOne(id);
    }
}
