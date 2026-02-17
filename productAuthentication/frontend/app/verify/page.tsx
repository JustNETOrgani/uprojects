"use client"

import { useState } from "react"
import { QRVerificationForm } from "@/components/products/qr-verification-form"
import { VerificationResultDisplay } from "@/components/products/verification-result"
import { ProtectedRoute } from "@/components/auth/protected-route"
import type { VerificationResult } from "@/lib/api"
import { Card, CardContent } from "@/components/ui/card"
import { QrCode, Shield, CheckCircle } from "lucide-react"

export default function VerifyPage() {
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null)

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Product Verification</h1>
          <p className="text-muted-foreground">
            Verify the authenticity of products using QR codes and blockchain technology
          </p>
        </div>

        {/* How it Works */}
        {!verificationResult && (
          <Card className="mb-8 bg-muted/50">
            <CardContent className="pt-6">
              <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                How Product Verification Works
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-start gap-3">
                  <QrCode className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">1. Scan QR Code</p>
                    <p className="text-muted-foreground">Scan or enter the QR code data from the product</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Shield className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">2. Blockchain Check</p>
                    <p className="text-muted-foreground">Verify against blockchain records for authenticity</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-foreground">3. Get Results</p>
                    <p className="text-muted-foreground">Receive detailed verification results and product info</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Verification Form */}
        {!verificationResult && <QRVerificationForm onVerificationResult={setVerificationResult} />}

        {/* Verification Results */}
        {verificationResult && (
          <div className="space-y-6">
            <VerificationResultDisplay result={verificationResult} />

            {/* New Verification Button */}
            <div className="text-center">
              <button
                onClick={() => setVerificationResult(null)}
                className="text-primary hover:text-primary/80 font-medium"
              >
                Verify Another Product
              </button>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  )
}
