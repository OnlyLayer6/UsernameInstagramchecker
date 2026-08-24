import requests
import random
import time
import string
import json
from urllib.parse import quote

class InstagramUsernameFinder:
    """
    A class to find available Instagram usernames using blind guessing.
    It uses rate limiting and rotating User-Agents to avoid detection.
    """
    def __init__(self, proxy_file=None):
        self.session = requests.Session()
        # Instagram's internal search API endpoint
        self.base_url = "https://www.instagram.com/web/search/topsearch/"
        self.stop_on_found = False
        self.found_username = None
        
        # Pool of User-Agents to simulate different browsers/devices
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
        ]
        
        # Allowed characters: lowercase letters and digits
        self.allowed_chars = string.ascii_lowercase + string.digits
        self.username_length_range = (4, 5)
        
        # Proxy management
        self.proxies = []
        self.proxy_index = 0
        if proxy_file:
            try:
                with open(proxy_file, 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                print(f"Proxy loaded: {len(self.proxies)} proxy(s) found.")
            except FileNotFoundError:
                print(f"Proxy file '{proxy_file}' not found. Using direct connection.")
        else:
            print("No proxy file specified. Using direct connection.")

    def get_next_proxy(self):
        """Returns the next proxy from the list in a round-robin fashion."""
        if not self.proxies:
            return None
        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return {'http': proxy, 'https': proxy}

    def set_random_user_agent(self):
        """Updates session headers with a random User-Agent."""
        self.session.headers.update({
            "User-Agent": random.choice(self.user_agents),
            "X-Requested-With": "XMLHttpRequest",
            "X-IG-App-ID": "936619743392459"
        })

    def generate_username(self):
        """Generates a random username of 4-5 characters (letters + numbers)."""
        length = random.choice(self.username_length_range)
        username = ''.join(random.choice(self.allowed_chars) for _ in range(length))
        return username

    def check_username(self, username):
        """
        Checks if the username is available.
        Returns True if available, False if taken, None on error.
        """
        try:
            self.set_random_user_agent()
            
            # API parameters for Instagram search
            params = {
                "q": username,
                "ig_sig": "known",
                "is_typeahead": "true",
                "context": "blended_search"
            }
            
            # Random delay to mimic human behavior (0.5 - 1.5 seconds)
            delay = random.uniform(0.5, 1.5)
            time.sleep(delay)
            
            # Get proxy
            proxies = self.get_next_proxy()
            
            response = self.session.get(
                self.base_url,
                params=params,
                headers=self.session.headers,
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # If the username appears in search results, it is likely taken
                if "users" in data and len(data["users"]) > 0:
                    for user in data["users"]:
                        if user.get("user", {}).get("username", "").lower() == username.lower():
                            return False  # Username is taken
                
                # If not found in results, assume it's available
                return True  
                
            elif response.status_code == 429:
                print(f"Rate limit detected. Waiting 30 seconds...")
                time.sleep(30)
                return None
                
            else:
                # print(f"Error: {response.status_code}")
                return None
                
        except Exception as e:
            # print(f"Exception: {str(e)}")
            return None

    def find_available_username(self, max_attempts=100):
        """
        Searches for an available username.
        Stops immediately when an available username is found or max_attempts is reached.
        """
        print(f"Starting search for {self.username_length_range[0]}-{self.username_length_range[1]} char usernames...")
        print(f"Will stop immediately when an available username is found.\n")
        
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            
            # Generate a random username
            username = self.generate_username()
            # print(f"[{attempts}] Trying: {username}")  # Uncomment to see every attempt
            
            # Check availability
            available = self.check_username(username)
            
            if available is True:
                print(f"\n Available username found : {username}")
                self.found_username = username
                self.stop_on_found = True
                break
            elif available is False:
                continue  # Username is taken, continue searching
            else:
                continue  # Error or rate limit, continue trying
        
        if not self.stop_on_found:
            print(f"\n Reached maximum attempts ({max_attempts}). No available username found.")
        
        return self.found_username

if __name__ == "__main__":
    # Specify the file containing valid proxies
    # If you don't have proxies, you can pass None
    finder = InstagramUsernameFinder(proxy_file="valid_proxies.txt")
    
    # To run without proxies, use:
    # finder = InstagramUsernameFinder()
    
    found = finder.find_available_username(max_attempts=200)
    
    if found:
        print(f"\n\n Final Result: Username '{found}' is available!")
        # Save result to a log file
        with open("found_usernames.txt", "a") as f:
            f.write(f"{found} - {time.ctime()}\n")
    else:
        print(f"\n\n Finished without finding an available username.")
