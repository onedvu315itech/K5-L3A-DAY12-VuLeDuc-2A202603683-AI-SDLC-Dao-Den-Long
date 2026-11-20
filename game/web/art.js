// Technical Art & 3D Prefab Library for Đảo Đèn Lồng (Whimsical Nightscape)
// Translates the 10 reference assets in game/web/assets/*.jpg into Three.js 3D prefabs & procedural Canvas textures.

import * as THREE from 'https://unpkg.com/three@0.170.0/build/three.module.js';

export const PALETTE = {
  night950: 0x071326,
  night900: 0x0B1D35,
  night800: 0x102B49,
  blue700: 0x16466A,
  blue500: 0x267FA0,
  teal300: 0x63C6C8,
  moon100: 0xFFF0B7,
  star100: 0xF7F7FF,
  lavender200: 0xC6B9E8,
  violet900: 0x29233F,
  ink950: 0x171923,
  mist100: 0xE9EDF2,
  raincoatYellow: 0xE5C646,
  amberGlow: 0xFFB347,
  crimson: 0xC8102E,
};

let cachedStarburstTex = null;
let cachedNonLaTex = null;

/**
 * 4/8-Point Starburst Texture inspired by assets/blinking_light.jpg
 */
export function getStarburstTexture() {
  if (cachedStarburstTex) return cachedStarburstTex;
  const size = 128;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  const cx = size / 2;
  const cy = size / 2;

  // Soft outer radial glow
  const grad = ctx.createRadialGradient(cx, cy, 1, cx, cy, cx);
  grad.addColorStop(0.0, 'rgba(255, 255, 255, 1.0)');
  grad.addColorStop(0.18, 'rgba(255, 240, 183, 0.85)');
  grad.addColorStop(0.45, 'rgba(99, 198, 200, 0.28)');
  grad.addColorStop(1.0, 'rgba(7, 19, 38, 0.0)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, size, size);

  // Draw 4 primary diamond spikes + 4 diagonal secondary spikes
  function drawSpike(angleRad, length, width, alpha) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(angleRad);
    ctx.beginPath();
    ctx.moveTo(0, -width);
    ctx.quadraticCurveTo(length * 0.35, 0, length, 0);
    ctx.quadraticCurveTo(length * 0.35, 0, 0, width);
    ctx.quadraticCurveTo(-length * 0.35, 0, -length, 0);
    ctx.quadraticCurveTo(-length * 0.35, 0, 0, -width);
    ctx.closePath();
    ctx.fillStyle = `rgba(247, 247, 255, ${alpha})`;
    ctx.fill();
    ctx.restore();
  }

  drawSpike(0, cx * 0.92, 4.2, 0.95);
  drawSpike(Math.PI / 2, cx * 0.92, 4.2, 0.95);
  drawSpike(Math.PI / 4, cx * 0.54, 2.4, 0.75);
  drawSpike(-Math.PI / 4, cx * 0.54, 2.4, 0.75);

  cachedStarburstTex = new THREE.CanvasTexture(canvas);
  return cachedStarburstTex;
}

/**
 * Fine-line Nón Lá Texture with radial bamboo ribs & 5-petal blossom branch (assets/conical_hat.jpg)
 */
export function getNonLaTexture() {
  if (cachedNonLaTex) return cachedNonLaTex;
  const size = 512;
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  // Warm parchment / bamboo base
  const bg = ctx.createLinearGradient(0, 0, 0, size);
  bg.addColorStop(0, '#D8CCA8');
  bg.addColorStop(0.5, '#EFE9D6');
  bg.addColorStop(1, '#C9B88E');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, size, size);

  // Concentric bamboo stitch rings (horizontal lines in UV space)
  ctx.strokeStyle = 'rgba(23, 25, 35, 0.28)';
  ctx.lineWidth = 2;
  for (let r = 1; r <= 6; r++) {
    const y = (r / 7) * size;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(size, y);
    ctx.stroke();
  }

  // Radial ribs (vertical lines in cylindrical/lathe UV space)
  ctx.strokeStyle = 'rgba(23, 25, 35, 0.35)';
  ctx.lineWidth = 1.8;
  const ribs = 24;
  for (let i = 0; i < ribs; i++) {
    const x = (i / ribs) * size;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, size);
    ctx.stroke();
  }

  // Dark fine rim border at bottom of cone
  ctx.fillStyle = '#29233F';
  ctx.fillRect(0, size - 16, size, 16);

  // Blossom branch (hoa mai / hoa đào) across the front slope
  ctx.strokeStyle = '#171923';
  ctx.lineWidth = 5;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(size * 0.18, size * 0.72);
  ctx.quadraticCurveTo(size * 0.42, size * 0.48, size * 0.74, size * 0.42);
  ctx.stroke();

  // Secondary twig
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(size * 0.44, size * 0.54);
  ctx.quadraticCurveTo(size * 0.52, size * 0.34, size * 0.62, size * 0.28);
  ctx.stroke();

  function drawBlossom(bx, by, radius) {
    ctx.save();
    ctx.translate(bx, by);
    for (let p = 0; p < 5; p++) {
      const a = (p / 5) * Math.PI * 2;
      const px = Math.cos(a) * radius * 0.65;
      const py = Math.sin(a) * radius * 0.65;
      ctx.beginPath();
      ctx.arc(px, py, radius * 0.52, 0, Math.PI * 2);
      ctx.fillStyle = '#FFFDF7';
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#171923';
      ctx.stroke();
    }
    // Blossom center stamens
    ctx.beginPath();
    ctx.arc(0, 0, radius * 0.22, 0, Math.PI * 2);
    ctx.fillStyle = '#FFB347';
    ctx.fill();
    ctx.restore();
  }

  drawBlossom(size * 0.32, size * 0.58, 26);
  drawBlossom(size * 0.48, size * 0.48, 32);
  drawBlossom(size * 0.64, size * 0.43, 24);
  drawBlossom(size * 0.58, size * 0.30, 20);

  cachedNonLaTex = new THREE.CanvasTexture(canvas);
  cachedNonLaTex.wrapS = THREE.RepeatWrapping;
  return cachedNonLaTex;
}

