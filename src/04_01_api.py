from fastapi import FastAPI, HTTPException, Query
import sqlite3
import os
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

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


# Bornes de validation partagées par les modèles (alignées sur correspondances.json et les CHECK SQL)
AGE_MIN, AGE_MAX = 18, 120
STATUT_PAIEMENT_MIN, STATUT_PAIEMENT_MAX = -2, 9


# Créer la classe ClientRequest pour avoir un modèle de client
class ClientRequest(BaseModel) :
    age: int = Field(..., description="Âge du client en années : entier entre 18 et 120", ge=AGE_MIN, le=AGE_MAX)
    # C'est ici qu'on ajoute la "notice" pour l'utilisateur dans la doc
    code_genre: GenreEnum = Field(..., description="Genre du client : 1 = Homme, 2 = Femme")
    code_marital: CodeMaritalEnum = Field(..., description="Statut matrimonial du client : 1 = Marié(e), 2 = Célibataire, 3 = Autre")
    code_scolaire: CodeScolaireEnum = Field(..., description="Code de niveau scolaire : 1 = Doctorat/Master, 2 = License, 3 = Baccalauréat, 4 = Autre")
    plafond: int = Field(..., description="Plafond de la carte bancaire : nombre entier positif", ge=0)
    code_statut_defaut: int = Field(..., description="Code du statut de défaut futur : 0 = Paiement à jour, 1 = Défaut", ge=0, le=1)
    
# Créer la classe HistoriqueMensuelRequest pour avoir un modèle de historique_mensuel
class HistoriqueMensuelRequest(BaseModel) :
    client_id: int = Field(..., description="ID du client existant", ge=1)
    # On sépare la date pour que l'utilisateur puisse choisir mois/année
    mois: MoisEnum = Field(..., description="Mois de l'historique : (1-12)")
    annee: int = Field(..., description="Année de l'historique : (ex: 2023)", ge=2000, le=2100)
    montant_encours: int = Field(..., description="Montant total dû de la carte (négatif si trop-perçu)")
    montant_paye: int = Field(..., description="Montant payé : nombre entier positif", ge=0)
    code_statut_paiement: int = Field(..., description="Code statut de paiement : de -2 à 9", ge=STATUT_PAIEMENT_MIN, le=STATUT_PAIEMENT_MAX)

class HistoriqueUpdateRequest(BaseModel):
    """
    Modèle pour une mise à jour partielle (PATCH).
    """
    montant_encours: Optional[int] = Field(default=None, description="Nouveau montant dû (négatif si trop-perçu)")
    montant_paye: Optional[int] = Field(default=None, description="Nouveau montant payé", ge=0)
    code_statut_paiement: Optional[int] = Field(default=None, description="Nouveau code statut de paiement : de -2 à 9", ge=STATUT_PAIEMENT_MIN, le=STATUT_PAIEMENT_MAX)
    
class ClientUpdateRequest(BaseModel):
    """Modèle pour la mise à jour partielle d'un client."""
    age: Optional[int] = Field(default=None, description="Âge du client", ge=AGE_MIN, le=AGE_MAX)
    code_genre: Optional[GenreEnum] = Field(default=None, description="Code genre")
    code_marital: Optional[CodeMaritalEnum] = Field(default=None, description="Code statut marital")
    code_scolaire: Optional[CodeScolaireEnum] = Field(default=None, description="Code niveau scolaire")
    plafond: Optional[int] = Field(default=None, description="Plafond de crédit", ge=0)
    code_statut_defaut: Optional[int] = Field(default=None, description="Code statut défaut : 0 ou 1", ge=0, le=1)
    

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
    conn = None
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
        
        # On retourne un dictionnaire propre : {"NomDeLaTable": ["Col1", "Col2"]}
        return resultats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if conn:
            conn.close()

# Route GET : Récupérer dynamiquement les tables de correspondance (Mappings)
@app.get("/metadata/mappings", tags=["Consultation"])
def get_metadata_mappings():
    """
    Renvoie dynamiquement les correspondances de toutes les tables de référence
    en se basant sur la structure exacte du schéma (clés spécifiques et colonne 'description').
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        mappings = {}
        
        # 1. Genre
        cursor.execute("SELECT code_genre, description FROM genre")
        mappings["genre"] = {row["code_genre"]: row["description"] for row in cursor.fetchall()}
        
        # 2. Statut Marital
        cursor.execute("SELECT code_marital, description FROM statut_marital")
        mappings["statut_marital"] = {row["code_marital"]: row["description"] for row in cursor.fetchall()}
        
        # 3. Niveau Scolaire
        cursor.execute("SELECT code_scolaire, description FROM niveau_scolaire")
        mappings["niveau_scolaire"] = {row["code_scolaire"]: row["description"] for row in cursor.fetchall()}
        
        # 4. Statut Défaut
        cursor.execute("SELECT code_statut_defaut, description FROM statut_defaut")
        mappings["statut_defaut"] = {row["code_statut_defaut"]: row["description"] for row in cursor.fetchall()}
        
        # 5. Statut Paiement (utile pour l'historique)
        cursor.execute("SELECT code_statut_paiement, description FROM statut_paiement")
        mappings["statut_paiement"] = {row["code_statut_paiement"]: row["description"] for row in cursor.fetchall()}
        
        return mappings

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur mappings : {str(e)}")
    finally:
        if conn:
            conn.close()

# Route GET : Récupérer un client par son ID
@app.get("/client/{client_id}", tags=["Gestion client"])
def lire_un_client(client_id: int):
    """
    Récupère la fiche d'un client par son ID
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        else:
            raise HTTPException(status_code=404, detail="Client non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {e}")
    finally:
        if conn:
            conn.close()


