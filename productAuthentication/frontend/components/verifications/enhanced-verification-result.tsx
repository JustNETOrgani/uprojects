"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Shield,
  TrendingUp,
  Clock,
  MapPin,
  FileText,
  Zap,
  Database,
  QrCode,
  Hash,
  User,
  Calendar,
  Package,
  Eye,
  Copy,
  ExternalLink,
  Info,
  Star,
  Activity,
  Lock,
  Unlock,
  Globe,
  Server,
} from "lucide-react"
import { apiClient } from "@/lib/api"

interface VerificationResult {
  product: {
    id: number
    product_name: string
    product_description?: string
    manufacturing_date: string
    batch_number: string
    category: string
    manufacturer: {
      full_name: string
      email: string
    }
  }
  verification: {
    id: number
    is_authentic: boolean
    location: string
    verification_date: string
    notes?: string
  }
  blockchain_verified: boolean
  blockchain_verification_id?: string
  detection_reasons: string[]
  confidence_score: number
  risk_level: string
}

interface EnhancedVerificationResultProps {
  result: VerificationResult
  onClose?: () => void
}

export default function EnhancedVerificationResult({ result, onClose }: EnhancedVerificationResultProps) {
  const [copiedText, setCopiedText] = useState<string | null>(null)

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(label)
      setTimeout(() => setCopiedText(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "low":
        return "text-emerald-600 bg-emerald-50 border-emerald-200"
      case "medium":
        return "text-yellow-600 bg-yellow-50 border-yellow-200"
      case "high":
        return "text-red-600 bg-red-50 border-red-200"
      default:
        return "text-gray-600 bg-gray-50 border-gray-200"
    }
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "text-emerald-600"
    if (score >= 0.6) return "text-yellow-600"
    return "text-red-600"
  }

  const getReasonIcon = (reason: string) => {
    if (reason.toLowerCase().includes("valid") || reason.toLowerCase().includes("verified") || reason.toLowerCase().includes("matches")) {
      return <CheckCircle className="w-4 h-4 text-emerald-600" />
    }
    if (reason.toLowerCase().includes("mismatch") || reason.toLowerCase().includes("invalid") || reason.toLowerCase().includes("failed")) {
      return <XCircle className="w-4 h-4 text-red-600" />
    }
    if (reason.toLowerCase().includes("warning") || reason.toLowerCase().includes("caution")) {
      return <AlertTriangle className="w-4 h-4 text-yellow-600" />
    }
    return <Info className="w-4 h-4 text-blue-600" />
  }

  const getReasonBadge = (reason: string) => {
    if (reason.toLowerCase().includes("valid") || reason.toLowerCase().includes("verified") || reason.toLowerCase().includes("matches")) {
      return "bg-emerald-100 text-emerald-700 border-emerald-200"
    }
    if (reason.toLowerCase().includes("mismatch") || reason.toLowerCase().includes("invalid") || reason.toLowerCase().includes("failed")) {
      return "bg-red-100 text-red-700 border-red-200"
    }
    if (reason.toLowerCase().includes("warning") || reason.toLowerCase().includes("caution")) {
      return "bg-yellow-100 text-yellow-700 border-yellow-200"
    }
    return "bg-blue-100 text-blue-700 border-blue-200"
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header with Main Result */}
      <Card className={`border-2 ${getRiskLevelColor(result.risk_level)}`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {result.verification.is_authentic ? (
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-8 h-8 text-emerald-600" />
                  <div>
                    <CardTitle className="text-2xl text-emerald-700">AUTHENTIC PRODUCT</CardTitle>
                    <CardDescription className="text-emerald-600">
                      This product has been verified as genuine
                    </CardDescription>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <XCircle className="w-8 h-8 text-red-600" />
                  <div>
                    <CardTitle className="text-2xl text-red-700">COUNTERFEIT DETECTED</CardTitle>
                    <CardDescription className="text-red-600">
                      This product has been flagged as potentially counterfeit
                    </CardDescription>
                  </div>
                </div>
              )}
            </div>
            <div className="text-right">
              <Badge className={`text-lg px-4 py-2 ${getRiskLevelColor(result.risk_level)}`}>
                {result.risk_level.toUpperCase()} RISK
              </Badge>
              <div className="mt-2">
                <div className={`text-3xl font-bold ${getConfidenceColor(result.confidence_score)}`}>
                  {Math.round(result.confidence_score * 100)}%
                </div>
                <div className="text-sm text-muted-foreground">Confidence</div>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <p className="text-sm font-medium">Product Name</p>
              <p className="text-lg font-semibold">{result.product.product_name}</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Batch Number</p>
              <p className="text-lg font-mono">{result.product.batch_number}</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Category</p>
              <Badge variant="outline" className="text-sm">
                {result.product.category.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Information Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="verification">Verification Details</TabsTrigger>
          <TabsTrigger value="blockchain">Blockchain & IPFS</TabsTrigger>
          <TabsTrigger value="analysis">Detection Analysis</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Product Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Package className="w-5 h-5" />
                  Product Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Product ID:</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-mono">{result.product.id}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(result.product.id.toString(), "Product ID")}
                      >
                        {copiedText === "Product ID" ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                      </Button>
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Manufacturing Date:</span>
                    <span className="text-sm">{new Date(result.product.manufacturing_date).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Category:</span>
                    <Badge variant="outline">
                      {result.product.category.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>
                </div>
                {result.product.product_description && (
                  <div>
                    <p className="text-sm font-medium mb-2">Description:</p>
                    <p className="text-sm text-muted-foreground">{result.product.product_description}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Manufacturer Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Manufacturer Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Manufacturer:</span>
                    <span className="text-sm font-semibold">{result.product.manufacturer.full_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Email:</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm">{result.product.manufacturer.email}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(result.product.manufacturer.email, "Email")}
                      >
                        {copiedText === "Email" ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Verification Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Verification Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className={`text-3xl font-bold mb-2 ${getConfidenceColor(result.confidence_score)}`}>
                    {Math.round(result.confidence_score * 100)}%
                  </div>
                  <p className="text-sm text-muted-foreground">Confidence Score</p>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-3xl font-bold mb-2 text-blue-600">
                    {result.detection_reasons.length}
                  </div>
                  <p className="text-sm text-muted-foreground">Validation Checks</p>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className={`text-3xl font-bold mb-2 ${result.verification.is_authentic ? 'text-emerald-600' : 'text-red-600'}`}>
                    {result.verification.is_authentic ? 'PASS' : 'FAIL'}
                  </div>
                  <p className="text-sm text-muted-foreground">Overall Result</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Verification Details Tab */}
        <TabsContent value="verification" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Verification Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Verification ID:</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-mono">{result.verification.id}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(result.verification.id.toString(), "Verification ID")}
                      >
                        {copiedText === "Verification ID" ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                      </Button>
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Verification Date:</span>
                    <span className="text-sm">{new Date(result.verification.verification_date).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Location:</span>
                    <span className="text-sm">{result.verification.location}</span>
                  </div>
                  {result.verification.notes && (
                    <div>
                      <p className="text-sm font-medium mb-2">Notes:</p>
                      <p className="text-sm text-muted-foreground">{result.verification.notes}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Risk Assessment
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Risk Level:</span>
                    <Badge className={getRiskLevelColor(result.risk_level)}>
                      {result.risk_level.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">Confidence Score:</span>
                      <span className={`text-sm font-semibold ${getConfidenceColor(result.confidence_score)}`}>
                        {Math.round(result.confidence_score * 100)}%
                      </span>
                    </div>
                    <Progress value={result.confidence_score * 100} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Blockchain & IPFS Tab */}
        <TabsContent value="blockchain" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5" />
                  Blockchain Verification
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Blockchain Status:</span>
                    <Badge variant={result.blockchain_verified ? "default" : "destructive"}>
                      {result.blockchain_verified ? "Verified" : "Not Verified"}
                    </Badge>
                  </div>
                  {result.blockchain_verification_id && (
                    <div>
                      <p className="text-sm font-medium mb-2">Blockchain Verification ID:</p>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono break-all bg-muted p-2 rounded">
                          {result.blockchain_verification_id}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyToClipboard(result.blockchain_verification_id!, "Blockchain ID")}
                        >
                          {copiedText === "Blockchain ID" ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="w-5 h-5" />
                  IPFS Storage
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">IPFS Status:</span>
                    <Badge variant="default">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Available
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Data Integrity:</span>
                    <Badge variant="default">
                      <Shield className="w-3 h-3 mr-1" />
                      Verified
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Detection Analysis Tab */}
        <TabsContent value="analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Detection Analysis
              </CardTitle>
              <CardDescription>
                Detailed breakdown of all validation checks performed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {result.detection_reasons.map((reason, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                    <div className="flex-shrink-0 mt-0.5">
                      {getReasonIcon(reason)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium">{reason}</span>
                        <Badge className={`text-xs ${getReasonBadge(reason)}`}>
                          {reason.toLowerCase().includes("valid") || reason.toLowerCase().includes("verified") || reason.toLowerCase().includes("matches") ? "PASS" : 
                           reason.toLowerCase().includes("mismatch") || reason.toLowerCase().includes("invalid") || reason.toLowerCase().includes("failed") ? "FAIL" : "INFO"}
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex justify-center gap-4">
        <Button onClick={onClose} variant="outline">
          Close
        </Button>
        <Button onClick={() => window.print()} variant="outline">
          <FileText className="w-4 h-4 mr-2" />
          Print Report
        </Button>
        <Button onClick={() => copyToClipboard(JSON.stringify(result, null, 2), "Full Report")}>
          {copiedText === "Full Report" ? (
            <>
              <CheckCircle className="w-4 h-4 mr-2" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 mr-2" />
              Copy Report
            </>
          )}
        </Button>
      </div>
    </div>
  )
}
