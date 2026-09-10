from fastapi import FastAPI, HTTPException
import sqlite3
import os
from pydantic import BaseModel, Field
from enum import Enum

# Le chemin ABSOLU du dossier où se trouve ce script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Remonter à la racine du projet (un niveau au-dessus de src/)
root_dir = os.path.dirname(script_dir)

# Chemin vers la BDD
DB_PATH = os.path.join(root_dir, 'database', 'creditcard.db')

app = FastAPI(title="Mon API Risklens")


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
    
class MoisEnum(int, Enum):
    janvier = 1
    fevrier = 2
    mars = 3
    avril = 4
    mai = 5
    juin = 6
    juillet = 7
    aout = 8
    septembre = 9
    octobre = 10
    novembre = 11
    decembre = 12


# Créer la classe ClientRequest pour avoir un modèle de client
class ClientRequest(BaseModel) :
    age: int = Field(..., description="Âge du client en années : nombre entier positif")
    # C'est ici qu'on ajoute la "notice" pour l'utilisateur dans la doc
    code_genre: GenreEnum = Field(..., description="Genre du client : 1 = Homme, 2 = Femme")
    code_marital: StatutMaritalEnum = Field(..., description="Statut matrimonial du client : 1 = Marié(e), 2 = Célibataire, 3 = Autre")
    code_scolaire: CodeScolaireEnum = Field(..., description="Code de niveau scolaire : 1 = Doctorat/Master, 2 = License, 3 = Baccalauréat, 4 = Autre")
    plafond: float = Field(..., description="Plafond de la carte bancaire : nombre entier positif")
    code_statut_defaut: int = Field(..., description="Code du statut de défaut futur : 0 = Paiement à jour, 1 = Défaut")
    
# Créer la classe HistoriqueMensuelRequest pour avoir un modèle de historique_mensuel
class HistoriqueMensuelRequest(BaseModel) :
    client_id: int = Field(..., description="ID du client existant")
    # On sépare la date pour que l'utilisateur puisse choisir mois/année
    mois: MoisEnum = Field(..., description="Mois de l'historique : (1-12)")
    annee: int = Field(..., description="Année de l'historique : (ex: 2023)", ge=2000, le=2100)
    montant_encours: int = Field(..., description="Montant total dû de la carte")
    montant_paye: int = Field(..., description="Montant payé")
    code_statut_paiement: int = Field(..., description="Score de statut du compte client")
    

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
    
    
# Route Post : ajouter un historique_mensuel pour un client
@app.post("/historique_mensuel/")
def ajouter_historique_mensuel(data: HistoriqueMensuelRequest):
    """Ajoute une ligne d'historique pour un client donné.
    
    La fonction cherche automatiquement le 'date_id' correspondant au mois/année saisis
    dans la table de référence des dates.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Trouver le date_id correspondant à la date saisie (mois + annee)
        # On suppose que tu as une table 'dates' avec des colonnes 'mois' et 'annee'
        cursor.execute(
            "SELECT date_id FROM dim_date WHERE mois = ? AND annee = ?", 
            (data.mois.value, data.annee)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=404, 
                detail=f"La date {data.mois.name}/{data.annee} n'est pas référencée dans la table 'date'. Veuillez d'abord créer cette date dans le catalogue des dates."
            )

        date_id = row['date_id']

        # 2. Insérer dans l'historique en utilisant le date_id trouvé
        cursor.execute(
            """INSERT INTO historique_mensuel 
               (client_id, date_id, montant_encours, montant_paye, code_statut_paiement) 
               VALUES (?, ?, ?, ?, ?)""",
            (data.client_id, date_id, data.montant_encours, data.montant_paye, data.code_statut_paiement)
        )
        
        conn.commit()
        
        return {
            "message": f"Historique ajouté pour le client {data.client_id} pour la date {data.mois.name}/{data.annee}",
            "date_id_utilise": date_id
        }

    except HTTPException:
        # On relance les erreurs HTTP (comme 404) sans modification
        raise
    except Exception as e:
        # En cas d'erreur technique (contrainte de clé étrangère, type de données, etc.)
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        conn.close()
    
    
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