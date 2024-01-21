import requests
import sys
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(alert_message, is_alert, timestamp_str, smtp_password, from_address, to_address, station):
    print("Preparing email.")
    alert_subject = "ALERT: " if is_alert else ""
    msg = MIMEMultipart()
    msg['Subject'] = f"{alert_subject} {station} checked: {alert_message}"
    msg['From'] = from_address
    msg['To'] = to_address

    # Set email importance based on is_alert value
    if is_alert:
        msg['Importance'] = 'High'
    else:
        msg['Importance'] = 'Low'

    body = f"{alert_message}\nTimestamp: {timestamp_str}"
    msg.attach(MIMEText(body, 'plain'))

    print("Sending email.")
    # Send the message via the ProtonMail SMTP server on localhost.
    # ProtonMail Bridge should be running.
    with smtplib.SMTP('127.0.0.1', 1025) as s:
        s.login(from_address, smtp_password)
        s.send_message(msg)
    print("Email sent.")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: aprsStaleCheck.py <station> <api_key> <smtp_password> <from_address> <to_address>")
        exit(1)

    station = sys.argv[1]
    api_key = sys.argv[2]
    smtp_password = sys.argv[3]
    from_address = sys.argv[4]
    to_address = sys.argv[5]

    url = f"https://api.aprs.fi/api/get"

    params = {
        'name': station,
        'what': 'loc',
        'apikey': api_key,
        'format': 'json',
    }

    print(f"Fetching data for station {station}")
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Failed to get data, received status code {response.status_code}")
        exit(1)

    data = response.json()

    if 'entries' in data and len(data['entries']) > 0:
        print(f"Data fetched, assessing lasttime for station {station}")

        lasttime = int(data['entries'][0]['lasttime'])
        lasttime_date = datetime.fromtimestamp(lasttime)

        formatted_lasttime = lasttime_date.strftime('%Y-%m-%d %H:%M:%S')

        alert = datetime.now() - lasttime_date > timedelta(seconds=3600)
        message = f"Lasttime ({formatted_lasttime}) was more than 3600 seconds ago." if alert else f"Lasttime ({formatted_lasttime}) is within the last 3600 seconds."

        print(message)
        send_email(message, alert, formatted_lasttime, smtp_password, from_address, to_address, station)
    else:
        print(f"No data returned for station {station}.")
        message = f"No data returned for station {station}. Please verify the station id."
        send_email(message, True, '', smtp_password, from_address, to_address, station)