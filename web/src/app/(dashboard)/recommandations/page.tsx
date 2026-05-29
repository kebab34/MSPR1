"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/auth-context";
import {
  IconBrain, IconSparkles, IconDumbbell, IconAlertCircle, IconCheck,
  IconActivity, IconTimer,
} from "@/components/icons";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

// ── Types ──────────────────────────────────────────────────────────────────────

type Exercice = {
  nom: string;
  type: string;
  series: number | null;
  repetitions: string | null;
  duree_secondes: number | null;
  repos_secondes: number;
  intensite: string;
  instructions: string;
  muscles_cibles: string[];
  adaptation_limitations: string | null;
};

type Seance = {
  titre: string;
  duree_estimee_min: number;
  echauffement: string[];
  exercices_principaux: Exercice[];
  retour_au_calme: string[];
  calories_estimees: number | null;
  niveau_difficulte: string;
};

type ProgrammeSemaine = {
  lundi?: Seance | null;
  mardi?: Seance | null;
  mercredi?: Seance | null;
  jeudi?: Seance | null;
  vendredi?: Seance | null;
  samedi?: Seance | null;
  dimanche?: Seance | null;
};

type WorkoutResult = {
  id: string;
  utilisateur_id: string;
  objectif: string;
  programme_semaine: ProgrammeSemaine;
  conseils_progression: string[];
  conseils_recuperation: string[];
  objectifs_semaine: string[];
  message_motivant: string;
  created_at: string;
};

// ── Constantes ────────────────────────────────────────────────────────────────

const OBJECTIFS = [
  { value: "perte_de_graisse", label: "Perte de graisse" },
  { value: "renforcement_musculaire", label: "Renforcement musculaire" },
  { value: "endurance", label: "Endurance" },
  { value: "sante_generale", label: "Santé générale" },
  { value: "souplesse", label: "Souplesse" },
];

const NIVEAUX = [
  { value: "debutant", label: "Débutant" },
  { value: "intermediaire", label: "Intermédiaire" },
  { value: "avance", label: "Avancé" },
];

const INTENSITE_COLORS: Record<string, string> = {
  faible: "#22c55e",
  modérée: "#f59e0b",
  élevée: "#ef4444",
};

const JOURS_ORDER = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"];

// ── Composant : carte d'un exercice ──────────────────────────────────────────

function ExerciceCard({ ex }: { ex: Exercice }) {
  const [open, setOpen] = useState(false);
  const dotColor = INTENSITE_COLORS[ex.intensite] || "#94a3b8";

  return (
    <div className="border border-slate-700 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3 py-2.5 bg-slate-800/60 hover:bg-slate-800 transition-colors text-left"
        aria-expanded={open}
      >
        <div className="flex items-center gap-2.5">
          <span
            className="w-2 h-2 rounded-full shrink-0"
            style={{ backgroundColor: dotColor }}
            aria-label={`Intensité ${ex.intensite}`}
          />
          <span className="text-sm text-white font-medium">{ex.nom}</span>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-400">
          {ex.series && ex.repetitions && (
            <span>{ex.series} × {ex.repetitions}</span>
          )}
          {ex.duree_secondes && (
            <span>{ex.duree_secondes}s</span>
          )}
          <span className={`transition-transform ${open ? "rotate-180" : ""}`}>▾</span>
        </div>
      </button>
      {open && (
        <div className="px-3 pb-3 pt-2 space-y-2 bg-slate-900/50">
          <p className="text-sm text-slate-300">{ex.instructions}</p>
          {ex.muscles_cibles.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {ex.muscles_cibles.map((m, i) => (
                <span key={i} className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full">
                  {m}
                </span>
              ))}
            </div>
          )}
          {ex.adaptation_limitations && (
            <p className="text-xs text-amber-400">
              ⚠ {ex.adaptation_limitations}
            </p>
          )}
          <p className="text-xs text-slate-500">
            Repos : {ex.repos_secondes}s
          </p>
        </div>
      )}
    </div>
  );
}

// ── Composant : carte d'une séance ───────────────────────────────────────────

