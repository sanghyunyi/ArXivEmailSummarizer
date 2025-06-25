from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

import smtplib
from email.mime.text import MIMEText

import base64
import time
from datetime import datetime

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv("../.env")

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']  # or modify if you need write/send access


def get_gmail_service():
    creds = None

    # ✅ Load token if it exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 🔄 Refresh or re-login if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 💾 Save the credentials for next time
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def fetch_emails(service, max_results=10):
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    email_texts = []
    
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_data['payload']
        parts = payload.get('parts', [])
        data = None
        
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                break
        
        if data:
            import base64
            decoded = base64.urlsafe_b64decode(data).decode('utf-8')
            email_texts.append(decoded)
    
    return email_texts


def fetch_filtered_emails(service, max_results=10):
    results = service.users().messages().list(
        userId='me',
        q='from:no-reply@arxiv.org',
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    email_texts = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', id=msg['id'], format='full'
        ).execute()

        headers = msg_data['payload']['headers']
        to_header = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
        from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')

        if 'rabble@arxiv.org' in to_header and 'no-reply@arxiv.org' in from_header:
            body_data = msg_data['payload']['body'].get('data')
            if body_data:
                try:
                    decoded = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
                    email_texts.append(decoded)
                except Exception as e:
                    print(f"⚠️ Failed to decode body: {e}")
            else:
                print("⚠️ No body data found in payload.")
    
    return email_texts


def fetch_filtered_emails(service, max_results=100):
    # Get timestamp for 240 hours ago
    timestamp_240h_ago = int(time.time()) - 240 * 60 * 60
    query = f'from:no-reply@arxiv.org after:{timestamp_240h_ago}'

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    email_data = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId='me', id=msg['id'], format='full'
        ).execute()

        headers = msg_data['payload']['headers']
        to_header = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
        from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')

        if 'rabble@arxiv.org' in to_header and 'no-reply@arxiv.org' in from_header:
            body_data = msg_data['payload']['body'].get('data')
            if body_data:
                try:
                    decoded = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')

                    # Extract and convert timestamp
                    internal_timestamp = int(msg_data.get('internalDate', '0')) // 1000
                    dt_string = datetime.fromtimestamp(internal_timestamp).strftime('%Y-%m-%d %H:%M:%S')

                    email_data.append({
                        "timestamp": internal_timestamp,
                        "datetime": dt_string,
                        "text": decoded
                    })

                except Exception as e:
                    print(f"⚠️ Failed to decode body: {e}")
            else:
                print("⚠️ No body data found in payload.")

    return email_data


def summarize_email(email_text, key_words):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Among the papers in the following emails, select and return the papers that are most relevant to the key words. 
    Provide the exact title, abstract, and link of the relevant papers from the original email.
    Do not summarize the papers in your own words.
    Just return the title, abstract, and link of the relevant papers.
    
    Key words: {key_words}
    
    Email:
    {email_text}
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0  # 🔥 Set temperature to 0 for deterministic output
            )
        )
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ Error summarizing email: {e}")
        return None


def send_email_summary(summary_text, datetime):
    sender = os.getenv("GMAIL_EMAIL")
    receiver = os.getenv("GMAIL_EMAIL")
    password = os.getenv("GMAIL_PASSWORD")  # Get from Google App Passwords (if 2FA enabled)

    msg = MIMEText(summary_text)
    msg['Subject'] = f"🧠 ArXiv Email Summary {datetime}"
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
