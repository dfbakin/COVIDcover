import os
import hashlib
import zipfile
import shutil


def check_hash(path):
    lst = []
    hash = hashlib.md5()
    with zipfile.ZipFile(path) as f:
        os.mkdir('tmp')
        f.extractall('tmp')
    for path, dirs, files in os.walk('tmp'):
        for file in files:
            with open(os.path.join(path, file), mode='rb') as f:
                hash.update(f.read())
            lst.append(hash.digest())
    shutil.rmtree('tmp')
    hash.update(b''.join(lst))
    output = hash.hexdigest()
    return output

