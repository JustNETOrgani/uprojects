"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertTriangle, CheckCircle, XCircle, Search, Filter, TrendingUp, Shield, Eye, QrCode, MapPin, Clock, Package, Copy } from "lucide-react"
import { apiClient, type Verification } from "@/lib/api"
import { useAuth } from "@/contexts/auth-context"
import Link from "next/link"


interface VerificationStats {
  total: number
  authentic: number
  counterfeit: number
  pending: number
}

export default function SimpleVerificationDashboard() {
  const { user } = useAuth()
  const [verifications, setVerifications] = useState<Verification[]>([])
  const [stats, setStats] = useState<VerificationStats>({ total: 0, authentic: 0, counterfeit: 0, pending: 0 })
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [filterStatus, setFilterStatus] = useState<string>("all")

  const [copiedText, setCopiedText] = useState<string | null>(null)

  useEffect(() => {
    loadVerifications()
  }, [])

  const loadVerifications = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getVerifications()
      setVerifications(data)

      // Calculate stats
      const total = data.length
      const authentic = data.filter((v) => v.is_authentic).length
      const counterfeit = data.filter((v) => !v.is_authentic).length
      const pending = 0 // Assuming no pending status in current schema

      setStats({ total, authentic, counterfeit, pending })
    } catch (error) {
      console.error("Failed to load verifications:", error)
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevel = (verification: Verification): string => {
    if (verification.is_authentic) return "low"
    return "high"
  }

  const getRiskBadge = (level: string) => {
    switch (level) {
      case "low":
        return (
          <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">
            <CheckCircle className="w-3 h-3 mr-1" />
            Low Risk
          </Badge>
        )
      case "medium":
        return (
          <Badge className="bg-yellow-100 text-yellow-700 border-yellow-200">
            <AlertTriangle className="w-3 h-3 mr-1" />
            Medium Risk
          </Badge>
        )
      case "high":
        return (
          <Badge className="bg-red-100 text-red-700 border-red-200">
            <XCircle className="w-3 h-3 mr-1" />
            High Risk
          </Badge>
        )
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getAuthenticityBadge = (isAuthentic: boolean) => {
    return isAuthentic ? (
      <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">
        <Shield className="w-3 h-3 mr-1" />
        Authentic
      </Badge>
    ) : (
      <Badge className="bg-red-100 text-red-700 border-red-200">
        <XCircle className="w-3 h-3 mr-1" />
        Counterfeit
      </Badge>
    )
  }

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(label)
      setTimeout(() => setCopiedText(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const filteredVerifications = verifications.filter((verification) => {
    const matchesSearch =
      verification.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
      verification.notes?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter =
      filterStatus === "all" ||
      (filterStatus === "authentic" && verification.is_authentic) ||
      (filterStatus === "counterfeit" && !verification.is_authentic)
    return matchesSearch && matchesFilter
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading verifications...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Verification Management</h1>
          <p className="text-muted-foreground">Monitor product authenticity and counterfeit detection</p>
        </div>
        <div className="flex gap-2">
          <Link href="/verifications/scan">
            <Button className="bg-primary hover:bg-primary/90">
              <QrCode className="w-4 h-4 mr-2" />
              Scan QR Code
            </Button>
          </Link>
          <Link href="/verifications/analyze">
            <Button variant="outline">
              <TrendingUp className="w-4 h-4 mr-2" />
              Analyze Product
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Verifications</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{stats.total}</div>
            <p className="text-xs text-muted-foreground">All time verifications</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Authentic Products</CardTitle>
            <CheckCircle className="h-4 w-4 text-emerald-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">{stats.authentic}</div>
            <p className="text-xs text-muted-foreground">
              {stats.total > 0 ? Math.round((stats.authentic / stats.total) * 100) : 0}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Counterfeit Detected</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.counterfeit}</div>
            <p className="text-xs text-muted-foreground">
              {stats.total > 0 ? Math.round((stats.counterfeit / stats.total) * 100) : 0}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Risk Score</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {stats.total > 0 ? Math.round((stats.counterfeit / stats.total) * 100) : 0}
            </div>
            <p className="text-xs text-muted-foreground">Average risk level</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            placeholder="Search by location or notes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-[180px]">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Verifications</SelectItem>
            <SelectItem value="authentic">Authentic Only</SelectItem>
            <SelectItem value="counterfeit">Counterfeit Only</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Verifications List */}
      <div className="grid gap-4">
        {filteredVerifications.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Shield className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold text-foreground mb-2">No verifications found</h3>
              <p className="text-muted-foreground text-center">
                {searchTerm || filterStatus !== "all"
                  ? "Try adjusting your search or filter criteria"
                  : "Start by verifying your first product"}
              </p>
            </CardContent>
          </Card>
        ) : (
          filteredVerifications.map((verification) => (
            <Card key={verification.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="space-y-4">
                  {/* Header */}
                  <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-muted rounded-lg">
                        <Package className="w-5 h-5 text-muted-foreground" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-foreground">Product ID: {verification.product_id}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          {getAuthenticityBadge(verification.is_authentic)}
                          {getRiskBadge(getRiskLevel(verification))}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Link href={`/products/${verification.product_id}`}>
                        <Button variant="outline" size="sm">
                          <Eye className="w-4 h-4 mr-2" />
                          View Product
                        </Button>
                      </Link>
                      <Link href={`/verifications/analyze/${verification.product_id}`}>
                        <Button variant="outline" size="sm">
                          <TrendingUp className="w-4 h-4 mr-2" />
                          Analyze
                        </Button>
                      </Link>
                    </div>
                  </div>

                  {/* Details Grid */}
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-muted-foreground" />
                      <div>
                        <p className="text-xs text-muted-foreground">Location</p>
                        <p className="text-sm font-medium">{verification.location}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-muted-foreground" />
                      <div>
                        <p className="text-xs text-muted-foreground">Verified</p>
                        <p className="text-sm font-medium">
                          {new Date(verification.verification_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Shield className="w-4 h-4 text-muted-foreground" />
                      <div>
                        <p className="text-xs text-muted-foreground">Verification ID</p>
                        <div className="flex items-center gap-1">
                          <p className="text-sm font-mono">{verification.id}</p>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(verification.id.toString(), `Verification ${verification.id}`)}
                          >
                            {copiedText === `Verification ${verification.id}` ? (
                              <CheckCircle className="w-3 h-3" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </Button>
                        </div>
                      </div>
                    </div>
                    {verification.blockchain_verification_id && (
                      <div className="flex items-center gap-2">
                        <Shield className="w-4 h-4 text-muted-foreground" />
                        <div>
                          <p className="text-xs text-muted-foreground">Blockchain ID</p>
                          <div className="flex items-center gap-1">
                            <p className="text-sm font-mono truncate">{verification.blockchain_verification_id}</p>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyToClipboard(verification.blockchain_verification_id!, "Blockchain ID")}
                            >
                              {copiedText === "Blockchain ID" ? (
                                <CheckCircle className="w-3 h-3" />
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Notes */}
                  {verification.notes && (
                    <div className="p-3 bg-muted rounded-lg">
                      <p className="text-xs text-muted-foreground mb-1">Notes</p>
                      <p className="text-sm">{verification.notes}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>


    </div>
  )
}
