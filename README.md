# 🏦 RiskLens ML — Analyse & Prédiction du Défaut de Paiement 💳

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![SQL](https://img.shields.io/badge/SQL-SQLite3-blue.svg)
![FastAPI](https://img.shields.io/badge/API-FastAPI-green.svg)
![PowerBI](https://img.shields.io/badge/BI-PowerBI-yellow.svg)
![Scikit-Learn](https://img.shields.io/badge/Library-Scikit--Learn-orange.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)

####  *🚧 Projet en cours de développement dans le cadre de ma formation Data & IA (Évolution active vers l'intégration du Machine Learning).*

## 📌 Présentation de mon projet de fin de bootcamp
**RiskLens ML** est une mission Data & IA complète visant à transformer des données transactionnelles historiques en un outil d'aide à la décision pour la gestion du risque crédit.
Durée prévue : 7 semaines à partir du 30 août  

Le projet suit un cycle de vie data complet : du diagnostic initial et la structuration d'une base de données relationnelle, à l'exposition des données via une API, jusqu'à la création d'un modèle prédictif et d'un dashboard décisionnel.

### 🎯 Problématique
> **"Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ?"**

L'enjeu est de déterminer si les habitudes de paiement et l'utilisation du crédit ainsi que les informations de bases d'un client sont des indicateurs suffisamment robustes pour anticiper un défaut, sans avoir accès à des données macro-économiques ou des scores de crédit externes.

Ce dataset est la base de données publique qui résulte de l'[étude scientifique de I-Cheng Yeh et Che-hui Lien (2009)](/docs/DefaultCreditCardClients_yeh_2009.pdf) (traduit en français [ici](/docs/traduction_DefaultCreditCardClients_yeh_2009.md)). Cette étude s'appuyait principalement sur l'Exactitude (Accuracy) globale. Mon but est de dépasser le score maximal de 2009 qui était de 0.54, ce qui équivaut à un **AUC de 0.77**.
Ma démarche adopte un prisme résolument **orienté métier**. En combinant un nettoyage rigoureux des données et un pilotage par le F1-score et le Recall, je cherche à optimiser la détection réelle des risques de défaut, garantissant ainsi une performance robuste et réellement actionnable pour la gestion des risques bancaires.


#### 🕵️‍♂️ Pour aller plus loin : Les coulisses de la donnée

Si la problématique pose le cadre quantitatif, ce dataset est né d'un séisme financier bien réel : **la crise des cartes de crédit à Taïwan en 2005** (la crise des *"Card Monsters"*). 

Pour découvrir comment des détails logistiques de l'époque (comme les règlements en espèces dans les supérettes 7-Eleven créant des décalages sur la variable `PAY_1`) ou les parallèles avec le **Buy Now, Pay Later (BNPL)** actuel éclairent ce projet d'un point de vue purement métier :
> 📖 **[Consulter l'analyse complète du contexte historique et technique](docs/contexte.md)**


## 🚀 Roadmap & Étapes du Projet

### 🛠️ Étape 1 : Cadrage & Diagnostic
*   Analyse du dataset *Default of Credit Card Clients*.
*   Formulation de la problématique et identification des limites (manque de données contextuelles).
*   Premier nettoyage et audit des données : [notebook d'audit](/src/01_01_audit.ipynb)

### 🗄️ Étape 2 : Structuration & Base de Données
*   Nettoyage final des données : [notebook de nettoyage](/src/02_01_nettoyage.ipynb)
*   Modélisation relationnelle : création  d'une [schéma de base relationnelle](/images/schema_bdd_svg.svg) | conception d'un schéma SQL normalisé (création de tables de correspondance pour transformer les codes numériques en libellés explicites) : [script de création des tables](/src/03_02_creation_tables.sql)
*   Chargement des données dans la base de données : [script d'ingestion des données](/src/03_01_ingestion_donnees.py)


### 🌐 Étape 3 : Exposition des données (API)
*   Développement d'une API avec **FastAPI**.
*   Implémentation des 4 types d'opérations **CRUD** (Create, Read, Update, Delete) pour permettre l'accès et la gestion des données sans accès direct à la base : [fichier API](/src/04_01_api.py)

### 🔍 Étape 4 : Analyse Exploratoire & Veille
*   Analyse statistique approfondie (corrélations, tendances) avec Python : [EDA laboratoire](/src/EDA_lab.ipynb)
*   Data Visualisation pour identifier les facteurs clés du défaut de paiement : [EDA DataViz](/src/EDA_storytelling.ipynb)
*   **Synthèse de veille :** Recherche autonome sur les évolutions actuelles de l'IA et du Big Data.

### 📊 Étape 5 : Restitution Décisionnelle (Power BI)
*   Construction d'un dashboard interactif sous **Power BI**.
*   Mise en place d'axes d'analyse et de KPI clés : [télécharger le rapport .pbix](/power_bi/rapport_pbi.pbix) *(fichier téléchargeable pour visionnage local)*
*   Restitution visuelle via Streamlit : [fichier Streamlit](/src/04_02_streamlit_app.py)

### 🧠 Étape 6 : Machine Learning & Risques
*   Entraînement et comparaison d'au moins 2 modèles via **GridSearch**.
*   Sélection du modèle optimal basé sur le **Recall** (minimisation des faux négatifs).
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
* **Opérations CRUD (POST / PUT / DELETE)** : Simuler l'ajout, la modification ou la suppression de dossiers clients en direct.
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
   Téléchargez le dataset depuis [Kaggle](https://www.kaggle.com/datasets/mariosfish/default-of-credit-card-clients/data) et placez le fichier CSV dans le dossier `data/`.

## 🛠️ Stack Technique
* **Langage :** Python (Pandas, NumPy, Uvicorn, Requests)
* **Base de données :** SQLite (Modélisation relationnelle, Foreign Keys)
* **API & Backend :** FastAPI, Pydantic (Validation des schémas JSON, Opérations CRUD, Documentation Swagger UI)
* **Déploiement Cloud :** Render (API Web Service), GitHub (Gestion de versions & Intégration continue)
* **Gestionnaire de paquets :** `uv` (`pyproject.toml`)
* **Business Intelligence :** Power BI (Dashboard décisionnel, Time Intelligence)
* **Machine Learning :** Scikit-Learn, SHAP (Explicabilité & Interprétabilité)
* **Front-end / UI :** Streamlit Cloud