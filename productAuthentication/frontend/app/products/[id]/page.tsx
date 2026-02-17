"use client"

import { ProductDetails } from "@/components/products/product-details"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { use } from "react"

interface ProductPageProps {
  params: Promise<{ id: string }>
}

export default function ProductPage({ params }: ProductPageProps) {
  const { id } = use(params)
  const productId = Number.parseInt(id, 10)

  if (isNaN(productId)) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground mb-2">Invalid Product ID</h1>
          <p className="text-muted-foreground">The product ID provided is not valid.</p>
        </div>
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8">
        <ProductDetails productId={productId} />
      </div>
    </ProtectedRoute>
  )
}
