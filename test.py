import requests

print(requests.get('http://127.0.0.1:8080/game_api/join', params={'user_token': '022837fe-c781-4d47-bd2c-44cb1fc08d3c',
                                                                  'score': 0}).content)
