const STORE_KEY = "svt3-prof-belhajj-v1";
const THEMES = {
  nutrition: { short: "Nutrition", badge: "Expert en Nutrition", image: "assets/digestive-system.svg", desc: "Digestion, équilibre alimentaire, santé et homéostasie." },
  genetics: { short: "Génétique", badge: "Génie Génétique", image: "assets/dna-double-helix.jpg", desc: "ADN, expression des gènes, hérédité et diversité." },
  earth: { short: "Le Globe & l’évolution", badge: "Maître du Globe", image: "assets/tectonic-plate-boundaries.png", desc: "Tectonique des plaques, histoire de la Terre et évolution du vivant." }
};
const root = document.getElementById("app");
let bank = null;
let saved = loadStored();
let session = null;
let lastCompleted = null;
let clockHandle = null;

function loadStored() {
  try { return JSON.parse(localStorage.getItem(STORE_KEY)) || { best: {}, resume: null, completed: 0 }; }
  catch { return { best: {}, resume: null, completed: 0 }; }
}
function persist() {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(saved)); }
  catch { /* Storage can be disabled or full; the quiz still works in memory. */ }
}
function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}
function shuffle(list) {
  const out = [...list];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}
function allQuestions() { return bank.themes.flatMap(t => t.questions); }
function findQuestion(themeId, id) { return bank.themes.find(t => t.id === themeId)?.questions.find(q => q.id === id); }
function formatTime(seconds) {
  const s = Math.max(0, Math.floor(seconds));
  return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
}
function elapsed() { return session ? Math.floor((Date.now() - session.startedAt) / 1000) : 0; }
function icon(name) {
  const paths = {
    arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    book: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21z"/><path d="M4 5.5v13A2.5 2.5 0 0 1 6.5 16H20"/>',
    repeat: '<path d="m17 2 4 4-4 4"/><path d="M3 11V9a3 3 0 0 1 3-3h15M7 22l-4-4 4-4"/><path d="M21 13v2a3 3 0 0 1-3 3H3"/>',
    home: '<path d="m3 10 9-7 9 7"/><path d="M5 9v12h14V9M9 21v-7h6v7"/>',
    spark: '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z"/><path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16Z"/>',
    leaf: '<path d="M20 4c-9 0-15 3-15 10a6 6 0 0 0 6 6c7 0 10-6 9-16Z"/><path d="M5 19c3-4 6-6 11-9"/>',
    dna: '<path d="M7 3c0 6 10 12 10 18M17 3c0 6-10 12-10 18M7 6h10M8 10h8M8 14h8M7 18h10"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18"/>'
  };
  return `<svg viewBox="0 0 24 24" aria-hidden="true">${paths[name] || paths.spark}</svg>`;
}
function bestLabel(themeId) {
  const best = saved.best?.[themeId];
  return best ? `Meilleur : ${best.percent} %` : "À découvrir";
}
function themeIcon(id) { return id === "nutrition" ? "leaf" : id === "genetics" ? "dna" : "globe"; }
function resumeMarkup() {
  if (!saved.resume) return "";
  const info = saved.resume;
  const progress = Math.min(info.index + (info.answers?.[info.index] ? 1 : 0), info.queue?.length || 0);
  const label = info.label || "ta séance";
  return `<aside class="resume-card" aria-label="Séance interrompue">
    <div class="resume-copy"><strong>Tu avais commencé ${escapeHTML(label)}.</strong><span>${progress} question${progress > 1 ? "s" : ""} traitée${progress > 1 ? "s" : ""} sur ${info.queue?.length || 0}. Ta progression est enregistrée sur cet appareil.</span></div>
    <div class="mini-actions"><button class="btn btn-primary" data-action="resume">Reprendre</button><button class="btn btn-secondary" data-action="discard-resume">Effacer</button></div>
  </aside>`;
}
function renderHome() {
  clearClock();
  const cards = bank.themes.map((theme, index) => {
    const meta = THEMES[theme.id];
    return `<article class="theme-card" data-theme-id="${theme.id}">
      <div class="theme-art"><span class="art-number">0${index + 1} / 03</span><span class="art-icon">${icon(themeIcon(theme.id))}</span><img src="${meta.image}" alt="Illustration éducative : ${escapeHTML(meta.short)}" loading="lazy"></div>
      <div class="theme-body"><h3>${escapeHTML(theme.titre)}</h3><p>${escapeHTML(meta.desc)}</p>
        <div class="card-meta"><span class="question-count">60 questions · ${theme.questions.filter(q => q.type === "vrai-faux").length} Vrai/Faux</span><span class="best-score">${escapeHTML(bestLabel(theme.id))}</span></div>
        <button class="card-button" data-action="start-theme" data-theme="${theme.id}">Réviser ce thème <span aria-hidden="true">→</span></button>
      </div>
    </article>`;
  }).join("");
  root.setAttribute("aria-busy", "false");
  root.innerHTML = `<div class="page-wrap">
    ${resumeMarkup()}
    <section class="hero" aria-labelledby="hero-title">
      <div class="hero-copy">
        <p class="eyebrow">Espace de révision · 3e Sciences expérimentales</p>
        <h1 id="hero-title">Le vivant,<br><span>ça se comprend.</span></h1>
        <p class="hero-lead">Des questions pour t’entraîner, des explications pour progresser. Avance à ton rythme, sans pression et sans compte.</p>
        <div class="hero-actions"><button class="btn btn-primary" data-action="start-exam">Examen complet ${icon("arrow")}</button><button class="btn btn-secondary" data-action="start-random">Quiz rapide · 15 questions</button></div>
        <div class="hero-metrics"><div class="metric"><strong>180</strong><span>questions corrigées</span></div><div class="metric"><strong>03</strong><span>thèmes du programme</span></div><div class="metric"><strong>0</strong><span>donnée envoyée</span></div></div>
      </div>
      <div class="hero-visual" aria-hidden="true"><div class="hero-orbit"></div><div class="hero-sticker"><svg viewBox="0 0 80 80"><path d="M40 67S13 52 13 32c0-12 16-18 27-3 11-15 27-9 27 3 0 20-27 35-27 35Z"/><path d="M40 29v36M29 39l11 7 12-8M29 52l11 6 11-7"/><circle cx="40" cy="20" r="3" fill="currentColor"/></svg><span class="hero-sticker-label">SVT · 3</span></div><span class="hero-note">Curiosité d’abord</span></div>
    </section>
    <div class="section-heading"><div><p class="eyebrow">Choisis ton terrain d’exploration</p><h2>Trois thèmes, un objectif : comprendre.</h2></div><p>Chaque thème contient 60 questions mélangées à chaque partie.</p></div>
    <section class="theme-grid" aria-label="Thèmes de révision">${cards}</section>
    <section class="exam-banner" aria-label="Mode examen"><div class="exam-copy"><span class="exam-icon">✦</span><div><strong>Prêt·e pour le grand tour ?</strong><span>Les 180 questions, tous thèmes confondus, en mode examen.</span></div></div><button class="btn btn-secondary" data-action="start-exam">Lancer l’examen complet ${icon("arrow")}</button></section>
    <p class="home-note"><strong>À propos du contenu :</strong> les questions reprises du document fourni sont identifiées dans les données. Le document transmis était incomplet ; les compléments sont signalés. Quelques formulations ou clés ont été précisées pour éviter une confusion scientifique. <strong>Vie privée :</strong> aucun compte, publicité, suivi ni envoi réseau ; les scores sont stockés uniquement dans le navigateur de cet appareil.</p>
  </div>`;
}
function makeQueue(questions) {
  return shuffle(questions).map(q => ({ theme: q.theme, id: q.id, optionOrder: shuffle(q.options.map((_, i) => i)) }));
}
function materialize(ref) {
  const q = findQuestion(ref.theme, ref.id);
  if (!q) return null;
  const order = ref.optionOrder || q.options.map((_, i) => i);
  return { ...q, optionOrder: order, displayOptions: order.map(i => q.options[i]), displayCorrect: order.map((original, display) => q.reponses_correctes.includes(original) ? display : -1).filter(i => i >= 0) };
}
function sessionLabel(type, themeId) {
  if (type === "exam") return "l’examen complet";
  if (type === "quick") return "le quiz rapide";
  if (type === "review") return "la révision de tes erreurs";
  return `le thème ${THEMES[themeId]?.short || ""}`;
}
function startSession(type, themeId = null, refs = null) {
  let questions;
  if (refs) questions = refs.map(ref => materialize(ref)).filter(Boolean);
  else if (type === "exam") questions = allQuestions();
  else if (type === "quick") questions = shuffle(allQuestions()).slice(0, 15);
  else questions = bank.themes.find(t => t.id === themeId)?.questions || [];
  const queue = refs ? questions : makeQueue(questions).map(materialize).filter(Boolean);
  const label = sessionLabel(type, themeId);
  session = { type, themeId, label, queue, index: 0, answers: [], selected: [], startedAt: Date.now() };
  saved.resume = null;
  persist();
  renderQuiz();
}
function saveResume() {
  if (!session) return;
  saved.resume = { type: session.type, themeId: session.themeId, label: session.label,
    queue: session.queue.map(q => ({ theme: q.theme, id: q.id, optionOrder: q.optionOrder })),
    index: session.index, answers: session.answers, selected: session.selected, startedAt: session.startedAt };
  persist();
}
function resumeSession() {
  const r = saved.resume;
  if (!r) return;
  const queue = r.queue.map(materialize).filter(Boolean);
  session = { ...r, queue, startedAt: r.startedAt || Date.now() };
  saved.resume = null;
  persist();
  renderQuiz();
}
function discardResume() { saved.resume = null; persist(); renderHome(); }
function renderIllustration(q) {
  if (!q.illustration) return "";
  return `<figure class="question-illustration"><img src="${escapeHTML(q.illustration.src)}" alt="${escapeHTML(q.illustration.alt)}"><figcaption>${escapeHTML(q.illustration.alt)}<br><span>Illustration pédagogique intégrée à l’application.</span></figcaption></figure>`;
}
function renderQuiz(focusAction = false) {
  if (!session) return renderHome();
  clearClock();
  const q = session.queue[session.index];
  if (!q) return finishSession();
  const submitted = Boolean(session.answers[session.index]);
  const selected = submitted ? session.answers[session.index].selected : session.selected;
  const progress = Math.round(((session.index + 1) / session.queue.length) * 100);
  const themeTitle = bank.themes.find(t => t.id === q.theme)?.titre || "SVT 3";
  const multi = q.reponses_correctes.length > 1;
  const options = q.displayOptions.map((text, i) => {
    const chosen = selected.includes(i);
    const correct = q.displayCorrect.includes(i);
    const wrong = submitted && chosen && !correct;
    const expected = submitted && correct && !chosen;
    const classes = ["answer-option", chosen ? "is-selected" : "", submitted && correct && chosen ? "is-correct" : "", wrong ? "is-wrong" : "", expected ? "is-expected" : ""].filter(Boolean).join(" ");
    const mark = submitted ? (correct ? "✓" : chosen ? "×" : "") : "";
    return `<button class="${classes}" data-action="select-answer" data-index="${i}" aria-pressed="${chosen}" ${submitted ? "disabled" : ""}>
      <span class="choice-key">${String.fromCharCode(65 + i)}</span><span class="choice-text">${escapeHTML(text)}</span><span class="choice-check" aria-hidden="true">${mark}</span>
    </button>`;
  }).join("");
  let feedback = "";
  if (submitted) {
    const answer = session.answers[session.index];
    const source = q.note_pedagogique ? `<p class="feedback-source">Note de précision pédagogique : ${escapeHTML(q.note_pedagogique)}</p>` : "";
    feedback = `<section class="feedback ${answer.correct ? "correct" : "incorrect"}" aria-live="polite"><h2 class="feedback-title">${answer.correct ? "✓ Bien joué, c’est juste !" : "↗ Pas tout à fait — on apprend en corrigeant."}</h2><p>${escapeHTML(q.explication)}</p>${source}</section>`;
  }
  root.setAttribute("aria-busy", "false");
  root.innerHTML = `<div class="quiz-wrap">
    <div class="quiz-top"><div class="quiz-course"><strong>${escapeHTML(themeTitle)}</strong><span>${escapeHTML(session.label)} · ${session.queue.length} questions</span></div><div class="quiz-tools"><span class="timer-pill" id="timer" aria-label="Temps écoulé">${formatTime(elapsed())}</span><button class="btn btn-quiet" data-action="quit-quiz">Quitter</button></div></div>
    <div class="progress-block"><div class="progress-label"><span>Question ${session.index + 1} sur ${session.queue.length}</span><span>${progress} %</span></div><div class="progress-track" role="progressbar" aria-label="Progression du quiz" aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100"><div class="progress-value" style="width:${progress}%"></div></div></div>
    <section class="question-card" aria-labelledby="question-title"><div class="question-kicker">${q.type === "vrai-faux" ? "Vrai ou faux" : multi ? "Plusieurs réponses" : "Une seule réponse"} <span aria-hidden="true">·</span> ${escapeHTML(THEMES[q.theme]?.short || "SVT")}</div><h1 id="question-title">${escapeHTML(q.question)}</h1>${multi && !submitted ? '<p class="question-hint">Plusieurs réponses peuvent être justes. Sélectionne toutes celles qui conviennent.</p>' : ""}<div class="answer-list" role="group" aria-label="Propositions de réponse">${options}</div>${renderIllustration(q)}${feedback}<div class="question-actions"><span class="action-help">${submitted ? "Prends le temps de lire l’explication." : "Tu peux changer ta réponse avant validation."}</span>${submitted ? `<button class="btn btn-primary" data-action="continue">${session.index + 1 === session.queue.length ? "Voir mon bilan" : "Question suivante"} ${icon("arrow")}</button>` : `<button class="btn btn-primary" data-action="submit" ${selected.length ? "" : "disabled"}>Valider ma réponse</button>`}</div></section>
  </div>`;
  startClock();
  if (focusAction) root.querySelector('[data-action="continue"]')?.focus();
}
function currentAnswerCorrect(q, selected) {
  const a = [...selected].sort((x, y) => x - y);
  const b = [...q.displayCorrect].sort((x, y) => x - y);
  return a.length === b.length && a.every((v, i) => v === b[i]);
}
function finishAnswer() {
  if (!session) return;
  const q = session.queue[session.index];
  if (!session.selected.length) return;
  session.answers[session.index] = { selected: [...session.selected], correct: currentAnswerCorrect(q, session.selected) };
  saveResume();
  renderQuiz(true);
}
function nextQuestion() {
  if (session.index + 1 < session.queue.length) {
    session.index++;
    session.selected = [];
    saveResume();
    renderQuiz();
  } else finishSession();
}
function themeStats(queue, answers) {
  const stats = {};
  for (let i = 0; i < queue.length; i++) {
    const id = queue[i].theme;
    stats[id] ||= { total: 0, correct: 0 };
    stats[id].total++;
    if (answers[i]?.correct) stats[id].correct++;
  }
  return stats;
}
function badgeFor(stats, type, themeId) {
  if (type === "theme" && themeId && (stats[themeId]?.correct || 0) / Math.max(stats[themeId]?.total || 1, 1) >= .85) return THEMES[themeId].badge;
  const percent = Math.round((session.answers.filter(a => a?.correct).length / session.queue.length) * 100);
  if (percent >= 90) return "Champion·ne de SVT";
  if (percent >= 70) return "Explorateur·rice confirmé·e";
  if (percent >= 50) return "Curieux·se en progression";
  return "Premier pas scientifique";
}
function finishSession() {
  if (!session) return;
  clearClock();
  const completed = { ...session, elapsed: elapsed(), stats: themeStats(session.queue, session.answers) };
  const correct = session.answers.filter(a => a?.correct).length;
  const percent = Math.round(correct / Math.max(session.queue.length, 1) * 100);
  completed.correct = correct;
  completed.percent = percent;
  completed.badge = badgeFor(completed.stats, session.type, session.themeId);
  lastCompleted = completed;
  saved.completed = (saved.completed || 0) + 1;
  for (const [themeId, stat] of Object.entries(completed.stats)) {
    const value = Math.round(stat.correct / stat.total * 100);
    if (!saved.best[themeId] || value > saved.best[themeId].percent) saved.best[themeId] = { percent: value, date: new Date().toISOString().slice(0, 10) };
  }
  saved.resume = null;
  persist();
  session = completed;
  renderResults(completed);
}
function resultThemeCards(stats) {
  return Object.entries(stats).map(([id, stat]) => `<div class="theme-result"><strong>${escapeHTML(bank.themes.find(t => t.id === id)?.titre || id)}</strong><span>${stat.correct} / ${stat.total} · ${Math.round(stat.correct / stat.total * 100)} %</span></div>`).join("");
}
function mistakesMarkup(result) {
  const mistakes = result.queue.map((q, i) => ({ q, answer: result.answers[i], i })).filter(x => !x.answer?.correct);
  if (!mistakes.length) return `<div class="empty-mistakes">Aucune erreur à revoir. Bravo pour ta régularité !</div>`;
  return `<div class="mistake-list">${mistakes.map(({ q, answer, i }) => {
    const correct = q.displayCorrect.map(n => q.displayOptions[n]).join(" · ");
    const chosen = (answer?.selected || []).map(n => q.displayOptions[n]).join(" · ") || "Aucune réponse";
    return `<details class="mistake-item"><summary>${i + 1}. ${escapeHTML(q.question)}</summary><div class="mistake-detail"><div><strong>Ta réponse :</strong> ${escapeHTML(chosen)}</div><div><strong>Réponse attendue :</strong> ${escapeHTML(correct)}</div><p>${escapeHTML(q.explication)}</p>${q.note_pedagogique ? `<p><strong>Précision :</strong> ${escapeHTML(q.note_pedagogique)}</p>` : ""}</div></details>`;
  }).join("")}</div>`;
}
function renderResults(result) {
  clearClock();
  const missed = result.answers.filter(a => !a?.correct).length;
  const typeLabel = result.type === "exam" ? "Examen complet" : result.type === "quick" ? "Quiz rapide" : result.type === "review" ? "Révision des erreurs" : THEMES[result.themeId]?.short || "Thème";
  root.setAttribute("aria-busy", "false");
  root.innerHTML = `<div class="results-wrap">
    <section class="results-hero"><div><p class="eyebrow">${escapeHTML(typeLabel)} · terminé</p><h1>${result.percent >= 70 ? "Très beau travail !" : "Chaque réponse te fait avancer."}</h1><p>Tu as répondu à ${result.queue.length} question${result.queue.length > 1 ? "s" : ""}. Lis les explications, puis reviens t’entraîner quand tu veux.</p><span class="badge-chip">✦ ${escapeHTML(result.badge)}</span></div><div class="score-ring" aria-label="${result.percent} pour cent"><strong>${result.percent}%</strong><span>réussite</span></div></section>
    <section class="result-metrics" aria-label="Résumé"><div class="result-metric"><strong>${result.correct} / ${result.queue.length}</strong><span>bonnes réponses</span></div><div class="result-metric"><strong>${formatTime(result.elapsed)}</strong><span>temps passé</span></div><div class="result-metric"><strong>${missed}</strong><span>à revoir</span></div></section>
    <section class="result-section"><h2>Ton bilan par thème</h2><div class="theme-results">${resultThemeCards(result.stats)}</div></section>
    <section class="result-section"><h2>Les questions à revoir</h2>${mistakesMarkup(result)}</section>
    <div class="result-actions"><button class="btn btn-primary" data-action="again">Recommencer ${icon("repeat")}</button>${missed ? `<button class="btn btn-secondary" data-action="review-errors">Revoir mes erreurs ${icon("arrow")}</button>` : ""}<button class="btn btn-secondary" data-action="home">Retour à l’accueil ${icon("home")}</button></div>
  </div>`;
}
function startClock() {
  clearClock();
  clockHandle = setInterval(() => {
    const timer = document.getElementById("timer");
    if (timer) timer.textContent = formatTime(elapsed());
  }, 1000);
}
function clearClock() { if (clockHandle) clearInterval(clockHandle); clockHandle = null; }
function toggleTheme() {
  const current = document.documentElement.dataset.theme || "auto";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("svt3-color-theme", next); } catch {}
}
function applySavedTheme() {
  try {
    const choice = localStorage.getItem("svt3-color-theme");
    if (choice === "light" || choice === "dark") document.documentElement.dataset.theme = choice;
    else document.documentElement.removeAttribute("data-theme");
  } catch { document.documentElement.removeAttribute("data-theme"); }
}
root.addEventListener("click", event => {
  const button = event.target.closest("[data-action]");
  if (!button) return;
  const action = button.dataset.action;
  if (action === "start-theme") startSession("theme", button.dataset.theme);
  if (action === "start-exam") startSession("exam");
  if (action === "start-random") startSession("quick");
  if (action === "resume") resumeSession();
  if (action === "discard-resume") discardResume();
  if (action === "home") { session = null; renderHome(); }
  if (action === "quit-quiz") { saved.resume = null; persist(); session = null; renderHome(); }
  if (action === "select-answer" && session && !session.answers[session.index]) {
    const selected = Number(button.dataset.index);
    const q = session.queue[session.index];
    const multi = q.reponses_correctes.length > 1;
    if (multi) session.selected = session.selected.includes(selected) ? session.selected.filter(n => n !== selected) : [...session.selected, selected];
    else session.selected = [selected];
    root.querySelectorAll('[data-action="select-answer"]').forEach(el => {
      const active = session.selected.includes(Number(el.dataset.index));
      el.classList.toggle("is-selected", active);
      el.setAttribute("aria-pressed", String(active));
    });
    const submit = root.querySelector('[data-action="submit"]');
    if (submit) submit.disabled = !session.selected.length;
  }
  if (action === "submit") finishAnswer();
  if (action === "continue") nextQuestion();
  if (action === "again" && lastCompleted) {
    const previous = lastCompleted;
    if (previous.type === "theme") startSession("theme", previous.themeId);
    else if (previous.type === "review") startSession("review", null, previous.queue.map(q => ({ theme: q.theme, id: q.id, optionOrder: q.optionOrder })));
    else startSession(previous.type);
  }
  if (action === "review-errors" && lastCompleted) {
    const refs = lastCompleted.queue.filter((_, i) => !lastCompleted.answers[i]?.correct).map(q => ({ theme: q.theme, id: q.id }));
    startSession("review", null, refs);
  }
});
document.getElementById("theme-toggle").addEventListener("click", toggleTheme);

async function init() {
  applySavedTheme();
  try {
    const response = await fetch("questions.json", { cache: "no-cache" });
    if (!response.ok) throw new Error("Le fichier de questions n’a pas pu être chargé.");
    bank = await response.json();
    if (bank.total_questions !== 180 || bank.themes.length !== 3 || bank.themes.some(t => t.questions.length !== 60)) throw new Error("La banque de questions est incomplète.");
    renderHome();
    if ("serviceWorker" in navigator && location.protocol.startsWith("http")) navigator.serviceWorker.register("sw.js").catch(() => {});
  } catch (error) {
    root.setAttribute("aria-busy", "false");
    root.innerHTML = `<section class="error-state"><p class="eyebrow">Un petit souci technique</p><h1>Impossible de charger le quiz.</h1><p>${escapeHTML(error.message)} Vérifie que l’application est ouverte depuis un serveur web, puis recharge la page.</p></section>`;
  }
}
init();
