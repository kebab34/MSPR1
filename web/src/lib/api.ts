// Options acceptées par apiFetch : méthode HTTP, token JWT, body JSON, paramètres de requête
type ApiFetchOptions = {
  method?: string;               // méthode HTTP : "GET", "POST", "PUT", "DELETE" (GET par défaut)
  token?: string | null;         // token JWT à envoyer dans le header Authorization
  body?: unknown;                // données à envoyer dans le corps de la requête (JSON)
  params?: Record<string, string>; // paramètres de l'URL (ex: { limit: "100" } → ?limit=100)
};

/**
 * Fonction centrale qui fait toutes les requêtes vers l'API.
 * Passe automatiquement par le proxy Next.js (/api/mspr/...) qui relaie vers FastAPI.
 * Ajoute le token JWT dans chaque requête si fourni.
 * Lance une erreur si la réponse HTTP n'est pas OK (4xx ou 5xx).
 */
export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { method = "GET", token, body, params } = options; // déstructure les options avec valeurs par défaut

  // Construit l'URL complète vers le proxy Next.js
  // window.location.origin = "http://localhost:8000" en production Docker
  const base = typeof window !== "undefined" ? window.location.origin : "http://localhost:3000";
  const url = new URL(`/api/mspr${path}`, base); // ex: /api/mspr/aliments → http://localhost:8000/api/mspr/aliments
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      url.searchParams.set(k, v); // ajoute chaque paramètre dans l'URL : ?limit=100&skip=0
    }
  }

  const headers: Record<string, string> = {}; // headers HTTP de la requête
  if (token) headers["authorization"] = `Bearer ${token}`; // ajoute le token JWT si présent
  if (body !== undefined) headers["content-type"] = "application/json"; // indique que le body est du JSON

  const res = await fetch(url.toString(), {
    method,                                                     // GET, POST, PUT, DELETE...
    headers,                                                    // authorization + content-type
    body: body !== undefined ? JSON.stringify(body) : undefined, // convertit le body en string JSON
  });

  if (!res.ok) {
    // La requête a échoué (4xx ou 5xx) : extrait le message d'erreur de la réponse
    let msg = `Erreur ${res.status}`; // message par défaut avec le code HTTP
    try {
      const err = await res.json();                       // essaie de lire le message d'erreur JSON
      msg = err.detail ?? err.message ?? msg;             // FastAPI retourne "detail", d'autres API retournent "message"
    } catch { /* ignore si la réponse n'est pas du JSON */ }
    throw new Error(msg); // lance une erreur que les composants peuvent attraper
  }

  if (res.status === 204) return undefined as T; // 204 = No Content (ex: après un DELETE) → retourne undefined
  return res.json() as Promise<T>; // parse et retourne la réponse JSON
}
