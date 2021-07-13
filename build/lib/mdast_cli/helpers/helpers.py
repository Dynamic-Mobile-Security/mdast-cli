import os

def get_app_path(test_app_path):
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, test_app_path)
    return path
