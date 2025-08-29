import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ArrowRight, Shield, TrendingUp, Users, Zap } from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
            {/* Header */}
            <header className="border-b bg-white/80 backdrop-blur-sm">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <Shield className="h-8 w-8 text-blue-600" />
                        <span className="text-xl font-bold">AI Risk Generator</span>
                    </div>
                    <nav className="hidden md:flex items-center space-x-6">
                        <Link href="/scenarios" className="text-gray-600 hover:text-gray-900">Scenarios</Link>
                        <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">Dashboard</Link>
                        <Link href="/reports" className="text-gray-600 hover:text-gray-900">Reports</Link>
                        <Button>Get Started</Button>
                    </nav>
                </div>
            </header>

            {/* Hero Section */}
            <section className="py-20 px-4">
                <div className="container mx-auto text-center">
                    <Badge variant="secondary" className="mb-4">
                        AI-Powered Risk Intelligence
                    </Badge>
                    <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Stress-Test Your Organization
                    </h1>
                    <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                        Generate AI-driven what-if scenarios that simulate financial, supply chain, and cyber risks.
                        Get quantitative simulations, causal maps, and mitigation strategies to strengthen resilience.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Button size="lg" className="text-lg px-8">
                            Create Scenario <ArrowRight className="ml-2 h-5 w-5" />
                        </Button>
                        <Button variant="outline" size="lg" className="text-lg px-8">
                            View Demo
                        </Button>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="py-16 px-4">
                <div className="container mx-auto">
                    <h2 className="text-3xl font-bold text-center mb-12">Comprehensive Risk Intelligence</h2>
                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <Card className="border-0 shadow-lg">
                            <CardHeader>
                                <TrendingUp className="h-10 w-10 text-blue-600 mb-2" />
                                <CardTitle>Financial Modeling</CardTitle>
                                <CardDescription>
                                    Monte Carlo simulations and stress-test curves for financial risk assessment
                                </CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="border-0 shadow-lg">
                            <CardHeader>
                                <Zap className="h-10 w-10 text-purple-600 mb-2" />
                                <CardTitle>Supply Chain Analysis</CardTitle>
                                <CardDescription>
                                    Model supplier dependencies and disruption cascades across your network
                                </CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="border-0 shadow-lg">
                            <CardHeader>
                                <Shield className="h-10 w-10 text-red-600 mb-2" />
                                <CardTitle>Cyber Risk Scenarios</CardTitle>
                                <CardDescription>
                                    Simulate cyber attacks and their business impact across domains
                                </CardDescription>
                            </CardHeader>
                        </Card>

                        <Card className="border-0 shadow-lg">
                            <CardHeader>
                                <Users className="h-10 w-10 text-green-600 mb-2" />
                                <CardTitle>Executive Reporting</CardTitle>
                                <CardDescription>
                                    Generate board-ready reports with actionable mitigation strategies
                                </CardDescription>
                            </CardHeader>
                        </Card>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-16 px-4 bg-gradient-to-r from-blue-600 to-purple-600">
                <div className="container mx-auto text-center text-white">
                    <h2 className="text-3xl font-bold mb-4">Ready to Strengthen Your Resilience?</h2>
                    <p className="text-xl mb-8 opacity-90">
                        Join leading organizations using AI-powered scenario planning
                    </p>
                    <Button size="lg" variant="secondary" className="text-lg px-8">
                        Start Free Trial
                    </Button>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-12 px-4">
                <div className="container mx-auto">
                    <div className="grid md:grid-cols-4 gap-8">
                        <div>
                            <div className="flex items-center space-x-2 mb-4">
                                <Shield className="h-6 w-6" />
                                <span className="font-bold">AI Risk Generator</span>
                            </div>
                            <p className="text-gray-400">
                                AI-powered risk scenario generation for enterprise resilience
                            </p>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-4">Product</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li><Link href="/scenarios" className="hover:text-white">Scenarios</Link></li>
                                <li><Link href="/simulations" className="hover:text-white">Simulations</Link></li>
                                <li><Link href="/reports" className="hover:text-white">Reports</Link></li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-4">Company</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li><Link href="/about" className="hover:text-white">About</Link></li>
                                <li><Link href="/security" className="hover:text-white">Security</Link></li>
                                <li><Link href="/compliance" className="hover:text-white">Compliance</Link></li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="font-semibold mb-4">Support</h3>
                            <ul className="space-y-2 text-gray-400">
                                <li><Link href="/docs" className="hover:text-white">Documentation</Link></li>
                                <li><Link href="/help" className="hover:text-white">Help Center</Link></li>
                                <li><Link href="/contact" className="hover:text-white">Contact</Link></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
                        <p>&copy; 2024 AI Risk Scenario Generator. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    )
}
