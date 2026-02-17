"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAuth } from "@/contexts/auth-context"
import { metaMaskService } from "@/lib/metamask"

export function RegisterForm() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    full_name: "",
    role: "",
    wallet_address: "",
  })
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isConnectingWallet, setIsConnectingWallet] = useState(false)

  const { register } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    try {
      await register(formData)
      router.push("/profile")
    } catch (err: any) {
      setError(err.message || "Registration failed. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleMetaMaskConnect = async () => {
    setIsConnectingWallet(true)
    setError("")

    try {
      const account = await metaMaskService.connectWallet()
      setFormData((prev) => ({ ...prev, wallet_address: account.address }))
    } catch (err) {
      setError("Failed to connect MetaMask. Please make sure it's installed and unlocked.")
    } finally {
      setIsConnectingWallet(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-2 text-center">
          <CardTitle className="text-2xl font-sans font-semibold text-foreground">Create Your Account</CardTitle>
          <CardDescription className="text-muted-foreground font-serif">
            Join our platform and start your blockchain journey
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="full_name" className="text-sm font-medium text-foreground">
                Full Name
              </Label>
              <Input
                id="full_name"
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData((prev) => ({ ...prev, full_name: e.target.value }))}
                placeholder="Enter your full name"
                required
                className="bg-input border-border focus:ring-ring"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-foreground">
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))}
                placeholder="Enter your email address"
                required
                className="bg-input border-border focus:ring-ring"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-foreground">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData((prev) => ({ ...prev, password: e.target.value }))}
                placeholder="Create a secure password"
                required
                className="bg-input border-border focus:ring-ring"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="role" className="text-sm font-medium text-foreground">
                Role
              </Label>
              <Select
                value={formData.role}
                onValueChange={(value) => setFormData((prev) => ({ ...prev, role: value }))}
              >
                <SelectTrigger className="bg-input border-border focus:ring-ring">
                  <SelectValue placeholder="Select your role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="manufacturer">Manufacturer</SelectItem>
                  <SelectItem value="retailer">Retailer</SelectItem>
                  <SelectItem value="distributor">Distributor</SelectItem>
                  <SelectItem value="consumer">Consumer</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="wallet_address" className="text-sm font-medium text-foreground">
                Wallet Address
              </Label>
              <div className="flex gap-2">
                <Input
                  id="wallet_address"
                  type="text"
                  value={formData.wallet_address}
                  onChange={(e) => setFormData((prev) => ({ ...prev, wallet_address: e.target.value }))}
                  placeholder="Enter wallet address or connect MetaMask"
                  required
                  className="bg-input border-border focus:ring-ring"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleMetaMaskConnect}
                  disabled={isConnectingWallet}
                  className="shrink-0 bg-accent text-accent-foreground hover:bg-accent/90 border-accent"
                >
                  {isConnectingWallet ? "..." : "Connect"}
                </Button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-medium"
              disabled={isLoading}
            >
              {isLoading ? "Creating account..." : "Create Account"}
            </Button>
          </form>

          <div className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="text-accent hover:text-accent/80 font-medium">
              Sign in
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
