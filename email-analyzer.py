import argparse
from email import message_from_string, policy
from email.header import decode_header
import logging
import html
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_email(raw_email):
    email_data = {}
    try:
        msg = message_from_string(raw_email, policy=policy.default)
        email_data['From'] = msg.get('From')
        email_data['To'] = msg.get('To')
        email_data['Date'] = msg.get('Date')
        email_data['Subject'] = msg.get('Subject')
        email_data['DKIM'] = msg.get('DKIM-Signature')
        email_data['SPF'] = msg.get('Received-SPF')
        email_data['DMARC'] = msg.get('ARC-Authentication-Results')

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    email_data['Content'] = part.get_payload(decode=True).decode(errors='replace')
                    break
        else:
            email_data['Content'] = msg.get_payload(decode=True).decode(errors='replace')

    except Exception as e:
        logging.error(f"Error parsing email: {e}")
    
    return email_data

def generate_html_summary(email_data):
    sanitized_content = html.escape(email_data.get('Content', 'N/A'))
    html_content = f"""
    <h2>Email Summary</h2>
    <ul>
        <li><strong>From:</strong> {html.escape(email_data.get('From', 'N/A'))}</li>
        <li><strong>To:</strong> {html.escape(email_data.get('To', 'N/A'))}</li>
        <li><strong>Date:</strong> {html.escape(email_data.get('Date', 'N/A'))}</li>
        <li><strong>Subject:</strong> {html.escape(email_data.get('Subject', 'N/A'))}</li>
        <li><strong>DKIM:</strong> {html.escape(email_data.get('DKIM', 'N/A'))}</li>
        <li><strong>SPF:</strong> {html.escape(email_data.get('SPF', 'N/A'))}</li>
        <li><strong>DMARC:</strong> {html.escape(email_data.get('DMARC', 'N/A'))}</li>
    </ul>
    <h3>Content:</h3>
    <div>{sanitized_content}</div>
    """
    return html_content

def main():
    parser = argparse.ArgumentParser(description='Analyze raw email text and produce an HTML summary.')
    parser.add_argument('-i', '--input', help='Input file containing raw email text.', required=True)
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.input):
        logging.error(f"Input file {args.input} does not exist.")
        return

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            raw_emails = f.read()
        
        # Assuming each email is separated by '---END OF EMAIL---'
        emails = raw_emails.split('---END OF EMAIL---')

        for email in emails:
            if email.strip():
                email_data = parse_email(email.strip())
                html_summary = generate_html_summary(email_data)
                print(html_summary)
    
    except Exception as e:
        logging.error(f"Error reading input file: {e}")

if __name__ == "__main__":
    main()
