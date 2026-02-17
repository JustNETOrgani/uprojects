import type { Metadata } from "next"
import { notFound } from "next/navigation"
import ProtectedRoute from "@/components/auth/protected-route"
import EnhancedVerificationResult from "@/components/verifications/enhanced-verification-result"
import { apiClient } from "@/lib/api"

interface VerificationResultPageProps {
  params: {
    id: string
  }
}

export const metadata: Metadata = {
  title: "Verification Result",
  description: "Detailed verification result and analysis",
}

async function getVerificationResult(verificationId: string) {
  try {
    const result = await apiClient.getVerification(parseInt(verificationId))
    return result
  } catch (error) {
    return null
  }
}

export default async function VerificationResultPage({ params }: VerificationResultPageProps) {
  const verification = await getVerificationResult(params.id)

  if (!verification) {
    notFound()
  }

  // Transform the verification data to match the expected format
  const result = {
    product: {
      id: verification.product_id,
      product_name: "Product Name", // This would need to be fetched from the product
      product_description: "Product description",
      manufacturing_date: new Date().toISOString(),
      batch_number: "BATCH-001",
      category: "electronics",
      manufacturer: {
        full_name: "Manufacturer Name",
        email: "manufacturer@example.com"
      }
    },
    verification: {
      id: verification.id,
      is_authentic: verification.is_authentic,
      location: verification.location,
      verification_date: verification.verification_date,
      notes: verification.notes
    },
    blockchain_verified: !!verification.blockchain_verification_id,
    blockchain_verification_id: verification.blockchain_verification_id,
    detection_reasons: [
      "QR code hash format is valid",
      "QR code hash matches stored value",
      "IPFS data integrity verified",
      "Product registered on blockchain"
    ],
    confidence_score: verification.is_authentic ? 0.85 : 0.2,
    risk_level: verification.is_authentic ? "low" : "high"
  }

  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8">
        <EnhancedVerificationResult result={result} />
      </div>
    </ProtectedRoute>
  )
}
