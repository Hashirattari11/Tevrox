import urllib.request

try:
    r = urllib.request.urlopen('http://localhost:3000/', timeout=30)
    print('Status:', r.status)
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='ignore')
    print('Status:', e.code)
    print('Length:', len(body))
    # Find error message in Next.js error page
    import re
    # Look for Next.js error
    match = re.search(r'<h1[^>]*>(.*?)</h1>', body, re.DOTALL | re.IGNORECASE)
    if match:
        print('Title:', match.group(1)[:200])
    match2 = re.search(r'<pre[^>]*>(.*?)</pre>', body, re.DOTALL | re.IGNORECASE)
    if match2:
        print('Pre:', match2.group(1)[:500])
    # Just print first 500 chars
    print(body[:500])
except Exception as e:
    print('ERR:', str(e)[:100])
