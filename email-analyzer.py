import argparse
from email import message_from_string
from email.header import decode_header

def parse_email(raw_email):
    email_data = {}
    msg = message_from_string(raw_email)
    
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
                email_data['Content'] = part.get_payload(decode=True).decode()
    else:
        email_data['Content'] = msg.get_payload()
    
    return email_data

def generate_html_summary(email_data):
    html_content = f"""
    <h2>Email Summary</h2>
    <ul>
        <li><strong>From:</strong> {email_data.get('From', 'N/A')}</li>
        <li><strong>To:</strong> {email_data.get('To', 'N/A')}</li>
        <li><strong>Date:</strong> {email_data.get('Date', 'N/A')}</li>
        <li><strong>Subject:</strong> {email_data.get('Subject', 'N/A')}</li>
        <li><strong>DKIM:</strong> {email_data.get('DKIM', 'N/A')}</li>
        <li><strong>SPF:</strong> {email_data.get('SPF', 'N/A')}</li>
        <li><strong>DMARC:</strong> {email_data.get('DMARC', 'N/A')}</li>
    </ul>
    <h3>Content:</h3>
    <div>{email_data.get('Content', 'N/A')}</div>
    """
    return html_content

def main():
    parser = argparse.ArgumentParser(description='Analyze raw email text and produce an HTML summary.')
    parser.add_argument('-i', '--input', help='Input file containing raw email text.', required=True)
    
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        raw_emails = f.read()
    
    # Assuming each email is separated by '---END OF EMAIL---'
    emails = raw_emails.split('---END OF EMAIL---')
    
    for email in emails:
        email_data = parse_email(email.strip())
        html_summary = generate_html_summary(email_data)
        print(html_summary)

if __name__ == "__main__":
    main()
