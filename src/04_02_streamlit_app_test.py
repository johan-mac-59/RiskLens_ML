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
    "La base de données et l'API": [
        st.Page("streamlit_pages/bdd_architecture.py", title="Architecture et API", icon=":material/database:"),
        st.Page("streamlit_pages/bdd_demo.py", title="Démo de l'API", icon=":material/terminal:"),
        st.Page("streamlit_pages/bdd_admin.py", title="Espace administrateur", icon=":material/lock:"),
    ],
    "3. Comprendre le jeu de données : des anomalies aux règles métier": [
        st.Page("streamlit_pages/p3_1_audit.py", title="3.1 Audit : un fichier complet, mais des valeurs anormales", icon=":material/search:"),
        st.Page("streamlit_pages/p3_2_montants.py", title="3.2 Les montants : erreurs de saisie ou réalité de l'époque ?", icon=":material/payments:"),
    ],
    "Analyse exploratoire": [
        st.Page("streamlit_pages/analyses_actuelles.py", title="Analyses (version actuelle)", icon=":material/bar_chart:"),
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
