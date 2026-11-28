/**
 * script.js — Blackjack RL frontend
 *
 * Responsibilities:
 *   - Mode switching (Human / Watch Q-Learning / Watch SARSA / Results)
 *   - Human game: send hit/stand to /api/action, render response
 *   - AI watch: fetch full game steps from /api/ai-game, animate them
 *   - Results: fetch /api/results, draw table + learning-curve chart
 */

"use strict";

// ── Start page ────────────────────────────────────────────────────────────────

document.getElementById("btn-start").addEventListener("click", () => {
  document.getElementById("start-page").classList.add("hidden");
  document.querySelector("header").classList.remove("hidden");
  document.querySelector(".mode-bar").classList.remove("hidden");
  document.querySelector("main").classList.remove("hidden");
});

// ── State ─────────────────────────────────────────────────────────────────────
let currentMode   = "human";   // "human" | "qlearning" | "sarsa" | "results"
let currentGameId = null;
let gameInProgress = false;
let aiAnimTimer   = null;

const stats = { win: 0, loss: 0, push: 0 };

// ── DOM references ────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

const modeBtns        = document.querySelectorAll(".mode-btn");
const gameSection     = $("game-section");
const resultsSection  = $("results-section");
const humanControls   = $("human-controls");
const aiControls      = $("ai-controls");

const dealerCardsEl   = $("dealer-cards");
const playerCardsEl   = $("player-cards");
const dealerScoreEl   = $("dealer-score");
const playerScoreEl   = $("player-score");
const outcomeBanner   = $("outcome-banner");

const btnNew    = $("btn-new");
const btnHit    = $("btn-hit");
const btnStand  = $("btn-stand");
const btnAiNew  = $("btn-ai-new");

const statW     = $("stat-w");
const statL     = $("stat-l");
const statP     = $("stat-p");
const statRate  = $("stat-rate");

const speedSlider = $("speed-slider");
const speedLabel  = $("speed-label");

// ── Mode switching ────────────────────────────────────────────────────────────

modeBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    const mode = btn.dataset.mode;
    if (mode === currentMode) return;

    // Cancel any ongoing AI animation
    if (aiAnimTimer) { clearTimeout(aiAnimTimer); aiAnimTimer = null; }

    modeBtns.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentMode = mode;

    if (mode === "results") {
      gameSection.classList.add("hidden");
      resultsSection.classList.remove("hidden");
      loadResults();
    } else {
      gameSection.classList.remove("hidden");
      resultsSection.classList.add("hidden");

      if (mode === "human") {
        humanControls.classList.remove("hidden");
        aiControls.classList.add("hidden");
      } else {
        humanControls.classList.add("hidden");
        aiControls.classList.remove("hidden");
      }

      resetBoard();
    }
  });
});

// ── Card rendering ────────────────────────────────────────────────────────────

/**
 * Build a card DOM element.
 * @param {{ rank: string, suit: string, red: boolean }|null} card
 *   Pass null to render a face-down card.
 */
function makeCardEl(card) {
  const el = document.createElement("div");
  el.className = "card";

  if (!card) {
    el.classList.add("hidden");
    return el;
  }

  el.classList.add(card.red ? "red" : "black");

  const top  = document.createElement("div");
  top.className = "rank-top";
  top.textContent = card.rank;

  const mid  = document.createElement("div");
  mid.className = "suit-mid";
  mid.textContent = card.suit;

  const bot  = document.createElement("div");
  bot.className = "rank-bot";
  bot.textContent = card.rank;

  el.append(top, mid, bot);
  return el;
}

function renderHand(container, cards, hideFirst = false) {
  container.innerHTML = "";
  if (!cards) return;
  cards.forEach((card, i) => {
    container.appendChild(makeCardEl(i === 0 && hideFirst ? null : card));
  });
}

// ── Outcome banner ────────────────────────────────────────────────────────────

function showOutcome(result, message) {
  const labels = { win: "★ WIN ★", loss: "✗ LOSS", push: "↔ PUSH" };
  outcomeBanner.textContent = `${labels[result] ?? result}  —  ${message}`;
  outcomeBanner.className   = `outcome-banner ${result}`;
  outcomeBanner.classList.remove("hidden");
}

function hideOutcome() {
  outcomeBanner.classList.add("hidden");
  outcomeBanner.className = "outcome-banner hidden";
}

// ── Render a full game state snapshot ────────────────────────────────────────

/**
 * Update the board from a state object returned by the API.
 * @param {object} state
 * @param {boolean} inProgress  True while the hand is still being played.
 */
