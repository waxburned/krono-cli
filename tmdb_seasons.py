import sys, re

content = sys.stdin.read()
matches = re.findall(r'Season (\d+)', content)
seen = []
for m in matches:
    if m not in seen and m != '0':
        seen.append(m)
for s in seen:
    print(s)
