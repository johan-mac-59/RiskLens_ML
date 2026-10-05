# 🏦 RiskLens ML — Analyse & Prédiction du Défaut de Paiement 💳

![Python](https://img.shields.io/badge/Python-3.14-blue.svg)
![SQL](https://img.shields.io/badge/SQL-SQLite3-blue.svg)
![FastAPI](https://img.shields.io/badge/API-FastAPI-green.svg)
![Plotly](https://img.shields.io/badge/DataViz-Plotly-purple.svg)
![Scikit-Learn](https://img.shields.io/badge/Library-Scikit--Learn-orange.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)

####  *🚧 Projet en cours de développement dans le cadre de ma formation Data & IA (Évolution active vers l'intégration du Machine Learning).*

## 📌 Présentation de mon projet de fin de bootcamp
**RiskLens ML** est une mission Data & IA complète visant à transformer des données transactionnelles historiques en un outil d'aide à la décision pour la gestion du risque crédit.
Durée prévue : 7 semaines à partir du 30 août  

Le projet suit un cycle de vie data complet : du diagnostic initial et la structuration d'une base de données relationnelle, à l'exposition des données via une API, jusqu'à la création d'un modèle prédictif et d'un dashboard interactif sous Streamlit.

### 🎯 Problématique
> **"Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ?"**

L'enjeu est de déterminer si les habitudes de paiement et l'utilisation du crédit ainsi que les informations de bases d'un client sont des indicateurs suffisamment robustes pour anticiper un défaut, sans avoir accès à des données macro-économiques ou des scores de crédit externes.

Ce dataset est la base de données publique qui résulte de l'[étude scientifique de I-Cheng Yeh et Che-hui Lien (2009)](/docs/DefaultCreditCardClients_yeh_2009.pdf) (traduit en français [ici](/docs/traduction_DefaultCreditCardClients_yeh_2009.md)). Cette étude comparait plusieurs modèles pour repérer les clients à risque. Le meilleur, un réseau de neurones, obtenait un score de 0.54, ce qui correspond à un **AUC de 0.77**. L'AUC mesure la capacité d'un modèle à distinguer les bons payeurs des futurs défaillants. Mon but est de dépasser ce score.
Ma démarche adopte un prisme résolument **orienté métier**. En combinant une compréhension approfondie du jeu de données (le fonctionnement de la banque, de ses codifications et des paiements de l'époque), un nettoyage rigoureux fondé sur des règles métier et un pilotage par un score de décision (moyenne du ROC AUC et du F2 score, qui privilégie le Recall), je cherche à optimiser la détection réelle des risques de défaut, garantissant ainsi une performance robuste et réellement actionnable pour la gestion des risques bancaires.


#### 🕵️‍♂️ Pour aller plus loin : Les coulisses de la donnée

Si la problématique pose le cadre quantitatif, ce dataset est né d'un séisme financier bien réel : **la crise des cartes de crédit à Taïwan en 2005** (la crise des *"Card Monsters"*). 

Pour découvrir comment des détails logistiques de l'époque (comme les règlements en espèces dans les supérettes 7-Eleven créant des décalages sur la variable `PAY_1`) ou les parallèles avec le **Buy Now, Pay Later (BNPL)** actuel éclairent ce projet d'un point de vue purement métier : 📖 **[Consulter l'analyse complète du contexte historique et technique](docs/contexte.md)**


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

### ⚖️ Étape intermédiaire : Isoler la population contentieuse par une règle métier
*   Définition d'une population contentieuse par une règle métier explicable : deux codifications de retard d'affilée, soit au moins 90 jours : [EDA contentieux](/src/05_02_EDA_contentieux.ipynb)
*   Correction des codifications incohérentes et création d'indicateurs pour le Machine Learning, inscrites au nettoyage : [nettoyage](/src/02_01_nettoyage.ipynb)
*   Résultat : environ 10 % des clients, un tiers des défauts, 7 prédictions justes sur 10, sans aucun modèle.

### 🧠 Étape 6 : Machine Learning & Risques
*   Entraînement et comparaison d'au moins 2 modèles via **GridSearch**, sur le dataset **nettoyé de sa population contentieuse**. Première itération, sur le dataset complet : [journal des expérimentations](/lab_ML/1ere_iteration/tableau_ML.md).
*   Sélection du modèle optimal sur un **score de décision** combinant ROC AUC et F2 score (le F2 privilégie le Recall : minimisation des faux négatifs).
*   Évaluation du **système complet** (règle contentieux + modèle) sur le même jeu de test, comparée à la règle seule, aux premiers modèles et à l'étude de référence.
*   **Évaluation des risques :** Analyse des biais, éthique et limites du modèle.

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
*   **Modéliser la population contentieuse comme une sous-population spécifique** : les clients au contentieux sont aujourd'hui écartés du ML et traités par une règle métier, car un client déjà au contentieux relève du recouvrement et non de la prévention du défaut. Un modèle dédié à cette sous-population serait techniquement possible (par exemple pour distinguer les clients qui régularisent de ceux qui restent en défaut), mais il répondrait à une autre question que celle du projet.
*   **Départager les PAY_1 = 1 après un retard** : au dernier mois observé, la banque code 1 des clients dont on ne sait pas encore s'ils sortent du retard (statut d'attente). Hors dette soldée ou absence totale de paiement, aucune règle métier ne permet de trancher ; un modèle combinant la durée du retard, les paiements et l'évolution du solde pourrait en départager une partie.
