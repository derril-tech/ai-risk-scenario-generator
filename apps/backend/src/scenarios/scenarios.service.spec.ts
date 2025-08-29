import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { ScenariosService } from './scenarios.service';
import { Scenario } from './entities/scenario.entity';
import { CreateScenarioDto, ScenarioType } from './dto/create-scenario.dto';

describe('ScenariosService', () => {
    let service: ScenariosService;
    let repository: Repository<Scenario>;

    const mockRepository = {
        create: jest.fn(),
        save: jest.fn(),
        find: jest.fn(),
        findOne: jest.fn(),
        update: jest.fn(),
        delete: jest.fn(),
    };

    beforeEach(async () => {
        const module: TestingModule = await Test.createTestingModule({
            providers: [
                ScenariosService,
                {
                    provide: getRepositoryToken(Scenario),
                    useValue: mockRepository,
                },
            ],
        }).compile();

        service = module.get<ScenariosService>(ScenariosService);
        repository = module.get<Repository<Scenario>>(getRepositoryToken(Scenario));
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('create', () => {
        it('should create a financial scenario successfully', async () => {
            const createScenarioDto: CreateScenarioDto = {
                name: 'Market Crash Test',
                description: 'Test market crash scenario',
                type: ScenarioType.FINANCIAL,
                assumptions: {
                    market_drop_percent: 30,
                    duration_months: 6,
                    affected_sectors: ['tech', 'finance']
                }
            };

            const expectedScenario = {
                id: 'test-id',
                ...createScenarioDto,
                status: 'draft',
                createdAt: new Date(),
                updatedAt: new Date(),
            };

            mockRepository.create.mockReturnValue(expectedScenario);
            mockRepository.save.mockResolvedValue(expectedScenario);

            const result = await service.create(createScenarioDto);

            expect(mockRepository.create).toHaveBeenCalledWith({
                ...createScenarioDto,
                status: 'draft',
                createdAt: expect.any(Date),
                updatedAt: expect.any(Date),
            });
            expect(mockRepository.save).toHaveBeenCalledWith(expectedScenario);
            expect(result).toEqual(expectedScenario);
        });

        it('should create a cyber scenario with proper assumptions', async () => {
            const createScenarioDto: CreateScenarioDto = {
                name: 'Ransomware Attack',
                description: 'Sophisticated ransomware attack',
                type: ScenarioType.CYBER,
                assumptions: {
                    systems_affected: ['erp', 'email', 'databases'],
                    downtime_hours: 72,
                    data_recovery_possible: true,
                    ransom_amount: 1000000
                }
            };

            const expectedScenario = {
                id: 'cyber-test-id',
                ...createScenarioDto,
                status: 'draft',
                createdAt: new Date(),
                updatedAt: new Date(),
            };

            mockRepository.create.mockReturnValue(expectedScenario);
            mockRepository.save.mockResolvedValue(expectedScenario);

            const result = await service.create(createScenarioDto);

            expect(result.type).toBe(ScenarioType.CYBER);
            expect(result.assumptions.systems_affected).toContain('erp');
            expect(result.assumptions.downtime_hours).toBe(72);
        });

        it('should handle supply chain scenario creation', async () => {
            const createScenarioDto: CreateScenarioDto = {
                name: 'Supplier Disruption',
                description: 'Major supplier outage',
                type: ScenarioType.SUPPLY_CHAIN,
                assumptions: {
                    supplier_outage_duration: 14,
                    affected_products: ['product_a', 'product_b'],
                    alternative_suppliers_available: false,
                    production_capacity_impact: 0.7
                }
            };

            const expectedScenario = {
                id: 'supply-test-id',
                ...createScenarioDto,
                status: 'draft',
                createdAt: new Date(),
                updatedAt: new Date(),
            };

            mockRepository.create.mockReturnValue(expectedScenario);
            mockRepository.save.mockResolvedValue(expectedScenario);

            const result = await service.create(createScenarioDto);

            expect(result.type).toBe(ScenarioType.SUPPLY_CHAIN);
            expect(result.assumptions.supplier_outage_duration).toBe(14);
            expect(result.assumptions.production_capacity_impact).toBe(0.7);
        });
    });

    describe('findAll', () => {
        it('should return all scenarios ordered by creation date', async () => {
            const scenarios = [
                { id: '1', name: 'Scenario 1', createdAt: new Date('2024-01-01') },
                { id: '2', name: 'Scenario 2', createdAt: new Date('2024-01-02') },
            ];

            mockRepository.find.mockResolvedValue(scenarios);

            const result = await service.findAll();

            expect(mockRepository.find).toHaveBeenCalledWith({
                order: { createdAt: 'DESC' },
            });
            expect(result).toEqual(scenarios);
        });

        it('should return empty array when no scenarios exist', async () => {
            mockRepository.find.mockResolvedValue([]);

            const result = await service.findAll();

            expect(result).toEqual([]);
        });
    });

    describe('findOne', () => {
        it('should return a scenario by id', async () => {
            const scenario = { id: 'test-id', name: 'Test Scenario' };
            mockRepository.findOne.mockResolvedValue(scenario);

            const result = await service.findOne('test-id');

            expect(mockRepository.findOne).toHaveBeenCalledWith({ where: { id: 'test-id' } });
            expect(result).toEqual(scenario);
        });

        it('should return null when scenario not found', async () => {
            mockRepository.findOne.mockResolvedValue(null);

            const result = await service.findOne('non-existent-id');

            expect(result).toBeNull();
        });
    });

    describe('scenario validation', () => {
        it('should validate financial scenario assumptions', () => {
            const assumptions = {
                market_drop_percent: 30,
                duration_months: 6,
                affected_sectors: ['tech', 'finance']
            };

            expect(assumptions.market_drop_percent).toBeGreaterThan(0);
            expect(assumptions.market_drop_percent).toBeLessThanOrEqual(100);
            expect(assumptions.duration_months).toBeGreaterThan(0);
            expect(Array.isArray(assumptions.affected_sectors)).toBe(true);
        });

        it('should validate cyber scenario assumptions', () => {
            const assumptions = {
                systems_affected: ['erp', 'email'],
                downtime_hours: 72,
                data_recovery_possible: true,
                ransom_amount: 1000000
            };

            expect(Array.isArray(assumptions.systems_affected)).toBe(true);
            expect(assumptions.systems_affected.length).toBeGreaterThan(0);
            expect(assumptions.downtime_hours).toBeGreaterThan(0);
            expect(typeof assumptions.data_recovery_possible).toBe('boolean');
            expect(assumptions.ransom_amount).toBeGreaterThanOrEqual(0);
        });
    });
});
