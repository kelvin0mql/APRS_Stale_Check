import requests
import re
import sys
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(alert_message, is_alert, timestamp_str, matched_line):
    alert_subject = "ALERT:" if is_alert else ""
    msg = MIMEMultipart()
    msg['Subject'] = f"{alert_subject} {alert_message}"
    msg['From'] = 'kelvind@kelvind.com'
    msg['To'] = 'kelvin.d.olson@me.com'
    body = f"{alert_message}\nTimestamp: {timestamp_str}\nMatched Line: {matched_line}"
    msg.attach(MIMEText(body, 'plain'))

    s = smtplib.SMTP(host='127.0.0.1', port=1025)
    smtp_password = 'kZaBEV0cSR3ZSirSD5kkuA'
    s.login('kelvind@kelvind.com', smtp_password)
    s.send_message(msg)
    s.quit()

target = sys.argv[1]
url = f"https://aprs.fi/info/a/{target}"

response = requests.get(url)
lines = response.text.split('\n')

search_text = "Last heard a station directly"
TIME_REGEX = r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b"

for line in lines:
    if search_text in line:
        print(line)  # Print only the line that contains the search_text
        match = re.search(TIME_REGEX, line)
        if match:
            timestamp_str = match.group()
            timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            age = now - timestamp_dt
            age_seconds = age.total_seconds()
            if age_seconds > 3600:
                alert_message = "The timestamp is more than 1 hour old."
                send_email(alert_message, is_alert=True, timestamp_str=timestamp_str, matched_line=line)
            else:
                alert_message = "The timestamp is within 1 hour."
                send_email(alert_message, is_alert=False, timestamp_str=timestamp_str, matched_line=line)
        else:
            print("No timestamp found in the line.")
    else:
        print("The searched text: 'Last heard a station directly' not found in this line.")