function applyState(state, inProgress = !state.done) {
  // Dealer: show hidden card until game ends
  renderHand(dealerCardsEl, state.done
    ? state.dealer_cards
    : [state.dealer_upcard, null],   // null = face-down hole card
    false
  );
  dealerScoreEl.textContent = state.done ? state.dealer_score : "?";

  // Player
  renderHand(playerCardsEl, state.player_cards);
  playerScoreEl.textContent = state.player_score;

  if (state.done) {
    showOutcome(state.result, state.message);
    updateStats(state.result);
  } else {
    hideOutcome();
  }
}

// ── Session stats ─────────────────────────────────────────────────────────────

function updateStats(result) {
  if (result === "win")  stats.win++;
  if (result === "loss") stats.loss++;
  if (result === "push") stats.push++;

  statW.textContent = stats.win;
  statL.textContent = stats.loss;
  statP.textContent = stats.push;

  const total = stats.win + stats.loss + stats.push;
  statRate.textContent = total
    ? `${((stats.win / total) * 100).toFixed(1)}%`
    : "—";
}

// ── Reset board ───────────────────────────────────────────────────────────────

function resetBoard() {
  dealerCardsEl.innerHTML  = "";
  playerCardsEl.innerHTML  = "";
  dealerScoreEl.textContent = "";
  playerScoreEl.textContent = "";
  hideOutcome();
  currentGameId  = null;
  gameInProgress = false;

  btnHit.disabled   = true;
  btnStand.disabled = true;
}

// ── Human mode ────────────────────────────────────────────────────────────────

btnNew.addEventListener("click", async () => {
  resetBoard();
  const state = await post("/api/new-game", {});
  currentGameId  = state.game_id;
  gameInProgress = !state.done;
  applyState(state);

  btnHit.disabled   = state.done;
  btnStand.disabled = state.done;
});

btnHit.addEventListener("click",   () => sendAction("hit"));
btnStand.addEventListener("click", () => sendAction("stand"));

async function sendAction(action) {
  if (!currentGameId || !gameInProgress) return;
  const state = await post("/api/action", { game_id: currentGameId, action });
  gameInProgress = !state.done;
  applyState(state);
  btnHit.disabled   = state.done;
  btnStand.disabled = state.done;
}

// ── AI watch mode ─────────────────────────────────────────────────────────────

btnAiNew.addEventListener("click", () => {
  if (aiAnimTimer) { clearTimeout(aiAnimTimer); aiAnimTimer = null; }
  resetBoard();
  runAiGame(currentMode);  // currentMode is "qlearning" or "sarsa"
});

async function runAiGame(agentKey) {
  btnAiNew.disabled = true;

  const data  = await post("/api/ai-game", { agent: agentKey });
  const steps = data.steps;
  let   i     = 0;

  function showNext() {
    if (i >= steps.length) {
      btnAiNew.disabled = false;
      return;
    }
    applyState(steps[i], i < steps.length - 1);
    i++;
    aiAnimTimer = setTimeout(showNext, getSpeed());
  }

  showNext();
}

function getSpeed() {
  return parseInt(speedSlider.value, 10);
}

speedSlider.addEventListener("input", () => {
  speedLabel.textContent = `${(getSpeed() / 1000).toFixed(1)} s / move`;
});

// ── Results ───────────────────────────────────────────────────────────────────

async function loadResults() {
  const data = await fetch("/api/results").then(r => r.json());
  renderResultsTable(data.results);
  drawLearningCurves(data.curves);
}

function renderResultsTable(rows) {
  const tbody = $("results-tbody");
  tbody.innerHTML = "";

  rows.forEach(row => {
    const tr = document.createElement("tr");
    const rate  = parseFloat(row.win_rate).toFixed(2);
    const avg   = parseFloat(row.average_reward).toFixed(4);

    tr.innerHTML = `
      <td>${row.algorithm}</td>
      <td>${row.schedule}</td>
      <td>${row.seed}</td>
      <td>${row.wins}</td>
      <td>${row.losses}</td>
      <td>${row.draws}</td>
      <td><strong>${rate}%</strong></td>
      <td>${avg}</td>
    `;
    tbody.appendChild(tr);
  });
}

/**
 * Draw learning curves onto the <canvas> using the Canvas 2D API.
 * No external chart library needed.
 *
 * Groups rows by (algorithm, schedule) and draws one line per group
 * (mean across seeds) with a shaded min–max band.
 */