/**
 * Mây Character Prefab — Chibi yellow raincoat (assets/double_character.jpg) +
 * curved floral Nón Lá (assets/conical_hat.jpg) + forward hanging lantern
 */
export function createMayPrefab() {
  const group = new THREE.Group();

  // Soft ground shadow disc
  const shadowMat = new THREE.MeshBasicMaterial({
    color: 0x050B16,
    transparent: true,
    opacity: 0.45,
    depthWrite: false,
  });
  const shadowDisc = new THREE.Mesh(new THREE.CircleGeometry(0.55, 24), shadowMat);
  shadowDisc.rotation.x = -Math.PI / 2;
  shadowDisc.position.y = 0.03;
  group.add(shadowDisc);

  // Small bare/storybook feet (animated during walk)
  const footMat = new THREE.MeshStandardMaterial({ color: 0xF5DEC4, roughness: 0.8 });
  const footGeo = new THREE.SphereGeometry(0.11, 12, 10);
  footGeo.scale(0.95, 0.55, 1.45);
  const leftFoot = new THREE.Mesh(footGeo, footMat);
  leftFoot.position.set(-0.16, 0.07, 0.04);
  const rightFoot = new THREE.Mesh(footGeo, footMat);
  rightFoot.position.set(0.16, 0.07, 0.04);
  group.add(leftFoot, rightFoot);

  // Dark inner legs
  const legMat = new THREE.MeshStandardMaterial({ color: PALETTE.ink950, roughness: 0.9 });
  const legGeo = new THREE.CylinderGeometry(0.065, 0.055, 0.32, 10);
  const leftLeg = new THREE.Mesh(legGeo, legMat);
  leftLeg.position.set(-0.15, 0.22, 0);
  const rightLeg = new THREE.Mesh(legGeo, legMat);
  rightLeg.position.set(0.15, 0.22, 0);
  group.add(leftLeg, rightLeg);

  // A-line flared yellow raincoat (double_character.jpg)
  const coatPoints = [
    new THREE.Vector2(0.0, 0.28),
    new THREE.Vector2(0.54, 0.28),
    new THREE.Vector2(0.46, 0.56),
    new THREE.Vector2(0.35, 0.88),
    new THREE.Vector2(0.24, 1.14),
    new THREE.Vector2(0.0, 1.14),
  ];
  const coatGeo = new THREE.LatheGeometry(coatPoints, 24);
  const coatMat = new THREE.MeshStandardMaterial({
    color: PALETTE.raincoatYellow,
    roughness: 0.62,
    metalness: 0.05,
  });
  const coat = new THREE.Mesh(coatGeo, coatMat);
  group.add(coat);

  // Dark bottom hem outline & center seam line (storybook ink line look)
  const inkMat = new THREE.MeshBasicMaterial({ color: PALETTE.ink950 });
  const hemRing = new THREE.Mesh(new THREE.TorusGeometry(0.535, 0.018, 8, 28), inkMat);
  hemRing.rotation.x = Math.PI / 2;
  hemRing.position.y = 0.29;
  group.add(hemRing);

  const centerSeam = new THREE.Mesh(new THREE.BoxGeometry(0.022, 0.84, 0.02), inkMat);
  centerSeam.position.set(0, 0.71, 0.39);
  centerSeam.rotation.x = -0.28;
  group.add(centerSeam);

  // 3 Front Clasp Buttons + 2 Side Pockets (double_character.jpg details)
  const claspMat = new THREE.MeshStandardMaterial({ color: 0xC49F27, roughness: 0.5 });
  for (let i = 0; i < 3; i++) {
    const y = 0.86 - i * 0.16;
    const z = 0.35 + i * 0.048;
    const clasp = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.045, 0.03), claspMat);
    clasp.position.set(0, y, z);
    const dot = new THREE.Mesh(new THREE.SphereGeometry(0.018, 8, 8), inkMat);
    dot.position.set(0.035, y, z + 0.015);
    group.add(clasp, dot);
  }

  for (const side of [-1, 1]) {
    const pocket = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.13, 0.03), claspMat);
    pocket.position.set(side * 0.26, 0.48, 0.38);
    pocket.rotation.y = side * 0.42;
    group.add(pocket);
  }

  // Flared sleeves
  const sleeveGeo = new THREE.ConeGeometry(0.17, 0.52, 14);
  const leftSleeve = new THREE.Mesh(sleeveGeo, coatMat);
  leftSleeve.position.set(-0.34, 0.82, 0.02);
  leftSleeve.rotation.z = 0.42;
  const rightSleeve = new THREE.Mesh(sleeveGeo, coatMat);
  rightSleeve.position.set(0.32, 0.88, 0.18);
  rightSleeve.rotation.z = -0.35;
  rightSleeve.rotation.x = 0.65; // Reaching forward to hold lantern
  group.add(leftSleeve, rightSleeve);

  // Warm crimson scarf collar
  const scarf = new THREE.Mesh(
    new THREE.TorusGeometry(0.24, 0.065, 10, 22),
    new THREE.MeshStandardMaterial({ color: PALETTE.crimson, roughness: 0.7 })
  );
  scarf.rotation.x = Math.PI / 2;
  scarf.position.y = 1.13;
  group.add(scarf);

  // Oversized storybook hood + shadowed upper face recess + pale chin (double_character.jpg)
  const headShadow = new THREE.Mesh(
    new THREE.SphereGeometry(0.24, 16, 16),
    new THREE.MeshStandardMaterial({ color: PALETTE.ink950, roughness: 0.95 })
  );
  headShadow.position.set(0, 1.31, 0.02);
  const chin = new THREE.Mesh(
    new THREE.SphereGeometry(0.19, 16, 12),
    new THREE.MeshStandardMaterial({ color: 0xF7E4C8, roughness: 0.7 })
  );
  chin.position.set(0, 1.24, 0.07);
  group.add(headShadow, chin);

  // Curved floral Nón Lá (conical_hat.jpg)
  const hatPoints = [];
  const steps = 12;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const r = t * 0.74;
    const y = (1 - Math.pow(t, 0.92)) * 0.42;
    hatPoints.push(new THREE.Vector2(r, y));
  }
  const hatGeo = new THREE.LatheGeometry(hatPoints, 32);
  const hatMat = new THREE.MeshStandardMaterial({
    map: getNonLaTexture(),
    side: THREE.DoubleSide,
    roughness: 0.75,
  });
  const hat = new THREE.Mesh(hatGeo, hatMat);
  hat.position.set(0, 1.38, 0.0);
  hat.rotation.x = -0.08;
  group.add(hat);

  // Forward Hanging Hand Lantern (makes yaw immediately readable)
  const lanternStick = new THREE.Mesh(
    new THREE.CylinderGeometry(0.018, 0.018, 0.55, 8),
    new THREE.MeshStandardMaterial({ color: PALETTE.ink950 })
  );
  lanternStick.rotation.x = Math.PI / 2;
  lanternStick.position.set(0.22, 1.05, 0.44);
  group.add(lanternStick);

  const handLanternGroup = new THREE.Group();
  handLanternGroup.position.set(0.22, 0.96, 0.68);

  const miniCage = new THREE.Mesh(
    new THREE.CylinderGeometry(0.11, 0.075, 0.2, 4),
    new THREE.MeshBasicMaterial({ color: PALETTE.moon100 })
  );
  miniCage.rotation.y = Math.PI / 4;
  const miniCap = new THREE.Mesh(
    new THREE.ConeGeometry(0.14, 0.09, 4),
    new THREE.MeshStandardMaterial({ color: PALETTE.ink950 })
  );
  miniCap.rotation.y = Math.PI / 4;
  miniCap.position.y = 0.13;
  handLanternGroup.add(miniCage, miniCap);

  const handSparkle = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: getStarburstTexture(),
      color: PALETTE.moon100,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      transparent: true,
      opacity: 0.85,
    })
  );
  handSparkle.scale.set(0.65, 0.65, 1);
  handLanternGroup.add(handSparkle);

  const handLight = new THREE.PointLight(PALETTE.amberGlow, 2.8, 13);
  handLight.position.set(0, 0, 0.05);
  handLanternGroup.add(handLight);
  group.add(handLanternGroup);

  group.userData = { leftFoot, rightFoot, handLanternGroup, handSparkle, hat };
  return group;
}

