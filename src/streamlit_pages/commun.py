# Code partagé par toutes les pages Streamlit (repris de 04_02_streamlit_app.py)
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import re
from pathlib import Path
import numpy as np
from plotly.subplots import make_subplots


# Configuration de l'URL de l'API
API_URL = "https://risklens-ml-api.onrender.com" 
# API_URL = "http://127.0.0.1:8000"  # En local

# Délai max d'attente d'une réponse API (Render met environ une minute à sortir de veille ; marge pour les lectures par lot)
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

    ⏳ L'API est hébergée sur l'offre gratuite de Render : quand le serveur s'est mis en veille, la première requête peut prendre jusqu'à une minute.
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
    """Applique les tailles communes aux axes de tout graphique Plotly avant son affichage
    (sauf si le graphique fixe lui-même une taille, comme l'entonnoir des démos)."""
    if isinstance(figure, go.Figure):
        for axe in list(figure.select_xaxes()) + list(figure.select_yaxes()):
            if axe.tickfont.size is None:
                axe.tickfont.size = TAILLE_GRADUATIONS
            if axe.title.font.size is None:
                axe.title.font.size = TAILLE_TITRES_AXES
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


# ==============================================================================
# ENCADRÉ DES OUTILS INTERACTIFS (simulateurs) : fond turquoise léger, pour les distinguer du texte
# Turquoise de la palette, absent des codifications ; transparence pour rester lisible en thème clair et sombre
# ==============================================================================
# Invitation en tête de l'encadré : turquoise plus foncé (lisible sur fond clair comme sombre), plus grande et en gras
def encadre_interactif(cle, invitation=None):
    st.markdown(f"""<style>
    .st-key-{cle} {{ background: rgba(68, 170, 153, 0.12); border: 1px solid rgba(68, 170, 153, 0.6);
                     border-radius: 0.6rem; padding: 1rem 1.2rem; }}
    .invitation-interactif {{ color: #2E8B7A; font-size: 1.3rem; font-weight: 700; margin-bottom: 0.2rem; }}
    </style>""", unsafe_allow_html=True)
    conteneur = st.container(key=cle)
    if invitation:
        conteneur.markdown(f'<div class="invitation-interactif">👇 {invitation}</div>', unsafe_allow_html=True)
    return conteneur


# ==============================================================================
# SIMULATEUR DE RISQUE PAR PROFIL, CALCULÉ SUR UN DATAFRAME (4.1, 5.5…)
# Même interface que le simulateur de la démo de l'API, qui interroge la base ;
# d : population sur laquelle on calcule (colonnes AGE_BUCKET, SEX, EDUCATION, MARRIAGE, dpnm)
# ==============================================================================
TRANCHES_AGE = ['21-25', '26-30', '31-35', '36-40', '41-50', '51+']


def simulateur_profil(d, cle, phrase_population, nom_moyenne, populations=None):
    """populations (facultatif) : {libellé : (données, phrase_population, nom_moyenne)}, choisies dans une case en tête du simulateur."""
    mappings = load_mappings()
    genre_map = {int(k): v for k, v in mappings.get("genre", {}).items()}
    marital_map = {int(k): v for k, v in mappings.get("statut_marital", {}).items()}
    scolaire_map = {int(k): v.replace("License", "Licence") for k, v in mappings.get("niveau_scolaire", {}).items()}
    with encadre_interactif(cle, invitation="À vous de tester : choisissez un profil de client et découvrez son taux de défaut de paiement"):
        st.subheader("🧮 Simulateur de risque par profil", anchor=cle.replace("_", "-"))
        if populations:
            choix = st.selectbox("Population", options=list(populations), key=f"{cle}_population")
            d, phrase_population, nom_moyenne = populations[choix]
        taux_moyen = d["dpnm"].mean() * 100
        st.markdown(f"Vous aussi, calculez le taux de défaut de paiement selon les critères choisis, {phrase_population}.")

        st.info("Sélectionnez les critères du client hypothétique.")
        col_sim1, col_sim2 = st.columns([1, 1])

        with col_sim1:
            # Choix Âge : les mêmes tranches que les graphiques (AGE_BUCKET)
            selected_tranche = st.selectbox(
                "Tranche d'âge",
                options=["Tous âges"] + TRANCHES_AGE,
                format_func=lambda x: x if x == "Tous âges" else f"{x} ans",
                key=f"{cle}_age"
            )

            # Genre
            selected_genre = st.selectbox(
                "Genre",
                options=[-1] + list(genre_map.keys()),
                format_func=lambda x: f"{genre_map.get(x, 'Tous les genres')} ({x})" if x != -1 else "Tous les genres",
                key=f"{cle}_genre"
            )

        with col_sim2:
            # Scolaire
            selected_edu = st.selectbox(
                "Niveau d'études",
                options=[-1] + list(scolaire_map.keys()),
                format_func=lambda x: f"{scolaire_map.get(x, 'Tous niveaux')} ({x})" if x != -1 else "Tous niveaux",
                key=f"{cle}_edu"
            )

            # Mariage
            selected_marital = st.selectbox(
                "Statut marital",
                options=[-1] + list(marital_map.keys()),
                format_func=lambda x: f"{marital_map.get(x, 'Tous statuts')} ({x})" if x != -1 else "Tous statuts",
                key=f"{cle}_marital"
            )

        # Bouton de calcul
        if st.button("🔍 Calculer le taux de défaut", type="primary", width='stretch', key=f"{cle}_bouton"):

            # Filtre de la population selon les critères choisis
            masque = pd.Series(True, index=d.index)
            if selected_tranche != "Tous âges":
                masque &= d["AGE_BUCKET"] == selected_tranche
            if selected_genre != -1:
                masque &= d["SEX"] == selected_genre
            if selected_edu != -1:
                masque &= d["EDUCATION"] == selected_edu
            if selected_marital != -1:
                masque &= d["MARRIAGE"] == selected_marital

            total_clients = int(masque.sum())
            if total_clients == 0:
                st.warning("Aucun client ne correspond exactement à ces critères combinés. Essayez d'élargir les tranches.")
            else:
                defaut_count = int(d.loc[masque, "dpnm"].sum())
                risk_pct = round(defaut_count / total_clients * 100, 2)

                # Affichage des résultats
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.metric(label="Nombre de clients ciblés", value=nombre_fr(total_clients))
                with col_res2:
                    st.metric(label="Taux de défaut observé", value=f"{nombre_fr(risk_pct, 2)} %")

                st.info(f"Sur ces {nombre_fr(total_clients)} clients, **{nombre_fr(defaut_count)}** ont fait défaut de paiement en octobre.")

                # Barre visuelle pour comparer à la moyenne de la population
                global_avg = round(taux_moyen, 2)
                col_viz1, col_viz2 = st.columns([3, 1])
                with col_viz1:
                    st.progress(risk_pct / 100, f"Risque du profil ({nombre_fr(risk_pct, 2)} %) contre moyenne {nom_moyenne} ({nombre_fr(global_avg, 2)} %)")
                with col_viz2:
                    delta_val = round(risk_pct - global_avg, 1) + 0.0
                    st.metric(label="Écart à la moyenne", value=f"{delta_val:+.1f} points".replace(".", ","))


