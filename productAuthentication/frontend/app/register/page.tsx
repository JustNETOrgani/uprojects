"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { RegisterForm } from "@/components/auth/register-form"
import { useAuth } from "@/contexts/auth-context"
import { ProfileCard } from "@/components/auth/profile-card"

export default function RegisterPage() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/profile")
    }
  }, [isAuthenticated, isLoading, router])

  // Show loading or register form based on auth state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  // Only show register form if user is not authenticated
  if (!isAuthenticated) {
    return <RegisterForm />
  }

  // Return null while redirecting
  return <ProfileCard/>
}
