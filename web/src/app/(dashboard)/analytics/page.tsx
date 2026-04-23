"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/auth-context";
import { fetchAll } from "@/lib/fetch-all";
import { PageHeader, Card, SkeletonTable } from "@/components/ui";
import {
  IconShield, IconUsers, IconLeaf, IconDumbbell,
  IconActivity, IconBook, IconTimer, IconBarChart,
} from "@/components/icons";

type Counts = {
  utilisateurs: number;
  aliments: number;
  exercices: number;
  mesures: number;
  journal: number;
  sessions: number;
};

const METRICS = [
  { key: "utilisateurs" as keyof Counts, label: "Utilisateurs", icon: <IconUsers size={18} />, color: "text-blue-400", bg: "bg-blue-500/10" },
  { key: "aliments" as keyof Counts, label: "Aliments", icon: <IconLeaf size={18} />, color: "text-emerald-400", bg: "bg-emerald-500/10" },
  { key: "exercices" as keyof Counts, label: "Exercices", icon: <IconDumbbell size={18} />, color: "text-cyan-400", bg: "bg-cyan-500/10" },
  { key: "mesures" as keyof Counts, label: "Mesures biométriques", icon: <IconActivity size={18} />, color: "text-purple-400", bg: "bg-purple-500/10" },
  { key: "journal" as keyof Counts, label: "Entrées journal", icon: <IconBook size={18} />, color: "text-amber-400", bg: "bg-amber-500/10" },
  { key: "sessions" as keyof Counts, label: "Sessions sport", icon: <IconTimer size={18} />, color: "text-red-400", bg: "bg-red-500/10" },
];

function BarChart({ counts }: { counts: Counts }) {
  const max = Math.max(...METRICS.map((m) => counts[m.key]), 1);
  return (
    <Card>
      <div className="flex items-center gap-2 mb-5">
        <IconBarChart size={16} className="text-slate-400" />
        <h2 className="text-sm font-semibold text-white">Distribution des données</h2>
      </div>
      <div className="space-y-3">
        {METRICS.map((m) => {
          const val = counts[m.key];
          const pct = Math.max(2, (val / max) * 100);
          return (
            <div key={m.key} className="flex items-center gap-3">
              <div className={`${m.bg} ${m.color} p-1.5 rounded-md shrink-0`}>{m.icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs text-slate-400">{m.label}</span>
                  <span className="text-xs font-semibold text-white">{val.toLocaleString("fr-FR")}</span>
                </div>
                <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${m.bg.replace("/10", "/60")}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

export default function AnalyticsPage() {
  const { token, profile } = useAuth();
  const [counts, setCounts] = useState<Counts | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token || profile?.app_role !== "admin") return;
    let cancelled = false;
    (async () => {
      try {
        const [u, a, e, m, j, s] = await Promise.all([
          fetchAll<unknown>("/utilisateurs", token),
          fetchAll<unknown>("/aliments", token),
          fetchAll<unknown>("/exercices", token),
          fetchAll<unknown>("/mesures", token),
          fetchAll<unknown>("/journal", token),
          fetchAll<unknown>("/sessions", token),
        ]);
        if (!cancelled) {
          setCounts({ utilisateurs: u.length, aliments: a.length, exercices: e.length, mesures: m.length, journal: j.length, sessions: s.length });
          setLoading(false);
        }
      } catch (e) {
        if (!cancelled) { setErr(e instanceof Error ? e.message : String(e)); setLoading(false); }
      }
    })();
    return () => { cancelled = true; };
  }, [token, profile?.app_role]);

  if (profile?.app_role !== "admin") {
    return (
      <div className="flex items-center justify-center py-20 text-slate-400">
        <div className="text-center">
          <IconShield size={32} className="mx-auto mb-3 text-slate-600" />
          <p className="font-medium text-white">Accès restreint</p>
          <p className="text-sm mt-1">Cette page est réservée aux administrateurs.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Analytics"
        subtitle="Vue d'ensemble des données de la plateforme"
      />

      {err && <p className="text-sm text-red-400">{err}</p>}

      {loading ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl p-5 animate-pulse">
                <div className="h-3 w-24 bg-slate-800 rounded mb-3" />
                <div className="h-7 w-16 bg-slate-800 rounded" />
              </div>
            ))}
          </div>
          <SkeletonTable rows={6} cols={2} />
        </div>
      ) : counts && (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {METRICS.map((m) => (
              <Card key={m.key}>
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">{m.label}</p>
                    <p className="mt-2 text-2xl font-semibold text-white">
                      {counts[m.key].toLocaleString("fr-FR")}
                    </p>
                  </div>
                  <div className={`p-2.5 rounded-lg ${m.bg} ${m.color}`}>{m.icon}</div>
                </div>
              </Card>
            ))}
          </div>

          {/* Bar chart */}
          <BarChart counts={counts} />

          {/* Derived stats */}
          {counts.utilisateurs > 0 && (
            <Card>
              <h2 className="text-sm font-semibold text-white mb-4">Moyennes par utilisateur</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  { label: "Mesures / user", value: (counts.mesures / counts.utilisateurs).toFixed(1) },
                  { label: "Entrées journal / user", value: (counts.journal / counts.utilisateurs).toFixed(1) },
                  { label: "Sessions / user", value: (counts.sessions / counts.utilisateurs).toFixed(1) },
                  { label: "Exercices / user", value: (counts.exercices / counts.utilisateurs).toFixed(1) },
                ].map((s) => (
                  <div key={s.label} className="bg-slate-800/50 rounded-lg p-3">
                    <p className="text-xs text-slate-500">{s.label}</p>
                    <p className="mt-1 text-lg font-semibold text-white">{s.value}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
