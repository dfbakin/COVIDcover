import requests

print(requests.get('http://127.0.0.1:8080/game_api/quit', params={'user_token': '0c4b8f94-b0d1-4731-8566-0bfa4a989610',
                                                                  'score': 0}).content)
