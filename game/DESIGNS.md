# DESIGNS.md — Visual Design System & Styles (Whimsical Nightscape)

<!-- [CP0] Initial visual baseline for Đảo Đèn Lồng (presentation only; no game logic) -->
<!-- [Phase 1] Night 1 (Đêm 1 – Đảo Bến) visual & aesthetic specs from PRD-0 -->
<!-- [Graphic Update] Integrated Whimsical Nightscape design system from graphic.md -->

> A cohesive night-time visual direction for *Đảo Đèn Lồng* — calm, magical, slightly mysterious, and storybook-like: moonlit landscapes, deep blue-navy skies, glowing stars, layered nature silhouettes, warm lantern light, and playful illustrated elements.

---

## 1. Creative Direction & Visual Theme

### Core Idea
- **Setting:** *Đảo Đèn Lồng* — a tranquil yet tense night island shrouded in deep navy-blue and ink fog, pierced by warm golden-moon lantern light, starry skies, and drifting fireflies.
- **Visual Language:**
  - **Night-sky environments:** deep navy and blue-teal gradients, dense stars of varied sizes, moonlight, and distant horizons.
  - **Nature silhouettes:** layered mountains, pine trees, bushes, rocks, grass, standing stones, and lone tree landmarks.
  - **Soft magical light:** moons, warm glowing lanterns, firefly motes, and star-shaped highlights.
  - **Storybook details:** Mây wearing a traditional **nón lá** (conical hat with subtle floral/fine-line detail) and carrying a small glowing lantern, vintage lamp/pillar silhouettes, friendly/whimsical ghost or wisp silhouettes, and hooded companion motifs.
  - **Mood:** dreamy, quiet, magical, fairy-tale night mood (non-violent; no gore/blood). Compositions feel spacious and atmospheric rather than crowded or aggressive.
- **Camera:** Third-person follow camera behind/above Mây (smooth tracking, unobstructed view of nearby lanterns, silhouettes, and hazards).

### Keywords
`dreamy` · `quiet` · `magical` · `night-sky` · `storybook` · `woodland` · `celestial` · `soft mystery`

---

## 2. Visual Hierarchy

Compose every 3D view and UI overlay in this priority order:
1. **Environment / Background** — deep night sky gradient (`night-950` to `night-800`), moon, and exponential distance fog (`FogExp2`).
2. **Main Focal Point** — Mây, the active Great Lantern (`L1`..`L5`), moon landmark, or primary HUD status.
3. **Supporting Silhouettes** — island terrain, trees, bushes, standing stones, grass, and pillar details.
4. **Atmospheric Details** — stars, drifting firefly motes, water reflections, and localized lantern glows.
5. **Foreground / UI Decoration** — restrained framing branches or subtle HUD borders that never compete with gameplay readability.

---

## 3. Color Palette & Design Tokens

### 3.1 Core Nightscape Tokens

| Token | Hex / Value | Usage |
|---|---|---|
| `night-950` | `#071326` | Deepest night sky background & base exponential fog (`FogExp2`) |
| `night-900` | `#0B1D35` | Main dark blue background & primary dark UI surfaces |
| `night-800` | `#102B49` | Secondary sky gradient, island ground base, & raised UI panels |
| `blue-700` | `#16466A` | Distant mountain/landscape silhouettes & blue atmosphere |
| `blue-500` | `#267FA0` | Teal-blue highlights, cloud accents, & Mây's cloak/body tint |
| `teal-300` | `#63C6C8` | Moonlit or magical cool highlights, pulse ring accent, & secondary UI accent |
| `moon-100` | `#FFF0B7` | Warm moonlight, lit Great Lantern core, & primary focal glow |
| `star-100` | `#F7F7FF` | Bright stars, small highlights, & primary HUD text |
| `lavender-200` | `#C6B9E8` | Optional soft festive/seasonal night accents (use selectively) |
| `violet-900` | `#29233F` | Dark purple silhouettes, shadow ink body/rim contrast |
| `ink-950` | `#171923` | Near-black illustration outlines, foreground silhouettes, & Shadow Ink core |
| `mist-100` | `#E9EDF2` | Light neutral surfaces & high-contrast readable labels |

### 3.2 Game Entity & Lighting Palette

