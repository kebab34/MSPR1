import type { Metadata } from "next";                      // type pour les métadonnées de la page (titre, description)
import { Inter, Roboto_Mono } from "next/font/google";      // polices Google chargées via Next.js (optimisé)
import { AuthProvider } from "@/contexts/auth-context";      // contexte d'authentification qui englobe toute l'app
import "./globals.css";                                       // styles CSS globaux (tailwind, variables...)

// Charge la police Inter (texte principal) et l'enregistre comme variable CSS
const inter = Inter({
  variable: "--font-inter",   // nom de la variable CSS qui contiendra cette police
  subsets: ["latin"],         // charge uniquement les caractères latins (plus léger)
});

// Charge la police Roboto Mono (texte monospace, pour le code)
const robotoMono = Roboto_Mono({
  variable: "--font-roboto-mono",
  subsets: ["latin"],
});

// Métadonnées de la page : titre affiché dans l'onglet du navigateur et description pour le SEO
export const metadata: Metadata = {
  title: "HealthAI Coach",
  description: "Interface web MSPR — coaching santé personnalisé",
};

// Layout racine : englobe TOUTES les pages de l'application
// children = le contenu de la page en cours (login, dashboard, etc.)
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode; // n'importe quel composant React
}>) {
  return (
    <html lang="fr" className="bg-zinc-950"> {/* langue française, fond noir sur tout le site */}
      <body className={`${inter.variable} ${robotoMono.variable} font-sans antialiased`}>
        {/* AuthProvider donne accès au token et au profil dans toutes les pages via useAuth() */}
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
