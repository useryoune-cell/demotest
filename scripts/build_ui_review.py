"""Collect source and a local screenshot gallery for review."""
from pathlib import Path
import html
import subprocess

output = Path('artifacts/ui-redesign')
changed = subprocess.check_output(['git', 'diff', '--name-only'], text=True).splitlines()
changed += ['app/static/css/design-tokens.css', 'app/static/css/design-system.css',
            'app/static/js/design-system.js', 'scripts/verify_redesign.py']
source = '\n\n'.join('## ' + name + '\n\n```' + Path(name).suffix.lstrip('.') + '\n'
                      + Path(name).read_text(encoding='utf-8') + '\n```' for name in changed)
(output / 'MA_NGUON_DAY_DU.md').write_text(source, encoding='utf-8')
cards = ''.join(f'<article><a href="{p.name}"><img loading="lazy" src="{p.name}"></a>'
                f'<p>{html.escape(p.stem)}</p></article>' for p in sorted(output.glob('*.png')))
(output / 'XEM_GIAO_DIEN.html').write_text('''<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Giao diện mới</title>
<style>body{font:16px system-ui;background:#faf8f3;color:#1f2937;margin:24px}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}
article{background:white;border:1px solid #e8e4da;border-radius:16px;padding:16px}
img{width:100%;height:330px;object-fit:contain;object-position:top}p{overflow-wrap:anywhere}</style>
<h1>Ảnh kiểm tra giao diện mới</h1><p>Nhấn ảnh để xem bản gốc. Trang chủ được giữ nguyên.</p>
<main>''' + cards + '</main></html>', encoding='utf-8')
print(f'{len(changed)} source files; {len(list(output.glob("*.png")))} screenshots')
