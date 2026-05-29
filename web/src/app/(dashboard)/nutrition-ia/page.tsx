"use client";

import { useState, useRef, useCallback } from "react";
import { useAuth } from "@/contexts/auth-context";
import {
  IconCamera, IconUpload, IconSparkles, IconLeaf, IconAlertCircle, IconCheck,
} from "@/components/icons";
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  RadialBarChart, RadialBar,
} from "recharts";

// ── Types ──────────────────────────────────────────────────────────────────────

type AlimentDetecte = {
  nom: string;
  quantite_estimee: string;
  calories: number;
  proteines: number;
  glucides: number;
  lipides: number;
  fibres: number;
};

type AnalyseResult = {
  aliments_detectes: AlimentDetecte[];
  total_calories: number;
  total_proteines: number;
  total_glucides: number;
  total_lipides: number;
  total_fibres: number;
  desequilibres_detectes: string[];
  suggestions_amelioration: string[];
  score_nutritionnel: number;
  message_global: string;
};

type RepasJour = {
  petit_dejeuner: string;
  dejeuner: string;
  diner: string;
  collations: string | null;
  calories_estimees: number;
  proteines_estimees: number;
  glucides_estimees: number;
  lipides_estimees: number;
};

type PlanRepasResult = {
  plan: Record<string, RepasJour>;
  calories_moyennes_par_jour: number;
  conseils_generaux: string[];
  liste_courses: string[];
  message_personnalise: string;
};

// ── Constantes ────────────────────────────────────────────────────────────────

const OBJECTIFS = [
  { value: "equilibre_nutritionnel", label: "Équilibre nutritionnel" },
  { value: "perte_de_poids", label: "Perte de poids" },
  { value: "prise_de_masse", label: "Prise de masse" },
  { value: "performance_sportive", label: "Performance sportive" },
  { value: "maintien", label: "Maintien" },
];

const MACRO_COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444"];

// ── Score visuel ──────────────────────────────────────────────────────────────

function ScoreGauge({ score }: { score: number }) {
  const color =
    score >= 75 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";
  const data = [
    { name: "score", value: score, fill: color },
    { name: "reste", value: 100 - score, fill: "#1e293b" },
  ];
  return (
    <div className="flex flex-col items-center gap-1">
      <ResponsiveContainer width={120} height={120}>
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius="60%"
          outerRadius="90%"
          startAngle={180}
          endAngle={-180}
          data={data}
        >
          <RadialBar dataKey="value" cornerRadius={6} />
        </RadialBarChart>
      </ResponsiveContainer>
      <span style={{ color }} className="text-2xl font-bold -mt-12 relative z-10">
        {score}
      </span>
      <span className="text-xs text-slate-400 mt-8">/ 100</span>
      <span className="text-xs text-slate-400">Score nutritionnel</span>
    </div>
  );
}

// ── Macros pie chart ──────────────────────────────────────────────────────────

