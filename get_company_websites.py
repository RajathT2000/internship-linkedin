"""
Get Official Websites for Companies
Reads company_list.txt and finds official website for each company
"""

import time
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

class WebsiteFinder:
    def __init__(self):
        """Initialize the website finder."""
        self.driver = None
        self.results = []
        
    def setup_driver(self):
        """Setup undetected ChromeDriver."""
        print("Setting up Chrome driver...")
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        
        self.driver = uc.Chrome(options=options)
        print("Chrome driver ready!")
    
    def load_companies(self):
        """Load companies from company_list.txt."""
        companies = []
        
        try:
            with open('company_list.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip header lines and empty lines
                    if line and not line.startswith('AI INTERNSHIP') and not line.startswith('Generated') and not line.startswith('==='):
                        # Remove numbering (e.g., "1. Company Name" -> "Company Name")
                        if '. ' in line:
                            company = line.split('. ', 1)[1]
                        else:
                            company = line
                        
                        if company:
                            companies.append(company)
            
            print(f"✓ Loaded {len(companies)} companies")
            return companies
            
        except FileNotFoundError:
            print("Error: company_list.txt not found!")
            return []
    
    def find_website(self, company_name):
        """Find official website for a company."""
        try:
            search_query = f"{company_name} Sydney Australia official website"
            google_url = f'https://www.google.com/search?q={search_query.replace(" ", "+")}'
            
            self.driver.get(google_url)
            time.sleep(2)
            
            # Get first result that's not social media or job boards
            links = self.driver.find_elements(By.XPATH, '//div[@class="g"]//a')
            
            excluded_domains = ['linkedin', 'facebook', 'twitter', 'instagram', 'indeed', 'seek', 
                              'jora', 'google', 'youtube', 'wikipedia']
            
            for link in links[:5]:
                try:
                    url = link.get_attribute('href')
                    
                    if url and url.startswith('http') and not any(domain in url.lower() for domain in excluded_domains):
                        # Try to visit and verify
                        self.driver.get(url)
                        time.sleep(2)
                        
                        # Check if page loaded successfully
                        title = self.driver.title.lower()
                        if '404' not in title and 'not found' not in title and 'error' not in title:
                            print(f"  ✓ {url}")
                            return url
                        
                except Exception as e:
                    continue
            
            print(f"  ✗ No website found")
            return "Not found"
            
        except Exception as e:
            print(f"  Error: {str(e)}")
            return "Error"
    
    def save_results(self):
        """Save results to CSV and text file."""
        print("\n" + "="*60)
        print("SAVING RESULTS")
        print("="*60)
        
        # Save to CSV
        df = pd.DataFrame(self.results)
        df.to_csv('companies_with_websites.csv', index=False)
        print(f"✓ Saved to companies_with_websites.csv")
        
        # Save to text file
        with open('companies_websites.txt', 'w', encoding='utf-8') as f:
            f.write("COMPANIES WITH WEBSITES\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            for result in self.results:
                f.write(f"Company: {result['Company']}\n")
                f.write(f"Website: {result['Website']}\n")
                f.write("-" * 40 + "\n")
        
        print(f"✓ Saved to companies_websites.txt")
        
        # Stats
        found = sum(1 for r in self.results if r['Website'] != 'Not found' and r['Website'] != 'Error')
        print(f"\nStats: {found}/{len(self.results)} websites found")
    
    def run(self):
        """Main execution."""
        try:
            self.setup_driver()
            
            # Load companies
            companies = self.load_companies()
            
            if not companies:
                print("No companies to process!")
                return
            
            print(f"\nFinding websites for {len(companies)} companies...\n")
            
            # Find website for each company
            for i, company in enumerate(companies, 1):
                print(f"[{i}/{len(companies)}] {company}")
                
                website = self.find_website(company)
                
                self.results.append({
                    'Company': company,
                    'Website': website
                })
            
            print("\n" + "="*60)
            print("COMPLETED!")
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            if self.results:
                self.save_results()
            
            if self.driver:
                print("\nClosing browser...")
                time.sleep(2)
                self.driver.quit()


def main():
    """Main entry point."""
    print("="*60)
    print("COMPANY WEBSITE FINDER")
    print("="*60)
    print("\nReading company_list.txt...")
    
    finder = WebsiteFinder()
    finder.run()
    
    print("\n✓ Results saved!")
    print("  - companies_with_websites.csv")
    print("  - companies_websites.txt")


if __name__ == "__main__":
    main()
