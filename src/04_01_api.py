from fastapi import FastAPI, HTTPException
import sqlite3
import os
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Union

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

class CodeMaritalEnum(int, Enum) :
    marie = 1
    celibataire = 2
    autre = 3

class CodeScolaireEnum(int, Enum) :
    doctorat_master = 1
    license = 2
    baccalauréat = 3
    autre = 4
    
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
    code_marital: CodeMaritalEnum = Field(..., description="Statut matrimonial du client : 1 = Marié(e), 2 = Célibataire, 3 = Autre")
    code_scolaire: CodeScolaireEnum = Field(..., description="Code de niveau scolaire : 1 = Doctorat/Master, 2 = License, 3 = Baccalauréat, 4 = Autre")
    plafond: int = Field(..., description="Plafond de la carte bancaire : nombre entier positif")
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

class HistoriqueUpdateRequest(BaseModel):
    """
    Modèle pour une mise à jour partielle (PATCH).
    """
    montant_encours: Optional[int] = Field(default=None, description="Nouveau montant dû")
    montant_paye: Optional[int] = Field(default=None, description="Nouveau montant payé")
    code_statut_paiement: Optional[int] = Field(default=None, description="Nouveau code_statut_paiement")
    
class ClientUpdateRequest(BaseModel):
    """Modèle pour la mise à jour partielle d'un client."""
    age: Optional[int] = Field(default=None, description="Âge du client")
    code_genre: Optional[GenreEnum] = Field(default=None, description="Code genre")
    code_marital: Optional[CodeMaritalEnum] = Field(default=None, description="Code statut marital")
    code_scolaire: Optional[CodeScolaireEnum] = Field(default=None, description="Code niveau scolaire")
    plafond: Optional[int] = Field(default=None, description="Plafond de crédit", ge=0)
    code_statut_defaut: Optional[int] = Field(default=None, description="Code statut défaut")
    

