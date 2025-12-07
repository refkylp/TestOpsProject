import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import subprocess
import json
from pathlib import Path

# Environment variables
CHROME_NODE_SERVICE = os.getenv("CHROME_NODE_SERVICE", "http://chrome-node-service:4444")
MAX_RETRIES = 5
RETRY_DELAY = 10  # seconds

class TestController:
    """
    Test Case Controller Pod'un ana sınıfı
    Görevleri:
    1. Behave test senaryolarını toplamak
    2. Chrome Node Pod'ların hazır olmasını beklemek
    3. Test'leri Selenium Grid üzerinden Chrome Node'lara göndermek
    4. Test sonuçlarını toplamak
    """
    
    def __init__(self):
        self.chrome_node_url = CHROME_NODE_SERVICE
        self.test_features_path = "features"
        self.drivers = []
        
    def check_chrome_node_health(self):
        """
        Chrome Node Pod'ların hazır olup olmadığını kontrol eder
        Selenium Grid'in /status endpoint'ini kullanır
        """
        print(f"🔍 Checking Chrome Node health at: {self.chrome_node_url}")
        
        for attempt in range(MAX_RETRIES):
            try:
                # Selenium Grid status endpoint
                status_url = f"{self.chrome_node_url}/wd/hub/status"
                response = requests.get(status_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Grid'in ready olup olmadığını kontrol et
                    if data.get("value", {}).get("ready", False):
                        print("✅ Chrome Node is ready!")
                        return True
                    else:
                        print(f"⏳ Chrome Node not ready yet (attempt {attempt + 1}/{MAX_RETRIES})")
                        
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Connection failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            
            if attempt < MAX_RETRIES - 1:
                print(f"⏰ Waiting {RETRY_DELAY} seconds before retry...")
                time.sleep(RETRY_DELAY)
        
        print("Chrome Node is not available after max retries")
        return False
    
    def collect_test_features(self):
        """
        Behave feature dosyalarını toplar
        """
        print(f"Collecting test features from: {self.test_features_path}")
        
        features_path = Path(self.test_features_path)
        
        if not features_path.exists():
            print(f"Features directory not found: {features_path}")
            return []
        
        # Tüm .feature dosyalarını bul
        feature_files = list(features_path.glob("**/*.feature"))
        
        print(f"Found {len(feature_files)} feature file(s):")
        for feature in feature_files:
            print(f"   - {feature.name}")
        
        return [str(f) for f in feature_files]
    
    def create_remote_driver(self):
        """
        Chrome Node Pod'a bağlanan Remote WebDriver oluşturur
        """
        print(f"Creating Remote WebDriver connection to: {self.chrome_node_url}")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        try:
            # Selenium Grid'e bağlan
            driver = webdriver.Remote(
                command_executor=f"{self.chrome_node_url}/wd/hub",
                options=chrome_options
            )
            print("Remote WebDriver created successfully!")
            return driver
            
        except WebDriverException as e:
            print(f"Failed to create Remote WebDriver: {e}")
            return None
    
    def execute_tests_with_behave(self, feature_files):
        """
        Behave framework kullanarak test'leri çalıştırır
        Remote WebDriver üzerinden Chrome Node'a bağlanır
        """
        print("\nStarting test execution...")
        
        # Environment variable olarak Chrome Node URL'ini set et
        # Böylece step definitions içinden erişebiliriz
        os.environ["SELENIUM_REMOTE_URL"] = f"{self.chrome_node_url}/wd/hub"
        
        try:
            # Behave komutunu çalıştır
            cmd = [
                "behave",
                "--format", "pretty",
                "--format", "json",
                "--outfile", "test_results.json",
                "--no-capture",  # Output'u göster
                "--no-capture-stderr"
            ]
            
            # Specific feature files varsa ekle
            if feature_files:
                cmd.extend(feature_files)
            
            print(f"Running command: {' '.join(cmd)}")
            
            # Subprocess ile behave'i çalıştır
            result = subprocess.run(
                cmd,
                cwd=os.getcwd(),
                capture_output=True,
                text=True
            )
            
            print("\n" + "="*50)
            print("TEST OUTPUT:")
            print("="*50)
            print(result.stdout)
            
            if result.stderr:
                print("\n" + "="*50)
                print("ERRORS:")
                print("="*50)
                print(result.stderr)
            
            # Exit code kontrol et
            if result.returncode == 0:
                print("\nAll tests passed!")
            else:
                print(f"\nTests failed with exit code: {result.returncode}")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Test execution failed: {e}")
            return False
    
    def send_test_to_chrome_node(self, test_scenario):
        """
        Tek bir test scenario'sunu Chrome Node'a gönderir
        (Alternative approach - direkt Selenium kullanarak)
        """
        print(f"Sending test scenario: {test_scenario}")
        
        driver = self.create_remote_driver()
        if not driver:
            print("Cannot send test - driver creation failed")
            return False
        
        try:
            # Örnek test execution
            # Bu kısım senin test senaryona göre değişir
            driver.get("https://useinsider.com/")
            print(f"Test scenario executed: {test_scenario}")
            return True
            
        except Exception as e:
            print(f"Test execution failed: {e}")
            return False
            
        finally:
            driver.quit()
    
    def run(self):
        """
        Ana execution fonksiyonu
        """
        print("\n" + "="*60)
        print("TEST CONTROLLER POD STARTED")
        print("="*60 + "\n")
        
        # 1. Chrome Node'ların hazır olmasını bekle
        if not self.check_chrome_node_health():
            print("Chrome Nodes are not ready. Exiting...")
            sys.exit(1)
        
        # 2. Test feature dosyalarını topla
        feature_files = self.collect_test_features()
        
        if not feature_files:
            print("No feature files found. Nothing to test.")
            sys.exit(0)
        
        # 3. Test'leri çalıştır
        success = self.execute_tests_with_behave(feature_files)
        
        # 4. Sonuç
        print("\n" + "="*60)
        if success:
            print("TEST CONTROLLER COMPLETED SUCCESSFULLY")
            print("="*60)
            sys.exit(0)
        else:
            print("TEST CONTROLLER COMPLETED WITH FAILURES")
            print("="*60)
            sys.exit(1)


def main():
    """
    Entry point
    """
    controller = TestController()
    controller.run()


if __name__ == "__main__":
    main()
