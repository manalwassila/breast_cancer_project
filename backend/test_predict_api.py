import requests
import os

API_URL = "http://127.0.0.1:8000"
IMAGE_PATH = os.path.join("static", "uploads", "01a4aaae-0bd0-4adc-b9c2-26727182cd81.png")

def test_predict():
    # 1. Login to get token
    login_data = {"username": "staff@mammoscan.ai", "password": "staffpassword"}
    resp = requests.post(f"{API_URL}/token", data=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test predict
    patient_data = {
        "first_name": "Test",
        "last_name": "User",
        "date_of_birth": "1990-01-01"
    }
    
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{API_URL}/predict", headers=headers, data=patient_data, files=files)
        
    if resp.status_code == 200:
        print("SUCCESS: Prediction test PASSED!")
        print(resp.json())
    else:
        print(f"FAILED: Prediction test FAILED: {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    test_predict()
