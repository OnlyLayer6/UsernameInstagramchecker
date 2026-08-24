import requests
import time

def test_proxies(input_file="proxies.txt", output_file="valid_proxies.txt"):
    """
    Tests a list of proxies from input_file and saves the working ones to output_file.
    """
    try:
        with open(input_file, 'r') as f:
            proxies_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ File '{input_file}' not found. Please create a proxies.txt file first.")
        return

    print(f"Testing {len(proxies_list)} proxies...")
    
    valid_proxies = []
    tested_count = 0
    
    for i, proxy_url in enumerate(proxies_list):
        tested_count += 1
        print(f"[{tested_count}/{len(proxies_list)}] Testing {proxy_url}...")
        
        try:
            # Configure proxy for the request
            proxies = {'http': proxy_url, 'https': proxy_url}
            
            # Request a lightweight page to test connectivity
            response = requests.get('https://example.com', proxies=proxies, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ {proxy_url} VALID")
                valid_proxies.append(proxy_url)
            else:
                print(f"   ❌ {proxy_url} INVALID (Status: {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ {proxy_url} ERROR ({str(e)})")
        
        # Small delay between tests to avoid overwhelming the target
        time.sleep(0.5)

    # Save valid proxies to the output file
    with open(output_file, 'w') as f:
        for proxy in valid_proxies:
            f.write(f"{proxy}\n")
            
    print(f"\n Finished!")
    print(f"   Total Proxies Tested: {tested_count}")
    print(f"   Valid Proxies: {len(valid_proxies)}")
    print(f"   Valid proxies saved to: {output_file}")

if __name__ == "__main__":
    test_proxies()
