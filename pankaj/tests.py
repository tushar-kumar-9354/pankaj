# test_subscription.py
import requests
import json

def test_subscription():
    url = "http://127.0.0.1:8000/blogs/subscribe/"
    
    # Test data
    test_email = "test3@example.com"
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Data
    data = {
        'email': test_email
    }
    
    print(f"Testing subscription for: {test_email}")
    print(f"URL: {url}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_subscription()