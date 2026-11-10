"""One-shot helper: sync ImmortalWrt version references to 25.12.2.
Deleted by itself in the same commit it produces.
"""
import pathlib
import sys

WF_DIR = pathlib.Path('.github/workflows')
WFS = [
    'build-x86-64-25.12.x.yml',
    'build-iso-25.12.x.yml',
    'build-rockchip-25.12.x.yml',
    'build-sunxi-cortexa53-25.12.x.yml',
]
CFGS = ['x86-64/imm25.config', 'rockchip/imm25.config']

OLD_V, NEW_V = '25.12.1', '25.12.2'
OLD_LINE = '        default: "%s"' % OLD_V
NEW_LINE = '        default: "%s"' % NEW_V

OLD_REPO = 'https://downloads.immortalwrt.org/releases/25.12.0-rc1'
NEW_REPO = 'https://downloads.immortalwrt.org/releases/25.12.2'

ok = True

for name in WFS:
    p = WF_DIR / name
    if not p.exists():
        print('MISSING', p)
        ok = False
        continue
    text = p.read_text(encoding='utf-8')
    n = text.count(OLD_LINE)
    m = text.count(NEW_LINE)
    print('%-46s old=%d new_before=%d' % (name, n, m))
    if n != 1:
        ok = False
        continue
    p.write_text(text.replace(OLD_LINE, NEW_LINE), encoding='utf-8')
    after = p.read_text(encoding='utf-8')
    print('%-46s old_after=%d new_after=%d' % (name, after.count(OLD_LINE), after.count(NEW_LINE)))
    if after.count(OLD_LINE) != 0 or after.count(NEW_LINE) != 1:
        ok = False

for name in CFGS:
    p = pathlib.Path(name)
    if not p.exists():
        print('MISSING', p)
        ok = False
        continue
    text = p.read_text(encoding='utf-8')
    n = text.count(OLD_REPO)
    print('%-46s old_repo=%d' % (name, n))
    if n != 1:
        ok = False
        continue
    p.write_text(text.replace(OLD_REPO, NEW_REPO), encoding='utf-8')
    after = p.read_text(encoding='utf-8')
    print('%-46s old_after=%d new_after=%d' % (name, after.count(OLD_REPO), after.count(NEW_REPO)))
    if after.count(OLD_REPO) != 0 or after.count(NEW_REPO) != 1:
        ok = False
    for line in after.splitlines():
        if 'CONFIG_VERSION_REPO=' in line:
            print('    ' + line)

# global residual check
residual = []
for p in list(WF_DIR.rglob('*.yml')) + list(CFGS):
    if not p.exists():
        continue
    t = p.read_text(encoding='utf-8', errors='replace')
    if 'default: "%s"' % OLD_V in t or OLD_REPO in t:
        residual.append(str(p))
if residual:
    print('RESIDUAL', residual)
    ok = False

if not ok:
    print('SYNC FAILED')
    sys.exit(1)

# self-cleanup so the temp workflow and helper do not stay in the repo
for tmp in ['.github/workflows/sync-25.12.2.yml', '.github/sync_version.py']:
    q = pathlib.Path(tmp)
    if q.exists():
        q.unlink()
        print('removed', tmp)

print('SYNC OK')
