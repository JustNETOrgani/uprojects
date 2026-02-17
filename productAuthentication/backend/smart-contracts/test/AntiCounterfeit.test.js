const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AntiCounterfeit", function () {
  let antiCounterfeit;
  let owner;
  let manufacturer;
  let retailer;
  let distributor;
  let consumer;
  let addr1;
  let addr2;

  const MANUFACTURER_ROLE = ethers.keccak256(ethers.toUtf8Bytes("MANUFACTURER_ROLE"));
  const RETAILER_ROLE = ethers.keccak256(ethers.toUtf8Bytes("RETAILER_ROLE"));
  const DISTRIBUTOR_ROLE = ethers.keccak256(ethers.toUtf8Bytes("DISTRIBUTOR_ROLE"));
  const CONSUMER_ROLE = ethers.keccak256(ethers.toUtf8Bytes("CONSUMER_ROLE"));
  const ADMIN_ROLE = ethers.keccak256(ethers.toUtf8Bytes("ADMIN_ROLE"));

  beforeEach(async function () {
    [owner, manufacturer, retailer, distributor, consumer, addr1, addr2] = await ethers.getSigners();

    const AntiCounterfeit = await ethers.getContractFactory("AntiCounterfeit");
    antiCounterfeit = await AntiCounterfeit.deploy();

    // Grant roles to test accounts
    await antiCounterfeit.grantUserRole(MANUFACTURER_ROLE, manufacturer.address);
    await antiCounterfeit.grantUserRole(RETAILER_ROLE, retailer.address);
    await antiCounterfeit.grantUserRole(DISTRIBUTOR_ROLE, distributor.address);
    await antiCounterfeit.grantUserRole(CONSUMER_ROLE, consumer.address);
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await antiCounterfeit.hasRole(await antiCounterfeit.DEFAULT_ADMIN_ROLE(), owner.address)).to.equal(true);
    });

    it("Should grant admin role to deployer", async function () {
      expect(await antiCounterfeit.hasRole(ADMIN_ROLE, owner.address)).to.equal(true);
    });
  });

  describe("Role Management", function () {
    it("Should grant manufacturer role", async function () {
      expect(await antiCounterfeit.hasRole(MANUFACTURER_ROLE, manufacturer.address)).to.equal(true);
    });

    it("Should grant retailer role", async function () {
      expect(await antiCounterfeit.hasRole(RETAILER_ROLE, retailer.address)).to.equal(true);
    });

    it("Should grant distributor role", async function () {
      expect(await antiCounterfeit.hasRole(DISTRIBUTOR_ROLE, distributor.address)).to.equal(true);
    });

    it("Should grant consumer role", async function () {
      expect(await antiCounterfeit.hasRole(CONSUMER_ROLE, consumer.address)).to.equal(true);
    });

    it("Should allow admin to grant roles", async function () {
      await antiCounterfeit.grantUserRole(MANUFACTURER_ROLE, addr1.address);
      expect(await antiCounterfeit.hasRole(MANUFACTURER_ROLE, addr1.address)).to.equal(true);
    });

    it("Should not allow non-admin to grant roles", async function () {
      await expect(
        antiCounterfeit.connect(addr1).grantUserRole(MANUFACTURER_ROLE, addr2.address)
      ).to.be.revertedWithCustomError(antiCounterfeit, "AccessControlUnauthorizedAccount");
    });
  });

  describe("Product Registration", function () {
    const productData = {
      name: "Test Product",
      description: "A test product for verification",
      manufacturingDate: Math.floor(Date.now() / 1000),
      batchNumber: "BATCH001",
      category: "Electronics",
      qrCodeHash: "QRC001"
    };

    it("Should allow manufacturer to register product", async function () {
      const tx = await antiCounterfeit.connect(manufacturer).registerProduct(
        productData.name,
        productData.description,
        productData.manufacturingDate,
        productData.batchNumber,
        productData.category,
        productData.qrCodeHash
      );

      await expect(tx)
        .to.emit(antiCounterfeit, "ProductRegistered")
        .withArgs(1, productData.name, manufacturer.address, productData.qrCodeHash, await time());

      const product = await antiCounterfeit.getProduct(1);
      expect(product.productName).to.equal(productData.name);
      expect(product.manufacturer).to.equal(manufacturer.address);
      expect(product.isActive).to.equal(true);
    });

    it("Should not allow non-manufacturer to register product", async function () {
      await expect(
        antiCounterfeit.connect(addr1).registerProduct(
          productData.name,
          productData.description,
          productData.manufacturingDate,
          productData.batchNumber,
          productData.category,
          productData.qrCodeHash
        )
      ).to.be.revertedWithCustomError(antiCounterfeit, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow duplicate QR code hash", async function () {
      await antiCounterfeit.connect(manufacturer).registerProduct(
        productData.name,
        productData.description,
        productData.manufacturingDate,
        productData.batchNumber,
        productData.category,
        productData.qrCodeHash
      );

      await expect(
        antiCounterfeit.connect(manufacturer).registerProduct(
          "Another Product",
          "Another description",
          productData.manufacturingDate,
          "BATCH002",
          productData.category,
          productData.qrCodeHash
        )
      ).to.be.revertedWith("QR code already exists");
    });

    it("Should not allow empty product name", async function () {
      await expect(
        antiCounterfeit.connect(manufacturer).registerProduct(
          "",
          productData.description,
          productData.manufacturingDate,
          productData.batchNumber,
          productData.category,
          productData.qrCodeHash
        )
      ).to.be.revertedWith("Product name cannot be empty");
    });

    it("Should not allow empty QR code hash", async function () {
      await expect(
        antiCounterfeit.connect(manufacturer).registerProduct(
          productData.name,
          productData.description,
          productData.manufacturingDate,
          productData.batchNumber,
          productData.category,
          ""
        )
      ).to.be.revertedWith("QR code hash cannot be empty");
    });
  });

  describe("Product Verification", function () {
    let productId;

    beforeEach(async function () {
      const tx = await antiCounterfeit.connect(manufacturer).registerProduct(
        "Test Product",
        "A test product",
        Math.floor(Date.now() / 1000),
        "BATCH001",
        "Electronics",
        "QRC001"
      );
      const receipt = await tx.wait();
      const event = receipt.logs.find(log => log.eventName === "ProductRegistered");
      productId = event.args.productId;
    });

    it("Should allow anyone to verify a product", async function () {
      const tx = await antiCounterfeit.connect(consumer).verifyProduct(
        productId,
        "New York, NY",
        "Verified at retail store"
      );

      await expect(tx)
        .to.emit(antiCounterfeit, "ProductVerified")
        .withArgs(productId, consumer.address, true, "New York, NY", await time());

      const result = await tx.wait();
      expect(result.status).to.equal(1);
    });

    it("Should not allow verification of non-existent product", async function () {
      await expect(
        antiCounterfeit.connect(consumer).verifyProduct(
          999,
          "New York, NY",
          "Test verification"
        )
      ).to.be.revertedWith("Product does not exist or is inactive");
    });

    it("Should not allow verification with empty location", async function () {
      await expect(
        antiCounterfeit.connect(consumer).verifyProduct(
          productId,
          "",
          "Test verification"
        )
      ).to.be.revertedWith("Location cannot be empty");
    });

    it("Should store verification history", async function () {
      await antiCounterfeit.connect(consumer).verifyProduct(
        productId,
        "New York, NY",
        "First verification"
      );

      await antiCounterfeit.connect(retailer).verifyProduct(
        productId,
        "Los Angeles, CA",
        "Second verification"
      );

      const history = await antiCounterfeit.getProductVerificationHistory(productId);
      expect(history.length).to.equal(2);
      expect(history[0].verifier).to.equal(consumer.address);
      expect(history[1].verifier).to.equal(retailer.address);
    });
  });

  describe("Location Updates", function () {
    let productId;

    beforeEach(async function () {
      const tx = await antiCounterfeit.connect(manufacturer).registerProduct(
        "Test Product",
        "A test product",
        Math.floor(Date.now() / 1000),
        "BATCH001",
        "Electronics",
        "QRC001"
      );
      const receipt = await tx.wait();
      const event = receipt.logs.find(log => log.eventName === "ProductRegistered");
      productId = event.args.productId;
    });

    it("Should allow distributor to update location", async function () {
      const tx = await antiCounterfeit.connect(distributor).updateProductLocation(
        productId,
        "Warehouse A",
        "Product moved to warehouse"
      );

      await expect(tx)
        .to.emit(antiCounterfeit, "LocationUpdated")
        .withArgs(productId, distributor.address, "Warehouse A", await time());
    });

    it("Should not allow non-distributor to update location", async function () {
      await expect(
        antiCounterfeit.connect(consumer).updateProductLocation(
          productId,
          "Warehouse A",
          "Product moved"
        )
      ).to.be.revertedWithCustomError(antiCounterfeit, "AccessControlUnauthorizedAccount");
    });

    it("Should not allow location update for non-existent product", async function () {
      await expect(
        antiCounterfeit.connect(distributor).updateProductLocation(
          999,
          "Warehouse A",
          "Product moved"
        )
      ).to.be.revertedWith("Product does not exist or is inactive");
    });

    it("Should not allow empty location", async function () {
      await expect(
        antiCounterfeit.connect(distributor).updateProductLocation(
          productId,
          "",
          "Product moved"
        )
      ).to.be.revertedWith("Location cannot be empty");
    });

    it("Should store location history", async function () {
      await antiCounterfeit.connect(distributor).updateProductLocation(
        productId,
        "Warehouse A",
        "First location"
      );

      await antiCounterfeit.connect(distributor).updateProductLocation(
        productId,
        "Warehouse B",
        "Second location"
      );

      const history = await antiCounterfeit.getProductLocationHistory(productId);
      expect(history.length).to.equal(2);
      expect(history[0].location).to.equal("Warehouse A");
      expect(history[1].location).to.equal("Warehouse B");
    });
  });

  describe("Product Retrieval", function () {
    let productId;
    const qrCodeHash = "QRC001";

    beforeEach(async function () {
      const tx = await antiCounterfeit.connect(manufacturer).registerProduct(
        "Test Product",
        "A test product",
        Math.floor(Date.now() / 1000),
        "BATCH001",
        "Electronics",
        qrCodeHash
      );
      const receipt = await tx.wait();
      const event = receipt.logs.find(log => log.eventName === "ProductRegistered");
      productId = event.args.productId;
    });

    it("Should retrieve product by ID", async function () {
      const product = await antiCounterfeit.getProduct(productId);
      expect(product.productName).to.equal("Test Product");
      expect(product.manufacturer).to.equal(manufacturer.address);
    });

    it("Should retrieve product by QR code", async function () {
      const product = await antiCounterfeit.getProductByQRCode(qrCodeHash);
      expect(product.productId).to.equal(productId);
      expect(product.productName).to.equal("Test Product");
    });

    it("Should not find product for non-existent QR code", async function () {
      await expect(
        antiCounterfeit.getProductByQRCode("NONEXISTENT")
      ).to.be.revertedWith("Product not found for this QR code");
    });

    it("Should get products by manufacturer", async function () {
      const products = await antiCounterfeit.getProductsByManufacturer(manufacturer.address);
      expect(products.length).to.equal(1);
      expect(products[0]).to.equal(productId);
    });
  });

  describe("Product Deactivation", function () {
    let productId;

    beforeEach(async function () {
      const tx = await antiCounterfeit.connect(manufacturer).registerProduct(
        "Test Product",
        "A test product",
        Math.floor(Date.now() / 1000),
        "BATCH001",
        "Electronics",
        "QRC001"
      );
      const receipt = await tx.wait();
      const event = receipt.logs.find(log => log.eventName === "ProductRegistered");
      productId = event.args.productId;
    });

    it("Should allow manufacturer to deactivate product", async function () {
      const tx = await antiCounterfeit.connect(manufacturer).deactivateProduct(productId);

      await expect(tx)
        .to.emit(antiCounterfeit, "ProductDeactivated")
        .withArgs(productId, manufacturer.address, await time());

      const product = await antiCounterfeit.getProduct(productId);
      expect(product.isActive).to.equal(false);
    });

    it("Should allow admin to deactivate product", async function () {
      await antiCounterfeit.connect(owner).deactivateProduct(productId);

      const product = await antiCounterfeit.getProduct(productId);
      expect(product.isActive).to.equal(false);
    });

    it("Should not allow non-manufacturer/non-admin to deactivate product", async function () {
      await expect(
        antiCounterfeit.connect(consumer).deactivateProduct(productId)
      ).to.be.revertedWith("Only manufacturer or admin can deactivate product");
    });

    it("Should not allow deactivation of already inactive product", async function () {
      await antiCounterfeit.connect(manufacturer).deactivateProduct(productId);

      await expect(
        antiCounterfeit.connect(manufacturer).deactivateProduct(productId)
      ).to.be.revertedWith("Product is already inactive");
    });
  });

  describe("Statistics", function () {
    it("Should return correct total products count", async function () {
      expect(await antiCounterfeit.getTotalProducts()).to.equal(0);

      await antiCounterfeit.connect(manufacturer).registerProduct(
        "Product 1",
        "Description 1",
        Math.floor(Date.now() / 1000),
        "BATCH001",
        "Electronics",
        "QRC001"
      );

      expect(await antiCounterfeit.getTotalProducts()).to.equal(1);

      await antiCounterfeit.connect(manufacturer).registerProduct(
        "Product 2",
        "Description 2",
        Math.floor(Date.now() / 1000),
        "BATCH002",
        "Electronics",
        "QRC002"
      );

      expect(await antiCounterfeit.getTotalProducts()).to.equal(2);
    });

    it("Should return correct total verifications count", async function () {
      expect(await antiCounterfeit.getTotalVerifications()).to.equal(0);

      const tx = await antiCounterfeit.connect(manufacturer).registerProduct(
        "Test Product",
        "A test product",
        Math.floor(Date.now() / 1000),
        "BATCH001",
        "Electronics",
        "QRC001"
      );
      const receipt = await tx.wait();
      const event = receipt.logs.find(log => log.eventName === "ProductRegistered");
      const productId = event.args.productId;

      await antiCounterfeit.connect(consumer).verifyProduct(
        productId,
        "New York, NY",
        "Test verification"
      );

      expect(await antiCounterfeit.getTotalVerifications()).to.equal(1);
    });
  });

  // Helper function to get current timestamp
  async function time() {
    const blockNum = await ethers.provider.getBlockNumber();
    const block = await ethers.provider.getBlock(blockNum);
    return block.timestamp;
  }
});
