import requests
import sys
from datetime import datetime, timedelta

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: aprsStaleCheck.py <station>")
        exit(1)

    target = sys.argv[1]
    url = f"https://api.aprs.fi/api/get"

    # Replace with your API key
    api_key = "<obfuscated>"

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

        # Checking if lasttime was more than 1 hour ago
        if datetime.now() - lasttime_date > timedelta(hours=1):
            print(f"ALERT: Lasttime ({formatted_lasttime}) was more than 1 hour ago.")
        else:
            print(f"Lasttime is within the last hour: {formatted_lasttime}")
    else:
        print(f"No data returned for station {target}.")