# Route Post : Ajouter un client
@app.post("/client/", tags=["Gestion client"])
def ajouter_un_client(client_data: ClientRequest):
    conn = None
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

        return {
            "message": f"Client ajouté avec succès !",
            "client_id": new_id
        }

    except sqlite3.IntegrityError as e:
        # Contrainte SQL non respectée (code inconnu dans une table de correspondance, CHECK...)
        raise HTTPException(status_code=400, detail=f"Données refusées par la BDD : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if conn:
            conn.close()
    
    
# Route Get : Lire un historique client
@app.get("/historique_mensuel/{client_id}", tags=['Gestion historique'])
def lire_historique_client(client_id: int):
    """
    Récupère tout l'historique transactionnel d'un client via son ID.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Vérifier si le client existe
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
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

        return {
            "client_id": client_id,
            "nombre_lignes": len(historique),
            "historique": historique
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if conn:
            conn.close()
    
    
@app.get("/historique_mensuel/{client_id}/{mois}/{annee}", tags=["Gestion historique"])
def lire_historique_mensuel(client_id: int, mois: MoisEnum, annee: int):
    """
    Récupère les détails d'une ligne d'historique spécifique pour un client via son ID, le mois et l'année.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Vérifier si le client existe (bonnes pratiques)
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Le client n'existe pas.")

        # 2. Récupérer le date_id pour la combinaison mois/année
        cursor.execute(
            "SELECT date_id FROM dim_date WHERE mois = ? AND annee = ?", 
            (mois.value, annee)
        )
        row_date = cursor.fetchone()

        if not row_date:
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
    finally:
        if conn:
            conn.close()

    
# Route Post : ajouter un historique_mensuel pour un client
@app.post("/historique_mensuel/", tags=["Gestion historique"])
def ajouter_historique_mensuel(data: HistoriqueMensuelRequest):
    """
    Ajoute une ligne d'historique pour un client donné.
    Si la date (mois/année) n'existe pas dans 'dim_date', elle est créée automatiquement.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 0. Vérifier si le client existe (message clair plutôt qu'une erreur de clé étrangère)
        cursor.execute("SELECT 1 FROM client WHERE client_id = ?", (data.client_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Le client {data.client_id} n'existe pas.")

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
        # Contrainte SQL non respectée (code statut inconnu, CHECK...)
        raise HTTPException(status_code=400, detail=f"Données refusées par la BDD : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if conn:
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

    conn = None
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
    except sqlite3.IntegrityError as e:
        # Contrainte SQL non respectée (code inconnu dans une table de correspondance, CHECK...)
        raise HTTPException(status_code=400, detail=f"Données refusées par la BDD : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if conn:
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

    conn = None
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
    except sqlite3.IntegrityError as e:
        # Contrainte SQL non respectée (code inconnu dans une table de correspondance, CHECK...)
        raise HTTPException(status_code=400, detail=f"Données refusées par la BDD : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if conn:
            conn.close()
        
 
# Route Delete : Supprimer un historique_mensuel par ID client et date
@app.delete("/historique_mensuel/{client_id}/{mois}/{annee}", tags=["Gestion historique"])
def supprimer_historique_mensuel(client_id: int, mois: MoisEnum, annee: int):
    """Supprime un historique mensuel spécifique en utilisant les paramètres de l'URL."""
    conn = None
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
            raise HTTPException(status_code=404, detail="Aucun historique trouvé pour ce client à cette date.")

        conn.commit()
        return {"message": f"Historique de {mois.name} {annee} supprimé pour le client {client_id}."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if conn:
            conn.close()
        
    
# Route Delete : Supprimer les historiques mensuels d'un client via son ID    
@app.delete("/historique_mensuel/{client_id}", tags=["Gestion historique"])
def supprimer_historique_client(client_id: int):
    """Supprime toutes les lignes d'historique associées à un client."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérifier si le client existe
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Le client n'existe pas.")

        # Suppression massive de l'historique
        cursor.execute(
            "DELETE FROM historique_mensuel WHERE client_id = ?", 
            (client_id,)
        )
        nb_lignes_supprimees = cursor.rowcount
        
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
        if conn:
            conn.close()


# Route Delete : Supprimer un client par son ID
@app.delete("/client/{client_id}", tags=["Gestion client"])
def supprimer_un_client(client_id: int):
    """
    Supprime un client via son ID, 
    ⚠️ supprime d'abord tout l'historique transactionnel.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Vérifier si le client existe
        cursor.execute("SELECT * FROM client WHERE client_id = ?", (client_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Le client n'existe pas")

        # 2. Nettoyage : Supprimer l'historique lié (si on ne veut pas de CASCADE en BDD)
        cursor.execute("DELETE FROM historique_mensuel WHERE client_id = ?", (client_id,))
        
        # 3. Suppression du client
        cursor.execute("DELETE FROM client WHERE client_id = ?", (client_id,))
        conn.commit()

        return {"message": f"Le client {client_id} et ses données ont été supprimés."}

    except HTTPException:
        raise
    except Exception as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="Erreur d'intégrité : il reste des liens non gérés.")
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if conn:
            conn.close()


# ==============================================================================
# ROUTE : Calcul du taux de défaut par profil démographique
# ==============================================================================
@app.get("/analyze/risk-by-profile", tags=["Analyse"])
def get_risk_by_profile(
    gender_code: Optional[int] = Query(None, description="Code genre (1=M, 2=F)", ge=1, le=2),
    marital_status: Optional[int] = Query(None, description="Statut marital (1 à 3)", ge=1, le=3),
    education_level: Optional[int] = Query(None, description="Niveau scolaire (1 à 4)", ge=1, le=4),
    age_min: Optional[int] = Query(None, description="Âge minimum", ge=0, le=AGE_MAX),
    age_max: Optional[int] = Query(None, description="Âge maximum", ge=0, le=AGE_MAX)
):
    """
    Calcule le taux de défaut moyen pour un profil démographique spécifique.
    Les paramètres sont optionnels (None = tous).
    """
    if age_min is not None and age_max is not None and age_min > age_max:
        raise HTTPException(status_code=400, detail="L'âge minimum doit être inférieur ou égal à l'âge maximum.")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construction dynamique de la requête
        query = "SELECT COUNT(*) as total, SUM(code_statut_defaut) as default_count FROM client"
        params = []

        conditions = []
        
        if gender_code is not None:
            conditions.append("code_genre = ?")
            params.append(gender_code)
            
        if marital_status is not None:
            conditions.append("code_marital = ?")
            params.append(marital_status)
            
        if education_level is not None:
            conditions.append("code_scolaire = ?")
            params.append(education_level)
            
        if age_min is not None and age_max is not None:
            conditions.append("age BETWEEN ? AND ?")
            params.extend([age_min, age_max])
        elif age_min is not None:
            conditions.append("age >= ?")
            params.append(age_min)
        elif age_max is not None:
            conditions.append("age <= ?")
            params.append(age_max)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        row = cursor.fetchone()

        total = row[0]
        defaults = row[1] or 0
        
        rate = (defaults / total * 100) if total > 0 else None
        
        return {
            "total_clients": total,
            "defaut_count": defaults,
            "default_rate_pct": round(rate, 2) if rate is not None else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")
    finally:
        if conn:
            conn.close()
    
    
    
#=======================================================
# ZONE ADMIN
#=======================================================

import secrets
from fastapi import Depends, status
from dotenv import load_dotenv
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Charge le fichier .env en local (ignoré automatiquement sur Render)
load_dotenv()

# Récupération des 2 variables
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# 1. Configuration du système de sécurité HTTP Basic
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Fonction de dépendance (Dependency) injectée dans les routes protégées.
    
    Elle intercepte les identifiants envoyés par le client (Streamlit, Swagger UI, Curl),
    les compare aux variables d'environnement secrètes, et autorise ou bloque l'accès.
    """
    # Si les variables d'environnement ne sont pas définies, l'accès est refusé à tout le monde
    if not ADMIN_USER or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Espace admin non configuré sur le serveur.",
        )

    # compare_digest compare en temps constant : on ne peut pas deviner le mot de passe
    # caractère par caractère en mesurant le temps de réponse (attaque temporelle)
    is_correct_user = secrets.compare_digest(
        credentials.username.encode("utf-8"), ADMIN_USER.encode("utf-8")
    )
    is_correct_pass = secrets.compare_digest(
        credentials.password.encode("utf-8"), ADMIN_PASSWORD.encode("utf-8")
    )
    
    if not (is_correct_user and is_correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Route réservée à l'ADMIN pour télécharger la BDD
@app.get("/admin/telecharger-db", tags=["Admin"], dependencies=[Depends(verify_credentials)])
def telecharger_database():
    """Permet à l'administrateur de télécharger une copie complète de la BDD SQLite."""
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Fichier de base de données introuvable."
        )
    
    return FileResponse(
        path=DB_PATH, 
        filename="risklens_backup.db", 
        media_type="application/x-sqlite3"
    )