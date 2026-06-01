import sys, re, html

media_type = sys.argv[1] if len(sys.argv) > 1 else "tv"
content = sys.stdin.read()
blocks = re.findall(
    r'href="/' + re.escape(media_type) + r'/(\d+)(?:-[^"]*)?\".*?<span>([^<]+)</span>.*?class="release_date[^"]*">([^<]+)',
    content, re.DOTALL)
seen = set()
for tmdb_id, name, date in blocks:
    name = html.unescape(name.strip())
    year_m = re.search(r'\d{4}', date)
    year = year_m.group() if year_m else '?'
    if tmdb_id not in seen:
        seen.add(tmdb_id)
        print(f"{tmdb_id}\t{name} ({year})")
