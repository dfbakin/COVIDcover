import requests

def quit_all():
    print(requests.get('http://127.0.0.1:8080/game_api/quit', params={'user_token': '2a288d46-b3bf-4669-a938-dbaa6e8d9126',
                                                                      'score': 0}).content)
    print(requests.get('http://127.0.0.1:8080/game_api/quit', params={'user_token': '9f8e6b0c-62c7-4b09-b6d3-f923f3bf9860',
                                                                      'score': 0}).content)
    print(requests.get('http://127.0.0.1:8080/game_api/quit', params={'user_token': '0c4b8f94-b0d1-4731-8566-0bfa4a989610',
                                                                      'score': 0}).content)
def join_all():
    print(requests.get('http://127.0.0.1:8080/game_api/join', params={'user_token': '2a288d46-b3bf-4669-a938-dbaa6e8d9126',
                                                                      'score': 0}).content)
    print(requests.get('http://127.0.0.1:8080/game_api/join', params={'user_token': '9f8e6b0c-62c7-4b09-b6d3-f923f3bf9860',
                                                                      'score': 0}).content)
    print(requests.get('http://127.0.0.1:8080/game_api/join', params={'user_token': '0c4b8f94-b0d1-4731-8566-0bfa4a989610',
                                                                      'score': 0}).content)
join_all()