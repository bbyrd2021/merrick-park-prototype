"""Fetch one ESV passage at build time. Credentials never enter published files."""
import html
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
REFERENCES = [
    'Psalm 118:24', 'Psalm 46:1', 'Proverbs 3:5-6', 'Isaiah 40:31',
    'Psalm 23:1', 'Romans 12:12', 'Philippians 4:6-7', 'Psalm 100:4',
    'Matthew 5:16', 'John 13:34', 'Romans 15:13', 'Psalm 121:1-2',
    'Micah 6:8', '1 Corinthians 16:14', 'Galatians 6:9', 'Psalm 34:8',
    'Colossians 3:15', 'Hebrews 10:24', 'James 1:17', 'Psalm 90:12',
    'Ephesians 4:32', 'Isaiah 26:3', 'Psalm 133:1', 'Matthew 11:28',
    '2 Corinthians 5:7', 'Lamentations 3:22-23', 'Joshua 1:9',
    'Philippians 4:13', 'Psalm 119:105', 'Romans 8:28', 'Numbers 6:24-26',
]

def fetch_verse(key, day):
    reference = REFERENCES[(day.toordinal() - datetime(2026, 1, 1).date().toordinal()) % len(REFERENCES)]
    params = {'q': reference, 'include-passage-references': 'false',
              'include-verse-numbers': 'false', 'include-footnotes': 'false',
              'include-headings': 'false', 'include-short-copyright': 'true'}
    request = Request('https://api.esv.org/v3/passage/text/?' + urlencode(params),
                      headers={'Authorization': 'Token ' + key})
    with urlopen(request, timeout=30) as response:
        data = json.load(response)
    passages = data.get('passages', [])
    if len(passages) != 1 or not isinstance(passages[0], str) or not passages[0].strip():
        raise ValueError('ESV returned an unexpected passage response')
    return data['canonical'], ' '.join(passages[0].split())

def render_verse(page, reference, passage, day):
    match = re.search(r'(<section[^>]*id="mp-verse"[^>]*>)([\s\S]*?)(</section>)', page)
    if not match:
        raise ValueError('Verse section missing')
    inner = match[2]
    inner = re.sub(r'<blockquote>[\s\S]*?</blockquote>', '<blockquote>' + html.escape(passage) + '</blockquote>', inner)
    inner = re.sub(r'<p><strong>.*?</strong></p>', '<p><strong>' + html.escape(reference) + '</strong></p>', inner, count=1)
    inner = inner.replace('Sample verse for design review',
        f'<a href="https://www.esv.org/{quote(reference)}/" target="_blank" rel="noopener">Read in the ESV Bible</a> · {day.strftime("%B %d, %Y")}')
    return page[:match.start()] + match[1] + inner + match[3] + page[match.end():]

def main():
    day = datetime.now(ZoneInfo('America/New_York')).date()
    key = os.environ.get('ESV_API_KEY', '').strip()
    verse = fetch_verse(key, day) if key else None
    output = ROOT / '_site'
    output.mkdir(exist_ok=True)
    for name in ['index.html', 'brand-preview.html']:
        page = (ROOT / name).read_text()
        if verse:
            page = render_verse(page, *verse, day)
        (output / name).write_text(page)
    shutil.copytree(ROOT / 'assets', output / 'assets', dirs_exist_ok=True)
    for name in ['.nojekyll', 'REACT-BITS-LICENSE.md', 'copyright.html']:
        shutil.copy2(ROOT / name, output / name)
    print('Built with daily ESV passage.' if verse else 'Built with sample verse; ESV_API_KEY is not configured.')

if __name__ == '__main__':
    main()