/**
 * Animate Mây walking stride & subtle lantern swing
 */
export function updateMayAnimation(playerGroup, tick, isMoving, reduceMotion = false) {
  const ud = playerGroup.userData;
  if (!ud || !ud.leftFoot) return;
  if (reduceMotion) {
    ud.leftFoot.position.z = 0.04;
    ud.rightFoot.position.z = 0.04;
    ud.handLanternGroup.rotation.z = 0;
    return;
  }
  const phase = tick * 0.22;
  const stride = isMoving ? Math.sin(phase) * 0.14 : 0;
  ud.leftFoot.position.z = 0.04 + stride;
  ud.rightFoot.position.z = 0.04 - stride;
  ud.handLanternGroup.rotation.z = Math.sin(tick * 0.1) * (isMoving ? 0.12 : 0.04);
  const pulse = 0.58 + 0.12 * Math.sin(tick * 0.15);
  ud.handSparkle.scale.set(pulse, pulse, 1);
}

/**
 * Great Lantern Prefab — Ornate Vintage Wrought-Iron Street Lamp (assets/lamp_post.jpg)
 * Preserves orb, tearGroup, fuelBg, fuelFill, ring, light references for syncAllEntities().
 */
export function createGreatLanternPrefab() {
  const g = new THREE.Group();

  const ironMat = new THREE.MeshStandardMaterial({
    color: PALETTE.ink950,
    roughness: 0.55,
    metalness: 0.45,
  });

  // 1. Stepped Moulded Pedestal Base (LatheGeometry matching lamp_post.jpg silhouette)
  const baseProfile = [
    new THREE.Vector2(0.0, 0.0),
    new THREE.Vector2(0.56, 0.0),
    new THREE.Vector2(0.48, 0.08),
    new THREE.Vector2(0.34, 0.16),
    new THREE.Vector2(0.39, 0.26),
    new THREE.Vector2(0.28, 0.36),
    new THREE.Vector2(0.24, 0.72),
    new THREE.Vector2(0.32, 0.85),
    new THREE.Vector2(0.21, 0.98),
    new THREE.Vector2(0.24, 1.18),
    new THREE.Vector2(0.14, 1.35),
    new THREE.Vector2(0.11, 1.48),
  ];
  const baseMesh = new THREE.Mesh(new THREE.LatheGeometry(baseProfile, 20), ironMat);
  g.add(baseMesh);

  // 2. Tall Slender Iron Post + Decorative Collars + Top Diamond Spire Finial
  const postShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.105, 2.55, 14), ironMat);
  postShaft.position.y = 2.68;
  g.add(postShaft);

  // Mid & upper bulbous collars
  for (const cy of [1.62, 2.65, 2.95]) {
    const collar = new THREE.Mesh(new THREE.SphereGeometry(0.16, 14, 10), ironMat);
    collar.scale.set(1, 0.75, 1);
    collar.position.y = cy;
    g.add(collar);
  }

  // Decorative C-scroll side ears at y=1.62 & y=2.78
  for (const side of [-1, 1]) {
    const ear = new THREE.Mesh(new THREE.TorusGeometry(0.11, 0.022, 8, 16, Math.PI * 1.35), ironMat);
    ear.position.set(side * 0.15, 1.62, 0);
    ear.rotation.z = side > 0 ? -0.4 : 0.4;
    g.add(ear);
  }

  // Top Spire Finial (lamp_post.jpg pointed pinnacle)
  const spire = new THREE.Mesh(new THREE.ConeGeometry(0.15, 0.45, 12), ironMat);
  spire.position.y = 4.12;
  const spireBall = new THREE.Mesh(new THREE.SphereGeometry(0.055, 10, 10), ironMat);
  spireBall.position.y = 4.36;
  g.add(spire, spireBall);

  // 3. S-Curved Wrought-Iron Scrollwork Bracket Arm
  const armCurve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(0, 3.25, 0),
    new THREE.Vector3(0.32, 3.45, 0),
    new THREE.Vector3(0.68, 3.92, 0),
    new THREE.Vector3(0.95, 3.82, 0),
    new THREE.Vector3(0.86, 3.45, 0),
  ]);
  const armTube = new THREE.Mesh(new THREE.TubeGeometry(armCurve, 24, 0.032, 8, false), ironMat);
  g.add(armTube);

  // Decorative scrollwork loops inside the bracket arm
  for (const [sx, sy, sr] of [
    [0.22, 3.18, 0.14],
    [0.36, 3.55, 0.13],
    [0.78, 3.68, 0.12],
  ]) {
    const scroll = new THREE.Mesh(new THREE.TorusGeometry(sr, 0.02, 8, 18), ironMat);
    scroll.position.set(sx, sy, 0);
    g.add(scroll);
  }

  // 4. Hanging 4-Sided Tapered Carriage Lantern (suspended at x=0.86, y=3.0)
  const lanternX = 0.86;
  const lanternY = 2.98;

  const capTop = new THREE.Mesh(new THREE.ConeGeometry(0.44, 0.22, 4), ironMat);
  capTop.position.set(lanternX, lanternY + 0.42, 0);
  capTop.rotation.y = Math.PI / 4;

  const capBottom = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.08, 0.12, 4), ironMat);
  capBottom.position.set(lanternX, lanternY - 0.36, 0);
  capBottom.rotation.y = Math.PI / 4;

  const bottomFinial = new THREE.Mesh(new THREE.TorusGeometry(0.07, 0.016, 6, 12), ironMat);
  bottomFinial.position.set(lanternX, lanternY - 0.46, 0);
  g.add(capTop, capBottom, bottomFinial);

  // 4-sided tapered glass lantern core ("orb")
  const orbGeo = new THREE.CylinderGeometry(0.34, 0.22, 0.64, 4);
  orbGeo.rotateY(Math.PI / 4);
  const orbMat = new THREE.MeshStandardMaterial({
    color: PALETTE.blue700,
    roughness: 0.25,
    metalness: 0.1,
  });
  const orb = new THREE.Mesh(orbGeo, orbMat);
  orb.position.set(lanternX, lanternY, 0);

  // Dark wrought-iron corner frame edges around the glass
  const frameEdges = new THREE.LineSegments(
    new THREE.EdgesGeometry(orbGeo),
    new THREE.LineBasicMaterial({ color: PALETTE.ink950 })
  );
  orb.add(frameEdges);

  // Starburst sparkle inside lit lantern
  const sparkle = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: getStarburstTexture(),
      color: PALETTE.moon100,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      transparent: true,
      opacity: 0.0,
    })
  );
  sparkle.scale.set(1.45, 1.45, 1);
  sparkle.position.set(lanternX, lanternY, 0);
  g.add(orb, sparkle);

  // Non-color unlit tear/crack strips
  const tearGroup = new THREE.Group();
  for (let t = 0; t < 2; t++) {
    const tear = new THREE.Mesh(
      new THREE.BoxGeometry(0.62, 0.07, 0.52),
      new THREE.MeshBasicMaterial({ color: PALETTE.ink950 })
    );
    tear.rotation.z = t === 0 ? 0.48 : -0.48;
    tear.rotation.y = t * 1.1;
    tearGroup.add(tear);
  }
  tearGroup.position.set(lanternX, lanternY, 0);
  g.add(tearGroup);

  // Fuel bar above lantern
  const fuelBg = new THREE.Mesh(
    new THREE.BoxGeometry(1.4, 0.14, 0.06),
    new THREE.MeshBasicMaterial({ color: PALETTE.night950 })
  );
  fuelBg.position.set(0.4, 4.55, 0);
  const fuelFill = new THREE.Mesh(
    new THREE.BoxGeometry(1.32, 0.1, 0.08),
    new THREE.MeshBasicMaterial({ color: PALETTE.amberGlow })
  );
  fuelFill.position.set(0.4, 4.55, 0);
  g.add(fuelBg, fuelFill);

  // Safe radius ground ring (R = 6m)
  const ring = new THREE.Mesh(
    new THREE.RingGeometry(5.86, 6.0, 56),
    new THREE.MeshBasicMaterial({
      color: PALETTE.moon100,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.12,
    })
  );
  ring.rotation.x = -Math.PI / 2;
  ring.position.y = 0.05;
  g.add(ring);

  const light = new THREE.PointLight(PALETTE.amberGlow, 0, 24);
  light.position.set(lanternX, lanternY, 0);
  g.add(light);

  return { group: g, orb, sparkle, tearGroup, fuelBg, fuelFill, ring, light };
}

