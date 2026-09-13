import streamlit as st
import requests
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="RiskLens - Credit Card Dashboard",
    page_icon="💳",
    layout="wide"
)

# Configuration de l'URL de l'API (En ligne sur Render ou Local)
API_URL = "https://risklens-ml-api.onrender.com"  
# API_URL = "http://127.0.0.1:8000"  # En local

st.title("🏦 RiskLens ML — Analyse & Prédiction du Défaut de Paiement 💳")

st.info(
    "🚧 **Interface centralisée RiskLens en cours de construction** | "
    "⏳ *Note : L'API étant sur Render, la première requête peut prendre jusqu'à 1 minute si le serveur s'est mis en veille.*"
)

# Barre latérale de navigation globale
st.sidebar.header("🧭 Navigation")
menu = st.sidebar.selectbox(
    "Section :",
    [
        "🏠 Accueil & Schéma BDD",
        "👤 Gestion des Clients",
        "📅 Gestion de l'Historique Mensuel"
    ]
)

# ==============================================================================
# SECTION 1 : ACCUEIL & SCHEMA BDD (Route GET /tables)
# ==============================================================================
if menu == "🏠 Accueil & Schéma BDD":
    st.subheader("📚 Structure et tables de la base de données")
    st.markdown("Visualisez ci-dessous les tables exposées par l'API et leurs colonnes respectives.")

    if st.button("Charger la structure de la BDD", type="primary"):
        try:
            response = requests.get(f"{API_URL}/tables")
            if response.status_code == 200:
                tables_info = response.json()
                
                for table_name, columns in tables_info.items():
                    with st.expander(f"📁 Table : `{table_name}` ({len(columns)} colonnes)"):
                        df_cols = pd.DataFrame({"Colonnes": columns})
                        st.dataframe(df_cols, use_container_width=True, hide_index=True)
            else:
                st.error(f"Erreur {response.status_code} lors de la récupération des tables.")
        except Exception as e:
            st.error(f"Impossible de joindre l'API : {e}")

# ==============================================================================
# SECTION 2 : GESTION DES CLIENTS (GET, POST, PATCH, DELETE)
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
                    
                    # Affichage propre sous forme de métriques et tableau stylé
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
        with st.form("form_add_client"):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Âge", min_value=18, max_value=100, value=30)
                code_genre = st.selectbox("Genre", options=[1, 2], format_func=lambda x: "Homme (1)" if x == 1 else "Femme (2)")
                code_marital = st.selectbox("Statut Matrimonial", options=[1, 2, 3], format_func=lambda x: {1: "Marié(e) (1)", 2: "Célibataire (2)", 3: "Autre (3)"}[x])
            with col2:
                code_scolaire = st.selectbox("Niveau Scolaire", options=[1, 2, 3, 4], format_func=lambda x: {1: "Doctorat/Master (1)", 2: "Licence (2)", 3: "Baccalauréat (3)", 4: "Autre (4)"}[x])
                plafond = st.number_input("Plafond de crédit (NT$)", min_value=0, value=50000)
                code_statut_defaut = st.selectbox("Statut Défaut initial", options=[0, 1], format_func=lambda x: "Paiement à jour (0)" if x == 0 else "Défaut (1)")
            
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
        patch_id = st.number_input("ID du client à modifier", min_value=1, value=8765, step=1, key="patch_client_id")
        
        with st.form("form_patch_client"):
            st.info("Laissez les champs sur leur valeur par défaut ou vide si vous ne souhaitez pas les modifier.")
            new_plafond = st.number_input("Nouveau Plafond (laisser à 0 pour ignorer)", min_value=0, value=0)
            new_age = st.number_input("Nouvel Âge (laisser à 0 pour ignorer)", min_value=0, value=0)
            new_defaut = st.selectbox("Nouveau Statut Défaut (-1 pour ignorer)", options=[-1, 0, 1], format_func=lambda x: "Ignorer" if x == -1 else str(x))
            
            submit_patch = st.form_submit_button("Mettre à jour", type="primary")
            
        if submit_patch:
            payload_patch = {}
            if new_plafond > 0:
                payload_patch["plafond"] = new_plafond
            if new_age > 0:
                payload_patch["age"] = new_age
            if new_defaut != -1:
                payload_patch["code_statut_defaut"] = new_defaut
                
            if payload_patch:
                try:
                    res = requests.patch(f"{API_URL}/client/{patch_id}", json=payload_patch)
                    if res.status_code == 200:
                        st.success(f"✅ {res.json().get('message')}")
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
# SECTION 3 : GESTION DE L'HISTORIQUE MENSUEL (GET, POST, PATCH, DELETE)
# ==============================================================================
elif menu == "📅 Gestion de l'Historique Mensuel":
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