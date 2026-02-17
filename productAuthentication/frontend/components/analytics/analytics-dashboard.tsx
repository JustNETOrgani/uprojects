"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts"
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
} from "lucide-react"
import type { AnalyticsData } from "@/lib/api"

// Mock data for demonstration (replace with real API calls)
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

const COLORS = ["#059669", "#10b981", "#34d399", "#6ee7b7", "#a7f3d0"]

export default function AnalyticsDashboard() {
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
      // For now, using mock data since analytics endpoints might not be fully implemented
      // const data = await apiClient.getAnalytics()
      // setAnalytics(data)

      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 1000))
      setAnalytics(mockAnalyticsData)
    } catch (error) {
      console.error("Failed to load analytics:", error)
      // Fallback to mock data
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
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Verification Trends
                </CardTitle>
                <CardDescription>Daily verification activity over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    count: {
                      label: "Verifications",
                      color: "hsl(var(--chart-1))",
                    },
                  }}
                  className="h-[300px]"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={analytics.verification_trends}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={formatDate} />
                      <YAxis />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Area
                        type="monotone"
                        dataKey="count"
                        stroke="var(--color-count)"
                        fill="var(--color-count)"
                        fillOpacity={0.3}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChartIcon className="w-5 h-5" />
                  Authenticity Distribution
                </CardTitle>
                <CardDescription>Breakdown of authentic vs counterfeit products</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer
                  config={{
                    authentic: {
                      label: "Authentic",
                      color: "hsl(var(--chart-1))",
                    },
                    counterfeit: {
                      label: "Counterfeit",
                      color: "hsl(var(--chart-5))",
                    },
                  }}
                  className="h-[300px]"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={[
                          { name: "Authentic", value: analytics.authentic_products, fill: "var(--color-authentic)" },
                          {
                            name: "Counterfeit",
                            value: analytics.counterfeit_products,
                            fill: "var(--color-counterfeit)",
                          },
                        ]}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        <Cell fill="#059669" />
                        <Cell fill="#be123c" />
                      </Pie>
                      <ChartTooltip content={<ChartTooltipContent />} />
                    </PieChart>
                  </ResponsiveContainer>
                </ChartContainer>
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
              <ChartContainer
                config={{
                  count: {
                    label: "Daily Verifications",
                    color: "hsl(var(--chart-1))",
                  },
                }}
                className="h-[400px]"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={analytics.verification_trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={formatDate} />
                    <YAxis />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="var(--color-count)"
                      strokeWidth={3}
                      dot={{ fill: "var(--color-count)", strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartContainer>
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
                <ChartContainer
                  config={{
                    count: {
                      label: "Products",
                      color: "hsl(var(--chart-1))",
                    },
                  }}
                  className="h-[300px]"
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={analytics.category_distribution} layout="horizontal">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="category" type="category" width={80} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Bar dataKey="count" fill="var(--color-count)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartContainer>
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
                    <div key={category.category} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <span className="text-sm font-medium">{category.category}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold">{category.count}</div>
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
