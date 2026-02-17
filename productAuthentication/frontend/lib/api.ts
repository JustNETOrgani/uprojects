const API_BASE_URL = "http://localhost:8000/api/v1" //https://blockchain-anti-counterfeit.onrender.com/
const AUTH_BASE_URL = `${API_BASE_URL}/auth`
const PRODUCTS_BASE_URL = `${API_BASE_URL}/products`
const VERIFICATIONS_BASE_URL = `${API_BASE_URL}/verifications`
const BLOCKCHAIN_BASE_URL = `${API_BASE_URL}/blockchain`
const ANALYTICS_BASE_URL = `${API_BASE_URL}/analytics`

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
  role: string
  wallet_address: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface User {
  email: string
  full_name: string
  role: string
  wallet_address: string
}

export interface Product {
  id: number
  product_name: string
  product_description?: string
  manufacturing_date: string
  batch_number: string
  category: string
  qr_code_hash: string
  qr_code_path?: string
  qrcode?: {
    qr_code_path: string
    qr_code_hash: string
  }
  blockchain_id?: string
  manufacturer_id: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProductCreate {
  product_name: string
  product_description?: string
  manufacturing_date: string
  batch_number: string
  category: ProductCategory
  qr_code_hash?: string
}

export interface ProductUpdate {
  product_name?: string
  product_description?: string
  manufacturing_date?: string
  batch_number?: string
  category?: ProductCategory
  is_active?: boolean
}

export enum ProductCategory {
  ELECTRONICS = "electronics",
  CLOTHING = "clothing",
  FOOD = "food",
  MEDICINE = "medicine",
  AUTOMOTIVE = "automotive",
  OTHER = "other",
}

export interface VerifyProductRequest {
  qr_data: string
  location?: string
  notes?: string
}

export interface VerificationResult {
  product: {
    id: number
    product_name: string
    product_description?: string
    manufacturing_date: string
    batch_number: string
    category: string
    manufacturer: {
      full_name: string
      email: string
    }
  }
  verification: {
    id: number
    is_authentic: boolean
    location: string
    verification_date: string
    notes?: string
  }
  blockchain_verified: boolean
  blockchain_verification_id?: string
  detection_reasons: string[]
  confidence_score: number
  risk_level: string
}

export interface QRCodeResponse {
  qr_code_path: string
  qr_code_url: string
  qr_hash: string
}

export interface Verification {
  id: number
  product_id: number
  verifier_id: number
  location: string
  notes?: string
  is_authentic: boolean
  verification_date: string
  blockchain_verification_id?: string
  // Additional fields from verification response
  detection_reasons?: string[]
  confidence_score?: number
  risk_level?: string
  blockchain_verified?: boolean
}

export interface VerificationCreate {
  product_id: number
  location: string
  notes?: string
}

export interface CounterfeitAnalysis {
  product_id: number
  product_name: string
  manufacturer_id: number
  detection_result: {
    is_authentic: boolean
    detection_reasons: string[]
    confidence_score: number
  }
  blockchain_analysis: {
    blockchain_verification: boolean
    verification_result: boolean
    transaction_hash?: string
    block_number?: number
    error?: string
  }
  pattern_analysis: {
    total_verifications: number
    authentic_verifications: number
    counterfeit_verifications: number
    verification_frequency: string
    suspicious_patterns: string[]
  }
  risk_assessment: {
    risk_score: number
    risk_level: string
    recommendation: string
  }
  analysis_timestamp: string
}

export interface BlockchainStatus {
  network: string
  chain_id: number
  latest_block: number
  contract_address: string
  connected: boolean
}

export interface BlockchainProduct {
  id: number
  productName: string
  productDescription: string
  manufacturingDate: number
  batchNumber: string
  category: string
  qrCodeHash: string
  manufacturer: string
  isActive: boolean
  createdAt: number
}

export interface GrantRoleRequest {
  role: string
  account: string
}

export interface BlockchainVerificationRequest {
  location: string
  notes?: string
}

export interface AnalyticsData {
  total_products: number
  total_verifications: number
  authentic_products: number
  counterfeit_products: number
  verification_trends: {
    date: string
    count: number
  }[]
  category_distribution: {
    category: string
    count: number
  }[]
  manufacturer_stats: {
    manufacturer_name: string
    product_count: number
    verification_count: number
  }[]
}

class ApiClient {
  
