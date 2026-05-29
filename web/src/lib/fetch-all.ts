import { apiFetch } from "./api"; // importe la fonction centrale de requête API

/**
 * Récupère TOUS les éléments d'un endpoint sans limite de pagination.
 * Utilisé pour les pages Analytics qui ont besoin de compter tous les enregistrements.
 * Exemple : fetchAll("/utilisateurs", token) → retourne tous les utilisateurs en base
 */
export async function fetchAll<T>(path: string, token: string): Promise<T[]> {
  const data = await apiFetch<T[]>(path, { token, params: { limit: "10000" } }); // demande jusqu'à 10 000 résultats
  return Array.isArray(data) ? data : []; // sécurité : retourne un tableau vide si la réponse n'est pas un tableau
}
