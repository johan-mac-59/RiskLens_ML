from fastapi import FastAPI, HTTPException
from typing import Optional
import sqlite3
import sys
import os

# Le chemin ABSOLU du dossier où se trouve ce script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Remonter à la racine du projet (un niveau au-dessus de src/)
root_dir = os.path.dirname(script_dir)

# Chemin vers la BDD
DB_PATH = os.path.join(root_dir, 'database', 'creditcard.db')

app = FastAPI(title="Mon API Risklens")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Pour récupérer les résultats sous forme de dictionnaires
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# 2. Route GET : Récupérer toutes les tables (CRUD: Read)
@app.get("/tables")
def lire_toutes_les_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Cette commande SQLite demande le nom de toutes les tables existantes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") 
        tables_list = cursor.fetchall()
        
        # On retourne juste une liste des noms pour être léger
        return {"tables": [t['name'] for t in tables_list]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Route GET : Récupérer un client par son ID
@app.get("/client/{client_id}")
def lire_un_client(client_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,)) 
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        else:
            raise HTTPException(status_code=404, detail="Client non trouvé")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {e}")

