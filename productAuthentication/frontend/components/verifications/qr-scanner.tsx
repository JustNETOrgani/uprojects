"use client"

import { useState, useRef } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  QrCode,
  Camera,
  Upload,
  FileText,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Scan,
  Smartphone,
  Monitor,
  Shield,
  Zap,
  Database,
  Copy,
  ExternalLink,
} from "lucide-react"
import { apiClient, type VerificationResult } from "@/lib/api"
import SimpleVerificationResult from "./simple-verification-result"



export default function QRScanner() {
  const [activeTab, setActiveTab] = useState("scan")
  const [qrData, setQrData] = useState("")
  const [location, setLocation] = useState("")
  const [notes, setNotes] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [result, setResult] = useState<VerificationResult | null>(null)
  const [copiedText, setCopiedText] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(label)
      setTimeout(() => setCopiedText(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const handleScan = async () => {
    if (!qrData.trim()) {
      setError("Please enter QR code data")
      return
    }

    try {
      setLoading(true)
      setError("")
      setResult(null)

      const verificationData = {
        qr_data: qrData,
        location: location || "Unknown",
        notes: notes || ""
      }

      const response = await apiClient.verifyProduct(verificationData)
      setResult(response)
      setError("") // Clear any previous errors
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed")
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        setQrData(content)
      }
      reader.readAsText(file)
    }
  }

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText()
      setQrData(text)
    } catch (err) {
      setError("Failed to paste from clipboard")
    }
  }

  const resetForm = () => {
    setQrData("")
    setLocation("")
    setNotes("")
    setError("")
    setResult(null)
  }

  const getLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude
          const lng = position.coords.longitude
          setLocation(`${lat.toFixed(4)}, ${lng.toFixed(4)}`)
        },
        (error) => {
          console.error("Error getting location:", error)
        }
      )
    }
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-foreground mb-2">Product Verification</h1>
        <p className="text-muted-foreground">
          Scan or enter QR code data to verify product authenticity
        </p>
      </div>

      {result ? (
        <SimpleVerificationResult 
          result={result} 
          onClose={() => setResult(null)} 
        />
      ) : (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="scan">QR Scanner</TabsTrigger>
            <TabsTrigger value="manual">Manual Entry</TabsTrigger>
            <TabsTrigger value="upload">Upload File</TabsTrigger>
          </TabsList>

          {/* QR Scanner Tab */}
          <TabsContent value="scan" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <QrCode className="w-5 h-5" />
                  QR Code Scanner
                </CardTitle>
                <CardDescription>
                  Use your device camera to scan QR codes or enter data manually
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center p-8 border-2 border-dashed border-muted-foreground/25 rounded-lg">
                  <Camera className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-semibold mb-2">Camera Scanner</h3>
                  <p className="text-muted-foreground mb-4">
                    Point your camera at a QR code to scan it automatically
                  </p>
                  <Button className="mb-4">
                    <Scan className="w-4 h-4 mr-2" />
                    Start Camera Scan
                  </Button>
                  <div className="text-sm text-muted-foreground">
                    <p>Or use the manual entry tab below</p>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Location (Optional)</label>
                    <div className="flex gap-2">
                      <Input
                        placeholder="Enter verification location"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                      />
                      <Button variant="outline" onClick={getLocation}>
                        <MapPin className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Notes (Optional)</label>
                    <Input
                      placeholder="Add verification notes"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Manual Entry Tab */}
          <TabsContent value="manual" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Manual QR Data Entry
                </CardTitle>
                <CardDescription>
                  Enter QR code data manually or paste from clipboard
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">QR Code Data *</label>
                  <div className="space-y-2">
                    <textarea
                      className="w-full min-h-[120px] p-3 border rounded-md resize-none"
                      placeholder="Paste QR code data here (JSON format)..."
                      value={qrData}
                      onChange={(e) => setQrData(e.target.value)}
                    />
                    <div className="flex gap-2">
                      <Button variant="outline" onClick={handlePaste} size="sm">
                        <Copy className="w-4 h-4 mr-2" />
                        Paste from Clipboard
                      </Button>
                      <Button variant="outline" onClick={() => setQrData("")} size="sm">
                        Clear
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Location (Optional)</label>
                    <div className="flex gap-2">
                      <Input
                        placeholder="Enter verification location"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                      />
                      <Button variant="outline" onClick={getLocation}>
                        <MapPin className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Notes (Optional)</label>
                    <Input
                      placeholder="Add verification notes"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </div>
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <div className="flex gap-2">
                  <Button 
                    onClick={handleScan} 
                    disabled={loading || !qrData.trim()}
                    className="flex-1"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Verifying...
                      </>
                    ) : (
                      <>
                        <Shield className="w-4 h-4 mr-2" />
                        Verify Product
                      </>
                    )}
                  </Button>
                  <Button variant="outline" onClick={resetForm}>
                    Reset
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Upload File Tab */}
          <TabsContent value="upload" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  Upload QR Data File
                </CardTitle>
                <CardDescription>
                  Upload a text file containing QR code data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center p-8 border-2 border-dashed border-muted-foreground/25 rounded-lg">
                  <Upload className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-semibold mb-2">Upload QR Data File</h3>
                  <p className="text-muted-foreground mb-4">
                    Select a text file containing QR code data
                  </p>
                  <Button onClick={() => fileInputRef.current?.click()}>
                    <Upload className="w-4 h-4 mr-2" />
                    Choose File
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".txt,.json"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>

                {qrData && (
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Loaded QR Data:</label>
                    <div className="p-3 bg-muted rounded-md">
                      <pre className="text-sm whitespace-pre-wrap">{qrData}</pre>
                    </div>
                  </div>
                )}

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Location (Optional)</label>
                    <div className="flex gap-2">
                      <Input
                        placeholder="Enter verification location"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                      />
                      <Button variant="outline" onClick={getLocation}>
                        <MapPin className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Notes (Optional)</label>
                    <Input
                      placeholder="Add verification notes"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </div>
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <div className="flex gap-2">
                  <Button 
                    onClick={handleScan} 
                    disabled={loading || !qrData.trim()}
                    className="flex-1"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Verifying...
                      </>
                    ) : (
                      <>
                        <Shield className="w-4 h-4 mr-2" />
                        Verify Product
                      </>
                    )}
                  </Button>
                  <Button variant="outline" onClick={resetForm}>
                    Reset
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Help Section */}
      {!result && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              How to Use
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="text-center">
                <Smartphone className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                <h4 className="font-medium mb-1">Mobile Scanning</h4>
                <p className="text-sm text-muted-foreground">
                  Use your phone camera to scan QR codes directly
                </p>
              </div>
              <div className="text-center">
                <Monitor className="w-8 h-8 mx-auto mb-2 text-green-600" />
                <h4 className="font-medium mb-1">Manual Entry</h4>
                <p className="text-sm text-muted-foreground">
                  Copy and paste QR data from any source
                </p>
              </div>
              <div className="text-center">
                <FileText className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                <h4 className="font-medium mb-1">File Upload</h4>
                <p className="text-sm text-muted-foreground">
                  Upload text files containing QR code data
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
