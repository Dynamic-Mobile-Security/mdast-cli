import hashlib
import os
import zipfile
from datetime import datetime
from time import sleep


def get_md5(path):
    with open(path, mode='rb') as f:
        content = f.read()

    m = hashlib.md5()
    m.update(content)
    return m.hexdigest().lower()


def zip(file_name, t):
    with open('sample.txt', 'wb') as file:
        file.write(b'Hello World')
    os.utime('sample.txt', (t, t))

    with zipfile.ZipFile(file_name, 'w') as myzip:
        myzip.write('sample.txt')


now = datetime.now()
t = int(now.timestamp())

file_name_1 = 'a1.zip'
zip(file_name_1, t)
md5_1 = get_md5(file_name_1)

sleep(10)

file_name_2 = 'a2.zip'
zip(file_name_2, t)
md5_2 = get_md5(file_name_2)

assert md5_1 == md5_2
