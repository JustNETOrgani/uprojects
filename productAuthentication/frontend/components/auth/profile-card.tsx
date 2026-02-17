"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { useAuth } from "@/contexts/auth-context"
import { metaMaskService } from "@/lib/metamask"

export function ProfileCard() {
  const { user, isLoading, isAuthenticated, logout, refreshToken } = useAuth()
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [refreshMessage, setRefreshMessage] = useState("")
  const [connectedWallet, setConnectedWallet] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login")
    }
  }, [isAuthenticated, isLoading, router])

  useEffect(() => {
    // Check if MetaMask is connected
    const checkWalletConnection = async () => {
      const account = await metaMaskService.getCurrentAccount()
      setConnectedWallet(account)
    }
    checkWalletConnection()
  }, [])

  const handleRefreshToken = async () => {
    setIsRefreshing(true)
    setRefreshMessage("")

    try {
      await refreshToken()
      setRefreshMessage("Token refreshed successfully!")
      setTimeout(() => setRefreshMessage(""), 3000)
    } catch (error) {
      setRefreshMessage("Failed to refresh token. Please log in again.")
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  const handleConnectWallet = async () => {
    try {
      const account = await metaMaskService.connectWallet()
      setConnectedWallet(account.address)
    } catch (error) {
      console.error("Failed to connect wallet:", error)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const getRoleBadgeVariant = (role: string) => {
    switch (role.toLowerCase()) {
      case "manufacturer":
        return "default"
      case "retailer":
        return "secondary"
      case "distributor":
        return "outline"
      case "consumer":
        return "destructive"
      default:
        return "default"
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-background p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-sans font-bold text-foreground">Profile Dashboard</h1>
            <p className="text-muted-foreground font-serif">Manage your account and blockchain settings</p>
          </div>
          <Button
            onClick={handleLogout}
            variant="outline"
            className="border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground bg-transparent"
          >
            Sign Out
          </Button>
        </div>

        {refreshMessage && (
          <Alert className={refreshMessage.includes("successfully") ? "border-green-500" : "border-destructive"}>
            <AlertDescription>{refreshMessage}</AlertDescription>
          </Alert>
        )}

        {/* User Information Card */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl font-sans text-foreground">Account Information</CardTitle>
            <CardDescription className="text-muted-foreground font-serif">
              Your registered account details
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Full Name</label>
                <p className="text-foreground font-medium">{user.full_name}</p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Email Address</label>
                <p className="text-foreground font-medium">{user.email}</p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Role</label>
                <div>
                  <Badge variant={getRoleBadgeVariant(user.role)} className="capitalize">
                    {user.role}
                  </Badge>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Wallet Address</label>
                <p className="text-foreground font-mono text-sm break-all">{user.wallet_address}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* MetaMask Connection Card */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl font-sans text-foreground">MetaMask Connection</CardTitle>
            <CardDescription className="text-muted-foreground font-serif">
              Connect your MetaMask wallet for blockchain interactions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {connectedWallet ? (
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Connected Wallet</label>
                <p className="text-foreground font-mono text-sm break-all">{connectedWallet}</p>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-green-600">Connected</span>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-muted-foreground">No wallet connected</p>
                <Button onClick={handleConnectWallet} className="bg-accent text-accent-foreground hover:bg-accent/90">
                  Connect MetaMask
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Actions Card */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl font-sans text-foreground">Account Actions</CardTitle>
            <CardDescription className="text-muted-foreground font-serif">
              Manage your authentication and session
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                onClick={handleRefreshToken}
                disabled={isRefreshing}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {isRefreshing ? "Refreshing..." : "Refresh Token"}
              </Button>
            </div>

            <Separator />

            <div className="text-sm text-muted-foreground">
              <p>
                <strong>Last login:</strong> {new Date().toLocaleDateString()}
              </p>
              <p>
                <strong>Session status:</strong> Active
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
