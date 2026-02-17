"use client"

import { ProductDashboard } from "@/components/products/product-dashboard"
import { ProtectedRoute } from "@/components/auth/protected-route"

export default function ProductsPage() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8">
        <ProductDashboard />
      </div>
    </ProtectedRoute>
  )
}