/**
 * Firefly Mote Prefab — Glowing core + 4/8-point Starburst Sprite (assets/blinking_light.jpg)
 */
export function createMotePrefab() {
  const g = new THREE.Group();
  const core = new THREE.Mesh(
    new THREE.SphereGeometry(0.14, 10, 10),
    new THREE.MeshBasicMaterial({ color: PALETTE.moon100 })
  );
  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: getStarburstTexture(),
      color: PALETTE.moon100,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      transparent: true,
      opacity: 0.95,
    })
  );
  sprite.scale.set(1.05, 1.05, 1);
  g.add(core, sprite);
  g.userData = { sprite };
  return g;
}

/**
 * Shadow Ink (Shade) Prefab — Storybook Floating Ghost with Domed Head, Oval Eyes,
 * Wavy "w" Mouth, Stubby Arms & Scalloped Sheet Skirt (assets/ghost.jpg)
 */
export function createGhostShadePrefab() {
  const g = new THREE.Group();

  // Floating oval shadow on ground
  const shadow = new THREE.Mesh(
    new THREE.CircleGeometry(0.52, 20),
    new THREE.MeshBasicMaterial({
      color: 0x050914,
      transparent: true,
      opacity: 0.42,
      depthWrite: false,
    })
  );
  shadow.rotation.x = -Math.PI / 2;
  shadow.position.y = 0.04;
  g.add(shadow);

  // Sculpted ghost sheet geometry (domed top + flared wavy 6-ripple bottom skirt)
  const ghostGeo = new THREE.CylinderGeometry(0.01, 0.68, 1.55, 28, 14, true);
  const posAttr = ghostGeo.attributes.position;
  for (let i = 0; i < posAttr.count; i++) {
    const vx = posAttr.getX(i);
    const vy = posAttr.getY(i); // -0.775 .. +0.775
    const vz = posAttr.getZ(i);
    const normY = (vy + 0.775) / 1.55; // 0 (bottom skirt) .. 1 (top crown)
    const ang = Math.atan2(vz, vx);

    // Smooth dome profile from top crown to flared skirt
    let radius;
    if (normY > 0.65) {
      const t = (normY - 0.65) / 0.35;
      radius = 0.44 * Math.sqrt(Math.max(0, 1 - t * t));
    } else {
      const t = (0.65 - normY) / 0.65;
      radius = 0.44 + t * 0.28;
    }

    // Wavy scalloped hem at the bottom (ghost.jpg 3-front ripples)
    const waveFactor = Math.pow(1 - normY, 2.2);
    const ripple = Math.sin(ang * 5) * 0.08 * waveFactor;
    const hemWaveY = Math.cos(ang * 5) * 0.075 * waveFactor;
    // Slight trailing sweep backward (-Z)
    const trailZ = -0.14 * waveFactor;

    posAttr.setXYZ(
      i,
      Math.cos(ang) * (radius + ripple),
      vy + 0.92 + hemWaveY,
      Math.sin(ang) * (radius + ripple) + trailZ
    );
  }
  ghostGeo.computeVertexNormals();

  const bodyMat = new THREE.MeshStandardMaterial({
    color: PALETTE.lavender200,
    emissive: PALETTE.violet900,
    emissiveIntensity: 0.65,
    roughness: 0.45,
    side: THREE.DoubleSide,
  });
  const body = new THREE.Mesh(ghostGeo, bodyMat);
  g.add(body);

  // Cute stubby side arms (ghost.jpg)
  const armGeo = new THREE.SphereGeometry(0.14, 12, 10);
  armGeo.scale(1.35, 0.75, 0.85);
  const leftArm = new THREE.Mesh(armGeo, bodyMat);
  leftArm.position.set(-0.46, 0.98, 0.1);
  leftArm.rotation.z = 0.35;
  const rightArm = new THREE.Mesh(armGeo, bodyMat);
  rightArm.position.set(0.46, 1.02, 0.12);
  rightArm.rotation.z = -0.35;
  body.add(leftArm, rightArm);

  // Two large dark oval eyes + cute wavy "w" mouth (ghost.jpg)
  const eyeMat = new THREE.MeshBasicMaterial({ color: PALETTE.violet900 });
  const eyeGeo = new THREE.SphereGeometry(0.085, 12, 10);
  eyeGeo.scale(0.95, 1.35, 0.45);

  const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
  leftEye.position.set(-0.14, 1.24, 0.41);
  leftEye.rotation.z = -0.12;

  const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
  rightEye.position.set(0.14, 1.24, 0.41);
  rightEye.rotation.z = 0.12;

  // Wavy "w" mouth using two small torus arcs
  const mouthGroup = new THREE.Group();
  for (const mx of [-0.042, 0.042]) {
    const arc = new THREE.Mesh(
      new THREE.TorusGeometry(0.042, 0.015, 6, 12, Math.PI),
      eyeMat
    );
    arc.rotation.z = Math.PI;
    arc.position.x = mx;
    mouthGroup.add(arc);
  }
  mouthGroup.position.set(0, 1.11, 0.43);
  body.add(leftEye, rightEye, mouthGroup);

  return { group: g, body };
}

