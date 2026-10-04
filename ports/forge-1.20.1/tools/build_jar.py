#!/usr/bin/env python3
"""Build the data-only Apotheosis EMC addon for Forge 1.20.1."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CONVERSION = SRC / "data/apotheosis/pe_custom_conversions/apotheosis_emc.json"
OUTPUT = ROOT / "build/emc-for-apotheosis-0.1.0+forge-1.20.1.jar"
EXPECTED = {
    "apotheosis:gem_dust": 8192,
    "apotheosis:uncommon_material": 128,
    "apotheosis:rare_material": 1024,
    "apotheosis:epic_material": 8192,
    "apotheosis:mythic_material": 12288,
}


def validate() -> dict[str, Path]:
    metadata_path = SRC / "META-INF/mods.toml"
    metadata = tomllib.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("modLoader") != "lowcodefml":
        raise ValueError("Forge data addon must use lowcodefml")
    mod = metadata.get("mods", [{}])[0]
    if mod.get("modId") != "apotheosis_emc" or mod.get("version") != "0.1.0+forge1201":
        raise ValueError("unexpected mod metadata")
    dependencies = {row["modId"]: row for row in metadata.get("dependencies", {}).get("apotheosis_emc", [])}
    for mod_id, version in {
        "forge": "[47,)",
        "minecraft": "[1.20.1]",
        "projecte": "[1.0.1]",
        "apotheosis": "[7.4.8]",
    }.items():
        row = dependencies.get(mod_id)
        if not row or row.get("mandatory") is not True or row.get("versionRange") != version:
            raise ValueError(f"missing or incorrect required dependency: {mod_id}")

    pack_path = SRC / "pack.mcmeta"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    if pack.get("pack", {}).get("pack_format") != 15:
        raise ValueError("Minecraft 1.20.1 datapack requires pack_format 15")

    doc = json.loads(CONVERSION.read_text(encoding="utf-8"))
    prices = doc.get("values", {}).get("before")
    if doc.get("replace") is not False or prices != EXPECTED:
        raise ValueError("conversion map differs from the reviewed five-price Forge table")
    license_path = ROOT / "LICENSE"
    if not license_path.is_file():
        raise ValueError("LICENSE is missing")
    return {
        "META-INF/mods.toml": metadata_path,
        "pack.mcmeta": pack_path,
        "LICENSE_apotheosis_emc": license_path,
        "data/apotheosis/pe_custom_conversions/apotheosis_emc.json": CONVERSION,
    }


def build() -> None:
    files = validate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as jar:
        for name, source in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            jar.writestr(info, source.read_bytes())
    with zipfile.ZipFile(OUTPUT) as jar:
        bad = jar.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failed at {bad}")
        if set(jar.namelist()) != set(files):
            raise ValueError("JAR entry set differs from the reviewed source bundle")
        for name, source in files.items():
            if jar.read(name) != source.read_bytes():
                raise ValueError(f"JAR entry does not match source: {name}")
    print(f"{OUTPUT} bytes={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    build()
