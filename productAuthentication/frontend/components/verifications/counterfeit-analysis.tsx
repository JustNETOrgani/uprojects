"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Search,
  Shield,
  TrendingUp,
  Clock,
  MapPin,
  FileText,
  Zap,
} from "lucide-react"
import { apiClient, type CounterfeitAnalysis } from "@/lib/api"

export default function CounterfeitAnalysisComponent() {
  const [productId, setProductId] = useState("")
  const [qrCodeHash, setQrCodeHash] = useState("")
  const [location, setLocation] = useState("")
  const [analysis, setAnalysis] = useState<CounterfeitAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleAnalyze = async () => {
    if (!productId.trim()) {
      setError("Product ID is required")
      return
    }

    try {
      setLoading(true)
      setError("")
      const result = await apiClient.analyzeCounterfeit(
        Number.parseInt(productId),
        qrCodeHash || undefined,
        location || undefined,
      )
      setAnalysis(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed")
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "low":
        return "text-emerald-600"
      case "medium":
        return "text-yellow-600"
      case "high":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  const getRiskLevelBg = (level: string) => {
    switch (level.toLowerCase()) {
      case "low":
        return "bg-emerald-50 border-emerald-200"
      case "medium":
        return "bg-yellow-50 border-yellow-200"
      case "high":
        return "bg-red-50 border-red-200"
      default:
        return "bg-gray-50 border-gray-200"
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Counterfeit Analysis</h1>
        <p className="text-muted-foreground">Comprehensive product authenticity analysis</p>
      </div>

      {/* Analysis Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5" />
            Product Analysis
          </CardTitle>
          <CardDescription>
            Enter product details to perform comprehensive counterfeit detection analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Product ID *</label>
              <Input placeholder="Enter product ID" value={productId} onChange={(e) => setProductId(e.target.value)} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">QR Code Hash (Optional)</label>
              <Input
                placeholder="Enter QR code hash"
                value={qrCodeHash}
                onChange={(e) => setQrCodeHash(e.target.value)}
              />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Analysis Location (Optional)</label>
            <Input
              placeholder="Enter location for analysis"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Button onClick={handleAnalyze} disabled={loading || !productId.trim()} className="w-full md:w-auto">
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyzing...
              </>
            ) : (
              <>
                <TrendingUp className="w-4 h-4 mr-2" />
                Analyze Product
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Overview Card */}
          <Card className={`border-2 bg-gray-50 border-gray-200`}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  {analysis.detection_result.is_authentic ? (
                    <CheckCircle className="w-6 h-6 text-emerald-600" />
                  ) : (
                    <XCircle className="w-6 h-6 text-red-600" />
                  )}
                  {analysis.product_name}
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <p className="text-sm font-medium">Authenticity Status</p>
                  <Badge className={analysis.detection_result.is_authentic ? "authentic" : "counterfeit"}>
                    {analysis.detection_result.is_authentic ? "Authentic" : "Counterfeit"}
                  </Badge>
                </div>
                <div className="space-y-2">
                  <p className="text-sm font-medium">Confidence Score</p>
                  <div className="flex items-center gap-2">
                    <Progress value={analysis.detection_result.confidence_score * 100} className="flex-1" />
                    <span className="text-sm font-medium">
                      {Math.round(analysis.detection_result.confidence_score * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 p-4 bg-card rounded-lg">
                <h4 className="font-medium mb-2">Recommendation</h4>
                <p className="text-sm text-muted-foreground">{analysis.risk_assessment.recommendation}</p>
              </div>
            </CardContent>
          </Card>

          {/* Detailed Analysis Tabs */}
          <Tabs defaultValue="detection" className="space-y-4">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="detection">Detection Results</TabsTrigger>
              <TabsTrigger value="blockchain">Blockchain Analysis</TabsTrigger>
            </TabsList>

            <TabsContent value="detection" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5" />
                    Detection Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {analysis.detection_result.detection_reasons.map((reason, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                        <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0"></div>
                        <p className="text-sm">{reason}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="blockchain" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="w-5 h-5" />
                    Blockchain Verification
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Blockchain Status:</span>
                        <Badge
                          variant={analysis.blockchain_analysis.blockchain_verification ? "default" : "destructive"}
                        >
                          {analysis.blockchain_analysis.blockchain_verification ? "Verified" : "Failed"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Verification Result:</span>
                        <Badge variant={analysis.blockchain_analysis.verification_result ? "default" : "destructive"}>
                          {analysis.blockchain_analysis.verification_result ? "Valid" : "Invalid"}
                        </Badge>
                      </div>
                    </div>
                    <div className="space-y-3">
                      {analysis.blockchain_analysis.transaction_hash && (
                        <div>
                          <span className="text-sm font-medium">Transaction Hash:</span>
                          <p className="text-xs text-muted-foreground font-mono break-all">
                            {analysis.blockchain_analysis.transaction_hash}
                          </p>
                        </div>
                      )}
                      {analysis.blockchain_analysis.block_number && (
                        <div>
                          <span className="text-sm font-medium">Block Number:</span>
                          <p className="text-sm text-muted-foreground">{analysis.blockchain_analysis.block_number}</p>
                        </div>
                      )}
                    </div>
                  </div>
                  {analysis.blockchain_analysis.error && (
                    <Alert variant="destructive" className="mt-4">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>{analysis.blockchain_analysis.error}</AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Analysis Metadata */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>Analyzed: {new Date(analysis.analysis_timestamp).toLocaleString()}</span>
                </div>
                <div className="flex items-center gap-1">
                  <FileText className="w-4 h-4" />
                  <span>Product ID: {analysis.product_id}</span>
                </div>
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  <span>Manufacturer ID: {analysis.manufacturer_id}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
