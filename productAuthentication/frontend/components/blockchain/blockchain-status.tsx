"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Activity,
  Server,
  Database,
  Shield,
  Zap,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Network,
  Hash,
} from "lucide-react"
import { apiClient, type BlockchainStatus } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"

interface NetworkStats {
  totalProducts: number
  blockchainStatus: BlockchainStatus | null
  detailedInfo: any | null
}

export default function BlockchainStatusComponent() {
  const { user } = useAuth()
  const [stats, setStats] = useState<NetworkStats>({
    totalProducts: 0,
    blockchainStatus: null,
    detailedInfo: null,
  })
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    loadBlockchainStatus()
  }, [])

  const loadBlockchainStatus = async () => {
    try {
      setLoading(true)
      setError("")

      // Load basic status and product count
      const [statusResult, productsResult] = await Promise.all([
        apiClient.getBlockchainStatus(),
        apiClient.getTotalProducts(),
      ])

      let detailedInfo = null
      // Load detailed info if user is admin
      if (user?.role === "ADMIN") {
        try {
          detailedInfo = await apiClient.getDetailedNetworkInfo()
        } catch (err) {
          console.warn("Could not load detailed network info:", err)
        }
      }

      setStats({
        totalProducts: productsResult.total_products,
        blockchainStatus: statusResult,
        detailedInfo,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load blockchain status")
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadBlockchainStatus()
    setRefreshing(false)
  }

  const getStatusBadge = (isConnected: boolean) => {
    return isConnected ? (
      <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">
        <CheckCircle className="w-3 h-3 mr-1" />
        Connected
      </Badge>
    ) : (
      <Badge className="bg-red-100 text-red-700 border-red-200">
        <AlertTriangle className="w-3 h-3 mr-1" />
        Disconnected
      </Badge>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading blockchain status...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Blockchain Status</h1>
          <p className="text-muted-foreground">Monitor blockchain network and smart contract status</p>
        </div>
        <Button onClick={handleRefresh} disabled={refreshing} variant="outline">
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? "animate-spin" : ""}`} />
          Refresh Status
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Status Overview */}
      {stats.blockchainStatus && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Network Status</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {getStatusBadge(stats.blockchainStatus.connected)}
                <p className="text-xs text-muted-foreground">{stats.blockchainStatus.network_name}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Chain ID</CardTitle>
              <Network className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stats.blockchainStatus.chain_id}</div>
              <p className="text-xs text-muted-foreground">Network identifier</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Block</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stats.blockchainStatus.latest_block}</div>
              <p className="text-xs text-muted-foreground">Latest block number</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Products</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">{stats.totalProducts}</div>
              <p className="text-xs text-muted-foreground">On blockchain</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Detailed Information Tabs */}
      <Tabs defaultValue="network" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="network">Network Info</TabsTrigger>
          <TabsTrigger value="contract">Smart Contract</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="network" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="w-5 h-5" />
                Network Information
              </CardTitle>
              <CardDescription>Blockchain network details and connection status</CardDescription>
            </CardHeader>
            <CardContent>
              {stats.blockchainStatus ? (
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Network Name:</span>
                      <span className="text-sm">{stats.blockchainStatus.network}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Chain ID:</span>
                      <span className="text-sm font-mono">{stats.blockchainStatus.chain_id}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Connection Status:</span>
                      {getStatusBadge(stats.blockchainStatus.connected)}
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Current Block:</span>
                      <span className="text-sm font-mono">{stats.blockchainStatus.block_number}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Contract Address:</span>
                      <span className="text-xs font-mono break-all">{stats.blockchainStatus.contract_address}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Last Updated:</span>
                      <span className="text-sm">{new Date().toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">Network information not available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="contract" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Hash className="w-5 h-5" />
                Smart Contract Details
              </CardTitle>
              <CardDescription>Anti-counterfeit smart contract information</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-muted rounded-lg">
                  <h4 className="font-medium mb-2">Contract Address</h4>
                  <p className="text-sm font-mono break-all text-muted-foreground">
                    {stats.blockchainStatus?.contract_address || "Not available"}
                  </p>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <h4 className="font-medium">Contract Functions</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• registerProduct()</li>
                      <li>• verifyProduct()</li>
                      <li>• getProduct()</li>
                      <li>• grantUserRole()</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-medium">Statistics</h4>
                    <div className="text-sm text-muted-foreground space-y-1">
                      <div className="flex justify-between">
                        <span>Total Products:</span>
                        <span>{stats.totalProducts}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Network:</span>
                        <span>{stats.blockchainStatus?.network_name}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Performance Metrics
              </CardTitle>
              <CardDescription>Blockchain network performance and statistics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold text-primary mb-1">{stats.totalProducts}</div>
                  <p className="text-sm text-muted-foreground">Products Registered</p>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold text-emerald-600 mb-1">
                    {stats.blockchainStatus?.is_connected ? "100%" : "0%"}
                  </div>
                  <p className="text-sm text-muted-foreground">Network Uptime</p>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-2xl font-bold text-blue-600 mb-1">
                    {stats.blockchainStatus?.block_number || 0}
                  </div>
                  <p className="text-sm text-muted-foreground">Current Block</p>
                </div>
              </div>

              {stats.detailedInfo && (
                <div className="mt-6 p-4 bg-card border rounded-lg">
                  <h4 className="font-medium mb-3">Detailed Network Information (Admin)</h4>
                  <div className="grid gap-3 md:grid-cols-2 text-sm">
                    <div className="flex justify-between">
                      <span>Total Products:</span>
                      <span>{stats.detailedInfo.total_products}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Contract Address:</span>
                      <span className="font-mono text-xs">{stats.detailedInfo.contract_address}</span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
