import json, os
from summarizer import get_gmail_service, fetch_filtered_emails, summarize_email, send_email_summary

PROCESSED_IDS_FILE = "processed_ids.json"

def load_processed_ids():
    if os.path.exists(PROCESSED_IDS_FILE):
        with open(PROCESSED_IDS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_ids(ids):
    with open(PROCESSED_IDS_FILE, "w") as f:
        json.dump(list(ids), f)

def main():
    service = get_gmail_service()
    processed_ids = load_processed_ids()
    new_processed_ids = set()

    emails = fetch_filtered_emails(service, max_results=10)[:1]  # recent batch

    for email in emails:
        msg_id = str(email["timestamp"])  # use timestamp as unique ID (can also use Gmail's real msg_id)
        if msg_id in processed_ids:
            continue  # skip already summarized emails

        summary = summarize_email(email['text'], key_words="RAG, AI, LLM")
        if summary:
            send_email_summary(summary, email['datetime'])
            new_processed_ids.add(msg_id)

    if new_processed_ids:
        processed_ids.update(new_processed_ids)
        save_processed_ids(processed_ids)
    else:
        print("✅ No new relevant emails to summarize.")

if __name__ == "__main__":
    main()