# ==============================================================================
# TABLEAUX HTML (largeurs de colonnes fixées, cellules colorées possibles)
# ==============================================================================
STYLE_CELLULE_HTML = "border: 1px solid rgba(128, 128, 128, 0.3); padding: 6px 8px; vertical-align: top; text-align: left;"


def tableau_html(entetes, lignes, largeurs=None):
    """Tableau HTML : une cellule est un texte, ou un couple (texte, style CSS ajouté à la cellule)."""
    def cellule(c, balise="td", fond=""):
        texte, style = c if isinstance(c, tuple) else (c, "")
        return f'<{balise} style="{STYLE_CELLULE_HTML} {fond} {style}">{texte}</{balise}>'
    colonnes = ("<colgroup>" + "".join(f'<col style="width: {l}%">' for l in largeurs) + "</colgroup>") if largeurs else ""
    tete = "".join(cellule(e, "th", "background: rgba(128, 128, 128, 0.1);") for e in entetes)
    corps = "".join("<tr>" + "".join(cellule(c) for c in ligne) + "</tr>" for ligne in lignes).replace("$", "&#36;")
    # Étiquettes grisées de codif() : la syntaxe Markdown de Streamlit n'est pas lue dans du HTML, on la traduit
    corps, tete = (re.sub(r":gray-background\[([^\]]*)\]",
                          r'<span style="background: rgba(128, 128, 128, 0.2); padding: 0 4px; border-radius: 4px;">\1</span>', t)
                   for t in (corps, tete))
    st.markdown(
        f'<table style="width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 1rem;">{colonnes}'
        f"<thead><tr>{tete}</tr></thead><tbody>{corps}</tbody></table>",
        unsafe_allow_html=True,
    )


# Mois dans l'ordre chronologique (gauche à droite) : PAY_6 = avril, ..., PAY_1 = septembre
MOIS_CHRONO = [(6, "Avril"), (5, "Mai"), (4, "Juin"), (3, "Juillet"), (2, "Août"), (1, "Septembre")]


def cellule_codif(valeur):
    """Cellule de tableau HTML colorée selon la codification (mêmes couleurs que COULEURS_CODIF)."""
    if valeur is None or valeur == "":
        return ("", "")
    v = int(valeur)
    fond = COULEURS_CODIF["2 et plus"] if v >= 2 else COULEURS_CODIF[str(v)]
    texte = "white" if v in (-1, -2) else "black"
    return (f"<b>{v}</b>", f"background: {fond}; color: {texte}; text-align: center;")


# ==============================================================================
# PARTIE 5 : LA POPULATION CONTENTIEUSE
# ==============================================================================
# Statut à M de chaque client, lu dans STATUT_INCIDENT (niveau 3 du nettoyage, docs/colonnes_creees.md). Ordre : du plus
# risqué au moins risqué. Couleurs, toutes tirées de la palette « Safe » de Plotly : bordeaux = en incident, violet = retard
# imminent (population à part), bleu nuit = sorti de l'incident, jaune = retard régularisé, vert-bleu = jamais en retard
STATUTS_CTX = {
    "En incident": COULEURS["bordeaux"],
    "Retard imminent": COULEURS["violet"],
    "Sorti de l'incident": COULEURS["mauve"],
    "Retard régularisé": COULEURS["jaune"],
    "Jamais en retard": COULEURS["turquoise"],
}
NOMS_STATUTS = list(STATUTS_CTX)
# Libellés sur deux lignes pour les axes des graphiques étroits
LIBELLES_STATUTS = {
    "En incident": "En<br>incident",
    "Retard imminent": "Retard<br>imminent",
    "Sorti de l'incident": "Sorti de<br>l'incident",
    "Retard régularisé": "Retard<br>régularisé",
    "Jamais en retard": "Jamais<br>en retard",
}


def statut_incident(d):
    """Statut de chaque client à M, lu dans STATUT_INCIDENT."""
    return pd.Series(pd.Categorical(d["STATUT_INCIDENT"], categories=NOMS_STATUTS), index=d.index)


@st.cache_data
def _decoupage_partie_5(chemin, date_modification):
    """Périmètre S12 et découpage train / test, identiques à ceux de l'étude de la population en incident (05_02) et de la première itération du ML :
    encours positif en septembre et plafond <= 500 000 NT$ (S12), 80/20, stratifié sur dpnm, random_state=42."""
    from sklearn.model_selection import train_test_split
    df = pd.read_csv(chemin)
    s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)].copy()
    train, test = train_test_split(s12, test_size=0.2, stratify=s12["dpnm"], random_state=42)
    return df, s12, train, test


def etiquette_grise(fig, x, y, texte, yshift=12, xshift=0):
    """Petite étiquette grisée posée sur une barre (au-dessus, ou à droite avec xshift pour les barres horizontales)."""
    fig.add_annotation(x=x, y=y, yshift=yshift, xshift=xshift, showarrow=False, text=f"<b>{texte}</b>",
                       font_size=TAILLE_ETIQUETTE, bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2)


def donnees_partie_5():
    """Population retenue, périmètre S12, jeux d'entraînement et de test, avec le statut de chaque client."""
    # Statuts calculés hors du cache : un changement de libellé ou de règle est pris en compte sans vider le cache
    donnees = [d.copy() for d in _decoupage_partie_5(DATA_PATH, DATA_PATH.stat().st_mtime)]
    for d in donnees[1:]:
        d["STATUT"] = statut_incident(d)
    return donnees


def entete_partie_5(df, s12, train, test, renvoi_genese=True):
    """En-tête court et global, repris sur toutes les pages de la partie 5 (renvoi_genese=False sur la page 5.1 elle-même).
    Le périmètre et le découpage entraînement / test sont présentés en page 5.1, pas ici."""
    st.title("⚖️ 5. La population en incident : des retards figés à une règle métier")
    renvoi = " La genèse de l'étude, l'hypothèse qui relie ses anomalies et sa méthode sont présentées en page « 5.1 La genèse »." if renvoi_genese else ""
    st.markdown(f"""
    Tout part de clients figés en retard, au taux de défaut anormalement élevé, et d'un modèle de machine learning qui plafonnait. L'étude a d'abord posé des règles candidates, fondées sur la logique métier. En les confrontant aux montants, elle a découvert des anomalies de codification et les a corrigées. Elle a ensuite vérifié et ajusté la définition sur le jeu d'entraînement, puis l'a validée une seule fois sur le jeu de test. Les corrections ont enfin été inscrites dans le nettoyage, et contrôlées.

    Le résultat est la **population en incident** : une sous-population définie par une règle métier **explicable et traçable**, prédite en défaut sans modèle. Rien n'est perdu en chemin : aucun client n'est supprimé, chaque correction laisse une trace, et l'historique des retards est transmis au machine learning sous forme de **nouvelles variables** (partie 6).{renvoi}
    """)


