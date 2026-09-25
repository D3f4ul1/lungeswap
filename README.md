# Spear Swap

A small client-side Fabric mod. Press **G** to instantly swap to your spear, land one attack, and swap right back.

It scans your hotbar for an item whose name contains `spear` or `trident`, selects it, attacks, and reverts to the slot you were on a tick later. No config, no HUD, nothing else.

## Install

1. Install [Fabric Loader](https://fabricmc.net/use/installer/) for Minecraft **1.21.11**.
2. Put [Fabric API](https://modrinth.com/mod/fabric-api) and `spearswap-1.0.0.jar` in your `mods` folder.
3. Launch the game.

## Keybind

| Key | Action |
| --- | --- |
| `G` | Swap, attack, swap back |

Rebind it under **Options → Controls → Spear Swap**.

## Requirements

- Minecraft 1.21.11
- Fabric Loader 0.19.5+
- Fabric API
- Java 21

## Building

```bash
./gradlew build
```

The jar lands in `build/libs/`.

## License

MIT — see [LICENSE](LICENSE).
