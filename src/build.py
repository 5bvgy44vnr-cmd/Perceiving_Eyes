import re, html, sys, os
SRC, TPL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

def load(name):
    s = open(os.path.join(SRC, name), encoding='cp1252').read()
    s = re.sub(r'<!\[if[^\]]*\]>|<!\[endif\]>', '', s)
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S)
    return s

def clean_inline(body):
    """Keep italics and footnote refs, drop everything else."""
    def fn(m):
        n = re.search(r'\[(\d+)\]', m.group(0))
        return f'\x01{n.group(1)}\x02' if n else ''
    body = re.sub(r'<a[^>]*href="#_ftn\d+"[^>]*>.*?</a>', fn, body, flags=re.S)
    body = re.sub(r'<a[^>]*href="#_ftnref\d+"[^>]*>.*?</a>', '', body, flags=re.S)
    body = re.sub(r'<(/?)(i|em)\b[^>]*>', lambda m: f'\x03{m.group(1)}\x04', body)
    body = re.sub(r'<[^>]+>', '', body)
    t = html.unescape(body).replace('\xa0', ' ')
    t = re.sub(r'\s+', ' ', t).strip()
    t = html.escape(t, quote=False)
    t = re.sub('\x03(/?)\x04', lambda m: f'<{m.group(1)}em>', t)
    t = re.sub(r'<em>\s*</em>', '', t)
    t = re.sub('\\s*\x01(\\d+)\x02', lambda m: f'<sup class="fn"><a href="#fn-{m.group(1)}" id="fnref-{m.group(1)}" aria-label="Footnote {m.group(1)}">{m.group(1)}</a></sup>', t)
    return t

ZONES_FIG = '<figure class="paper-fig"><svg viewBox="0 0 600 600" role="img" aria-label="Diagram of four concentric zones: Perception at the centre, then Modulation, Introduction and Digression outermost"><use href="#zones-art"/></svg><figcaption>The four zones of art interpretation</figcaption></figure>'

DAYS_TABLE = '''<div class="table-wrap"><table class="days-table"><thead><tr><th>English</th><th>Hindu</th><th>French</th><th>Planet</th></tr></thead><tbody>
<tr><td>Sunday</td><td>Ravivar</td><td>Dimanche</td><td>Sun</td></tr>
<tr><td>Monday</td><td>Somavar</td><td>Lundi</td><td>Moon</td></tr>
<tr><td>Tuesday</td><td>Mangalvar</td><td>Mardi</td><td>Mars</td></tr>
<tr><td>Wednesday</td><td>Bhudvar</td><td>Mercredi</td><td>Mercury</td></tr>
<tr><td>Thursday</td><td>Bhrihastivar</td><td>Jeudi</td><td>Jupiter</td></tr>
<tr><td>Friday</td><td>Shukravar</td><td>Vendredi</td><td>Venus</td></tr>
<tr><td>Saturday</td><td>Shanivar</td><td>Samedi</td><td>Saturn</td></tr>
</tbody></table></div>'''

