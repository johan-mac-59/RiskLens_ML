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
# Effectifs de chaque étape du nettoyage, enregistrés par 02_01_nettoyage (page 3.5)
ENTONNOIR_PATH = BASE_DIR / "data" / "csv_streamlit" / "entonnoir_nettoyage.csv"

# --- 2. FONCTIONS DE CHARGEMENT AVEC CACHE ---
@st.cache_data
def _lire_csv(chemin, date_modification):
    """Lecture mise en cache ; la date de modification fait partie de la clé : un CSV régénéré est relu automatiquement."""
    return pd.read_csv(chemin)


def load_data():
    return _lire_csv(DATA_PATH, DATA_PATH.stat().st_mtime).copy()


def load_entonnoir():
    """Effectifs du nettoyage, indexés par étape (colonnes : retires, clients, plafonds_atypiques_origine)."""
    return _lire_csv(ENTONNOIR_PATH, ENTONNOIR_PATH.stat().st_mtime).set_index("etape")

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
# EN-TÊTE COMMUN AUX PAGES DE LA PARTIE 2
# ==============================================================================
def entete_partie_2():
    st.title("🗄️ 2. La base de données et l'API REST")
    st.markdown("""
    Avant d'être analysées, les données sont rangées comme dans le système d'information d'une banque : une **base de données relationnelle** (SQLite), accessible uniquement par une **API REST** (FastAPI). Le fichier plat de 30 000 lignes devient des tables reliées entre elles, et toute lecture ou modification passe par l'API, qui contrôle chaque donnée avant de toucher à la base.

    La base contient les 30 000 clients du fichier d'origine, après un nettoyage structurel (niveau 0). C'est une base de démonstration : les analyses des parties suivantes s'appuient sur une version plus poussée du nettoyage.
    """)


# ==============================================================================
# EN-TÊTE COMMUN AUX PAGES DE LA PARTIE 3
# ==============================================================================
def entete_partie_3():
    st.title("🔎 3. Comprendre le jeu de données : des anomalies aux règles métier")
    st.markdown("""
    Les données ne se lisent pas telles quelles. Chaque incohérence repérée a soulevé une question, prolongé l'enquête et abouti à une **règle métier**. C'est ce qui a conduit à étudier une population définie par ces règles, en écartant le plus possible les incohérences.

    Chaque étape suit le même fil : **anomalie constatée → question posée → enquête → règle retenue**.

    Le **taux de défaut** cité dans cette partie est la part des clients en défaut de paiement en octobre 2005, le mois qui suit les six mois de données. Il sert à décrire, jamais à fixer une règle.
    """)


# ==============================================================================
# EN-TÊTE COMMUN AUX PAGES DE LA PARTIE 4
# ==============================================================================
# ==============================================================================
# RÈGLE COMMUNE DES TAILLES DE POLICE DES GRAPHIQUES (valeurs brutes, en pixels)
# ==============================================================================
TAILLE_ETIQUETTE = 14     # étiquettes de données (valeurs écrites sur les graphiques)
TAILLE_GRADUATIONS = 14   # libellés des axes x et y (12 par défaut dans Plotly, + 2)
TAILLE_TITRES_AXES = 15   # titres des axes x et y (environ 14 par défaut dans Plotly, + 1)

_plotly_chart_streamlit = st.plotly_chart


def _plotly_chart_style_commun(figure, *args, **kwargs):
    """Applique les tailles communes aux axes de tout graphique Plotly avant son affichage."""
    if isinstance(figure, go.Figure):
        figure.update_xaxes(tickfont_size=TAILLE_GRADUATIONS, title_font_size=TAILLE_TITRES_AXES)
        figure.update_yaxes(tickfont_size=TAILLE_GRADUATIONS, title_font_size=TAILLE_TITRES_AXES)
    return _plotly_chart_streamlit(figure, *args, **kwargs)


# Toutes les pages importent commun.py : st.plotly_chart applique ainsi la règle commune partout
if getattr(st.plotly_chart, "__name__", "") != "_plotly_chart_style_commun":
    st.plotly_chart = _plotly_chart_style_commun


def codif(valeur):
    """Valeur de PAY_n affichée comme une étiquette grisée dans les textes, pour ne pas la confondre avec un chiffre.
    Syntaxe Markdown de Streamlit : fonctionne aussi dans st.info, st.caption, etc."""
    return f":gray-background[{valeur}]"


def nombre_fr(n, decimales=0):
    """Nombre au format français : espace pour les milliers, virgule pour les décimales."""
    return f"{n:,.{decimales}f}".replace(",", " ").replace(".", ",")


def entete_partie_4(df):
    st.title("📊 4. Explorer le portefeuille : profils, usage de la carte, paiements et défauts")
    st.markdown(f"""
    Les données sont désormais fiables. Cette partie les explore sous tous les angles : le profil des clients, l'usage qu'ils font de leur carte (paiement comptant ou crédit), leur comportement de paiement, la vie de leurs comptes, puis les retards et le défaut de paiement. Chaque étape éclaire le risque de défaut. C'est au fil de cette exploration qu'est apparue une population à part, celle des clients en gestion contentieuse : une réalité métier qu'il a fallu constater, nommer, puis définir pour ce dataset (partie 5).

    Les analyses portent sur les **{nombre_fr(len(df))} clients** retenus par le nettoyage (page « 3.5 Décisions ») et sont calculées en direct sur ces données. Le **taux de défaut**, c'est-à-dire la part des clients en défaut de paiement en octobre 2005, le mois qui suit les six mois de données, y est en moyenne de **{nombre_fr(df['dpnm'].mean() * 100, 1)} %**. Les taux affichés décrivent des tendances et ne servent à fixer aucune règle.
    """)


# ==============================================================================
# PALETTE GÉNÉRALE DES GRAPHIQUES : « Safe » de Plotly (px.colors.qualitative.Safe), lisible par les daltoniens
# Les teintes réservées aux codifications (COULEURS_CODIF) ne sont pas réutilisées ailleurs, pour garder leur sens
# ==============================================================================
COULEURS = {
    "bleu_pale": "#88CCEE",
    "rouge_pale": "#CC6677",
    "jaune": "#DDCC77",
    "vert_fonce": "#117733",
    "mauve": "#332288",
    "violet": "#AA4499",
    "turquoise": "#44AA99",
    "olive": "#999933",
    "bordeaux": "#882255",
    "gris": "#888888",
    "orange": "#EE7733",  # repère (ex. ligne de moyenne), absent de la palette des barres
}


# ==============================================================================
# COULEURS DES CODIFICATIONS DE PAIEMENT (palette « Safe » de Plotly, lisible par les daltoniens)
# Du plus risqué au moins risqué : couleurs chaudes pour les retards, froides pour les codifications saines
# ==============================================================================
COULEURS_CODIF = {
    "2 et plus": "#CC6677",  # rouge pâle
    "1": "#DDCC77",          # jaune orangé
    "0": "#88CCEE",          # bleu pâle
    "-1": "#117733",         # vert foncé
    "-2": "#332288",         # mauve foncé
}

