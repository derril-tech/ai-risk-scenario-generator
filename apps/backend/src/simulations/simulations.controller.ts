import { Controller, Post, Get, Param, Body, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { SimulationsService } from './simulations.service';
import { RunSimulationDto } from './dto/run-simulation.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('Simulations')
@Controller('simulations')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class SimulationsController {
    constructor(private readonly simulationsService: SimulationsService) { }

    @Post('run')
    @ApiOperation({ summary: 'Run a Monte Carlo simulation' })
    runSimulation(@Body() runSimulationDto: RunSimulationDto) {
        return this.simulationsService.runSimulation(runSimulationDto);
    }

    @Get('scenario/:scenarioId')
    @ApiOperation({ summary: 'Get simulations for a scenario' })
    getSimulationsByScenario(@Param('scenarioId') scenarioId: string) {
        return this.simulationsService.getSimulationsByScenario(scenarioId);
    }
}
