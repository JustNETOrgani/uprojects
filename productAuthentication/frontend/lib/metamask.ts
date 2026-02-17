// MetaMask integration utilities
export interface MetaMaskAccount {
  address: string
  balance?: string
}

class MetaMaskService {
  async isMetaMaskInstalled(): Promise<boolean> {
    return typeof window !== "undefined" && typeof window.ethereum !== "undefined"
  }

  async connectWallet(): Promise<MetaMaskAccount> {
    if (!(await this.isMetaMaskInstalled())) {
      throw new Error("MetaMask is not installed")
    }

    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts",
      })

      if (accounts.length === 0) {
        throw new Error("No accounts found")
      }

      const address = accounts[0]

      // Get balance
      const balance = await window.ethereum.request({
        method: "eth_getBalance",
        params: [address, "latest"],
      })

      return {
        address,
        balance: Number.parseInt(balance, 16).toString(),
      }
    } catch (error) {
      throw new Error("Failed to connect to MetaMask")
    }
  }

  async getCurrentAccount(): Promise<string | null> {
    if (!(await this.isMetaMaskInstalled())) {
      return null
    }

    try {
      const accounts = await window.ethereum.request({
        method: "eth_accounts",
      })
      return accounts.length > 0 ? accounts[0] : null
    } catch (error) {
      return null
    }
  }

  onAccountsChanged(callback: (accounts: string[]) => void) {
    if (typeof window !== "undefined" && window.ethereum) {
      window.ethereum.on("accountsChanged", callback)
    }
  }

  removeAccountsChangedListener(callback: (accounts: string[]) => void) {
    if (typeof window !== "undefined" && window.ethereum) {
      window.ethereum.removeListener("accountsChanged", callback)
    }
  }
}

export const metaMaskService = new MetaMaskService()

// Extend Window interface for TypeScript
declare global {
  interface Window {
    ethereum?: any
  }
}
