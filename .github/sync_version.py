import pathlib
import traceback

WF_DIR = pathlib.Path('.github/workflows')
WFS = [
    'build-x86-64-25.12.x.yml',
    'build-iso-25.12.x.yml',
    'build-rockchip-25.12.x.yml',
    'build-sunxi-cortexa53-25.12.x.yml',
]
CFGS = [pathlib.Path('x86-64/imm25.config'), pathlib.Path('rockchip/imm25.config')]

OLD_LINE = '        default: "25.12.1"'
NEW_LINE = '        default: "25.12.2"'
OLD_REPO = 'https://downloads.immortalwrt.org/releases/25.12.0-rc1'
NEW_REPO = 'https://downloads.immortalwrt.org/releases/25.12.2'

report = []
report.append('chore: sync ImmortalWrt version to 25.12.2')
report.append('')
report.append('25.12.x workflow default: 25.12.1 -> 25.12.2')
report.append('imm25.config CONFIG_VERSION_REPO: 25.12.0-rc1 -> 25.12.2')
report.append('')

bad = []
for name in WFS:
    p = WF_DIR / name
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        bad.append(name + ' unreadable')
        report.append('%s: UNREADABLE' % name)
        continue
    n = text.count(OLD_LINE)
    if n != 1:
        bad.append('%s count=%d' % (name, n))
        report.append('%s: old_count=%d SKIP' % (name, n))
        continue
    p.write_text(text.replace(OLD_LINE, NEW_LINE), encoding='utf-8')
    after = p.read_text(encoding='utf-8')
    report.append('%s: replaced 1, old_after=%d new_after=%d'
                  % (name, after.count(OLD_LINE), after.count(NEW_LINE)))
    if after.count(OLD_LINE) != 0 or after.count(NEW_LINE) != 1:
        bad.append(name + ' verify failed')

for p in CFGS:
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        bad.append(str(p) + ' unreadable')
        report.append('%s: UNREADABLE' % p)
        continue
    n = text.count(OLD_REPO)
    if n != 1:
        bad.append('%s count=%d' % (p, n))
        report.append('%s: old_repo_count=%d SKIP' % (p, n))
        continue
    p.write_text(text.replace(OLD_REPO, NEW_REPO), encoding='utf-8')
    after = p.read_text(encoding='utf-8')
    line = ''
    for l in after.splitlines():
        if 'CONFIG_VERSION_REPO=' in l:
            line = l
            break
    report.append('%s: replaced 1' % p)
    report.append('  ' + line)
    if after.count(OLD_REPO) != 0 or after.count(NEW_REPO) != 1:
        bad.append(str(p) + ' verify failed')

report.append('')
report.append('RESULT: ' + ('ALL 6 FILES SYNCED' if not bad else 'PROBLEM ' + '; '.join(bad)))

# self cleanup: remove the one-shot workflow and this helper from the commit
for tmp in ['.github/workflows/sync-25.12.2.yml', '.github/sync_version.py']:
    q = pathlib.Path(tmp)
    if q.exists():
        q.unlink()

report.append('self-cleanup: removed .github/workflows/sync-25.12.2.yml and .github/sync_version.py')

text = '\n'.join(report) + '\n'
pathlib.Path('.github/sync_report.txt').write_text(text, encoding='utf-8')
print(text)
