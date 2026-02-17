import type { Metadata } from "next"
import ProtectedRoute from "@/components/auth/protected-route"
import AdminDashboard from "@/components/blockchain/admin-dashboard"

export const metadata: Metadata = {
  title: "Admin Dashboard",
  description: "Blockchain administration and role management",
}

export default function AdminPage() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8">
        <AdminDashboard />
      </div>
    </ProtectedRoute>
  )
}
