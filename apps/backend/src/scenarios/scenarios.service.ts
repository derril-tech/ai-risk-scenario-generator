import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { CreateScenarioDto } from './dto/create-scenario.dto';
import { Scenario } from './entities/scenario.entity';

@Injectable()
export class ScenariosService {
    constructor(
        @InjectRepository(Scenario)
        private scenarioRepository: Repository<Scenario>,
    ) { }

    async create(createScenarioDto: CreateScenarioDto): Promise<Scenario> {
        const scenario = this.scenarioRepository.create({
            ...createScenarioDto,
            status: 'draft',
            createdAt: new Date(),
            updatedAt: new Date(),
        });
        return this.scenarioRepository.save(scenario);
    }

    async findAll(): Promise<Scenario[]> {
        return this.scenarioRepository.find({
            order: { createdAt: 'DESC' },
        });
    }

    async findOne(id: string): Promise<Scenario> {
        return this.scenarioRepository.findOne({ where: { id } });
    }
}
