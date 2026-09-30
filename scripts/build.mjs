import { readFile, rm, mkdir, cp, copyFile, access } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const out = path.join(root, "dist");
const bank = JSON.parse(await readFile(path.join(root, "questions.json"), "utf8"));
if (bank.total_questions !== 180 || bank.themes.length !== 3) throw new Error("La banque doit contenir trois thèmes et 180 questions.");
for (const theme of bank.themes) {
  if (theme.questions.length !== 60) throw new Error(`${theme.id}: ${theme.questions.length} questions au lieu de 60.`);
  for (const q of theme.questions) {
    if (!q.question || !q.explication || !Array.isArray(q.options) || q.options.length < 2) throw new Error(`Question incomplète: ${theme.id} #${q.id}`);
    if (!q.reponses_correctes?.length || q.reponses_correctes.some(i => !Number.isInteger(i) || i < 0 || i >= q.options.length)) throw new Error(`Réponse invalide: ${theme.id} #${q.id}`);
    if (q.illustration) await access(path.join(root, q.illustration.src));
  }
}
await rm(out, { recursive: true, force: true });
await mkdir(out, { recursive: true });
for (const file of ["index.html", "style.css", "script.js", "questions.json", "manifest.webmanifest", "sw.js"]) {
  await copyFile(path.join(root, file), path.join(out, file));
}
await cp(path.join(root, "assets"), path.join(out, "assets"), { recursive: true });
console.log(`Build réussi : ${bank.total_questions} questions, ${bank.themes.length} thèmes → dist/`);
