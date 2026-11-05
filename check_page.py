import urllib.request

r = urllib.request.urlopen('http://localhost:3000/', timeout=15)
body = r.read().decode('utf-8', errors='ignore')

checks = ['Tevrox', 'Skincare', 'Log in', 'Sign up', 'Sparkles', 'animate', 'login', 'signup']
for c in checks:
    print(f'Contains "{c}": {c.lower() in body.lower()}')

print()
print('First 600 chars:')
print(body[:600])
