from zipfile import ZipFile
import os


class FileMissing(Exception):
    pass


if not all(i in os.listdir('.') for i in ['data', 'main_build', 'multi_build', 'versions.json']):
    raise FileMissing
if os.path.isfile('game.zip'):
    os.remove('game.zip')

with ZipFile('game.zip', mode='w') as file:
    print('data:')
    for root, dir, files in os.walk('data'):
        for f in files:
            file.write(os.path.join(root, f))
    print('main_build:')
    for root, dir, files in os.walk('main_build'):
        for f in files:
            file.write(os.path.join(root, f))
    print('multi_build:')
    for root, dir, files in os.walk('multi_build'):
        for f in files:
            file.write(os.path.join(root, f))
    file.write('versions.json')
