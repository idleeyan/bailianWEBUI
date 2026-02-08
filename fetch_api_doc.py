import requests

url = "https://bailian.console.aliyun.com/cn-beijing/?tab=api#/api/?type=model&url=2975126"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)}")
    print("\n" + "="*50)
    print("Response Content (first 5000 chars):")
    print("="*50)
    print(response.text[:5000])
except Exception as e:
    print(f"Error: {e}")
