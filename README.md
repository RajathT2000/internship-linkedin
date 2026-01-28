# LinkedIn PACE Outreach Agent

A professional LinkedIn automation tool built in Python to help Macquarie University students find and connect with AI leads and Engineering Managers at MQ PACE partner companies.

## Features

- **Automated LinkedIn Login**: Securely logs into LinkedIn using credentials from `.env` file
- **Smart Search**: Searches for 'AI Lead' and 'Engineering Manager' roles at specified companies
- **Personalized Outreach**: Drafts customized connection requests highlighting your skills
- **Anti-Detection**: Implements human-like delays (10-20 seconds) between actions
- **Activity Logging**: Tracks all outreach attempts in `outreach_history.csv`
- **Undetected Chrome**: Uses undetected-chromedriver to avoid automation detection

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "Internship- linkedin"
```

### 2. Create virtual environment

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

Create a `.env` file (copy from `.env.example`):

```bash
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password_here
```

### 5. Configure MQ PACE Partners

Edit `pace_partners.txt` and add company names (one per line):

```
Atlassian
Accenture
Commonwealth Bank
```

## Usage

Run the bot:

```bash
python linkedin_outreach_bot.py
```

The bot will:
1. Log into LinkedIn
2. Search for AI leads and Engineering Managers at each company
3. Send personalized connection requests
4. Log all activity to `outreach_history.csv`

## Safety Features

- **Human-like delays**: 10-20 second delays between actions
- **Randomized timing**: Adds variance to appear more natural
- **Rate limiting**: Built-in delays between companies and searches
- **Activity logging**: Complete audit trail of all actions

## Project Structure

```
├── linkedin_outreach_bot.py    # Main automation script
├── pace_partners.txt            # List of companies to target
├── requirements.txt             # Python dependencies
├── .env                         # LinkedIn credentials (not tracked)
├── .env.example                 # Template for credentials
├── outreach_history.csv         # Activity log (created on first run)
└── README.md                    # This file
```

## Important Notes

⚠️ **Use Responsibly**: LinkedIn has automation policies. This tool implements delays and human-like behavior, but use at your own risk.

⚠️ **Account Safety**: Start with a small batch of companies to test. Don't run continuously for hours.

⚠️ **Credential Security**: Never commit your `.env` file. It's in `.gitignore` by default.

## Troubleshooting

**Login fails**: Check your credentials in `.env` file
**No results found**: Verify company names in `pace_partners.txt`
**Chrome crashes**: Update Chrome to latest version
**Detection issues**: The tool uses undetected-chromedriver, but LinkedIn may still detect automation

## Technologies

- Python 3.8+
- undetected-chromedriver
- Selenium WebDriver
- pandas
- python-dotenv

## License

MIT License - Use at your own risk

## Author

Built for Macquarie University PACE program students seeking AI internships.
