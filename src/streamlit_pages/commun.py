# Code partagé par toutes les pages Streamlit (repris de 04_02_streamlit_app.py)
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from pathlib import Path
import numpy as np
from plotly.subplots import make_subplots


# Configuration de l'URL de l'API
API_URL = "https://risklens-ml-api.onrender.com" 
# API_URL = "http://127.0.0.1:8000"  # En local

# Délai max d'attente d'une réponse API (Render peut mettre ~2 min à sortir de veille)
API_TIMEOUT = 180

# ==============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================
# --- 1. CHEMINS DE FICHIERS ---
current_file = Path(__file__).resolve()
BASE_DIR = next(
    p for p in [current_file] + list(current_file.parents) if (p / "data").exists()
)
DATA_PATH = BASE_DIR / "data" / "csv_streamlit" / "dataset_streamlit.csv"
MAPPING_PATH = BASE_DIR / "data" / "correspondances.json"

# --- 2. FONCTIONS DE CHARGEMENT AVEC CACHE ---
@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

@st.cache_data
def load_mappings():
    """Charge le JSON et reformatte chaque table en dictionnaire {code_int: description}."""
    if not os.path.exists(MAPPING_PATH):
        return {}

    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    mappings = {}
    for category, items in raw_data.items():
        if isinstance(items, list) and items:
            # Repère la colonne servant de clé (ex: 'code_genre', 'code_marital', etc.)
            code_key = next(
                (k for k in items[0].keys() if "code" in k or "id" in k),
                list(items[0].keys())[0],
            )

            # Reconstruit le dictionnaire simple {1: 'Homme', 2: 'Femme'}
            mappings[category] = {
                int(item[code_key]): item["description"]
                for item in items
                if code_key in item and "description" in item
            }
        elif isinstance(items, dict):
            mappings[category] = {int(k): v for k, v in items.items()}

    return mappings

def ratios_affichables(d, cols):
    """Ratios de paiement à afficher dans les graphiques : uniquement quand une facture était exigible
    (BILL_AMT(n+1) > 0). La colonne ratio_PAY_BILLn garde sa définition unique (100 % sans facture
    exigible, voir docs/colonnes_creees.md) : ce filtre ne sert qu'à l'affichage."""
    out = d[cols].copy()
    for col in cols:
        n = int(col.replace('ratio_PAY_BILL', ''))
        out[col] = out[col].where(d[f'BILL_AMT{n + 1}'] > 0)
    return out




@st.cache_data
def _fetch_app_mappings():
    # Une exception n'est jamais mise en cache par st.cache_data :
    # si l'API est en veille, le prochain appel retentera la requête
    res = requests.get(f"{API_URL}/metadata/mappings", timeout=API_TIMEOUT)
    res.raise_for_status()
    return res.json()

def message_erreur_api(res):
    """Transforme la réponse d'erreur de l'API en message lisible pour l'utilisateur."""
    try:
        detail = res.json().get("detail")
    except ValueError:
        # Réponse non JSON (ex : page d'erreur Render pendant le réveil du serveur)
        return f"réponse inattendue du serveur (code {res.status_code})"
    if isinstance(detail, list):
        # Erreur de validation FastAPI (422) : liste de champs refusés
        return " ; ".join(
            f"{err.get('loc', ['?'])[-1]} : {err.get('msg', '')}" for err in detail
        )
    return detail


def load_app_mappings():
    try:
        return _fetch_app_mappings()
    except Exception:
        return {}


@st.cache_data(ttl=600)
def _fetch_global_default_rate():
    # Taux de défaut sur toute la BDD (même population que le simulateur), rafraîchi toutes les 10 min
    res = requests.get(f"{API_URL}/analyze/risk-by-profile", timeout=API_TIMEOUT)
    res.raise_for_status()
    return res.json()["default_rate_pct"]

def load_global_default_rate():
    try:
        return _fetch_global_default_rate()
    except Exception:
        # Repli sur le dataset local si l'API ne répond pas
        return round(df["dpnm"].mean() * 100, 2)


# ==============================================================================
# EN-TÊTE COMMUN AUX PAGES DE LA PARTIE 3
# ==============================================================================
def entete_partie_3():
    st.title("🔎 Comprendre le jeu de données : des anomalies aux règles métier")
    st.markdown("""
    Les données ne se lisent pas telles quelles. Chaque incohérence repérée a soulevé une question, prolongé l'enquête et abouti à une **règle métier**. C'est ce qui a conduit à étudier une population définie par ces règles, en écartant le plus possible les incohérences.

    Chaque étape suit le même fil : **anomalie constatée → question posée → enquête → règle retenue**.
    """)
