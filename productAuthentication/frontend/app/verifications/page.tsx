import type { Metadata } from "next"
import ProtectedRoute from "@/components/auth/protected-route"
import SimpleVerificationDashboard from "@/components/verifications/simple-verification-dashboard"

export const metadata: Metadata = {
  title: "Verification Management",
  description: "Monitor product authenticity and counterfeit detection",
}

export default function VerificationsPage() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8">
        <SimpleVerificationDashboard />
      </div>
    </ProtectedRoute>
  )
}