function drawLearningCurves(rows) {
  const canvas = $("curves-canvas");
  const ctx    = canvas.getContext("2d");
  const W      = canvas.width;
  const H      = canvas.height;

  // Layout margins
  const ml = 54, mr = 20, mt = 24, mb = 44;
  const plotW = W - ml - mr;
  const plotH = H - mt - mb;

  // ── Group data by (algorithm, schedule) ──────────────────────────────────
  const groups = {};
  rows.forEach(r => {
    const key = `${r.algorithm} (${r.schedule})`;
    if (!groups[key]) groups[key] = {};
    const ep  = parseInt(r.episode);
    const wr  = parseFloat(r.win_rate);
    if (!groups[key][ep]) groups[key][ep] = [];
    groups[key][ep].push(wr);
  });

  // ── Determine axis ranges ─────────────────────────────────────────────────
  const allEps  = [...new Set(rows.map(r => parseInt(r.episode)))].sort((a,b)=>a-b);
  const minEp   = allEps[0];
  const maxEp   = allEps[allEps.length - 1];
  const minRate = 30;
  const maxRate = 50;

  const xScale = ep   => ml + ((ep - minEp) / (maxEp - minEp)) * plotW;
  const yScale = rate => mt + plotH - ((rate - minRate) / (maxRate - minRate)) * plotH;

  // ── Draw background ───────────────────────────────────────────────────────
  ctx.fillStyle = "#131e28";
  ctx.fillRect(0, 0, W, H);

  // Grid lines
  ctx.strokeStyle = "#1e3040";
  ctx.lineWidth   = 1;
  for (let r = minRate; r <= maxRate; r += 5) {
    const y = yScale(r);
    ctx.beginPath(); ctx.moveTo(ml, y); ctx.lineTo(ml + plotW, y); ctx.stroke();
    ctx.fillStyle   = "#6a8a9a";
    ctx.font        = "11px monospace";
    ctx.textAlign   = "right";
    ctx.fillText(`${r}%`, ml - 6, y + 4);
  }

  // X axis labels
  ctx.fillStyle = "#6a8a9a";
  ctx.font      = "11px monospace";
  ctx.textAlign = "center";
  allEps.forEach(ep => {
    const x = xScale(ep);
    ctx.fillText(ep >= 1000 ? `${ep/1000}k` : ep, x, mt + plotH + 20);
  });

  // Axis titles
  ctx.fillStyle = "#c9a84c";
  ctx.font      = "12px Georgia";
  ctx.textAlign = "center";
  ctx.fillText("Training Episodes", ml + plotW / 2, H - 4);

  ctx.save();
  ctx.translate(14, mt + plotH / 2);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText("Win Rate (%)", 0, 0);
  ctx.restore();

  // ── Colors per group ──────────────────────────────────────────────────────
  const palette = {
    "Q-learning (fixed)": "#00d4ff",
    "Q-learning (decay)": "#7fff00",
    "SARSA (fixed)":      "#ff6b6b",
    "SARSA (decay)":      "#ff9f43",
  };

  // ── Draw each group ───────────────────────────────────────────────────────
  Object.entries(groups).forEach(([key, epData]) => {
    const color   = palette[key] ?? "#ffffff";
    const episodes = allEps.filter(ep => epData[ep]);

    const means = episodes.map(ep => {
      const vals = epData[ep];
      return vals.reduce((a, b) => a + b, 0) / vals.length;
    });
    const mins = episodes.map(ep => Math.min(...epData[ep]));
    const maxs = episodes.map(ep => Math.max(...epData[ep]));

    // Shaded band (min–max)
    ctx.beginPath();
    episodes.forEach((ep, i) => ctx.lineTo(xScale(ep), yScale(maxs[i])));
    [...episodes].reverse().forEach((ep, i) => {
      ctx.lineTo(xScale(ep), yScale(mins[episodes.length - 1 - i]));
    });
    ctx.closePath();
    ctx.fillStyle = color + "28";   // 16% opacity hex suffix
    ctx.fill();

    // Mean line
    ctx.beginPath();
    episodes.forEach((ep, i) => {
      i === 0
        ? ctx.moveTo(xScale(ep), yScale(means[i]))
        : ctx.lineTo(xScale(ep), yScale(means[i]));
    });
    ctx.strokeStyle = color;
    ctx.lineWidth   = 2;
    ctx.stroke();
  });

  // ── Legend ────────────────────────────────────────────────────────────────
  const legendKeys = Object.keys(palette);
  const lx = ml + plotW - 196;
  const ly = mt + 8;

  ctx.fillStyle   = "rgba(13,27,42,.8)";
  ctx.strokeStyle = "#2a3a4a";
  ctx.lineWidth   = 1;
  ctx.beginPath();
  ctx.roundRect(lx - 8, ly - 6, 210, legendKeys.length * 20 + 10, 6);
  ctx.fill(); ctx.stroke();

  legendKeys.forEach((key, i) => {
    const y = ly + i * 20 + 4;
    ctx.fillStyle = palette[key];
    ctx.fillRect(lx, y - 1, 22, 3);

    ctx.fillStyle = "#dce8f0";
    ctx.font      = "11px monospace";
    ctx.textAlign = "left";
    ctx.fillText(key, lx + 28, y + 4);
  });
}

// ── Generic POST helper ───────────────────────────────────────────────────────

async function post(url, body) {
  const res = await fetch(url, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(body),
  });
  return res.json();
}
