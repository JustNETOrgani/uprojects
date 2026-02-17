"use client"

import { useAuth } from "@/contexts/auth-context"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Shield, BarChart3, Activity, Crown, Package, Search } from "lucide-react"

export function Navbar() {
  const { user, isAuthenticated, logout, isLoading } = useAuth()
  const router = useRouter()

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
  }

  if (isLoading) {
    return (
      <nav className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-sans font-bold text-foreground">
                AuthApp
              </Link>
            </div>
            <div className="animate-pulse">
              <div className="w-8 h-8 bg-muted rounded-full"></div>
            </div>
          </div>
        </div>
      </nav>
    )
  }

  return (
    <nav className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <div className="flex items-center space-x-8">
            <Link href="/" className="text-xl font-sans font-bold text-foreground">
              <Shield className="w-6 h-6 inline-block mr-2 text-primary" />
              SecureAuth
            </Link>

            {isAuthenticated && (
              <div className="hidden md:flex items-center space-x-6">
                <Link
                  href="/products"
                  className="text-muted-foreground hover:text-foreground transition-colors font-medium flex items-center gap-1"
                >
                  <Package className="w-4 h-4" />
                  Products
                </Link>
                <Link
                  href="/verify"
                  className="text-muted-foreground hover:text-foreground transition-colors font-medium flex items-center gap-1"
                >
                  <Search className="w-4 h-4" />
                  Verify
                </Link>
                <Link
                  href="/verifications"
                  className="text-muted-foreground hover:text-foreground transition-colors font-medium flex items-center gap-1"
                >
                  <Activity className="w-4 h-4" />
                  Verifications
                </Link>
                <Link
                  href="/blockchain"
                  className="text-muted-foreground hover:text-foreground transition-colors font-medium flex items-center gap-1"
                >
                  <Shield className="w-4 h-4" />
                  Blockchain
                </Link>
                <Link
                  href="/analytics"
                  className="text-muted-foreground hover:text-foreground transition-colors font-medium flex items-center gap-1"
                >
                  <BarChart3 className="w-4 h-4" />
                  Analytics
                </Link>
                {user?.role === "ADMIN" && (
                  <Link
                    href="/admin"
                    className="text-muted-foreground hover:text-foreground transition-colors font-medium flex items-center gap-1"
                  >
                    <Crown className="w-4 h-4" />
                    Admin
                  </Link>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-accent text-accent-foreground">
                        {getInitials(user.full_name)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <div className="flex flex-col space-y-1 p-2">
                    <p className="text-sm font-medium leading-none">{user.full_name}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                    <p className="text-xs leading-none text-primary font-medium">{user.role}</p>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/products" className="cursor-pointer">
                      <Package className="w-4 h-4 mr-2" />
                      Products
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/verify" className="cursor-pointer">
                      <Search className="w-4 h-4 mr-2" />
                      Verify Products
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/verifications" className="cursor-pointer">
                      <Activity className="w-4 h-4 mr-2" />
                      Verifications
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/blockchain" className="cursor-pointer">
                      <Shield className="w-4 h-4 mr-2" />
                      Blockchain Status
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/analytics" className="cursor-pointer">
                      <BarChart3 className="w-4 h-4 mr-2" />
                      Analytics
                    </Link>
                  </DropdownMenuItem>
                  {user.role === "MANUFACTURER" && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link href="/products/create" className="cursor-pointer">
                          <Package className="w-4 h-4 mr-2" />
                          Create Product
                        </Link>
                      </DropdownMenuItem>
                    </>
                  )}
                  {user.role === "ADMIN" && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link href="/admin" className="cursor-pointer">
                          <Crown className="w-4 h-4 mr-2" />
                          Admin Dashboard
                        </Link>
                      </DropdownMenuItem>
                    </>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/profile" className="cursor-pointer">
                      Profile
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-destructive">
                    Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex items-center space-x-2">
                <Button asChild variant="ghost" className="text-muted-foreground hover:text-foreground">
                  <Link href="/login">Sign In</Link>
                </Button>
                <Button asChild className="bg-accent text-accent-foreground hover:bg-accent/90">
                  <Link href="/register">Sign Up</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
