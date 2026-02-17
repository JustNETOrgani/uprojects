const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying AntiCounterfeit contract...");

  // Get the contract factory
  const AntiCounterfeit = await ethers.getContractFactory("AntiCounterfeit");
  
  // Deploy the contract
  const antiCounterfeit = await AntiCounterfeit.deploy();
  
  // Wait for deployment to finish
  await antiCounterfeit.waitForDeployment();
  
  const address = await antiCounterfeit.getAddress();
  console.log("AntiCounterfeit contract deployed to:", address);
  
  // Get the deployer's address
  const [deployer] = await ethers.getSigners();
  console.log("Deployed by:", deployer.address);
  
  // Grant initial roles to the deployer
  console.log("Setting up initial roles...");
  
  // Grant manufacturer role to deployer
  await antiCounterfeit.grantUserRole(
    ethers.keccak256(ethers.toUtf8Bytes("MANUFACTURER_ROLE")),
    deployer.address
  );
  
  // Grant retailer role to deployer
  await antiCounterfeit.grantUserRole(
    ethers.keccak256(ethers.toUtf8Bytes("RETAILER_ROLE")),
    deployer.address
  );
  
  // Grant distributor role to deployer
  await antiCounterfeit.grantUserRole(
    ethers.keccak256(ethers.toUtf8Bytes("DISTRIBUTOR_ROLE")),
    deployer.address
  );
  
  // Grant consumer role to deployer
  await antiCounterfeit.grantUserRole(
    ethers.keccak256(ethers.toUtf8Bytes("CONSUMER_ROLE")),
    deployer.address
  );
  
  console.log("Initial roles granted to deployer");
  console.log("Deployment completed successfully!");
  
  // Save deployment info
  const deploymentInfo = {
    contractAddress: address,
    deployer: deployer.address,
    network: network.name,
    timestamp: new Date().toISOString()
  };
  
  console.log("Deployment Info:", JSON.stringify(deploymentInfo, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