# créer la connexion
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Pour récupérer les résultats sous forme de dictionnaires
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# Route GET : Récupérer toutes les tables (CRUD: Read)
@app.get("/tables", tags=["Consultation"])
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
@app.get("/client/{client_id}", tags=["Gestion client"])
def lire_un_client(client_id: int):
    """
    Récupère la fiche d'un client par son ID
    """
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
@app.post("/client/", tags=["Gestion client"])
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
    
    
# Route Get : Lire un historique client
@app.get("/historique_mensuel/{client_id}", tags=['Gestion historique'])
def lire_historique_client(client_id: int):
    """
    Récupère tout l'historique transactionnel d'un client via son ID.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Vérifier si le client existe
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Le client n'existe pas.")

        # 2. Récupérer l'historique avec jointure sur dim_date
        # On récupère mois et annee depuis la table de dimensions pour avoir des libellés lisibles
        cursor.execute("""
            SELECT 
                h.client_id,
                d.mois,
                d.annee,
                h.montant_encours,
                h.montant_paye,
                h.code_statut_paiement
            FROM historique_mensuel h
            JOIN dim_date d ON h.date_id = d.date_id
            WHERE h.client_id = ?
            ORDER BY d.annee DESC, d.mois ASC
        """, (client_id,))

        lignes = cursor.fetchall()
        
        # 3. Transformer les résultats en dictionnaires lisibles
        historique = []
        for ligne in lignes:
            historique.append({
                "client_id": ligne['client_id'],
                "date_complexe": {
                    "mois_num": ligne['mois'],
                    "annee": ligne['annee'],
                },
                "montant_encours": ligne['montant_encours'],
                "montant_paye": ligne['montant_paye'],
                "code_statut_paiement": ligne['code_statut_paiement']
            })

        conn.close()
        
        return {
            "client_id": client_id,
            "nombre_lignes": len(historique),
            "historique": historique
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    
    
@app.get("/historique_mensuel/{client_id}/{mois}/{annee}", tags=["Gestion historique"])
def lire_historique_mensuel(client_id: int, mois: MoisEnum, annee: int):
    """
    Récupère les détails d'une ligne d'historique spécifique pour un client via son ID, le mois et l'année.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Vérifier si le client existe (bonnes pratiques)
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Le client n'existe pas.")

        # 2. Récupérer le date_id pour la combinaison mois/année
        cursor.execute(
            "SELECT date_id FROM dim_date WHERE mois = ? AND annee = ?", 
            (mois.value, annee)
        )
        row_date = cursor.fetchone()

        if not row_date:
            conn.close()
            raise HTTPException(status_code=404, detail=f"La date {mois.name}/{annee} n'existe pas dans le catalogue.")

        date_id = row_date['date_id']

        # 3. Récupérer la ligne d'historique exacte
        cursor.execute(
            """SELECT h.client_id, d.mois, d.annee, 
                      h.montant_encours, h.montant_paye, h.code_statut_paiement
               FROM historique_mensuel h
               JOIN dim_date d ON h.date_id = d.date_id
               WHERE h.client_id = ? AND h.date_id = ?""",
            (client_id, date_id)
        )
        row_histo = cursor.fetchone()

        conn.close()

        if not row_histo:
            return {
                "message": f"Aucun historique trouvé pour le client {client_id} en {mois.name}/{annee}",
                "found": False
            }

        # 4. Retourner les données sous forme de dictionnaire
        return {
            "found": True,
            "client_id": row_histo['client_id'],
            "date": {
                "mois": row_histo['mois'],
                "annee": row_histo['annee']
            },
            "montant_encours": row_histo['montant_encours'],
            "montant_paye": row_histo['montant_paye'],
            "code_statut_paiement": row_histo['code_statut_paiement']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")

    
# Route Post : ajouter un historique_mensuel pour un client
@app.post("/historique_mensuel/", tags=["Gestion historique"])
def ajouter_historique_mensuel(data: HistoriqueMensuelRequest):
    """
    Ajoute une ligne d'historique pour un client donné.
    Si la date (mois/année) n'existe pas dans 'dim_date', elle est créée automatiquement.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Recherche de la date dans le dictionnaire dim_date
        cursor.execute(
            "SELECT date_id FROM dim_date WHERE mois = ? AND annee = ?", 
            (data.mois.value, data.annee)
        )
        row_date = cursor.fetchone()

        if not row_date:
            # Calcul explicite du date_id (ex: 2000 * 100 + 1 = 200001)
            date_id = data.annee * 100 + data.mois.value
            
            # La date n'existe pas : création automatique dans dim_date avec son ID calculé
            cursor.execute(
                "INSERT INTO dim_date (date_id, mois, annee) VALUES (?, ?, ?)",
                (date_id, data.mois.value, data.annee)
            )
            date_creee = True
        else:
            date_id = row_date['date_id']
            date_creee = False

        # 2. Vérification de l'existence du couple (client_id, date_id)
        cursor.execute(
            "SELECT 1 FROM historique_mensuel WHERE client_id = ? AND date_id = ?",
            (data.client_id, date_id)
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=409, 
                detail=f"Un historique existe déjà pour le client {data.client_id} en {data.mois.name} {data.annee}."
            )

        # 3. Insertion dans la table de faits historique_mensuel
        cursor.execute(
            """INSERT INTO historique_mensuel 
               (client_id, date_id, montant_encours, montant_paye, code_statut_paiement) 
               VALUES (?, ?, ?, ?, ?)""",
            (data.client_id, date_id, data.montant_encours, data.montant_paye, data.code_statut_paiement)
        )
        
        # Validation atomique (dim_date + historique_mensuel)
        conn.commit()
        
        message_suffix = " (nouvelle date créée dans le catalogue)" if date_creee else ""

        return {
            "message": f"Historique ajouté avec succès pour le client {data.client_id} ({data.mois.name} {data.annee}){message_suffix}.",
            "date_id_utilise": date_id
        }

    except HTTPException:
        raise
    except sqlite3.IntegrityError as e:
        # Capture les violations de clés étrangères (ex: client_id inexistant)
        raise HTTPException(
            status_code=400, 
            detail=f"Erreur d'intégrité BDD : Vérifiez que le client {data.client_id} existe bien."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
        

# Route Patch : modifier un client
@app.patch("/client/{client_id}", tags=["Gestion client"])
def modifier_client(client_id: int, data: ClientUpdateRequest):
    """
    Modifie partiellement les informations d'un client existant.
    Seuls les champs renseignés dans le JSON seront mis à jour.
    """
    
    # mode='json' convertit automatiquement les Enums en entiers pour SQLite
    champs_a_modifier = data.model_dump(exclude_unset=True, exclude_none=True, mode='json')

    if not champs_a_modifier:
        raise HTTPException(status_code=400, detail="Aucun champ à modifier.")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Vérifier si le client existe
        cursor.execute("SELECT 1 FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Le client n'existe pas.")

        # 2. Construction dynamique de la requête SQL
        set_clause = ", ".join([f"{cle} = ?" for cle in champs_a_modifier.keys()])
        valeurs = list(champs_a_modifier.values())

        query = f"UPDATE client SET {set_clause} WHERE client_id = ?"
        cursor.execute(query, (*valeurs, client_id))

        conn.commit()
        return {"message": f"Le client {client_id} a été modifié avec succès."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        conn.close()
    

# Route Patch : modifier un historique mensuel
@app.patch("/historique_mensuel/{client_id}/{mois}/{annee}", tags=['Gestion historique'])
def modifier_historique_mensuel(
    client_id: int, 
    mois: MoisEnum, 
    annee: int, 
    data: HistoriqueUpdateRequest
):
    """Met à jour uniquement les champs spécifiés de l'historique mensuel pour un client donné et une date donnée."""
    
    # 1. Extraction automatique des champs explicitement envoyés
    champs_a_modifier = data.model_dump(exclude_unset=True, exclude_none=True)

    if not champs_a_modifier:
        raise HTTPException(status_code=400, detail="Aucun champ à modifier.")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 2. Récupération du date_id
        cursor.execute(
            "SELECT date_id FROM dim_date WHERE mois = ? AND annee = ?", 
            (mois.value, annee)
        )
        row_date = cursor.fetchone()

        if not row_date:
            raise HTTPException(status_code=404, detail="La date n'est pas référencée.")

        date_id = row_date['date_id']

        # 3. Vérification de l'existence de la ligne d'historique
        cursor.execute(
            "SELECT * FROM historique_mensuel WHERE client_id = ? AND date_id = ?", 
            (client_id, date_id)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Aucun historique trouvé pour ce client à cette date.")

        # 4. Construction et exécution de la requête SQL dynamique
        set_clause = ", ".join([f"{cle} = ?" for cle in champs_a_modifier.keys()])
        valeurs = list(champs_a_modifier.values())

        query = f"UPDATE historique_mensuel SET {set_clause} WHERE client_id = ? AND date_id = ?"
        cursor.execute(query, (*valeurs, client_id, date_id))
        
        conn.commit()
        return {"message": f"Ligne {mois.name} {annee} partiellement mise à jour pour le client {client_id}."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        conn.close()
        
 
# Route Delete : Supprimer un historique_mensuel par ID client et date
@app.delete("/historique_mensuel/{client_id}/{mois}/{annee}", tags=["Gestion historique"])
def supprimer_historique_mensuel(client_id: int, mois: MoisEnum, annee: int):
    """Supprime un historique mensuel spécifique en utilisant les paramètres de l'URL."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Trouver le date_id correspondant à la date saisie (mois + annee)
        cursor.execute(
            "SELECT date_id FROM dim_date WHERE mois = ? AND annee = ?", 
            (mois.value, annee)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail=f"La date {mois.name} {annee} n'est pas référencée.")

        date_id = row['date_id']

        # 2. Supprimer la ligne spécifique à ce client et cette date
        cursor.execute(
            "DELETE FROM historique_mensuel WHERE client_id = ? AND date_id = ?", 
            (client_id, date_id)
        )
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Aucun historique trouvé pour ce client à cette date.")

        conn.commit()
        return {"message": f"Historique de {mois.name} {annee} supprimé pour le client {client_id}."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        conn.close()
        
    
# Route Delete : Supprimer les historiques mensuels d'un client via son ID    
@app.delete("/historique_mensuel/client/{client_id}", tags=["Gestion client"])
def supprimer_historique_client(client_id: int):
    """Supprime toutes les lignes d'historique associées à un client."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérifier si le client existe (au cas où)
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Le client n'existe pas.")

        # Suppression massive de l'historique
        nb_lignes_supprimees = cursor.execute(
            "DELETE FROM historique_mensuel WHERE client_id = ?", 
            (client_id,)
        ).rowcount
        
        conn.commit()
        
        return {
            "message": f"L'historique du client {client_id} a été supprimé.",
            "lignes_supprimees": nb_lignes_supprimees
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        conn.close()


# Route Delete : Supprimer un client par son ID
@app.delete("/client/{client_id}", tags=["Gestion client"])
def supprimer_un_client(client_id: int):
    """
    Supprime un client via son ID, 
    ⚠️ supprime d'abord tout l'historique transactionnel.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Vérifier si le client existe
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Le client n'existe pas")

        # 2. Nettoyage : Supprimer l'historique lié (si on ne veut pas de CASCADE en BDD)
        cursor.execute("DELETE FROM historique_mensuel WHERE client_id = ?", (client_id,))
        
        # 3. Suppression du client
        cursor.execute("DELETE FROM client WHERE client_id = ?", (client_id,))
        conn.commit()
        
        conn.close()
        return {"message": f"Le client {client_id} et ses données ont été supprimés."}

    except HTTPException:
        raise
    except Exception as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="Erreur d'intégrité : il reste des liens non gérés.")
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")

