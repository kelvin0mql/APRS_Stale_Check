import requests
import sys
from datetime import datetime, timedelta

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: aprsStaleCheck.py <station> <api_key>")
        exit(1)

    target = sys.argv[1]
    api_key = sys.argv[2]  # API key is accepted via command line arguments
    url = f"https://api.aprs.fi/api/get"

    params = {
        'name': target,
        'what': 'loc',
        'apikey': api_key,
        'format': 'json',
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Failed to get data, received status code {response.status_code}")
        exit(1)

    data = response.json()

    if 'entries' in data and len(data['entries']) > 0:
        # Getting lasttime from data and converting it to datetime
        lasttime = int(data['entries'][0]['lasttime'])
        lasttime_date = datetime.fromtimestamp(lasttime)

        # Formatting lasttime according to YYYY-MM-DD hh:mm:ss
        formatted_lasttime = lasttime_date.strftime('%Y-%m-%d %H:%M:%S')

        # Checking if lasttime was more than 10 seconds ago
        if datetime.now() - lasttime_date > timedelta(seconds=10):
            print(f"ALERT: Lasttime ({formatted_lasttime}) was more than 10 seconds ago.")
        else:
            print(f"Lasttime is within the last 10 seconds: {formatted_lasttime}")
    else:
        print(f"No data returned for station {target}.")