def entete_partie_6():
    """En-tête de la partie 6, repris sur toutes ses pages."""
    st.title("🤖 6. Le machine learning")
    st.markdown("""
    Le but du machine learning est de prédire le défaut de paiement d'octobre 2005 à partir des six mois d'historique de chaque client, et de faire mieux que l'étude de référence de 2009. Cette partie raconte la première tentative, puis la démarche reprise une fois la population contentieuse définie : les scénarios, le modèle retenu et son évaluation sur le test, ce qui limite ses performances, et les risques du projet.
    """)


# ==============================================================================
# DÉMOS DE LA PARTIE 7 (pages 7.2 et 7.3) : légende des niveaux de risque, du plus risqué au moins risqué
# ==============================================================================
# Bleu des encadrés d'information de Streamlit (st.info) : le risque faible a la même couleur que le message « client non signalé »
BLEU_INFO = "#1C83E1"
NIVEAUX_DEMO = {
    "Retiré par le nettoyage": (COULEURS["gris"], "white", "paiement géant, compte inactif ou plafond de plus de 500 000 NT$ : hors du système"),
    "Sans encours en septembre": ("#BBBBBB", "black", "rien à rembourser fin septembre : hors du périmètre"),
    "En incident (règle)": (STATUTS_CTX["En incident"], "white", "en incident en septembre : deux retards d'affilée en août et septembre, ou un retard grave (3 et plus) en septembre"),
    "Retard imminent (règle)": (STATUTS_CTX["Retard imminent"], "white", "un seul retard, posé par la banque en septembre après un mois d'août sain"),
    "Très haut risque": (COULEURS["rouge_pale"], "white", "score du modèle au-dessus du seuil de 10 % des défauts"),
    "Haut risque": (COULEURS["orange"], "black", "score entre les seuils de 10 % et 30 % des défauts"),
    "Risque modéré": (COULEURS["jaune"], "black", "score entre les seuils de 30 % et 60 % des défauts"),
    "Risque faible": (BLEU_INFO, "white", "score sous le seuil de 60 % des défauts"),
}
# Les deux populations confiées aux règles métier, chacune à part (statut à M, STATUT_INCIDENT)
NIVEAUX_REGLES = {"En incident": "En incident (règle)", "Retard imminent": "Retard imminent (règle)"}
# Niveaux du modèle signalés selon la part des défauts visée (clé du seuil dans bornes_niveaux.json)
SIGNALES_DEMO = {"regle_seule": [], "tres_haut_risque": ["Très haut risque"], "haut_risque": ["Très haut risque", "Haut risque"],
                 "risque_modere": ["Très haut risque", "Haut risque", "Risque modéré"]}
# Choix des démos 1 et 2 : les règles métier seules, puis les règles et le modèle à trois seuils
CHOIX_DEMO = {"Règles métier seules (sans modèle)": "regle_seule", "10 % des défauts": "tres_haut_risque",
              "30 % des défauts": "haut_risque", "60 % des défauts": "risque_modere"}

def couleur_signales(seuil_choisi):
    """Couleur du groupe « Déclarés en défaut par le modèle » : celle du dernier niveau signalé avec le seuil choisi (gris si aucun)."""
    return NIVEAUX_DEMO[SIGNALES_DEMO[seuil_choisi][-1]][0] if SIGNALES_DEMO[seuil_choisi] else COULEURS["gris"]


def mention_seuil(choix):
    """Fin de phrase de la fiche client des démos : le seuil choisi plus haut, ou le choix de la règle seule."""
    if CHOIX_DEMO[choix] == "regle_seule":
        return f"avec le choix « {choix} » fait plus haut : le modèle classe le client, mais ne déclare personne en défaut."
    return f"au seuil de {choix} (seuil choisi plus haut)."


def couleur_texte(couleur):
    """Couleur lisible sur fond blanc : les couleurs claires (jaune, gris clair, bleu pâle) sont assombries."""
    r, g, b = (int(couleur[i:i + 2], 16) for i in (1, 3, 5))
    if 0.299 * r + 0.587 * g + 0.114 * b > 150:
        r, g, b = (int(v * 0.6) for v in (r, g, b))
    return f"#{r:02X}{g:02X}{b:02X}"


def carte_chiffre(conteneur, libelle, valeur, couleur, aide=None):
    """Carte d'un chiffre (même allure que st.metric), valeur écrite à la couleur de son groupe ; aide : texte au survol."""
    titre = f" title=\"{aide}\"" if aide else ""
    conteneur.markdown(
        f"<div{titre} style='background: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); "
        f"margin-bottom: 1rem;'><div style='color: #262730; font-size: 15px;'>{libelle}</div>"
        f"<div style='color: {couleur_texte(couleur)}; font-size: 1.35rem; font-weight: 700; margin-top: 6px;'>{valeur}</div></div>",
        unsafe_allow_html=True)


COULEUR_DEFAUT = COULEURS["violet"]   # part des clients en défaut constaté, dans l'entonnoir des démos


def figure_entonnoir(etapes, hauteur):
    """Entonnoir des démos en barres centrées : au centre de chaque barre, la part des clients en défaut constaté
    (COULEUR_DEFAUT), de part et d'autre les clients pas en défaut, à la couleur de l'étape. Nombre de clients et taux de
    défaut écrits au centre de la barre. etapes : liste de (nom, clients, défauts, couleur)."""
    noms = [e[0] for e in etapes][::-1]                        # première étape en haut
    clients = [e[1] for e in etapes][::-1]
    defauts = [e[2] for e in etapes][::-1]
    couleurs = [e[3] for e in etapes][::-1]
    sains = [(n - d) / 2 for n, d in zip(clients, defauts)]  # clients pas en défaut, de chaque côté
    fig = go.Figure()
    fig.add_trace(go.Bar(y=noms, x=sains, base=[-n / 2 for n in clients], orientation="h", name="Pas en défaut",
                         marker_color=couleurs, width=0.75, hoverinfo="skip"))
    fig.add_trace(go.Bar(y=noms, x=defauts, base=[-d / 2 for d in defauts], orientation="h", name="En défaut constaté",
                         marker_color=COULEUR_DEFAUT, width=0.75, hovertemplate="%{y} : %{x} clients en défaut constaté<extra></extra>"))
    fig.add_trace(go.Bar(y=noms, x=sains, base=[d / 2 for d in defauts], orientation="h", name="Pas en défaut",
                         marker_color=couleurs, width=0.75, showlegend=False, hoverinfo="skip"))
    for nom, n, d in zip(noms, clients, defauts):
        fig.add_annotation(y=nom, x=0, showarrow=False, font=dict(size=17, color="#262730"), bgcolor="rgba(255, 255, 255, 0.8)", borderpad=3,
                           text=f"<b>{nombre_fr(n)}</b> · {nombre_fr(d / n * 100, 1)} % en défaut" if n else "<b>0</b>")
    demi = max(clients) / 2 if clients else 1
    fig.update_layout(barmode="overlay", height=hauteur, separators=", ", margin=dict(t=20, b=10, l=10, r=10),
                      xaxis=dict(visible=False, range=[-demi * 1.02, demi * 1.02]), yaxis=dict(tickfont=dict(size=17)),
                      legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5, font=dict(size=14)))
    return fig