  private getAuthHeaders() {
    const token = localStorage.getItem("access_token")
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        username: credentials.username,
        password: credentials.password,
      }),
    })

    console.log({ response })

    if (!response.ok) {
      throw new Error("Login failed")
    }

    return response.json()
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Registration failed")
    }

    return response.json()
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch user data")
    }

    return response.json()
  }

  async refreshToken(): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Token refresh failed")
    }

    return response.json()
  }

  async createProduct(productData: ProductCreate): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/products`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(productData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to create product")
    }

    return response.json()
  }

  async getProducts(skip = 0, limit = 100): Promise<Product[]> {
    const response = await fetch(`${API_BASE_URL}/products/?skip=${skip}&limit=${limit}`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch products")
    }

    return response.json()
  }

  async getMyProducts(): Promise<Product[]> {
    const response = await fetch(`${API_BASE_URL}/products`, {
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch your products")
    }

    return response.json()
  }

  async getProduct(productId: number): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch product")
    }

    return response.json()
  }

  async getProductByQRCode(qrCodeHash: string): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/products/qr/${qrCodeHash}`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch product by QR code")
    }

    return response.json()
  }

  async updateProduct(productId: number, productData: ProductUpdate): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(productData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to update product")
    }

    return response.json()
  }

  async deleteProduct(productId: number): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`, {
      method: "DELETE",
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to delete product")
    }

    return response.json()
  }

  async generateQRCode(productId: number): Promise<QRCodeResponse> {
    const response = await fetch(`${API_BASE_URL}/products/${productId}/qr-code`, {
      method: "POST",
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to generate QR code")
    }

    return response.json()
  }

  async verifyProduct(verificationData: VerifyProductRequest): Promise<VerificationResult> {
    const response = await fetch(`${API_BASE_URL}/products/verify-product`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(verificationData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to verify product")
    }

    return response.json()
  }

  async createVerification(verificationData: VerificationCreate): Promise<Verification> {
    const response = await fetch(`${VERIFICATIONS_BASE_URL}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(verificationData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to create verification")
    }

    return response.json()
  }

  async analyzeCounterfeit(productId: number, qrCodeHash?: string, location?: string): Promise<CounterfeitAnalysis> {
    const params = new URLSearchParams()
    if (qrCodeHash) params.append("qr_code_hash", qrCodeHash)
    if (location) params.append("location", location)

    const url = `${VERIFICATIONS_BASE_URL}/analyze-counterfeit/${productId}${params.toString() ? "?" + params.toString() : ""}`

    const response = await fetch(url, {
      method: "POST",
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to analyze counterfeit")
    }

    return response.json()
  }

  async getVerifications(skip = 0, limit = 100): Promise<Verification[]> {
    const response = await fetch(`${VERIFICATIONS_BASE_URL}/?skip=${skip}&limit=${limit}`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch verifications")
    }

    return response.json()
  }

  async getVerification(verificationId: number): Promise<Verification> {
    const response = await fetch(`${VERIFICATIONS_BASE_URL}/${verificationId}`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch verification")
    }

    return response.json()
  }

  async getProductVerifications(productId: number): Promise<Verification[]> {
    const response = await fetch(`${VERIFICATIONS_BASE_URL}/product/${productId}`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch product verifications")
    }

    return response.json()
  }

  async getBlockchainStatus(): Promise<BlockchainStatus> {
    const response = await fetch(`${BLOCKCHAIN_BASE_URL}/status`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch blockchain status")
    }

    return response.json()
  }

  async getTotalProducts(): Promise<{ total_products: number }> {
    const response = await fetch(`${BLOCKCHAIN_BASE_URL}/products/count`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch total products")
    }

    return response.json()
  }

  async getBlockchainProduct(productId: number): Promise<BlockchainProduct> {
    const response = await fetch(`${BLOCKCHAIN_BASE_URL}/products/${productId}`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch blockchain product")
    }

    return response.json()
  }

  async getBlockchainProductByQR(qrCodeHash: string): Promise<BlockchainProduct> {
    const response = await fetch(`${BLOCKCHAIN_BASE_URL}/products/qr/${qrCodeHash}`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch blockchain product by QR")
    }

    return response.json()
  }

  async grantBlockchainRole(
    roleData: GrantRoleRequest,
  ): Promise<{ success: boolean; role: string; account: string; message: string }> {
    const response = await fetch(`${BLOCKCHAIN_BASE_URL}/grant-role`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(roleData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to grant blockchain role")
    }

    return response.json()
  }

  async verifyProductOnBlockchain(
    productId: number,
    verificationData: BlockchainVerificationRequest,
  ): Promise<{
    success: boolean
    transaction_hash?: string
    block_number?: number
    gas_used?: number
  }> {
    const response = await fetch(`${BLOCKCHAIN_BASE_URL}/products/${productId}/verify`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...this.getAuthHeaders(),
      },
      body: JSON.stringify(verificationData),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to verify product on blockchain")
    }

    return response.json()
  }

  async getDetailedNetworkInfo(): Promise<BlockchainStatus & { total_products: number; contract_address: string }> {
    const response = await fetch(`${BLOCKCHAIN_BASE_URL}/admin/network-info`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Failed to fetch detailed network info")
    }

    return response.json()
  }

  async getAnalytics(): Promise<AnalyticsData> {
    const response = await fetch(`${ANALYTICS_BASE_URL}/overview`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch analytics data")
    }

    return response.json()
  }

  async getVerificationTrends(range = "7d"): Promise<{ date: string; count: number }[]> {
    const response = await fetch(`${ANALYTICS_BASE_URL}/verification-trends?range=${range}`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch verification trends")
    }

    return response.json()
  }

  async getCategoryDistribution(): Promise<{ category: string; count: number }[]> {
    const response = await fetch(`${ANALYTICS_BASE_URL}/product-categories`, {
      headers: {
        ...this.getAuthHeaders(),
      },
    })

    if (!response.ok) {
      throw new Error("Failed to fetch category distribution")
    }

    return response.json()
  }
}

export const apiClient = new ApiClient()
