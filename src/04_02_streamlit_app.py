import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib as plt
import json
import os


# ==============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================
@st.cache_data
def load_eda_insights():
    """Charge les statistiques d'analyse calculées par le notebook."""
    try:
        # 1. On récupère le chemin du dossier où se trouve le script actuel (le dossier 'src')
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. On remonte d'un niveau vers la racine du projet, puis on entre dans 'data'
        # os.path.join est propre car il gère les '/' ou '\' selon si tu es sur Windows ou Linux
        target_path = os.path.join(current_dir, '..', 'data', 'eda_insights.json')
        
        # Debug optionnel : pour que tu puisses voir dans ta console Streamlit où il cherche
        # print(f"DEBUG: Recherche du fichier dans : {target_path}")

        if os.path.exists(target_path):
            with open(target_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            st.error(f"❌ Fichier introuvable : {target_path}")
            return None
            
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des insights : {e}")
        return None

@st.cache_data
def load_app_mappings():
    try:
        res = requests.get(f"{API_URL}/metadata/mappings")
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}
        
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

# ==============================================================================
# FONCTIONS UTILITAIRES
# ==============================================================================
@st.cache_data
def load_app_mappings():
    try:
        res = requests.get(f"{API_URL}/metadata/mappings")
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}

# ==============================================================================
# NAVIGATION
# ==============================================================================
st.sidebar.image("images/logo_risklens.svg", width=250)
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
        "📚 Architecture Technique"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("👨‍💻 **Développé par Johan**\n\n*Futur Data Analyst*")

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

