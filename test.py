import requests
print(requests.get('http://127.0.0.1:8080/game_api/quit',
             params={'user_token': '0515d797-6ff2-49ee-99c4-3f1dd0362eea', 'score': 0}).content)