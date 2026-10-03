# EMC for Apotheosis

This data-only ProjectE addon gives EMC to six plain Apotheosis materials, so you can replenish salvaged materials for reforging, gem work, and related crafting. It prices Gem Dust, Mysterious Scrap Metal, Timeworn Fabric, Luminous Crystal Shard, Arcane Sands, and Godforged Pearl. Gems, affix gear, socketed equipment, and other stateful items have no added EMC.

The first build targets Minecraft 1.21.1, NeoForge, Apotheosis 8.9.0, and ProjectE 1.1.0. Apotheosis's own required modules must also be installed. The six values are author-designed; they were absent from the tested pre-addon EMC map. An isolated dedicated server loaded and reloaded the final JAR with ProjectE Integration and Recipe Integration present, confirming all six values. The host's maximum salvage return and observed cheapest reforge input were checked for EMC-positive cycles. A client Transmutation Table transaction and individual modpack overrides were not tested.

Build this lowcodefml JAR with `python3 tools/build_jar.py`. The source JSON and `VALUE_ACCEPTANCE.json` pin the six reviewed prices. The released JAR contains no bundled host or ProjectE code.

The CurseForge avatar candidate is [branding/icon.png](branding/icon.png); its [provenance](branding/PROVENANCE.md) records the author-owned EMC stone and frame. This image is not embedded in the current JAR.

License: All Rights Reserved. Modpack inclusion is permitted, including monetized packs; see [LICENSE](LICENSE). Questions and bug reports: comment on the CurseForge project or DM [@kuronami333](https://x.com/kuronami333). Do not use GitHub Issues for support.
