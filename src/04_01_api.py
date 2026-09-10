from fastapi import FastAPI, HTTPException
import sqlite3
import os


# Le chemin ABSOLU du dossier où se trouve ce script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Remonter à la racine du projet (un niveau au-dessus de src/)
root_dir = os.path.dirname(script_dir)

# Chemin vers la BDD
DB_PATH = os.path.join(root_dir, 'database', 'creditcard.db')

app = FastAPI(title="Mon API Risklens")


from enum import Enum

# On définit les choix possibles
class GenreEnum(int, Enum) :
    homme = 1
    femme = 2

class StatutMaritalEnum(int, Enum) :
    marie = 1
    celibataire = 2
    autre = 3

class CodeScolaireEnum(int, Enum) :
    doctorat_master = 1
    License = 2
    Baccalauréat = 3
    Autre = 4

from pydantic import BaseModel, Field

# Créer la classe ClientRequest pour avoir un modèle de client
class ClientRequest(BaseModel):
    age: int = Field(..., description="Âge du client en années : nombre entier positif")
    # C'est ici qu'on ajoute la "notice" pour l'utilisateur dans la doc
    code_genre: GenreEnum = Field(..., description="Genre du client : 1 = Homme, 2 = Femme")
    code_marital: StatutMaritalEnum = Field(..., description="Statut matrimonial du client : 1 = Marié(e), 2 = Célibataire, 3 = Autre")
    code_scolaire: CodeScolaireEnum = Field(..., description="Code de niveau scolaire : 1 = Doctorat/Master, 2 = License, 3 = Baccalauréat, 4 = Autre")
    plafond: float = Field(..., description="Plafond de la carte bancaire : nombre entier positif")
    code_statut_defaut: int = Field(..., description="Code du statut de défaut futur : 0 = Paiement à jour, 1 = Défaut")
    

# créer la connexion
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Pour récupérer les résultats sous forme de dictionnaires
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# Route GET : Récupérer toutes les tables (CRUD: Read)
@app.get("/tables")
def lire_toutes_les_tables():
    """Récupère le nom des tables et leurs colonnes"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. On récupère la liste de toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%';")
        tables_list = cursor.fetchall()
        
        resultats = {}

        # 2. Pour chaque table, on demande ses colonnes
        for table in tables_list:
            table_name = table['name']
            try:
                # La commande magique qui donne les infos des colonnes
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                # On garde juste le nom de la colonne pour être clair
                resultats[table_name] = [col['name'] for col in columns]
            except Exception as e:
                resultats[table_name] = ["Erreur lors de la lecture des colonnes"]

        conn.close()
        
        # On retourne un dictionnaire propre : {"NomDeLaTable": ["Col1", "Col2"]}
        return resultats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")


# Route GET : Récupérer un client par son ID
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


# Route Post : Ajouter un client
@app.post("/client/")
def ajouter_un_client(client_data: ClientRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # On insère les données en respectant l'ordre des colonnes que tu m'as donné
        cursor.execute(
            """INSERT INTO client 
               (age, code_genre, code_marital, code_scolaire, plafond, code_statut_defaut) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (client_data.age, 
             client_data.code_genre, 
             client_data.code_marital, 
             client_data.code_scolaire, 
             client_data.plafond, 
             client_data.code_statut_defaut)
        )
        
        conn.commit() # On valide le changement
        new_id = cursor.lastrowid # On récupère l'ID auto-généré par SQLite
        
        conn.close()
        
        return {
            "message": f"Client ajouté avec succès !", 
            "client_id": new_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    
    
# Route Delete : Supprimer un client par son ID
@app.delete("/client/{client_id}")
def supprimer_un_client(client_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. On vérifie d'abord si le client existe pour ne pas faire d'erreur silencieuse
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Le client n'existe pas")

        # 2. On effectue la suppression
        cursor.execute("DELETE FROM client WHERE client_id = ?", (client_id,))
        conn.commit()
        
        conn.close()
        return {"message": f"Le client avec l'ID {client_id} a été supprimé"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")