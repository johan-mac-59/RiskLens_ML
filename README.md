# 🏦 RiskLens ML — Analyse & Prédiction du Défaut de Paiement 💳

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![SQL](https://img.shields.io/badge/SQL-SQLite3-blue.svg)
![FastAPI](https://img.shields.io/badge/API-FastAPI-green.svg)
![Plotly](https://img.shields.io/badge/DataViz-Plotly-purple.svg)
![Scikit-Learn](https://img.shields.io/badge/Library-Scikit--Learn-orange.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)

## 📌 Présentation de mon projet de fin de bootcamp
**RiskLens ML** est une mission Data & IA complète visant à transformer des données transactionnelles historiques en un outil d'aide à la décision pour la gestion du risque crédit.
Durée prévue : 7 semaines à partir du 30 août  

Le projet suit un cycle de vie data complet : du diagnostic initial et la structuration d'une base de données relationnelle, à l'exposition des données via une API, jusqu'à la création d'un modèle prédictif et d'un dashboard interactif sous Streamlit.

### 🎯 Problématique
> **"Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ?"**

L'enjeu est de déterminer si les habitudes de paiement et l'utilisation du crédit ainsi que les informations de bases d'un client sont des indicateurs suffisamment robustes pour anticiper un défaut, sans avoir accès à des données macro-économiques ou des scores de crédit externes.

Ce dataset est la base de données publique qui résulte de l'[étude scientifique de I-Cheng Yeh et Che-hui Lien (2009)](/docs/DefaultCreditCardClients_yeh_2009.pdf) (traduit en français [ici](/docs/traduction_DefaultCreditCardClients_yeh_2009.md)). Cette étude comparait plusieurs modèles pour repérer les clients à risque. Le meilleur, un réseau de neurones, obtenait un score de 0.54, ce qui correspond à un **AUC de 0.77**. L'AUC mesure la capacité d'un modèle à distinguer les bons payeurs des futurs défaillants. Mon but était de dépasser ce score. Sur le même fichier, mes modèles trient un peu mieux (score de 0,567, soit un AUC d'environ 0,78), mais la comparaison reste indicative : l'étude cherchait surtout à bien estimer la probabilité de défaut, pas à détecter un maximum de défauts, et ne publie ni rappel ni précision ([détail](/docs/hypotheses_et_conclusions.md)).
Ma démarche adopte un prisme résolument **orienté métier**. En combinant une compréhension approfondie du jeu de données (le fonctionnement de la banque, de ses codifications et des paiements de l'époque), un nettoyage rigoureux fondé sur des règles métier et un pilotage par la **précision des défauts prédits** à un taux de détection fixé (le rappel minimal), je cherche à optimiser la détection réelle des risques de défaut. Le résultat est présenté par **niveaux de risque**, pour une gestion des risques bancaires réellement actionnable.


#### 🕵️‍♂️ Pour aller plus loin : Les coulisses de la donnée

Si la problématique pose le cadre quantitatif, ce dataset est né d'un séisme financier bien réel : **la crise des cartes de crédit à Taïwan en 2005** (la crise des *"Card Monsters"*). 

Pour découvrir comment des détails logistiques de l'époque (comme les règlements en espèces dans les supérettes 7-Eleven créant des décalages sur la variable `PAY_1`) ou les parallèles avec le **Buy Now, Pay Later (BNPL)** actuel éclairent ce projet d'un point de vue purement métier : 📖 **[Consulter l'analyse complète du contexte historique et technique](docs/contexte.md)**


## 🏁 Résultats en bref

*   **Une règle métier avant tout modèle** : les clients au contentieux (deux codifications de retard d'affilée, soit au moins 90 jours) représentent environ 10 % des clients et un tiers des défauts, avec 7 prédictions justes sur 10, sans aucun modèle. Un modèle dédié à cette population a été essayé : avec l'exigence de la banque (ne sortir un client du contentieux que s'il a au moins 9 chances sur 10 de payer), il ne sait sortir personne. La règle reste la décision.
*   **Le machine learning pour les autres clients** : la version finale, confirmée sur un jeu de test jamais vu, classe les clients par niveau de risque : environ 4 sur 10 font défaut en **haut risque**, 2 sur 10 en **risque modéré**, 1 sur 10 en **risque faible**. Règle et modèle ensemble repèrent environ trois quarts des défauts en signalant environ 4 clients sur 10 : un outil de **priorisation**, pas de sanction.
*   **Une limite mesurée** : environ un tiers des défauts ne s'annonce pas dans le comportement des six mois. La cible semble suivre le statut posé par la banque plutôt qu'un défaut de paiement observé ; c'est elle qui fixe le plafond des modèles.
*   **Réponse à la problématique** : oui, en partie. Le comportement de paiement explique une partie du défaut, à l'échelle des groupes de clients, mais pas au client près ; une fois le contentieux mis à part, les montants (factures, paiements, plafond) portent l'essentiel de ce qui est prévisible.

Détails : [journal du machine learning](/lab_ML/tableau_ML.md), [méthodologie](/lab_ML/methodologie_ML.md), [hypothèses et conclusions](/docs/hypotheses_et_conclusions.md).


## 🚀 Roadmap & Étapes du Projet

### 🛠️ Étape 1 : Cadrage & Diagnostic
*   Analyse du dataset *Default of Credit Card Clients*.
*   Formulation de la problématique et identification des limites (manque de données contextuelles).
*   Premier nettoyage et audit des données : [notebook d'audit](/src/01_01_audit.ipynb)

### 🗄️ Étape 2 : Structuration & Base de Données
*   Nettoyage final des données : [notebook de nettoyage](/src/02_01_nettoyage.ipynb)
*   Modélisation relationnelle : création  d'une [schéma de base relationnelle](/images/schema_bdd__risklens.png) | conception d'un schéma SQL normalisé (création de tables de correspondance pour transformer les codes numériques en libellés explicites) : [script de création des tables](/src/03_02_creation_tables.sql)
*   Chargement des données dans la base de données : [script d'ingestion des données](/src/03_01_ingestion_donnees.py)


### 🌐 Étape 3 : Exposition des données (API)
*   Développement d'une API avec **FastAPI**.
*   Implémentation des 4 types d'opérations **CRUD** (Create, Read, Update, Delete) pour permettre l'accès et la gestion des données sans accès direct à la base : [fichier API](/src/04_01_api.py)

### 🔍 Étape 4 : Analyse Exploratoire
*   Analyse statistique approfondie (corrélations, tendances) avec Python : [EDA laboratoire](/src/05_01_EDA_lab.ipynb)
*   Recherche du périmètre de la population contentieuse (CTX) à isoler : [EDA contentieux](/src/05_02_EDA_contentieux.ipynb)
*   Étude dédiée de la codification PAY_n = 1 (statut provisoire du dernier mois, corrections retenues) : [EDA codification 1](/src/05_04_EDA_codification1.ipynb)
*   Data Visualisation pour identifier les facteurs clés du défaut de paiement : [EDA DataViz](/src/05_03_EDA_storytelling.ipynb)

### 📊 Étape 5 : Restitution Décisionnelle (Streamlit)
*   Dashboard interactif sous **Streamlit**, construit au fil de l'analyse : chaque graphique et chaque chiffre est recalculé en direct sur les données.
*   Restitution en ligne : [accéder au site Streamlit](https://risklens-ml.streamlit.app/)

### 🧠 Étape 6 : Machine Learning & Risques
*   Modèles entraînés sur les clients à encours positif, **sans la population contentieuse** (traitée par la règle métier), avec un découpage entraînement / test propre au machine learning : [création des jeux](/lab_ML/creation_datasets_ML.ipynb).
*   Six modèles comparés (régression logistique, SVM, KNN, réseau de neurones, RandomForest, CatBoost), puis les quatre meilleurs gardés pour la phase finale (régression logistique, réseau de neurones, RandomForest, CatBoost), réglés par une **boucle automatique de GridSearch** sous contrainte de surapprentissage, en validation croisée à 5 plis ; réglage sur la **précision des défauts prédits** au rappel minimal (60 % des défauts), classement par le score décisionnel F2.
*   Variables ajoutées par scénarios, puis élaguées ; chaque scénario comparé à sa référence pli par pli, les écarts serrés tranchés par une validation croisée répétée : [journal des scénarios](/lab_ML/tableau_ML.md).
*   **Version finale** : 21 variables, aucune donnée démographique, CatBoost ; lue **une seule fois** sur le jeu de test, qui confirme la validation : [évaluation finale](/lab_ML/evaluation_finale_test.ipynb).
*   **Limites** : analyse des défauts que les modèles manquent et de la cible elle-même : [méthodologie, section 13](/lab_ML/methodologie_ML.md).

### 🎙️ Étape 7 : Storytelling & Restitution
*   Synthèse finale et présentation orale adaptée à un public non technique.

## 📋 Pilotage du projet
Le suivi rigoureux de la mission est assuré via un tableau **Trello**, mis à jour hebdomadairement pour monitorer l'avancement des étapes et le respect du planning.
*   [lien Trello](https://trello.com/b/OKlbbtCy/risklens-ml)

## 🌐 Architecture & Accès en Ligne

Le projet est entièrement déployé dans le cloud selon une architecture découplée (API Backend + Interface Frontend) :

* **🖥️ Interface Utilisateur (Frontend Streamlit) :** [Accéder à la démo en ligne](https://risklens-ml.streamlit.app/)
* **⚙️ Documentation Technique (Backend FastAPI / Swagger UI) :** [Explorer l'API et les routes](https://risklens-ml-api.onrender.com/docs)

### 🧪 Fonctionnalités à tester sur l'interface :
* **Consultation (GET)** : Requêter les profils clients et leurs historiques de paiement issus de la BDD SQLite.
* **Opérations CRUD (POST / PATCH / DELETE)** : Simuler l'ajout, la modification ou la suppression de dossiers clients en direct.
* **Validation des schémas JSON** : Inspecter la structure des requêtes et les modèles de données (Pydantic).

> ℹ️ *L'API est hébergée sur l'offre gratuite de Render. Si le serveur est en veille, la première requête peut prendre jusque 1 minute à répondre.*

## ⚙️ Installation
1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/johan-mac-59/RiskLens_ML
   cd RiskLens_ML
   ```
2. **Installer les dépendances** (via `uv`) :
   ```bash
   uv sync
   ```
3. **Configuration des données** :
   Téléchargez le dataset depuis [Kaggle](https://www.kaggle.com/datasets/mariosfish/default-of-credit-card-clients/data) et placez le fichier CSV dans le dossier `data/raw/`, sous le nom `default of credit card clients.csv` (le nom attendu par `src/02_01_nettoyage.ipynb`).
   Pour reproduire le machine learning : exécuter `src/02_01_nettoyage.ipynb` en entier, puis `lab_ML/creation_datasets_ML.ipynb`, puis les scénarios `lab_ML/ml_0.ipynb`, `ml_1`… dans l'ordre (détail : section 0 de [`lab_ML/methodologie_ML.md`](lab_ML/methodologie_ML.md)).

## 🛠️ Stack Technique
* **Langage :** Python (Pandas, NumPy, Uvicorn, Requests)
* **Base de données :** SQLite (Modélisation relationnelle, Foreign Keys)
* **API & Backend :** FastAPI, Pydantic (Validation des schémas JSON, Opérations CRUD, Documentation Swagger UI)
* **Déploiement Cloud :** Render (API Web Service), GitHub (Gestion de versions & Intégration continue)
* **Gestionnaire de paquets :** `uv` (`pyproject.toml`)
* **Data visualisation :** Plotly, Streamlit (dashboard interactif)
* **Machine Learning :** Scikit-Learn, CatBoost
* **Front-end / UI :** Streamlit Cloud

## 🔭 Axes d'amélioration
*   **Obtenir la définition exacte de la cible (`dpnm`)** : elle n'est pas documentée, et ne semble pas être un simple défaut de paiement observé (des clients sans dette sont comptés en défaut). C'est la condition de toute amélioration.
*   **Obtenir les vrais encours et la liste réelle des clients en incident** (recouvrement, contentieux) : le montant du relevé n'est pas la dette réelle, et la population contentieuse est ici reconstruite à partir des codifications.
*   **Départager les PAY_1 = 1 après un retard par un modèle** : au dernier mois observé, la banque codifie 1 des clients dont on ne sait pas encore s'ils sortent du retard (statut d'attente). Hors dette soldée ou absence totale de paiement, aucune règle métier ne permet de trancher ; un modèle combinant la durée du retard, les paiements et l'évolution du solde pourrait en départager une partie, mais ce travail dépend fortement de la définition réelle de la cible.
*   **Estimer une probabilité de défaut par client** (calibration), l'objectif principal de l'étude d'origine, au lieu d'un taux par niveau de risque.
