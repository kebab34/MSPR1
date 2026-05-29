"""
ETL - Load Module
Load data into Supabase
"""
import os                                    # pour lire les variables d'environnement
from supabase import create_client, Client  # client officiel Supabase pour Python
import pandas as pd                          # pour manipuler les DataFrames
import logging                               # pour écrire des messages de log
from typing import List, Dict, Any           # pour typer les arguments des fonctions

logging.basicConfig(level=logging.INFO)  # configure le niveau de log minimum
logger = logging.getLogger(__name__)     # crée un logger avec le nom du fichier courant


class SupabaseLoader:
    """Classe qui gère toutes les opérations d'écriture vers Supabase."""

    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")  # lit l'URL Supabase depuis le .env
        # Préfère la clé de service (accès total) sinon utilise la clé publique
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY (or SUPABASE_KEY) must be set")

        self.client: Client = create_client(supabase_url, supabase_key)  # crée la connexion à Supabase
        logger.info("Supabase client initialized (using service key for write operations)")

    def load_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = "append") -> bool:
        """
        Insère un DataFrame dans une table Supabase par lots de 1000 lignes.
        Utilisé pour les tables sans contrainte d'unicité (insert simple).
        """
        try:
            records = df.to_dict('records')  # convertit le DataFrame en liste de dictionnaires Python

            if if_exists == "replace":
                # Option "replace" : supprimer d'abord les données existantes (non implémenté ici)
                pass

            batch_size = 1000  # nombre de lignes envoyées en une seule requête
            for i in range(0, len(records), batch_size):  # boucle sur les lots
                batch = records[i:i + batch_size]          # extrait un lot de 1000 lignes
                self.client.table(table_name).insert(batch).execute()  # insère le lot dans Supabase
                logger.info(f"Inserted batch {i//batch_size + 1} into {table_name}")

            logger.info(f"Successfully loaded {len(records)} records into {table_name}")
            return True  # succès

        except Exception as e:
            logger.error(f"Error loading data into {table_name}: {str(e)}")
            return False  # échec

    def upsert_dataframe(self, df: pd.DataFrame, table_name: str, on_conflict: str = "id") -> bool:
        """
        Upsert un DataFrame dans une table Supabase par lots de 100 lignes.
        Upsert = si la ligne existe déjà (selon on_conflict), on la met à jour, sinon on l'insère.
        on_conflict = colonne utilisée pour détecter les doublons (ex: "email", "nom").
        """
        try:
            # Convertit le DataFrame en liste de dicts, remplace les NaN par None (JSON ne supporte pas NaN)
            records = df.where(pd.notna(df), None).to_dict('records')

            batch_size = 100  # lots plus petits pour Supabase (limite de l'API)
            total_batches = (len(records) + batch_size - 1) // batch_size  # nombre total de lots

            for i in range(0, len(records), batch_size):  # boucle sur les lots
                batch = records[i:i + batch_size]          # extrait un lot
                try:
                    # Envoie le lot en upsert : Supabase gère lui-même insert vs update
                    response = self.client.table(table_name).upsert(batch, on_conflict=on_conflict).execute()
                    logger.info(f"Upserted batch {i//batch_size + 1}/{total_batches} into {table_name} ({len(batch)} records)")
                except Exception as batch_error:
                    logger.warning(f"Error in batch {i//batch_size + 1}: {str(batch_error)}")
                    # Si un lot entier échoue, on essaie ligne par ligne pour sauver ce qu'on peut
                    for record in batch:
                        try:
                            self.client.table(table_name).upsert([record], on_conflict=on_conflict).execute()
                        except Exception as record_error:
                            logger.warning(f"Skipped record in {table_name}: {record_error}")  # on passe à la suivante

            logger.info(f"Successfully upserted {len(records)} records into {table_name}")
            return True

        except Exception as e:
            logger.error(f"Error upserting data into {table_name}: {str(e)}")
            return False

    def delete_records(self, table_name: str, filters: Dict[str, Any]) -> bool:
        """
        Supprime des lignes dans une table Supabase selon des filtres.
        filters est un dictionnaire ex: {"email": "test@test.com"} → supprime toutes les lignes avec cet email.
        """
        try:
            query = self.client.table(table_name).delete()  # prépare une requête de suppression

            for key, value in filters.items():  # applique chaque filtre un par un
                query = query.eq(key, value)    # .eq = "égal à" (WHERE key = value en SQL)

            query.execute()  # envoie la requête à Supabase
            logger.info(f"Deleted records from {table_name} with filters {filters}")
            return True

        except Exception as e:
            logger.error(f"Error deleting records from {table_name}: {str(e)}")
            return False
