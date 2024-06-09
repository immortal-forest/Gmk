import os
from threading import Thread


def threaded(func):
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs, name=func.__name__)
        thread.start()
        thread.join()
        return

    return wrapper


def minimize():
    with open("app.min", 'w') as file:
        pass


def maximize():
    try:
        os.remove("app.min")
    except OSError:
        pass


def is_minimized() -> bool:
    return os.path.exists("app.min")
