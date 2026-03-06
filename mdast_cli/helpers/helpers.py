import hashlib
import os


def get_app_path(test_app_path):
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, test_app_path)
    return path


def check_app_md5(file_path):
    with open(f'{file_path}', "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()
