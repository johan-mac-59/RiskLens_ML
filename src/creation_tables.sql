-- Activer le support des clés étrangères sous SQLite
PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. SUPPRESSION DES TABLES (Ordre inverse des dépendances)
-- ============================================================
DROP TABLE IF EXISTS historique_mensuel;
DROP TABLE IF EXISTS client;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS statut_paiement;
DROP TABLE IF EXISTS statut_defaut;
DROP TABLE IF EXISTS niveau_scolaire;
DROP TABLE IF EXISTS statut_marital;
DROP TABLE IF EXISTS genre;


-- =======================
-- 2. CRÉATION DES TABLES
-- =======================

CREATE TABLE genre(
    code_genre          INTEGER PRIMARY KEY,
    "description"       VARCHAR(20) NOT NULL
)
;

CREATE TABLE statut_marital(
    code_marital        INTEGER PRIMARY KEY,
    "description"       VARCHAR(30) NOT NULL
)
;

CREATE TABLE niveau_scolaire(
    code_scolaire       INTEGER PRIMARY KEY,
    "description"       VARCHAR(40) NOT NULL
)
;

CREATE TABLE statut_defaut(
    code_statut_defaut      INTEGER PRIMARY KEY,
    "description"           VARCHAR(50) NOT NULL
)
;

CREATE TABLE client(
    client_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    age                 INTEGER NOT NULL,
    code_genre          INTEGER NOT NULL,
    code_marital        INTEGER NOT NULL,
    code_scolaire       INTEGER NOT NULL,
    plafond             INTEGER NOT NULL,
    code_statut_defaut  INTEGER NOT NULL,
    FOREIGN KEY (code_genre) REFERENCES genre(code_genre),
    FOREIGN KEY (code_marital) REFERENCES statut_marital(code_marital),
    FOREIGN KEY (code_scolaire) REFERENCES niveau_scolaire(code_scolaire),
    FOREIGN KEY (code_statut_defaut) REFERENCES statut_defaut(code_statut_defaut)
    )
;

CREATE TABLE dim_date(
    date_id     INTEGER PRIMARY KEY,
    mois        INTEGER NOT NULL,
    annee       INTEGER NOT NULL 
)
;

CREATE TABLE statut_paiement(
    code_statut_paiement    INTEGER PRIMARY KEY,
    "description"           VARCHAR(100)
)
;

CREATE TABLE historique_mensuel (
    client_id               INTEGER NOT NULL,
    date_id                 INTEGER NOT NULL,
    montant_encours         INTEGER NOT NULL,
    montant_paye            INTEGER NOT NULL,
    code_statut_paiement    INTEGER NOT NULL,
    
    -- Clé primaire composite basée sur les 2 clés étrangères
    PRIMARY KEY (client_id, date_id),

    FOREIGN KEY (client_id) REFERENCES client(id_client),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (code_statut_paiement) REFERENCES statut_paiement(code_statut_paiement)
)
;


-- mettre l'autoincrement à partir de 30001 dans le script python