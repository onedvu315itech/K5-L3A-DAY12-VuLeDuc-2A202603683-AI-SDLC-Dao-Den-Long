# DESIGNS.md — Visual Design Template & Styles

<!-- [CP0] Initial visual baseline for Đảo Đèn Lồng (presentation only; no game logic) -->

## 1. Visual Theme & Mood
- **Setting:** *Đảo Đèn Lồng* — tranquil yet tense night island shrouded in dark ink fog, pierced by warm golden lantern light and drifting fireflies.
- **Camera:** Third-person follow camera behind/above Mây (smooth tracking, unobstructed view of nearby lanterns and hazards).
- **HUD Style:** Minimal dark translucent overlay (`rgba(10, 15, 28, 0.78)`) with warm gold border (`#ffcc66` / `rgba(255, 204, 102, 0.35)`), readable sans-serif text, non-intrusive top-left placement.

## 2. Color Palette

| Element | Hex / Value | Usage |
|---|---|---|
| Night Sky & Fog | `#070b14` | Scene background & exponential fog (`FogExp2`) |
| Moon Ambient / Rim | `#334155` / `#93c5fd` | Ambient fill + cool directional moonlight |
| Island Ground | `#1e293b` | Matte terrain surface (`roughness: 0.9`) |
| Mây (Player) | `#60a5fa` (cloak/body) + `#fbbf24` (hand lantern) | Recognizable silhouette + warm local point light |
| Great Lantern (Unlit) | `#475569` pillar, `#334155` orb | Dormant stone/metal lantern |
| Great Lantern (Lit) | `#fef08a` orb, `#fbbf24` emissive & point light | Bright warm beacon pushing back the dark mood |
| Firefly *(Phase 1+)* | `#fde047` / `#facc15` | Small glowing collectible orb |
| Shadow Ink *(Phase 1+)* | `#09090b` / `#1e1b4b` | Dark silhouette hazard in the fog |

## 3. Character & Entity Style Guidelines
- **Mây (Player):** Stylized low-poly/capsule silhouette with a visible front-facing hand lantern so heading (`yaw`) is immediately readable.
- **Great Lanterns:** Distinct tall pillar + glowing core sphere; clear visual contrast between unlit and lit states (emissive + point light toggle).
- **Environment:** Clean low-poly island landmarks (no external copyrighted models/assets; all procedural Three.js geometry or properly credited CC0/MIT assets in `game/CREDITS.md`).

<!-- [Phase 1+] Append phase-specific visual specs below with <!-- [Phase N] --> tags -->
