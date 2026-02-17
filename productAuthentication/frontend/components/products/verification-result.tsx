"use client"

import type { VerificationResult } from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { CheckCircle, XCircle, Shield, Package, User, Calendar, MapPin, FileText, Hash } from "lucide-react"
import { format } from "date-fns"

interface VerificationResultProps {
  result: VerificationResult
}

export function VerificationResultDisplay({ result }: VerificationResultProps) {
  const isAuthentic = result.verification.is_authentic

  return (
    <div className="space-y-6">
      {/* Verification Status */}
      <Card
        className={`border-2 ${isAuthentic ? "border-primary bg-primary/5" : "border-destructive bg-destructive/5"}`}
      >
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            {isAuthentic ? (
              <CheckCircle className="h-6 w-6 text-primary" />
            ) : (
              <XCircle className="h-6 w-6 text-destructive" />
            )}
            <div>
              <div className={`text-xl ${isAuthentic ? "text-primary" : "text-destructive"}`}>
                {isAuthentic ? "Product Verified" : "Verification Failed"}
              </div>
              <div className="text-sm text-muted-foreground font-normal">
                {isAuthentic
                  ? "This product has been verified as authentic"
                  : "This product could not be verified as authentic"}
              </div>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Badge variant={isAuthentic ? "default" : "destructive"} className="text-sm">
              {isAuthentic ? "Authentic" : "Not Verified"}
            </Badge>
            {result.blockchain_verified && (
              <Badge variant="secondary" className="text-sm bg-accent text-accent-foreground">
                <Shield className="h-3 w-3 mr-1" />
                Blockchain Verified
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

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
              <p className="text-foreground font-medium">{result.product.product_name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Category</label>
              <p className="text-foreground capitalize">{result.product.category}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Batch Number</label>
              <p className="text-foreground font-mono">{result.product.batch_number}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Manufacturing Date</label>
              <p className="text-foreground">{format(new Date(result.product.manufacturing_date), "PPP")}</p>
            </div>
          </div>

          {result.product.product_description && (
            <>
              <Separator />
              <div>
                <label className="text-sm font-medium text-muted-foreground">Description</label>
                <p className="text-foreground mt-1">{result.product.product_description}</p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Manufacturer Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5 text-primary" />
            Manufacturer Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">Company Name</label>
              <p className="text-foreground font-medium">{result.product.manufacturer.full_name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">Contact Email</label>
              <p className="text-foreground">{result.product.manufacturer.email}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Verification Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Verification Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                Verification Date
              </label>
              <p className="text-foreground">{format(new Date(result.verification.verification_date), "PPP 'at' p")}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                Location
              </label>
              <p className="text-foreground">{result.verification.location}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                <Hash className="h-3 w-3" />
                Verification ID
              </label>
              <p className="text-foreground font-mono text-sm">{result.verification.id}</p>
            </div>
            {result.blockchain_verification_id && (
              <div>
                <label className="text-sm font-medium text-muted-foreground flex items-center gap-1">
                  <Shield className="h-3 w-3" />
                  Blockchain ID
                </label>
                <p className="text-foreground font-mono text-sm">{result.blockchain_verification_id}</p>
              </div>
            )}
          </div>

          {result.verification.notes && (
            <>
              <Separator />
              <div>
                <label className="text-sm font-medium text-muted-foreground">Notes</label>
                <p className="text-foreground mt-1">{result.verification.notes}</p>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
