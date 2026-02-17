"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  CheckCircle,
  XCircle,
  Shield,
  Clock,
  MapPin,
  Package,
  User,
  Copy,
  FileText,
  Zap,
  Database,
} from "lucide-react"
import { apiClient, type VerificationResult } from "@/lib/api"

interface SimpleVerificationResultProps {
  result: VerificationResult
  onClose?: () => void
}

export default function SimpleVerificationResult({ result, onClose }: SimpleVerificationResultProps) {
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
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

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Main Result Card */}
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
                {result.risk_level?.toUpperCase() || 'UNKNOWN'} RISK
              </Badge>
              <div className="mt-2">
                <div className={`text-3xl font-bold ${getConfidenceColor(result.confidence_score || 0)}`}>
                  {Math.round((result.confidence_score || 0) * 100)}%
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
              <p className="text-lg font-semibold">{result.product?.product_name || 'Unknown'}</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Batch Number</p>
              <p className="text-lg font-mono">{result.product?.batch_number || 'Unknown'}</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Category</p>
              <Badge variant="outline" className="text-sm">
                {result.product?.category?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Details Grid */}
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
                  <span className="text-sm font-mono">{result.product?.id || 'N/A'}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(result.product?.id?.toString() || '')}
                  >
                    <Copy className="w-3 h-3" />
                  </Button>
                </div>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium">Manufacturing Date:</span>
                <span className="text-sm">
                  {result.product?.manufacturing_date ? 
                    new Date(result.product.manufacturing_date).toLocaleDateString() : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium">Category:</span>
                <Badge variant="outline">
                  {result.product?.category?.replace('_', ' ').toUpperCase() || 'UNKNOWN'}
                </Badge>
              </div>
            </div>
            {result.product?.product_description && (
              <div>
                <p className="text-sm font-medium mb-2">Description:</p>
                <p className="text-sm text-muted-foreground">{result.product.product_description}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Verification Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Verification Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm font-medium">Verification ID:</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-mono">{result.verification?.id || 'N/A'}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(result.verification?.id?.toString() || '')}
                  >
                    <Copy className="w-3 h-3" />
                  </Button>
                </div>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium">Verification Date:</span>
                <span className="text-sm">
                  {result.verification?.verification_date ? 
                    new Date(result.verification.verification_date).toLocaleString() : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm font-medium">Location:</span>
                <span className="text-sm">{result.verification?.location || 'N/A'}</span>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Confidence Score:</span>
                  <span className={`text-sm font-semibold ${getConfidenceColor(result.confidence_score || 0)}`}>
                    {Math.round((result.confidence_score || 0) * 100)}%
                  </span>
                </div>
                <Progress value={(result.confidence_score || 0) * 100} className="h-2" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detection Reasons */}
      {result.detection_reasons && result.detection_reasons.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
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
                    {(() => {
                      const reasonLower = reason.toLowerCase();
                      // Positive indicators (green checkmark)
                      if (reasonLower.includes("valid") || 
                          reasonLower.includes("matches") || 
                          reasonLower.includes("complete") || 
                          reasonLower.includes("reasonable") ||
                          (reasonLower.includes("verified") && !reasonLower.includes("not verified"))) {
                        return <CheckCircle className="w-4 h-4 text-emerald-600" />;
                      }
                      // Negative indicators (red X)
                      else if (reasonLower.includes("mismatch") || 
                               reasonLower.includes("invalid") || 
                               reasonLower.includes("failed") || 
                               reasonLower.includes("not found") || 
                               reasonLower.includes("not registered") ||
                               reasonLower.includes("not verified")) {
                        return <XCircle className="w-4 h-4 text-red-600" />;
                      }
                      // Neutral/warning indicators (blue shield)
                      else {
                        return <Shield className="w-4 h-4 text-blue-600" />;
                      }
                    })()}
                  </div>
                  <div className="flex-1">
                    <span className="text-sm">{reason}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Blockchain & IPFS Status */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5" />
              Blockchain Verification
            </CardTitle>
          </CardHeader>
          <CardContent>
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
                      onClick={() => copyToClipboard(result.blockchain_verification_id || '')}
                    >
                      <Copy className="w-3 h-3" />
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
          <CardContent>
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

      {/* Action Buttons */}
      <div className="flex justify-center gap-4">
        {onClose && (
          <Button onClick={onClose} variant="outline">
            Close
          </Button>
        )}
        <Button onClick={() => window.print()} variant="outline">
          <FileText className="w-4 h-4 mr-2" />
          Print Report
        </Button>
        <Button onClick={() => copyToClipboard(JSON.stringify(result, null, 2))}>
          <Copy className="w-4 h-4 mr-2" />
          Copy Report
        </Button>
      </div>
    </div>
  )
}
