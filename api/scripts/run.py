import requests
import time
import os
import sys

code = sys.argv[1] # [en-mx, en-ca]

email = os.environ['VISA_EMAIL']
pswd = os.environ['VISA_PSWD']
ifttt_key = os.environ['VISA_IFTTT_KEY']

while True:
    url = f'http://localhost:8800/ais/register/?code={code}&email={email}&pswd={pswd}'
    r = requests.get(url=url)
    data = r.json()
    if data and data['code'] == 0 and len(data['msg']) > 0:
        url = f'https://maker.ifttt.com/trigger/VISA/with/key/{ifttt_key}'
        date = data['msg'][0]
        date = '/'.join([str(_) for _ in date])
        data = {
            'value1': code,
            'value2': date,
        }
        requests.post(url, data=data)
    time.sleep(120)