| Element | Hex / Value | Usage |
|---|---|---|
| Night Sky & Fog | `#071326` (`night-950`) -> `#102B49` (`night-800`) | Scene background gradient & dynamic `FogExp2` |
| Moon Ambient / Rim | `#16466A` (`blue-700`) / `#63C6C8` (`teal-300`) | Ambient fill + cool directional moonlight |
| Island Ground & Water | `#102B49` (`night-800`) / `#0B1D35` (`night-900`) | Matte terrain surface (`roughness: 0.9`) with subtle rippled water reflections around the island |
| Mây (Player) | `#267FA0` (`blue-500`) cloak + `#eab308` / `#FFF0B7` nón lá & hand lantern | Recognizable storybook silhouette + warm local point light |
| Great Lantern (Unlit) | `#16466A` / `#475569` pillar, `#102B49` orb | Dormant vintage lamp / stone-wood lantern silhouette |
| Great Lantern (Lit) | `#FFF0B7` (`moon-100`) orb, `#fbbf24` / `#f59e0b` emissive & point light | Warm golden beacon pushing back the dark fog + subtle safe-radius ground ring |
| Firefly (Mote) | `#FFF0B7` (`moon-100`) / `#fde047` | Small floating golden-warm collectible orb |
| Shadow Ink (Shade) | `#171923` (`ink-950`) body + `#29233F` (`violet-900`) / `#4c1d95` rim | Storybook ghost/wisp silhouette hazard; shifts to pale lavender/teal (`#C6B9E8` / `#63C6C8`) jitter when `state == "stunned"` |

