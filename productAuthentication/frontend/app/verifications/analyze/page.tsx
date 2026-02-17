import type { Metadata } from "next"
import ProtectedRoute from "@/components/auth/protected-route"
import CounterfeitAnalysisComponent from "@/components/verifications/counterfeit-analysis"

export const metadata: Metadata = {
  title: "Counterfeit Analysis",
  description: "Comprehensive product authenticity analysis",
}

export default function CounterfeitAnalysisPage() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8">
        <CounterfeitAnalysisComponent />
      </div>
    </ProtectedRoute>
  )
}
