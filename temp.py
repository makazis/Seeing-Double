from math import *
import requests

# Replace with your target IP (and port if needed)
target_ip = "http://85.254.75.9:48983"  # Example IP

try:
    response = requests.get(target_ip)
    
    # Check if the request was successful
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Content: {response.text[:500]}")  # Print first 500 chars
    
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")



markusa ip adrese: 85.254.75.9