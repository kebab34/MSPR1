import { apiFetch } from "./api"; // importe la fonction centrale de requête API

// Type représentant un utilisateur simplifié pour les listes déroulantes (pickers)
export type PickUser = {
  id_utilisateur: string; // UUID de l'utilisateur en base
  email: string;          // email (toujours présent)
  prenom?: string;        // prénom (optionnel)
  nom?: string;           // nom (optionnel)
  app_role?: string;      // rôle : "user" ou "admin"
};

/**
 * Retourne le nom affiché d'un utilisateur dans une liste déroulante.
 * Si l'utilisateur a un prénom et/ou nom → affiche "Jean Dupont"
 * Sinon → affiche l'email
 */
export function labelUser(u: PickUser): string {
  const name = [u.prenom, u.nom].filter(Boolean).join(" "); // joint prénom + nom en ignorant les valeurs vides
  return name || u.email; // retourne le nom complet ou l'email si pas de nom
}

/**
 * Récupère la liste des utilisateurs disponibles pour un sélecteur (select/dropdown).
 * - Si l'utilisateur est admin → retourne tous les utilisateurs (pour voir les données de tout le monde)
 * - Si l'utilisateur est simple user → retourne uniquement lui-même (peut seulement voir ses propres données)
 */
export async function fetchUsersForPicker(
  token: string,
  profile: { id_utilisateur: string; email: string; prenom?: string; nom?: string; app_role?: string } | null,
): Promise<PickUser[]> {
  if (!profile) return []; // pas de profil chargé → retourne une liste vide

  if (profile.app_role === "admin") {
    // Admin : récupère tous les utilisateurs depuis l'API
    const data = await apiFetch<PickUser[]>("/utilisateurs", { token, params: { limit: "1000" } });
    return Array.isArray(data) ? data : [];
  }

  // Utilisateur normal : retourne uniquement son propre profil
  return [{
    id_utilisateur: profile.id_utilisateur,
    email: profile.email,
    prenom: profile.prenom,
    nom: profile.nom,
    app_role: profile.app_role,
  }];
}
