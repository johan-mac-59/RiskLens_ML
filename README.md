# 🏦 RiskLens ML — Analyse & Prédiction du Défaut de Paiement 💳

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/API-FastAPI-green.svg)
![PowerBI](https://img.shields.io/badge/BI-PowerBI-yellow.svg)
![Scikit-Learn](https://img.shields.io/badge/Library-Scikit--Learn-orange.svg)

## 📌 Présentation de mon projet de fin de bootcamp
**RiskLens ML** est une mission Data & IA complète visant à transformer des données transactionnelles historiques en un outil d'aide à la décision pour la gestion du risque crédit.
Durée prévue : 7 semaines à partir du 30 août

Le projet suit un cycle de vie data complet : du diagnostic initial et la structuration d'une base de données relationnelle, à l'exposition des données via une API, jusqu'à la création d'un modèle prédictif et d'un dashboard décisionnel.

### 🎯 Problématique
> **"Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ?"**

L'enjeu est de déterminer si les habitudes de paiement et l'utilisation du crédit sont des indicateurs suffisamment robustes pour anticiper un défaut, sans avoir accès à des données macro-économiques ou des scores de crédit externes.

## 🚀 Roadmap & Étapes du Projet

### 🛠️ Étape 1 : Cadrage & Diagnostic
*   Analyse du dataset *Default of Credit Card Clients*.
*   Formulation de la problématique et identification des limites (manque de données contextuelles).
*   Premier nettoyage et audit des données.

### 🗄️ Étape 2 : Structuration & Base de Données
*   Nettoyage final des données.
*   **Modélisation relationnelle :** Conception d'un schéma SQL normalisé (création de tables de correspondance pour transformer les codes numériques en libellés explicites).
*   Chargement des données dans la base de données.

### 🌐 Étape 3 : Exposition des données (API)
*   Développement d'une API avec **FastAPI**.
*   Implémentation des 4 opérations **CRUD** (Create, Read, Update, Delete) pour permettre l'accès et la gestion des données sans accès direct à la base.

### 🔍 Étape 4 : Analyse Exploratoire & Veille
*   Analyse statistique approfondie (corrélations, tendances) avec Python.
*   Data Visualisation pour identifier les facteurs clés du défaut de paiement.
*   **Synthèse de veille :** Recherche autonome sur les évolutions actuelles de l'IA et du Big Data.

### 📊 Étape 5 : Restitution Décisionnelle (Power BI)
*   Construction d'un dashboard interactif sous **Power BI**.
*   Mise en place de 3 axes d'analyse et de 4 KPI clés (incluant une analyse géographique via une carte).

### 🧠 Étape 6 : Machine Learning & Risques
*   Entraînement et comparaison d'au moins 2 modèles via **GridSearch**.
*   Sélection du modèle optimal basé sur le **Recall** (minimisation des faux négatifs).
*   **Évaluation des risques :** Analyse des biais, éthique et limites du modèle.

### 🎙️ Étape 7 : Storytelling & Restitution
*   Synthèse finale et présentation orale adaptée à un public non technique.

## 📋 Pilotage du projet
Le suivi rigoureux de la mission est assuré via un tableau **Trello**, mis à jour hebdomadairement pour monitorer l'avancement des étapes et le respect du planning.
*   [lien Trello](https://trello.com/b/OKlbbtCy/risklens-ml)

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
*   **Langage :** Python (Pandas, NumPy)
*   **Base de données :** SQL (Structuration relationnelle)
*   **API :** FastAPI
*   **BI :** Power BI
*   **Machine Learning :** Scikit-Learn, SHAP (pour l'explicabilité)