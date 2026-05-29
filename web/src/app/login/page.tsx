"use client"; // ce composant s'exécute côté navigateur (formulaires, états, navigation)

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";          // pour rediriger après connexion
import { useAuth } from "@/contexts/auth-context";    // pour accéder aux fonctions login/register
import { IconActivity, IconAlertCircle } from "@/components/icons";

export default function LoginPage() {
  const { token, profile, loading, login, register } = useAuth(); // fonctions et état d'auth
  const router = useRouter();
  const [tab, setTab] = useState<"login" | "register">("login"); // onglet actif : connexion ou inscription
  const [err, setErr] = useState<string | null>(null);           // message d'erreur à afficher
  const [pending, setPending] = useState(false);                 // true pendant l'appel API (désactive le bouton)

  // Champs du formulaire
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [prenom, setPrenom] = useState("");
  const [nom, setNom] = useState("");
  const [password2, setPassword2] = useState(""); // confirmation du mot de passe (inscription seulement)

  useEffect(() => {
    // Si l'utilisateur est déjà connecté, redirige vers l'accueil automatiquement
    if (!loading && token && profile) router.replace("/");
  }, [loading, token, profile, router]);

  async function onLogin(e: React.FormEvent) {
    e.preventDefault(); // empêche le rechargement de la page (comportement par défaut du formulaire HTML)
    setErr(null);        // efface l'erreur précédente
    if (!email || !password) { setErr("Email et mot de passe requis."); return; }
    setPending(true); // affiche le spinner sur le bouton
    try {
      await login(email, password); // appelle l'API /auth/login via auth-context
      router.replace("/");           // redirige vers l'accueil après connexion réussie
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : String(ex)); // affiche le message d'erreur
    } finally {
      setPending(false); // cache le spinner dans tous les cas
    }
  }

  async function onRegister(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    if (!email || !password) { setErr("Email et mot de passe requis."); return; }
    if (password !== password2) { setErr("Les mots de passe ne correspondent pas."); return; }
    if (password.length < 6) { setErr("Le mot de passe doit contenir au moins 6 caractères."); return; }
    setPending(true);
    try {
      await register(email, password, prenom, nom); // appelle l'API /auth/register
      router.replace("/");
    } catch (ex) {
      setErr(ex instanceof Error ? ex.message : String(ex));
    } finally {
      setPending(false);
    }
  }

  // Pendant le chargement initial (vérification du localStorage), affiche un spinner centré
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950">
        <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center px-4">
      {/* Fond quadrillé décoratif */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff06_1px,transparent_1px),linear-gradient(to_bottom,#ffffff06_1px,transparent_1px)] bg-[size:64px_64px]" />

      <div className="relative w-full max-w-sm">
        {/* Logo et titre */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-blue-600 mb-4 shadow-lg shadow-blue-500/20">
            <IconActivity size={24} className="text-white" />
          </div>
          <h1 className="text-2xl font-semibold text-white">HealthAI Coach</h1>
          <p className="text-sm text-slate-400 mt-1">Votre espace santé personnalisé</p>
        </div>

        {/* Carte blanche du formulaire */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
          {/* Sélecteur d'onglet : Connexion / Inscription */}
          <div className="flex bg-slate-800 rounded-lg p-1 mb-5">
            {(["login", "register"] as const).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => { setTab(t); setErr(null); }} // change d'onglet et efface l'erreur
                className={`flex-1 py-1.5 text-sm rounded-md font-medium transition-all ${
                  tab === t ? "bg-slate-700 text-white shadow" : "text-slate-400 hover:text-slate-300"
                }`}
              >
                {t === "login" ? "Se connecter" : "S'inscrire"}
              </button>
            ))}
          </div>

          {/* Affiche l'erreur si présente */}
          {err && (
            <div className="flex items-center gap-2 px-3 py-2.5 mb-4 bg-red-500/10 border border-red-500/20 rounded-lg text-sm text-red-400">
              <IconAlertCircle size={14} className="shrink-0" />
              <span>{err}</span>
            </div>
          )}

          {/* Formulaire de connexion */}
          {tab === "login" ? (
            <form onSubmit={onLogin} className="space-y-4">
              <div className="flex flex-col gap-1">
                <label className="text-xs text-slate-400 font-medium">Adresse e-mail</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)} // met à jour l'état à chaque frappe
                  placeholder="vous@exemple.com"
                  required
                  autoComplete="email"
                  className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs text-slate-400 font-medium">Mot de passe</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  autoComplete="current-password"
                  className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button
                type="submit"
                disabled={pending} // désactive le bouton pendant l'appel API
                className="w-full flex items-center justify-center gap-2 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 disabled:cursor-not-allowed text-white font-medium text-sm rounded-lg transition-colors"
              >
                {pending && <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
                {pending ? "Connexion…" : "Se connecter"}
              </button>
            </form>
          ) : (
            // Formulaire d'inscription
            <form onSubmit={onRegister} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <label className="text-xs text-slate-400 font-medium">Prénom</label>
                  <input
                    value={prenom}
                    onChange={(e) => setPrenom(e.target.value)}
                    placeholder="Jean"
                    className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-xs text-slate-400 font-medium">Nom</label>
                  <input
                    value={nom}
                    onChange={(e) => setNom(e.target.value)}
                    placeholder="Dupont"
                    className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs text-slate-400 font-medium">Adresse e-mail</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="vous@exemple.com"
                  required
                  className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs text-slate-400 font-medium">Mot de passe</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min. 6 caractères"
                  required
                  className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-xs text-slate-400 font-medium">Confirmer le mot de passe</label>
                <input
                  type="password"
                  value={password2}
                  onChange={(e) => setPassword2(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button
                type="submit"
                disabled={pending}
                className="w-full flex items-center justify-center gap-2 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 disabled:cursor-not-allowed text-white font-medium text-sm rounded-lg transition-colors"
              >
                {pending && <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />}
                {pending ? "Inscription…" : "Créer mon compte"}
              </button>
            </form>
          )}
        </div>

        <p className="text-center text-xs text-slate-600 mt-6">
          Interface MSPR — Coaching santé personnalisé
        </p>
      </div>
    </div>
  );
}
