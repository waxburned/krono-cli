import sys, re, html

content = sys.stdin.read()
blocks = re.findall(
    r'href="/tv/(\d+)-[^"]*".*?<span>([^<]+)</span>.*?class="release_date[^"]*">([^<]+)',
    content, re.DOTALL)
seen = set()
for tmdb_id, name, date in blocks:
    name = html.unescape(name.strip())
    year_m = re.search(r'\d{4}', date)
    year = year_m.group() if year_m else '?'
    if tmdb_id not in seen:
        seen.add(tmdb_id)
        print(f"{tmdb_id}\t{name} ({year})")
