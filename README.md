# LungeSwap

A small client-side Fabric mod. Press **G** to instantly swap to your spear, land one attack, and swap right back.

In short: a **spear swap helper**. It scans your hotbar for an item whose name contains `spear` or `trident`, selects it, attacks, and reverts to the slot you were on a tick later. Your main weapon is never out of your hand for more than a single tick. No config, no HUD, nothing else.

Also written up as **lunge swap** and **spear helper**.

Because it only drives your own hotbar and attack key, it works on any server — nothing is needed on the other side.

## Install

1. Install [Fabric Loader](https://fabricmc.net/use/installer/) for Minecraft **1.21.11**.
2. Put [Fabric API](https://modrinth.com/mod/fabric-api) and `lungeswap-1.0.0.jar` in your `mods` folder.
3. Launch the game.

## Keybind

| Key | Action |
| --- | --- |
| `G` | Swap to spear, attack, swap back |

Rebind it under **Options → Controls → LungeSwap**.

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