/**
 * Sky Dome Enhancements: Concentric Halo Full Moon (assets/noel_moon.jpg & lake.jpg)
 * + Prominent 4/8-point Starburst Stars (assets/blinking_light.jpg)
 */
export function createNightSkyDecor() {
  const skyGroup = new THREE.Group();

  // Concentric Halo Full Moon at (48, 66, -95)
  const moonGroup = new THREE.Group();
  moonGroup.position.set(48, 66, -95);
  moonGroup.lookAt(0, 0, 0);

  const moonCore = new THREE.Mesh(
    new THREE.CircleGeometry(9.5, 40),
    new THREE.MeshBasicMaterial({ color: PALETTE.moon100, fog: false })
  );
  moonGroup.add(moonCore);

  // 3 Concentric storybook halos (noel_moon.jpg)
  const haloConfigs = [
    { r: 14.5, color: PALETTE.moon100, opacity: 0.22 },
    { r: 21.0, color: PALETTE.lavender200, opacity: 0.12 },
    { r: 29.5, color: PALETTE.teal300, opacity: 0.06 },
  ];
  haloConfigs.forEach((hc, idx) => {
    const halo = new THREE.Mesh(
      new THREE.CircleGeometry(hc.r, 40),
      new THREE.MeshBasicMaterial({
        color: hc.color,
        transparent: true,
        opacity: hc.opacity,
        depthWrite: false,
        fog: false,
      })
    );
    halo.position.z = -0.2 * (idx + 1);
    moonGroup.add(halo);
  });
  skyGroup.add(moonGroup);

  // Moon reflection shimmer on the lake below (lake.jpg)
  const reflectionGroup = new THREE.Group();
  reflectionGroup.position.set(34, -10.35, -68);
  for (let i = 0; i < 7; i++) {
    const w = 7.5 - i * 0.7 + (i % 2) * 1.4;
    const strip = new THREE.Mesh(
      new THREE.PlaneGeometry(w, 0.85),
      new THREE.MeshBasicMaterial({
        color: PALETTE.moon100,
        transparent: true,
        opacity: 0.32 - i * 0.035,
        depthWrite: false,
      })
    );
    strip.rotation.x = -Math.PI / 2;
    strip.position.z = i * 2.4;
    reflectionGroup.add(strip);
  }
  skyGroup.add(reflectionGroup);

  // Distant 360° Jagged Mountain Horizon Ring (lake.jpg)
  const mountainMat = new THREE.MeshBasicMaterial({ color: 0x0C223D, side: THREE.DoubleSide });
  const peakCount = 48;
  const mRadius = 175;
  for (let i = 0; i < peakCount; i++) {
    const a = (i / peakCount) * Math.PI * 2;
    const h = 18 + ((i * 37) % 19) * 1.4;
    const w = 26 + ((i * 13) % 11);
    const peak = new THREE.Mesh(new THREE.ConeGeometry(w * 0.55, h, 4), mountainMat);
    peak.position.set(Math.cos(a) * mRadius, -10.5 + h * 0.45, Math.sin(a) * mRadius);
    peak.rotation.y = -a + Math.PI / 4;
    skyGroup.add(peak);
  }

  // 42 Prominent 4/8-Point Starburst Sprites in the sky (blinking_light.jpg)
  const starTex = getStarburstTexture();
  for (let i = 0; i < 42; i++) {
    const a = ((i * 97) % 360) * (Math.PI / 180);
    const elev = 0.22 + ((i * 41) % 60) / 100;
    const dist = 142;
    const sp = new THREE.Sprite(
      new THREE.SpriteMaterial({
        map: starTex,
        color: i % 3 === 0 ? PALETTE.moon100 : PALETTE.star100,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
        transparent: true,
        opacity: 0.85,
        fog: false,
      })
    );
    const sc = 3.2 + (i % 4) * 1.2;
    sp.scale.set(sc, sc, 1);
    sp.position.set(
      dist * Math.cos(elev) * Math.cos(a),
      dist * Math.sin(elev) + 14,
      dist * Math.cos(elev) * Math.sin(a)
    );
    skyGroup.add(sp);
  }

  return skyGroup;
}

