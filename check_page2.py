import urllib.request

r = urllib.request.urlopen('http://localhost:3000/', timeout=15)
body = r.read().decode('utf-8', errors='ignore')
print('Body length:', len(body))
print()
# Check if it has actual HTML content
if '<body' in body:
    body_start = body.find('<body')
    print('Body section found')
    print(body[body_start:body_start+500])
else:
    print('No <body> tag found')
    print('Full body:')
    print(body[:1000])
