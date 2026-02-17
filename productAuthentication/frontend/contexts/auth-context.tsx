"use client"

import type React from "react"
import { createContext, useContext, useEffect, useState } from "react"
import { apiClient, type User, type LoginRequest, type RegisterRequest } from "@/lib/api"

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginRequest) => Promise<void>
  register: (userData: RegisterRequest) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = !!user

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem("access_token")
    if (token) {
      loadUser()
    } else {
      setIsLoading(false)
    }
  }, [])

  const loadUser = async () => {
    try {
      const userData = await apiClient.getCurrentUser()
      setUser(userData)
    } catch (error) {
      // Token might be expired, clear it
      localStorage.removeItem("access_token")
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (credentials: LoginRequest) => {
    setIsLoading(true)
    try {
      const response = await apiClient.login(credentials)
      localStorage.setItem("access_token", response.access_token)
      await loadUser()
    } catch (error) {
      setIsLoading(false)
      throw error
    }
  }

  const register = async (userData: RegisterRequest) => {
    setIsLoading(true)
    try {
      await apiClient.register(userData)
      // After registration, automatically log in
      await login({ username: userData.email, password: userData.password })
    } catch (error) {
      setIsLoading(false)
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem("access_token")
    setUser(null)
  }

  const refreshToken = async () => {
    try {
      const response = await apiClient.refreshToken()
      localStorage.setItem("access_token", response.access_token)
    } catch (error) {
      logout()
      throw error
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        refreshToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
