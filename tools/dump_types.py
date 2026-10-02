#!/usr/bin/env python3
"""Дамп типов из Assembly-CSharp без запуска игры, через рефлексию.

Пример:
  python tools/dump_types.py --dll "E:\...\Assembly-CSharp.dll" --grep "Money|Teleport"
"""
import argparse, subprocess, tempfile, sys
from pathlib import Path

PS_TEMPLATE = r'''
$dll = "{dll}";
$asm = [System.Reflection.Assembly]::LoadFrom($dll);
foreach ($t in $asm.GetTypes()) {{
  try {{
    $methods = ($t.GetMethods() | ForEach-Object {{ $_.Name }}) -join ","
    $fields = ($t.GetFields([System.Reflection.BindingFlags]::NonPublic -bor [System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Static) | ForEach-Object {{ $_.Name }}) -join ","
    Write-Output ("TYPE: " + $t.FullName + " | M: " + $methods + " | F: " + $fields);
  }} catch {{ Write-Output ("TYPE-ERR: " + $t.FullName); }}
}}
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dll", required=True)
    ap.add_argument("--grep", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    dll = str(Path(args.dll))
    ps = PS_TEMPLATE.replace("{dll}", dll.replace('"', '`"'))
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as f:
        f.write(ps)
        ps_path = f.name
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_path],
                       capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    if args.grep:
        import re
        pat = re.compile(args.grep, re.I)
        out = "\n".join([l for l in out.splitlines() if pat.search(l)])
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"[OK] {args.out} ({len(out.splitlines())} строк)")
    else:
        print(out[:20000])
        if len(out) > 20000:
            print(f"... обрезано ({len(out)} символов), укажи --out", file=sys.stderr)

if __name__ == "__main__":
    main()