function MacroPie({ proteines, glucides, lipides, fibres }: {
  proteines: number; glucides: number; lipides: number; fibres: number;
}) {
  const data = [
    { name: "Protéines", value: Math.round(proteines) },
    { name: "Glucides", value: Math.round(glucides) },
    { name: "Lipides", value: Math.round(lipides) },
    { name: "Fibres", value: Math.round(fibres) },
  ].filter((d) => d.value > 0);

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          outerRadius={70}
          dataKey="value"
          label={({ name, value }) => `${name} ${value}g`}
          labelLine={false}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={MACRO_COLORS[i % MACRO_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip formatter={(v: number) => [`${v}g`]} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

// ── Page principale ───────────────────────────────────────────────────────────

export default function NutritionIAPage() {
  const { token } = useAuth();
  const fileRef = useRef<HTMLInputElement>(null);

  // Tab actif
  const [tab, setTab] = useState<"analyse" | "plan">("analyse");

  // Analyse photo
  const [photo, setPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [objectif, setObjectif] = useState("equilibre_nutritionnel");
  const [allergies, setAllergies] = useState("");
  const [notes, setNotes] = useState("");
  const [analyseLoading, setAnalyseLoading] = useState(false);
  const [analyseError, setAnalyseError] = useState<string | null>(null);
  const [analyseResult, setAnalyseResult] = useState<AnalyseResult | null>(null);

  // Plan repas
  const [planObjectif, setPlanObjectif] = useState("equilibre_nutritionnel");
  const [planAllergies, setPlanAllergies] = useState("");
  const [planRegime, setPlanRegime] = useState("");
  const [planCalories, setPlanCalories] = useState("");
  const [planBudget, setPlanBudget] = useState("");
  const [planJours, setPlanJours] = useState("7");
  const [planLoading, setPlanLoading] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);
  const [planResult, setPlanResult] = useState<PlanRepasResult | null>(null);

  // Drag & drop
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      setPhoto(file);
      setPhotoPreview(URL.createObjectURL(file));
      setAnalyseResult(null);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhoto(file);
      setPhotoPreview(URL.createObjectURL(file));
      setAnalyseResult(null);
    }
  };

  // Analyse photo
  const handleAnalyse = async () => {
    if (!photo) return;
    setAnalyseLoading(true);
    setAnalyseError(null);
    setAnalyseResult(null);

    const form = new FormData();
    form.append("photo", photo);
    form.append("objectif", objectif);
    form.append("allergies", allergies);
    if (notes) form.append("notes_utilisateur", notes);

    try {
      const res = await fetch("/api/mspr/ai/nutrition/analyze-photo", {
        method: "POST",
        headers: { authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Erreur ${res.status}`);
      }
      setAnalyseResult(await res.json());
    } catch (e: unknown) {
      setAnalyseError(e instanceof Error ? e.message : "Erreur inconnue");
    } finally {
      setAnalyseLoading(false);
    }
  };

  // Plan repas
  const handlePlan = async () => {
    setPlanLoading(true);
    setPlanError(null);
    setPlanResult(null);

    const body: Record<string, unknown> = {
      objectif: planObjectif,
      nb_jours: parseInt(planJours, 10),
      allergies: planAllergies.split(",").map((s) => s.trim()).filter(Boolean),
    };
    if (planRegime) body.regime = planRegime;
    if (planCalories) body.calories_cibles = parseFloat(planCalories);
    if (planBudget) body.budget_quotidien = parseFloat(planBudget);

    try {
      const res = await fetch("/api/mspr/ai/nutrition/meal-plan", {
        method: "POST",
        headers: {
          authorization: `Bearer ${token}`,
          "content-type": "application/json",
        },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Erreur ${res.status}`);
      }
      setPlanResult(await res.json());
    } catch (e: unknown) {
      setPlanError(e instanceof Error ? e.message : "Erreur inconnue");
    } finally {
      setPlanLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center">
          <IconSparkles size={20} className="text-emerald-400" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-white">Nutrition IA</h1>
          <p className="text-sm text-slate-400">
            Analysez vos repas et générez des plans nutritionnels personnalisés
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-800/50 rounded-lg p-1 w-fit">
        {(["analyse", "plan"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              tab === t
                ? "bg-slate-700 text-white"
                : "text-slate-400 hover:text-slate-200"
            }`}
            aria-selected={tab === t}
            role="tab"
          >
            {t === "analyse" ? "Analyser une photo" : "Générer un plan repas"}
          </button>
        ))}
      </div>

      {/* ── TAB : Analyse photo ─────────────────────────────── */}
      {tab === "analyse" && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Colonne gauche : formulaire */}
          <div className="space-y-4">
            {/* Zone drag & drop */}
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileRef.current?.click()}
              className="border-2 border-dashed border-slate-700 rounded-xl p-6 flex flex-col items-center gap-3 cursor-pointer hover:border-emerald-500/50 hover:bg-emerald-500/5 transition-all"
              role="button"
              aria-label="Zone de dépôt de photo de repas"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && fileRef.current?.click()}
            >
              {photoPreview ? (
                <img
                  src={photoPreview}
                  alt="Aperçu du repas"
                  className="max-h-48 rounded-lg object-cover"
                />
              ) : (
                <>
                  <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center">
                    <IconCamera size={24} className="text-slate-500" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm text-slate-300 font-medium">
                      Glissez une photo ou cliquez pour sélectionner
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      JPEG, PNG, WebP — max 5 Mo
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-emerald-400">
                    <IconUpload size={12} />
                    Choisir un fichier
                  </div>
                </>
              )}
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={handleFileChange}
              aria-label="Sélectionner une photo de repas"
            />

            {/* Objectif */}
            <div className="space-y-1.5">
              <label htmlFor="objectif-analyse" className="text-sm text-slate-300 font-medium">
                Objectif santé
              </label>
              <select
                id="objectif-analyse"
                value={objectif}
                onChange={(e) => setObjectif(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
              >
                {OBJECTIFS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Allergies */}
            <div className="space-y-1.5">
              <label htmlFor="allergies-analyse" className="text-sm text-slate-300 font-medium">
                Allergies / intolérances{" "}
                <span className="text-slate-500 font-normal">(séparées par des virgules)</span>
              </label>
              <input
                id="allergies-analyse"
                type="text"
                value={allergies}
                onChange={(e) => setAllergies(e.target.value)}
                placeholder="gluten, lactose, noix…"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>

            {/* Notes */}
            <div className="space-y-1.5">
              <label htmlFor="notes-analyse" className="text-sm text-slate-300 font-medium">
                Notes supplémentaires{" "}
                <span className="text-slate-500 font-normal">(optionnel)</span>
              </label>
              <textarea
                id="notes-analyse"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                placeholder="Ex : portion pour 2, repas de midi…"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 resize-none focus:outline-none focus:border-emerald-500"
              />
            </div>

            <button
              onClick={handleAnalyse}
              disabled={!photo || analyseLoading}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2.5 rounded-lg transition-colors"
              aria-busy={analyseLoading}
            >
              {analyseLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyse en cours…
                </>
              ) : (
                <>
                  <IconSparkles size={16} />
                  Analyser le repas
                </>
              )}
            </button>

            {analyseError && (
              <div
                role="alert"
                className="flex items-start gap-2 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2 text-sm text-red-400"
              >
                <IconAlertCircle size={16} className="shrink-0 mt-0.5" />
                {analyseError}
              </div>
            )}
          </div>

          {/* Colonne droite : résultats */}
          {analyseResult && (
            <div className="space-y-4">
              {/* Score + message */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 flex gap-4 items-center">
                <ScoreGauge score={analyseResult.score_nutritionnel} />
                <p className="text-sm text-slate-300 flex-1 leading-relaxed">
                  {analyseResult.message_global}
                </p>
              </div>

              {/* Totaux */}
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: "Calories", value: `${Math.round(analyseResult.total_calories)} kcal`, color: "text-orange-400" },
                  { label: "Protéines", value: `${Math.round(analyseResult.total_proteines)}g`, color: "text-blue-400" },
                  { label: "Glucides", value: `${Math.round(analyseResult.total_glucides)}g`, color: "text-green-400" },
                  { label: "Lipides", value: `${Math.round(analyseResult.total_lipides)}g`, color: "text-yellow-400" },
                ].map((m) => (
                  <div key={m.label} className="bg-slate-800/50 border border-slate-700 rounded-lg p-3">
                    <p className="text-xs text-slate-400">{m.label}</p>
                    <p className={`text-lg font-semibold ${m.color}`}>{m.value}</p>
                  </div>
                ))}
              </div>

              {/* Pie chart macros */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <h3 className="text-sm font-medium text-slate-300 mb-2">
                  Répartition des macronutriments
                </h3>
                <MacroPie
                  proteines={analyseResult.total_proteines}
                  glucides={analyseResult.total_glucides}
                  lipides={analyseResult.total_lipides}
                  fibres={analyseResult.total_fibres}
                />
              </div>

              {/* Aliments détectés */}
              {analyseResult.aliments_detectes.length > 0 && (
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                  <h3 className="text-sm font-medium text-slate-300 mb-3">
                    Aliments détectés
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs" aria-label="Tableau des aliments détectés">
                      <thead>
                        <tr className="text-slate-400 border-b border-slate-700">
                          <th className="text-left py-1.5 pr-3">Aliment</th>
                          <th className="text-right py-1.5 pr-3">Quantité</th>
                          <th className="text-right py-1.5">Kcal</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analyseResult.aliments_detectes.map((a, i) => (
                          <tr key={i} className="border-b border-slate-800 last:border-0">
                            <td className="py-1.5 pr-3 text-slate-200">{a.nom}</td>
                            <td className="text-right py-1.5 pr-3 text-slate-400">{a.quantite_estimee}</td>
                            <td className="text-right py-1.5 text-orange-400">{Math.round(a.calories)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Suggestions */}
              {analyseResult.suggestions_amelioration.length > 0 && (
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                  <h3 className="text-sm font-medium text-slate-300 mb-3">
                    Suggestions d'amélioration
                  </h3>
                  <ul className="space-y-2">
                    {analyseResult.suggestions_amelioration.map((s, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                        <IconCheck size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Déséquilibres */}
              {analyseResult.desequilibres_detectes.length > 0 && (
                <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4">
                  <h3 className="text-sm font-medium text-amber-400 mb-2">
                    Déséquilibres détectés
                  </h3>
                  <ul className="space-y-1">
                    {analyseResult.desequilibres_detectes.map((d, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-amber-300">
                        <IconAlertCircle size={14} className="shrink-0 mt-0.5" />
                        {d}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* État vide */}
          {!analyseResult && !analyseLoading && (
            <div className="hidden lg:flex flex-col items-center justify-center gap-3 border border-dashed border-slate-700 rounded-xl p-8 text-center">
              <IconLeaf size={32} className="text-slate-600" />
              <p className="text-sm text-slate-500">
                Les résultats de l'analyse apparaîtront ici
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── TAB : Plan repas ───────────────────────────────── */}
      {tab === "plan" && (
        <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
          {/* Formulaire */}
          <div className="space-y-4">
            <div className="space-y-1.5">
              <label htmlFor="plan-objectif" className="text-sm text-slate-300 font-medium">
                Objectif
              </label>
              <select
                id="plan-objectif"
                value={planObjectif}
                onChange={(e) => setPlanObjectif(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
              >
                {OBJECTIFS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label htmlFor="plan-calories" className="text-sm text-slate-300 font-medium">
                  Calories/jour
                </label>
                <input
                  id="plan-calories"
                  type="number"
                  value={planCalories}
                  onChange={(e) => setPlanCalories(e.target.value)}
                  placeholder="2000"
                  min={800}
                  max={5000}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div className="space-y-1.5">
                <label htmlFor="plan-budget" className="text-sm text-slate-300 font-medium">
                  Budget (€/jour)
                </label>
                <input
                  id="plan-budget"
                  type="number"
                  value={planBudget}
                  onChange={(e) => setPlanBudget(e.target.value)}
                  placeholder="15"
                  min={0}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="plan-jours" className="text-sm text-slate-300 font-medium">
                Nombre de jours
              </label>
              <select
                id="plan-jours"
                value={planJours}
                onChange={(e) => setPlanJours(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
              >
                {[1, 3, 5, 7, 10, 14].map((n) => (
                  <option key={n} value={n}>{n} jour{n > 1 ? "s" : ""}</option>
                ))}
              </select>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="plan-regime" className="text-sm text-slate-300 font-medium">
                Régime alimentaire <span className="text-slate-500 font-normal">(optionnel)</span>
              </label>
              <input
                id="plan-regime"
                type="text"
                value={planRegime}
                onChange={(e) => setPlanRegime(e.target.value)}
                placeholder="végétarien, vegan, sans gluten…"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="plan-allergies" className="text-sm text-slate-300 font-medium">
                Allergies <span className="text-slate-500 font-normal">(séparées par des virgules)</span>
              </label>
              <input
                id="plan-allergies"
                type="text"
                value={planAllergies}
                onChange={(e) => setPlanAllergies(e.target.value)}
                placeholder="noix, lait, œufs…"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>

            <button
              onClick={handlePlan}
              disabled={planLoading}
              className="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2.5 rounded-lg transition-colors"
              aria-busy={planLoading}
            >
              {planLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Génération en cours…
                </>
              ) : (
                <>
                  <IconSparkles size={16} />
                  Générer le plan
                </>
              )}
            </button>

            {planError && (
              <div
                role="alert"
                className="flex items-start gap-2 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2 text-sm text-red-400"
              >
                <IconAlertCircle size={16} className="shrink-0 mt-0.5" />
                {planError}
              </div>
            )}
          </div>

          {/* Résultats plan */}
          {planResult ? (
            <div className="space-y-4">
              {/* Message personnalisé */}
              <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4">
                <p className="text-sm text-emerald-300">{planResult.message_personnalise}</p>
                <p className="text-xs text-slate-400 mt-1">
                  Moyenne : {Math.round(planResult.calories_moyennes_par_jour)} kcal/jour
                </p>
              </div>

              {/* Jours */}
              <div className="space-y-3">
                {Object.entries(planResult.plan).map(([jour, repas]) => (
                  <div
                    key={jour}
                    className="bg-slate-800/50 border border-slate-700 rounded-xl p-4"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-semibold text-white capitalize">{jour}</h3>
                      <span className="text-xs text-orange-400">
                        {Math.round(repas.calories_estimees)} kcal
                      </span>
                    </div>
                    <div className="grid gap-2 text-sm">
                      <p>
                        <span className="text-slate-400">Petit-déjeuner : </span>
                        <span className="text-slate-200">{repas.petit_dejeuner}</span>
                      </p>
                      <p>
                        <span className="text-slate-400">Déjeuner : </span>
                        <span className="text-slate-200">{repas.dejeuner}</span>
                      </p>
                      <p>
                        <span className="text-slate-400">Dîner : </span>
                        <span className="text-slate-200">{repas.diner}</span>
                      </p>
                      {repas.collations && (
                        <p>
                          <span className="text-slate-400">Collations : </span>
                          <span className="text-slate-200">{repas.collations}</span>
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Conseils + liste courses */}
              <div className="grid gap-4 md:grid-cols-2">
                {planResult.conseils_generaux.length > 0 && (
                  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                    <h3 className="text-sm font-medium text-slate-300 mb-2">Conseils</h3>
                    <ul className="space-y-1.5">
                      {planResult.conseils_generaux.map((c, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                          <IconCheck size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                          {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {planResult.liste_courses.length > 0 && (
                  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                    <h3 className="text-sm font-medium text-slate-300 mb-2">Liste de courses</h3>
                    <ul className="space-y-1">
                      {planResult.liste_courses.map((item, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
                          <span className="w-1 h-1 rounded-full bg-emerald-400 shrink-0" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ) : (
            !planLoading && (
              <div className="hidden lg:flex flex-col items-center justify-center gap-3 border border-dashed border-slate-700 rounded-xl p-8 text-center">
                <IconLeaf size={32} className="text-slate-600" />
                <p className="text-sm text-slate-500">Votre plan de repas apparaîtra ici</p>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}
