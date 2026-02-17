"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { apiClient, ProductCategory } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { CalendarIcon, Package, ArrowLeft } from "lucide-react"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import { toast } from "@/hooks/use-toast"

const productFormSchema = z.object({
  product_name: z.string().min(1, "Product name is required").max(100, "Product name must be less than 100 characters"),
  product_description: z.string().max(500, "Description must be less than 500 characters").optional(),
  manufacturing_date: z.date({
    required_error: "Manufacturing date is required",
  }),
  batch_number: z.string().min(1, "Batch number is required").max(50, "Batch number must be less than 50 characters"),
  category: z.nativeEnum(ProductCategory, {
    required_error: "Please select a category",
  }),
})

type ProductFormValues = z.infer<typeof productFormSchema>

interface ProductFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

export function ProductForm({ onSuccess, onCancel }: ProductFormProps) {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<ProductFormValues>({
    resolver: zodResolver(productFormSchema),
    defaultValues: {
      product_name: "",
      product_description: "",
      batch_number: "",
      manufacturing_date: new Date(),
    },
  })

  const onSubmit = async (values: ProductFormValues) => {
    try {
      setIsSubmitting(true)

      const productData = {
        ...values,
        manufacturing_date: values.manufacturing_date.toISOString().split("T")[0], // Format as YYYY-MM-DD
      }

      const newProduct = await apiClient.createProduct(productData)

      toast({
        title: "Success",
        description: `Product "${newProduct.product_name}" created successfully`,
      })

      if (onSuccess) {
        onSuccess()
      } else {
        router.push("/products")
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create product",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    } else {
      router.back()
    }
  }

  const categoryOptions = [
    { value: ProductCategory.ELECTRONICS, label: "Electronics" },
    { value: ProductCategory.CLOTHING, label: "Clothing" },
    { value: ProductCategory.FOOD, label: "Food" },
    { value: ProductCategory.MEDICINE, label: "Medicine" },
    { value: ProductCategory.AUTOMOTIVE, label: "Automotive" },
    { value: ProductCategory.OTHER, label: "Other" },
  ]

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={handleCancel} className="p-2">
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-foreground">Create New Product</h1>
          <p className="text-muted-foreground">Add a new product to your inventory with blockchain verification</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5 text-primary" />
            Product Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Product Name */}
              <FormField
                control={form.control}
                name="product_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Product Name *</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter product name" {...field} />
                    </FormControl>
                    <FormDescription>A clear, descriptive name for your product</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Product Description */}
              <FormField
                control={form.control}
                name="product_description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Product Description</FormLabel>
                    <FormControl>
                      <Textarea placeholder="Describe your product (optional)" className="min-h-[100px]" {...field} />
                    </FormControl>
                    <FormDescription>Additional details about the product, materials, features, etc.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Batch Number */}
                <FormField
                  control={form.control}
                  name="batch_number"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Batch Number *</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., BATCH-2024-001" {...field} />
                      </FormControl>
                      <FormDescription>Unique identifier for this production batch</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Category */}
                <FormField
                  control={form.control}
                  name="category"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Category *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a category" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {categoryOptions.map((option) => (
                            <SelectItem key={option.value} value={option.value}>
                              {option.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormDescription>Product category for organization and filtering</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Manufacturing Date */}
              <FormField
                control={form.control}
                name="manufacturing_date"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Manufacturing Date *</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant="outline"
                            className={cn("w-full pl-3 text-left font-normal", !field.value && "text-muted-foreground")}
                          >
                            {field.value ? format(field.value, "PPP") : <span>Pick a date</span>}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={field.onChange}
                          disabled={(date) => date > new Date() || date < new Date("1900-01-01")}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                    <FormDescription>When this product was manufactured</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Form Actions */}
              <div className="flex flex-col sm:flex-row gap-3 pt-6">
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="bg-primary hover:bg-primary/90 flex-1 sm:flex-none"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                      Creating Product...
                    </>
                  ) : (
                    <>
                      <Package className="h-4 w-4 mr-2" />
                      Create Product
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCancel}
                  disabled={isSubmitting}
                  className="flex-1 sm:flex-none bg-transparent"
                >
                  Cancel
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card className="bg-muted/50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
            <div className="space-y-1">
              <p className="text-sm font-medium text-foreground">Blockchain Integration</p>
              <p className="text-sm text-muted-foreground">
                Your product will be automatically registered on the blockchain for authenticity verification. A unique
                QR code will be generated for easy verification by customers.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
