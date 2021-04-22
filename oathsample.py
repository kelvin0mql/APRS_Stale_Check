import json
import requests

token_url = "https://qa1.apiclient.com/auth/realms/rest-api/protocol/openid-connect/token"
test_api_url = "https://qa1.apiclient.com/C27APO/v2/locations/3"
client_id = 'V2Rest'
client_secret = '6372aaaf-c35f-4934-8f92-9241de29d470'

# step A, B - single call with client credentials as the basic auth header - will return access_token
data = {'grant_type': 'client_credentials'}
access_token_response = requests.post(token_url, data=data, verify=True, allow_redirects=True, auth=(client_id, client_secret))
print(access_token_response.headers)
print(access_token_response.text)
tokens = json.loads(access_token_response.text)
print("access token: " + tokens['access_token'])

# step B - with the returned access_token we can make as many calls as we want
api_call_headers = {
    'Authorization': 'Bearer ' + tokens['access_token'],
    'Accept': 'application/json'
}
api_call_response = requests.get(test_api_url, headers=api_call_headers, verify=True)
print(api_call_response.text)
print('Monkey, monkey, monkey!')
