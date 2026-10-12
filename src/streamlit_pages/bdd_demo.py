from streamlit_pages.commun import *

mappings = load_mappings()

entete_partie_2()
st.header("2.4 Démo de l'API : les clients et leur historique", anchor="demo")

st.markdown("""
**Ce que vous consultez** : la base de données SQLite du projet. Elle contient les 30 000 clients du jeu de données d'origine, après un nettoyage structurel (les valeurs du niveau d'études et du statut marital absentes de la nomenclature sont ramenées à « autres »). Les données y sont rangées comme dans une banque : une table des clients (profil, plafond, défaut du mois suivant) et une table de l'historique mensuel (facture, paiement et codification de paiement de chaque mois, d'avril à septembre 2005). Les codifications sont traduites en libellés grâce à des tables de correspondance.

**Ce que vous pouvez faire** : chaque action ci-dessous interroge en direct l'API REST du projet (FastAPI), qui lit ou modifie la base.
- **👤 Gestion des clients** : consulter la fiche d'un client à partir de son ID (de 1 à 30 000), créer un client, modifier ses informations ou le supprimer.
- **📅 Historique transactionnel** : consulter les 6 mois d'historique d'un client, ajouter un mois, en modifier un, ou supprimer un mois ou tout l'historique.
- **🧮 Simulateur de risque**, sous les deux onglets : choisir un profil (âge, genre, niveau d'études, statut marital) et obtenir, calculés par l'API sur la base, le nombre de clients concernés et leur taux de défaut.

Il s'agit d'une base de démonstration : vous pouvez tester toutes les opérations sans risque. Les analyses des autres pages s'appuient sur une version plus poussée du nettoyage.
""")

tab_clients, tab_historique = st.tabs(["👤 Gestion des clients", "📅 Historique transactionnel"])

# ==============================================================================
# SECTION 3 : GESTION DES CLIENTS (GET, POST, PATCH, DELETE)
# ==============================================================================
with tab_clients:
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
                        # Défaut constaté en octobre 2005 : libellé lu dans les tables de correspondance (Non défaillant / Défaillant)
                        statut_defaut = client_data.get('code_statut_defaut', 0)
                        libelle_defaut = mappings.get("statut_defaut", {}).get(statut_defaut, statut_defaut)
                        st.metric("Statut de défaut", f"{'⚠️' if statut_defaut == 1 else '✅'} {libelle_defaut}")
                    
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
with tab_historique:
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

# Simulateur hors des onglets, sous eux, pour qu'il ressorte
# ==============================================================================
# CALCULATEUR INTERACTIF RÉEL : TAUX DE DÉFAUT PAR PROFIL
# ==============================================================================
st.markdown("---")
with encadre_interactif("simulateur_api", invitation="À vous de tester : choisissez un profil de client et découvrez son taux de défaut de paiement"):
    st.subheader("🧮 Simulateur de Risque par Profil Démographique", anchor="simulateur")
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
