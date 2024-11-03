import sys
import requests


def handler(week=None):
    print(week)
    


if __name__ == "__main__":
    # print('hello')
    week = sys.argv[1] if sys.argv[1] else None
    handler(week=week)