"use client"; // ce composant s'exécute côté navigateur (pas sur le serveur)

import { useEffect } from "react";
import { useRouter } from "next/navigation";           // pour naviguer entre les pages
import { useAuth } from "@/contexts/auth-context";     // pour lire le token et l'état de connexion
import { DashboardShell } from "@/components/dashboard-shell"; // structure visuelle (sidebar + contenu)

// Layout partagé par toutes les pages du dashboard (/, /aliments, /exercices, etc.)
// Il vérifie que l'utilisateur est connecté avant d'afficher quoi que ce soit
export default function DashboardGroupLayout({
  children, // le contenu de la page en cours
}: {
  children: React.ReactNode;
}) {
  const { token, profile, loading, authError } = useAuth(); // récupère l'état d'authentification
  const router = useRouter();                               // permet de rediriger vers /login

  useEffect(() => {
    // Quand le chargement est terminé et qu'il n'y a pas de token → redirige vers /login
    if (!loading && !token) {
      router.replace("/login"); // replace() = pas de retour arrière possible
    }
  }, [loading, token, router]); // se redéclenche si token ou loading changent

  // Pendant le chargement initial (vérification du token en localStorage) → affiche un spinner
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-zinc-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm">Chargement…</span>
        </div>
      </div>
    );
  }

  // Si pas de token ou pas de profil chargé → affiche un message de redirection
  if (!token || !profile) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-zinc-950 text-zinc-400 gap-4 px-4">
        {authError && (
          <p className="text-red-400 text-center max-w-lg text-sm">{authError}</p> // affiche l'erreur si présente
        )}
        <p>Redirection vers la connexion…</p>
      </div>
    );
  }

  // Utilisateur connecté → affiche le dashboard avec la sidebar
  return <DashboardShell>{children}</DashboardShell>;
}
