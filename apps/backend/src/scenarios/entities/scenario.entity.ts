import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity('scenarios')
export class Scenario {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column()
    name: string;

    @Column({ nullable: true })
    description: string;

    @Column({
        type: 'enum',
        enum: ['financial', 'supply_chain', 'cyber', 'operational'],
    })
    type: string;

    @Column({
        type: 'enum',
        enum: ['draft', 'active', 'completed', 'archived'],
        default: 'draft',
    })
    status: string;

    @Column('jsonb', { nullable: true })
    assumptions: Record<string, any>;

    @Column('jsonb', { nullable: true })
    narrative: Record<string, any>;

    @CreateDateColumn()
    createdAt: Date;

    @UpdateDateColumn()
    updatedAt: Date;
}
