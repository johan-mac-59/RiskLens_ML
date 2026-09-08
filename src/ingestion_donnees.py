import os
import pandas as pd
import json

# Le chemin ABSOLU du dossier où se trouve ce script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Remonter à la racine du projet (un niveau au-dessus de src/)
root_dir = os.path.dirname(script_dir)

# Construire les chemins vers tes fichiers
csv_path = os.path.join(root_dir, 'data', 'cleaned_creditcard.csv')
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

    conn.commit()
    conn.close()
    
    
creer_tables(db_path = db_path, schema_path = schema_path)
peupler_dimensions(json_path = json_path, db_path = db_path)



df = pd.read_csv(csv_path)