Ce dataset est la base de données publique qui résulte de [l'étude scientifique de I-Cheng Yeh et Che-hui Lien (2009)](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/DefaultCreditCardClients_yeh_2009.pdf) (traduit en français [ici](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/traduction_DefaultCreditCardClients_yeh_2009.md)). Cette étude s'appuyait principalement sur l'Exactitude (Accuracy) globale. Mon but est de dépasser le score maximal de 2009 qui était de 0.54, ce qui équivaut à un **AUC de 0.77**.
Ma démarche adopte un prisme résolument **orienté métier**. En combinant un nettoyage rigoureux des données et un pilotage par le F1-score et le Recall, je cherche à optimiser la détection réelle des risques de défaut, garantissant ainsi une performance robuste et réellement actionnable pour la gestion des risques bancaires.


#### 🕵️‍♂️ Pour aller plus loin : Les coulisses de la donnée

Si la problématique pose le cadre quantitatif, ce dataset est né d'un séisme financier bien réel : **la crise des cartes de crédit à Taïwan en 2005** (la crise des *"Card Monsters"*).  
Pour découvrir comment des détails logistiques de l'époque (comme les règlements en espèces dans les supérettes 7-Eleven créant des décalages sur la variable `PAY_1`) ou les parallèles avec le **Buy Now, Pay Later (BNPL)** actuel éclairent ce projet d'un point de vue purement métier :
📖 [Lire le contexte du projet](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/contexte.md)
""")

    

    st.markdown("**🚀 Objectif ML Engineer :** Mon but est de dépasser le score d'exactitude de 2009 (AUC 0.77) en optimisant le **Recall**. En banque, oublier un client à risque (Faux Négatif) coûte bien plus cher que de suspecter un client sûr (Faux Positif).")
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown("L'analyse par segments révèle des signaux forts :")

    # 1. Chargement des vrais insights et des mappings
    insights = load_eda_insights()
    api_mappings = load_app_mappings()
    
    # 2. Préparation des mappings pour la traduction (Genre, Mariage)
    genre_map = {int(k): v for k, v in api_mappings.get("genre", {}).items()}
    marital_map = {int(k): v for k, v in api_mappings.get("statut_marital", {}).items()}
    scolaire_map = {int(k): v for k, v in api_mappings.get("niveau_scolaire", {}).items()}

    # On crée deux lignes de graphiques pour ne pas surcharger la page
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    # --- LIGNE 1 : ÂGE & ÉDUCATION ---
    with row1_col1:
        st.subheader("📈 Le Risque par Tranche d'Âge")
        if insights and 'age_risk' in insights:
            age_dict = {str(k): v * 100 for k, v in insights['age_risk'].items()}
            fig_age = px.bar(x=list(age_dict.keys()), y=list(age_dict.values()), 
                             labels={"x": "Âge", "y": "Taux (%)"}, 
                             color=list(age_dict.values()), 
                             color_continuous_scale="Viridis")
            # CORRECTION ICI : use_container_width au lieu de use_string_width
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("Données d'âge indisponibles.")

    with row1_col2:
        st.subheader("🎓 Impact du Niveau Scolaire")
        if insights and 'edu_risk' in insights:
            edu_dict = {str(k): v * 100 for k, v in insights['edu_risk'].items()}
            # Traduction des codes en labels lisibles
            edu_labels = [scolaire_map.get(int(k), k) for k in edu_dict.keys()]
            fig_edu = px.bar(x=edu_labels, y=list(edu_dict.values()), 
                             labels={"x": "Éducation", "y": "Taux (%)"}, color=list(edu_dict.values()), 
                             color_continuous_scale="Reds")
            st.plotly_chart(fig_edu, use_container_width=True)
        else:
            st.info("Données d'éducation indisponibles.")

    # --- LIGNE 2 : GENRE & MARIAGE ---
    with row2_col1:
        st.subheader("👫 Le Risque par Genre")
        if insights and 'sex_risk' in insights:
            sex_dict = {str(k): v * 100 for k, v in insights['sex_risk'].items()}
            # On traduit les codes (ex: "1") en labels (ex: "Homme")
            sex_labels = [genre_map.get(int(k), k) for k in sex_dict.keys()]
            fig_sex = px.bar(x=sex_labels, y=list(sex_dict.values()), 
                             labels={"x": "Genre", "y": "Taux (%)"}, 
                             color=list(sex_dict.values()), 
                             color_continuous_scale="magma")
            st.plotly_chart(fig_sex, use_container_width=True)
        else:
            st.info("Données de genre indisponibles.")

    with row2_col2:
        st.subheader("💍 Impact du Statut Marital")
        if insights and 'marriage_risk' in insights:
            mar_dict = {str(k): v * 100 for k, v in insights['marriage_risk'].items()}
            # On traduit les codes (ex: "1") en labels (ex: "Marié")
            mar_labels = [marital_map.get(int(k), k) for k in mar_dict.keys()]
            fig_mar = px.bar(x=mar_labels, y=list(mar_dict.values()), 
                             labels={"x": "Statut", "y": "Taux (%)"}, 
                             color=list(mar_dict.values()), 
                             color_continuous_scale="GnBu")
            st.plotly_chart(fig_mar, use_container_width=True)
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
        
        # Choix Âge : on offre des tranches
        age_tranches = [
            ("Tous âges", 0, 100),
            ("21-25 ans", 21, 25),
            ("26-30 ans", 26, 30),
            ("31-35 ans", 31, 35),
            ("36-40 ans", 36, 40),
            ("41-50 ans", 41, 50),
            ("51-60 ans", 51, 60),
            ("61+ ans", 61, 80)
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
    if st.button("🔍 Calculer le taux de défaut", type="primary", use_container_width=True):
        
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
                res = requests.get(f"{API_URL}/analyze/risk-by-profile", params=params)
                
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
                            color = "green" if risk_pct < 25 else "orange" if risk_pct < 35 else "red"
                            
                            st.metric(
                                label="Taux de défaut observé",
                                value=f"{risk_pct}%",
                                delta_color="inverse" # Rouge si haut, vert si bas
                            )
                        
                        st.info(f"Sur ces {data['total_clients']} clients, **{data['defaut_count']}** ont présenté un défaut de paiement le mois suivant.")
                        
                        # Visualisation contextuelle simple
                        if risk_pct:
                            # On ajoute une barre visuelle pour comparer à la moyenne globale (ex: 22%)
                            global_avg = 22.0 # À adapter avec ta vraie moyenne
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
    
    st.markdown("""
                  ---
                  
                #### 🚧 *Analyse exploratoire du comportement de paiement en cours*
                """)


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
                res = requests.get(f"{API_URL}/client/{c_id}")
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
                    st.dataframe(df_client, use_container_width=True, hide_index=True)
                else:
                    st.error("Client non trouvé dans la base de données.")
            except Exception as e:
                st.error(f"Erreur de communication : {e}")

    # --- ONGLET 2 : AJOUTER (POST /client/) ---
    with tab_ajouter:
        st.markdown("### Nouveau client")
        
        # --- CHARGEMENT DYNAMIQUE DES MAPPINGS DEPUIS L'API ---
        api_mappings = load_app_mappings()
        
        # Conversion sécurisée des clés en entiers
        genre_map = {int(k): v for k, v in api_mappings.get("genre", {}).items()}
        marital_map = {int(k): v for k, v in api_mappings.get("statut_marital", {}).items()}
        scolaire_map = {int(k): v for k, v in api_mappings.get("niveau_scolaire", {}).items()}
        defaut_map = {int(k): v for k, v in api_mappings.get("statut_defaut", {}).items()}

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
                res = requests.post(f"{API_URL}/client/", json=payload_client)
                if res.status_code == 200:
                    resp_json = res.json()
                    st.success(f"✅ {resp_json.get('message')} (ID attribué : **{resp_json.get('client_id')}**)")
                else:
                    st.error(f"Erreur : {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Erreur API : {e}")

    # --- ONGLET 3 : MODIFIER (PATCH /client/{id}) ---
    with tab_modifier:
        st.markdown("### Modification partielle d'un client")
        
        # --- CHARGEMENT DYNAMIQUE DES MAPPINGS DEPUIS L'API ---
        api_mappings = load_app_mappings()
        
        # Conversion sécurisée des clés en entiers (car le JSON convertit les clés dict en string)
        genre_map = {int(k): v for k, v in api_mappings.get("genre", {}).items()}
        marital_map = {int(k): v for k, v in api_mappings.get("statut_marital", {}).items()}
        scolaire_map = {int(k): v for k, v in api_mappings.get("niveau_scolaire", {}).items()}
        defaut_map = {int(k): v for k, v in api_mappings.get("statut_defaut", {}).items()}

        patch_id = st.number_input("ID du client à modifier", min_value=1, value=8765, step=1, key="patch_client_id")
        
        # Chargement automatique dès que l'ID change ou s'il n'est pas encore en cache
        cache_key = f"current_client_{patch_id}"
        if cache_key not in st.session_state:
            try:
                res_info = requests.get(f"{API_URL}/client/{patch_id}")
                if res_info.status_code == 200:
                    st.session_state[cache_key] = res_info.json()
                else:
                    st.session_state[cache_key] = None
            except Exception:
                st.session_state[cache_key] = None
        
        current_data = st.session_state.get(cache_key)
        
        # Affichage dynamique selon le résultat (avec affichage textuel propre basé sur les mappings dynamiques)
        if current_data:
            g_lib = genre_map.get(current_data.get('code_genre'), current_data.get('code_genre'))
            m_lib = marital_map.get(current_data.get('code_marital'), current_data.get('code_marital'))
            s_lib = scolaire_map.get(current_data.get('code_scolaire'), current_data.get('code_scolaire'))
            d_lib = defaut_map.get(current_data.get('code_statut_defaut'), current_data.get('code_statut_defaut'))

            st.info(
                f"✅ **Client trouvé** ➔ "
                f"Âge : {current_data.get('age')} ans | "
                f"Plafond : {current_data.get('plafond')} NT$ | "
                f"Genre : {g_lib} | "
                f"Marital : {m_lib} | "
                f"Scolaire : {s_lib} | "
                f"Défaut : {d_lib}"
            )
        else:
            st.warning("⚠️ Aucun client trouvé avec cet ID dans la base de données.")

        with st.form("form_patch_client"):
            st.info("Laissez les champs sur 'Ignorer' si vous ne souhaitez pas les modifier.")
            
            col1, col2 = st.columns(2)
            with col1:
                new_age = st.number_input("Nouvel Âge", min_value=0, value=0)
                
                genre_options = [-1] + list(genre_map.keys())
                new_genre = st.selectbox(
                    "Nouveau Genre", 
                    options=genre_options, 
                    format_func=lambda x: "Ignorer" if x == -1 else f"{genre_map.get(x, x)} ({x})"
                )
                
                marital_options = [-1] + list(marital_map.keys())
                new_marital = st.selectbox(
                    "Nouveau Statut Matrimonial", 
                    options=marital_options, 
                    format_func=lambda x: "Ignorer" if x == -1 else f"{marital_map.get(x, x)} ({x})"
                )
                
            with col2:
                scolaire_options = [-1] + list(scolaire_map.keys())
                new_scolaire = st.selectbox(
                    "Nouveau Niveau Scolaire", 
                    options=scolaire_options, 
                    format_func=lambda x: "Ignorer" if x == -1 else f"{scolaire_map.get(x, x)} ({x})"
                )
                
                new_plafond = st.number_input("Nouveau Plafond", min_value=0, value=0)
                
                defaut_options = [-1] + list(defaut_map.keys())
                new_defaut = st.selectbox(
                    "Nouveau Statut Défaut", 
                    options=defaut_options, 
                    format_func=lambda x: "Ignorer" if x == -1 else f"{defaut_map.get(x, x)} ({x})"
                )
            
            submit_patch = st.form_submit_button("Mettre à jour", type="primary")
            
        if submit_patch:
            payload_patch = {}
            if new_age > 0:
                payload_patch["age"] = new_age
            if new_genre != -1:
                payload_patch["code_genre"] = new_genre
            if new_marital != -1:
                payload_patch["code_marital"] = new_marital
            if new_scolaire != -1:
                payload_patch["code_scolaire"] = new_scolaire
            if new_plafond > 0:
                payload_patch["plafond"] = new_plafond
            if new_defaut != -1:
                payload_patch["code_statut_defaut"] = new_defaut
                
            if payload_patch:
                try:
                    res = requests.patch(f"{API_URL}/client/{patch_id}", json=payload_patch)
                    if res.status_code == 200:
                        st.success(f"✅ {res.json().get('message')}")
                        # On supprime le cache pour forcer un rechargement frais des nouvelles données
                        if cache_key in st.session_state:
                            del st.session_state[cache_key]
                    else:
                        st.error(f"Erreur : {res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Erreur API : {e}")
            else:
                st.warning("Aucun champ valide sélectionné pour la modification.")
    # --- ONGLET 4 : SUPPRIMER (DELETE /client/{id}) ---
    with tab_supprimer:
        st.markdown("### Supprimer un client")
        st.warning("⚠️ Attention : La suppression d'un client supprime également tout son historique associé en cascade.")
        del_client_id = st.number_input("ID du client à supprimer", min_value=1, value=8765, step=1, key="del_client_id")
        
        if st.button("🗑️ Supprimer définitivement ce client", type="secondary"):
            try:
                res = requests.delete(f"{API_URL}/client/{del_client_id}")
                if res.status_code == 200:
                    st.success(f"✅ {res.json().get('message')}")
                else:
                    st.error(f"Erreur : {res.json().get('detail')}")
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
        
        if st.button("Affirmer l'historique", type="primary"):
            try:
                res = requests.get(f"{API_URL}/historique_mensuel/{hist_client_id}")
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
                        st.dataframe(df_histo, use_container_width=True, hide_index=True)
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
                montant_encours = st.number_input("Montant encours (NT$)", min_value=0, value=10000)
                montant_paye = st.number_input("Montant payé (NT$)", min_value=0, value=5000)
                code_statut = st.number_input("Code statut paiement", value=0)
                
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
                res = requests.post(f"{API_URL}/historique_mensuel/", json=payload_histo)
                if res.status_code == 200:
                    result_data = res.json()
                    st.success(f"✅ {result_data.get('message', 'Enregistrement réussi !')}")
                    if 'date_id_utilise' in result_data:
                        st.info(f"📅 Date ID associé : **{result_data.get('date_id_utilise')}**")
                else:
                    st.error(f"❌ Erreur : {res.json().get('detail')}")
            except Exception as e:
                st.error(f"Erreur de communication : {e}")

    # --- ONGLET 3 : MODIFIER (PATCH /historique_mensuel/{client_id}/{mois}/{annee}) ---
    with tab_h_modifier:
        st.markdown("### Modifier un historique mensuel spécifique")
        with st.form("form_patch_histo"):
            col1, col2 = st.columns(2)
            with col1:
                p_client_id = st.number_input("ID du client", min_value=1, value=12238, key="p_h_client")
                p_mois = st.selectbox("Mois concerné", options=list(range(1, 13)), format_func=lambda x: f"Mois {x}", key="p_h_mois")
            with col2:
                p_annee = st.number_input("Année concernée", min_value=2000, max_value=2100, value=2026, key="p_h_annee")
                p_statut = st.number_input("Nouveau code statut (laisser -1 pour ignorer)", value=-1)
            
            p_encours = st.number_input("Nouveau montant encours (-1 pour ignorer)", value=-1)
            p_paye = st.number_input("Nouveau montant payé (-1 pour ignorer)", value=-1)
            
            submit_patch_histo = st.form_submit_button("Mettre à jour la ligne", type="primary")
            
        if submit_patch_histo:
            payload_patch_histo = {}
            if p_encours >= 0:
                payload_patch_histo["montant_encours"] = p_encours
            if p_paye >= 0:
                payload_patch_histo["montant_paye"] = p_paye
            if p_statut >= -1 and p_statut != -1:
                payload_patch_histo["code_statut_paiement"] = p_statut
                
            if payload_patch_histo:
                try:
                    res = requests.patch(f"{API_URL}/historique_mensuel/{p_client_id}/{p_mois}/{p_annee}", json=payload_patch_histo)
                    if res.status_code == 200:
                        st.success(f"✅ {res.json().get('message')}")
                    else:
                        st.error(f"Erreur : {res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Erreur API : {e}")
            else:
                st.warning("Aucune modification renseignée.")

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
                    res = requests.delete(f"{API_URL}/historique_mensuel/{d_client_id}/{d_mois}/{d_annee}")
                    if res.status_code == 200:
                        st.success(f"✅ {res.json().get('message')}")
                    else:
                        st.error(f"Erreur : {res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Erreur API : {e}")
                    
        else:
            d_client_all = st.number_input("ID du client dont il faut vider l'historique", min_value=1, value=12238, key="d_all_client")
            if st.button("🗑️ Vider tout l'historique de ce client", type="secondary"):
                try:
                    res = requests.delete(f"{API_URL}/historique_mensuel/client/{d_client_all}")
                    if res.status_code == 200:
                        st.success(f"✅ {res.json().get('message')} ({res.json().get('lignes_supprimees')} lignes supprimées)")
                    else:
                        st.error(f"Erreur : {res.json().get('detail')}")
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
                res = requests.get(f"{API_URL}/tables")
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
        st.markdown("#### 🛠️ Technique")
        st.link_button("📖 Documentation API", f"{API_URL}/docs", use_container_width=True)
    
    with col_l2:
        st.markdown("#### 💻 Code")
        st.link_button("GitHub Repository", "https://github.com/johan-mac-59/RiskLens_ML", use_container_width=True)
        
    with col_l3:
        st.markdown("#### 🤝 Réseau")
        st.link_button("💼 Mon profil LinkedIn", "https://www.linkedin.com/in/johan-machu/", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>RiskLens ML © 2024 — Projet Portfolio Data Analyst</p>", unsafe_allow_html=True)