"use client"

import { useState, useRef, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { apiClient, type VerificationResult } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { QrCode, MapPin, Scan, Upload, X, Camera, RotateCcw } from "lucide-react"
import { toast } from "@/hooks/use-toast"


import QrScanner from 'qr-scanner'

const verificationFormSchema = z.object({
  qr_data: z.string().min(1, "QR code data is required"),
  location: z.string().max(100, "Location must be less than 100 characters").optional(),
  notes: z.string().max(500, "Notes must be less than 500 characters").optional(),
})

type VerificationFormValues = z.infer<typeof verificationFormSchema>

interface QRVerificationFormProps {
  onVerificationResult: (result: VerificationResult | null) => void
}

export function QRVerificationForm({ onVerificationResult }: QRVerificationFormProps) {
  const [isVerifying, setIsVerifying] = useState(false)
  const [isProcessingImage, setIsProcessingImage] = useState(false)
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [isScanning, setIsScanning] = useState(false)
  const [availableCameras, setAvailableCameras] = useState<MediaDeviceInfo[]>([])
  const [currentCameraId, setCurrentCameraId] = useState<string>('')
  const [hasPermission, setHasPermission] = useState<boolean | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const qrScannerRef = useRef<QrScanner | null>(null)

  const form = useForm<VerificationFormValues>({
    resolver: zodResolver(verificationFormSchema),
    defaultValues: {
      qr_data: "",
      location: "",
      notes: "",
    },
  })

  // Initialize camera permissions and available cameras
  useEffect(() => {
    const initializeCameras = async () => {
      try {
        // Check if QR Scanner is supported
        const hasCamera = await QrScanner.hasCamera()
        if (!hasCamera) {
          console.log('No camera available')
          return
        }

        // Request camera permission
        const stream = await navigator.mediaDevices.getUserMedia({ video: true })
        stream.getTracks().forEach(track => track.stop()) // Stop the test stream
        setHasPermission(true)

        // Get available cameras
        const devices = await navigator.mediaDevices.enumerateDevices()
        const cameras = devices.filter(device => device.kind === 'videoinput')
        setAvailableCameras(cameras)
        
        // Set default camera (prefer back camera)
        const backCamera = cameras.find(camera => 
          camera.label.toLowerCase().includes('back') || 
          camera.label.toLowerCase().includes('rear') ||
          camera.label.toLowerCase().includes('environment')
        )
        setCurrentCameraId(backCamera?.deviceId || cameras[0]?.deviceId || '')
        
      } catch (error) {
        console.error('Camera initialization error:', error)
        setHasPermission(false)
        toast({
          title: "Camera Permission Required",
          description: "Please allow camera access to use QR scanning feature",
          variant: "destructive",
        })
      }
    }

    initializeCameras()
  }, [])

  const onSubmit = async (values: VerificationFormValues) => {
    try {
      setIsVerifying(true)
      onVerificationResult(null) 

      const result = await apiClient.verifyProduct({
        qr_data: values.qr_data,
        location: values.location || "Unknown",
        notes: values.notes || "",
      })

      onVerificationResult(result)

      toast({
        title: "Verification Complete",
        description: result.verification.is_authentic ? "Product verified as authentic" : "Product verification failed",
        variant: result.verification.is_authentic ? "default" : "destructive",
      })
    } catch (error) {
      toast({
        title: "Verification Failed",
        description: error instanceof Error ? error.message : "Failed to verify product",
        variant: "destructive",
      })
      onVerificationResult(null)
    } finally {
      setIsVerifying(false)
    }
  }

  const processQRImage = async (file: File) => {
    try {
      setIsProcessingImage(true)
      
      // Create image URL for preview
      const imageUrl = URL.createObjectURL(file)
      setUploadedImage(imageUrl)

      // Process QR code from image
      const result = await QrScanner.scanImage(file, {
        returnDetailedScanResult: true,
      })

      if (result && result.data) {
        form.setValue('qr_data', result.data)
        toast({
          title: "QR Code Detected",
          description: "QR code data has been extracted from the image",
        })
      }
    } catch (error) {
      console.error('QR scanning error:', error)
      toast({
        title: "QR Code Not Found",
        description: "Could not detect a QR code in the uploaded image. Please try a clearer image or enter the data manually.",
        variant: "destructive",
      })
    } finally {
      setIsProcessingImage(false)
    }
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast({
          title: "Invalid File Type",
          description: "Please upload an image file (PNG, JPG, etc.)",
          variant: "destructive",
        })
        return
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: "File Too Large",
          description: "Please upload an image smaller than 10MB",
          variant: "destructive",
        })
        return
      }

      processQRImage(file)
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const removeUploadedImage = () => {
    if (uploadedImage) {
      URL.revokeObjectURL(uploadedImage)
      setUploadedImage(null)
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const startCameraScanning = async () => {
    try {
      setIsScanning(true)
      
      // Wait a bit for the video element to be rendered
      await new Promise(resolve => setTimeout(resolve, 100))
      
      if (!videoRef.current) {
        setIsScanning(false)
        toast({
          title: "Camera Error",
          description: "Video element not ready. Please try again.",
          variant: "destructive",
        })
        return
      }

      if (!currentCameraId && availableCameras.length === 0) {
        setIsScanning(false)
        toast({
          title: "Camera Error",
          description: "No camera available on this device.",
          variant: "destructive",
        })
        return
      }

      // Stop any existing scanner
      if (qrScannerRef.current) {
        qrScannerRef.current.stop()
        qrScannerRef.current.destroy()
      }

      // Use currentCameraId or fallback to first available camera
      const cameraToUse = currentCameraId || availableCameras[0]?.deviceId

      // Initialize QR Scanner with specific camera
      qrScannerRef.current = new QrScanner(
        videoRef.current,
        (result) => {
          form.setValue('qr_data', result.data)
          stopCameraScanning()
          toast({
            title: "QR Code Scanned",
            description: "QR code has been successfully scanned from camera",
          })
        },
        {
          returnDetailedScanResult: true,
          highlightScanRegion: true,
          highlightCodeOutline: true,
          preferredCamera: cameraToUse,
        }
      )

      await qrScannerRef.current.start()
      
      toast({
        title: "Camera Started",
        description: "Point your camera at a QR code to scan",
      })
    } catch (error) {
      console.error('Camera scanning error:', error)
      setIsScanning(false)
      
      let errorMessage = "Could not start camera scanning."
      
      if (error instanceof Error) {
        if (error.name === 'NotAllowedError') {
          errorMessage = "Camera permission denied. Please allow camera access and try again."
        } else if (error.name === 'NotFoundError') {
          errorMessage = "No camera found on this device."
        } else if (error.name === 'NotSupportedError') {
          errorMessage = "Camera is not supported in this browser."
        } else if (error.message.includes('Video element')) {
          errorMessage = "Camera interface not ready. Please try again."
        }
      }
      
      toast({
        title: "Camera Error",
        description: errorMessage,
        variant: "destructive",
      })
    }
  }

  const stopCameraScanning = () => {
    if (qrScannerRef.current) {
      qrScannerRef.current.stop()
      qrScannerRef.current.destroy()
      qrScannerRef.current = null
    }
    setIsScanning(false)
  }

  const switchCamera = async () => {
    if (availableCameras.length <= 1) return

    const currentIndex = availableCameras.findIndex(camera => camera.deviceId === currentCameraId)
    const nextIndex = (currentIndex + 1) % availableCameras.length
    const nextCamera = availableCameras[nextIndex]
    
    setCurrentCameraId(nextCamera.deviceId)
    
    // If currently scanning, restart with new camera
    if (isScanning && qrScannerRef.current) {
      try {
        stopCameraScanning()
        // Wait for cleanup to complete
        await new Promise(resolve => setTimeout(resolve, 200))
        // Start with new camera
        await startCameraScanning()
      } catch (error) {
        console.error('Camera switch error:', error)
        toast({
          title: "Camera Switch Error",
          description: "Failed to switch camera. Please try again.",
          variant: "destructive",
        })
      }
    }
    
    toast({
      title: "Camera Switched",
      description: `Switched to ${getCameraLabel(nextCamera)}`,
    })
  }

  const getCameraLabel = (camera: MediaDeviceInfo) => {
    if (camera.label) {
      // Try to determine if it's front or back camera
      const label = camera.label.toLowerCase()
      if (label.includes('back') || label.includes('rear') || label.includes('environment')) {
        return 'Back Camera'
      } else if (label.includes('front') || label.includes('user') || label.includes('facing')) {
        return 'Front Camera'
      }
      return camera.label
    }
    return `Camera ${availableCameras.indexOf(camera) + 1}`
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCameraScanning()
    }
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <QrCode className="h-5 w-5 text-primary" />
          Verify Product Authenticity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* QR Code Data Input */}
            <FormField
              control={form.control}
              name="qr_data"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>QR Code Data *</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="QR code data will appear here after scanning or upload" 
                      {...field} 
                    />
                  </FormControl>
                  <FormDescription>
                    The QR code data will be automatically filled when you scan or upload an image
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* QR Code Input Methods */}
            <div className="space-y-4">
              <div className="flex gap-2">
                {/* Upload Image Button */}
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleUploadClick}
                  disabled={isProcessingImage || isScanning}
                  className="flex-1"
                >
                  {isProcessingImage ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload QR Image
                    </>
                  )}
                </Button>

                {/* Camera Scan Button */}
                <Button
                  type="button"
                  variant="outline"
                  onClick={isScanning ? stopCameraScanning : startCameraScanning}
                  disabled={hasPermission === false || (availableCameras.length === 0 && hasPermission !== null)}
                  className="flex-1"
                >
                  {isScanning ? (
                    <>
                      <X className="h-4 w-4 mr-2" />
                      Stop Scanning
                    </>
                  ) : (
                    <>
                      <Camera className="h-4 w-4 mr-2" />
                      {hasPermission === false ? 'No Camera Access' : 
                       hasPermission === null ? 'Loading...' : 
                       availableCameras.length === 0 ? 'No Camera Found' : 'Scan with Camera'}
                    </>
                  )}
                </Button>
              </div>

              {/* Camera Switch Button - Only show if scanning and multiple cameras available */}
              {isScanning && availableCameras.length > 1 && (
                <div className="flex justify-center">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={switchCamera}
                    className="gap-2"
                  >
                    <RotateCcw className="h-4 w-4" />
                    Switch to {getCameraLabel(availableCameras.find(camera => camera.deviceId !== currentCameraId) || availableCameras[0])}
                  </Button>
                </div>
              )}

              {/* Camera Permission Message */}
              {hasPermission === false && (
                <div className="text-sm text-muted-foreground text-center p-3 bg-muted rounded-lg">
                  Camera access is required for QR scanning. Please allow camera permissions in your browser settings.
                </div>
              )}

              {/* Hidden File Input */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleImageUpload}
                accept="image/*"
                className="hidden"
              />

              {/* Uploaded Image Preview */}
              {uploadedImage && (
                <div className="relative">
                  <img
                    src={uploadedImage}
                    alt="Uploaded QR code"
                    className="max-w-full h-48 object-contain border rounded-lg"
                  />
                  <Button
                    type="button"
                    variant="destructive"
                    size="sm"
                    onClick={removeUploadedImage}
                    className="absolute top-2 right-2"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}

              {/* Camera Video Preview */}
              {isScanning && (
                <div className="relative bg-black rounded-lg overflow-hidden">
                  <video
                    ref={videoRef}
                    className="w-full max-w-md h-64 object-cover mx-auto"
                    playsInline
                    muted
                  />
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="border-2 border-primary border-dashed w-48 h-48 rounded-lg opacity-75"></div>
                  </div>
                  {/* Current Camera Info */}
                  <div className="absolute top-2 left-2 bg-black/50 text-white text-xs px-2 py-1 rounded">
                    {currentCameraId && availableCameras.length > 0 && 
                      getCameraLabel(availableCameras.find(camera => camera.deviceId === currentCameraId) || availableCameras[0])
                    }
                  </div>
                  {/* Instructions */}
                  <div className="absolute bottom-2 left-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded text-center">
                    Position the QR code within the dashed area
                  </div>
                </div>
              )}
            </div>

            {/* Location */}
            <FormField
              control={form.control}
              name="location"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Verification Location</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input placeholder="e.g., Store Name, City" className="pl-10" {...field} />
                    </div>
                  </FormControl>
                  <FormDescription>Where are you verifying this product? (Optional)</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Notes */}
            <FormField
              control={form.control}
              name="notes"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Verification Notes</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Any additional notes about this verification (optional)"
                      className="min-h-[80px]"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>Additional context or observations about the product</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Submit Button */}
            <Button 
              type="submit" 
              disabled={isVerifying || isProcessingImage || isScanning} 
              className="w-full bg-primary hover:bg-primary/90"
            >
              {isVerifying ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Verifying Product...
                </>
              ) : (
                <>
                  <QrCode className="h-4 w-4 mr-2" />
                  Verify Product
                </>
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