def figure_recipient(groupes, couleur_modele, hauteur):
    """Récipient des clients déclarés en défaut (deux règles métier + signalés par le modèle), rempli par les défauts constatés :
    en bas les vrais défauts (règle de l'incident, règle du retard imminent, puis modèle), au-dessus les fausses déclarations.
    groupes : {nom: (clients, défauts)}."""
    inc_n, inc_d = groupes["En incident (règle)"]
    imm_n, imm_d = groupes["Retard imminent (règle)"]
    sig_n, sig_d = groupes["Déclarés en défaut par le modèle"]
    return figure_recipient_parts([("Vrais défauts, règle de l'incident", inc_d, NIVEAUX_DEMO["En incident (règle)"][0]),
                                   ("Vrais défauts, règle du retard imminent", imm_d, NIVEAUX_DEMO["Retard imminent (règle)"][0]),
                                   ("Vrais défauts, modèle", sig_d, couleur_modele)], inc_n + imm_n + sig_n, hauteur)

def figure_recipient_parts(vrais_defauts, declares, hauteur):
    """Récipient des clients déclarés en défaut : en bas les vrais défauts, en une ou plusieurs parts (nom, nombre, couleur),
    au-dessus les fausses déclarations ; declares : nombre de clients déclarés en défaut."""
    vrais = sum(v for _, v, _ in vrais_defauts)
    fausses = declares - vrais
    morceaux = [(nom, valeur, couleur, None, f"<b>{nombre_fr(valeur)}</b>") for nom, valeur, couleur in vrais_defauts]
    morceaux.append(("Fausses déclarations (pas en défaut)", fausses, "#E6E6E6", "/", f"<b>{nombre_fr(fausses)}</b><br>fausses déclarations"))
    fig = go.Figure()
    for nom, valeur, couleur, motif, texte in morceaux:
        # Largeur du contenu = écart entre les parois (± 0,38) : le contenu touche les bords du récipient
        fig.add_trace(go.Bar(x=[0], y=[valeur], name=nom, width=0.76,
                             marker=dict(color=couleur, line_width=0, pattern=dict(shape=motif, bgcolor="#E6E6E6", fgcolor="#B0B0B0", fgopacity=0.5, solidity=0.15) if motif else None),
                             text=[texte] if valeur else [""], textposition="inside", insidetextanchor="middle",
                             textfont=dict(size=17, color="#262730" if motif else "white"),
                             hovertemplate=f"{nom} : %{{y}}<extra></extra>"))
    # Parois du récipient (ouvert en haut), un peu plus hautes que son contenu
    haut = declares * 1.12
    for x0, y0, x1, y1 in ((-0.38, 0, -0.38, haut), (0.38, 0, 0.38, haut), (-0.38, 0, 0.38, 0)):
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color="#888888", width=5))
    fig.add_annotation(x=0, y=haut, yshift=18, showarrow=False, font=dict(size=17),
                       text=f"<b>{nombre_fr(declares)} déclarés en défaut</b><br>dont {nombre_fr(vrais / declares * 100 if declares else 0, 0)} % de vrais défauts")
    fig.update_layout(barmode="stack", height=hauteur, showlegend=True, separators=", ", margin=dict(t=70, b=10, l=10, r=10),
                      legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5, font=dict(size=14)),
                      xaxis=dict(visible=False, range=[-0.6, 0.6]), yaxis=dict(visible=False, range=[0, haut * 1.05]))
    return fig


def tableau_performance(groupes):
    """Performance d'un lot des démos : chaque règle métier, les deux règles ensemble, le modèle, le système complet (et, s'il y a
    des clients écartés avant le système, le système complet sur tout le lot). groupes : {nom du groupe: (clients, défauts constatés)}."""
    inc_n, inc_d = groupes["En incident (règle)"]
    imm_n, imm_d = groupes["Retard imminent (règle)"]
    sig_n, sig_d = groupes["Déclarés en défaut par le modèle"]
    eca_n, eca_d = groupes["Non déclarés en défaut par le modèle"]
    avant = [v for n, v in groupes.items() if n in ("Retirés par le nettoyage", "Sans encours en septembre")]
    reg_n, reg_d = inc_n + imm_n, inc_d + imm_d
    perim_n, perim_d = reg_n + sig_n + eca_n, reg_d + sig_d + eca_d

    def ligne(nom, perimetre, detectes, defauts, declares, clients):
        rappel = detectes / defauts if defauts else 0
        precision = detectes / declares if declares else 0
        f2 = 5 * precision * rappel / (4 * precision + rappel) if precision + rappel else 0
        return [f"<b>{nom}</b>", perimetre, f"{nombre_fr(detectes)} sur {nombre_fr(defauts)}", f"{nombre_fr(rappel * 100, 1)} %",
                f"{nombre_fr(precision * 100, 1)} %", f"{nombre_fr(declares / clients * 100, 1)} %" if clients else "–", nombre_fr(f2, 3)]

    lignes = [ligne("Règle de l'incident", "périmètre", inc_d, perim_d, inc_n, perim_n),
              ligne("Règle du retard imminent", "périmètre", imm_d, perim_d, imm_n, perim_n),
              ligne("Règles métier (les deux)", "périmètre", reg_d, perim_d, reg_n, perim_n),
              ligne("Modèle", "clients hors des deux populations", sig_d, sig_d + eca_d, sig_n, sig_n + eca_n),
              ligne("Système complet (règles + modèle)", "périmètre", reg_d + sig_d, perim_d, reg_n + sig_n, perim_n)]
    if avant:
        tous_n, tous_d = perim_n + sum(v[0] for v in avant), perim_d + sum(v[1] for v in avant)
        lignes.append(ligne("Système complet, sur tout le lot", "tous les clients lus (écartés avant le système : non détectés)",
                            reg_d + sig_d, tous_d, reg_n + sig_n, tous_n))
    st.markdown("**Performance sur ce lot**")
    tableau_html(["", "Clients pris en compte", "Défauts détectés", "Taux de rappel", "Précision des défauts prédits",
                  "Clients déclarés en défaut", "Score décisionnel F2"], lignes, largeurs=[20, 20, 13, 11, 13, 12, 11])
    st.caption("Taux de rappel : part des défauts constatés que l'étape déclare en défaut. Précision des défauts prédits : part des clients "
               "déclarés en défaut qui le sont vraiment dans les données. Score décisionnel F2 : combine les deux, en donnant plus de poids au rappel.")

def encadre_niveau(nom, texte):
    """Encadré d'un client (fiche des démos), à la couleur de son niveau dans le tableau des niveaux de risque."""
    encadre_couleur(NIVEAUX_DEMO[nom][0], texte)


