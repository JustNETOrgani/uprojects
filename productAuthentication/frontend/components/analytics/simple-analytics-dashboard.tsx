"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChartIcon,
  Activity,
  AlertTriangle,
  CheckCircle,
  Package,
  Users,
  Calendar,
  RefreshCw,
  Shield,
  XCircle,
} from "lucide-react"
import { apiClient, type AnalyticsData } from "@/lib/api"

// Simplified mock data
const mockAnalyticsData: AnalyticsData = {
  total_products: 1247,
  total_verifications: 3891,
  authentic_products: 1156,
  counterfeit_products: 91,
  verification_trends: [
    { date: "2024-01-01", count: 45 },
    { date: "2024-01-02", count: 52 },
    { date: "2024-01-03", count: 48 },
    { date: "2024-01-04", count: 61 },
    { date: "2024-01-05", count: 55 },
    { date: "2024-01-06", count: 67 },
    { date: "2024-01-07", count: 73 },
  ],
  category_distribution: [
    { category: "Electronics", count: 456 },
    { category: "Clothing", count: 312 },
    { category: "Medicine", count: 234 },
    { category: "Food", count: 156 },
    { category: "Automotive", count: 89 },
  ],
  manufacturer_stats: [
    { manufacturer_name: "TechCorp Inc.", product_count: 234, verification_count: 567 },
    { manufacturer_name: "Fashion Brand Co.", product_count: 189, verification_count: 445 },
    { manufacturer_name: "MedSupply Ltd.", product_count: 156, verification_count: 389 },
    { manufacturer_name: "AutoParts Pro", product_count: 123, verification_count: 298 },
  ],
}

export default function SimpleAnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData>(mockAnalyticsData)
  const [loading, setLoading] = useState(false)
  const [timeRange, setTimeRange] = useState("7d")
  const [selectedTab, setSelectedTab] = useState("overview")

  useEffect(() => {
    loadAnalytics()
  }, [timeRange])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      // Load real data from API
      const data = await apiClient.getAnalytics()
      console.log("Analytics data loaded:", data)
      setAnalytics(data)
    } catch (error) {
      console.error("Failed to load analytics:", error)
      // Fallback to mock data only if API fails
      setAnalytics(mockAnalyticsData)
    } finally {
      setLoading(false)
    }
  }

  const calculateAuthenticityRate = () => {
    const total = analytics.authentic_products + analytics.counterfeit_products
    return total > 0 ? Math.round((analytics.authentic_products / total) * 100) : 0
  }

  const calculateTrendPercentage = () => {
    const trends = analytics.verification_trends
    if (trends.length < 2) return 0
    const latest = trends[trends.length - 1].count
    const previous = trends[trends.length - 2].count
    return Math.round(((latest - previous) / previous) * 100)
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric" })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Analytics Dashboard</h1>
          <p className="text-muted-foreground">Comprehensive insights into product verification and authenticity</p>
        </div>
        <div className="flex gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[140px]">
              <Calendar className="w-4 h-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="1y">Last year</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={loadAnalytics} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Products</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{analytics.total_products.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Registered products</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Verifications</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{analytics.total_verifications.toLocaleString()}</div>
            <div className="flex items-center text-xs text-muted-foreground">
              {calculateTrendPercentage() >= 0 ? (
                <TrendingUp className="w-3 h-3 mr-1 text-emerald-600" />
              ) : (
                <TrendingDown className="w-3 h-3 mr-1 text-red-600" />
              )}
              {Math.abs(calculateTrendPercentage())}% from yesterday
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Authenticity Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">{calculateAuthenticityRate()}%</div>
            <p className="text-xs text-muted-foreground">
              {analytics.authentic_products} authentic, {analytics.counterfeit_products} counterfeit
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risk Level</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{100 - calculateAuthenticityRate()}%</div>
            <p className="text-xs text-muted-foreground">Counterfeit detection rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Tabs */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="manufacturers">Manufacturers</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Verification Trends - Simple Bar Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Verification Trends
                </CardTitle>
                <CardDescription>Daily verification activity over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics.verification_trends.map((trend, index) => (
                    <div key={trend.date} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>{formatDate(trend.date)}</span>
                        <span className="font-medium">{trend.count} verifications</span>
                      </div>
                      <Progress 
                        value={(trend.count / Math.max(...analytics.verification_trends.map(t => t.count))) * 100} 
                        className="h-2" 
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Authenticity Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="w-5 h-5" />
                  Authenticity Distribution
                </CardTitle>
                <CardDescription>Breakdown of authentic vs counterfeit products</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-emerald-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-emerald-600" />
                      <span className="font-medium">Authentic Products</span>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-emerald-600">{analytics.authentic_products}</div>
                      <div className="text-sm text-muted-foreground">
                        {Math.round((analytics.authentic_products / (analytics.authentic_products + analytics.counterfeit_products)) * 100)}%
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <XCircle className="w-5 h-5 text-red-600" />
                      <span className="font-medium">Counterfeit Products</span>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-red-600">{analytics.counterfeit_products}</div>
                      <div className="text-sm text-muted-foreground">
                        {Math.round((analytics.counterfeit_products / (analytics.authentic_products + analytics.counterfeit_products)) * 100)}%
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Verification Trends Analysis
              </CardTitle>
              <CardDescription>Detailed view of verification patterns over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.verification_trends.map((trend, index) => (
                  <div key={trend.date} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium">{index + 1}</span>
                      </div>
                      <div>
                        <div className="font-medium">{formatDate(trend.date)}</div>
                        <div className="text-sm text-muted-foreground">Daily verifications</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold">{trend.count}</div>
                      <div className="text-sm text-muted-foreground">verifications</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categories" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Product Categories
                </CardTitle>
                <CardDescription>Distribution of products by category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics.category_distribution.map((category, index) => (
                    <div key={category.category} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{category.category}</span>
                        <span>{category.count} products</span>
                      </div>
                      <Progress 
                        value={(category.count / analytics.total_products) * 100} 
                        className="h-2" 
                      />
                      <div className="text-xs text-muted-foreground text-right">
                        {Math.round((category.count / analytics.total_products) * 100)}% of total
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Category Statistics</CardTitle>
                <CardDescription>Detailed breakdown by product category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics.category_distribution.map((category, index) => (
                    <div key={category.category} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full bg-primary" />
                        <span className="font-medium">{category.category}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{category.count}</div>
                        <div className="text-xs text-muted-foreground">
                          {Math.round((category.count / analytics.total_products) * 100)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="manufacturers" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Manufacturer Performance
              </CardTitle>
              <CardDescription>Top manufacturers by product count and verification activity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.manufacturer_stats.map((manufacturer, index) => (
                  <div
                    key={manufacturer.manufacturer_name}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="space-y-1">
                      <h4 className="font-medium">{manufacturer.manufacturer_name}</h4>
                      <div className="flex gap-4 text-sm text-muted-foreground">
                        <span>{manufacturer.product_count} products</span>
                        <span>{manufacturer.verification_count} verifications</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline">#{index + 1}</Badge>
                      <div className="text-xs text-muted-foreground mt-1">
                        {Math.round(manufacturer.verification_count / manufacturer.product_count)} avg verifications
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
