import streamlit as st
import requests
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="RiskLens - Credit Card Dashboard",
    page_icon="💳",
    layout="wide"
)

st.title("💳 RiskLens — Pilotage & Gestion des Risques")
st.sidebar.header("Navigation")

# Choix de l'action dans la barre latérale
choix = st.sidebar.selectbox(
    "Aller vers :",
    ["Consulter un client", "Ajouter un historique mensuel"]
)

# Configuration de l'URL de l'API (Locale ou Cloud)
# API_URL = "http://127.0.0.1:8000"  # En local
API_URL = "https://risklens-ml-api.onrender.com"  # En ligne sur Render

if choix == "Consulter un client":
    st.subheader("🔍 Consultation d'une fiche client")
    
    client_id = st.number_input("Saisir l'ID du client", min_value=1, value=8765, step=1)
    
    if st.button("Rechercher", type="primary"):
        try:
            response = requests.get(f"{API_URL}/client/{client_id}")
            
            if response.status_code == 200:
                st.success("Client trouvé avec succès !")
                data = response.json()
                
                # Transformation du dictionnaire JSON en DataFrame Pandas pour un affichage en tableau propre
                if isinstance(data, dict):
                    df_client = pd.DataFrame([data])
                    
                    st.markdown("### 📋 Informations du client")
                    st.dataframe(df_client, use_container_width=True)
                    
                    # Exemple de mise en valeur sous forme de métriques si les clés existent
                    if "age" in data and "plafond" in data:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(label="Âge du client", value=f"{data['age']} ans")
                        with col2:
                            st.metric(label="Plafond de crédit", value=f"{data['plafond']} €")
                else:
                    st.write(data)
                    
            else:
                st.error(f"Erreur {response.status_code} : Le client n'existe pas ou l'API a rencontré un problème.")
        except Exception as e:
            st.error(f"Impossible de joindre l'API : {e}")

elif choix == "Ajouter un historique mensuel":
    st.subheader("➕ Ajout d'une ligne d'historique transactionnel")
    
    with st.form("form_historique"):
        col1, col2 = st.columns(2)
        with col1:
            client_id = st.number_input("ID du client", min_value=1, value=12238)
            annee = st.number_input("Année", min_value=2000, max_value=2100, value=2026)
        with col2:
            mois = st.selectbox("Mois", options=list(range(1, 13)), format_func=lambda x: f"Mois {x}")
            montant_encours = st.number_input("Montant encours", min_value=0, value=10000)
            montant_paye = st.number_input("Montant payé", min_value=0, value=5000)
            code_statut = st.number_input("Code statut paiement", value=0)
            
        submit = st.form_submit_button("Envoyer à l'API", type="primary")
        
    if submit:
        payload = {
            "client_id": client_id,
            "mois": mois,
            "annee": annee,
            "montant_encours": montant_encours,
            "montant_paye": montant_paye,
            "code_statut_paiement": code_statut
        }
        
        try:
            res = requests.post(f"{API_URL}/historique_mensuel/", json=payload)
            if res.status_code == 200:
                result_data = res.json()
                st.success(f"✅ {result_data.get('message', 'Enregistrement réussi !')}")
                
                if 'date_id_utilise' in result_data:
                    st.info(f"📅 Date ID associé : **{result_data.get('date_id_utilise')}**")
                
                # Affichage d'un joli tableau récapitulatif des données envoyées
                st.markdown("### 📊 Données transmises à l'API")
                df_payload = pd.DataFrame([payload])
                st.dataframe(df_payload, use_container_width=True)
                
            else:
                st.error(f"❌ Erreur {res.status_code} : {res.json().get('detail')}")
        except Exception as e:
            st.error(f"Erreur de communication : {e}")