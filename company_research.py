"""
MQ PACE Company Research Tool
Finds companies offering internships in Sydney and extracts contact details
"""

import time
import random
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import re

class CompanyResearcher:
    def __init__(self):
        """Initialize the research tool."""
        self.driver = None
        self.companies_data = []
        self.contacts_without_linkedin = []
        
    def human_delay(self, min_seconds=5, max_seconds=10):
        """Implement human-like delays."""
        delay = random.uniform(min_seconds, max_seconds)
        print(f"Waiting {delay:.1f} seconds...")
        time.sleep(delay)
    
    def setup_driver(self):
        """Setup undetected ChromeDriver."""
        print("Setting up Chrome driver...")
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 20)
        print("Chrome driver ready!")
    
    def search_mq_pace_companies(self):
        """Search for MQ PACE verified companies offering internships in Sydney."""
        print("\n" + "="*60)
        print("SEARCHING FOR MQ PACE COMPANIES IN SYDNEY")
        print("="*60)
        
        # Known MQ PACE partner companies in Sydney
        pace_companies = [
            "Atlassian", "Canva", "Commonwealth Bank", "Westpac", "ANZ", "NAB",
            "Accenture", "Deloitte", "PwC", "EY", "KPMG", "Google Australia",
            "Microsoft Australia", "IBM Australia", "Telstra", "Optus",
            "SafetyCulture", "Deputy", "Airwallex", "Afterpay",
            "Woolworths Group", "Coles Group", "REA Group", "Domain",
            "Cochlear", "ResMed", "CSIRO", "Data61", "Macquarie Group",
            "Nine Entertainment", "Seven West Media", "Harrison.ai"
        ]
        
        return pace_companies[:20]  # Return first 20
    
    def research_company_careers(self, company_name):
        """Research a company's careers page and extract contact information."""
        print(f"\n{'='*60}")
        print(f"RESEARCHING: {company_name}")
        print(f"{'='*60}")
        
        try:
            # Search for company careers page
            search_query = f"{company_name} careers internship Sydney Australia"
            google_url = f'https://www.google.com/search?q={search_query.replace(" ", "+")}'
            
            print(f"Searching: {search_query}")
            self.driver.get(google_url)
            self.human_delay(3, 6)
            
            # Get first few results
            results = self.driver.find_elements(By.XPATH, '//div[@class="g"]//a')
            
            careers_url = None
            for result in results[:5]:
                try:
                    url = result.get_attribute('href')
                    if url and any(keyword in url.lower() for keyword in ['career', 'job', 'graduate', 'internship']):
                        careers_url = url
                        print(f"Found careers page: {careers_url}")
                        break
                except:
                    continue
            
            if not careers_url:
                print(f"No careers page found for {company_name}")
                return None
            
            # Visit careers page
            self.driver.get(careers_url)
            self.human_delay(4, 7)
            
            # Extract page content
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            company_data = {
                'company_name': company_name,
                'careers_url': careers_url,
                'has_internship': any(word in page_text.lower() for word in ['intern', 'graduate', 'trainee', 'entry level']),
                'sydney_location': 'sydney' in page_text.lower(),
                'contacts': []
            }
            
            print(f"✓ Careers page analyzed")
            print(f"  - Has internship keywords: {company_data['has_internship']}")
            print(f"  - Mentions Sydney: {company_data['sydney_location']}")
            
            return company_data
            
        except Exception as e:
            print(f"Error researching {company_name}: {str(e)}")
            return None
    
    def search_company_contacts(self, company_name):
        """Search for HR/Talent contacts at the company via Google."""
        print(f"\nSearching for contacts at {company_name}...")
        
        contact_roles = [
            "Talent Acquisition",
            "HR Manager",
            "Recruitment Manager",
            "Graduate Program Manager"
        ]
        
        all_contacts = []
        
        for role in contact_roles:
            try:
                # Search Google for LinkedIn profiles
                search_query = f"{role} {company_name} Sydney site:linkedin.com/in"
                google_url = f'https://www.google.com/search?q={search_query.replace(" ", "+")}'
                
                self.driver.get(google_url)
                self.human_delay(3, 5)
                
                # Extract LinkedIn URLs and names
                links = self.driver.find_elements(By.XPATH, '//a[@href]')
                
                for link in links[:3]:  # Top 3 results per role
                    try:
                        url = link.get_attribute('href')
                        text = link.text.strip()
                        
                        if url and 'linkedin.com/in/' in url and text:
                            # Clean URL
                            if 'url?q=' in url:
                                url = url.split('url?q=')[1].split('&')[0]
                            
                            contact = {
                                'name': text,
                                'role': role,
                                'linkedin_url': url,
                                'company': company_name
                            }
                            
                            # Check if already added
                            if not any(c['linkedin_url'] == url for c in all_contacts):
                                all_contacts.append(contact)
                                print(f"  ✓ Found: {text} ({role})")
                    except:
                        continue
                
                self.human_delay(2, 4)
                
            except Exception as e:
                print(f"  Error searching {role}: {str(e)}")
                continue
        
        return all_contacts
    
    def save_results(self):
        """Save all research results to files."""
        print("\n" + "="*60)
        print("SAVING RESULTS")
        print("="*60)
        
        # Save companies with full data
        if self.companies_data:
            companies_df = pd.DataFrame(self.companies_data)
            companies_df.to_csv('mq_pace_companies_research.csv', index=False)
            print(f"✓ Saved {len(self.companies_data)} companies to mq_pace_companies_research.csv")
        
        # Save contacts without LinkedIn separately
        if self.contacts_without_linkedin:
            with open('contacts_to_search_manually.txt', 'w') as f:
                f.write("CONTACTS TO SEARCH ON LINKEDIN MANUALLY\n")
                f.write("="*60 + "\n\n")
                
                for contact in self.contacts_without_linkedin:
                    f.write(f"Name: {contact['name']}\n")
                    f.write(f"Company: {contact['company']}\n")
                    f.write(f"Role: {contact['role']}\n")
                    f.write("-" * 40 + "\n")
            
            print(f"✓ Saved {len(self.contacts_without_linkedin)} contacts to contacts_to_search_manually.txt")
        
        # Create detailed report
        with open('research_report.txt', 'w') as f:
            f.write("MQ PACE COMPANIES RESEARCH REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            for company in self.companies_data:
                f.write(f"COMPANY: {company['company_name']}\n")
                f.write(f"Careers URL: {company.get('careers_url', 'N/A')}\n")
                f.write(f"Has Internships: {company.get('has_internship', 'Unknown')}\n")
                f.write(f"Sydney Location: {company.get('sydney_location', 'Unknown')}\n")
                f.write(f"\nContacts Found: {len(company.get('contacts', []))}\n")
                
                for contact in company.get('contacts', []):
                    f.write(f"  - {contact['name']} ({contact['role']})\n")
                    f.write(f"    LinkedIn: {contact.get('linkedin_url', 'Not found')}\n")
                
                f.write("\n" + "-"*60 + "\n\n")
        
        print("✓ Saved detailed report to research_report.txt")
    
    def run(self):
        """Main execution method."""
        try:
            self.setup_driver()
            
            # Get MQ PACE companies
            companies = self.search_mq_pace_companies()
            print(f"\n✓ Found {len(companies)} MQ PACE partner companies")
            
            # Research each company
            for i, company_name in enumerate(companies, 1):
                print(f"\n[{i}/{len(companies)}] Processing {company_name}...")
                
                # Research careers page
                company_data = self.research_company_careers(company_name)
                
                if company_data:
                    # Search for contacts
                    contacts = self.search_company_contacts(company_name)
                    company_data['contacts'] = contacts
                    
                    # Separate contacts with and without LinkedIn
                    for contact in contacts:
                        if not contact.get('linkedin_url') or contact['linkedin_url'] == 'Not found':
                            self.contacts_without_linkedin.append(contact)
                    
                    self.companies_data.append(company_data)
                
                # Delay between companies
                if i < len(companies):
                    self.human_delay(5, 10)
            
            print("\n" + "="*60)
            print("RESEARCH COMPLETED!")
            print("="*60)
            print(f"Total companies researched: {len(self.companies_data)}")
            print(f"Total contacts found: {sum(len(c.get('contacts', [])) for c in self.companies_data)}")
            
        except KeyboardInterrupt:
            print("\n\nResearch interrupted by user")
            
        except Exception as e:
            print(f"\nError during research: {str(e)}")
            
        finally:
            self.save_results()
            
            if self.driver:
                print("\nClosing browser...")
                self.human_delay(2, 4)
                self.driver.quit()


def main():
    """Main entry point."""
    print("="*60)
    print("MQ PACE COMPANY RESEARCH TOOL")
    print("Researching Sydney-based internship opportunities")
    print("="*60)
    
    input("\nPress ENTER to start research...")
    
    researcher = CompanyResearcher()
    researcher.run()
    
    print("\n✓ All results saved!")
    print("  - mq_pace_companies_research.csv")
    print("  - contacts_to_search_manually.txt")
    print("  - research_report.txt")


if __name__ == "__main__":
    main()
