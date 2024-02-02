import os


def isDev():
  return os.environ('DJANGO_SETTINGS_MODULE') == 'main.settings_dev'


def getHost():
  if isDev:
    return 'http://127.0.0.1:8000'
  else:
    return 'https://sicongchen.top'