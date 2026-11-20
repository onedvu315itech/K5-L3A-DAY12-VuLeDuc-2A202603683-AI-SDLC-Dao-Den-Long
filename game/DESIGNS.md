# DESIGNS.md — Visual Design System & Technical Art Blueprint (Whimsical Nightscape)

<!-- [CP0] Initial visual baseline for Đảo Đèn Lồng (presentation only; no game logic) -->
<!-- [Phase 1] Night 1 (Đêm 1 – Đảo Bến) visual & aesthetic specs from PRD-0 -->
<!-- [Graphic Update] Integrated Whimsical Nightscape design system + Technical Art 3D Prefab Blueprints from game/web/assets/*.jpg -->

> A cohesive night-time visual direction and technical art blueprint for *Đảo Đèn Lồng* — calm, magical, slightly mysterious, and storybook-like: moonlit landscapes, deep blue-navy skies, glowing 4/8-point starbursts, layered nature silhouettes, ornate wrought-iron street lanterns, and playful illustrated characters.

---

## 1. Creative Direction & Visual Theme

### Core Idea
- **Setting:** *Đảo Đèn Lồng* — a tranquil yet tense night island shrouded in deep navy-blue and teal fog, surrounded by a reflective moonlit lake and distant mountain/pine silhouettes, pierced by warm golden-moon lantern light and drifting fireflies.
- **Visual Language:**
  - **Night-sky environments (`lake.jpg`, `bush.jpg`, `noel_moon.jpg`):** Deep navy (`#071326`) to blue-teal (`#16466A`) sky dome, concentric-halo glowing full moon (`#FFF0B7`), layered clouds, and dense stars with 4/8-point diamond starburst highlights (`blinking_light.jpg`).
  - **Nature silhouettes (`lake.jpg`, `bush.jpg`, `stone.jpg`, `tree.jpg`):** Layered pine trees, a landmark wide-canopy lone oak/banyan tree, Stonehenge-style standing stone trilithons (vertical monoliths + horizontal lintel), and perimeter bushes with cool teal rim highlights (`#63C6C8`).
  - **Storybook characters & props (`double_character.jpg`, `conical_hat.jpg`, `lamp_post.jpg`, `ghost.jpg`):**
    - **Mây:** Chibi storybook proportions (`1:2` head-to-body ratio), A-line flared raincoat/cloak with front buttons/pockets, wearing a curved *nón lá* adorned with a 5-petal blossom branch (`conical_hat.jpg`), carrying a warm hanging lantern.
    - **Great Lanterns (`L1`..`L5`):** Ornate vintage wrought-iron street lamps (`lamp_post.jpg`) with a stepped moulded base, slender finial post, S-scrollwork bracket arm, and a hanging 4-sided tapered carriage lantern.
    - **Shadow Ink (Shades):** Cute, rounded storybook ghosts (`ghost.jpg`) with a domed head, large dark oval eyes, wavy `"w"` mouth, stubby arms, and a 3-ripple flowing sheet skirt.
- **Camera:** Third-person follow camera behind/above Mây (smooth tracking, unobstructed view of nearby lanterns, silhouettes, and hazards).

### Keywords
`dreamy` · `quiet` · `magical` · `night-sky` · `storybook` · `woodland` · `celestial` · `soft mystery`

---

## 2. Visual Hierarchy

Compose every 3D view and UI overlay in this priority order:
1. **Environment / Background** — deep night sky gradient (`night-950` `#071326` to `night-800` `#102B49`), glowing halo moon (`#FFF0B7`), distant mountain/pine horizon ring, and exponential fog (`FogExp2`).
2. **Main Focal Point** — Mây, the active Great Lanterns (`L1`..`L5`), or primary HUD status.
3. **Supporting Silhouettes** — island terrain, Stonehenge trilithons (`stone.jpg`), lone tree (`tree.jpg`), pine clusters (`lake.jpg`), and teal-rimmed bushes (`bush.jpg`).
4. **Atmospheric Details** — 4/8-point starburst particles (`blinking_light.jpg`), drifting firefly motes, and rippled lake reflections.
5. **Foreground / UI Decoration** — atmospheric menu/intro image cards (`/assets/lake.jpg`, `/assets/bush.jpg`, `/assets/stone.jpg`, `/assets/tree.jpg`) and high-contrast navy HUD panels.

---

## 3. Color Palette & Design Tokens

### 3.1 Core Nightscape Tokens

| Token | Hex / Value | Usage |
|---|---|---|
| `night-950` | `#071326` | Deepest night sky background, tree/pine silhouettes, & base `FogExp2` |
| `night-900` | `#0B1D35` | Main dark blue background, reflective lake water, & primary dark UI surfaces |
| `night-800` | `#102B49` | Secondary sky gradient, island ground base, & raised UI panels |
| `blue-700` | `#16466A` | Distant mountain ridges, moonlit stone monoliths, & blue atmosphere |
| `blue-500` | `#267FA0` | Teal-blue cloud accents, monolith rim highlights, & ambient fill |
| `teal-300` | `#63C6C8` | Moonlit foliage rim highlights (`bush.jpg`), pulse ring wave, & secondary UI accent |
| `moon-100` | `#FFF0B7` | Warm full moon, lit Great Lantern glass core, firefly motes, & primary focal glow |
| `star-100` | `#F7F7FF` | Bright 4/8-point starbursts (`blinking_light.jpg`) & primary HUD text |
| `lavender-200` | `#C6B9E8` | Soft lavender ghost/wisp highlights (`ghost.jpg`) & concentric moon halo (`noel_moon.jpg`) |
| `violet-900` | `#29233F` | Dark purple ghost eyes/contours (`ghost.jpg`) & shadow ink contrast |
| `ink-950` | `#171923` | Near-black wrought-iron lamp post (`lamp_post.jpg`) & illustration outlines |
| `mist-100` | `#E9EDF2` | Ghost body tint / light neutral surfaces & *nón lá* blossom petals |

### 3.2 CSS Custom Properties (Web UI / HUD)

```css
:root {
  --color-night-950: #071326;
  --color-night-900: #0B1D35;
  --color-night-800: #102B49;
  --color-blue-700: #16466A;
  --color-blue-500: #267FA0;
  --color-teal-300: #63C6C8;
  --color-moon-100: #FFF0B7;
  --color-star-100: #F7F7FF;
  --color-lavender-200: #C6B9E8;
  --color-violet-900: #29233F;
  --color-ink-950: #171923;
  --color-mist-100: #E9EDF2;

  --surface-page: var(--color-night-950);
  --surface-raised: rgba(16, 43, 73, 0.84);
  --text-primary: var(--color-star-100);
  --text-muted: #B8C7D8;
  --accent-primary: var(--color-moon-100);
  --accent-secondary: var(--color-teal-300);

  --radius-card: 12px;
  --radius-control: 8px;
}
```

---

## 4. Technical Art Blueprints (3D Prefabs & Textures from `game/web/assets/`)

All 10 reference assets live in `game/web/assets/` and are served at `/assets/<filename>`. Every 3D entity and environment prop in `game/web/index.html` MUST be built using these multi-part prefab blueprints rather than bare primitive placeholders:

### 4.1 Mây (Player Character) — `double_character.jpg` + `conical_hat.jpg`
- **Chibi Raincoat Body (`double_character.jpg`):**
  - A-line flared raincoat torso (`CylinderGeometry(0.22, 0.52, 0.95, 18)`) in warm storybook yellow-gold (`#E5C646` / `#F2C14E`) or ivory cloak with a dark inner shadow recess under the hood (`#171923`), 3 vertical front clasp buttons (`BoxGeometry(0.12, 0.04, 0.04)`), two side pocket flaps, two angled sleeves (`ConeGeometry(0.16, 0.48, 12)`), and two small bare/booted feet (`SphereGeometry(0.11, 10, 10)` scaled flat) that alternate stride when moving.
- **Curved Floral *Nón Lá* (`conical_hat.jpg`):**
  - Built with `LatheGeometry` (slightly convex conical profile, radius `0.72`, height `0.38`) mapped with a procedural high-res Canvas texture reproducing `conical_hat.jpg`: warm ivory-bamboo base (`#E8E2D0`), 16 fine radial ink ribs, 4 concentric stitch rings, and a painted 5-petal blossom branch (*hoa mai/đào*) across the front slope.
- **Forward Hanging Hand Lantern:**
  - Extended on a small front arm at `(0, 1.02, 0.62)` so heading (`yaw`) is immediately readable: miniature 4-sided carriage lantern cage (`#171923`), glowing core (`#FFF0B7`), `PointLight(0xFFB347, 2.8, 14)`, and subtle 4-point starburst sparkles.

### 4.2 Great Lanterns (`L1`..`L5`) — `lamp_post.jpg`
- **Ornate Wrought-Iron Street Lamp Silhouette (`#171923` / `#29233F` metallic matte):**
  1. **Stepped Moulded Base:** Multi-ring `LatheGeometry` / stacked cylinders (`y = 0..1.1m`) with bulb collars matching the lower pedestal of `lamp_post.jpg`.
  2. **Slender Post & Top Spire Finial:** Vertical post (`radius = 0.09`, `y = 1.1..3.8m`) with mid-scrollwork collar rings and a pointed diamond spire finial at `y = 4.05m`.
  3. **S-Curved Scrollwork Bracket Arm:** Curved `TubeGeometry` (`CatmullRomCurve3`) extending horizontally `0.85m` from the upper post with decorative C-scroll rings.
  4. **Hanging 4-Sided Tapered Carriage Lantern:** Suspended from the bracket tip at `y = 3.1m` — dark iron pyramid cap, 4-sided tapered glass housing (`CylinderGeometry(0.36, 0.24, 0.65, 4)` rotated `45°`) with dark frame edges, and a bottom curl finial.
  5. **Lit vs. Unlit Visual State:**
     - **Lit:** Glass housing glows warm moon-yellow (`#FFF0B7`, emissive `#FFB347`), floating 4-point starburst sprite, fuel bar above, and soft safe-radius ground ring (`R = 6m`).
     - **Unlit:** Glass housing is dormant slate-blue (`#16466A`), 20% vertically squashed (`scale.y = 0.8`) with dark cross-tear strips for non-color accessibility.

### 4.3 Shadow Ink (Shades) — `ghost.jpg`
- **Storybook Floating Ghost Mesh:**
  - **Domed Sheet Body (`LatheGeometry` + wavy skirt):** Smooth rounded head (`radius = 0.45`) flowing into a flared, 6-wave scalloped bottom hem (`y = 0.2..1.7m`), tilted slightly backward when moving.
  - **Facial Features & Arms:** Two large dark oval eyes (`SphereGeometry` scaled `(0.11, 0.16, 0.06)` at `z = 0.41`), a small wavy `"w"` mouth, and two stubby outstretched side arms (`Capsule/Sphere` at `y = 1.0`).
  - **Palette & State:**
    - **Normal Patrol/Chase:** Deep night-violet / ink body (`#171923` with `#29233F` / `#7A3CFF` rim glow and pale `#C6B9E8` eyes) — or pale lavender-white ghost silhouette with dark violet aura so it reads clearly against the night fog.
    - **Stunned (`state == "stunned"`):** Shifts to pale misty lavender-teal (`#C6B9E8` / `#63C6C8`) with rapid horizontal jitter.

### 4.4 Fireflies (Motes) & Sparkle Effects — `blinking_light.jpg`
- **4/8-Point Starburst Sprite (`THREE.Sprite` + `AdditiveBlending`):**
  - Procedural Canvas texture replicating `blinking_light.jpg` (bright white-gold center `#F7F7FF` / `#FFF0B7`, sharp vertical & horizontal 4-point diamond spikes + 45° secondary spikes + soft radial halo).
  - Used on every Firefly Mote (with gentle sinusoidal bobbing and twinkle), lit Great Lantern cores, and Mây's lantern.

### 4.5 Island Environment & Landmarks — `lake.jpg`, `bush.jpg`, `stone.jpg`, `tree.jpg`, `noel_moon.jpg`
- **Reflective Moonlit Lake & Sky Dome (`lake.jpg`, `noel_moon.jpg`):**
  - Water plane (`y = -1.5m`) in deep navy-teal (`#0B1D35`, `roughness: 0.25`, `metalness: 0.65`) with subtle concentric moon reflection shimmer.
  - Upper sky features a large glowing **Full Moon** (`#FFF0B7`) with 3 concentric translucent lavender-teal halos (`noel_moon.jpg`) and a 500-star sky field where 40 prominent stars use the 4-point starburst sprite (`blinking_light.jpg`).
- **Distant Mountain & Pine Horizon Ring (`lake.jpg`):**
  - Low-poly jagged mountain ridge ring at `R = 145m` in `#16466A` and `#102B49`, plus clusters of layered dark pine tree silhouettes (`#071326`, 3-tier stacked cones) along the island outer rim.
- **Stonehenge Standing Stone Trilithons (`stone.jpg`):**
  - Placed as dramatic non-colliding perimeter/scenic landmarks on the islands: two tall chiseled vertical monoliths (`Box/Dodecahedron` beveled, `#16466A` with `#63C6C8` moonlit rim edge) topped by a horizontal stone lintel slab.
- **Landmark Lone Tree (`tree.jpg`) & Teal-Rimmed Bushes (`bush.jpg`):**
  - **Lone Tree:** Sculpted dark silhouette trunk (`#071326`) with branching boughs and a wide, multi-cluster spherical foliage canopy silhouetted against the stars.
  - **Bushes & Grass Tufts:** Layered dark-navy bush clusters (`#0B1D35`) around the island border accented with bright cool-teal leaf highlights (`#63C6C8`).

---

## 5. UI, Backdrops, HUD & Accessibility

- **Illustrated Menu & Intro Backdrops (`/assets/*.jpg`):**
  - **Main Menu Overlay:** Full-bleed atmospheric background using `/assets/lake.jpg` (`background-size: cover; background-position: center`) with a soft dark navy radial vignette (`rgba(7, 19, 38, 0.68)`) so the menu card sits inside the moonlit lake world.
  - **Night Intro Card (`introOverlay`):** Displays a themed illustration banner per night (`/assets/bush.jpg` for Night 1 *Đảo Bến*, `/assets/tree.jpg` for Night 2 *Đảo Cầu*, `/assets/stone.jpg` for Night 3 *Đảo Chuông*) alongside a portrait badge of Mây (`/assets/double_character.jpg` / `/assets/conical_hat.jpg`).
- **HUD Panels:** Deep navy translucent surfaces (`rgba(11, 29, 53, 0.84)`) with warm moon-gold borders (`rgba(255, 240, 183, 0.38)`), minimum `18px` font size, high-contrast `--color-star-100` (`#F7F7FF`) text, and full support for Colorblind Mode, Large Text Mode (`1.25x`), and Reduce Motion (`prefers-reduced-motion`).

---

## 6. Design Acceptance Checklist

- [ ] All 10 reference assets in `game/web/assets/` are integrated into the visual experience (UI backdrops + 3D prefab geometry/textures).
- [ ] Overall mood feels calm, dreamy, storybook-like, and night-time oriented (`#071326`, `#0B1D35`, `#102B49`, `#16466A`, `#267FA0`, `#63C6C8`, `#FFF0B7`).
- [ ] Mây features the chibi raincoat silhouette (`double_character.jpg`), curved floral *nón lá* (`conical_hat.jpg`), and forward hand lantern.
- [ ] Great Lanterns (`L1`..`L5`) use the ornate wrought-iron street lamp post + hanging 4-sided carriage lantern (`lamp_post.jpg`).
- [ ] Shades use the floating storybook ghost silhouette (`ghost.jpg`) with eyes, wavy skirt, and stunned jitter state.
- [ ] Motes and prominent stars use 4/8-point diamond starburst sprites (`blinking_light.jpg`).
- [ ] Island scenery includes the concentric-halo moon (`noel_moon.jpg`), reflective lake & pines (`lake.jpg`), lone tree (`tree.jpg`), standing stone trilithons (`stone.jpg`), and teal-rimmed bushes (`bush.jpg`).
- [ ] All headless/unit tests and contract checks (`python game/scripts/verify.py`) continue to pass with zero simulation logic changes.