function SeanceCard({ jour, seance }: { jour: string; seance: Seance }) {
  const [open, setOpen] = useState(false);
  const diffColor =
    seance.niveau_difficulte === "facile"
      ? "text-green-400"
      : seance.niveau_difficulte === "difficile"
      ? "text-red-400"
      : "text-yellow-400";

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-800/80 transition-colors text-left"
        aria-expanded={open}
      >
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-blue-400 uppercase tracking-wide">
              {jour}
            </span>
            <span className={`text-xs ${diffColor}`}>
              · {seance.niveau_difficulte}
            </span>
          </div>
          <p className="text-sm font-medium text-white mt-0.5">{seance.titre}</p>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-400 shrink-0">
          <span className="flex items-center gap-1">
            <IconTimer size={12} />
            {seance.duree_estimee_min} min
          </span>
          {seance.calories_estimees && (
            <span className="text-orange-400">{seance.calories_estimees} kcal</span>
          )}
          <span className={`transition-transform ${open ? "rotate-180" : ""}`}>▾</span>
        </div>
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-3 border-t border-slate-700">
          {/* Échauffement */}
          {seance.echauffement.length > 0 && (
            <div className="pt-3">
              <p className="text-xs font-semibold text-slate-400 uppercase mb-2">Échauffement</p>
              <ul className="space-y-1">
                {seance.echauffement.map((e, i) => (
                  <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                    <span className="text-blue-400 shrink-0">•</span>
                    {e}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Exercices */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase mb-2">
              Exercices ({seance.exercices_principaux.length})
            </p>
            <div className="space-y-2">
              {seance.exercices_principaux.map((ex, i) => (
                <ExerciceCard key={i} ex={ex} />
              ))}
            </div>
          </div>

          {/* Retour au calme */}
          {seance.retour_au_calme.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase mb-2">Retour au calme</p>
              <ul className="space-y-1">
                {seance.retour_au_calme.map((e, i) => (
                  <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                    <span className="text-emerald-400 shrink-0">•</span>
                    {e}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Page principale ───────────────────────────────────────────────────────────

export default function RecommandationsPage() {
  const { token, profile } = useAuth();

  // Form state
  const [objectif, setObjectif] = useState("sante_generale");
  const [niveau, setNiveau] = useState("debutant");
  const [equipements, setEquipements] = useState("");
  const [activites, setActivites] = useState("");
  const [duree, setDuree] = useState("45");
  const [joursParSemaine, setJoursParSemaine] = useState("3");
  const [limitations, setLimitations] = useState("");

  // Résultats
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<WorkoutResult | null>(null);

  // Feedback
  const [feedbackNote, setFeedbackNote] = useState(0);
  const [feedbackLoading, setFeedbackLoading] = useState(false);
  const [feedbackDone, setFeedbackDone] = useState(false);

  const handleGenerer = async () => {
    if (!profile?.id_utilisateur) {
      setError("Utilisateur non identifié. Reconnectez-vous.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setFeedbackDone(false);

    const body = {
      utilisateur_id: profile.id_utilisateur,
      objectif,
      niveau,
      equipements_disponibles: equipements.split(",").map((s) => s.trim()).filter(Boolean),
      activites_preferees: activites.split(",").map((s) => s.trim()).filter(Boolean),
      duree_seance_min: parseInt(duree, 10),
      jours_par_semaine: parseInt(joursParSemaine, 10),
      limitations_physiques: limitations.split(",").map((s) => s.trim()).filter(Boolean),
      poids: profile.poids ?? undefined,
      age: profile.age ?? undefined,
    };

    try {
      const res = await fetch("/api/reco/recommendations/generate", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Erreur ${res.status}`);
      }
      setResult(await res.json());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async () => {
    if (!result || feedbackNote === 0) return;
    setFeedbackLoading(true);
    try {
      await fetch("/api/reco/recommendations/feedback", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          recommendation_id: result.id,
          utilisateur_id: result.utilisateur_id,
          note: feedbackNote,
        }),
      });
      setFeedbackDone(true);
    } finally {
      setFeedbackLoading(false);
    }
  };

  // Données pour le graphe de charge hebdomadaire
  const chargeData = JOURS_ORDER.map((jour) => {
    const seance = result?.programme_semaine[jour as keyof ProgrammeSemaine];
    return {
      jour: jour.slice(0, 3),
      duree: seance ? seance.duree_estimee_min : 0,
      actif: !!seance,
    };
  });

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
          <IconBrain size={20} className="text-blue-400" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-white">Recommandations sport</h1>
          <p className="text-sm text-slate-400">
            Programme d'entraînement personnalisé généré par IA
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
        {/* ── Formulaire ─────────────────────────────────── */}
        <div className="space-y-4">
          <div className="space-y-1.5">
            <label htmlFor="objectif" className="text-sm text-slate-300 font-medium">
              Objectif
            </label>
            <select
              id="objectif"
              value={objectif}
              onChange={(e) => setObjectif(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            >
              {OBJECTIFS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label htmlFor="niveau" className="text-sm text-slate-300 font-medium">
              Niveau de forme
            </label>
            <div className="grid grid-cols-3 gap-2" role="radiogroup" aria-label="Niveau de forme">
              {NIVEAUX.map((n) => (
                <button
                  key={n.value}
                  onClick={() => setNiveau(n.value)}
                  role="radio"
                  aria-checked={niveau === n.value}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all border ${
                    niveau === n.value
                      ? "bg-blue-600/20 border-blue-500/50 text-blue-300"
                      : "border-slate-700 text-slate-400 hover:text-slate-200 hover:border-slate-600"
                  }`}
                >
                  {n.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label htmlFor="duree" className="text-sm text-slate-300 font-medium">
                Durée (min)
              </label>
              <select
                id="duree"
                value={duree}
                onChange={(e) => setDuree(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                {[15, 20, 30, 45, 60, 90].map((d) => (
                  <option key={d} value={d}>{d} min</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label htmlFor="jours" className="text-sm text-slate-300 font-medium">
                Séances/semaine
              </label>
              <select
                id="jours"
                value={joursParSemaine}
                onChange={(e) => setJoursParSemaine(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                {[1, 2, 3, 4, 5, 6, 7].map((j) => (
                  <option key={j} value={j}>{j}×</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-1.5">
            <label htmlFor="equipements" className="text-sm text-slate-300 font-medium">
              Équipements disponibles{" "}
              <span className="text-slate-500 font-normal">(séparés par des virgules)</span>
            </label>
            <input
              id="equipements"
              type="text"
              value={equipements}
              onChange={(e) => setEquipements(e.target.value)}
              placeholder="haltères, tapis, barre de traction…"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="activites" className="text-sm text-slate-300 font-medium">
              Activités préférées{" "}
              <span className="text-slate-500 font-normal">(optionnel)</span>
            </label>
            <input
              id="activites"
              type="text"
              value={activites}
              onChange={(e) => setActivites(e.target.value)}
              placeholder="course, natation, yoga…"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="space-y-1.5">
            <label htmlFor="limitations" className="text-sm text-slate-300 font-medium">
              Limitations physiques{" "}
              <span className="text-slate-500 font-normal">(optionnel)</span>
            </label>
            <input
              id="limitations"
              type="text"
              value={limitations}
              onChange={(e) => setLimitations(e.target.value)}
              placeholder="douleur genou, dos fragile…"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <button
            onClick={handleGenerer}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-2.5 rounded-lg transition-colors"
            aria-busy={loading}
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Génération en cours…
              </>
            ) : (
              <>
                <IconSparkles size={16} />
                Générer mon programme
              </>
            )}
          </button>

          {error && (
            <div
              role="alert"
              className="flex items-start gap-2 bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2 text-sm text-red-400"
            >
              <IconAlertCircle size={16} className="shrink-0 mt-0.5" />
              {error}
            </div>
          )}
        </div>

        {/* ── Résultats ──────────────────────────────────── */}
        {result ? (
          <div className="space-y-4">
            {/* Message motivant */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
              <p className="text-sm text-blue-200">{result.message_motivant}</p>
            </div>

            {/* Objectifs semaine */}
            {result.objectifs_semaine.length > 0 && (
              <div className="grid gap-2 sm:grid-cols-3">
                {result.objectifs_semaine.map((obj, i) => (
                  <div key={i} className="bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2.5 flex items-start gap-2">
                    <IconActivity size={14} className="text-blue-400 shrink-0 mt-0.5" />
                    <p className="text-xs text-slate-300">{obj}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Graphe charge hebdomadaire */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
              <h3 className="text-sm font-medium text-slate-300 mb-3">
                Charge hebdomadaire (minutes)
              </h3>
              <ResponsiveContainer width="100%" height={120}>
                <BarChart data={chargeData} barSize={28}>
                  <XAxis dataKey="jour" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
                  <YAxis hide />
                  <Tooltip
                    formatter={(v: number) => [`${v} min`, "Durée"]}
                    contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                    labelStyle={{ color: "#94a3b8" }}
                    itemStyle={{ color: "#e2e8f0" }}
                  />
                  <Bar dataKey="duree" radius={[4, 4, 0, 0]}>
                    {chargeData.map((d, i) => (
                      <Cell key={i} fill={d.actif ? "#3b82f6" : "#1e293b"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Programme semaine */}
            <div className="space-y-3">
              {JOURS_ORDER.map((jour) => {
                const seance = result.programme_semaine[jour as keyof ProgrammeSemaine];
                if (!seance) {
                  return (
                    <div key={jour} className="bg-slate-900/50 border border-slate-800 rounded-xl px-4 py-3 flex items-center gap-2">
                      <span className="text-xs font-semibold text-slate-600 uppercase tracking-wide w-20">
                        {jour}
                      </span>
                      <span className="text-sm text-slate-600">Repos</span>
                    </div>
                  );
                }
                return <SeanceCard key={jour} jour={jour} seance={seance} />;
              })}
            </div>

            {/* Conseils */}
            <div className="grid gap-4 md:grid-cols-2">
              {result.conseils_progression.length > 0 && (
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                  <h3 className="text-sm font-medium text-slate-300 mb-2">Conseils de progression</h3>
                  <ul className="space-y-1.5">
                    {result.conseils_progression.map((c, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                        <IconCheck size={14} className="text-blue-400 shrink-0 mt-0.5" />
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {result.conseils_recuperation.length > 0 && (
                <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                  <h3 className="text-sm font-medium text-slate-300 mb-2">Récupération</h3>
                  <ul className="space-y-1.5">
                    {result.conseils_recuperation.map((c, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                        <IconCheck size={14} className="text-emerald-400 shrink-0 mt-0.5" />
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Feedback */}
            {!feedbackDone ? (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <h3 className="text-sm font-medium text-slate-300 mb-3">
                  Ce programme vous convient-il ?
                </h3>
                <div className="flex items-center gap-2 mb-3">
                  {[1, 2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      onClick={() => setFeedbackNote(n)}
                      className={`w-9 h-9 rounded-lg text-sm font-semibold transition-all ${
                        feedbackNote >= n
                          ? "bg-blue-600 text-white"
                          : "bg-slate-700 text-slate-400 hover:bg-slate-600"
                      }`}
                      aria-label={`Note ${n} sur 5`}
                    >
                      {n}
                    </button>
                  ))}
                  <span className="text-xs text-slate-500 ml-1">/ 5</span>
                </div>
                <button
                  onClick={handleFeedback}
                  disabled={feedbackNote === 0 || feedbackLoading}
                  className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm px-4 py-1.5 rounded-lg transition-colors"
                >
                  {feedbackLoading ? "Envoi…" : "Envoyer le feedback"}
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-emerald-400">
                <IconCheck size={16} />
                Feedback envoyé, merci !
              </div>
            )}
          </div>
        ) : (
          !loading && (
            <div className="hidden lg:flex flex-col items-center justify-center gap-3 border border-dashed border-slate-700 rounded-xl p-8 text-center">
              <IconDumbbell size={32} className="text-slate-600" />
              <p className="text-sm text-slate-500">
                Votre programme d'entraînement personnalisé apparaîtra ici
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
}
