"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Shield,
  Users,
  Settings,
  Key,
  AlertTriangle,
  CheckCircle,
  Crown,
  UserPlus,
  Database,
  Activity,
} from "lucide-react"
import { apiClient, type GrantRoleRequest } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"

export default function AdminDashboard() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  // Role management state
  const [roleForm, setRoleForm] = useState<GrantRoleRequest>({
    role: "MANUFACTURER_ROLE",
    account: "",
  })

  // Network stats
  const [networkStats, setNetworkStats] = useState({
    totalProducts: 0,
    networkStatus: null as any,
  })

  useEffect(() => {
    if (user?.role === "ADMIN") {
      loadNetworkStats()
    }
  }, [user])

  const loadNetworkStats = async () => {
    try {
      const [productsResult, statusResult] = await Promise.all([
        apiClient.getTotalProducts(),
        apiClient.getDetailedNetworkInfo(),
      ])

      setNetworkStats({
        totalProducts: productsResult.total_products,
        networkStatus: statusResult,
      })
    } catch (err) {
      console.error("Failed to load network stats:", err)
    }
  }

  const handleGrantRole = async () => {
    if (!roleForm.account.trim()) {
      setError("Account address is required")
      return
    }

    try {
      setLoading(true)
      setError("")
      setSuccess("")

      const result = await apiClient.grantBlockchainRole(roleForm)
      setSuccess(`Successfully granted ${result.role} to ${result.account}`)
      setRoleForm({ ...roleForm, account: "" })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to grant role")
    } finally {
      setLoading(false)
    }
  }

  // Check if user is admin
  if (user?.role !== "ADMIN") {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Shield className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">Access Denied</h3>
            <p className="text-muted-foreground text-center">You need administrator privileges to access this page.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Crown className="w-8 h-8 text-primary" />
        <div>
          <h1 className="text-3xl font-bold text-foreground">Admin Dashboard</h1>
          <p className="text-muted-foreground">Blockchain administration and role management</p>
        </div>
      </div>

      {/* Admin Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Network Status</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">
              <CheckCircle className="w-3 h-3 mr-1" />
              Online
            </Badge>
            <p className="text-xs text-muted-foreground mt-1">Blockchain operational</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Products</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{networkStats.totalProducts}</div>
            <p className="text-xs text-muted-foreground">On blockchain</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">-</div>
            <p className="text-xs text-muted-foreground">System users</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Admin Level</CardTitle>
            <Crown className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <Badge className="bg-primary text-primary-foreground">Super Admin</Badge>
            <p className="text-xs text-muted-foreground mt-1">Full access</p>
          </CardContent>
        </Card>
      </div>

      {/* Admin Tabs */}
      <Tabs defaultValue="roles" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="roles">Role Management</TabsTrigger>
          <TabsTrigger value="network">Network Control</TabsTrigger>
          <TabsTrigger value="settings">System Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="roles" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus className="w-5 h-5" />
                Grant Blockchain Roles
              </CardTitle>
              <CardDescription>
                Assign blockchain roles to user wallet addresses for smart contract interactions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="role">Role Type</Label>
                  <Select value={roleForm.role} onValueChange={(value) => setRoleForm({ ...roleForm, role: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="MANUFACTURER_ROLE">Manufacturer Role</SelectItem>
                      <SelectItem value="VERIFIER_ROLE">Verifier Role</SelectItem>
                      <SelectItem value="ADMIN_ROLE">Admin Role</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="account">Wallet Address</Label>
                  <Input
                    id="account"
                    placeholder="0x..."
                    value={roleForm.account}
                    onChange={(e) => setRoleForm({ ...roleForm, account: e.target.value })}
                  />
                </div>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {success && (
                <Alert className="border-emerald-200 bg-emerald-50">
                  <CheckCircle className="h-4 w-4 text-emerald-600" />
                  <AlertDescription className="text-emerald-700">{success}</AlertDescription>
                </Alert>
              )}

              <Button onClick={handleGrantRole} disabled={loading || !roleForm.account.trim()} className="w-full">
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Granting Role...
                  </>
                ) : (
                  <>
                    <Key className="w-4 h-4 mr-2" />
                    Grant Role
                  </>
                )}
              </Button>

              <div className="mt-6 p-4 bg-muted rounded-lg">
                <h4 className="font-medium mb-2">Role Descriptions</h4>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div>
                    <strong>Manufacturer Role:</strong> Can register products on the blockchain
                  </div>
                  <div>
                    <strong>Verifier Role:</strong> Can verify products and create verification records
                  </div>
                  <div>
                    <strong>Admin Role:</strong> Full administrative access to smart contract functions
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="network" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Network Information
              </CardTitle>
              <CardDescription>Detailed blockchain network status and configuration</CardDescription>
            </CardHeader>
            <CardContent>
              {networkStats.networkStatus ? (
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium">Network:</span>
                        <span className="text-sm">{networkStats.networkStatus.network_name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm font-medium">Chain ID:</span>
                        <span className="text-sm font-mono">{networkStats.networkStatus.chain_id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm font-medium">Block Number:</span>
                        <span className="text-sm font-mono">{networkStats.networkStatus.block_number}</span>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium">Total Products:</span>
                        <span className="text-sm">{networkStats.networkStatus.total_products}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm font-medium">Connection:</span>
                        <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">
                          {networkStats.networkStatus.is_connected ? "Connected" : "Disconnected"}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-muted rounded-lg">
                    <h4 className="font-medium mb-2">Smart Contract Address</h4>
                    <p className="text-sm font-mono break-all text-muted-foreground">
                      {networkStats.networkStatus.contract_address}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">Loading network information...</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                System Configuration
              </CardTitle>
              <CardDescription>Administrative settings and system configuration</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    System settings are currently managed through environment variables and smart contract
                    configuration. Contact the system administrator for configuration changes.
                  </AlertDescription>
                </Alert>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="p-4 bg-muted rounded-lg">
                    <h4 className="font-medium mb-2">Environment</h4>
                    <p className="text-sm text-muted-foreground">Development Mode</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg">
                    <h4 className="font-medium mb-2">API Version</h4>
                    <p className="text-sm text-muted-foreground">v1.0.0</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
