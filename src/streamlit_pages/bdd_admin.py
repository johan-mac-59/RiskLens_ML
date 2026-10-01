from streamlit_pages.commun import *

# ==============================================================================
# ESPACE RÉSERVÉ À L'ADMINISTRATEUR
# ==============================================================================

# -------------------------------------------------------------
# 2. ZONE PROTEGÉE (Authentification requise)
# -------------------------------------------------------------
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
