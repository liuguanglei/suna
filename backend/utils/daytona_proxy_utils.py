from utils.config import config
from urllib.parse import urlparse
def convert_daytona_proxy_url(url: str) -> str:
        """Convert Daytona preview URL to local format.
        
        Args:
            url: The Daytona preview URL in format like https://8000-7f52815b-f82f-4aba-a645-f86b463afe09.proxy.daytona.works/test.html
            
        Returns:
            The converted local URL in format like http://127.0.0.1:3000/8000-04cbf4e5-d602-4d5e-aa72-7710a9783742/test.html
        """
        try:
            # Check if the URL is a Daytona URL
            if "proxy.daytona.works" not in url:
                return url
            
            # Extract the subdomain part which contains the port and container ID
            
            parsed_url = urlparse(url)
            subdomain = parsed_url.netloc.split('.')[0]  # Get part before proxy.daytona.works
            
            # Extract path if exists
            path = parsed_url.path if parsed_url.path != '/' else ''
            
            # Get base URL from config, default to http://localhost:3000 if not set
            base_url = config.get('DAYTONA_PROXY_URL', 'http://192.168.10.81:3300')
            
            # Ensure base_url doesn't end with slash
            if base_url.endswith('/'):
                base_url = base_url[:-1]
            
            # Convert to local format: {base_url}/{subdomain}{path}
            local_url = f"{base_url}/{subdomain}{path}"
            
            return local_url
        except Exception:
            # If parsing fails, return the original URL
            return url

if __name__ == "__main__":
    new = convert_daytona_proxy_url("https://8000-7f52815b-f82f-4aba-a645-f86b463afe09.proxy.daytona.works/test.html")
    print(new)