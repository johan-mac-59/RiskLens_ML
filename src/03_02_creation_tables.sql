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


-- ============================================================
-- 2. CRÉATION DES TABLES DIMENSIONS / CORRESPONDANCE
-- ============================================================

CREATE TABLE genre (
    code_genre INTEGER PRIMARY KEY,
    description VARCHAR(20) NOT NULL
);

CREATE TABLE statut_marital (
    code_marital INTEGER PRIMARY KEY,
    description VARCHAR(30) NOT NULL
);

CREATE TABLE niveau_scolaire (
    code_scolaire INTEGER PRIMARY KEY,
    description VARCHAR(40) NOT NULL
);

CREATE TABLE statut_defaut (
    code_statut_defaut INTEGER PRIMARY KEY,
    description VARCHAR(50) NOT NULL
);

CREATE TABLE dim_date (
    date_id INTEGER PRIMARY KEY,
    mois INTEGER NOT NULL,
    annee INTEGER NOT NULL 
);

CREATE TABLE statut_paiement (
    code_statut_paiement INTEGER PRIMARY KEY,
    description VARCHAR(100) NOT NULL
);


-- ============================================================
-- 3. CRÉATION DES TABLES PRINCIPALES (CLIENT & HISTORIQUE)
-- ============================================================

CREATE TABLE client (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER NOT NULL CHECK (age >= 0),
    code_genre INTEGER NOT NULL,
    code_marital INTEGER NOT NULL,
    code_scolaire INTEGER NOT NULL,
    plafond INTEGER NOT NULL CHECK (plafond >= 0),
    code_statut_defaut INTEGER,
    
    -- Cascade sur les codifications pour permettre leur refonte dans les tables dimensions
    FOREIGN KEY (code_genre) REFERENCES genre(code_genre) ON UPDATE CASCADE,
    FOREIGN KEY (code_marital) REFERENCES statut_marital(code_marital) ON UPDATE CASCADE,
    FOREIGN KEY (code_scolaire) REFERENCES niveau_scolaire(code_scolaire) ON UPDATE CASCADE,
    FOREIGN KEY (code_statut_defaut) REFERENCES statut_defaut(code_statut_defaut) ON UPDATE CASCADE
);

CREATE TABLE historique_mensuel (
    client_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    montant_encours INTEGER NOT NULL,
    montant_paye INTEGER NOT NULL CHECK (montant_paye >= 0),
    code_statut_paiement INTEGER NOT NULL,
    
    -- Clé primaire composite
    PRIMARY KEY (client_id, date_id),

    -- Pas de CASCADE sur client_id et date_id (IDs immuables)
    FOREIGN KEY (client_id) REFERENCES client(client_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    
    -- Cascade sur la codification du statut de paiement
    FOREIGN KEY (code_statut_paiement) REFERENCES statut_paiement(code_statut_paiement) ON UPDATE CASCADE
);