/**
 * Standing Stone Trilithon Landmark (assets/stone.jpg) —
 * Two chiseled moonlit stone monoliths topped by a horizontal lintel slab.
 */
export function createStandingStoneTrilithon(scale = 1.0) {
  const g = new THREE.Group();
  const stoneMat = new THREE.MeshStandardMaterial({
    color: PALETTE.blue700,
    emissive: 0x0A1E36,
    emissiveIntensity: 0.4,
    roughness: 0.88,
    flatShading: true,
  });
  const rimMat = new THREE.MeshStandardMaterial({
    color: PALETTE.teal300,
    roughness: 0.6,
    flatShading: true,
  });

  // Left & Right vertical monoliths
  for (const sx of [-1.25, 1.25]) {
    const pillar = new THREE.Mesh(new THREE.BoxGeometry(1.15, 4.4, 0.85), stoneMat);
    pillar.position.set(sx, 2.2, 0);
    pillar.rotation.z = sx < 0 ? -0.03 : 0.03;
    // Moonlit chisel highlight strip on top/outer edge
    const highlight = new THREE.Mesh(new THREE.BoxGeometry(0.16, 4.35, 0.88), rimMat);
    highlight.position.set(sx + (sx < 0 ? -0.52 : 0.52), 2.2, 0);
    g.add(pillar, highlight);
  }

  // Horizontal Lintel Slab on top
  const lintel = new THREE.Mesh(new THREE.BoxGeometry(4.1, 0.95, 1.05), stoneMat);
  lintel.position.set(0, 4.78, 0);
  lintel.rotation.z = 0.015;
  const lintelRim = new THREE.Mesh(new THREE.BoxGeometry(4.12, 0.14, 1.08), rimMat);
  lintelRim.position.set(0, 5.22, 0);
  g.add(lintel, lintelRim);

  g.scale.setScalar(scale);
  return g;
}

