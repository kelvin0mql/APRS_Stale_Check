import requests
import sys
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(alert_message, is_alert, timestamp_str, smtp_password):
    print("Preparing email.")
    alert_subject = "ALERT:" if is_alert else ""
    msg = MIMEMultipart()
    msg['Subject'] = f"{alert_subject} {alert_message}"
    msg['From'] = 'kelvind@kelvind.com'
    msg['To'] = 'kelvin.d.olson@me.com'
    body = f"{alert_message}\nTimestamp: {timestamp_str}"
    msg.attach(MIMEText(body, 'plain'))

    print("Sending email.")
    # Send the message via the ProtonMail SMTP server on localhost.
    # ProtonMail Bridge should be running.
    with smtplib.SMTP('127.0.0.1', 1025) as s:
        s.login('kelvind@kelvind.com', smtp_password)
        s.send_message(msg)
    print("Email sent.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: aprsStaleCheck.py <station> <api_key> <smtp_password>")
        exit(1)

    target = sys.argv[1]
    api_key = sys.argv[2]
    smtp_password = sys.argv[3]  # SMTP password is accepted via command line arguments.
    url = f"https://api.aprs.fi/api/get"

    params = {
        'name': target,
        'what': 'loc',
        'apikey': api_key,
        'format': 'json',
    }

    print(f"Fetching data for station {target}")
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Failed to get data, received status code {response.status_code}")
        exit(1)

    data = response.json()

    if 'entries' in data and len(data['entries']) > 0:
        print(f"Data fetched, assessing lasttime for station {target}")
        # Getting lasttime from data and converting it to datetime
        lasttime = int(data['entries'][0]['lasttime'])
        lasttime_date = datetime.fromtimestamp(lasttime)

        # Formatting lasttime according to YYYY-MM-DD hh:mm:ss
        formatted_lasttime = lasttime_date.strftime('%Y-%m-%d %H:%M:%S')

        # Checking if lasttime was more than 600 seconds ago
        alert = datetime.now() - lasttime_date > timedelta(seconds=600)
        message = f"Lasttime ({formatted_lasttime}) was more than 600 seconds ago." if alert else f"Lasttime is within the last 600 seconds: {formatted_lasttime}"
        print(message)

        send_email(message, alert, formatted_lasttime, smtp_password)
    else:
        print(f"No data returned for station {target}.")
        message = f"No data returned for station {target}. Please verify the station id."
        send_email(message, True, '', smtp_password)