"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/auth-context";
import { apiFetch } from "@/lib/api";
import { fetchUsersForPicker, labelUser, type PickUser } from "@/lib/picker-users";
import { PageHeader, Btn, Card, Input, Select, Alert, SkeletonTable, EmptyState, Badge } from "@/components/ui";
import { IconPlus, IconAlertCircle, IconCheck, IconCalendar, IconLeaf, IconFlame } from "@/components/icons";

type Row = {
  id_journal: string;
  id_utilisateur: string;
  id_aliment: string;
  quantite: number;
  date_consommation?: string;
  aliment?: { nom: string; calories: number; proteines: number; glucides: number; lipides: number; unite: string };
};

type Aliment = { id_aliment: string; nom: string; calories: number; proteines: number; glucides: number; lipides: number; unite: string };

function fmt(iso?: string) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });
}

export default function JournalPage() {
  const { token, profile } = useAuth();
  const [users, setUsers] = useState<PickUser[]>([]);
  const [aliments, setAliments] = useState<Aliment[]>([]);
  const [userId, setUserId] = useState("");
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  const today = new Date().toISOString().slice(0, 10);
  const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10);
  const [dateDebut, setDateDebut] = useState(weekAgo);
  const [dateFin, setDateFin] = useState(today);
  const [dateEntree, setDateEntree] = useState(today);
  const [alimentId, setAlimentId] = useState("");
  const [quantite, setQuantite] = useState("100");

  useEffect(() => {
    if (!token || !profile) return;
    Promise.all([
      fetchUsersForPicker(token, profile),
      apiFetch<Aliment[]>("/aliments", { token }),
    ]).then(([u, a]) => {
      setUsers(u);
      setAliments(Array.isArray(a) ? a : []);
    }).catch(() => {});
  }, [token, profile]);

  useEffect(() => { if (users.length && !userId) setUserId(users[0].id_utilisateur); }, [users, userId]);
  useEffect(() => { if (aliments.length && !alimentId) setAlimentId(aliments[0].id_aliment); }, [aliments, alimentId]);

  useEffect(() => {
    if (!token || !userId) return;
    let cancelled = false;
    setLoading(true);
    apiFetch<Row[]>("/journal", { token, params: { utilisateur_id: userId, date_debut: dateDebut, date_fin: dateFin } })
      .then((d) => { if (!cancelled) { setRows(Array.isArray(d) ? d : []); setLoading(false); } })
      .catch((e) => { if (!cancelled) { setErr(String(e)); setLoading(false); } });
    return () => { cancelled = true; };
  }, [token, userId, dateDebut, dateFin]);

  async function onAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!token || !userId || !alimentId) return;
    setErr(null); setMsg(null); setSaving(true);
    try {
      const q = parseFloat(quantite);
      if (!q || q <= 0) throw new Error("Quantité invalide");
      await apiFetch("/journal", {
        method: "POST", token,
        body: { id_utilisateur: userId, id_aliment: alimentId, quantite: q, date_consommation: new Date(dateEntree).toISOString() },
      });
      setMsg("Entrée ajoutée au journal.");
      setShowForm(false);
      const data = await apiFetch<Row[]>("/journal", { token, params: { utilisateur_id: userId, date_debut: dateDebut, date_fin: dateFin } });
      setRows(Array.isArray(data) ? data : []);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : String(ex));
    } finally {
      setSaving(false);
    }
  }

  const aliMap = Object.fromEntries(aliments.map((a) => [a.id_aliment, a]));

  // Daily nutrition totals
  const todayRows = rows.filter((r) => r.date_consommation?.startsWith(today));
  const todayCal = todayRows.reduce((s, r) => {
    const a = aliMap[r.id_aliment];
    return s + (a ? (a.calories * r.quantite) / 100 : 0);
  }, 0);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Journal alimentaire"
        subtitle="Suivez vos apports nutritionnels quotidiens"
        action={
          <Btn size="sm" onClick={() => setShowForm(!showForm)}>
            <IconPlus size={14} /> Ajouter
          </Btn>
        }
      />

      {msg && <Alert variant="success"><IconCheck size={14} /><span>{msg}</span></Alert>}
      {err && <Alert variant="error"><IconAlertCircle size={14} /><span>{err}</span></Alert>}

      {/* Today's summary */}
      {todayCal > 0 && (
        <Card className="border-amber-500/20 bg-amber-500/5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 shrink-0"><IconFlame size={18} /></div>
            <div>
              <p className="text-xs text-slate-400">Calories aujourd'hui</p>
              <p className="text-xl font-semibold text-white">{Math.round(todayCal)} <span className="text-sm font-normal text-slate-400">kcal</span></p>
            </div>
          </div>
        </Card>
      )}

      {/* Add form */}
      {showForm && aliments.length > 0 && (
        <Card>
          <h2 className="text-sm font-semibold text-white mb-4">Nouvelle entrée</h2>
          <form onSubmit={onAdd} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Input label="Date" type="date" value={dateEntree} onChange={(e) => setDateEntree(e.target.value)} />
            <Select label="Aliment" value={alimentId} onChange={(e) => setAlimentId(e.target.value)}>
              {aliments.map((a) => <option key={a.id_aliment} value={a.id_aliment}>{a.nom}</option>)}
            </Select>
            <Input label="Quantité (g)" type="number" step="1" min="1" value={quantite} onChange={(e) => setQuantite(e.target.value)} />
            <div className="sm:col-span-3 flex gap-2">
              <Btn type="submit" loading={saving} size="sm">Enregistrer</Btn>
              <Btn type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}>Annuler</Btn>
            </div>
          </form>
        </Card>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-end gap-3">
        <div className="flex items-center gap-2">
          <IconCalendar size={14} className="text-slate-500" />
          <Input type="date" value={dateDebut} onChange={(e) => setDateDebut(e.target.value)} className="w-36" />
        </div>
        <span className="text-slate-500 text-sm">→</span>
        <Input type="date" value={dateFin} onChange={(e) => setDateFin(e.target.value)} className="w-36" />
        {users.length > 1 && (
          <Select value={userId} onChange={(e) => setUserId(e.target.value)} className="w-48">
            {users.map((u) => <option key={u.id_utilisateur} value={u.id_utilisateur}>{labelUser(u)}</option>)}
          </Select>
        )}
      </div>

      {/* Table */}
      {loading ? <SkeletonTable rows={5} cols={5} /> : rows.length === 0 ? (
        <EmptyState message="Aucune entrée sur cette période." action={<Btn size="sm" onClick={() => setShowForm(true)}><IconPlus size={14} /> Ajouter</Btn>} />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-800/50 border-b border-slate-800">
                {["Date", "Aliment", "Quantité", "Calories", "Protéines / Glucides / Lipides"].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase tracking-wide whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => {
                const a = aliMap[r.id_aliment];
                const ratio = r.quantite / 100;
                const cal = a ? Math.round(a.calories * ratio) : null;
                const prot = a ? (a.proteines * ratio).toFixed(1) : null;
                const gluc = a ? (a.glucides * ratio).toFixed(1) : null;
                const lip = a ? (a.lipides * ratio).toFixed(1) : null;
                return (
                  <tr key={r.id_journal} className="border-b border-slate-800/60 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 text-slate-300 whitespace-nowrap">{fmt(r.date_consommation)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-md bg-emerald-500/10 flex items-center justify-center shrink-0">
                          <IconLeaf size={11} className="text-emerald-400" />
                        </div>
                        <span className="text-slate-200">{a?.nom ?? <span className="text-slate-500 font-mono text-xs">{r.id_aliment.slice(0, 8)}…</span>}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-300">{r.quantite} g</td>
                    <td className="px-4 py-3">
                      {cal != null ? (
                        <span className="font-semibold text-amber-400">{cal} <span className="font-normal text-slate-500 text-xs">kcal</span></span>
                      ) : <span className="text-slate-600">—</span>}
                    </td>
                    <td className="px-4 py-3">
                      {prot && gluc && lip ? (
                        <div className="flex items-center gap-2 text-xs">
                          <Badge variant="blue">{prot}g P</Badge>
                          <Badge variant="amber">{gluc}g G</Badge>
                          <Badge variant="red">{lip}g L</Badge>
                        </div>
                      ) : <span className="text-slate-600">—</span>}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
