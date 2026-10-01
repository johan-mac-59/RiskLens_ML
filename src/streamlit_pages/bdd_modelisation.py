from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 2.2 : LA MODÉLISATION DE LA BASE
# ==============================================================================
entete_partie_2()

st.header("2.2 La modélisation de la base", anchor="modelisation")
st.info("Le schéma relationnel a été conçu pour éviter la redondance et assurer l'intégrité des données via des clés étrangères.")
# Si tu as l'image locale, remplace le lien ci-dessous
st.image("https://raw.githubusercontent.com/johan-mac-59/RiskLens_ML/main/images/schema_bdd__risklens.png", width="stretch")
st.caption("Représentation conceptuelle de la BDD SQLite")

st.markdown("Le schéma montre la base telle qu'elle a été conçue. Le bouton ci-dessous interroge l'API en direct (route `/tables`) et affiche les tables réellement présentes dans la base, avec leurs colonnes.")
if st.button("Afficher les tables de la base (en direct, via l'API)", type="primary"):
    try:
        res = requests.get(f"{API_URL}/tables", timeout=API_TIMEOUT)
        if res.status_code == 200:
            tables = res.json()
            for t_name, cols in tables.items():
                with st.expander(f"📁 Table : {t_name}"):
                    st.write(cols)
        else:
            st.error(message_erreur_api(res))
    except Exception as e:
        st.error(f"Erreur : {e}")
