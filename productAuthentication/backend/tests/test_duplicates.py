import requests

BASE_URL = "http://localhost:8000/api/v1"

def create_manufacturer_user(email, password):
    # Try to register or login manufacturer user
    reg_data = {
        "email": email,
        "password": password,
        "full_name": "Test Manufacturer",
        "role": "manufacturer"
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    if resp.status_code == 200:
        return resp.json()
    # fallback login
    resp = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    return {"token": resp.json().get("access_token")} if resp.status_code == 200 else None

def create_product(token, product_info):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/products/", json=product_info, headers=headers)
    if resp.status_code == 200:
        return resp.json()
    else:
        print("Create product failed:", resp.text)
        return None

def update_product_qr_hash(token, product_id, qr_hash):
    headers = {"Authorization": f"Bearer {token}"}
    # Directly updating QR hash for test purposes (assuming PATCH/PUT allowed)
    resp = requests.put(f"{BASE_URL}/products/{product_id}", json={"qr_code_hash": qr_hash}, headers=headers)
    return resp.status_code == 200

def verify_product(token, product_id, location="Test Location"):
    headers = {"Authorization": f"Bearer {token}"}
    verification_data = {
        "product_id": product_id,
        "location": location,
        "notes": "Test verification"
    }
    resp = requests.post(f"{BASE_URL}/verifications/", json=verification_data, headers=headers)
    return resp.json() if resp.status_code == 200 else None

def test_duplicate_qr_code_detection():
    # Setup
    user = create_manufacturer_user("duplicate_qr@test.com", "password123")
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvYmlyaWthbjAyMEBnbWFpbC5jb20iLCJleHAiOjE3NTU3ODY3NjJ9.EJIqpt_T6-BHZhAcF0BwOxX-PnELSJWS3ntgiDcS_74'

    # Create first product normally
    product1 = create_product(token, {
        "product_name": "Original Product",
        "product_description": "Legitimate item",
        "category": "electronics",
        "batch_number": "BATCH001",
        "manufacturing_date": "2024-01-01"
    })

    if not product1:
        print("Failed to create original product")
        return

    # Create second product normally
    product2 = create_product(token, {
        "product_name": "Fake Product",
        "product_description": "Counterfeit item",
        "category": "electronics",
        "batch_number": "BATCH002",
        "manufacturing_date": "2024-01-15"
    })

    if not product2:
        print("Failed to create fake product")
        return

    # Force the second product to reuse the QR hash of the first product
    qr_hash_to_duplicate = product1["qr_code_hash"]
    success = update_product_qr_hash(token, product2["id"], qr_hash_to_duplicate)
    if not success:
        print("Failed to update QR hash of fake product")
        return

    # Verify first product - Should be authentic
    verification1 = verify_product(token, product1["id"])
    print("Verification 1 - Original Product:", verification1)

    # Verify second product - Should detect counterfeit due to duplicate QR hash
    verification2 = verify_product(token, product2["id"])
    print("Verification 2 - Fake Product with duplicated QR hash:", verification2)

if __name__ == "__main__":
    test_duplicate_qr_code_detection()
