ArXiv Email Summarizer with Gemini
==================================

Automatically fetch, filter, and summarize recent arXiv update emails using Google Gemini API, and send the summarized results to your inbox daily.

----------------------------------
FEATURES
----------------------------------

- Connects to your Gmail using Gmail API
- Filters emails from `no-reply@arxiv.org` sent to a specific address (e.g., `rabble@arxiv.org`)
- Extracts and decodes email contents (plain text)
- Uses Gemini 1.5 Flash to summarize relevant papers based on keywords (e.g., "RAG, AI, LLM")
- Sends a concise summary email back to you
- Avoids reprocessing previously summarized emails
- Runs daily in the background via cron

----------------------------------
REQUIREMENTS
----------------------------------

- Python 3.8+
- Gmail account with 2FA enabled
- Google Cloud Project with Gmail API enabled
- Google AI API Key for Gemini

----------------------------------
SETUP INSTRUCTIONS
----------------------------------

1. Clone the Repository

   git clone https://github.com/yourname/arxiv-mail-summarizer.git
   cd arxiv-mail-summarizer

2. Create `.env` File

```env
   GEMINI_API_KEY=<your_gemini_api_key_here>
   GMAIL_PASSWORD=<your_gmail_app_password>
```

   ⚠️ Do NOT commit this file. Add it to `.gitignore`.

3. Setup Gmail API Credentials

   - Go to: https://console.cloud.google.com/
   - Enable Gmail API
   - Download `credentials.json` and place it in the root directory
   - First run will open a browser for Gmail OAuth — token will be saved as `token.json`

----------------------------------
USAGE
----------------------------------

Run Manually:

   python main.py

Run Automatically (Every 24 Hours):

   On Linux/macOS:
   Run `crontab -e`, then add:

   0 8 * * * /usr/bin/python3 /full/path/to/main.py >> /tmp/arxiv_summary.log 2>&1

----------------------------------
CUSTOMIZATION
----------------------------------

- Change `key_words` in the `main()` logic
- Modify email filters in `fetch_filtered_emails()`
- Use `gemini-1.5-pro` for more detailed output (note quota)

----------------------------------
SECURITY
----------------------------------

- Uses OAuth with cached `token.json`
- Uses Gmail App Password for SMTP
- Do not expose `.env`, `token.json`, or `credentials.json`

----------------------------------
EXAMPLE OUTPUT
----------------------------------

Subject:
   🧠 ArXiv Email Summary 2025-06-14 13:58:01

Body:
   • [Paper Title]
     Summary: ...
     Link: https://arxiv.org/abs/...

   • [Another Paper Title]
     Summary: ...
     Link: https://arxiv.org/abs/...

----------------------------------
LICENSE
----------------------------------

MIT License