def encadre_couleur(couleur, texte):
    """Encadré à la couleur donnée ; texte : Markdown simple (le gras **…** est traduit en HTML)."""
    html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texte)
    st.markdown(f"<div style='border-left: 8px solid {couleur}; background: {couleur}26; padding: 12px 16px; "
                f"border-radius: 6px; margin-bottom: 1rem;'>{html}</div>", unsafe_allow_html=True)


def legende_niveaux(taux, seuil_choisi):
    """Tableau coloré des niveaux de risque des démos ; taux : {niveau: taux de défaut constaté en %}, seuls ces niveaux sont affichés ;
    seuil_choisi : clé du seuil sélectionné, qui décide des niveaux signalés par le modèle."""
    def decision(nom):
        if nom in NIVEAUX_REGLES.values():
            return ("<b>prédit en défaut par la règle</b>", "background: rgba(204, 102, 119, 0.25);")
        if nom in NIVEAUX_DEMO and nom in SIGNALES_DEMO["risque_modere"] + ["Risque faible"]:
            return ("<b>déclaré en défaut par le modèle</b>", "background: rgba(204, 102, 119, 0.25);") if nom in SIGNALES_DEMO[seuil_choisi] else ("non déclaré", "")
        return ("hors du système", "")
    st.markdown("**Les niveaux de risque, avec le seuil choisi**")
    tableau_html(["Niveau", "Comment le client y arrive", "Décision", "Défaut constaté"],
                 [[(f"<b>{nom}</b>", f"background: {fond}; color: {texte};"), definition, decision(nom), f"{nombre_fr(taux[nom], 1)} %"]
                  for nom, (fond, texte, definition) in NIVEAUX_DEMO.items() if nom in taux],
                 largeurs=[26, 38, 20, 16])
    st.caption("Défaut constaté : part des clients du niveau en défaut de paiement en octobre 2005 dans les données (cible `dpnm`), sur toute la réserve de la démo. "
               "Seuils fixés sur le jeu d'entraînement.")



def entete_partie_7():
    """En-tête de la partie 7, repris sur toutes ses pages."""
    st.title("🚀 7. Le déploiement du modèle : du fichier de la banque à la décision")
    st.markdown("""
    Un modèle ne vaut que s'il sert. Cette partie met en service le système construit dans le projet, les règles métier (population en incident, retard imminent) puis le modèle, et le fait tourner **en direct**, des données jusqu'à la décision, sur des clients que le modèle n'a **jamais vus**.
    """)


def entete_partie_8():
    """En-tête de la partie 8, repris sur toutes ses pages."""
    st.title("🎯 8. Réponse à la problématique et conclusion")
    st.markdown("""
    Le projet partait d'une question : **« Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ? »** Par « informations économiques », il faut entendre deux choses absentes du dataset : la conjoncture (chômage, inflation, croissance) et les données économiques du client (revenu, autres crédits, loyer, endettement total, reste à vivre). Cette partie y répond, compare le résultat à l'étude de référence de 2009, puis en tire ce qu'il faut retenir, les limites et les recommandations.
    """)


