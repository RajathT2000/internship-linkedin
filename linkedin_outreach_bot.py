"""
LinkedIn PACE Outreach Agent
Automates connection requests to AI leads and Engineering Managers at MQ PACE partner companies.
"""

import os
import time
import random
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

# Load environment variables
load_dotenv()

class LinkedInOutreachBot:
    def __init__(self):
        """Initialize the LinkedIn automation bot."""
        self.driver = None
        self.outreach_history = []
    
    def human_delay(self, min_seconds=10, max_seconds=20):
        """Implement human-like delays to avoid detection."""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"Waiting {delay:.1f} seconds...")
        time.sleep(delay)
    
    def setup_driver(self):
        """Setup undetected ChromeDriver with anti-detection measures."""
        print("Setting up Chrome driver...")
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        print("Chrome driver ready!")
    
    def login_to_linkedin(self):
        """Navigate to LinkedIn and wait for manual login."""
        print("Opening LinkedIn...")
        print("\n" + "="*60)
        print("PLEASE LOG IN MANUALLY")
        print("="*60)
        print("1. The browser will open LinkedIn")
        print("2. Log in with your credentials")
        print("3. Complete any security checks (2FA, captcha, etc.)")
        print("4. Wait on the LinkedIn home/feed page")
        print("="*60)
        
        self.driver.get('https://www.linkedin.com')
        
        # Wait for user confirmation
        while True:
            response = input("\nDid you login successfully? (yes/y to continue): ").strip().lower()
            if response in ['yes', 'y']:
                break
            else:
                print("Please complete the login and then type 'yes' or 'y'")
        
        print("\n✓ Login confirmed! Starting automation...")
        self.human_delay(3, 5)
        return True
    
    def search_person(self, job_title, company_name, location="Sydney, Australia"):
        """Search for a person with specific job title at a company."""
        search_query = f"{job_title} at {company_name} in {location}"
        print(f"\nSearching for: {search_query}")
        
        try:
            # Navigate to LinkedIn search
            self.driver.get('https://www.linkedin.com/search/results/people/')
            self.human_delay(3, 5)
            
            # Find and use search box
            search_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Search"]'))
            )
            search_box.clear()
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            self.human_delay(5, 8)
            
            # Get search results
            results = self.driver.find_elements(By.XPATH, '//li[contains(@class, "reusable-search__result-container")]')
            
            if not results:
                print(f"No results found for {search_query}")
                return []
            
            people_found = []
            for i, result in enumerate(results[:3]):  # Limit to top 3 results
                try:
                    name_element = result.find_element(By.XPATH, './/span[@dir="ltr"]//span[@aria-hidden="true"]')
                    name = name_element.text
                    
                    # Try to find Connect button
                    connect_buttons = result.find_elements(By.XPATH, './/button[contains(@aria-label, "Invite") or contains(text(), "Connect")]')
                    
                    people_found.append({
                        'name': name,
                        'company': company_name,
                        'job_title': job_title,
                        'can_connect': len(connect_buttons) > 0,
                        'element': result
                    })
                    
                    print(f"Found: {name} ({job_title}) at {company_name}")
                    
                except Exception as e:
                    print(f"Could not extract info from result {i+1}: {str(e)}")
                    continue
            
            return people_found
            
        except Exception as e:
            print(f"Search failed: {str(e)}")
            return []
    
    def send_connection_request(self, person_info):
        """Send a personalized connection request."""
        try:
            name = person_info['name']
            company = person_info['company']
            
            print(f"\nPreparing to connect with {name}...")
            
            # Click Connect button
            connect_button = person_info['element'].find_element(
                By.XPATH, './/button[contains(@aria-label, "Invite") or contains(text(), "Connect")]'
            )
            connect_button.click()
            self.human_delay(3, 5)
            
            # Try to add a note
            try:
                add_note_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Add a note"]'))
                )
                add_note_button.click()
                self.human_delay(2, 4)
                
                # Personalized message
                message = f"""Hi {name.split()[0]},

I'm a Macquarie University student seeking an MQ PACE verified AI internship in Sydney. I've built RAG agents, SQL automation tools, and have strong experience in Python and machine learning.

I'd greatly appreciate any guidance or potential referral opportunities at {company}.

Best regards"""
                
                note_field = self.driver.find_element(By.XPATH, '//textarea[@name="message"]')
                note_field.send_keys(message)
                self.human_delay(2, 4)
                
                # Send connection request
                send_button = self.driver.find_element(By.XPATH, '//button[@aria-label="Send now"]')
                send_button.click()
                
                print(f"✓ Connection request sent to {name} with personalized note!")
                
            except:
                # If can't add note, just send connection
                try:
                    send_button = self.driver.find_element(By.XPATH, '//button[contains(text(), "Send") or @aria-label="Send invitation"]')
                    send_button.click()
                    print(f"✓ Connection request sent to {name} (without note)")
                except Exception as e:
                    print(f"Could not send connection request: {str(e)}")
                    return False
            
            # Log the outreach
            self.outreach_history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'name': name,
                'company': company,
                'job_title': person_info['job_title'],
                'status': 'sent'
            })
            
            self.human_delay(10, 20)
            return True
            
        except Exception as e:
            print(f"Failed to send connection request: {str(e)}")
            self.outreach_history.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'name': person_info.get('name', 'Unknown'),
                'company': person_info.get('company', 'Unknown'),
                'job_title': person_info.get('job_title', 'Unknown'),
                'status': 'failed'
            })
            return False
    
    def process_company(self, company_name, job_titles=['AI Lead', 'Engineering Manager', 'Talent Acquisition', 'HR Manager']):
        """Process a single company - search for specific roles and send connection requests."""
        print(f"\n{'='*60}")
        print(f"Processing: {company_name}")
        print(f"{'='*60}")
        
        for job_title in job_titles:
            people = self.search_person(job_title, company_name)
            
            for person in people:
                if person['can_connect']:
                    success = self.send_connection_request(person)
                    if success:
                        self.human_delay(20, 35)  # Extra delay after successful connection
                else:
                    print(f"Cannot connect with {person['name']} - already connected or pending")
                    self.outreach_history.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'name': person['name'],
                        'company': company_name,
                        'job_title': job_title,
                        'status': 'skipped'
                    })
            
            self.human_delay(15, 25)  # Delay between job title searches
    
    def save_outreach_history(self, filename='outreach_history.csv'):
        """Save all outreach attempts to CSV file."""
        if self.outreach_history:
            df = pd.DataFrame(self.outreach_history)
            
            # Append to existing file or create new
            if os.path.exists(filename):
                df.to_csv(filename, mode='a', header=False, index=False)
            else:
                df.to_csv(filename, index=False)
            
            print(f"\n✓ Outreach history saved to {filename}")
            print(f"Total interactions logged: {len(self.outreach_history)}")
        else:
            print("\nNo outreach history to save.")
    
    def run(self, companies):
        """Main execution method."""
        try:
            self.setup_driver()
            
            if not self.login_to_linkedin():
                print("Failed to login. Exiting...")
                return
            
            print(f"\nStarting outreach to {len(companies)} companies...")
            
            for company in companies:
                self.process_company(company)
                self.human_delay(25, 40)  # Delay between companies
            
            print("\n" + "="*60)
            print("Outreach campaign completed!")
            print("="*60)
            
        except Exception as e:
            print(f"\nError during execution: {str(e)}")
            
        finally:
            self.save_outreach_history()
            
            if self.driver:
                print("\nClosing browser...")
                self.human_delay(3, 5)
                self.driver.quit()


def main():
    """Main entry point."""
    # Load MQ PACE partner companies from config file
    with open('pace_partners.txt', 'r') as f:
        companies = [line.strip() for line in f if line.strip()]
    
    if not companies:
        print("No companies found in pace_partners.txt")
        return
    
    print(f"Loaded {len(companies)} MQ PACE partner companies")
    
    # Initialize and run the bot
    bot = LinkedInOutreachBot()
    bot.run(companies)


if __name__ == "__main__":
    main()
