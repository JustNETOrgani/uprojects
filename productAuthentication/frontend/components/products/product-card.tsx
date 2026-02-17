"use client"

import type { Product } from "@/lib/api"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { MoreHorizontal, Eye, Edit, Trash2, QrCode, Shield } from "lucide-react"
import { format } from "date-fns"
import { useRouter } from "next/navigation"

interface ProductCardProps {
  product: Product
  isManufacturer?: boolean
  onView?: (product: Product) => void
  onEdit?: (product: Product) => void
  onDelete?: (product: Product) => void
  onGenerateQR?: (product: Product) => void
}

export function ProductCard({
  product,
  isManufacturer = false,
  onView,
  onEdit,
  onDelete,
  onGenerateQR,
}: ProductCardProps) {
  const router = useRouter()

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

  const handleCardClick = () => {
    router.push(`/products/${product.id}`)
  }

  return (
    <Card
      className="group hover:shadow-lg transition-all duration-200 border-border bg-card cursor-pointer"
      onClick={handleCardClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <h3 className="font-semibold text-card-foreground line-clamp-1">{product.product_name}</h3>
            <Badge className={getCategoryColor(product.category)}>{product.category}</Badge>
          </div>
          {isManufacturer && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    onView?.(product)
                  }}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  View Details
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    onEdit?.(product)
                  }}
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Product
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    onGenerateQR?.(product)
                  }}
                >
                  <QrCode className="h-4 w-4 mr-2" />
                  Generate QR
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete?.(product)
                  }}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </CardHeader>

      <CardContent className="pb-3">
        <div className="space-y-2 text-sm text-muted-foreground">
          <div className="flex justify-between">
            <span>Batch:</span>
            <span className="font-medium text-card-foreground">{product.batch_number}</span>
          </div>
          <div className="flex justify-between">
            <span>Manufactured:</span>
            <span className="font-medium text-card-foreground">
              {format(new Date(product.manufacturing_date), "MMM dd, yyyy")}
            </span>
          </div>
          {product.blockchain_id && (
            <div className="flex items-center gap-1 text-primary">
              <Shield className="h-3 w-3" />
              <span className="text-xs font-medium">Blockchain Verified</span>
            </div>
          )}
        </div>
        {product.product_description && (
          <p className="text-sm text-muted-foreground mt-3 line-clamp-2">{product.product_description}</p>
        )}
      </CardContent>

      <CardFooter className="pt-0">
        <div className="flex items-center justify-between w-full text-xs text-muted-foreground">
          <span>Created {format(new Date(product.created_at), "MMM dd")}</span>
          <div className="flex items-center gap-1">
            <div className={`w-2 h-2 rounded-full ${product.is_active ? "bg-primary" : "bg-muted-foreground"}`} />
            <span>{product.is_active ? "Active" : "Inactive"}</span>
          </div>
        </div>
      </CardFooter>
    </Card>
  )
}
