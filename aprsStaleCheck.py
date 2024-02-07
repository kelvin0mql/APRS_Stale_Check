import requests
import sys
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(alert_message, is_alert, timestamp_str, smtp_password, from_address, to_address, station, verbosity, json_data=None):
    if is_alert or verbosity in ['INFO', 'DEBUG']:
        print("Preparing email.") if verbosity != 'WARN' else None
        alert_subject = "ALERT: " if is_alert else ""
        msg = MIMEMultipart()
        msg['Subject'] = f"{alert_subject}{station} checked: {alert_message} ({verbosity})"
        msg['From'] = from_address
        msg['To'] = to_address
        if is_alert:
            msg['Importance'] = 'High'
        else:
            msg['Importance'] = 'Low'

        body = f"{alert_message}\nTimestamp: {timestamp_str}"
        body += f"\nData from https://aprs.fi/info/a/{station}"
        if verbosity == 'DEBUG' and json_data:
            body += f"\n\nJSON Response:\n{json_data}"
        msg.attach(MIMEText(body, 'plain'))

        print("Sending email.") if verbosity != 'WARN' else None
        with smtplib.SMTP('127.0.0.1', 1025) as s:
            s.login(from_address, smtp_password)
            s.send_message(msg)
        print("Email sent.") if verbosity != 'WARN' else None

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: aprsStaleCheck.py <station> <api_key> <smtp_password> <from_address> <to_address> <verbosity>")
        print("\nVerbosity options:")
        print("WARN - Only show warnings and errors. Only sends email if station lasttime is older than one hour, or if no data was returned from aprs.fi/api.")
        print("INFO - Show information about program execution, including warnings and errors. Sends email regardless of station status.")
        print("DEBUG - Show all information, including the JSON string returned from aprs.fi/api/get. Sends email regardless of station status.")
        exit(1)

    station = sys.argv[1]
    api_key = sys.argv[2]
    smtp_password = sys.argv[3]
    from_address = sys.argv[4]
    to_address = sys.argv[5]
    verbosity = sys.argv[6]

    url = f"https://api.aprs.fi/api/get"
    headers = {'User-Agent': 'aprsStaleCheck.py/0.0.1 (+https://github.com/kelvin0mql/misc_python/)'}

    params = {
        'name': station,
        'what': 'loc',
        'apikey': api_key,
        'format': 'json',
    }

    print(f"Fetching data for station {station}") if verbosity != 'WARN' else None
    response = requests.get(url, params=params)

    if verbosity == 'DEBUG':
        print("Response: ", response.json())

    if response.status_code != 200:
        print(f"Failed to get data, received status code {response.status_code}") if (verbosity == 'INFO' or verbosity == 'DEBUG') and (response.status_code != 200) else None
        exit(1)

    data = response.json()

    if 'entries' in data and len(data['entries']) > 0:
        print(f"Data fetched, assessing lasttime for station {station}") if verbosity != 'WARN' else None

        lasttime = int(data['entries'][0]['lasttime'])
        lasttime_date = datetime.fromtimestamp(lasttime)
        formatted_lasttime = lasttime_date.strftime('%Y-%m-%d %H:%M:%S')
        alert = datetime.now() - lasttime_date > timedelta(seconds=3600)
        message = f"Lasttime ({formatted_lasttime}) was more than 3600 seconds ago." if alert else f"Lasttime is within the last 3600 seconds: {formatted_lasttime}"
        print(message) if verbosity not in ['WARN'] else None
        send_email(message, alert, formatted_lasttime, smtp_password, from_address, to_address, station, verbosity, json_data=data if verbosity == 'DEBUG' else None)
    else:
        print(f"No data returned for station {station}.") if verbosity not in ['WARN'] else None
        message = f"No data returned for station {station}. Please verify the station id."
        send_email(message, True, '', smtp_password, from_address, to_address, station, verbosity, json_data=data if verbosity == 'DEBUG' else None)
