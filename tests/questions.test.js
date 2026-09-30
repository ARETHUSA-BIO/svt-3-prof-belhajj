import test from "node:test";
import assert from "node:assert/strict";
import { readFile, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const bank = JSON.parse(await readFile(path.join(root, "questions.json"), "utf8"));

test("la banque contient trois thèmes et 180 questions", () => {
  assert.equal(bank.themes.length, 3);
  assert.equal(bank.total_questions, 180);
  assert.equal(bank.themes.reduce((n, theme) => n + theme.questions.length, 0), 180);
  for (const theme of bank.themes) assert.equal(theme.questions.length, 60, theme.id);
});

test("chaque question possède des choix, une correction et une explication", () => {
  for (const theme of bank.themes) for (const q of theme.questions) {
    assert.ok(q.question.trim(), `${theme.id} #${q.id}: question`);
    assert.ok(q.explication.trim(), `${theme.id} #${q.id}: explication`);
    assert.ok(Array.isArray(q.options) && q.options.length >= 2, `${theme.id} #${q.id}: options`);
    assert.ok(q.reponses_correctes.length > 0, `${theme.id} #${q.id}: réponse`);
    for (const index of q.reponses_correctes) assert.ok(Number.isInteger(index) && index >= 0 && index < q.options.length, `${theme.id} #${q.id}: index ${index}`);
    assert.ok(["qcm", "vrai-faux"].includes(q.type));
    assert.ok(["fourni", "complément"].includes(q.origine));
  }
});

test("les compléments reflètent le manque de contenu dans la pièce jointe", () => {
  const counts = Object.fromEntries(bank.themes.map(t => [t.id, t.questions.filter(q => q.origine === "complément").length]));
  assert.deepEqual(counts, { nutrition: 0, genetics: 12, earth: 60 });
  assert.equal(bank.themes.flatMap(t => t.questions).filter(q => q.note_pedagogique).length >= 4, true);
});

test("toutes les illustrations mentionnées existent dans le projet", async () => {
  for (const theme of bank.themes) for (const q of theme.questions) if (q.illustration) await access(path.join(root, q.illustration.src));
});

test("l’application ne charge ni scripts distants ni traceurs", async () => {
  const html = await readFile(path.join(root, "index.html"), "utf8");
  const js = await readFile(path.join(root, "script.js"), "utf8");
  assert.doesNotMatch(html, /<script[^>]+src=["']https?:/i);
  assert.doesNotMatch(js, /google-analytics|googletagmanager|facebook\.net|segment\.io/i);
});
