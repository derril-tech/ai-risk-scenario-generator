import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
    TrendingUp,
    TrendingDown,
    AlertTriangle,
    Shield,
    Activity,
    BarChart3,
    FileText,
    Clock
} from 'lucide-react'
import Link from 'next/link'

export default function DashboardPage() {
    const recentScenarios = [
        {
            id: 'scenario-1',
            name: 'Market Crash Scenario',
            type: 'financial',
            status: 'completed',
            risk_score: 8.5,
            last_run: '2 hours ago'
        },
        {
            id: 'scenario-2',
            name: 'Cyber Attack - Ransomware',
            type: 'cyber',
            status: 'running',
            risk_score: 9.2,
            last_run: 'Running now'
        },
        {
            id: 'scenario-3',
            name: 'Supply Chain Disruption',
            type: 'supply_chain',
            status: 'draft',
            risk_score: 6.8,
            last_run: '1 day ago'
        }
    ]

    const riskMetrics = [
        {
            title: 'Overall Risk Score',
            value: '7.8',
            change: '+0.3',
            trend: 'up',
            description: 'Weighted average across all scenarios'
        },
        {
            title: 'Expected Annual Loss',
            value: '$4.2M',
            change: '-$0.8M',
            trend: 'down',
            description: 'Projected losses from active scenarios'
        },
        {
            title: 'Mitigation Coverage',
            value: '68%',
            change: '+5%',
            trend: 'up',
            description: 'Risks with active mitigation strategies'
        },
        {
            title: 'Recovery Time',
            value: '72h',
            change: '-12h',
            trend: 'down',
            description: 'Average recovery time estimate'
        }
    ]

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed': return 'bg-green-100 text-green-800'
            case 'running': return 'bg-blue-100 text-blue-800'
            case 'draft': return 'bg-gray-100 text-gray-800'
            default: return 'bg-gray-100 text-gray-800'
        }
    }

    const getRiskColor = (score: number) => {
        if (score >= 8) return 'text-red-600'
        if (score >= 6) return 'text-orange-600'
        return 'text-green-600'
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b">
                <div className="container mx-auto px-4 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Risk Dashboard</h1>
                            <p className="text-gray-600 mt-2">Monitor and analyze organizational risk exposure</p>
                        </div>
                        <div className="flex gap-3">
                            <Link href="/scenarios/create">
                                <Button variant="outline">New Scenario</Button>
                            </Link>
                            <Link href="/reports">
                                <Button>Generate Report</Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="container mx-auto px-4 py-8">
                {/* Key Metrics */}
                <div className="grid md:grid-cols-4 gap-6 mb-8">
                    {riskMetrics.map((metric, index) => (
                        <Card key={index}>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-gray-600">
                                    {metric.title}
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex items-center justify-between">
                                    <div className="text-2xl font-bold">{metric.value}</div>
                                    <div className={`flex items-center text-sm ${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
                                        }`}>
                                        {metric.trend === 'up' ? (
                                            <TrendingUp className="h-4 w-4 mr-1" />
                                        ) : (
                                            <TrendingDown className="h-4 w-4 mr-1" />
                                        )}
                                        {metric.change}
                                    </div>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">{metric.description}</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    {/* Recent Scenarios */}
                    <div className="lg:col-span-2">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Activity className="h-5 w-5" />
                                    Recent Scenarios
                                </CardTitle>
                                <CardDescription>
                                    Latest risk scenarios and their current status
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {recentScenarios.map((scenario) => (
                                        <div key={scenario.id} className="flex items-center justify-between p-4 border rounded-lg">
                                            <div className="flex items-center gap-3">
                                                <div className="p-2 bg-blue-100 rounded-lg">
                                                    <Shield className="h-4 w-4" />
                                                </div>
                                                <div>
                                                    <h4 className="font-medium">{scenario.name}</h4>
                                                    <p className="text-sm text-gray-600 capitalize">
                                                        {scenario.type.replace('_', ' ')} • {scenario.last_run}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-3">
                                                <div className="text-right">
                                                    <div className={`font-bold ${getRiskColor(scenario.risk_score)}`}>
                                                        {scenario.risk_score}/10
                                                    </div>
                                                    <div className="text-xs text-gray-500">Risk Score</div>
                                                </div>
                                                <Badge className={getStatusColor(scenario.status)}>
                                                    {scenario.status}
                                                </Badge>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="mt-4 pt-4 border-t">
                                    <Link href="/scenarios">
                                        <Button variant="outline" className="w-full">
                                            View All Scenarios
                                        </Button>
                                    </Link>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Quick Actions */}
                    <div className="space-y-6">
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Quick Actions</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <Link href="/scenarios/create">
                                    <Button variant="outline" className="w-full justify-start">
                                        <AlertTriangle className="h-4 w-4 mr-2" />
                                        Create New Scenario
                                    </Button>
                                </Link>
                                <Link href="/simulations">
                                    <Button variant="outline" className="w-full justify-start">
                                        <BarChart3 className="h-4 w-4 mr-2" />
                                        Run Simulation
                                    </Button>
                                </Link>
                                <Link href="/reports">
                                    <Button variant="outline" className="w-full justify-start">
                                        <FileText className="h-4 w-4 mr-2" />
                                        Generate Report
                                    </Button>
                                </Link>
                                <Link href="/mitigations">
                                    <Button variant="outline" className="w-full justify-start">
                                        <Shield className="h-4 w-4 mr-2" />
                                        View Mitigations
                                    </Button>
                                </Link>
                            </CardContent>
                        </Card>

                        {/* Risk Alerts */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg flex items-center gap-2">
                                    <AlertTriangle className="h-5 w-5 text-red-500" />
                                    Risk Alerts
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                                    <div className="flex items-center gap-2 mb-1">
                                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                                        <span className="font-medium text-sm">Critical Risk</span>
                                    </div>
                                    <p className="text-sm text-gray-700">
                                        Cyber scenario shows 92% likelihood of impact
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
                                </div>

                                <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                                    <div className="flex items-center gap-2 mb-1">
                                        <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                                        <span className="font-medium text-sm">High Risk</span>
                                    </div>
                                    <p className="text-sm text-gray-700">
                                        Market volatility increased by 15%
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">1 day ago</p>
                                </div>

                                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                                    <div className="flex items-center gap-2 mb-1">
                                        <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                                        <span className="font-medium text-sm">Medium Risk</span>
                                    </div>
                                    <p className="text-sm text-gray-700">
                                        Supplier concentration above threshold
                                    </p>
                                    <p className="text-xs text-gray-500 mt-1">3 days ago</p>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Recent Activity */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg flex items-center gap-2">
                                    <Clock className="h-5 w-5" />
                                    Recent Activity
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                <div className="text-sm">
                                    <p className="font-medium">Simulation completed</p>
                                    <p className="text-gray-600">Market Crash Scenario</p>
                                    <p className="text-xs text-gray-500">2 hours ago</p>
                                </div>

                                <div className="text-sm">
                                    <p className="font-medium">Report generated</p>
                                    <p className="text-gray-600">Executive Summary Q4</p>
                                    <p className="text-xs text-gray-500">1 day ago</p>
                                </div>

                                <div className="text-sm">
                                    <p className="font-medium">Mitigation implemented</p>
                                    <p className="text-gray-600">Enhanced backup system</p>
                                    <p className="text-xs text-gray-500">3 days ago</p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}
