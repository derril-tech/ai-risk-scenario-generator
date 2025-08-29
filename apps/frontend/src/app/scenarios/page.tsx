import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Plus, TrendingUp, Shield, Zap, AlertTriangle } from 'lucide-react'
import Link from 'next/link'

export default function ScenariosPage() {
    const scenarios = [
        {
            id: 'scenario-1',
            name: 'Market Crash Scenario',
            type: 'financial',
            status: 'active',
            risk_level: 'high',
            created_at: '2024-01-15',
            description: 'Severe market downturn affecting portfolio values',
            impact_estimate: '$2.5M',
            likelihood: '15%'
        },
        {
            id: 'scenario-2',
            name: 'Cyber Attack - Ransomware',
            type: 'cyber',
            status: 'completed',
            risk_level: 'critical',
            created_at: '2024-01-10',
            description: 'Ransomware attack encrypting critical systems',
            impact_estimate: '$4.2M',
            likelihood: '25%'
        },
        {
            id: 'scenario-3',
            name: 'Supply Chain Disruption',
            type: 'supply_chain',
            status: 'draft',
            risk_level: 'medium',
            created_at: '2024-01-12',
            description: 'Major supplier outage causing production delays',
            impact_estimate: '$1.8M',
            likelihood: '30%'
        }
    ]

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active': return 'bg-green-100 text-green-800'
            case 'completed': return 'bg-blue-100 text-blue-800'
            case 'draft': return 'bg-gray-100 text-gray-800'
            default: return 'bg-gray-100 text-gray-800'
        }
    }

    const getRiskColor = (level: string) => {
        switch (level) {
            case 'critical': return 'bg-red-100 text-red-800'
            case 'high': return 'bg-orange-100 text-orange-800'
            case 'medium': return 'bg-yellow-100 text-yellow-800'
            case 'low': return 'bg-green-100 text-green-800'
            default: return 'bg-gray-100 text-gray-800'
        }
    }

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'financial': return <TrendingUp className="h-5 w-5" />
            case 'cyber': return <Shield className="h-5 w-5" />
            case 'supply_chain': return <Zap className="h-5 w-5" />
            default: return <AlertTriangle className="h-5 w-5" />
        }
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b">
                <div className="container mx-auto px-4 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Risk Scenarios</h1>
                            <p className="text-gray-600 mt-2">Create and manage AI-driven risk scenarios</p>
                        </div>
                        <Link href="/scenarios/create">
                            <Button className="flex items-center gap-2">
                                <Plus className="h-4 w-4" />
                                Create Scenario
                            </Button>
                        </Link>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="container mx-auto px-4 py-8">
                {/* Stats Cards */}
                <div className="grid md:grid-cols-4 gap-6 mb-8">
                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-gray-600">Total Scenarios</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">12</div>
                            <p className="text-xs text-gray-500">+2 this month</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-gray-600">Active Scenarios</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">5</div>
                            <p className="text-xs text-gray-500">Currently running</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-gray-600">High Risk</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-red-600">3</div>
                            <p className="text-xs text-gray-500">Require attention</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium text-gray-600">Avg Impact</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">$2.8M</div>
                            <p className="text-xs text-gray-500">Expected loss</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Scenarios Grid */}
                <div className="grid gap-6">
                    {scenarios.map((scenario) => (
                        <Card key={scenario.id} className="hover:shadow-lg transition-shadow">
                            <CardHeader>
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-blue-100 rounded-lg">
                                            {getTypeIcon(scenario.type)}
                                        </div>
                                        <div>
                                            <CardTitle className="text-lg">{scenario.name}</CardTitle>
                                            <CardDescription className="mt-1">
                                                {scenario.description}
                                            </CardDescription>
                                        </div>
                                    </div>
                                    <div className="flex gap-2">
                                        <Badge className={getRiskColor(scenario.risk_level)}>
                                            {scenario.risk_level}
                                        </Badge>
                                        <Badge className={getStatusColor(scenario.status)}>
                                            {scenario.status}
                                        </Badge>
                                    </div>
                                </div>
                            </CardHeader>

                            <CardContent>
                                <div className="grid md:grid-cols-4 gap-4 mb-4">
                                    <div>
                                        <p className="text-sm text-gray-600">Type</p>
                                        <p className="font-medium capitalize">{scenario.type.replace('_', ' ')}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-600">Impact Estimate</p>
                                        <p className="font-medium text-red-600">{scenario.impact_estimate}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-600">Likelihood</p>
                                        <p className="font-medium">{scenario.likelihood}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-600">Created</p>
                                        <p className="font-medium">{scenario.created_at}</p>
                                    </div>
                                </div>

                                <div className="flex gap-2">
                                    <Link href={`/scenarios/${scenario.id}`}>
                                        <Button variant="outline" size="sm">View Details</Button>
                                    </Link>
                                    <Link href={`/scenarios/${scenario.id}/simulate`}>
                                        <Button size="sm">Run Simulation</Button>
                                    </Link>
                                    <Button variant="outline" size="sm">Generate Report</Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                {/* Empty State */}
                {scenarios.length === 0 && (
                    <Card className="text-center py-12">
                        <CardContent>
                            <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-gray-900 mb-2">No scenarios yet</h3>
                            <p className="text-gray-600 mb-4">
                                Create your first risk scenario to start analyzing potential threats
                            </p>
                            <Link href="/scenarios/create">
                                <Button>Create Your First Scenario</Button>
                            </Link>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    )
}