### 3.3 CSS Custom Properties (Web UI / HUD)

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
  --surface-raised: rgba(16, 43, 73, 0.82); /* night-800 translucent */
  --text-primary: var(--color-star-100);
  --text-muted: #B8C7D8;
  --accent-primary: var(--color-moon-100);
  --accent-secondary: var(--color-teal-300);

  --radius-card: 12px;
  --radius-control: 8px;
}
```

### Color Rules
- Prefer **dark navy, deep blue, and blue-teal** as the dominant environment colors.
- Reserve **warm pale yellow / golden light** (`#FFF0B7`, `#fbbf24`) for moons, lanterns, fireflies, and primary action highlights.
- Use **cyan/teal** (`#63C6C8`) as cool magical illumination (e.g., Mây's pulse wave, moonlight rim), not on every surface.
- Keep foreground and hazard silhouettes dark enough (`#171923`, `#29233F`) to read clearly against the blue-teal sky and ground.
- Avoid introducing unrelated saturated colors.

---

## 4. Environment, Silhouettes & Visual Reference Motifs

All 3D procedural geometry and 2D/UI decorative elements translate the reference motifs into cohesive island landmarks (no uncredited external copyrighted models; procedural Three.js meshes or properly credited CC0/MIT assets in `game/CREDITS.md`):

| Reference Motif | Visual Content | In-Game / UI Role |
|---|---|---|
| `lake.jpg` | Moonlit mountain lake with rippled reflection, pine silhouettes, starry sky | Island water surround, distant mountain horizon ring, skybox star field |
| `bush.jpg` | Framed night sky, moon, clouds, foliage, small glowing lights | Island perimeter bushes, layered organic foliage silhouettes, drifting fireflies |
| `stone.jpg` | Large standing stones beneath a dense blue star field | Mysterious standing stone landmarks on the island interior |
| `tree.jpg` | Lone tree silhouette against a star-filled blue sky | Central / landmark lone tree silhouette on the island |
| `lamp_post.jpg` | Ornate vintage street lamp silhouette | Visual inspiration for the 5 Great Lantern (`L1`..`L5`) pillars & decorative frames |
| `blinking_light.jpg` | Cluster or trail of bright star-shaped lights | Sparkle particles on lantern ignition, mote pickup, and pulse burst |
| `noel_moon.jpg` | Large glowing moon with silhouettes against night sky | Prominent glowing full moon in the upper sky dome |
| `ghost.jpg` | Simple friendly/storybook ghost silhouette | Visual inspiration for non-violent, whimsical Shadow Ink (Shade) wisp shapes |
| `double_character.jpg` | Hooded storybook characters with simple readable proportions | Visual proportion guide for Mây's cloak/body silhouette |
| `conical_hat.jpg` | Fine-line conical hat (*nón lá*) with subtle floral/ribbed detail | Mây's signature *nón lá* headpiece (`#eab308` / `#FFF0B7` rim) |

---

## 5. Phase 1: Đêm 1 – Đảo Bến Entity & Scene Specs

- **Dynamic Island Illumination:**
  - As Great Lanterns are lit (`0 -> 5`), ambient/moon light intensity increases and `FogExp2` density decreases smoothly so the nightscape transitions from mysterious deep navy (`#071326`) toward a clearer, starlit blue-teal sky (`#16466A`).
- **Mây (Player Character):**
  - Storybook hooded/cloaked silhouette (`#267FA0`) wearing a traditional **nón lá** (conical hat with subtle radial rib lines) and a **small glowing hand lantern** (`#FFF0B7` / `#fbbf24`) hanging forward so heading (`yaw`) is immediately readable.
  - Smooth jump arc animation (`player.pos[1] > 0`) and a cool-teal / moon-gold expanding ring burst (`#63C6C8` + `#FFF0B7`) when `pulse` triggers.
- **5 Great Lanterns (`L1`..`L5`):**
  - Placed in a balanced ring on the circular island (`R ≈ 42m`), combining stone/vintage lamp-post pillar silhouettes with a glowing core orb and a soft safe-radius ground ring when lit.
- **Fireflies (Motes) & Shadow Ink (Shades):**
  - **Fireflies:** Tiny warm-moon glowing orbs (`#FFF0B7` / `#fde047`) with gentle staggered bobbing and twinkle (visual `Y` offset only; core logic stays on `Y = 0`).
  - **Shadow Ink:** Storybook ghost/wisp silhouettes (`#171923` core, `#29233F` cloak rim, `Y ≈ 1.0` center) with subtle floating motion; visually shifts to pale lavender-teal jitter (`#C6B9E8` / `#63C6C8`) when `state == "stunned"`.

---

## 6. UI, HUD, Motion & Accessibility Guidance

### 6.1 HUD & Overlay Surfaces
- **HUD Panel:** Deep navy translucent card (`rgba(11, 29, 53, 0.82)` / `--surface-raised`) with restrained `12px` radius (`--radius-card`), subtle warm moon-gold or teal border (`rgba(255, 240, 183, 0.3)`), and non-intrusive top-left placement.
- **Required HUD Fields:** Remaining time (`time_left_s`), Flames (`flames`), Carried Motes (`carried` / `carry_capacity`), Lit Lanterns (`lit / 5`), Score, and Pulse cooldown status.
- **Win (`won`) / Lose (`lost`) Overlay:** Calm, storybook modal panel over a darkened backdrop (`rgba(7, 19, 38, 0.88)`) showing final score, outcome reason, and a high-contrast **Play Again** button (`--color-moon-100` fill with `--color-ink-950` text, `8px` radius).
- **Typography:** High-legibility sans-serif interface text in `--text-primary` (`#F7F7FF`) and `--text-muted` (`#B8C7D8`). Never place small text directly over busy star fields without a backing surface.

### 6.2 Lighting, Glow & Motion Rules
- **Restrained Glow:** Keep the brightest glow close to light sources (moon, hand lantern, Great Lanterns, fireflies) with smooth falloff. Do not apply glow to every HUD border or text label.
- **Subtle Motion:** Use gentle staggered star twinkle, soft lantern/firefly pulse, and slow floating wisp motion. Avoid rapid flashing or jarring screen shake. Respect `prefers-reduced-motion` for UI transitions and decorative animations.
- **Accessibility & Responsiveness:** Maintain WCAG-compliant text contrast on HUD panels, provide clear hover/focus/active states on controls (not relying on glow alone), and keep the HUD legible across both desktop and narrow viewports.

---

## 7. Design Acceptance Checklist

- [x] Overall mood feels calm, dreamy, storybook-like, and night-time oriented.
- [x] Dominant environment colors come from the navy / deep blue / teal palette (`#071326`, `#0B1D35`, `#102B49`, `#16466A`, `#267FA0`).
- [x] Warm moonlight (`#FFF0B7`, `#fbbf24`) is used selectively for focal beacons (moon, lanterns, fireflies).
- [x] Layered nature silhouettes (distant mountains, lone tree, standing stones, bushes) create clear foreground/midground/background separation.
- [x] Mây's *nón lá* and forward hand lantern make player position and `yaw` heading immediately readable.
- [x] HUD and Game Over panels use the Whimsical Nightscape tokens with high text contrast and unobscured gameplay visibility.

---

## Design Principle

**Create a quiet, magical night world; let the deep blue environment and layered silhouettes establish the mood, let warm lantern light and one focal element tell the story, and use glow and decoration sparingly.**

---

<!-- [Phase 2] Ticket-02 ("Ba hòn đảo") standardized palette, 3-night maps, new entities, HUD, menus, and audio -->

## 8. Phase 2: Standardized Palette, 3 Nights & New Visuals

### 8.1 Standardized Color Palette (Max 10% RGB channel deviation)
| Role | Hex |
|---|---|
| Night sky / Fog | `#0E1430` / `#1B2350` |
| Grass / Sand / Wood / Sea of Clouds | `#2F5D50` / `#C9B48A` / `#6B4A2F` / `#12384A` |
| Lit Lantern / Core / Unlit Lantern | `#FFB347` / `#FFE9B0` / `#5B5F6E` |
| Firefly Core / Halo | `#FFF6C2` / `#FFE58A` |
| Shadow Ink Body / Rim / Stunned | `#120A1A` / `#7A3CFF` / `#3A3450` |
| Mây Cloak / Mây Scarf & Wind Charm | `#E8E2D0` / `#C8102E` |
| Gold Border & Score / Gió Lạc (Drifter) | `#F2C14E` / `#8FA3B8` |
| Danger UI / UI Text | `#FF5A5F` / `#F5F1E6` |

- **Ambient Light Formula:** `intensity = 0.15 + 0.55 * (lit_lanterns / total_lanterns)`

### 8.2 Three-Night Map Visuals
- **Night 1 — Đảo Bến:** Circular island (`R=40m`) over `#12384A` sea of clouds, 5 lanterns (`L1..L5`).
- **Night 2 — Đảo Cau:** Twin `R=28m` circular islands at `(0,0,0)` & `(70,0,0)` joined by a wooden bamboo bridge (`#6B4A2F`, `x∈[26,44]`, `z∈[-2,2]`, no railings), 2 glowing jump pads at `(20,0,18)` & `(50,0,-18)`, 6 lanterns (`L1..L6`), Wind Charm `C1` at `(35,0,0)`.
- **Night 3 — Đảo Chuông:** `R=45m` 3-tier island (Tier 0 `Y=0`; Tier 1 `Y=3` ring `12..24m` for `z>0`; Tier 2 `Y=6` disk `R=8m` with `8m`-tall `R=2m` central Bell Tower), 2 radial ramps (`width=3m` at `30°` & `150°` from `r=30m` to `24m`), jump pad at `(0,3,13)`, 7 lanterns (`L1..L7`), Wind Charms `C1, C2`, plus swirling leaf particles + audio cue 2s before wind gusts.

### 8.3 New Entities, Menus, HUD & Audio
- **Mây:** Cream-ivory cloak (`#E8E2D0`) + crimson scarf (`#C8102E`) + *nón lá* + hanging lantern.
- **Gió Lạc (Drifter):** Flowing grey-blue silk ribbon (`#8FA3B8`) that glides, chases, and flees.
- **Bùa Gió (Wind Charm):** Red talisman with gold border (`#C8102E` / `#F2C14E`).
- **3-Night Flow & Menus:** Main Menu → Night Intro (island title + Ông Đăng's words) → Play → Result → Next Night / Dawn Victory screen (with total score) or Retry Night.
- **Pause (`Esc`/`P`) & Settings:** Resume / Restart Night / Settings (Volume & Mouse Sensitivity saved in `localStorage`) / Main Menu.
- **Full HUD:** Flames (top-left), `mm:ss` timer (top-center; turns `#FF5A5F` & blinks at `<=30s`), `k/n` lanterns & score (top-right), 10-slot firefly bar (bottom-center), Dash & Pulse cooldown icons (bottom-right), `"E — Nạp ánh sáng (x/10)"` prompt near unlit lantern, off-screen directional arrow to nearest unlit lantern.
- **Procedural Audio (Web Audio API):** Ambient night sound + SFX for pickup, light lantern, pulse, hit, jump, dash, win, lose, shade spawn, and final 10s countdown.

---

<!-- [Phase 3] Ticket-03 ("Đèn cạn dầu") fuel bars, low-fuel blink, and Colorblind Mode -->

## 9. Phase 3: Lantern Fuel Visuals & Colorblind Mode
- **Lantern Fuel Bar & Low-Fuel Alert:**
  - Lit lanterns display a fuel bar (`0..100`) above the lantern; when `fuel < 30`, both the lantern glow and fuel bar blink slowly at **1 Hz**.
  - Unlit lanterns are distinguishable **without color**: orb squashed vertically by **20%** (`scale.y = 0.8`) with visible paper tear/crack strips.
- **Dynamic Capacity HUD:** Bottom-center firefly bar scales dynamically up to `player.capacity` (`10..20`), showing `carried / capacity`.
- **Colorblind Mode (`Bảng màu dễ phân biệt`, persisted in `localStorage`):**
  - Shadow Ink rim & eyes change from `#7A3CFF` to `#00B3FF`.
  - Danger UI color changes from `#FF5A5F` to `#FFFFFF` paired with a `⚠` icon.
