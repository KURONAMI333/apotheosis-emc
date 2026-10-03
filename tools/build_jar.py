#!/usr/bin/env python3
"""Build the reviewed lowcodefml data JAR without Gradle or Java compilation."""

import hashlib
import json
from pathlib import Path
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
VALUE_PATH = SRC / "data/apotheosis/pe_custom_conversions/apotheosis_emc.json"
ACCEPTANCE_PATH = ROOT / "VALUE_ACCEPTANCE.json"
ALLOWED = {
    "apotheosis:gem_dust",
    "apotheosis:mysterious_scrap_metal",
    "apotheosis:timeworn_fabric",
    "apotheosis:luminous_crystal_shard",
    "apotheosis:arcane_sands",
    "apotheosis:godforged_pearl",
}
RARITIES = {
    "apotheosis:mysterious_scrap_metal": (1, 0),
    "apotheosis:timeworn_fabric": (2, 1),
    "apotheosis:luminous_crystal_shard": (2, 2),
    "apotheosis:arcane_sands": (2, 4),
    "apotheosis:godforged_pearl": (3, 5),
}


def validate() -> bytes:
    mod_data = tomllib.loads((SRC / "META-INF/neoforge.mods.toml").read_text())
    if mod_data.get("modLoader") != "lowcodefml" or mod_data["mods"][0]["modId"] != "apotheosis_emc":
        raise ValueError("unexpected mod metadata")
    pack = json.loads((SRC / "pack.mcmeta").read_text())
    if pack["pack"]["pack_format"] != 48:
        raise ValueError("Minecraft 1.21.1 requires pack_format 48")
    if not VALUE_PATH.is_file():
        raise ValueError("conversion JSON is absent")
    raw = VALUE_PATH.read_bytes()
    doc = json.loads(raw)
    rows = doc.get("values", {}).get("before")
    if not isinstance(rows, list) or not rows:
        raise ValueError("a nonempty reviewed values.before table is required")
    seen = set()
    prices = {}
    for row in rows:
        if set(row) != {"type", "id", "emc_value"} or row["type"] != "projecte:item":
            raise ValueError("only plain ProjectE item values are allowed")
        item_id, value = row["id"], row["emc_value"]
        if item_id not in ALLOWED or item_id in seen or type(value) is not int or value <= 0:
            raise ValueError(f"unsafe, duplicate, or unapproved item value: {item_id}")
        seen.add(item_id)
        prices[item_id] = value
    if not ACCEPTANCE_PATH.is_file():
        raise ValueError("VALUE_ACCEPTANCE.json is absent")
    accepted = json.loads(ACCEPTANCE_PATH.read_text())
    digest = hashlib.sha256(raw).hexdigest()
    if accepted.get("conversion_sha256") != digest:
        raise ValueError("conversion JSON does not match VALUE_ACCEPTANCE.json")
    if accepted.get("prices") != prices:
        raise ValueError("conversion prices differ from the reviewed design record")
    if accepted.get("price_kind") != "author_design" or not accepted.get("price_reason"):
        raise ValueError("author-designed price reasoning is required")
    if accepted.get("runtime_status") not in {"unverified", "server_map_verified", "verified"}:
        raise ValueError("runtime verification status is required")
    loop = accepted.get("loop_assumptions", {})
    sigil = loop.get("sigil_emc_floor")
    gear = loop.get("eligible_gear_emc_floor")
    if type(sigil) is not int or sigil < 0 or type(gear) is not int or gear < 0:
        raise ValueError("nonnegative assumed Sigil and gear floors are required")
    for item_id, (material_count, sigil_count) in RARITIES.items():
        if item_id in prices and 4 * prices[item_id] > material_count * prices[item_id] + sigil_count * sigil + gear:
            raise ValueError(f"maximum salvage exceeds assumed reforge input: {item_id}")
    return raw


def main() -> None:
    validate()
    files = {
        "META-INF/neoforge.mods.toml": SRC / "META-INF/neoforge.mods.toml",
        "pack.mcmeta": SRC / "pack.mcmeta",
        "LICENSE_apotheosis_emc": ROOT / "LICENSE",
        "data/apotheosis/pe_custom_conversions/apotheosis_emc.json": VALUE_PATH,
    }
    out = ROOT / "build/apotheosis_emc-0.1.0+neoforge-1.21.1.jar"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as jar:
        for name, source in files.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            jar.writestr(info, source.read_bytes())
    print(f"{out} sha256={hashlib.sha256(out.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(f"Build held: {exc}") from None
