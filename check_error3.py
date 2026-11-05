import urllib.request
try:
    r = urllib.request.urlopen('http://localhost:3000/', timeout=30)
    print('Status:', r.status)
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='ignore')
    print('Status:', e.code)
    print('Length:', len(body))
    # Print the full error page body to see what's wrong
    print(body[:3000])
except Exception as e:
    print('ERR:', str(e)[:100])
