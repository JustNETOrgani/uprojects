import type { Metadata } from "next"
import ProtectedRoute from "@/components/auth/protected-route"
import BlockchainStatusComponent from "@/components/blockchain/blockchain-status"

export const metadata: Metadata = {
  title: "Blockchain Status",
  description: "Monitor blockchain network and smart contract status",
}

export default function BlockchainPage() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto py-8">
        <BlockchainStatusComponent />
      </div>
    </ProtectedRoute>
  )
}
