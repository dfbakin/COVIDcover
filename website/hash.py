import os
import hashlib
import requests


def check_hash(script_path, ip_and_port):
    lst = []
    hash = hashlib.md5()
    for path, dirs, files in os.walk(script_path):
        for file in files:
            if 'launcher' not in file:
                with open(os.path.join(path, file), mode='rb') as f:
                    hash.update(f.read())
                lst.append(hash.digest())
    hash.update(b''.join(lst))
    output = hash.hexdigest()
    response = requests.get(f'{ip_and_port}/game_api/check_hash/{output}')
    if response:
        return response.json()['success']
    return False
