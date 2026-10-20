# Run before every push: scans every file in every commit for things that mustn't be published.
# Usage: python3 publish_check.py [--crawl=GLOB,...] [EXTRA_TERM ...]
#   EXTRA_TERM: the tester's public IP, city, country. --crawl: files of crawl data whose URLs are
#   allowed anywhere (default queries/*.csv).
# Exits 1 and lists matches if anything is found. Fix it in history (not just HEAD) before pushing.
import glob, os, re, subprocess, sys


def run(*args):
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()


terms = {t for t in [
    os.path.expanduser('~'), os.environ.get('USER', ''),
    run('git', 'config', 'user.email'),
    run('gcloud', 'config', 'get-value', 'account'),
    run('gcloud', 'config', 'get-value', 'project'),
    *[a for a in sys.argv[1:] if not a.startswith('--crawl=')],
] if len(t) > 2}
patterns = {
    'personal or billing info': re.compile('|'.join(re.escape(t) for t in terms), re.I),
    'BigQuery job ID': re.compile(r'bqjob_|job_[A-Za-z0-9_-]{20,}'),
    'IP address': re.compile(r'(?<![\d./v])(?!127\.0\.0\.1|0\.0\.0\.0)(?:\d{1,3}\.){3}\d{1,3}(?![\d.])|(?<![\w/:])(?:[0-9a-f]{1,4}:){4,7}[0-9a-f]{1,4}\b', re.I),
    'URL with query string': re.compile(r'https?://[^\s"\'<>,\\]+\?[^\s"\'<>,\\]*[=&][^\s"\'<>,\\]*'),
    'country-specific host': re.compile(r'\b(?:google|bing|yahoo|amazon|facebook)\.(?:co\.)?(?!com\b|net\b|org\b)[a-z]{2}\b'),
    'long base64 payload': re.compile(r'(?<!base64,)(?<![A-Za-z0-9+/_-])[A-Za-z0-9+/_-]{200,}={0,2}'),
}
# URLs from the crawl data were recorded by HTTP Archive, not by us; allow them anywhere.
crawl_globs = next((a[8:] for a in sys.argv[1:] if a.startswith('--crawl=')), 'queries/*.csv').split(',')
crawl_files = {f for g in crawl_globs for f in glob.glob(g)}
allowed = set()
for path in crawl_files:
    allowed.update(patterns['URL with query string'].findall(open(path, errors='replace').read()))
seen, found = set(), 0
for commit in run('git', 'rev-list', '--all').split():
    for line in run('git', 'ls-tree', '-r', commit).splitlines():
        meta, path = line.split('\t', 1)
        sha = meta.split()[2]
        if sha in seen or path in crawl_files:
            continue
        seen.add(sha)
        blob = subprocess.run(['git', 'cat-file', 'blob', sha], capture_output=True).stdout
        if b'\0' in blob[:8000]:
            continue
        text = blob.decode('utf8', 'replace')
        for name, pat in patterns.items():
            hits = [h for h in pat.findall(text) if h not in allowed]
            if hits:
                found += 1
                print(f'{commit[:8]} {path}: {name} ({len(hits)}): {hits[0][:80]!r}')
sys.exit(1 if found else 0)
