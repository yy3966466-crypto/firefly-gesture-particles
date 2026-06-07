import { dist } from './utils.js';
import { LANDMARK } from './hand-detector.js';

const FINGER_TIPS = [
  LANDMARK.THUMB_TIP,
  LANDMARK.INDEX_TIP,
  LANDMARK.MIDDLE_TIP,
  LANDMARK.RING_TIP,
  LANDMARK.PINKY_TIP
];

const FINGER_MCP = [
  LANDMARK.THUMB_TIP - 2,
  LANDMARK.INDEX_MCP,
  LANDMARK.MIDDLE_MCP,
  LANDMARK.RING_MCP,
  LANDMARK.PINKY_MCP
];

function fingertipSpread(points) {
  let sum = 0;
  for (let i = 0; i < 5; i++) {
    const tip = points[FINGER_TIPS[i]];
    const mcp = points[FINGER_MCP[i]];
    if (tip && mcp) sum += dist(tip.x, tip.y, mcp.x, mcp.y);
  }
  return sum / 5;
}

export const GestureState = {
  IDLE: 'idle',
  PALM: 'palm',
  FIST_ATTRACT: 'fist_attract',
  FIST_EXPLODE: 'fist_explode',
  FIST_RECOVER: 'fist_recover',
  CIRCLE_DRAW: 'circle_draw',
  CIRCLE_HOLD: 'circle_hold'
};

const SPREAD_THRESHOLD = 35;
const FIST_THRESHOLD = 15;

export function createGestureClassifier() {
  return {
    state: GestureState.IDLE,
    stateTimer: 0,
    handCenter: { x: 0, y: 0 },
    indexTrail: [],
    circleCenter: null,
    circleRadius: 0,
  };
}

export function classifyGesture(classifier, hands, dt, videoW, videoH, screenW, screenH) {
  const c = classifier;
  c.stateTimer += dt;

  if (!hands || hands.length === 0) {
    if (c.state !== GestureState.IDLE) {
      c.state = GestureState.IDLE;
      c.stateTimer = 0;
    }
    return c;
  }

  const primaryHand = hands[0];
  const points = primaryHand.points;
  const wrist = points[LANDMARK.WRIST];
  const indexTip = points[LANDMARK.INDEX_TIP];

  const midTip = points[LANDMARK.MIDDLE_TIP];
  const rawCx = (wrist.x + (midTip?.x || wrist.x)) / 2;
  const rawCy = (wrist.y + (midTip?.y || wrist.y)) / 2;
  c.handCenter = {
    x: (rawCx / videoW) * screenW,
    y: (rawCy / videoH) * screenH
  };

  const spread = fingertipSpread(points);

  switch (c.state) {
    case GestureState.IDLE:
      if (spread > SPREAD_THRESHOLD) {
        c.state = GestureState.PALM;
        c.stateTimer = 0;
      } else if (spread < FIST_THRESHOLD) {
        c.state = GestureState.FIST_ATTRACT;
        c.stateTimer = 0;
      }
      updateIndexTrail(c, indexTip, 1.0, videoW, videoH, screenW, screenH);
      break;

    case GestureState.PALM:
      if (spread <= SPREAD_THRESHOLD) {
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;

    case GestureState.FIST_ATTRACT:
      if (spread < FIST_THRESHOLD && c.stateTimer > 0.3) {
        c.state = GestureState.FIST_EXPLODE;
        c.stateTimer = 0;
      } else if (spread >= FIST_THRESHOLD) {
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;

    case GestureState.FIST_EXPLODE:
      if (c.stateTimer > 0.1) {
        c.state = GestureState.FIST_RECOVER;
        c.stateTimer = 0;
      }
      break;

    case GestureState.FIST_RECOVER:
      if (c.stateTimer > 2.0 || spread > SPREAD_THRESHOLD) {
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;

    case GestureState.CIRCLE_DRAW:
      updateIndexTrail(c, indexTip, dt, videoW, videoH, screenW, screenH);
      if (checkCircleComplete(c)) {
        c.state = GestureState.CIRCLE_HOLD;
        c.stateTimer = 0;
      } else if (spread > SPREAD_THRESHOLD || spread < FIST_THRESHOLD) {
        c.indexTrail = [];
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;

    case GestureState.CIRCLE_HOLD:
      if (c.stateTimer > 3.0) {
        c.indexTrail = [];
        c.circleCenter = null;
        c.state = GestureState.IDLE;
        c.stateTimer = 0;
      }
      break;
  }

  return c;
}

function updateIndexTrail(c, indexTip, dt, videoW, videoH, screenW, screenH) {
  if (!indexTip) return;

  const sx = (indexTip.x / videoW) * screenW;
  const sy = (indexTip.y / videoH) * screenH;

  c.indexTrail.push({ x: sx, y: sy, time: c.stateTimer });

  const cutoff = c.stateTimer - 2.0;
  c.indexTrail = c.indexTrail.filter(p => p.time > cutoff);

  if (c.state === GestureState.IDLE && c.indexTrail.length > 30) {
    c.state = GestureState.CIRCLE_DRAW;
    c.stateTimer = 0;
  }
}

function checkCircleComplete(c) {
  if (c.indexTrail.length < 20) return false;

  let cx = 0, cy = 0;
  const pts = c.indexTrail;
  for (const p of pts) { cx += p.x; cy += p.y; }
  cx /= pts.length;
  cy /= pts.length;

  let totalAngle = 0;
  for (let i = 1; i < pts.length; i++) {
    const a1 = Math.atan2(pts[i - 1].y - cy, pts[i - 1].x - cx);
    const a2 = Math.atan2(pts[i].y - cy, pts[i].x - cx);
    let da = a2 - a1;
    if (da > Math.PI) da -= Math.PI * 2;
    if (da < -Math.PI) da += Math.PI * 2;
    totalAngle += da;
  }

  if (Math.abs(totalAngle) > Math.PI * 1.6) {
    c.circleCenter = { x: cx, y: cy };
    c.circleRadius = pts.reduce((s, p) => s + dist(p.x, p.y, cx, cy), 0) / pts.length;
    return true;
  }
  return false;
}
