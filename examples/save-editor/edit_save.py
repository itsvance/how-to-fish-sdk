#!/usr/bin/env python3
"""Сейвы How to Fish правим тут. by Vance.
Сейвы голый JSON, разрабы шифровать поленились, нам же лучше.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path.home() / "AppData" / "LocalLow" / "Dazed Games" / "How to Fish" / "Saves"


def all_txt(root):
    return [p for p in root.rglob("*.txt") if not p.name.endswith(".backup")]


def cmd_list(root):
    print(f"saves root: {root}")
    for sid in sorted(d for d in root.iterdir() if d.is_dir()):
        print(f"\n[{sid.name}]")
        for f in sorted(sid.glob("*.txt")):
            if f.name.endswith(".backup"):
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"  {f.name} - битый: {e}")
                continue
            if "Money" in data:
                hp = data.get("Players", [{}])[0].get("Health", "?")
                print(f"  {f.stem}: Money={data.get('Money')} Euro={data.get('Euro')} HP={hp}")
            else:
                print(f"  {f.name} (local)")


def find_world(root, name):
    for p in all_txt(root):
        if p.stem == name or p.name == name:
            return p
    low = name.lower()
    for p in all_txt(root):
        if p.stem.lower() == low:
            return p
    print(f"мир '{name}' не нашел, глянь --list", file=sys.stderr)
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description="save editor by Vance")
    ap.add_argument("--list", action="store_true", help="показать миры")
    ap.add_argument("--world", default=None, help="имя мира")
    ap.add_argument("--money", type=int, default=None, help="сколько бабок насыпать")
    ap.add_argument("--euro", type=int, default=None)
    ap.add_argument("--heal", action="store_true", help="отхилить")
    ap.add_argument("--difficulty", type=int, default=None)
    ap.add_argument("--max-island", type=int, default=None, dest="max_island")
    ap.add_argument("--give-item", action="append", type=int, default=[])
    ap.add_argument("--local", action="store_true", help="править local.txt")
    ap.add_argument("--unlock-skins", action="store_true", help="открыть скины")
    ap.add_argument("--complete-bestiary", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="только показать, не писать")
    ap.add_argument("--no-backup", action="store_true", help="без бэкапа, для смелых")
    a = ap.parse_args()

    if not ROOT.is_dir():
        print(f"папки нет: {ROOT}, игру хоть раз запускал?", file=sys.stderr)
        sys.exit(2)

    if a.list or (not a.world and not a.local):
        cmd_list(ROOT)
        return

    if a.local:
        for p in ROOT.rglob("local.txt"):
            data = json.loads(p.read_text(encoding="utf-8"))
            if a.unlock_skins:
                data["UnlockedItemSkins"] = sorted(set(data.get("UnlockedItemSkins", [])) | set(range(50)))
                data["UnlockedBoatSkins"] = sorted(set(data.get("UnlockedBoatSkins", [])) | set(range(20)))
            if a.complete_bestiary:
                for c in data.get("CreaturesToList", []):
                    c["BeenKilled"] = True
                    c["KilledDrip"] = True
            if a.dry_run:
                print(f"dry-run {p}, не трогаю")
                continue
            if not a.no_backup:
                shutil.copy2(p, str(p) + ".mybackup")
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"готово: {p}")
        return

    p = find_world(ROOT, a.world)
    data = json.loads(p.read_text(encoding="utf-8"))

    if a.money is not None:
        print(f"Money: {data.get('Money')} -> {a.money}")
        data["Money"] = a.money
    if a.euro is not None:
        data["Euro"] = a.euro
    if a.difficulty is not None:
        data["Difficulty"] = a.difficulty
    if a.max_island is not None:
        data["MaxIsland"] = a.max_island

    for pl in data.get("Players", []):
        if a.heal:
            pl["Health"] = 100
            pl["Fullness"] = 100
        for iid in a.give_item:
            inv = pl.setdefault("InventoryItems", [])
            inv.append({"Exists": True, "InventorySlot": len(inv), "ItemID": iid, "Weight": 1.0})

    if a.dry_run:
        print("dry-run, файл не трогаю, расслабься")
        print(json.dumps({k: data.get(k) for k in ("Money", "Euro", "Difficulty")}, ensure_ascii=False))
        return

    if not a.no_backup:
        shutil.copy2(p, str(p) + ".mybackup")
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"готово: {p}, заходи проверяй")


if __name__ == "__main__":
    main()
