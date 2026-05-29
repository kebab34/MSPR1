"use client"; // s'exécute côté navigateur (états, navigation, interactions)

import Link from "next/link";                          // composant de navigation Next.js (optimisé)
import { usePathname, useRouter } from "next/navigation"; // pathname = URL actuelle, router = navigation
import { useState } from "react";
import { useAuth } from "@/contexts/auth-context";     // pour lire le profil et la fonction logout
import { cn } from "@/lib/utils";                      // utilitaire pour combiner les classes CSS conditionnellement
import {
  IconHome, IconBook, IconTimer, IconActivity, IconDumbbell,
  IconLeaf, IconUsers, IconBarChart, IconUser, IconLogOut, IconMenu, IconX,
  IconSparkles, IconBrain,
} from "@/components/icons";

// Type d'un élément de navigation dans la sidebar
type NavItem = {
  href: string;           // URL de la page
  label: string;          // texte affiché dans le menu
  icon: React.ReactNode;  // icône affichée à gauche du texte
  adminOnly?: boolean;    // si true → visible seulement pour les admins
};

// Liste de tous les liens de navigation
const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Accueil", icon: <IconHome size={16} /> },
  { href: "/journal", label: "Journal alimentaire", icon: <IconBook size={16} /> },
  { href: "/sessions", label: "Sessions sport", icon: <IconTimer size={16} /> },
  { href: "/mesures", label: "Mesures", icon: <IconActivity size={16} /> },
  { href: "/exercices", label: "Exercices", icon: <IconDumbbell size={16} /> },
  { href: "/aliments", label: "Aliments", icon: <IconLeaf size={16} /> },
  { href: "/nutrition-ia", label: "Nutrition IA", icon: <IconSparkles size={16} /> },
  { href: "/recommandations", label: "Recommandations sport", icon: <IconBrain size={16} /> },
  { href: "/utilisateurs", label: "Utilisateurs", icon: <IconUsers size={16} />, adminOnly: true },
  { href: "/analytics", label: "Analytics", icon: <IconBarChart size={16} />, adminOnly: true },
  { href: "/profil", label: "Mon profil", icon: <IconUser size={16} /> },
];

// Composant d'un lien de navigation : actif (bleu) ou inactif (gris)
function NavLink({ item, active, onClick }: { item: NavItem; active: boolean; onClick?: () => void }) {
  return (
    <Link
      href={item.href}
      onClick={onClick} // ferme le menu mobile si fourni
      className={cn(
        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all",
        active
          ? "bg-blue-600/15 text-blue-400 border border-blue-500/20" // style actif : fond bleu translucide
          : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"  // style inactif : gris avec hover
      )}
    >
      <span className={cn("shrink-0", active ? "text-blue-400" : "text-slate-500")}>{item.icon}</span>
      {item.label}
    </Link>
  );
}

// Composant de la barre latérale (sidebar)
function Sidebar({ onClose }: { onClose?: () => void }) {
  const pathname = usePathname();                    // URL actuelle pour savoir quel lien est actif
  const { profile, logout } = useAuth();             // profil de l'utilisateur connecté + fonction logout
  const router = useRouter();
  const isAdmin = profile?.app_role === "admin";     // true si l'utilisateur est admin

  // Filtre les liens : cache ceux adminOnly si l'utilisateur n'est pas admin
  const visibleItems = NAV_ITEMS.filter((i) => !i.adminOnly || isAdmin);

  function handleLogout() {
    logout();               // efface le token du localStorage et réinitialise le contexte
    router.push("/login");  // redirige vers la page de connexion
  }

  // Génère les initiales de l'utilisateur (ex: "Jean Dupont" → "JD") pour l'avatar
  const initials = [profile?.prenom, profile?.nom]
    .filter(Boolean)                        // enlève les valeurs null/undefined
    .map((s) => (s as string)[0])           // prend la première lettre de chaque mot
    .join("")
    .toUpperCase() || profile?.email?.slice(0, 2).toUpperCase() || "?"; // fallback sur email ou "?"

  return (
    <div className="flex flex-col h-full bg-zinc-950 border-r border-slate-800">
      {/* En-tête : logo + bouton fermer (mobile) */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center">
            <IconActivity size={14} className="text-white" />
          </div>
          <span className="text-sm font-semibold text-white tracking-tight">HealthAI Coach</span>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-slate-500 hover:text-white p-1">
            <IconX size={16} /> {/* bouton X pour fermer le menu mobile */}
          </button>
        )}
      </div>

      {/* Liste des liens de navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        {visibleItems.map((item) => (
          <NavLink
            key={item.href}
            item={item}
            active={item.href === "/" ? pathname === "/" : pathname.startsWith(item.href)} // détecte le lien actif
            onClick={onClose} // ferme le menu mobile au clic
          />
        ))}
      </nav>

      {/* Pied de sidebar : avatar utilisateur + bouton déconnexion */}
      <div className="px-3 py-4 border-t border-slate-800 space-y-2">
        <div className="flex items-center gap-3 px-3 py-2">
          {/* Avatar avec initiales */}
          <div className="w-8 h-8 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center shrink-0 text-xs font-semibold text-blue-400">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-slate-200 truncate">
              {[profile?.prenom, profile?.nom].filter(Boolean).join(" ") || "Utilisateur"}
            </p>
            <p className="text-xs text-slate-500 truncate">{profile?.email}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-all"
        >
          <IconLogOut size={14} />
          Déconnexion
        </button>
      </div>
    </div>
  );
}

// Composant principal : structure de toutes les pages du dashboard
export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false); // contrôle l'ouverture du menu mobile

  return (
    <div className="min-h-screen flex bg-zinc-950">
      {/* Sidebar fixe sur desktop (écrans larges) */}
      <aside className="hidden lg:flex lg:w-60 lg:shrink-0 lg:flex-col">
        <div className="fixed top-0 left-0 h-full w-60"> {/* position fixe pour rester visible au scroll */}
          <Sidebar />
        </div>
      </aside>

      {/* Sidebar mobile : overlay plein écran avec fond semi-transparent */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div className="fixed inset-0 bg-black/60" onClick={() => setMobileOpen(false)} /> {/* clic en dehors = ferme */}
          <div className="relative w-64 z-10">
            <Sidebar onClose={() => setMobileOpen(false)} />
          </div>
        </div>
      )}

      {/* Zone de contenu principal */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Barre du haut sur mobile (cachée sur desktop) */}
        <header className="lg:hidden sticky top-0 z-40 flex items-center gap-3 px-4 py-3 bg-zinc-950/90 border-b border-slate-800 backdrop-blur">
          <button
            onClick={() => setMobileOpen(true)} // ouvre le menu mobile
            className="text-slate-400 hover:text-white p-1"
          >
            <IconMenu size={20} /> {/* icône hamburger */}
          </button>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-blue-600 flex items-center justify-center">
              <IconActivity size={12} className="text-white" />
            </div>
            <span className="text-sm font-semibold text-white">HealthAI Coach</span>
          </div>
        </header>

        {/* Contenu de la page (children = /aliments, /exercices, etc.) */}
        <main className="flex-1 px-4 py-6 lg:px-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
