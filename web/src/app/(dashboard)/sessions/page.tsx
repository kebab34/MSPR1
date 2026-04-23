"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/auth-context";
import { apiFetch } from "@/lib/api";
import { fetchUsersForPicker, labelUser, type PickUser } from "@/lib/picker-users";
import { PageHeader, Btn, Card, Input, Select, Alert, SkeletonTable, EmptyState, Badge } from "@/components/ui";
import { IconTimer, IconPlus, IconAlertCircle, IconCheck, IconCalendar, IconZap } from "@/components/icons";

type Session = {
  id_session: string;
  id_utilisateur: string;
  duree?: number;
  intensite?: string;
  date_session?: string;
  created_at: string;
};

const INTENSITE_BADGE: Record<string, "emerald" | "amber" | "red"> = {
  faible: "emerald", moderee: "amber", elevee: "red",
};

function fmt(iso?: string) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });
}

export default function SessionsPage() {
  const { token, profile } = useAuth();
  const [users, setUsers] = useState<PickUser[]>([]);
  const [userId, setUserId] = useState("");
  const [rows, setRows] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  const [dateDebut, setDateDebut] = useState(() => {
    const d = new Date(); d.setDate(d.getDate() - 30); return d.toISOString().slice(0, 10);
  });
  const [dateFin, setDateFin] = useState(() => new Date().toISOString().slice(0, 10));
  const [dateSession, setDateSession] = useState(() => new Date().toISOString().slice(0, 10));
  const [duree, setDuree] = useState("45");
  const [intensite, setIntensite] = useState<"faible" | "moderee" | "elevee">("moderee");

  useEffect(() => {
    if (!token || !profile) return;
    fetchUsersForPicker(token, profile).then(setUsers).catch(() => {});
  }, [token, profile]);

  useEffect(() => {
    if (users.length && !userId) setUserId(users[0].id_utilisateur);
  }, [users, userId]);

  useEffect(() => {
    if (!token || !userId) return;
    let cancelled = false;
    setLoading(true);
    apiFetch<Session[]>("/sessions", { token, params: { utilisateur_id: userId, date_debut: dateDebut, date_fin: dateFin } })
      .then((d) => { if (!cancelled) { setRows(Array.isArray(d) ? d : []); setLoading(false); } })
      .catch((e) => { if (!cancelled) { setErr(String(e)); setLoading(false); } });
    return () => { cancelled = true; };
  }, [token, userId, dateDebut, dateFin]);

  async function onAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!token || !userId) return;
    setErr(null); setMsg(null); setSaving(true);
    try {
      const d = parseInt(duree, 10);
      if (!d || d < 1) throw new Error("Durée invalide");
      await apiFetch("/sessions", {
        method: "POST", token,
        body: { id_utilisateur: userId, duree: d, intensite, date_session: new Date(dateSession).toISOString() },
      });
      setMsg("Session enregistrée.");
      setShowForm(false);
      const data = await apiFetch<Session[]>("/sessions", { token, params: { utilisateur_id: userId, date_debut: dateDebut, date_fin: dateFin } });
      setRows(Array.isArray(data) ? data : []);
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : String(ex));
    } finally {
      setSaving(false);
    }
  }

  const totalMin = rows.reduce((s, r) => s + (r.duree ?? 0), 0);
  const totalH = Math.floor(totalMin / 60);
  const restMin = totalMin % 60;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Sessions sport"
        subtitle="Historique de vos séances d'entraînement"
        action={
          <Btn size="sm" onClick={() => setShowForm(!showForm)}>
            <IconPlus size={14} /> Nouvelle session
          </Btn>
        }
      />

      {msg && <Alert variant="success"><IconCheck size={14} /><span>{msg}</span></Alert>}
      {err && <Alert variant="error"><IconAlertCircle size={14} /><span>{err}</span></Alert>}

      {/* Add form */}
      {showForm && (
        <Card>
          <h2 className="text-sm font-semibold text-white mb-4">Nouvelle session</h2>
          <form onSubmit={onAdd} className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Input label="Date" type="date" value={dateSession} onChange={(e) => setDateSession(e.target.value)} />
            <Input label="Durée (min)" type="number" min={1} value={duree} onChange={(e) => setDuree(e.target.value)} />
            <Select label="Intensité" value={intensite} onChange={(e) => setIntensite(e.target.value as typeof intensite)}>
              <option value="faible">Faible</option>
              <option value="moderee">Modérée</option>
              <option value="elevee">Élevée</option>
            </Select>
            {users.length > 1 && (
              <Select label="Utilisateur" value={userId} onChange={(e) => setUserId(e.target.value)}>
                {users.map((u) => <option key={u.id_utilisateur} value={u.id_utilisateur}>{labelUser(u)}</option>)}
              </Select>
            )}
            <div className="col-span-2 sm:col-span-4 flex gap-2">
              <Btn type="submit" loading={saving} size="sm">Enregistrer</Btn>
              <Btn type="button" variant="ghost" size="sm" onClick={() => setShowForm(false)}>Annuler</Btn>
            </div>
          </form>
        </Card>
      )}

      {/* Filters + stats */}
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
        {rows.length > 0 && (
          <div className="ml-auto flex items-center gap-4 text-sm">
            <span className="text-slate-400"><span className="text-white font-semibold">{rows.length}</span> session{rows.length > 1 ? "s" : ""}</span>
            <span className="text-slate-400">Total : <span className="text-white font-semibold">{totalH > 0 ? `${totalH}h ` : ""}{restMin}min</span></span>
          </div>
        )}
      </div>

      {/* Table */}
      {loading ? <SkeletonTable rows={5} cols={4} /> : rows.length === 0 ? (
        <EmptyState message="Aucune session sur cette période." action={<Btn size="sm" onClick={() => setShowForm(true)}><IconPlus size={14} /> Ajouter</Btn>} />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-800/50 border-b border-slate-800">
                {["Date", "Durée", "Intensité", "Enregistrée le"].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((s) => (
                <tr key={s.id_session} className="border-b border-slate-800/60 hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                        <IconTimer size={13} className="text-blue-400" />
                      </div>
                      <span className="text-slate-200">{fmt(s.date_session)}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {s.duree != null ? (
                      <span className="font-semibold text-white">{s.duree} <span className="font-normal text-slate-400 text-xs">min</span></span>
                    ) : <span className="text-slate-600">—</span>}
                  </td>
                  <td className="px-4 py-3">
                    {s.intensite ? (
                      <span className="flex items-center gap-1.5">
                        <IconZap size={12} className={s.intensite === "elevee" ? "text-red-400" : s.intensite === "moderee" ? "text-amber-400" : "text-emerald-400"} />
                        <Badge variant={INTENSITE_BADGE[s.intensite] ?? "slate"}>{s.intensite}</Badge>
                      </span>
                    ) : <span className="text-slate-600">—</span>}
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">{fmt(s.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
