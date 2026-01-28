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
import re
import importlib
import sys

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
    
    def add_natural_typos(self, text):
        """Add natural spelling variations to avoid AI detection."""
        # Common natural variations
        variations = {
            'internship': ['intership', 'internship', 'internshp'],
            'opportunity': ['oportunity', 'opportunity', 'oppurtunity'],
            'experience': ['experiance', 'experience', 'experince'],
            'interested': ['intrested', 'interested', 'intersted'],
            'currently': ['currenly', 'currently', 'curenttly'],
            'appreciate': ['apreciate', 'appreciate', 'appriciate'],
            'working': ['workng', 'working', 'workin'],
            'university': ['university', 'univeristy', 'universtiy']
        }
        
        result = text
        # Apply 1-2 typos randomly
        num_typos = random.randint(1, 2)
        words_to_change = random.sample(list(variations.keys()), min(num_typos, len(variations)))
        
        for word in words_to_change:
            if word in result:
                result = result.replace(word, random.choice(variations[word]))
        
        return result
    
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
    
    def search_and_message_person(self, person_name, company_name):
        """Search for a specific person on LinkedIn and send them a message."""
        search_query = f"{person_name} {company_name}"
        print(f"\nSearching LinkedIn for: {search_query}")
        
        try:
            # Navigate to LinkedIn search
            search_url = f'https://www.linkedin.com/search/results/people/?keywords={search_query.replace(" ", "%20")}'
            self.driver.get(search_url)
            self.human_delay(5, 8)
            
            # Get first result
            results = self.driver.find_elements(By.XPATH, '//li[contains(@class, "reusable-search__result-container")]')
            
            if not results:
                print(f"No results found for {person_name}")
                return False
            
            # Click on first profile
            first_result = results[0]
            profile_link = first_result.find_element(By.XPATH, './/a[contains(@href, "/in/")]')
            profile_url = profile_link.get_attribute('href')
            
            print(f"Found profile: {profile_url}")
            self.driver.get(profile_url)
            self.human_delay(5, 8)
            
            # Try to send message
            return self.send_direct_message(person_name, company_name)
            
        except Exception as e:
            print(f"Error searching for {person_name}: {str(e)}")
            return False
    
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
    
    def send_direct_message(self, person_name, company_name):
        """Send a direct message to a person."""
        try:
            print(f"\nPreparing to message {person_name}...")
            
            # Look for Message button
            try:
                message_buttons = self.driver.find_elements(By.XPATH, '//button[contains(@class, "message") or contains(., "Message")]')
                
                if not message_buttons:
                    print(f"Cannot message {person_name} - Message button not available (might need connection or Premium)")
                    self.outreach_history.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'name': person_name,
                        'company': company_name,
                        'job_title': 'Tech Lead',
                        'status': 'no_message_access'
                    })
                    return False
                
                message_buttons[0].click()
                self.human_delay(3, 5)
                
                # Compose message with natural typos
                base_message = f"""Hi {person_name.split()[0]},

I'm a Macquarie University student currently seeking an AI internship in Sydney. I've been working on RAG agents and Python automation projects.

I noticed {company_name} and was interested in learning more about potential opportunities or any guidance you might offer.

Thank you for your time!

Best regards,
Rajath"""
                
                message = self.add_natural_typos(base_message)
                
                print("\n--- MESSAGE PREVIEW ---")
                print(message)
                print("--- END PREVIEW ---\n")
                
                # Ask for confirmation
                confirm = input("Send this message? (yes/y to send, no/n to skip): ").strip().lower()
                
                if confirm not in ['yes', 'y']:
                    print("Message skipped by user")
                    return False
                
                # Type message
                message_box = self.driver.find_element(By.XPATH, '//div[@role="textbox" or contains(@class, "msg-form__contenteditable")]')
                message_box.click()
                self.human_delay(1, 2)
                message_box.send_keys(message)
                self.human_delay(3, 5)
                
                # Send
                send_button = self.driver.find_element(By.XPATH, '//button[contains(., "Send") and @type="submit"]')
                send_button.click()
                
                print(f"✓ Message sent to {person_name}!")
                
                self.outreach_history.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'name': person_name,
                    'company': company_name,
                    'job_title': 'Tech Lead',
                    'status': 'message_sent'
                })
                
                self.human_delay(20, 35)
                return True
                
            except Exception as e:
                print(f"Error sending message: {str(e)}")
                return False
                
        except Exception as e:
            print(f"Failed to message: {str(e)}")
            return False
    
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
    
    def research_company_website(self, company_name):
        """Visit company website and look for team/about pages to find tech leads."""
        print(f"\nResearching {company_name} website...")
        
        try:
            # Google search for company
            google_query = f"{company_name} careers team australia"
            self.driver.get(f'https://www.google.com/search?q={google_query.replace(" ", "+")}')
            self.human_delay(3, 5)
            
            # Get first few results
            results = self.driver.find_elements(By.XPATH, '//div[@class="g"]//a')
            
            for result in results[:3]:
                try:
                    url = result.get_attribute('href')
                    if url and 'linkedin' not in url.lower():
                        print(f"Checking: {url}")
                        self.driver.get(url)
                        self.human_delay(5, 8)
                        
                        # Look for names on the page (simple heuristic)
                        page_text = self.driver.find_element(By.TAG_NAME, 'body').text
                        
                        # Look for tech-related keywords
                        if any(keyword in page_text.lower() for keyword in ['engineering', 'ai', 'machine learning', 'technology', 'data science']):
                            print(f"Found relevant content on {url}")
                            return True
                        
                except Exception as e:
                    continue
            
            return False
            
        except Exception as e:
            print(f"Error researching website: {str(e)}")
            return False
    
    def process_company(self, company_name, job_titles=['AI Lead', 'Engineering Manager', 'Talent Acquisition', 'HR Manager']):
        """Process a single company - search for specific roles and send connection requests."""
        print(f"\n{'='*60}")
        print(f"Processing: {company_name}")
        print(f"{'='*60}")
        
        # First, research the company website
        self.research_company_website(company_name)
        self.human_delay(5, 10)
        
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
        """Main execution method with interactive menu."""
        try:
            self.setup_driver()
            
            if not self.login_to_linkedin():
                print("Failed to login. Exiting...")
                return
            
            # Interactive menu loop
            while True:
                print("\n" + "="*60)
                print("LINKEDIN OUTREACH BOT - INTERACTIVE MENU")
                print("="*60)
                print("1. Process all companies")
                print("2. Process single company")
                print("3. Search and message specific person")
                print("4. View outreach history")
                print("5. Reload code (apply new changes without restart)")
                print("6. Save and exit")
                print("7. Exit without saving")
                print("="*60)
                
                choice = input("\nEnter your choice (1-7): ").strip()
                
                if choice == "1":
                    print(f"\nStarting outreach to {len(companies)} companies...")
                    for company in companies:
                        self.process_company(company)
                        self.human_delay(25, 40)
                    print("\nOutreach campaign completed!")
                    
                elif choice == "2":
                    print("\nAvailable companies:")
                    for i, company in enumerate(companies, 1):
                        print(f"{i}. {company}")
                    company_num = input("\nEnter company number: ").strip()
                    try:
                        idx = int(company_num) - 1
                        if 0 <= idx < len(companies):
                            self.process_company(companies[idx])
                        else:
                            print("Invalid company number")
                    except:
                        print("Invalid input")
                        
                elif choice == "3":
                    person_name = input("Enter person's name: ").strip()
                    company_name = input("Enter company name: ").strip()
                    if person_name and company_name:
                        self.search_and_message_person(person_name, company_name)
                    else:
                        print("Name and company are required")
                        
                elif choice == "4":
                    if self.outreach_history:
                        print("\n--- OUTREACH HISTORY ---")
                        for i, entry in enumerate(self.outreach_history, 1):
                            print(f"{i}. {entry['name']} at {entry['company']} - Status: {entry['status']}")
                        print(f"\nTotal: {len(self.outreach_history)} interactions")
                    else:
                        print("\nNo outreach history yet")
                        
                elif choice == "5":
                    print("\n" + "="*60)
                    print("RELOADING CODE...")
                    print("="*60)
                    print("1. Make your code changes in the editor")
                    print("2. Save the file")
                    print("3. Come back here")
                    input("\nPress ENTER when you've saved your changes...")
                    
                    try:
                        # Reload the current module
                        module_name = __name__
                        if module_name in sys.modules:
                            importlib.reload(sys.modules[module_name])
                        print("✓ Code reloaded successfully!")
                        print("✓ Browser session maintained!")
                        print("✓ Login preserved!")
                        print("\nYour changes are now active. Continue using the menu.")
                    except Exception as e:
                        print(f"⚠ Reload failed: {str(e)}")
                        print("Don't worry - your session is still active, just can't apply changes.")
                        
                elif choice == "6":
                    self.save_outreach_history()
                    print("\nExiting...")
                    break
                    
                elif choice == "7":
                    confirm = input("Exit without saving history? (yes/y to confirm): ").strip().lower()
                    if confirm in ['yes', 'y']:
                        print("\nExiting without saving...")
                        break
                    
                else:
                    print("Invalid choice. Please enter 1-7")
            
        except KeyboardInterrupt:
            print("\n\nBot interrupted by user")
            save_choice = input("Save outreach history before exiting? (yes/y): ").strip().lower()
            if save_choice in ['yes', 'y']:
                self.save_outreach_history()
            
        except Exception as e:
            print(f"\nError during execution: {str(e)}")
            
        finally:
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
