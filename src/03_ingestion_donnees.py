import os
import pandas as pd
import json

# Le chemin ABSOLU du dossier où se trouve ce script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Remonter à la racine du projet (un niveau au-dessus de src/)
root_dir = os.path.dirname(script_dir)

# Construire les chemins vers tes fichiers
csv_path = os.path.join(root_dir, 'data', 'creditcard_pret_ingestion.csv')
json_path = os.path.join(root_dir, 'data', 'correspondances.json')
db_path = os.path.join(root_dir, 'database', 'creditcard.db')
schema_path = os.path.join(root_dir, 'src', 'creation_tables.sql')

import sqlite3
from pathlib import Path


def creer_tables(db_path: str | Path, schema_path: str | Path) -> None:
    """Exécute le fichier DDL (schema.sql) pour créer la structure de la base de données.

    La fonction lit le fichier SQL, s'assure que le dossier de la base existe,
    puis exécute l'ensemble des instructions de création de tables et contraintes
    via la méthode executescript().

    Args:
        db_path (str | Path): Chemin vers le fichier de base de données SQLite (.db).
        schema_path (str | Path): Chemin vers le fichier script SQL (schema.sql).

    Raises:
        FileNotFoundError: Si le fichier schema.sql est introuvable.
        sqlite3.OperationalError: En cas d'erreur de syntaxe dans le script SQL.
    """
    db_path = Path(db_path)
    schema_path = Path(schema_path)
    
    # Créer le dossier parent (ex: database/) s'il n'existe pas encore
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # executescript permet de lancer plusieurs requêtes séparées par des points-virgules
    cursor.executescript(schema_sql)

    conn.commit()
    conn.close()
    print(f"✓ Structure BDD initialisée à partir de '{schema_path.name}'.")
    
    
def peupler_dimensions(db_path: str, json_path: str):
    """Lit les référentiels depuis un fichier JSON et peuple les tables dimensions dans SQLite.

    La fonction parcourt chaque clé du fichier JSON (correspondant au nom d'une
    table dimension SQL) et insère ou met à jour dynamiquement les enregistrements
    associés. Le support des clés étrangères est activé au préalable.

    Args:
        db_path (str | Path): Chemin vers la base de données SQLite (.db).
        json_path (str | Path): Chemin vers le fichier JSON contenant les correspondances.

    Raises:
        FileNotFoundError: Si le fichier JSON est introuvable au chemin indiqué.
        sqlite3.OperationalError: Si la base de données est inaccessible ou vérouillée.
        sqlite3.IntegrityError: En cas de contrainte SQL non respectée lors de l'injection.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Activation des clés étrangère
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Charger le dictionnaire JSON
    with open(json_path, "r", encoding="utf-8") as f:
        mappings = json.load(f)

    # Injecter chaque table dimension
    for table_name, rows in mappings.items():
        if not rows:
            continue

        # Extraction dynamique des colonnes et des paramètres SQL (?)
        columns = list(rows[0].keys())
        col_names = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))

        query = f"INSERT OR REPLACE INTO {table_name} ({col_names}) VALUES ({placeholders})"

        # Conversion des dictionnaires en tuples de valeurs
        values = [tuple(row[col] for col in columns) for row in rows]

        cursor.executemany(query, values)
        print(
            f"✓ Table dimension '{table_name}' : {len(values)} lignes insérées."
        )
    print("Peuplement des tables de dimension terminé")

    conn.commit()
    conn.close()
    

def ingerer_dataset_csv(db_path: Path, csv_path: Path) -> None:
    """Lit le CSV nettoyé et peuple les tables client et historique_mensuel."""
    df = pd.read_csv(csv_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    client_data = []
    historique_mensuel_data = []

    # Mapping mois CSV (1 à 6) -> date_id (YYYYMM)
    month_mapping = [
        (1, 200509),  # Septembre 2005
        (2, 200508),  # Août 2005
        (3, 200507),  # Juillet 2005
        (4, 200506),  # Juin 2005
        (5, 200505),  # Mai 2005
        (6, 200504),  # Avril 2005
    ]

    for _, row in df.iterrows():
        client_id = int(row["ID"])

        # 1. Extraction Client
        client_data.append(
            (
                client_id,
                int(row["AGE"]),
                int(row["SEX"]),
                int(row["MARRIAGE"]),
                int(row["EDUCATION"]),
                int(row["LIMIT_BAL"]),
                int(row["dpnm"]),
            )
        )

        # 2. Dépliage de l'historique sur 6 mois
        for m_idx, date_id in month_mapping:
            historique_mensuel_data.append(
                (
                    client_id,
                    date_id,
                    int(row[f"BILL_AMT{m_idx}"]),
                    int(row[f"PAY_AMT{m_idx}"]),
                    int(row[f"PAY_{m_idx}"]),
                )
            )

    # Insertion dans la table client
    query_client = """
        INSERT INTO client (client_id, age, code_genre, code_marital, code_scolaire, plafond, code_statut_defaut)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.executemany(query_client, client_data)

    # Insertion dans la table historique_mensuel
    query_historique_mensuel = """
        INSERT INTO historique_mensuel (client_id, date_id, montant_encours, montant_paye, code_statut_paiement)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.executemany(query_historique_mensuel, historique_mensuel_data)

    conn.commit()
    conn.close()

    print(f"✓ Table 'client' : {len(client_data)} clients insérés.")
    print(
        f"✓ Table 'historique_mensuel' : {len(historique_mensuel_data)} lignes insérées."
    )
    
# On enchaine les 3 fonctions créées qui forment le pipeline
creer_tables(db_path = db_path, schema_path = schema_path)
peupler_dimensions(json_path = json_path, db_path = db_path)
ingerer_dataset_csv(db_path=db_path, csv_path=csv_path)