# ==============================================================================
# GRAPHIQUE DE DÉTECTION (pages 6.4 et 8.1) : défauts détectés, précision, hasard
# ==============================================================================
def figure_detection(libelles, barres, precisions, hasard, nom_barres="Part des défauts détectés", titre_x=None, info_survol=None, y_max=100, hauteur=480,
                     en_courbes=False, etiquetes=None, axe_numerique=False,
                     etiquettes_barres_dedans=False):
    """Barres : une part en % (défauts détectés ou clients signalés) ; courbe : précision des défauts prédits ;
    ligne : précision au hasard. info_survol : (libellé, valeurs) ajouté au survol des barres.
    en_courbes : la première mesure en courbe plutôt qu'en barres (beaucoup de points) ;
    etiquetes : positions (index) des points dont la valeur est écrite, toutes par défaut ;
    axe_numerique : abscisses en nombres (parts en %, de 0 à 100) plutôt qu'en catégories ;
    etiquettes_barres_dedans : valeurs des barres écrites en haut, à l'intérieur (quand la courbe passe juste au-dessus)."""
    def textes(valeurs, gras=False):
        return [(f"<b>{nombre_fr(v, 0)} %</b>" if gras else f"{nombre_fr(v, 0)} %") if v is not None and (etiquetes is None or i in etiquetes) else ""
                for i, v in enumerate(valeurs)]
    fig = go.Figure()
    # Barres claires, étiquettes au-dessus des barres ; courbe foncée et épaisse, étiquettes au-dessus : deux mesures bien distinctes
    x_survol = "%{x} % des défauts détectés" if axe_numerique else "%{x}"
    survol = f"{x_survol}<br>{nom_barres} : %{{y:.1f}} %"
    if info_survol:
        survol += f"<br>{info_survol[0]} : %{{customdata:.1f}} %"
    if en_courbes:
        fig.add_trace(go.Scatter(x=libelles, y=barres, name=nom_barres, mode="lines+markers+text",
                                 line=dict(color=COULEURS["bleu_pale"], width=4), marker_size=5,
                                 text=textes(barres), textposition="top left", textfont=dict(size=TAILLE_ETIQUETTE),
                                 customdata=info_survol[1] if info_survol else None, hovertemplate=survol + "<extra></extra>"))
    else:
        fig.add_trace(go.Bar(x=libelles, y=barres, name=nom_barres, marker_color=COULEURS["bleu_pale"],
                             width=0.5, text=textes(barres), cliponaxis=False,
                             textposition="inside" if etiquettes_barres_dedans else "outside", insidetextanchor="end",
                             textfont=dict(size=TAILLE_ETIQUETTE), customdata=info_survol[1] if info_survol else None,
                             hovertemplate=survol + "<extra></extra>"))
    fig.add_trace(go.Scatter(x=libelles, y=precisions, name="Précision des défauts prédits", mode="lines+markers+text",
                             line=dict(color=COULEURS["vert_fonce"], width=4), marker_size=5 if en_courbes else 10,
                             text=textes(precisions, gras=True), textposition="top center",
                             textfont=dict(size=TAILLE_ETIQUETTE, color=COULEURS["vert_fonce"]),
                             hovertemplate=x_survol + "<br>Précision : %{y:.1f} %<extra></extra>"))
    # Précision d'un tirage au hasard (taux de défaut de la population) : ligne sur toute la largeur,
    # une trace vide la fait figurer dans la légende
    fig.add_hline(y=hasard, line=dict(color=COULEURS["orange"], dash="dot", width=2))
    fig.add_trace(go.Scatter(x=[None], y=[None], name=f"Au hasard ({nombre_fr(hasard, 0)} %)",
                             mode="lines", line=dict(color=COULEURS["orange"], dash="dot", width=2)))
    # Axe des abscisses en catégories : sinon Plotly lit « 30 % » comme un nombre et écarte les libellés sur deux lignes
    if axe_numerique:
        fig.update_xaxes(type="linear", range=[0, 100], dtick=10, ticksuffix=" %")
    else:
        fig.update_xaxes(type="category")
    fig.update_layout(xaxis_title=titre_x, yaxis_title="%", yaxis_range=[0, y_max], height=hauteur, separators=", ",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
    return fig

# ==============================================================================
# DÉMOS DE LA PARTIE 7 : TRAITEMENT EN DIRECT DES CLIENTS BRUTS (pages 7.3 et 7.4)
# Copies des notebooks : nettoyage en trois niveaux (src/02_01_nettoyage.ipynb), colonnes du modèle
# (lab_ML/creation_datasets_ML.ipynb). Les pages contrôlent, client par client, que le résultat reste celui du projet.
# ==============================================================================
PAY = [f"PAY_{i}" for i in range(1, 7)]
BILL = [f"BILL_AMT{i}" for i in range(1, 7)]
PAY_AMT = [f"PAY_AMT{i}" for i in range(1, 7)]


# ------------------------------------------------------------------------------
# Niveau 1 : suppressions (copie de src/02_01_nettoyage.ipynb)
# ------------------------------------------------------------------------------
def nettoyage_niveau_1(df):
    """Renvoie (clients gardés, retirés pour paiement géant, retirés comme comptes inactifs, retirés pour plafond atypique)."""
    df = df.copy()
    # Audit : catégories inconnues regroupées dans « autres »
    df["MARRIAGE"] = df["MARRIAGE"].where(df["MARRIAGE"].isin([1, 2, 3]), 3)
    df["EDUCATION"] = df["EDUCATION"].where(df["EDUCATION"].isin([1, 2, 3, 4]), 4)
    # Paiements géants (> 1 000 000) ; comptes inactifs (aucune facture positive sur 6 mois, aucun paiement de PAY_AMT1 à
    # PAY_AMT5 : PAY_AMT6 règle la facture de mars, antérieure à la période) ; plafonds de plus de 500 000 NT$
    geant = (df[PAY_AMT] > 1000000).any(axis=1)
    inactif = (df[BILL] <= 0).all(axis=1) & (df[PAY_AMT[:5]] == 0).all(axis=1)
    plafond = df["LIMIT_BAL"] > 500000
    return (df[~(geant | inactif | plafond)].copy(), df[geant], df[inactif & ~geant], df[plafond & ~geant & ~inactif])


# ------------------------------------------------------------------------------
# Niveau 2 : correction des codifications 1 (copie de src/02_01_nettoyage.ipynb ; modèles de src/02_02_modele_sorties_retard)
# ------------------------------------------------------------------------------
DECISIONS_CODIF_1 = {6783: {4: 0, 3: 0, 2: 0}, 11498: {4: 2, 3: 2, 2: 2}, 892: {3: 0, 2: 0}, 1967: {3: 0, 2: 0},
                     5645: {2: 0}, 19195: {2: 2}, 25176: {2: 2}}   # ID : {n : nouvelle valeur de PAY_n}


def _corriger_codifications_1(d):
    """Codifications 1 d'avril à août (PAY_6 à PAY_2) ; d indexé par ID."""
    d = d.copy()
    for n in range(6, 1, -1):
        for k in d.index[(d[f"PAY_{n}"] == 1) & (d[f"BILL_AMT{n - 1}"] <= 0)]:
            saines = [d.at[k, f"PAY_{j}"] for j in range(n + 1, 7) if d.at[k, f"PAY_{j}"] <= 0]
            if saines:
                d.at[k, f"PAY_{n}"] = saines[0]
    for n in range(5, 1, -1):
        regle = (d[f"PAY_{n}"] == 1) & (d[f"BILL_AMT{n}"] <= 0) & (d[f"PAY_{n + 1}"] <= 0)
        d.loc[regle, f"PAY_{n}"] = d.loc[regle, f"PAY_{n + 1}"]
    for id_client, valeurs in DECISIONS_CODIF_1.items():
        if id_client in d.index:
            for n, v in valeurs.items():
                if d.at[id_client, f"PAY_{n}"] == 1:
                    d.at[id_client, f"PAY_{n}"] = v
    return d


def _exemples_du_mois(d, n):
    """Variables des modèles de 02_02 pour le mois n, en colonnes relatives (m1 = mois précédent)."""
    bloc = pd.DataFrame(index=d.index)
    for k in range(1, 6):
        bloc[f"codif_m{k}"] = d[f"PAY_{n + k}"].mask(d[f"PAY_{n + k}"] >= 2, 2).astype(float) if n + k <= 6 else np.nan
    for k in range(0, 6):
        bloc[f"solde_m{k}"] = d[f"BILL_AMT{n + k}"] if n + k <= 6 else np.nan
        bloc[f"paiement_m{k}"] = d[f"PAY_AMT{n + k}"] if n + k <= 6 else np.nan
    bloc["LIMIT_BAL"] = d["LIMIT_BAL"]
    return bloc


@st.cache_resource
def _modeles_codification_1():
    import pickle
    dossier = BASE_DIR / "src" / "modeles_pay1"
    synthese = json.loads((dossier / "synthese.json").read_text(encoding="utf-8"))
    modeles = {}
    for nom, info in synthese["modeles"].items():
        with open(dossier / info["fichier"], "rb") as f:
            modeles[nom] = (pickle.load(f), info["seuil"])
    return synthese, modeles


def nettoyage_niveau_2(df):
    """Codifications 1 d'avril à août corrigées, puis celle de septembre : client sain en août → la codification d'août ;
    en retard en août → sortie (-1) si les trois modèles de 02_02 l'annoncent, sinon retard maintenu (2).
    La codification de la banque est gardée dans PAY_1_original. Renvoie aussi le nombre de 1 de septembre corrigés."""
    d = _corriger_codifications_1(df.set_index("ID", drop=False))
    synthese, modeles = _modeles_codification_1()
    uns = d["PAY_1"] == 1
    sains, retard = uns & (d["PAY_2"] <= 0), uns & (d["PAY_2"] >= 2)
    corrigee = d["PAY_1"].copy()
    corrigee[sains] = d.loc[sains, "PAY_2"]
    if retard.any():
        X = _exemples_du_mois(d.loc[retard], 1)[synthese["variables"]]
        voix = sum(((m.predict_proba(X)[:, 1] if hasattr(m, "predict_proba") else m.decision_function(X)) >= s).astype(int)
                   for m, s in modeles.values())
        corrigee[retard] = np.where(voix >= synthese["voix_necessaires"], -1, 2)
    d["PAY_1_original"] = d["PAY_1"]
    d["PAY_1"] = corrigee.astype(int)
    return d.reset_index(drop=True), int(uns.sum())


# ------------------------------------------------------------------------------
# Niveau 3 : uniformisation des codifications 2 d'avril à juin, puis statut à M et indicateurs de retard et d'incident
# (copie de src/02_01_nettoyage.ipynb, fonctions de 05_02_EDA_incidents)
# ------------------------------------------------------------------------------
def _uniformiser_retards(d):
    d2 = d.copy()
    for n in (6, 5, 4):   # avril, mai, juin, dans l'ordre
        facture, paiement = d2[f"BILL_AMT{n}"], d2[f"PAY_AMT{n - 1}"]
        cible = (facture > 0) & (paiement < 0.015 * facture) & d2[f"PAY_{n}"].isin([-1, 0, 1])
        if n < 6:
            cible &= d2[f"PAY_{n + 1}"].isin([-1, 0])   # client sain (hors -2) le mois précédent
        d2.loc[cible, f"PAY_{n}"] = 2
    return d2


def _statut_incident(d):
    codes = d[PAY].copy()
    niveaux = codes.values
    simple_retard_avril = (d["PAY_AMT6"] >= d["BILL_AMT5"]).values
    retard = niveaux >= 2
    passage_incident = np.zeros(len(d), bool)
    retard_regularise = np.zeros(len(d), bool)
    mois_sortie = np.full(len(d), -1.0)
    mois_regularisation = np.full(len(d), -1.0)
    for i, r in enumerate(retard):
        k = 1
        while k < 6:
            if r[k] and not r[k - 1]:
                fin = k
                while fin + 1 < 6 and r[fin + 1]:
                    fin += 1
                serie = fin > k or niveaux[i, k:fin + 1].max() >= 3
                if fin == 5 and not serie:
                    serie = not simple_retard_avril[i]   # 2 isolé en avril : incident sauf simple retard
                if serie:
                    if not passage_incident[i]:
                        mois_sortie[i] = k
                    passage_incident[i] = True
                else:
                    if not retard_regularise[i]:
                        mois_regularisation[i] = k
                    retard_regularise[i] = True
                k = fin + 1
            else:
                k += 1
    passage_incident = pd.Series(passage_incident, index=d.index)
    retard_regularise = pd.Series(retard_regularise, index=d.index)
    incident_m = ((codes["PAY_1"] >= 2) & (codes["PAY_2"] >= 2)) | (codes["PAY_1"] >= 3)
    retard_imminent = (codes["PAY_1"] >= 2) & ~incident_m
    statut = pd.Series(np.select([incident_m, retard_imminent, passage_incident, retard_regularise],
                                 ["En incident", "Retard imminent", "Sorti de l'incident", "Retard régularisé"],
                                 default="Jamais en retard"), index=d.index)
    mois_sortie = pd.Series(mois_sortie, index=d.index)
    mois_sortie[incident_m] = -1
    mois_regularisation = pd.Series(mois_regularisation, index=d.index)
    mois_regularisation[incident_m] = -1
    return pd.DataFrame({"STATUT_INCIDENT": statut, "MOIS_SORTIE_INCIDENT": mois_sortie,
                         "FLAG_INCIDENT": (passage_incident | incident_m).astype(int), "MOIS_SORTIE_RETARD": mois_regularisation,
                         "FLAG_RETARD": (retard_regularise & ~incident_m).astype(int), "FLAG_RETARD_IMMINENT": retard_imminent.astype(int)})


def _nb_mois_retard_incident(d):
    niveaux = d[PAY].values
    simple_retard_avril = (d["PAY_AMT6"] >= d["BILL_AMT5"]).values
    nb_retard = np.zeros(len(d), int)
    nb_incident = np.zeros(len(d), int)
    for i, v in enumerate(niveaux):
        r = v >= 2
        k = 0
        while k < 6:
            if r[k] and (k == 0 or not r[k - 1]):
                fin = k
                while fin + 1 < 6 and r[fin + 1]:
                    fin += 1
                serie = fin > k or v[k:fin + 1].max() >= 3
                if fin == 5 and not serie:
                    serie = not simple_retard_avril[i]
                if serie:
                    nb_incident[i] += fin - k + 1
                else:
                    nb_retard[i] += 1
                k = fin + 1
            else:
                k += 1
    return pd.Series(nb_retard, index=d.index), pd.Series(nb_incident, index=d.index)


def nettoyage_niveau_3(df):
    """Uniformisation des codifications 2 d'avril à juin, puis statut à M et indicateurs. Renvoie aussi le nombre de
    codifications passées à 2."""
    avant = df[PAY].copy()
    d = _uniformiser_retards(df)
    nb_uniformisees = int((d[PAY] != avant).values.sum())
    statuts = _statut_incident(d)
    for col in statuts.columns:
        d[col] = statuts[col]
    d["NB_MOIS_RETARD"], d["NB_MOIS_INCIDENT"] = _nb_mois_retard_incident(d)
    return d, nb_uniformisees


def nettoyage_complet(df):
    """Les trois niveaux du nettoyage, comme src/02_01_nettoyage.ipynb. Renvoie (clients gardés, retirés pour paiement géant,
    retirés comme comptes inactifs, retirés pour plafond atypique, détail des corrections)."""
    gardes, geants, inactifs, plafonds = nettoyage_niveau_1(df)
    gardes, nb_uns = nettoyage_niveau_2(gardes)
    gardes, nb_uniformisees = nettoyage_niveau_3(gardes)
    return gardes, geants, inactifs, plafonds, {"uns_septembre": nb_uns, "retards_uniformises": nb_uniformisees}


# ------------------------------------------------------------------------------
# Colonnes du modèle : copie de lab_ML/creation_datasets_ML.ipynb (celles que peut demander le modèle final)
# ------------------------------------------------------------------------------
def colonnes_du_modele(d):
    d = d.copy()
    for n in range(1, 6):
        bill = d[f"BILL_AMT{n + 1}"]
        d[f"ratio_PAY_BILL{n}"] = (d[f"PAY_AMT{n}"] / bill.where(bill > 0) * 100).clip(lower=0, upper=200).fillna(100)
    for n in range(1, 7):
        d[f"ratio_BILL_LIMIT{n}"] = np.minimum((np.maximum(d[f"BILL_AMT{n}"], 0) / d["LIMIT_BAL"]) * 100, 200)
    codifs = pd.DataFrame({n: d[f"PAY_{n}"].clip(upper=2) for n in range(1, 7)})

    def codification_habituelle(ligne):
        valeurs = ligne.dropna()
        comptes = valeurs.value_counts()
        ex_aequo = comptes[comptes == comptes.max()].index
        return next(v for v in valeurs if v in ex_aequo)

    d["PAY_habituel"] = codifs.apply(codification_habituelle, axis=1).astype(int) if len(d) else pd.Series(dtype=int)
    d["CUMUL_INCIDENT"] = (d[PAY] >= 2).sum(axis=1).astype(int)
    return d


# ------------------------------------------------------------------------------
# Règles métier : les deux populations retirées du ML, chacune à part (statut à M)
# ------------------------------------------------------------------------------
def aux_regles(d):
    """Clients confiés aux règles métier : en incident à M ou en retard imminent."""
    return d["STATUT_INCIDENT"].isin(list(NIVEAUX_REGLES))


def niveau_regle(d):
    """Niveau de règle de chaque client (« En incident (règle) », « Retard imminent (règle) »), vide pour les autres."""
    return d["STATUT_INCIDENT"].map(NIVEAUX_REGLES)

# Lecture des clients dans la base, par l'API (une ligne au format du fichier d'origine par client)
def ligne_depuis_api(fiche, historique):
    """Reconstruit la ligne d'un client au format du fichier d'origine, à partir de sa fiche et de son historique lus par l'API."""
    ligne = {"ID": fiche["client_id"], "LIMIT_BAL": fiche["plafond"], "SEX": fiche["code_genre"], "EDUCATION": fiche["code_scolaire"],
             "MARRIAGE": fiche["code_marital"], "AGE": fiche["age"]}
    # Seuls les six mois étudiés sont lus (avril à septembre 2005) : le mois m correspond à PAY_(10 - m) (septembre = 1) ;
    # les autres mois éventuels de la base sont ignorés
    mois = {10 - h["date_complexe"]["mois_num"]: h for h in historique
            if h["date_complexe"]["annee"] == 2005 and 4 <= h["date_complexe"]["mois_num"] <= 9}
    if sorted(mois) != list(range(1, 7)):
        raise ValueError(f"client {fiche['client_id']} : il manque un ou plusieurs mois d'avril à septembre 2005 dans la base")
    ligne |= {f"PAY_{n}": mois[n]["code_statut_paiement"] for n in range(1, 7)}
    ligne |= {f"BILL_AMT{n}": mois[n]["montant_encours"] for n in range(1, 7)}
    ligne |= {f"PAY_AMT{n}": mois[n]["montant_paye"] for n in range(1, 7)}
    ligne["dpnm"] = fiche["code_statut_defaut"]
    return ligne


def lire_client_api(id_client):
    """Un client : GET /client puis GET /historique_mensuel (fiche « un client à la fois »)."""
    res_client = requests.get(f"{API_URL}/client/{id_client}", timeout=API_TIMEOUT)
    res_historique = requests.get(f"{API_URL}/historique_mensuel/{id_client}", timeout=API_TIMEOUT)
    if res_client.status_code != 200 or res_historique.status_code != 200:
        raise ValueError(f"L'API a refusé la lecture du client {id_client} : "
                         f"{message_erreur_api(res_client if res_client.status_code != 200 else res_historique)}")
    return ligne_depuis_api(res_client.json(), res_historique.json()["historique"]), (res_client.json(), res_historique.json())


def lire_lot_api(ids):
    """Un lot : POST /clients/lot, un seul appel pour tous les clients (fiche et historique de chacun).
    Renvoie les lignes reconstruites, les identifiants introuvables dans la base et les clients illisibles."""
    res = requests.post(f"{API_URL}/clients/lot", json={"ids": [int(i) for i in ids]}, timeout=API_TIMEOUT)
    if res.status_code != 200:
        raise ValueError(f"L'API a refusé la lecture du lot : {message_erreur_api(res)}")
    reponse = res.json()
    lignes, illisibles = [], []
    for c in reponse["clients"]:
        try:
            lignes.append(ligne_depuis_api(c["client"], c["historique"]))
        except ValueError as e:
            illisibles.append(str(e))
    return lignes, reponse["introuvables"], illisibles


# ==============================================================================
# PARTIE 8 : LE SYSTÈME DU PROJET FACE AU MODÈLE BRUT, SUR LES MÊMES CLIENTS (pages 8.1 et 8.2)
# Clients de la démo 1 (test du ML + 20 % des deux populations des règles métier, 5 441 clients), jamais vus par aucun des deux :
# - système du projet : règles métier (en incident à M, retard imminent), puis CatBoost de ml_17 (données nettoyées de dataset_streamlit.csv) ;
# - modèle brut de la démo 3 : CatBoost sur les 23 variables d'origine, chaque client noté par le modèle de pli qui ne
#   l'a pas vu (données d'origine de clients_bruts_demo.csv, qui contient tous ces clients).
# Fichiers préparés par lab_ML/demo_ML/creation_demo_ML.ipynb et creation_demo_3.ipynb.
# ==============================================================================
@st.cache_data
def systemes_sur_clients_demo():
    """Une ligne par client : défaut constaté, règles métier, probabilité de ml_17 (hors règles métier), score du modèle brut,
    codifications d'origine. Le défaut constaté des deux fichiers est contrôlé client par client."""
    import joblib
    dossier = BASE_DIR / "lab_ML" / "demo_ML"
    liste = pd.read_csv(dossier / "clients_demo.csv")
    projet = load_data().set_index("ID").loc[liste["ID"]].reset_index()
    bruts = pd.read_csv(dossier / "clients_bruts_demo.csv", sep=";", encoding="utf-8-sig").set_index("ID").loc[liste["ID"]].reset_index()
    assert (projet["dpnm"].values == bruts["dpnm"].values).all(), "Défaut constaté différent entre les deux fichiers"

    final = joblib.load(dossier / "modele_final.joblib")
    ctx = aux_regles(projet).values
    proba = np.full(len(projet), np.nan)
    proba[~ctx] = final["modele"].predict_proba(projet.loc[~ctx, final["variables"]])[:, 1]

    brut = joblib.load(dossier / "demo_3_modeles_plis.joblib")
    pli_du_client = {i: numero for numero, ids in enumerate(brut["ids_non_vus"]) for i in ids}
    plis = bruts["ID"].map(pli_du_client)
    assert plis.notna().all(), "Des clients de la démo 1 n'ont pas de modèle de pli"
    score_brut = np.full(len(bruts), np.nan)
    for numero, modele in enumerate(brut["modeles"]):
        dans_pli = (plis == numero).values
        if dans_pli.any():
            score_brut[dans_pli] = modele.predict_proba(bruts.loc[dans_pli, brut["variables"]])[:, 1]

    sortie = pd.DataFrame({"ID": projet["ID"], "dpnm": projet["dpnm"], "regles": ctx, "proba_modele": proba, "score_brut": score_brut})
    for n in range(1, 7):
        sortie[f"PAY_{n}_origine"] = bruts[f"PAY_{n}"].values
    return sortie


def score_systeme_projet(d):
    """Score de tri du système du projet : les deux populations des règles métier en tête (au-dessus de toute probabilité),
    puis la probabilité du modèle final."""
    return np.where(d["regles"], 2.0, d["proba_modele"])


def precision_au_rappel(y, score, rappel):
    """Clients rangés du plus au moins risqué, signalés jusqu'à détecter la part de défauts voulue.
    Renvoie (précision, part des clients signalés), en %."""
    y = np.asarray(y)
    ordre = np.argsort(-np.asarray(score), kind="stable")
    cumul = np.cumsum(y[ordre])
    k = int(np.searchsorted(cumul, np.ceil(rappel / 100 * y.sum()))) + 1
    return cumul[k - 1] / k * 100, k / len(y) * 100


def aire_roc(y, score):
    """ROC AUC (probabilité qu'un défaut soit mieux classé qu'un bon client), ex aequo comptés pour moitié."""
    from sklearn.metrics import roc_auc_score
    return roc_auc_score(y, score)
