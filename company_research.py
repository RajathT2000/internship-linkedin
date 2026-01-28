"""
AI Internship Company Finder
Searches job boards and filters for relevant AI/ML internships
"""

import time
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
        self.companies_list = []
        
    def setup_driver(self):
        """Setup undetected ChromeDriver."""
        print("Setting up Chrome driver...")
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)
        print("Chrome driver ready!")
    
    def is_relevant_ai_internship(self, job_description):
        """Check if the job description is actually for AI/ML/tech internship."""
        description_lower = job_description.lower()
        
        # Positive keywords - must have at least one
        positive_keywords = [
            'artificial intelligence', 'machine learning', 'ai', 'ml', 'data science',
            'python', 'tensorflow', 'pytorch', 'deep learning', 'neural network',
            'computer vision', 'nlp', 'natural language', 'data analysis', 'software',
            'algorithm', 'model', 'automation', 'programming', 'coding'
        ]
        
        # Negative keywords - if present, likely not relevant
        negative_keywords = [
            'medical intern', 'clinical', 'hospital', 'patient care', 'nursing',
            'physician', 'doctor', 'healthcare provider', 'medical student',
            'residency', 'clinical rotation'
        ]
        
        # Check for negative keywords first
        if any(keyword in description_lower for keyword in negative_keywords):
            return False
        
        # Check for positive keywords
        if any(keyword in description_lower for keyword in positive_keywords):
            return True
        
        return False
    
    def search_job_boards_for_companies(self):
        """Search job boards for companies offering AI internships in Sydney."""
        print("\n" + "="*60)
        print("SEARCHING JOB BOARDS FOR AI INTERNSHIPS")
        print("="*60)
        
        companies_found = {}  # {company_name: job_description}
        job_boards = [
            ('Seek', 'https://www.seek.com.au/ai-internship-jobs/in-Sydney-NSW?daterange=31'),
            ('Indeed', 'https://au.indeed.com/jobs?q=ai+internship+OR+machine+learning+internship&l=Sydney+NSW'),
            ('Jora', 'https://au.jora.com/jobs?q=ai+internship&l=Sydney+NSW')
        ]
        
        for board_name, url in job_boards:
            try:
                print(f"\nSearching {board_name}...")
                self.driver.get(url)
                time.sleep(3)
                
                # Extract company names and job descriptions
                if board_name == 'Seek':
                    job_cards = self.driver.find_elements(By.XPATH, '//article[@data-automation="normalJob"]')
                    
                    for card in job_cards[:50]:
                        try:
                            company_elem = card.find_element(By.XPATH, './/a[@data-automation="jobCompany"]')
                            company_name = company_elem.text.strip()
                            
                            # Click to see full description
                            try:
                                card.click()
                                time.sleep(1)
                                
                                # Get job description
                                desc_elem = self.driver.find_element(By.XPATH, '//div[@data-automation="jobAdDetails"]')
                                job_description = desc_elem.text
                                
                                # Check if relevant
                                if company_name and self.is_relevant_ai_internship(job_description):
                                    if company_name not in companies_found:
                                        companies_found[company_name] = job_description[:200]
                                        print(f"  ✓ {company_name}")
                                else:
                                    print(f"  ✗ {company_name} (not relevant AI internship)")
                            except:
                                continue
                                
                        except:
                            continue
                
                elif board_name == 'Indeed':
                    job_cards = self.driver.find_elements(By.XPATH, '//div[contains(@class, "job_seen_beacon")]')
                    
                    for card in job_cards[:50]:
                        try:
                            company_elem = card.find_element(By.XPATH, './/span[@class="companyName"]')
                            company_name = company_elem.text.strip()
                            
                            # Try to get job description
                            try:
                                card.click()
                                time.sleep(1)
                                
                                desc_elem = self.driver.find_element(By.XPATH, '//div[@id="jobDescriptionText"]')
                                job_description = desc_elem.text
                                
                                if company_name and self.is_relevant_ai_internship(job_description):
                                    if company_name not in companies_found:
                                        companies_found[company_name] = job_description[:200]
                                        print(f"  ✓ {company_name}")
                                else:
                                    print(f"  ✗ {company_name} (not relevant AI internship)")
                            except:
                                continue
                                
                        except:
                            continue
                
                else:  # Jora
                    job_links = self.driver.find_elements(By.XPATH, '//a[contains(@class, "job-link")]')
                    
                    for link in job_links[:50]:
                        try:
                            # Get company name from nearby element
                            parent = link.find_element(By.XPATH, './..')
                            company_elem = parent.find_element(By.XPATH, './/div[contains(@class, "company")]')
                            company_name = company_elem.text.strip()
                            
                            # Click to see description
                            try:
                                link.click()
                                time.sleep(1)
                                
                                desc_elem = self.driver.find_element(By.XPATH, '//div[contains(@class, "description")]')
                                job_description = desc_elem.text
                                
                                if company_name and self.is_relevant_ai_internship(job_description):
                                    if company_name not in companies_found:
                                        companies_found[company_name] = job_description[:200]
                                        print(f"  ✓ {company_name}")
                                else:
                                    print(f"  ✗ {company_name} (not relevant AI internship)")
                            except:
                                continue
                                
                        except:
                            continue
                
                if len(companies_found) >= 100:
                    print(f"\n✓ Reached 100 companies!")
                    break
                    
            except Exception as e:
                print(f"Error searching {board_name}: {str(e)}")
                continue
        
        companies_list = list(companies_found.keys())[:100]
        print(f"\n✓ Found {len(companies_list)} relevant AI internship companies")
        return companies_list
    
    def find_company_website(self, company_name):
        """Find and verify the official website of a company."""
        try:
            # Open new tab for website verification
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            search_query = f"{company_name} Sydney Australia official website"
            google_url = f'https://www.google.com/search?q={search_query.replace(" ", "+")}'
            
            self.driver.get(google_url)
            time.sleep(2)
            
            # Get first result that's not LinkedIn, Indeed, Seek, etc.
            links = self.driver.find_elements(By.XPATH, '//div[@class="g"]//a')
            
            for link in links[:5]:
                try:
                    url = link.get_attribute('href')
                    if url and not any(x in url.lower() for x in ['linkedin', 'indeed', 'seek', 'jora', 'google', 'facebook', 'youtube']):
                        print(f"  Verifying website: {url}")
                        
                        # Try to visit the website to verify it exists
                        try:
                            self.driver.get(url)
                            time.sleep(2)
                            
                            # Check if page loaded successfully
                            if "404" not in self.driver.title and "not found" not in self.driver.title.lower():
                                print(f"  ✓ Website verified: {url}")
                                # Close verification tab
                                self.driver.close()
                                self.driver.switch_to.window(self.driver.window_handles[0])
                                return url
                            else:
                                print(f"  ✗ Website not accessible (404)")
                        except:
                            print(f"  ✗ Website failed to load")
                            continue
                except:
                    continue
            
            # Close verification tab and return to main tab
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            print(f"  ✗ No valid website found for {company_name}")
            return None
            
        except Exception as e:
            # Make sure we're back to main tab
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            print(f"Error finding website: {str(e)}")
            return None
    
    def scrape_team_members_from_website(self, company_name, website_url):
        """Scrape team member information from company website."""
        print(f"\nScraping {website_url} for team members...")
        
        team_members = []
        
        try:
            # Open new tab for scraping
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Visit website
            self.driver.get(website_url)
            time.sleep(3)
            
            # Look for team/about/people pages
            team_page_keywords = ['team', 'about', 'people', 'leadership', 'staff', 'our-team', 'about-us']
            team_page_url = None
            
            # Find links to team pages
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.lower()
                    
                    if href and any(keyword in href.lower() or keyword in text for keyword in team_page_keywords):
                        team_page_url = href
                        print(f"  Found team page: {team_page_url}")
                        break
                except:
                    continue
            
            # Visit team page if found
            if team_page_url:
                self.driver.get(team_page_url)
                time.sleep(3)
            
            # Extract text content
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Look for names (simple heuristic: capitalized words, 2-4 words)
            name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
            potential_names = re.findall(name_pattern, page_text)
            
            # Filter for likely real names
            common_titles = ['CEO', 'CTO', 'Director', 'Manager', 'Lead', 'Engineer', 'Developer', 'Designer', 'Analyst']
            
            # Look for LinkedIn links on the page
            linkedin_links = self.driver.find_elements(By.XPATH, '//a[contains(@href, "linkedin.com/in/")]')
            linkedin_profiles = {}
            
            for link in linkedin_links:
                try:
                    url = link.get_attribute('href')
                    # Try to find associated name nearby
                    parent = link.find_element(By.XPATH, './../..')
                    nearby_text = parent.text
                    
                    for name in potential_names:
                        if name in nearby_text:
                            linkedin_profiles[name] = url
                            break
                except:
                    continue
            
            # Extract team members
            seen_names = set()
            for name in potential_names:
                # Skip common non-names
                if name in seen_names or len(name) < 5:
                    continue
                    
                # Check if it's near a job title
                context_start = max(0, page_text.find(name) - 100)
                context_end = min(len(page_text), page_text.find(name) + 100)
                context = page_text[context_start:context_end].lower()
                
                has_title = any(title.lower() in context for title in common_titles)
                
                if has_title or name in linkedin_profiles:
                    team_member = {
                        'name': name,
                        'company': company_name,
                        'linkedin_url': linkedin_profiles.get(name, 'Not found'),
                        'source': 'company_website'
                    }
                    team_members.append(team_member)
                    seen_names.add(name)
                    print(f"  ✓ Found: {name}")
                    
                    if len(team_members) >= 2:
                        break
            
            # If not enough found, search Google for company team members
            if len(team_members) < 2:
                print(f"  Only found {len(team_members)} on website, searching Google...")
                google_members = self.search_google_for_team_members(company_name)
                team_members.extend(google_members)
            
            # Close scraping tab and return to main tab
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return team_members[:2]  # Return max 2
            
        except Exception as e:
            # Make sure we're back to main tab
            if len(self.driver.window_handles) > 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            print(f"Error scraping website: {str(e)}")
            return []
    
    def search_google_for_team_members(self, company_name):
        """Search Google for team members if website scraping fails."""
        try:
            search_query = f"{company_name} Sydney team members site:linkedin.com/in"
            google_url = f'https://www.google.com/search?q={search_query.replace(" ", "+")}'
            
            self.driver.get(google_url)
            time.sleep(2)
            
            team_members = []
            links = self.driver.find_elements(By.XPATH, '//a[@href]')
            
            for link in links[:5]:
                try:
                    url = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if url and 'linkedin.com/in/' in url and text and len(text.split()) >= 2:
                        # Clean URL
                        if 'url?q=' in url:
                            url = url.split('url?q=')[1].split('&')[0]
                        
                        team_member = {
                            'name': text,
                            'company': company_name,
                            'linkedin_url': url,
                            'source': 'google_search'
                        }
                        team_members.append(team_member)
                        print(f"  ✓ Found via Google: {text}")
                        
                        if len(team_members) >= 2:
                            break
                except:
                    continue
            
            return team_members
            
        except Exception as e:
            print(f"Error searching Google: {str(e)}")
            return []
    
    def save_results(self, companies):
        """Save company list to files."""
        print("\n" + "="*60)
        print("SAVING RESULTS")
        print("="*60)
        
        # Save to CSV
        df = pd.DataFrame({'Company Name': companies})
        df.to_csv('ai_internship_companies.csv', index=False)
        print(f"✓ Saved {len(companies)} companies to ai_internship_companies.csv")
        
        # Save to text file
        with open('company_list.txt', 'w', encoding='utf-8') as f:
            f.write("AI INTERNSHIP COMPANIES - SYDNEY, AUSTRALIA\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            for i, company in enumerate(companies, 1):
                f.write(f"{i}. {company}\n")
        
        print(f"✓ Saved company list to company_list.txt")
        print(f"\nTotal: {len(companies)} AI internship companies")
    
    def run(self):
        """Main execution method."""
        try:
            self.setup_driver()
            
            print("\nStarting automatic search...")
            
            # Search job boards and filter
            companies = self.search_job_boards_for_companies()
            
            print("\n" + "="*60)
            print("SEARCH COMPLETED!")
            print("="*60)
            print(f"Found {len(companies)} relevant AI internship companies")
            
            self.save_results(companies)
            
        except KeyboardInterrupt:
            print("\n\nSearch interrupted by user")
            if self.companies_list:
                self.save_results(self.companies_list)
            
        except Exception as e:
            print(f"\nError during search: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            if self.driver:
                print("\nClosing browser...")
                time.sleep(2)
                self.driver.quit()


def main():
    """Main entry point."""
    print("="*60)
    print("AI INTERNSHIP COMPANY FINDER")
    print("Sydney, Australia")
    print("="*60)
    print("\nSearching job boards for AI/ML internships...")
    print("Filtering out medical internships and non-tech roles...")
    print("Target: 100 companies\n")
    
    researcher = CompanyResearcher()
    researcher.run()
    
    print("\n✓ Results saved!")
    print("  - ai_internship_companies.csv")
    print("  - company_list.txt")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
        
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
