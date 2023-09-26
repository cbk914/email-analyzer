import os
from dotenv import load_dotenv
import argparse
from email import message_from_string
from email.header import decode_header

# Load API keys from .env file
load_dotenv()

# Initialize API keys
API_KEYS = {
    'HAVEIBEENPWNED': os.getenv("HAVEIBEENPWNED_API_KEY"),
    'CRIMINAL_IP': os.getenv("CRIMINAL_IP_API_KEY"),
    'SHODAN': os.getenv("SHODAN_API_KEY"),
    'CENSYS': os.getenv("CENSYS_API_KEY"),
    'VIRUSTOTAL': os.getenv("VIRUSTOTAL_API_KEY"),
    'HUNTER': os.getenv("HUNTER_API_KEY"),
    'IPINFO': os.getenv("IPINFO_API_KEY"),
    'FULLCONTACT': os.getenv("FULLCONTACT_API_KEY"),
    'OPENWEATHERMAP': os.getenv("OPENWEATHERMAP_API_KEY")
}

def make_api_request(service, query):
    if not API_KEYS.get(service):
        print(f"Skipping {service} as API key is not provided.")
        return None
    
    if not query:
        print(f"Skipping {service} as query is empty.")
        return None
    
    try:
        if service == 'HAVEIBEENPWNED':
            return haveibeenpwned(query)
        elif service == 'CRIMINAL_IP':
            return criminal_ip(query)
        elif service == 'SHODAN':
            return shodan(query)
        elif service == 'CENSYS':
            return censys(query)
        elif service == 'VIRUSTOTAL':
            return virustotal(query)
        elif service == 'HUNTER':
            return hunter(query)
        elif service == 'IPINFO':
            return ipinfo(query)
        elif service == 'FULLCONTACT':
            return fullcontact(query)
        elif service == 'OPENWEATHERMAP':
            return openweathermap(query)
    except Exception as e:
        print(f"An error occurred while querying {service}: {e}")
        return None

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
    
    emails = raw_emails.split('---END OF EMAIL---')
    
    for email in emails:
        email_data = parse_email(email.strip())
        html_summary = generate_html_summary(email_data)
        
        # Make API requests
        if email_data.get('From'):
            email_from = email_data.get('From').split('<')[-1].split('>')[0]
            haveibeenpwned_data = make_api_request('HAVEIBEENPWNED', email_from)
            hunter_data = make_api_request('HUNTER', email_from)
            fullcontact_data = make_api_request('FULLCONTACT', email_from)
        
        if email_data.get('Received-SPF'):
            ip_from_spf = email_data.get('Received-SPF').split(' ')[-1]
            criminal_ip_data = make_api_request('CRIMINAL_IP', ip_from_spf)
            shodan_data = make_api_request('SHODAN', ip_from_spf)
            censys_data = make_api_request('CENSYS', ip_from_spf)
            virustotal_data = make_api_request('VIRUSTOTAL', ip_from_spf)
            ipinfo_data = make_api_request('IPINFO', ip_from_spf)
        
        print(html_summary)
if __name__ == "__main__":
    main()
