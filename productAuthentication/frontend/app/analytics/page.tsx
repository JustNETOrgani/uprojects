import type { Metadata } from "next"
import ProtectedRoute from "@/components/auth/protected-route"
import SimpleAnalyticsDashboard from "@/components/analytics/simple-analytics-dashboard"

export const metadata: Metadata = {
  title: "Analytics Dashboard",
  description: "Comprehensive insights into product verification and authenticity",
}

export default function AnalyticsPage() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8">
        <SimpleAnalyticsDashboard />
      </div>
    </ProtectedRoute>
  )
}
