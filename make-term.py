import html

def read_lines(path):
    raw = open(path, 'rb').read()
    for enc in ('utf-8-sig', 'utf-16', 'utf-8', 'gbk'):
        try:
            return raw.decode(enc).splitlines()
        except Exception:
            continue
    return raw.decode('utf-8', 'replace').splitlines()


sheet = read_lines('shots/direction-sheet.txt')
cut = next((i for i, l in enumerate(sheet) if l.startswith('## 6. Hero')), 60)
body = sheet[:cut + 8]

log = [l for l in read_lines('shots/inspect-log.txt') if l.strip()]
start = next((i for i, l in enumerate(log) if 'MEASURED' in l), 0)
tail = log[start:]

install = read_lines('shots/_term-install.txt')

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><style>
body {{ margin: 0; background: #ffffff; }}
.panel {{ width: {width}px; background: #0f1512; color: #dfe8e2;
  font-family: 'Cascadia Mono', 'Consolas', 'Microsoft YaHei', monospace;
  font-size: {fs}px; line-height: 1.62; padding: 24px 28px;
  white-space: pre-wrap; word-break: break-word; }}
</style></head><body><div class="panel">{text}</div></body></html>"""


def page(lines, width, fs):
    return TEMPLATE.format(width=width, fs=fs, text=html.escape('\n'.join(lines)))


open('shots/term-draw.html', 'w', encoding='utf-8').write(page(body, 1180, 12.5))
open('shots/term-inspect.html', 'w', encoding='utf-8').write(page(tail, 1180, 13))
open('shots/term-install.html', 'w', encoding='utf-8').write(page(install, 880, 13.5))
print(len(body), len(tail), len(install))
