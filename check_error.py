import urllib.request
try:
    r = urllib.request.urlopen('http://localhost:3000/', timeout=30)
    print('Status:', r.status)
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='ignore')
    print('Status:', e.code)
    print('Length:', len(body))
    print(body[:2000])
except Exception as e:
    print('ERR:', str(e)[:100])