/**
 * Lone Wide-Canopy Tree Silhouette Landmark (assets/tree.jpg)
 */
export function createLoneTreeSilhouette(scale = 1.0) {
  const g = new THREE.Group();
  const darkSilhouetteMat = new THREE.MeshStandardMaterial({
    color: PALETTE.night950,
    roughness: 0.95,
  });
  const rimFoliageMat = new THREE.MeshStandardMaterial({
    color: PALETTE.night800,
    roughness: 0.9,
  });

  // Tapered trunk + flared roots
  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.38, 0.72, 2.8, 10),
    darkSilhouetteMat
  );
  trunk.position.y = 1.4;
  g.add(trunk);

  // Branching boughs
  for (const [bx, by, bz, rz, rx] of [
    [-0.9, 2.7, 0.2, 0.65, 0.1],
    [0.95, 2.6, -0.2, -0.62, -0.1],
    [0.1, 2.8, 0.85, 0.1, -0.6],
  ]) {
    const bough = new THREE.Mesh(
      new THREE.CylinderGeometry(0.16, 0.28, 1.8, 8),
      darkSilhouetteMat
    );
    bough.position.set(bx * 0.5, by, bz * 0.5);
    bough.rotation.z = rz;
    bough.rotation.x = rx;
    g.add(bough);
  }

  // Wide multi-cluster oak/banyan canopy silhouette (tree.jpg)
  const clusters = [
    [0, 4.1, 0, 2.1, 1.35, 2.0, darkSilhouetteMat],
    [-1.55, 3.65, 0.3, 1.45, 1.1, 1.4, darkSilhouetteMat],
    [1.6, 3.6, -0.2, 1.5, 1.1, 1.4, darkSilhouetteMat],
    [0.2, 3.7, 1.35, 1.35, 1.0, 1.3, rimFoliageMat],
    [-0.4, 3.6, -1.3, 1.35, 1.0, 1.3, darkSilhouetteMat],
    [-2.3, 3.2, -0.1, 1.05, 0.85, 1.0, rimFoliageMat],
    [2.35, 3.15, 0.2, 1.05, 0.85, 1.0, rimFoliageMat],
  ];
  for (const [cx, cy, cz, sx, sy, sz, mat] of clusters) {
    const sphere = new THREE.Mesh(new THREE.DodecahedronGeometry(1.0, 1), mat);
    sphere.position.set(cx, cy, cz);
    sphere.scale.set(sx, sy, sz);
    g.add(sphere);
  }

  g.scale.setScalar(scale);
  return g;
}

/**
 * Layered Pine Silhouette (assets/lake.jpg) & Teal-Rimmed Bush Cluster (assets/bush.jpg)
 */
export function createPineTreeSilhouette(heightScale = 1.0) {
  const g = new THREE.Group();
  const pineMat = new THREE.MeshStandardMaterial({
    color: PALETTE.night950,
    roughness: 0.92,
  });
  const tiers = 4;
  for (let i = 0; i < tiers; i++) {
    const r = (1.35 - i * 0.24) * heightScale;
    const h = (1.65 - i * 0.18) * heightScale;
    const cone = new THREE.Mesh(new THREE.ConeGeometry(r, h, 9), pineMat);
    cone.position.y = (0.85 + i * 0.88) * heightScale;
    g.add(cone);
  }
  return g;
}