def build_paper():
    s = load('1outline.htm')
    s = s[s.find('<div class=Section1>'):]
    blocks = []   # (kind, html)
    notes = []
    pat = re.compile(r'<(p|h\d|table)\b([^>]*)>(.*?)(?=<(?:p|h\d|table)\b|</table>|$)', re.S)
    in_list = False
    seen_principles = False
    for m in pat.finditer(s):
        tag, attr, body = m.groups()
        attr = re.sub(r'\s+', ' ', attr)
        if tag == 'table':
            if 'Ravivar' in body:
                blocks.append(('table', DAYS_TABLE))
            continue
        has_img = 'image002' in body
        t = clean_inline(body)
        if has_img:
            blocks.append(('fig', ZONES_FIG))
        if not t:
            continue
        plain = re.sub(r'<[^>]+>', '', t)
        # footnotes
        ref = re.search(r'name="?_ftn(\d+)"?', body)
        if ref or 'MsoFootnoteText' in attr:
            if ref:
                notes.append([ref.group(1), re.sub(r'^2\.\s+(?=Hugh)', '', t)])
            else:
                notes[-1][1] += t
            continue
        if tag in ('h1', 'h3'):
            blocks.append(('h', plain.rstrip('.')))
            continue
        if re.search(r'the planet of \w+day$', plain):
            blocks.append(('h3', plain))
            continue
        if plain.startswith('There are also certain principles'):
            blocks.append(('p', t)); seen_principles = True; in_list = True
            blocks.append(('ol-open', '')); continue
        if in_list:
            if attr.strip() == '':
                blocks.append(('li', t)); continue
            blocks.append(('ol-close', '')); in_list = False
        is_quote = 'margin-left' in attr or ('MsoBodyTextIndent ' in attr + ' ' and '150%' in attr)
        blocks.append(('bq' if is_quote else 'p', t))
    assert seen_principles and len(notes) == 16, len(notes)

    chapters = [['I', 'Introduction', []]]
    roman = {'Conceptualizing art': ('II', 'Conceptualizing Art'), 'Appendix': ('III', 'Appendix: The Visual Piece'), 'Days in a Week': ('IV', 'Days in a Week')}
    for kind, h in blocks:
        if kind == 'h':
            r, title = roman[h]
            chapters.append([r, title, []]); continue
        out = chapters[-1][2]
        if kind == 'p': out.append(f'<p>{h}</p>')
        elif kind == 'bq': out.append(f'<blockquote><p>{h}</p></blockquote>')
        elif kind == 'h3': out.append(f'<h4>{h}</h4>')
        elif kind == 'ol-open': out.append('<ol class="principles-list">')
        elif kind == 'ol-close': out.append('</ol>')
        elif kind == 'li': out.append(f'<li>{h}</li>')
        else: out.append(h)
    assert len(chapters) == 4, [c[1] for c in chapters]
    res = []
    for i, (r, title, parts) in enumerate(chapters):
        words = len(re.sub(r'<[^>]+>', ' ', ' '.join(parts)).split())
        mins = max(1, round(words / 220))
        res.append(f'<details class="chapter" id="ch-{r.lower()}"{" open" if i == 0 else ""}><summary><span class="ch-num">{r}</span><span class="ch-title">{title}</span><span class="ch-meta">{mins} min</span><span class="ch-icon" aria-hidden="true"></span></summary><div class="ch-body">' + '\n'.join(parts) + '</div></details>')
    fn = ''.join(f'<li id="fn-{n}"><p>{t} <a class="fn-back" href="#fnref-{n}" aria-label="Back to text">&#8617;</a></p></li>' for n, t in notes)
    res.append(f'<details class="chapter" id="ch-notes"><summary><span class="ch-num">N</span><span class="ch-title">Notes</span><span class="ch-meta">16 notes</span><span class="ch-icon" aria-hidden="true"></span></summary><div class="ch-body"><ol class="footnotes">{fn}</ol></div></details>')
    total = sum(len(re.sub(r'<[^>]+>', ' ', ' '.join(c[2])).split()) for c in chapters)
    return '\n'.join(res), total

def build_biblio():
    s = load('2biblio.htm')
    s = s[s.rfind('<p', 0, s.find('Barnard')):]
    items = []
    for m in re.finditer(r'<p\b[^>]*>(.*?)</p>', s, re.S):
        t = clean_inline(m.group(1))
        if len(t) > 25 and 'pramod' not in t.lower():
            t = re.sub(r'&lt;\s*(http[^&]*?)\s*&gt;', lambda u: '&lt;' + u.group(1).replace(' ', '') + '&gt;', t)
            items.append(f'<li>{t}</li>')
    assert len(items) > 30, len(items)
    return '\n'.join(items), len(items)

# Link check, 18 Nov 2026: every resource and museum link from the 2003 site was opened in a
# browser (page text read only, nothing downloaded). Only these two still load their content;
# the rest returned 404, redirected to unrelated or spam sites, or did not respond.
WORKING_LINKS = [
    ('Communication Quotations', 'https://www.wow4u.com/71-communication-quotes/', 'wow4u.com'),
    ('The Art Renewal Center', 'https://www.artrenewal.org/', 'artrenewal.org · museum'),
]

def build_resources():
    items = []
    for title, url, host in WORKING_LINKS:
        items.append(f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener"><span class="lk-title">{html.escape(title)}</span>'
                     f'<span class="lk-host">{html.escape(host)}</span><span class="lk-arrow" aria-hidden="true">&#8599;</span></a></li>')
    return '\n'.join(items), len(items)

paper, words = build_paper()
bib, nb = build_biblio()
res, nr = build_resources()
tpl = open(TPL, encoding='utf-8').read()
for k, v in {'PAPER': paper, 'BIBLIO': bib, 'RESOURCES': res,
             'WORDS': f'{words:,}', 'NBIB': str(nb), 'NRES': str(nr), 'READMIN': str(round(words / 220))}.items():
    assert '{{' + k + '}}' in tpl, k
    tpl = tpl.replace('{{' + k + '}}', v)
assert '{{' not in tpl
open(OUT, 'w', encoding='utf-8').write(tpl)
print('ok', words, nb, nr, len(tpl))
