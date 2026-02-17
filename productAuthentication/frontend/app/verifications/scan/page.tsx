import type { Metadata } from "next"
import ProtectedRoute from "@/components/auth/protected-route"
import QRScanner from "@/components/verifications/qr-scanner"

export const metadata: Metadata = {
  title: "QR Code Scanner",
  description: "Scan QR codes to verify product authenticity",
}

export default function QRScannerPage() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8">
        <QRScanner />
      </div>
    </ProtectedRoute>
  )
}
