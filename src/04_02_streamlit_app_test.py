import streamlit as st
from streamlit_pages.commun import BASE_DIR, API_URL

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
    /* Texte courant agrandi d'un point (16 -> 17 px), titres inchangés */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] td,
    [data-testid="stMarkdownContainer"] th {
        font-size: 17px;
    }
    /* Légendes (st.caption) : 14 -> 15 px */
    [data-testid="stCaptionContainer"] p {
        font-size: 15px;
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

# Pages (st.navigation) : les pages sont ajoutées au fur et à mesure de la migration
pages = {
    "": [
        st.Page("streamlit_pages/p0_accueil.py", title="Accueil & Présentation", icon=":material/home:", default=True),
    ],
    "1. Les données": [
        st.Page("streamlit_pages/p1_donnees.py", title="1. Les données : ce qu'on mesure", icon=":material/table_chart:"),
    ],
    "2. La base de données et l'API REST": [
        st.Page("streamlit_pages/bdd_chargement.py", title="2.1 Du fichier CSV à la base de données", icon=":material/upload_file:"),
        st.Page("streamlit_pages/bdd_modelisation.py", title="2.2 La modélisation de la base", icon=":material/database:"),
        st.Page("streamlit_pages/bdd_api.py", title="2.3 L'API REST", icon=":material/api:"),
        st.Page("streamlit_pages/bdd_demo.py", title="2.4 Démo de l'API : les clients et leur historique", icon=":material/terminal:"),
        st.Page("streamlit_pages/bdd_admin.py", title="2.5 L'espace administrateur", icon=":material/lock:"),
    ],
    "3. Comprendre le jeu de données : des anomalies aux règles métier": [
        st.Page("streamlit_pages/p3_1_audit.py", title="3.1 Audit : un fichier complet, mais des valeurs anormales", icon=":material/search:"),
        st.Page("streamlit_pages/p3_2_montants.py", title="3.2 Les montants : erreurs de saisie ou réalité de l'époque ?", icon=":material/payments:"),
        st.Page("streamlit_pages/p3_3_codifications.py", title="3.3 Les codifications : une étiquette de la banque, à lire avec les paiements", icon=":material/pin:"),
        st.Page("streamlit_pages/p3_4_plafonds.py", title="3.4 Les plafonds : une poignée de clients hors de la clientèle standard", icon=":material/credit_card:"),
        st.Page("streamlit_pages/p3_5_decisions.py", title="3.5 Décisions : une règle argumentée pour chaque anomalie", icon=":material/gavel:"),
    ],
    "4. Explorer le portefeuille : profils, usage de la carte, paiements et défauts": [
        st.Page("streamlit_pages/p4_1_population.py", title="4.1 Le profil des clients : des écarts de risque réels, mais modérés", icon=":material/groups:"),
        st.Page("streamlit_pages/p4_2_credit.py", title="4.2 L'usage du crédit : les clients qui utilisent le plus leur plafond sont les plus risqués", icon=":material/credit_score:"),
        st.Page("streamlit_pages/p4_3_usage_carte.py", title="4.3 Le type d'usage de la carte : plus le client rembourse, moins il fait défaut", icon=":material/payments:"),
        st.Page("streamlit_pages/p4_4_vie_comptes.py", title="4.4 La vie des comptes : les nouveaux comptes ne sont pas plus risqués", icon=":material/history:"),
        st.Page("streamlit_pages/p4_5_paiements.py", title="4.5 Les paiements : un comportement stable, alors que la dette grandit", icon=":material/account_balance_wallet:"),
        st.Page("streamlit_pages/p4_6_retards.py", title="4.6 Les retards : plus nombreux, plus graves, et plus risqués quand ils durent", icon=":material/warning:"),
    ],
    "5. La population contentieuse : des retards figés à une règle métier": [
        st.Page("streamlit_pages/p5_2_faux_retards.py", title="5.2 Chercher le contentieux révèle de faux retards, corrigés au nettoyage", icon=":material/find_replace:"),
        st.Page("streamlit_pages/p5_3_definition.py", title="5.3 La définition du contentieux : deux mois de retard d'affilée, et une sortie confirmée par les paiements", icon=":material/policy:"),
        st.Page("streamlit_pages/p5_4_comportements.py", title="5.4 Des comportements distincts, sans même regarder le défaut", icon=":material/compare_arrows:"),
    ],
}
# Menu automatique masqué : il se placerait au-dessus du logo et du titre.
# Le menu est reconstruit ci-dessous avec st.page_link, sous le logo et le titre.
page = st.navigation(pages, position="hidden")
for section, pages_section in pages.items():
    if section:
        st.sidebar.markdown(f"**{section}**")
    for p in pages_section:
        st.sidebar.page_link(p)

st.sidebar.markdown("---")
st.sidebar.info("👨‍💻 **Développé par Johan**\n\n*Futur Data Analyst*")

page.run()

# Bandeau « Ressources & Contact », affiché en bas de toutes les pages
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
