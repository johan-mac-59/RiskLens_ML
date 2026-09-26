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

df = load_data()
mappings = load_mappings()


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
# CONFIGURATION & STYLE
# ==============================================================================
st.set_page_config(
    page_title="RiskLens ML — Analyse & Prédiction du Défaut de Paiement",
    page_icon="💳",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Force un texte sombre lisible sur les cartes blanches (même en mode sombre) */
    .stMetric [data-testid="stMetricLabel"], 
    .stMetric [data-testid="stMetricValue"] {
        color: #262730 !important;
    }
    .highlight-box {
        background-color: #e1f5fe;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0288d1;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Configuration de l'URL de l'API
API_URL = "https://risklens-ml-api.onrender.com" 
# API_URL = "http://127.0.0.1:8000"  # En local

# Délai max d'attente d'une réponse API (Render peut mettre ~2 min à sortir de veille)
API_TIMEOUT = 180


# ==============================================================================
# NAVIGATION
# ==============================================================================
st.sidebar.image(str(BASE_DIR / "images" / "logo_risklens.svg"), width=250)
st.sidebar.title("🏦 RiskLens ML — Analyse & Prédiction du Défaut de Paiement 💳")
st.sidebar.markdown("---")
st.info(
    "🚧 **Interface centralisée RiskLens en cours de construction** | "
    "⏳ *Note : L'API étant sur Render, la première requête peut prendre jusqu'à 1 minute si le serveur s'est mis en veille.*"
)

menu = st.sidebar.radio(
    "🧭 Navigation",
    [
        "🏠 Accueil & Présentation",
        "📊 Analyse & Insights",
        "👤 Gestion des Clients",
        "📅 Historique Transactionnel",
        "📚 Architecture Technique",
        "🔐 Espace réservé à l'Administrateur",
        "🪣 Tests"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("👨‍💻 **Développé par Johan**\n\n*Futur Data Analyst*")

#========================================================================================
# SECTION TESTS
#========================================================================================
if menu == "🪣 Tests" :
    st.markdown("Mon bac à sable 🪣")
    
    
    st.markdown("#### Corrélation entre comptes récemment activés et risque")
    
    col_graph, col_comment = st.columns([2,1])
    # 1. Définition des cycles chronologiques
    cycles = [
        {'mois': 'Mai (M-5)', 'curr_bill': 'BILL_AMT5', 'dormant_cols': [6]},
        {'mois': 'Juin (M-4)', 'curr_bill': 'BILL_AMT4', 'dormant_cols': [6, 5]},
        {'mois': 'Juillet (M-3)', 'curr_bill': 'BILL_AMT3', 'dormant_cols': [6, 5, 4]},
        {'mois': 'Août (M-2)', 'curr_bill': 'BILL_AMT2', 'dormant_cols': [6, 5, 4, 3]},
        {'mois': 'Septembre (M-1)', 'curr_bill': 'BILL_AMT1', 'dormant_cols': [6, 5, 4, 3, 2]}
    ]

    # Calculs des réactivations et du taux de défaut
    resultats = []

    for c in cycles:
        nom_mois = c['mois']
        curr_bill = c['curr_bill']
        curr_pay = curr_bill.replace('BILL_AMT', 'PAY_AMT')
        dormant_cols = c['dormant_cols']
        
        # Masque de dormance cumulée : BILL_AMT <= 0 ET PAY_AMT == 0 sur TOUS les mois antérieurs
        mask_inactif_cumul = pd.Series(True, index=df.index)
        for m in dormant_cols:
            mask_inactif_cumul &= (df[f'BILL_AMT{m}'] <= 0) & (df[f'PAY_AMT{m}'] == 0)
        
        # Masque de sortie de sommeil au mois courant (facture > 0 OU paiement > 0)
        mask_reactivation = mask_inactif_cumul & ((df[curr_bill] > 0) | (df[curr_pay] > 0))
        nb_reactives = mask_reactivation.sum()
        
        # Calcul du taux de défaut pour cette population
        if nb_reactives > 0:
            nb_defauts = df.loc[mask_reactivation, 'dpnm'].sum()
            tx_defaut = (nb_defauts / nb_reactives) * 100
        else:
            tx_defaut = 0.0
        
        resultats.append({
            'Mois de réactivation': nom_mois,
            'Nombre de réactivations': nb_reactives,
            'Taux de défaut': tx_defaut
        })

    df_res = pd.DataFrame(resultats)

    # 2. Création du graphique Plotly avec double axe Y
    fig_defaut_dormant = make_subplots(specs=[[{"secondary_y": True}]])

    # Axe Y principal : Barres pour le nombre de réactivations
    fig_defaut_dormant.add_trace(
        go.Bar(
            x=df_res['Mois de réactivation'],
            y=df_res['Nombre de réactivations'],
            name="Activations",
            marker_color='#1f77b4',
            text=df_res['Nombre de réactivations'],
            textposition='outside',
            textfont=dict(size=15, color='black'),
            hovertemplate="<b>%{x}</b><br>Comptes réactivés : %{y}<extra></extra>"
        ),
        secondary_y=False
    )

    # Axe Y secondaire : Ligne + marqueurs pour le taux de défaut
    fig_defaut_dormant.add_trace(
        go.Scatter(
            x=df_res['Mois de réactivation'],
            y=df_res['Taux de défaut'],
            name="Taux de défaut futur (%)",
            mode='lines+markers+text',
            marker=dict(color='orange', size=10),
            line=dict(color='orange', width=2),
            text=[f"{val:.1f}%" for val in df_res['Taux de défaut']],
            textfont=dict(size=15, color='orange'),
            textposition='top center',
            hovertemplate="<b>%{x}</b><br>Taux de défaut : %{y:.2f}%<extra></extra>"
        ),
        secondary_y=True
    )

    # 3. Personnalisation de la mise en page
    max_react = df_res['Nombre de réactivations'].max()
    max_tx = df_res['Taux de défaut'].max()

    fig_defaut_dormant.update_layout(
        xaxis_title="Mois d\'activation",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        height=600
    )

    # Axe Y gauche (Effectifs)
    fig_defaut_dormant.update_yaxes(
        title_text="Nombre de comptes devenus actifs",
        range=[0, max_react * 1.2 if max_react > 0 else 10],
        showgrid=True,
        ticks='outside',      # <-- Petit trait de graduation vers l'extérieur
        secondary_y=False
    )

    # Axe Y droit (Taux de défaut)
    fig_defaut_dormant.update_yaxes(
        title_text="Taux de défaut (%)",
        title_font=dict(color="orange"),
        tickfont=dict(color="orange"),
        range=[0, max_tx * 1.3 if max_tx > 0 else 10],
        showgrid=False,
        secondary_y=True
    )

    # 4. Affichage Streamlit
    with col_graph :
        st.plotly_chart(fig_defaut_dormant, width='stretch')
    
    # 5. Commentaires
    with col_comment :
        st.markdown('')
        st.markdown('')
        st.markdown('')
        st.markdown(f"""
                    J'ai considéré comme compte devenant actif tout client ayant un encours à un mois donné, tout en ayant aucune activité de paiement ou d'utilisation de crédit sur tous les mois précédents.  
                    Le nombre d'activations de compte diminue en première période puis se stabilise. **Le taux de défaut futur ne semble pas être affecté par l'ancienneté récente d'un client.**  
                    *Pour rappel, le taux défaut moyen sur l'ensemble des clients du jeu de données est de **{round(df['dpnm'].sum()/df['dpnm'].count()*100,2)} %**.*  
                    Il m'est impossible de comparer avec une fermeture de comptes, des clients sont en effet avec des comptes gelés sur la période qu'il est difficile de mesurer avec les données à ma disposition.  
                    """)
    
    
    st.markdown('---')

    # Graphe Evolution de comptes actifs
    col_graph1, col_graph2 = st.columns([1,1])

        
    # 1. Liste des colonnes d'encours dans l'ordre chronologique
    colonnes_bill = [
        ('BILL_AMT6', 'M-6'),
        ('BILL_AMT5', 'M-5'),
        ('BILL_AMT4', 'M-4'),
        ('BILL_AMT3', 'M-3'),
        ('BILL_AMT2', 'M-2'),
        ('BILL_AMT1', 'M-1'),
    ]

    actifs_pct = {}
    actifs_counts = {}
    total_clients = len(df)

    # 2. Calcul du taux de comptes actifs (!= 0)
    for col, label in colonnes_bill:
        if col in df.columns:
            nb_actifs = (df[col] != 0).sum()
            prop = (nb_actifs / total_clients) * 100

            actifs_pct[label] = prop
            actifs_counts[label] = nb_actifs

    df_actifs = pd.DataFrame({
        'Mois': list(actifs_pct.keys()),
        'Pourcentage': list(actifs_pct.values()),
        'Nombre': list(actifs_counts.values()),
    })

    # 3. Création du graphique Plotly
    fig_actifs = go.Figure()

    # Ajout des barres avec les pourcentages au-dessus
    fig_actifs.add_trace(
        go.Bar(
            x=df_actifs['Mois'],
            y=df_actifs['Pourcentage'],
            text=[f'{val:.1f}%' for val in df_actifs['Pourcentage']],
            textposition='outside',
            textfont=dict(size=14, color='black'),
            marker_color='#1f77b4',  # Couleur bleue sobre et professionnelle
            customdata=df_actifs['Nombre'],
            hovertemplate=(
                '<b>%{x}</b><br>Comptes actifs : %{customdata:,}<br>Proportion :'
                ' %{y:.1f}%<extra></extra>'
            ),
        )
    )

    # Ajout des annotations à la verticale (n = ...) au milieu de chaque barre
    for _, row in df_actifs.iterrows():
        fig_actifs.add_annotation(
            x=row['Mois'],
            y=row['Pourcentage'] / 2,
            text=f"n = {int(row['Nombre']):,}".replace(',', ' '),
            showarrow=False,
            textangle=-90,  # Écriture à la verticale
            font=dict(color='white', size=16, family='Arial Black'),
        )

    # 4. Personnalisation du design et des axes
    fig_actifs.update_layout(
        xaxis_title='Mois',
        yaxis_title='Pourcentage de comptes actifs (%)',
        yaxis=dict(
            range=[0, 105],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
        ),
        height=500
    )

    # 5. Affichage dans Streamlit
    with col_graph1 :
        st.markdown("#### Evolution de la proportion de comptes actifs (encours non nul)")
        st.plotly_chart(fig_actifs, width='stretch')
        
        
    # 6. commentaires sur les 2 graphes
    st.markdown("""
Le nombre de compte présentant un encours (y compris négatif pour les client ayant un trop perçu) augmentent chaque mois. Le nombre de comptes présentant un encours positif (somme à devoir) augmentent également chaque mois. Le taux de clients qui paient tout ou partie de leur échéance est stable sur les 6 mois.  
Cela ne signifie pas que le taux de clients à jour est stable car un client peut présenter un paiement insuffisant pour recouvrer sa dette ou son minimum d'échéance de crédit.
                """)
    st.markdown('---')
    
    
    # Graphe Evolution du taux de clients qui présentent un paiement sur encours positif
    st.markdown("#### Evolution des ratios de paiement moyen et médian par rapport à l'encours de crédit")
    # 1. Appairage chronologique : PAY_AMTn comparé à BILL_AMT(n+1)
    paires_chronologiques = [
        ('PAY_AMT5', 'BILL_AMT6', 'M-5'),
        ('PAY_AMT4', 'BILL_AMT5', 'M-4'),
        ('PAY_AMT3', 'BILL_AMT4', 'M-3'),
        ('PAY_AMT2', 'BILL_AMT3', 'M-2'),
        ('PAY_AMT1', 'BILL_AMT2', 'M-1'),
    ]

    proportions_pct = {}
    counts_dict = {}

    # 2. Calcul du taux de paiement effectif sur encours positif
    for pay_col, bill_col, label in paires_chronologiques:
        if pay_col in df.columns and bill_col in df.columns:
            subset_avec_encours = df[df[bill_col] > 0]

            if len(subset_avec_encours) > 0:
                nb_payeurs = (subset_avec_encours[pay_col] > 0).sum()
                prop = (nb_payeurs / len(subset_avec_encours)) * 100

                proportions_pct[label] = prop
                counts_dict[label] = nb_payeurs

    df_pay = pd.DataFrame({
        'Mois': list(proportions_pct.keys()),
        'Pourcentage': list(proportions_pct.values()),
        'Nombre': list(counts_dict.values()),
    })

    # 3. Création du graphique Plotly
    fig_pay = go.Figure()

    # Barres principales avec le pourcentage au-dessus
    fig_pay.add_trace(
        go.Bar(
            x=df_pay['Mois'],
            y=df_pay['Pourcentage'],
            text=[f'{val:.1f}%' for val in df_pay['Pourcentage']],
            textposition='outside',
            textfont=dict(size=14, color='black'),
            marker_color="#2ca02c", 
            customdata=df_pay['Nombre'],
            hovertemplate=(
                '<b>%{x}</b><br>Payeurs effectifs : %{customdata:,}<br>Taux de'
                ' paiement : %{y:.1f}%<extra></extra>'
            ),
        )
    )

    # Ajout du nombre d'individus à la verticale (n = ...) au centre des barres
    for _, row in df_pay.iterrows():
        fig_pay.add_annotation(
            x=row['Mois'],
            y=row['Pourcentage'] / 2,
            text=f"n = {int(row['Nombre']):,}".replace(',', ' '),
            showarrow=False,
            textangle=-90,  # Texte affiché à la verticale
            font=dict(color='white', size=16, family='Arial Black'),
        )

    # 4. Configuration de la mise en page
    fig_pay.update_layout(
        xaxis_title='Mois',
        yaxis_title='Pourcentage de paiements effectifs (%)',
        yaxis=dict(
            range=[0, 105],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
        ),
        height=500,
    )

    # 5. Affichage dans Streamlit
    with col_graph2 :
        st.markdown("#### Evolution du taux de clients présentant un paiement sur encours positif")
        st.plotly_chart(fig_pay, width='stretch')
        
        
    # GRAPHES EVOLUTION DES RATIOS DE PAIEMENT SUR DETTE MOYEN ET MEDIAN

    col_graph1, col_graph2 = st.columns([1, 1])

    # 1. Définition des paires de colonnes et des étiquettes de M-5 à M-1
    mapping_ratios = [
        ('ratio_PAY_AMT5_to_BILL_AMT6', 'M-5'),
        ('ratio_PAY_AMT4_to_BILL_AMT5', 'M-4'),
        ('ratio_PAY_AMT3_to_BILL_AMT4', 'M-3'),
        ('ratio_PAY_AMT2_to_BILL_AMT3', 'M-2'),
        ('ratio_PAY_AMT1_to_BILL_AMT2', 'M-1'),
    ]

    # Filtrage des colonnes présentes dans le DataFrame
    colonnes_actives = [
        col for col, label in mapping_ratios if col in df.columns
    ]
    labels_x = [label for col, label in mapping_ratios if col in df.columns]

    if len(colonnes_actives) > 0:

    # =========================================================================
    # 1. GRAPHIQUE BLEU : RATIO MOYEN
    # =========================================================================
        moyennes = df[colonnes_actives].mean()

        fig_ratio = go.Figure()
        fig_ratio.add_trace(
            go.Scatter(
                x=labels_x,
                y=moyennes.values,
                mode='lines+markers+text',
                text=[f'{val:.2f}' for val in moyennes.values],
                textposition='top center',
                textfont=dict(size=14, color='black'),
                marker=dict(size=9, color='#1f77b4'),  # Bleu
                line=dict(width=2.5, color='#1f77b4'),
                hovertemplate=(
                    '<b>%{x}</b><br>Ratio de paiement moyen :'
                    ' %{y:.2f}%<extra></extra>'
                ),
            )
        )

        max_val_moy = moyennes.max()
        min_val_moy = moyennes.min()
        marge_moy = (
            (max_val_moy - min_val_moy) * 0.25 if max_val_moy != min_val_moy else 0.05
        )

        fig_ratio.update_layout(
            title=dict(
                text=(
                    '<b>Évolution du ratio moyen (Paiement / Facture'
                    ' précédente)</b>'
                ),
                font=dict(size=14),
            ),
            xaxis_title='Mois (Période relative)',
            yaxis_title='Ratio de paiement moyen (%)',
            yaxis=dict(
                range=[min_val_moy - marge_moy, max_val_moy + marge_moy],
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1,
            ),
            height=500,
        )

        with col_graph1:
            st.plotly_chart(fig_ratio, width='stretch')

        # =========================================================================
        # 2. GRAPHIQUE VIOLET : RATIO MÉDIAN
        # =========================================================================
        medianes = df[colonnes_actives].median()

        fig_medianes = go.Figure()
        fig_medianes.add_trace(
            go.Scatter(
                x=labels_x,
                y=medianes.values,
                mode='lines+markers+text',
                text=[f'{val:.2f}' for val in medianes.values],
                textposition='top center',
                textfont=dict(size=14, color='black'),
                marker=dict(size=9, color='#8e44ad'),  # Violet
                line=dict(width=2.5, color='#8e44ad'),
                hovertemplate=(
                    '<b>%{x}</b><br>Ratio de paiement médian :'
                    ' %{y:.2f}%<extra></extra>'
                ),
            )
        )

        max_val_med = medianes.max()
        min_val_med = medianes.min()
        marge_med = (
            (max_val_med - min_val_med) * 0.25 if max_val_med != min_val_med else 0.05
        )

        fig_medianes.update_layout(
            title=dict(
                text=(
                    '<b>Évolution du ratio médian (Paiement / Facture'
                    ' précédente)</b>'
                ),
                font=dict(size=14),
            ),
            xaxis_title='Mois',
            yaxis_title='Ratio de paiement médian (%)',
            yaxis=dict(
                range=[min_val_med - marge_med, max_val_med + marge_med],
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1,
            ),
            height=500,
        )

        with col_graph2:
            st.plotly_chart(fig_medianes, width='stretch')

    else:
        st.warning("Aucune des colonnes de ratios n'a été trouvée dans le dataset.")
    

# ==============================================================================
# SECTION 1 : ACCUEIL & PRÉSENTATION
# ==============================================================================
if menu == "🏠 Accueil & Présentation":
    st.title("🏦 RiskLens ML — Analyse & Prédiction du Risque Crédit 💳")
    

    st.markdown(f"""
**RiskLens ML** est une mission Data & IA complète visant à transformer des données transactionnelles historiques en un outil d'aide à la décision pour la gestion du risque crédit.
Durée prévue : 7 semaines à partir du 30 août  

Le projet suit un cycle de vie data complet : du diagnostic initial et la structuration d'une base de données relationnelle, à l'exposition des données via une API, jusqu'à la création d'un modèle prédictif et d'un dashboard décisionnel.

### 🎯 Problématique
> **"Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ?"**

L'enjeu est de déterminer si les habitudes de paiement et l'utilisation du crédit ainsi que les informations de bases d'un client sont des indicateurs suffisamment robustes pour anticiper un défaut, sans avoir accès à des données macro-économiques ou des scores de crédit externes.

Ce dataset est la base de données publique qui résulte de [l'étude scientifique de I-Cheng Yeh et Che-hui Lien (2009)](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/DefaultCreditCardClients_yeh_2009.pdf) (traduit en français [ici](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/traduction_DefaultCreditCardClients_yeh_2009.md)). Cette étude comparait plusieurs modèles pour repérer les clients à risque. Le meilleur, un réseau de neurones, obtenait un score de 0.54, ce qui correspond à un **AUC de 0.77**. L'AUC mesure la capacité d'un modèle à distinguer les bons payeurs des futurs défaillants. Mon but est de dépasser ce score.
Ma démarche adopte un prisme résolument **orienté métier**. En combinant un nettoyage rigoureux des données et un pilotage par le F1-score et le Recall, je cherche à optimiser la détection réelle des risques de défaut, garantissant ainsi une performance robuste et réellement actionnable pour la gestion des risques bancaires.


#### 🕵️‍♂️ Pour aller plus loin : Les coulisses de la donnée

Si la problématique pose le cadre quantitatif, ce dataset est né d'un séisme financier bien réel : **la crise des cartes de crédit à Taïwan en 2005** (la crise des *"Card Monsters"*).  
Pour découvrir comment des détails logistiques de l'époque (comme les règlements en espèces dans les supérettes 7-Eleven créant des décalages sur la variable `PAY_1`) ou les parallèles avec le **Buy Now, Pay Later (BNPL)** actuel éclairent ce projet d'un point de vue purement métier :
📖 [Lire le contexte du projet](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/contexte.md)
""")

    

    st.markdown("**🚀 Objectif ML Engineer :** Mon but est de dépasser le score de référence de 2009 (ratio de surface de 0.54, soit un AUC de 0.77) en optimisant le **Recall**. En banque, oublier un client à risque (Faux Négatif) coûte bien plus cher que de suspecter un client sûr (Faux Positif).")

    st.markdown("---")
    st.subheader("🛠️ Roadmap du Projet")
    cols_road = st.columns(5)
    steps = ["Audit & Cadrage", "Modélisation BDD", "Développement API", "EDA & Storytelling", "ML & Prédiction"]
    for i, step in enumerate(steps):
        cols_road[i].markdown(f"**{i+1}. {step}**")
        cols_road[i].markdown("✅" if i < 3 else "⏳")

# ==============================================================================
# SECTION 2 : ANALYSE & INSIGHTS
# ==============================================================================
elif menu == "📊 Analyse & Insights":
    st.title("📊 Analyse Exploratoire & Insights")
    st.subheader("L'analyse par segments démographiques révèle des signaux forts :")

    # Mappings métiers
    sex_map = mappings.get("genre", {})
    marriage_map = mappings.get("statut_marital", {})
    education_map = mappings.get("niveau_scolaire", {})
    
    # Dispositions en grille 2x2
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # --- 1. TRANCHE D'ÂGE ---
    with row1_col1:
        st.markdown("#### 📈 Le Risque par Tranche d'Âge")
        df_age = df.copy()

        # Binning automatique si la colonne AGE_BUCKET n'est pas pré-calculée
        if "AGE_BUCKET" not in df_age.columns and "AGE" in df_age.columns:
            # Mêmes buckets que dans 05_03_EDA_storytelling (intervalles fermés à droite : 21-25, 26-30, ...)
            age_bins = [20, 25, 30, 35, 40, 50, 80]
            age_labels = ['21-25', '26-30', '31-35', '36-40', '41-50', '51+']
            df_age["AGE_BUCKET"] = pd.cut(
                df_age["AGE"], bins=age_bins, labels=age_labels, include_lowest=True
            )

        if "AGE_BUCKET" in df_age.columns:
            rates_age = (
                df_age.groupby("AGE_BUCKET", observed=True)["dpnm"].mean() * 100
            ).reset_index()
            rates_age.columns = ["Tranche", "Taux"]

            fig_age = px.bar(
                rates_age,
                x="Tranche",
                y="Taux",
                labels={"Tranche": "Tranche d'âge", "Taux": "Taux de défaut mois suivant (%)"},
                color="Tranche",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_age.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            fig_age.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                yaxis_range=[0, max(rates_age["Taux"]) * 1.25],
                height=380,
            )
            st.plotly_chart(fig_age, width='stretch')
        else:
            st.info("Données d'âge indisponibles.")

    # --- 2. NIVEAU SCOLAIRE ---
    with row1_col2:
        st.markdown("#### 🎓 Impact du Niveau Scolaire")
        if "EDUCATION" in df.columns:
            df_edu = df[df["EDUCATION"].isin(education_map.keys())].copy()
            rates_edu = (
                df_edu.groupby("EDUCATION", observed=True)["dpnm"].mean() * 100
            ).reset_index()
            rates_edu["Niveau"] = rates_edu["EDUCATION"].map(education_map)

            fig_edu = px.bar(
                rates_edu,
                x="Niveau",
                y="dpnm",
                labels={"Niveau": "Éducation", "dpnm": "Taux de défaut mois suivant (%)"},
                color="Niveau",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_edu.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            fig_edu.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                yaxis_range=[0, max(rates_edu["dpnm"]) * 1.25],
                height=380,
            )
            st.plotly_chart(fig_edu, width='stretch')
        else:
            st.info("Données d'éducation indisponibles.")

    # --- 3. GENRE ---
    with row2_col1:
        st.markdown("#### 👫 Le Risque par Genre")
        if "SEX" in df.columns:
            df_sex = df[df["SEX"].isin(sex_map.keys())].copy()
            rates_sex = (
                df_sex.groupby("SEX", observed=True)["dpnm"].mean() * 100
            ).reset_index()
            rates_sex["Genre"] = rates_sex["SEX"].map(sex_map)

            fig_sex = px.bar(
                rates_sex,
                x="Genre",
                y="dpnm",
                labels={"Genre": "Genre", "dpnm": "Taux de défaut mois suivant (%)"},
                color="Genre",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_sex.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            fig_sex.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                yaxis_range=[0, max(rates_sex["dpnm"]) * 1.25],
                height=380,
            )
            st.plotly_chart(fig_sex, width='stretch')
        else:
            st.info("Données de genre indisponibles.")

    # --- 4. STATUT MARITAL ---
    with row2_col2:
        st.markdown("#### 💍 Impact du Statut Marital")
        if "MARRIAGE" in df.columns:
            df_mar = df[df["MARRIAGE"].isin(marriage_map.keys())].copy()
            rates_mar = (
                df_mar.groupby("MARRIAGE", observed=True)["dpnm"].mean() * 100
            ).reset_index()
            rates_mar["Statut"] = rates_mar["MARRIAGE"].map(marriage_map)

            fig_mar = px.bar(
                rates_mar,
                x="Statut",
                y="dpnm",
                labels={"Statut": "Statut", "dpnm": "Taux de défaut mois suivant (%)"},
                color="Statut",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_mar.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            fig_mar.update_layout(
                showlegend=False,
                coloraxis_showscale=False,
                yaxis_range=[0, max(rates_mar["dpnm"]) * 1.25],
                height=380,
            )
            st.plotly_chart(fig_mar, width='stretch')
        else:
            st.info("Données de mariage indisponibles.")

    st.markdown("---")
    st.subheader("🚩 Le Profil 'Critique'")
    st.warning("""
Au premier abord, les données personnelles semblaient dénués d'intéret et le [tableau de corrélation](https://raw.githubusercontent.com/johan-mac-59/RiskLens_ML/main/images/heatmap_demographique.png) ne montrait rien, mais en regardant de plus près on constate des tendances :
- Les profils jeunes, de genre masculin, mariés, avec un niveau scolaire plus faible semblent avoir un taux de défaut sensiblement supérieur au reste de la population  **
""")
    st.markdown("""
Je regarde les facteurs et je les cumule :
- Taux de défaut moyen de **28%** pour les clients âgés de 25 ans et moins, possédant un bac ou une license
- Taux de défaut moyen de **32%** pour les clients âgés de 25 ans et moins, possédant un bac ou une license, mariés
- Taux de défaut moyen de **36%** pour les clients âgés de 25 ans et moins, possédant un bac ou une license, mariés, et de sexe masculin **MAIS représente seulement 53 individus**

Si on regarde ces 4 facteurs inversés :
- Taux de défaut moyen de **16%** pour un individu de sexe féminin, célibataire, âgé de plus de 25 ans et possédant un doctorat/master, avec une **population de 3246 individus**

En conclusion, nous observons une disparité majeure de risque selon le profil : le taux de défaut peut varier de 16% à 36% selon la combinaison des facteurs démographiques. Bien que le segment à haut risque soit numériquement faible, l'écart de risque est significatif, ce qui justifie l'intégration de ces variables dans mon futur modèle de scoring.
""")
    

    # ==============================================================================
    # CALCULATEUR INTERACTIF RÉEL : TAUX DE DÉFAUT PAR PROFIL
    # ==============================================================================
    st.markdown("---")
    st.subheader("🧮 Simulateur de Risque par Profil Démographique")
    st.markdown("Vous aussi, calculez le taux de défaut de paiement selon les critères démographiques choisis en direct sur la base de données")

    col_sim1, col_sim2 = st.columns([1, 1])

    with col_sim1:
        st.info("Sélectionnez les critères du client hypothétique.")
        
        # Conversion sécurisée des clés en entiers
        genre_map = {int(k): v for k, v in mappings.get("genre", {}).items()}
        marital_map = {int(k): v for k, v in mappings.get("statut_marital", {}).items()}
        scolaire_map = {int(k): v for k, v in mappings.get("niveau_scolaire", {}).items()}
        defaut_map = {int(k): v for k, v in mappings.get("statut_defaut", {}).items()}
        
        # Choix Âge : on offre des tranches
        age_tranches = [
            ("Tous âges", 0, 100),
            ("21-25 ans", 21, 25),
            ("26-30 ans", 26, 30),
            ("31-35 ans", 31, 35),
            ("36-40 ans", 36, 40),
            ("41-50 ans", 41, 50),
            ("51-+", 51, 80)
        ]
        
        selected_tranche = st.selectbox(
            "Tranche d'âge", 
            options=[t[0] for t in age_tranches],
            format_func=lambda x: x
        )
        
        # On récupère les bornes de la tranche sélectionnée
        age_min, age_max = next((t[1], t[2]) for t in age_tranches if t[0] == selected_tranche)

        # Genre
        genre_options = [-1] + list(genre_map.keys())
        selected_genre = st.selectbox(
            "Genre", 
            options=genre_options, 
            format_func=lambda x: f"{genre_map.get(x, 'Tous les genres')} ({x})" if x != -1 else "Tous les genres"
        )

    with col_sim2:
        # Scolaire
        edu_options = [-1] + list(scolaire_map.keys())
        selected_edu = st.selectbox(
            "Niveau Scolaire", 
            options=edu_options, 
            format_func=lambda x: f"{scolaire_map.get(x, 'Tous niveaux')} ({x})" if x != -1 else "Tous niveaux"
        )

        # Mariage
        marital_options = [-1] + list(marital_map.keys())
        selected_marital = st.selectbox(
            "Statut Marital", 
            options=marital_options, 
            format_func=lambda x: f"{marital_map.get(x, 'Tous statuts')} ({x})" if x != -1 else "Tous statuts"
        )

    # Bouton de calcul
    if st.button("🔍 Calculer le taux de défaut", type="primary", width='stretch'):
        
        # Préparation des paramètres pour l'API
        params = {}
        if selected_genre != -1:
            params["gender_code"] = selected_genre
        if selected_edu != -1:
            params["education_level"] = selected_edu
        if selected_marital != -1:
            params["marital_status"] = selected_marital
        
        # Ajout des tranches d'âge
        params["age_min"] = age_min
        params["age_max"] = age_max

        try:
            with st.spinner("Interrogation de la BDD en temps réel..."):
                res = requests.get(f"{API_URL}/analyze/risk-by-profile", params=params, timeout=API_TIMEOUT)
                
                if res.status_code == 200:
                    data = res.json()
                    
                    if "error" in data:
                        st.error(f"Erreur API : {data['error']}")
                    elif data["total_clients"] == 0:
                        st.warning("Aucun client ne correspond exactement à ces critères combinés. Essayez d'élargir les tranches.")
                    else:
                        # Affichage des résultats
                        col_res1, col_res2 = st.columns(2)
                        
                        with col_res1:
                            st.metric(
                                label="Nombre de clients ciblés",
                                value=f"{data['total_clients']}"
                            )
                        
                        with col_res2:
                            risk_pct = data['default_rate_pct']
                            
                            st.metric(
                                label="Taux de défaut observé",
                                value=f"{risk_pct}%",
                                delta_color="inverse" # Rouge si haut, vert si bas
                            )
                        
                        st.info(f"Sur ces {data['total_clients']} clients, **{data['defaut_count']}** ont présenté un défaut de paiement le mois suivant.")
                        
                        # Visualisation contextuelle simple
                        if risk_pct:
                            # On ajoute une barre visuelle pour comparer à la moyenne globale de la BDD
                            global_avg = load_global_default_rate()
                            col_viz1, col_viz2 = st.columns([3, 1])
                            with col_viz1:
                                st.progress(risk_pct/100, f"Risque du profil ({risk_pct}%) vs Moyenne ({global_avg}%)")
                            with col_viz2:
                                delta_val = risk_pct - global_avg
                                st.metric(label="Écart à la moyenne", value=f"{delta_val:+.1f}%")

                else:
                    st.error(f"Impossible de joindre l'API pour le calcul. Code erreur : {res.status_code}")
                    # Afficher les détails de l'erreur si disponible
                    try:
                        error_data = res.json()
                        st.error(f"Détails de l'erreur : {error_data}")
                    except:
                        st.error("Aucun détail d'erreur disponible")

        except requests.exceptions.RequestException as e:
            st.error(f"Erreur réseau lors du calcul : {e}")
        except Exception as e:
            st.error(f"Erreur lors du calcul : {e}")
            import traceback
            st.text_area("Détails de l'erreur", value=traceback.format_exc(), height=200)
            
    
    st.markdown('---')        
    st.subheader("Analyse des plafonds de crédit, leur utilisation et leurs liens avec le défaut de paiement")
    st.markdown("#### Répartition des plafonds")

    # Histogramme complet avec Plotly
    fig1 = px.histogram(df['LIMIT_BAL'].dropna(), nbins=100, 
                        labels={'value': 'Montant du plafond (NT$)', 'count': 'Nombre de clients'})
    fig1.update_traces(marker_color='#1f77b4', marker_line_color='white', marker_line_width=0.5)
    fig1.update_layout(xaxis_title='Montant du plafond (NT$)', 
                    xaxis_range=[0, 1030000],
                    yaxis_title='Nombre de clients',
                    showlegend=False,
                    height=600)
    
    # Formatage des axes X pour afficher les nombres complets avec espaces
    fig1.update_xaxes(tickformat=',.0f', tickprefix=' ', tickangle=0)

    # Ajout des lignes de moyenne et médiane
    mean_val = df['LIMIT_BAL'].mean()
    median_val = df['LIMIT_BAL'].median()

    fig1.add_vline(x=mean_val, line_color="#ff7f0e", line_dash="dash", 
                annotation_text=f"Moyenne: {int(mean_val):,}".replace(',', ' '), 
                annotation_position="top right")

    fig1.add_vline(x=median_val, line_color="#2ca02c", line_dash="dash", 
                annotation_text=f"Médiane: {int(median_val):,}".replace(',', ' '), 
                annotation_position="top left")

    st.plotly_chart(fig1, width='stretch')
    
    st.markdown(
    rf"Le plafond moyen de crédit est de {f'{mean_val:,.0f}'.replace(',', ' ')} NT\$ et la médiane se situe à {f'{median_val:,.0f}'.replace(',', ' ')} NT\$."
    )
    total_clients = len(df)
    clients_inf_500k = len(df[df['LIMIT_BAL'] <= 500000])
    pourcentage = (clients_inf_500k / total_clients) * 100
    st.markdown(f"Sur un total de {total_clients:,} clients, {clients_inf_500k:,} clients ont un plafond de crédit ≤ 500 000 NT$ ({pourcentage:.2f}%)")
    
    
    # Histogramme du taux de dpnm par tranches de plafond
    st.markdown('---')   
    st.markdown("#### Le taux de défaut selon le montant autorisé de crédit")

    if "dpnm" in df.columns:
        bin_size = 20000
        bins = np.arange(1, 1000001 + bin_size, bin_size)
        labels = [f"{i//1000}k-{(i+bin_size)//1000}k" for i in bins[:-1]]

        df["LIMIT_BAL_interval"] = pd.cut(
            df["LIMIT_BAL"], bins=bins, labels=labels, right=False
        )

        # Calcul simultané des taux et des effectifs
        grouped = df.groupby("LIMIT_BAL_interval", observed=False)["dpnm"]
        counts = grouped.count()
        rates = grouped.mean() * 100
        rates_values = rates.fillna(0).values

        # 1. Étiquette affichée UNIQUEMENT si 0 client
        text_labels = ["0 client" if count == 0 else "" for count in counts]

        # 2. Attribution dynamique des couleurs (Vert si 0% avec clients)
        colors = []
        for count, rate in zip(counts, rates):
            if count == 0:
                colors.append("#d3d3d3")  # Gris clair (pas de client)
            elif rate == 0:
                colors.append("#2ca02c")  # Vert pour 0% de défaut
            else:
                colors.append("#ff7f0e")  # Orange pour taux > 0%

        fig3 = go.Figure(
            data=[
                go.Bar(
                    x=rates.index,
                    y=rates_values,
                    marker_color=colors,
                    marker_line_color=colors,  # Rendre le trait à 0% bien net
                    marker_line_width=2,
                    text=text_labels,
                    textposition="outside",
                    textfont=dict(size=10, color="#7f7f7f"),
                )
            ]
        )

        max_y = max(rates_values) * 1.25 if max(rates_values) > 0 else 30

        # 3. L'axe Y démarre à -1%
        fig3.update_layout(
            xaxis_title="Intervalle de montant de crédit",
            yaxis_title="Taux de défaut mois suivant(%)",
            xaxis_tickangle=-45,
            yaxis_range=[-1, max_y],
            height=600,
        )

        st.plotly_chart(fig3, width='stretch')
    else:
        st.error("Aucune colonne 'dpnm' trouvée dans le DataFrame")

    st.markdown("""
On constate un taux de défaut moyen qui a tendance à baisser jusqu'à 500 000 NT$ de crédit autorisé.  
Au-delà, le nombre de clients est trop faible pour établir une tendance, le taux de défaut oscille entre 0 et 25% avec un nombre très faible et parfois nul par tranche de plafond.
    """)
    st.markdown('---')   
    st.markdown("#### Focus sur les plafonds les plus courants")

    # Histogramme de répartition des plafond <= 500000
    df_filtered = df[df['LIMIT_BAL'] <= 500000]
    fig2 = px.histogram(df_filtered['LIMIT_BAL'].dropna(), nbins=50,
                        labels={'value': 'Montant du plafond (NT$)', 'count': 'Nombre de clients'})
    fig2.update_traces(marker_color='#1f77b4', marker_line_color='white', marker_line_width=0.5)
    fig2.update_layout(xaxis_title='Montant du plafond (NT$)',
                    yaxis_title='Nombre de clients',
                    xaxis_range=[0, 510000],
                    showlegend=False,
                    height=600)
    
    # Formatage des axes X pour afficher les nombres complets avec espaces
    fig2.update_xaxes(tickformat=',.0f', tickprefix=' ', tickangle=0)

    # Ajout des lignes de moyenne et médiane
    mean_val = df_filtered['LIMIT_BAL'].mean()
    median_val = df_filtered['LIMIT_BAL'].median()

    fig2.add_vline(x=mean_val, line_color="#ff7f0e", line_dash="dash", 
                annotation_text=f"Moyenne: {int(mean_val):,}".replace(',', ' '), 
                annotation_position="top right")

    fig2.add_vline(x=median_val, line_color="#2ca02c", line_dash="dash", 
                annotation_text=f"Médiane: {int(median_val):,}".replace(',', ' '), 
                annotation_position="top left")

    st.plotly_chart(fig2, width='stretch')

    # Histogramme du taux de dpnm par tranches de plafond <= 500000
    st.markdown('---')   
    st.markdown("#### Le taux de défaut selon le montant autorisé de crédit (≤ 500 000 NT$)")

    df_filtered = df[df['LIMIT_BAL'] <= 500000].copy()

    if 'dpnm' in df_filtered.columns:
        # Tranches de 10 000 NT$ pour garder un détail fin (50 barres)
        bin_size = 10000
        bins = np.arange(1, 500001 + bin_size, bin_size)
        labels = [f'{i//1000}k-{(i+bin_size)//1000}k' for i in bins[:-1]]

        df_filtered['LIMIT_BAL_interval'] = pd.cut(
            df_filtered['LIMIT_BAL'], bins=bins, labels=labels, right=False
        )

        # observed=False conserve toutes les tranches jusqu'à 500k, même si sans clients
        default_rates = (
            df_filtered.groupby('LIMIT_BAL_interval', observed=False)['dpnm'].mean()
            * 100
        )

        # Remplace les NaN (tranches sans clients) par 0
        rates_values = default_rates.fillna(0).values

        fig4 = go.Figure(
            data=[
                go.Bar(
                    x=default_rates.index,
                    y=rates_values,
                    marker_color='#ff7f0e'
                )
            ]
        )

        max_y = (
            max(rates_values) * 1.25
            if len(rates_values) > 0 and max(rates_values) > 0
            else 30
        )

        fig4.update_layout(
            xaxis_title='Intervalle de montant de crédit (LIMIT_BAL)',
            yaxis_title='Taux de défaut mois suivant (%)',
            xaxis_tickangle=-45,
            # Sol à -1 pour faire ressortir les barres à 0%
            yaxis_range=[-1, max_y],
            height=600,
        )

        st.plotly_chart(fig4, width='stretch')
        
    else:
        st.error("Aucune colonne 'dpnm' trouvée dans le DataFrame")
        st.write("Colonnes disponibles :", df_filtered.columns.tolist())
    
    st.markdown("La tendance baissière du risque est bien visible sur le graphique ci-dessus.")
    
    st.markdown('---')   
    st.markdown("#### Répartition du taux moyen d'utilisation du plafond")

    # Calcul de la moyenne des ratios d'utilisation pour chaque client sur les 6 mois
    ratio_plafond = [
        'ratio_BILL_LIMIT1',
        'ratio_BILL_LIMIT2',
        'ratio_BILL_LIMIT3',
        'ratio_BILL_LIMIT4',
        'ratio_BILL_LIMIT5',
        'ratio_BILL_LIMIT6',
    ]

    # Calcul de la moyenne par client sur les 6 mois
    df['mean_ratio'] = df[ratio_plafond].mean(axis=1)

    # Comptages spécifiques
    nb_clients_zero = df[df['mean_ratio'] == 0]['mean_ratio'].count()
    nb_clients_sup_120 = df[df['mean_ratio'] > 120]['mean_ratio'].count()

    # Création de l'histogramme avec Plotly
    fig_repartition_ratio_plafond = px.histogram(
        df['mean_ratio'].clip(upper=120),
        nbins=120,
        labels={
            'value': "Taux d'utilisation moyen du plafond (%)",
            'count': 'Nombre de clients',
        },
    )

    # Personnalisation du graphique
    fig_repartition_ratio_plafond.update_layout(
        xaxis_title="Taux d'utilisation moyen du plafond (%)",
        yaxis_title='Nombre de clients',
        height=600,
        showlegend=False,  # Masque la légende
    )

    fig_repartition_ratio_plafond.update_traces(
        marker_color='#1f77b4', marker_line_color='white', marker_line_width=0.5
    )

    # Affichage du graphique
    st.plotly_chart(fig_repartition_ratio_plafond, width='stretch')
    
    st.markdown(f"""
    dont :  
    - Nombre de clients avec une utilisation moyenne à 0% : {nb_clients_zero}
    - Nombre de clients avec une utilisation moyenne supérieure à 120% : {nb_clients_sup_120}          
                """)
     
    st.markdown('---')   
    st.markdown("#### Evolution du ratio d'utilisation du plafond de crédit")
    # 1. Alignement direct : du plus ancien (M-6 / ratio 6) au plus récent (M-1 / ratio 1)
    mapping = [
    ('M-6', 'ratio_BILL_LIMIT6'),
    ('M-5', 'ratio_BILL_LIMIT5'),
    ('M-4', 'ratio_BILL_LIMIT4'),
    ('M-3', 'ratio_BILL_LIMIT3'),
    ('M-2', 'ratio_BILL_LIMIT2'),
    ('M-1', 'ratio_BILL_LIMIT1')
    ]

    labels = []
    medianes_ratio_BILL_LIMIT = []

    # 2. Calcul séquentiel
    for label, col in mapping:
        if col in df.columns:
            labels.append(label)
            medianes_ratio_BILL_LIMIT.append(df[col].median())

    # 3. Tracé avec Plotly
    fig5 = go.Figure()

    # Ajout de la ligne principale
    fig5.add_trace(go.Scatter(
        x=labels,
        y=medianes_ratio_BILL_LIMIT,
        mode='lines+markers+text',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8),
        text=[f'{val:.2f}%' for val in medianes_ratio_BILL_LIMIT],
        textposition="top center",
        textfont=dict(size=14, weight='bold')
    ))

    # Configuration de l'axe Y pour avoir une échelle adaptée
    max_y = max(medianes_ratio_BILL_LIMIT) if medianes_ratio_BILL_LIMIT else 100
    min_y = min(medianes_ratio_BILL_LIMIT) if medianes_ratio_BILL_LIMIT else 0
    fig5.update_layout(
        xaxis_title='Mois',
        yaxis_title='Ratio médian d\'utilisation (%)',
        height=600,
        showlegend=False,
        yaxis=dict(
            range=[min_y*0.9, max_y * 1.1],  # Ajout d'un espace en haut
            gridcolor='lightgray',
            gridwidth=1,
            griddash='dot'  # Style de ligne pointillée pour moins de visibilité
        ),
        xaxis=dict(
            gridcolor='lightgray',
            gridwidth=1,
            griddash='dot'
        )
    )

    # Ajout de la grille
    fig5.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig5.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    st.plotly_chart(fig5, width='stretch')

    st.markdown("Hausse constante du ratio d'utilisation de crédit sur les 6 derniers mois.")
    st.markdown("Mais qui utilise le plus son crédit ?")
    
    # Taux d'utilisation médian par tranches de plafond de crédit
    st.markdown('---')   
    st.markdown("#### Taux d'utilisation médian selon le montant du plafond de crédit")

    # Filtrer les données pour les clients avec plafond <= 500000
    df_filtered = df[df['LIMIT_BAL'] <= 500000]

    # Vérifier si la colonne existe
    if 'ratio_BILL_LIMIT1' in df_filtered.columns:
        # Création des tranches de plafond
        bin_size = 10000
        bins = np.arange(1, 500002, bin_size)  # Commence à 0 au lieu de 1
        labels = [f'{i}-{i+bin_size-1}' for i in bins[:-1]]
        
        # Assigner chaque client à une tranche
        df_filtered['LIMIT_BAL_bin'] = pd.cut(df_filtered['LIMIT_BAL'], 
                                            bins=bins, labels=labels, right=False)
        
        # Calculer le taux d'utilisation médian par tranche
        usage_by_bin = df_filtered.groupby('LIMIT_BAL_bin')['ratio_BILL_LIMIT1'].median().reset_index()
        
        # Création du graphique avec Plotly
        fig6 = go.Figure(data=[go.Bar(
            x=usage_by_bin['LIMIT_BAL_bin'],
            y=usage_by_bin['ratio_BILL_LIMIT1'],
            marker_color='#9932CC'
        )])
        
        # Personnalisation du graphique
        fig6.update_layout(
            title='Taux d\'utilisation du plafond par tranches de plafond (dernier mois)',
            xaxis_title='Tranches de plafond (NT$)',
            yaxis_title='Taux d\'utilisation médian (%)',
            height=600,
            xaxis_tickangle=-45
        )
        
        # Gestion explicite des ticks pour s'assurer que tous les intervalles s'affichent
        fig6.update_xaxes(
            tickvals=list(range(len(usage_by_bin))),
            ticktext=usage_by_bin['LIMIT_BAL_bin'],
            tickangle=-45
        )
        
        st.plotly_chart(fig6, width='stretch')
        
    else:
        st.error("La colonne 'ratio_BILL_LIMIT1' n'existe pas dans le DataFrame")
        st.write("Colonnes disponibles :", df_filtered.columns.tolist())
    
    st.markdown("Sur le dernier mois, les crédits les plus petits (jusque 150 000 NT$) sont les plus utilisés en ratio.")
    st.markdown("A partir de 200 000 NT$, les utilisations deviennent très faibles")
    st.markdown("On a vu que les crédits de plus petits montants sont les plus risqués, mais est-ce la bonne variable à mettre en corrélation avec le défaut de paiement ?")
    
    st.markdown('---')   
    st.markdown("#### Taux de défaut de paiement selon l'utilisation moyenne du plafond")
    
    ratio_cols = [f"ratio_BILL_LIMIT{i}" for i in range(1, 7)]

    # Vérification de la présence des colonnes nécessaires
    if all(col in df.columns for col in ratio_cols) and "dpnm" in df.columns:
        df_ratio = df.copy()

        # Calcul du ratio moyen par client sur les 6 mois
        df_ratio["ratio_mean_client"] = df_ratio[ratio_cols].mean(axis=1)

        # Utilisation de -inf et +inf pour inclure tous les profils (ex: négatifs ou > 200%)
        bins = [-np.inf, 0.0, 10, 30, 50, 70, 90, 110, np.inf]
        labels = [
            "0%",
            ">0-10%",
            "10-30%",
            "30-50%",
            "50-70%",
            "70-90%",
            "90-110%",
            ">110%",
        ]

        df_ratio["ratio_mean_bin"] = pd.cut(
            df_ratio["ratio_mean_client"],
            bins=bins,
            labels=labels,
            include_lowest=True,
        )

        # Agrégation : effectifs et taux de défaut moyen
        stats_defaut = (
            df_ratio.groupby("ratio_mean_bin", observed=False)["dpnm"]
            .agg(nb_clients="count", taux_defaut=lambda x: x.mean() * 100)
            .reset_index()
        )

        stats_defaut["taux_defaut"] = stats_defaut["taux_defaut"].fillna(0)

        # Étiquettes personnalisées au-dessus des barres
        text_labels = [
            f"{row['taux_defaut']:.1f}%<br>(n={int(row['nb_clients'])})"
            for _, row in stats_defaut.iterrows()
        ]

        fig_defaut_ratio_plafond = go.Figure()

        fig_defaut_ratio_plafond.add_trace(
            go.Bar(
                x=stats_defaut["ratio_mean_bin"],
                y=stats_defaut["taux_defaut"],
                marker_color='#ff7f0e',
                text=text_labels,
                textposition="outside",
                textfont=dict(size=14),
            )
        )

        max_y = (
            max(stats_defaut["taux_defaut"]) * 1.25
            if max(stats_defaut["taux_defaut"]) > 0
            else 30
        )

        fig_defaut_ratio_plafond.update_layout(
            xaxis_title="Tranche d'utilisation moyenne sur 6 mois (%)",
            yaxis_title="Taux de défaut mois suivant(%)",
            height=600,
            showlegend=False,
        )

        # Affichage Streamlit adaptatif
        st.plotly_chart(fig_defaut_ratio_plafond, width='stretch')
    else:
        st.error(
        "Colonnes de ratio ou colonne cible 'dpnm' manquantes dans le DataFrame."
        ) 
    
    st.markdown("""
Malgré les nettoyages effectués sur le jeu de données, des artéfacts subsistent avec des encours nuls ou négatifs qui ressortent en paiement (ici 106 clients concernés). Il s'agit évidemment d'une donnée à ne pas prendre en compte pour regarder la tendance.  
La tendance est claire : plus un client utilise son autorisation de crédit, plus son taux de défaut augmente.  
**Le seul montant du plafond ne peut pas expliquer le risque de crédit, on voit ici que le ratio de son utilisation est également en corrélation forte avec le risque d'impayé futur.**
    """)

    st.markdown('---')
    st.subheader("🚧 Analyse du comportement de paiement en cours")



# ==============================================================================
# SECTION 3 : GESTION DES CLIENTS (GET, POST, PATCH, DELETE)
# ==============================================================================
elif menu == "👤 Gestion des Clients":
    st.subheader("👥 Espace de gestion des clients")
    
    tab_consulter, tab_ajouter, tab_modifier, tab_supprimer = st.tabs([
        "🔍 Consulter", "➕ Ajouter", "✏️ Modifier", "🗑️ Supprimer"
    ])
    
    # --- ONGLET 1 : CONSULTER (GET /client/{id}) ---
    with tab_consulter:
        st.markdown("### Fiche d'un client")
        c_id = st.number_input("ID du client à rechercher", min_value=1, value=8765, step=1, key="get_client_id")
        
        if st.button("Rechercher le client", type="primary"):
            try:
                res = requests.get(f"{API_URL}/client/{c_id}", timeout=API_TIMEOUT)
                if res.status_code == 200:
                    client_data = res.json()
                    st.success("Client trouvé !") 
                    
                    # On crée les colonnes. Le style sera appliqué via le CSS global.
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Âge", f"{client_data.get('age', 'N/A')} ans")
                    with col2:
                        st.metric("Plafond", f"{client_data.get('plafond', 'N/A')} NT$")
                    with col3:
                        statut_defaut = client_data.get('code_statut_defaut', 0)
                        st.metric("Statut Défaut", "⚠️ Risqué" if statut_defaut == 1 else "✅ Sûr")
                    
                    st.markdown("#### 📋 Détails complets")
                    df_client = pd.DataFrame([client_data])
                    st.dataframe(df_client, hide_index=True)
                else:
                    st.error("Client non trouvé dans la base de données.")
            except Exception as e:
                st.error(f"Erreur de communication : {e}")

    # --- ONGLET 2 : AJOUTER (POST /client/) ---
    with tab_ajouter:
        st.markdown("### Nouveau client")
        
        # Conversion sécurisée des clés en entiers
        genre_map = {int(k): v for k, v in mappings.get("genre", {}).items()}
        marital_map = {int(k): v for k, v in mappings.get("statut_marital", {}).items()}
        scolaire_map = {int(k): v for k, v in mappings.get("niveau_scolaire", {}).items()}
        defaut_map = {int(k): v for k, v in mappings.get("statut_defaut", {}).items()}

        with st.form("form_add_client"):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Âge", min_value=18, max_value=100, value=30)
                
                genre_options = list(genre_map.keys())
                code_genre = st.selectbox(
                    "Genre", 
                    options=genre_options, 
                    format_func=lambda x: f"{genre_map.get(x, x)} ({x})"
                )
                
                marital_options = list(marital_map.keys())
                code_marital = st.selectbox(
                    "Statut Matrimonial", 
                    options=marital_options, 
                    format_func=lambda x: f"{marital_map.get(x, x)} ({x})"
                )
                
            with col2:
                scolaire_options = list(scolaire_map.keys())
                code_scolaire = st.selectbox(
                    "Niveau Scolaire", 
                    options=scolaire_options, 
                    format_func=lambda x: f"{scolaire_map.get(x, x)} ({x})"
                )
                
                plafond = st.number_input("Plafond de crédit (NT$)", min_value=0, value=50000)
                
                defaut_options = list(defaut_map.keys())
                code_statut_defaut = st.selectbox(
                    "Statut Défaut initial", 
                    options=defaut_options, 
                    format_func=lambda x: f"{defaut_map.get(x, x)} ({x})"
                )
            
            submit_client = st.form_submit_button("Enregistrer le client", type="primary")
            
        if submit_client:
            payload_client = {
                "age": age,
                "code_genre": code_genre,
                "code_marital": code_marital,
                "code_scolaire": code_scolaire,
                "plafond": plafond,
                "code_statut_defaut": code_statut_defaut
            }
            try:
                res = requests.post(f"{API_URL}/client/", json=payload_client, timeout=API_TIMEOUT)
                if res.status_code == 200:
                    resp_json = res.json()
                    st.success(f"✅ {resp_json.get('message')} (ID attribué : **{resp_json.get('client_id')}**)")
                else:
                    st.error(f"Erreur : {message_erreur_api(res)}")
            except Exception as e:
                st.error(f"Erreur API : {e}")

    # --- ONGLET 3 : MODIFIER (PATCH /client/{id}) ---
    with tab_modifier:
        st.markdown("### Modification partielle d'un client")
        
        # --- CHARGEMENT DYNAMIQUE DES MAPPINGS DEPUIS L'API (repli sur le JSON local si l'API ne répond pas) ---
        mappings_patch = load_app_mappings() or mappings
        
        # Conversion sécurisée des clés en entiers (car le JSON convertit les clés dict en string)
        genre_map = {int(k): v for k, v in mappings_patch.get("genre", {}).items()}
        marital_map = {int(k): v for k, v in mappings_patch.get("statut_marital", {}).items()}
        scolaire_map = {int(k): v for k, v in mappings_patch.get("niveau_scolaire", {}).items()}
        defaut_map = {int(k): v for k, v in mappings_patch.get("statut_defaut", {}).items()}

        patch_id = st.number_input("ID du client à modifier", min_value=1, value=8765, step=1, key="patch_client_id")
        
        # Chargement automatique dès que l'ID change (seuls les clients trouvés sont mis en cache)
        cache_key = f"current_client_{patch_id}"
        if cache_key not in st.session_state:
            try:
                res_info = requests.get(f"{API_URL}/client/{patch_id}", timeout=API_TIMEOUT)
                if res_info.status_code == 200:
                    st.session_state[cache_key] = res_info.json()
            except Exception as e:
                st.error(f"Impossible de joindre l'API : {e}")
        
        current_data = st.session_state.get(cache_key)
        
        if not current_data:
            st.warning("⚠️ Aucun client trouvé avec cet ID dans la base de données.")
        else:
            def options_avec_valeur(map_codes, valeur):
                """Liste des codes du référentiel, complétée par la valeur en base si elle n'y figure pas."""
                options = list(map_codes.keys())
                if valeur is not None and valeur not in options:
                    options.append(valeur)
                return options

            st.info("Les champs sont pré-remplis avec les valeurs actuelles : seuls les champs modifiés seront envoyés.")

            with st.form("form_patch_client"):
                col1, col2 = st.columns(2)
                with col1:
                    new_age = st.number_input(
                        "Âge", min_value=18, max_value=120,
                        value=int(current_data["age"]), key=f"patch_age_{patch_id}"
                    )
                    
                    genre_options = options_avec_valeur(genre_map, current_data["code_genre"])
                    new_genre = st.selectbox(
                        "Genre", 
                        options=genre_options, 
                        index=genre_options.index(current_data["code_genre"]),
                        format_func=lambda x: f"{genre_map.get(x, x)} ({x})",
                        key=f"patch_genre_{patch_id}"
                    )
                    
                    marital_options = options_avec_valeur(marital_map, current_data["code_marital"])
                    new_marital = st.selectbox(
                        "Statut Matrimonial", 
                        options=marital_options, 
                        index=marital_options.index(current_data["code_marital"]),
                        format_func=lambda x: f"{marital_map.get(x, x)} ({x})",
                        key=f"patch_marital_{patch_id}"
                    )
                    
                with col2:
                    scolaire_options = options_avec_valeur(scolaire_map, current_data["code_scolaire"])
                    new_scolaire = st.selectbox(
                        "Niveau Scolaire", 
                        options=scolaire_options, 
                        index=scolaire_options.index(current_data["code_scolaire"]),
                        format_func=lambda x: f"{scolaire_map.get(x, x)} ({x})",
                        key=f"patch_scolaire_{patch_id}"
                    )
                    
                    new_plafond = st.number_input(
                        "Plafond (NT$)", min_value=0,
                        value=int(current_data["plafond"]), key=f"patch_plafond_{patch_id}"
                    )
                    
                    defaut_options = options_avec_valeur(defaut_map, current_data["code_statut_defaut"])
                    new_defaut = st.selectbox(
                        "Statut Défaut", 
                        options=defaut_options, 
                        index=defaut_options.index(current_data["code_statut_defaut"]),
                        format_func=lambda x: f"{defaut_map.get(x, x)} ({x})",
                        key=f"patch_defaut_{patch_id}"
                    )
                
                submit_patch = st.form_submit_button("Mettre à jour", type="primary")
                
            if submit_patch:
                # On n'envoie que les champs dont la valeur diffère de celle en base
                nouvelles_valeurs = {
                    "age": new_age,
                    "code_genre": new_genre,
                    "code_marital": new_marital,
                    "code_scolaire": new_scolaire,
                    "plafond": new_plafond,
                    "code_statut_defaut": new_defaut,
                }
                payload_patch = {
                    champ: valeur
                    for champ, valeur in nouvelles_valeurs.items()
                    if valeur != current_data.get(champ)
                }
                    
                if payload_patch:
                    try:
                        res = requests.patch(f"{API_URL}/client/{patch_id}", json=payload_patch, timeout=API_TIMEOUT)
                        if res.status_code == 200:
                            st.success(f"✅ {res.json().get('message')} (champs modifiés : {', '.join(payload_patch)})")
                            # On met à jour le cache avec les nouvelles valeurs
                            st.session_state[cache_key] = {**current_data, **payload_patch}
                        else:
                            st.error(f"Erreur : {message_erreur_api(res)}")
                    except Exception as e:
                        st.error(f"Erreur API : {e}")
                else:
                    st.warning("Aucune valeur n'a été modifiée.")
    # --- ONGLET 4 : SUPPRIMER (DELETE /client/{id}) ---
    with tab_supprimer:
        st.markdown("### Supprimer un client")
        st.warning("⚠️ Attention : La suppression d'un client supprime également tout son historique associé en cascade.")
        del_client_id = st.number_input("ID du client à supprimer", min_value=1, value=8765, step=1, key="del_client_id")
        
        if st.button("🗑️ Supprimer définitivement ce client", type="secondary"):
            try:
                res = requests.delete(f"{API_URL}/client/{del_client_id}", timeout=API_TIMEOUT)
                if res.status_code == 200:
                    st.success(f"✅ {res.json().get('message')}")
                else:
                    st.error(f"Erreur : {message_erreur_api(res)}")
            except Exception as e:
                st.error(f"Erreur API : {e}")

# ==============================================================================
# SECTION 4 : GESTION DE L'HISTORIQUE MENSUEL (GET, POST, PATCH, DELETE)
# ==============================================================================
elif menu == "📅 Historique Transactionnel":
    st.subheader("📊 Suivi et historique transactionnel des clients")
    
    tab_h_consulter, tab_h_ajouter, tab_h_modifier, tab_h_supprimer = st.tabs([
        "📈 Consulter l'historique", "➕ Ajouter / Enregistrer", "✏️ Modifier", "🗑️ Supprimer"
    ])
    
    # --- ONGLET 1 : CONSULTER (GET /historique_mensuel/{client_id}) ---
    with tab_h_consulter:
        st.markdown("### Historique complet d'un client")
        hist_client_id = st.number_input("ID du client", min_value=1, value=12238, step=1, key="get_hist_id")
        
        if st.button("Afficher l'historique", type="primary"):
            try:
                res = requests.get(f"{API_URL}/historique_mensuel/{hist_client_id}", timeout=API_TIMEOUT)
                if res.status_code == 200:
                    data = res.json()
                    historique_list = data.get("historique", [])
                    
                    st.success(f"Client {hist_client_id} : {data.get('nombre_lignes', 0)} mois enregistrés.")
                    
                    if historique_list:
                        df_lignes = []
                        for h in historique_list:
                            date_info = h.get("date_complexe", {})
                            df_lignes.append({
                                "Mois": date_info.get("mois_num"),
                                "Année": date_info.get("annee"),
                                "Montant Encours (NT$)": h.get("montant_encours"),
                                "Montant Payé (NT$)": h.get("montant_paye"),
                                "Statut Paiement": h.get("code_statut_paiement")
                            })
                        df_histo = pd.DataFrame(df_lignes)
                        st.dataframe(df_histo, hide_index=True)
                    else:
                        st.info("Aucun historique trouvé pour ce client.")
                else:
                    st.error("Client introuvable ou erreur de récupération.")
            except Exception as e:
                st.error(f"Erreur de communication : {e}")

    # --- ONGLET 2 : AJOUTER (POST /historique_mensuel/) ---
    with tab_h_ajouter:
        st.markdown("### Ajouter une ligne d'historique mensuel")
        with st.form("form_add_historique"):
            col1, col2 = st.columns(2)
            with col1:
                client_id = st.number_input("ID du client", min_value=1, value=12238)
                annee = st.number_input("Année", min_value=2000, max_value=2100, value=2026)
                mois = st.selectbox("Mois", options=list(range(1, 13)), format_func=lambda x: f"Mois {x}")
            with col2:
                montant_encours = st.number_input("Montant encours (NT$, négatif si trop-perçu)", value=10000)
                montant_paye = st.number_input("Montant payé (NT$)", min_value=0, value=5000)
                code_statut = st.number_input("Code statut paiement (-2 à 9)", min_value=-2, max_value=9, value=0)
                
            submit_histo = st.form_submit_button("Envoyer l'historique", type="primary")
            
        if submit_histo:
            payload_histo = {
                "client_id": client_id,
                "mois": mois,
                "annee": annee,
                "montant_encours": montant_encours,
                "montant_paye": montant_paye,
                "code_statut_paiement": code_statut
            }
            try:
                res = requests.post(f"{API_URL}/historique_mensuel/", json=payload_histo, timeout=API_TIMEOUT)
                if res.status_code == 200:
                    result_data = res.json()
                    st.success(f"✅ {result_data.get('message', 'Enregistrement réussi !')}")
                    if 'date_id_utilise' in result_data:
                        st.info(f"📅 Date ID associé : **{result_data.get('date_id_utilise')}**")
                else:
                    st.error(f"❌ Erreur : {message_erreur_api(res)}")
            except Exception as e:
                st.error(f"Erreur de communication : {e}")

    # --- ONGLET 3 : MODIFIER (PATCH /historique_mensuel/{client_id}/{mois}/{annee}) ---
    with tab_h_modifier:
        st.markdown("### Modifier un historique mensuel spécifique")

        # Sélection de la ligne hors formulaire pour pouvoir charger ses valeurs actuelles
        col1, col2, col3 = st.columns(3)
        with col1:
            p_client_id = st.number_input("ID du client", min_value=1, value=12238, key="p_h_client")
        with col2:
            p_mois = st.selectbox("Mois concerné", options=list(range(1, 13)), index=8, format_func=lambda x: f"Mois {x}", key="p_h_mois")
        with col3:
            p_annee = st.number_input("Année concernée", min_value=2000, max_value=2100, value=2005, key="p_h_annee")

        # Chargement de la ligne actuelle (seules les lignes trouvées sont mises en cache)
        histo_key = f"current_histo_{p_client_id}_{p_mois}_{p_annee}"
        if histo_key not in st.session_state:
            try:
                res_info = requests.get(f"{API_URL}/historique_mensuel/{p_client_id}/{p_mois}/{p_annee}", timeout=API_TIMEOUT)
                if res_info.status_code == 200 and res_info.json().get("found"):
                    st.session_state[histo_key] = res_info.json()
            except Exception as e:
                st.error(f"Impossible de joindre l'API : {e}")

        current_histo = st.session_state.get(histo_key)

        if not current_histo:
            st.warning("⚠️ Aucun historique trouvé pour ce client à cette date.")
        else:
            statut_map = mappings.get("statut_paiement", {})
            statut_options = list(statut_map.keys()) or list(range(-2, 10))
            statut_actuel = current_histo["code_statut_paiement"]
            if statut_actuel not in statut_options:
                statut_options.append(statut_actuel)

            st.info("Les champs sont pré-remplis avec les valeurs actuelles : seuls les champs modifiés seront envoyés.")

            with st.form("form_patch_histo"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    p_encours = st.number_input(
                        "Montant encours (NT$)",
                        value=int(current_histo["montant_encours"]), key=f"p_h_encours_{histo_key}"
                    )
                with col2:
                    p_paye = st.number_input(
                        "Montant payé (NT$)", min_value=0,
                        value=int(current_histo["montant_paye"]), key=f"p_h_paye_{histo_key}"
                    )
                with col3:
                    p_statut = st.selectbox(
                        "Code statut paiement",
                        options=statut_options,
                        index=statut_options.index(statut_actuel),
                        format_func=lambda x: f"{x} : {statut_map.get(x, '')}",
                        key=f"p_h_statut_{histo_key}"
                    )

                submit_patch_histo = st.form_submit_button("Mettre à jour la ligne", type="primary")

            if submit_patch_histo:
                # On n'envoie que les champs dont la valeur diffère de celle en base
                nouvelles_valeurs = {
                    "montant_encours": p_encours,
                    "montant_paye": p_paye,
                    "code_statut_paiement": p_statut,
                }
                payload_patch_histo = {
                    champ: valeur
                    for champ, valeur in nouvelles_valeurs.items()
                    if valeur != current_histo.get(champ)
                }

                if payload_patch_histo:
                    try:
                        res = requests.patch(f"{API_URL}/historique_mensuel/{p_client_id}/{p_mois}/{p_annee}", json=payload_patch_histo, timeout=API_TIMEOUT)
                        if res.status_code == 200:
                            st.success(f"✅ {res.json().get('message')} (champs modifiés : {', '.join(payload_patch_histo)})")
                            # On met à jour le cache avec les nouvelles valeurs
                            st.session_state[histo_key] = {**current_histo, **payload_patch_histo}
                        else:
                            st.error(f"Erreur : {message_erreur_api(res)}")
                    except Exception as e:
                        st.error(f"Erreur API : {e}")
                else:
                    st.warning("Aucune valeur n'a été modifiée.")

    # --- ONGLET 4 : SUPPRIMER (DELETE /historique_mensuel/...) ---
    with tab_h_supprimer:
        st.markdown("### Suppression d'historique")
        
        choix_del_type = st.radio("Type de suppression :", ["Supprimer un mois spécifique", "Supprimer tout l'historique d'un client"])
        
        if choix_del_type == "Supprimer un mois spécifique":
            with st.form("form_del_one_histo"):
                d_client_id = st.number_input("ID du client", min_value=1, value=12238)
                d_mois = st.selectbox("Mois", options=list(range(1, 13)), format_func=lambda x: f"Mois {x}", key="d_h_mois")
                d_annee = st.number_input("Année", min_value=2000, max_value=2100, value=2026, key="d_h_annee")
                
                sub_del_one = st.form_submit_button("Supprimer ce mois", type="secondary")
                
            if sub_del_one:
                try:
                    res = requests.delete(f"{API_URL}/historique_mensuel/{d_client_id}/{d_mois}/{d_annee}", timeout=API_TIMEOUT)
                    if res.status_code == 200:
                        st.success(f"✅ {res.json().get('message')}")
                    else:
                        st.error(f"Erreur : {message_erreur_api(res)}")
                except Exception as e:
                    st.error(f"Erreur API : {e}")
                    
        else:
            d_client_all = st.number_input("ID du client dont il faut vider l'historique", min_value=1, value=12238, key="d_all_client")
            if st.button("🗑️ Vider tout l'historique de ce client", type="secondary"):
                try:
                    res = requests.delete(f"{API_URL}/historique_mensuel/{d_client_all}", timeout=API_TIMEOUT)
                    if res.status_code == 200:
                        st.success(f"✅ {res.json().get('message')} ({res.json().get('lignes_supprimees')} lignes supprimées)")
                    else:
                        st.error(f"Erreur : {message_erreur_api(res)}")
                except Exception as e:
                    st.error(f"Erreur API : {e}")

# ==============================================================================
# SECTION 5 : ARCHITECTURE TECHNIQUE
# ==============================================================================
elif menu == "📚 Architecture Technique":
    st.title("📚 Architecture Technique & Pipeline")
    
    st.markdown("""
    Cette section détaille la structure technique du projet. L'objectif était de construire un pipeline de données robuste et découplé.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚙️ Stack Technique")
        st.markdown("""
        - **Backend :** FastAPI, Pydantic (Validation)
        - **Base de Données :** SQLite (Modélisation relationnelle normalisée)
        - **Frontend :** Streamlit (UI & DataViz)
        - **Analyse :** Pandas, Plotly, Scikit-Learn
        - **Déploiement :** Render (API) & Streamlit Cloud (UI)
        """)
        
        if st.button("Charger la structure des tables", type="primary"):
            try:
                res = requests.get(f"{API_URL}/tables", timeout=API_TIMEOUT)
                if res.status_code == 200:
                    tables = res.json()
                    for t_name, cols in tables.items():
                        with st.expander(f"📁 Table : {t_name}"):
                            st.write(cols)
            except Exception as e:
                st.error(f"Erreur : {e}")

    with col2:
        st.subheader("📐 Modèle de Données")
        st.info("Le schéma relationnel a été conçu pour éviter la redondance et assurer l'intégrité des données via des clés étrangères.")
        # Si tu as l'image locale, remplace le lien ci-dessous
        st.image("https://raw.githubusercontent.com/johan-mac-59/RiskLens_ML/main/images/schema_bdd__risklens.png", width=200)
        st.caption("Représentation conceptuelle de la BDD SQLite")

    st.markdown("---")
    st.markdown("### 🔗 Ressources & Contact")
    
    # On crée 3 colonnes pour un alignement parfait
    col_l1, col_l2, col_l3 = st.columns(3)
    
    with col_l1:
        st.markdown("<h4 style='text-align: center;'>🛠️ Technique</h4>", unsafe_allow_html=True)
        st.link_button("📖 Documentation API", f"{API_URL}/docs", width='stretch')

    with col_l2:
        st.markdown("<h4 style='text-align: center;'>💻 Code</h4>", unsafe_allow_html=True)
        st.link_button("GitHub Repository", "https://github.com/johan-mac-59/RiskLens_ML", width='stretch')
        
    with col_l3:
        st.markdown("<h4 style='text-align: center;'>🤝 Réseau</h4>", unsafe_allow_html=True)
        st.link_button("💼 Mon profil LinkedIn", "https://www.linkedin.com/in/johan-machu/", width='stretch')

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>RiskLens ML © 2026 — Projet Portfolio Data Analyst</p>", unsafe_allow_html=True)
    
    
    
# -------------------------------------------------------------
# 2. ZONE PROTEGÉE (Authentification requise)
# -------------------------------------------------------------
elif menu == "🔐 Espace réservé à l'Administrateur":
    st.subheader("🔐 Espace réservé à l'Administrateur")
    
    # CAS 1 : Non connecté -> Formulaire de connexion
    if "admin_auth" not in st.session_state:
        st.warning("🔒 L'accès à cet espace est restreint. Veuillez vous identifier.")
        
        with st.form("form_login_admin"):
            username = st.text_input("Identifiant Administrateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")

        if submit:
            if username and password:
                test_auth = (username, password)
                
                try:
                    # Envoi d'une requête GET pour tester l'accès avec les identifiants
                    res = requests.get(f"{API_URL}/admin/telecharger-db", auth=test_auth, timeout=API_TIMEOUT)
                    
                    if res.status_code == 200:
                        # Identifiants valides : on sauvegarde la session ET le fichier téléchargé
                        st.session_state["admin_auth"] = test_auth
                        st.session_state["db_content"] = res.content
                        st.success("✅ Authentification réussie !")
                        st.rerun()
                    elif res.status_code in (401, 403):
                        st.error("❌ Identifiant ou mot de passe incorrect.")
                    else:
                        st.error(f"Erreur API ({res.status_code}) : {res.text}")
                
                except Exception as e:
                    st.error(f"Impossible de joindre l'API : {e}")
            else:
                st.error("Veuillez remplir tous les champs.")

    # CAS 2 : Connecté -> Téléchargement de la BDD
    else:
        st.info("Vous êtes connecté en tant qu'administrateur.")
        
        col_info, col_logout = st.columns([4, 1])
        with col_logout:
            if st.button("🚪 Déconnexion", width='stretch'):
                del st.session_state["admin_auth"]
                st.session_state.pop("db_content", None)
                st.rerun()

        st.markdown("---")
        st.subheader("💾 Sauvegarde & Export")

        # La copie de la BDD récupérée à la connexion est réutilisée ; on peut la rafraîchir à la demande
        if st.button("🔄 Récupérer une copie à jour de la BDD"):
            auth = st.session_state["admin_auth"]

            try:
                response = requests.get(f"{API_URL}/admin/telecharger-db", auth=auth, timeout=API_TIMEOUT)

                if response.status_code == 200:
                    st.session_state["db_content"] = response.content
                    st.success("✅ Copie mise à jour !")
                else:
                    st.error(f"Erreur lors de la récupération : {response.status_code}")

            except Exception as e:
                st.error(f"Impossible de contacter l'API : {e}")

        if st.session_state.get("db_content"):
            st.download_button(
                label="💾 Enregistrer le fichier .db",
                data=st.session_state["db_content"],
                file_name="risklens_backup.db",
                mime="application/x-sqlite3"
            )