export function createTealBushCluster(scale = 1.0) {
  const g = new THREE.Group();
  const darkBushMat = new THREE.MeshStandardMaterial({
    color: PALETTE.night900,
    roughness: 0.9,
  });
  const tealLeafMat = new THREE.MeshStandardMaterial({
    color: PALETTE.teal300,
    emissive: PALETTE.blue700,
    emissiveIntensity: 0.35,
    roughness: 0.75,
  });

  const blobs = [
    [0, 0.45, 0, 0.75, 0.55, 0.7, darkBushMat],
    [-0.55, 0.36, 0.2, 0.55, 0.42, 0.5, darkBushMat],
    [0.52, 0.38, -0.15, 0.58, 0.44, 0.52, darkBushMat],
    [0.15, 0.55, 0.35, 0.38, 0.32, 0.35, tealLeafMat],
    [-0.35, 0.48, 0.38, 0.32, 0.26, 0.3, tealLeafMat],
  ];
  for (const [bx, by, bz, sx, sy, sz, mat] of blobs) {
    const m = new THREE.Mesh(new THREE.DodecahedronGeometry(1.0, 1), mat);
    m.position.set(bx, by, bz);
    m.scale.set(sx, sy, sz);
    g.add(m);
  }
  g.scale.setScalar(scale);
  return g;
}

/**
 * Decorate an island with perimeter silhouettes (Stonehenge trilithons, lone tree,
 * layered pine trees, and teal-rimmed bushes) away from center play paths.
 */
export function populateIslandScenery(mapGroup, night) {
  if (night === 1) {
    // Đảo Bến (R=40m): Perimeter bushes, pine clusters, 2 standing stone trilithons, 1 lone tree on rim
    const loneTree = createLoneTreeSilhouette(1.15);
    loneTree.position.set(-34, 0, -16);
    loneTree.rotation.y = 0.6;
    mapGroup.add(loneTree);

    const stone1 = createStandingStoneTrilithon(0.95);
    stone1.position.set(26, 0, -28);
    stone1.rotation.y = -0.75;
    const stone2 = createStandingStoneTrilithon(0.8);
    stone2.position.set(-28, 0, 26);
    stone2.rotation.y = 2.2;
    mapGroup.add(stone1, stone2);

    const pineAngles = [0.25, 0.42, 1.85, 2.05, 3.6, 3.78, 5.1, 5.3];
    pineAngles.forEach((ang, idx) => {
      const r = 37.2 + (idx % 2) * 1.1;
      const pine = createPineTreeSilhouette(0.85 + (idx % 3) * 0.22);
      pine.position.set(Math.cos(ang) * r, 0, Math.sin(ang) * r);
      mapGroup.add(pine);
    });

    for (let i = 0; i < 14; i++) {
      const ang = (i / 14) * Math.PI * 2 + 0.15;
      const r = 36.2;
      const bush = createTealBushCluster(0.75 + (i % 3) * 0.18);
      bush.position.set(Math.cos(ang) * r, 0, Math.sin(ang) * r);
      bush.rotation.y = -ang;
      mapGroup.add(bush);
    }
  } else if (night === 2) {
    // Đảo Cau: Two islands at x=0 and x=70 (R=28m)
    const treeA = createLoneTreeSilhouette(1.0);
    treeA.position.set(-23, 0, -10);
    mapGroup.add(treeA);

    const stoneB = createStandingStoneTrilithon(0.9);
    stoneB.position.set(92, 0, 11);
    stoneB.rotation.y = -1.2;
    mapGroup.add(stoneB);

    for (const cx of [0, 70]) {
      for (let i = 0; i < 8; i++) {
        const ang = (i / 8) * Math.PI * 2 + 0.4;
        // Leave bridge corridor clear near ang=0 / ang=PI
        if (Math.abs(Math.sin(ang)) < 0.38) continue;
        const r = 25.5;
        const bush = createTealBushCluster(0.75);
        bush.position.set(cx + Math.cos(ang) * r, 0, Math.sin(ang) * r);
        mapGroup.add(bush);
        if (i % 2 === 0) {
          const pine = createPineTreeSilhouette(0.85);
          pine.position.set(cx + Math.cos(ang + 0.12) * 26.2, 0, Math.sin(ang + 0.12) * 26.2);
          mapGroup.add(pine);
        }
      }
    }
  } else {
    // Night 3: Đảo Chuông (R=45m) — Monumental Standing Stone Trilithons & Pines on outer ring
    for (const ang of [-0.65, -2.45, 2.35]) {
      const r = 41.5;
      const stone = createStandingStoneTrilithon(0.95);
      stone.position.set(Math.cos(ang) * r, 0, Math.sin(ang) * r);
      stone.rotation.y = -ang + Math.PI / 2;
      mapGroup.add(stone);
    }
    const loneTree3 = createLoneTreeSilhouette(1.1);
    loneTree3.position.set(0, 0, -41.5);
    mapGroup.add(loneTree3);

    for (let i = 0; i < 12; i++) {
      const ang = (i / 12) * Math.PI * 2 + 0.2;
      const r = 42.2;
      const bush = createTealBushCluster(0.8);
      bush.position.set(Math.cos(ang) * r, 0, Math.sin(ang) * r);
      mapGroup.add(bush);
    }
  }
}
