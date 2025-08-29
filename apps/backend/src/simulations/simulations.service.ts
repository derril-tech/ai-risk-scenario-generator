import { Injectable } from '@nestjs/common';
import { RunSimulationDto } from './dto/run-simulation.dto';

@Injectable()
export class SimulationsService {
    async runSimulation(runSimulationDto: RunSimulationDto) {
        // TODO: Implement actual Monte Carlo simulation
        // For now, return mock results
        const mockResults = {
            id: `sim-${Date.now()}`,
            scenarioId: runSimulationDto.scenarioId,
            runs: runSimulationDto.runs,
            results: {
                mean: Math.random() * 1000000,
                median: Math.random() * 800000,
                p95: Math.random() * 2000000,
                p99: Math.random() * 5000000,
                standardDeviation: Math.random() * 500000,
            },
            distribution: Array.from({ length: 100 }, () => Math.random() * 1000000),
            status: 'completed',
            createdAt: new Date().toISOString(),
        };

        return mockResults;
    }

    async getSimulationsByScenario(scenarioId: string) {
        // TODO: Implement database query
        return {
            scenarioId,
            simulations: [
                {
                    id: `sim-${scenarioId}-1`,
                    runs: 10000,
                    status: 'completed',
                    createdAt: new Date().toISOString(),
                },
            ],
        };
    }
}
