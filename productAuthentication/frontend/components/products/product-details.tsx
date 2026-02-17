"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/auth-context"
import { apiClient, type Product } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import {
  ArrowLeft,
  Package,
  Hash,
  Shield,
  QrCode,
  Edit,
  Trash2,
  MoreHorizontal,
  Download,
  Eye,
  EyeOff,
} from "lucide-react"
import { format } from "date-fns"
import { toast } from "@/hooks/use-toast"

interface ProductDetailsProps {
  productId: number
}

export function ProductDetails({ productId }: ProductDetailsProps) {
  const { user } = useAuth()
  const router = useRouter()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [qrImageError, setQrImageError] = useState(false)

  const isManufacturer = user?.role === "manufacturer"
  const isOwner = product && user && product.manufacturer_id === user.id

  useEffect(() => {
    loadProduct()
  }, [productId])

  const loadProduct = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getProduct(productId)
      setProduct(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load product details",
        variant: "destructive",
      })
      router.push("/products")
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateQR = async () => {
    if (!product) return

    try {
      setActionLoading("qr")
      const result = await apiClient.generateQRCode(product.id)
      toast({
        title: "Success",
        description: "QR code generated successfully",
      })
      // Update product with new QR code path
      setProduct({ ...product, qr_code_path: result.qr_code_path })
      setQrImageError(false) // Reset error state on new generation
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate QR code",
        variant: "destructive",
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleToggleStatus = async () => {
    if (!product) return

    try {
      setActionLoading("status")
      const updatedProduct = await apiClient.updateProduct(product.id, {
        is_active: !product.is_active,
      })
      setProduct(updatedProduct)
      toast({
        title: "Success",
        description: `Product ${updatedProduct.is_active ? "activated" : "deactivated"} successfully`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update product status",
        variant: "destructive",
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async () => {
    if (!product) return

    if (!confirm(`Are you sure you want to delete "${product.product_name}"? This action cannot be undone.`)) {
      return
    }

    try {
      setActionLoading("delete")
      await apiClient.deleteProduct(product.id)
      toast({
        title: "Success",
        description: "Product deleted successfully",
      })
      router.push("/products")
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete product",
        variant: "destructive",
      })
      setActionLoading(null)
    }
  }

  const handleDownloadQR = () => {
    if (!product?.qr_code_path) return
    
    // Create a temporary anchor element to trigger download
    const link = document.createElement('a')
    link.href = product.qr_code_path
    link.download = `${product.product_name}-qr-code.png`
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleQrImageError = () => {
    setQrImageError(true)
  }

  const getCategoryColor = (category: string) => {
    const colors = {
      electronics: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
      clothing: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
      food: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
      medicine: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
      automotive: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300",
      other: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
    }
    return colors[category as keyof typeof colors] || colors.other
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading product details...</p>
        </div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="text-center py-12">
        <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-foreground mb-2">Product not found</h3>
        <p className="text-muted-foreground mb-4">The product you're looking for doesn't exist or has been removed.</p>
        <Button onClick={() => router.push("/products")} variant="outline">
          Back to Products
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()} className="p-2">
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">{product.product_name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={getCategoryColor(product.category)}>{product.category}</Badge>
              <Badge variant={product.is_active ? "default" : "secondary"}>
                {product.is_active ? "Active" : "Inactive"}
              </Badge>
              {product.blockchain_id && (
                <Badge variant="secondary" className="bg-accent text-accent-foreground">
                  <Shield className="h-3 w-3 mr-1" />
                  Blockchain Verified
                </Badge>
              )}
            </div>
          </div>
        </div>

        {isOwner && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <MoreHorizontal className="h-4 w-4 mr-2" />
                Actions
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => router.push(`/products/${product.id}/edit`)}>
                <Edit className="h-4 w-4 mr-2" />
                Edit Product
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleGenerateQR} disabled={actionLoading === "qr"}>
                <QrCode className="h-4 w-4 mr-2" />
                {actionLoading === "qr" ? "Generating..." : "Generate QR Code"}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleToggleStatus} disabled={actionLoading === "status"}>
                {product.is_active ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                {actionLoading === "status"
                  ? "Updating..."
                  : product.is_active
                    ? "Deactivate Product"
                    : "Activate Product"}
              </DropdownMenuItem>
              <Separator />
              <DropdownMenuItem
                onClick={handleDelete}
                disabled={actionLoading === "delete"}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                {actionLoading === "delete" ? "Deleting..." : "Delete Product"}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Product Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5 text-primary" />
                Product Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Product Name</label>
                  <p className="text-foreground font-medium">{product.product_name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Category</label>
                  <p className="text-foreground capitalize">{product.category}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Batch Number</label>
                  <p className="text-foreground font-mono">{product.batch_number}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Manufacturing Date</label>
                  <p className="text-foreground">{format(new Date(product.manufacturing_date), "PPP")}</p>
                </div>
              </div>

              {product.product_description && (
                <>
                  <Separator />
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Description</label>
                    <p className="text-foreground mt-1">{product.product_description}</p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Technical Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Hash className="h-5 w-5 text-primary" />
                Technical Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Product ID</label>
                  <p className="text-foreground font-mono">{product.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">QR Code Hash</label>
                  <p className="text-foreground font-mono text-sm break-all">{product.qr_code_hash}</p>
                </div>
                {product.blockchain_id && (
                  <div>
                    <label className="text-sm font-medium text-muted-foreground">Blockchain ID</label>
                    <p className="text-foreground font-mono">{product.blockchain_id}</p>
                  </div>
                )}
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Created</label>
                  <p className="text-foreground">{format(new Date(product.created_at), "PPP 'at' p")}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* QR Code */}
          {product.qr_code_path && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <QrCode className="h-5 w-5 text-primary" />
                  QR Code
                </CardTitle>
              </CardHeader>
              <CardContent className="text-center space-y-4">
                <div className="bg-white p-4 rounded-lg inline-block border">
                  {!qrImageError ? (
                    <img
                      src={product.qr_code_path}
                      alt={`QR Code for ${product.product_name}`}
                      className="w-32 h-32 object-contain"
                      onError={handleQrImageError}
                      onLoad={() => setQrImageError(false)}
                    />
                  ) : (
                    <div className="w-32 h-32 bg-gray-200 rounded flex items-center justify-center">
                      <QrCode className="h-16 w-16 text-gray-400" />
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full bg-transparent"
                    onClick={handleDownloadQR}
                    disabled={qrImageError}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download QR Code
                  </Button>
                  {isOwner && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full bg-transparent"
                      onClick={handleGenerateQR}
                      disabled={actionLoading === "qr"}
                    >
                      <QrCode className="h-4 w-4 mr-2" />
                      {actionLoading === "qr" ? "Generating..." : "Regenerate QR"}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Status Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Product Status</span>
                <Badge variant={product.is_active ? "default" : "secondary"}>
                  {product.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Blockchain</span>
                <Badge variant={product.blockchain_id ? "default" : "secondary"}>
                  {product.blockchain_id ? "Verified" : "Not Verified"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">QR Code</span>
                <Badge variant={product.qr_code_path ? "default" : "secondary"}>
                  {product.qr_code_path ? "Generated" : "Not Generated"}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
