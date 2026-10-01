from streamlit_pages.commun import *

# ==============================================================================
# SECTION 5 : ARCHITECTURE TECHNIQUE
# ==============================================================================
st.title("📚 Architecture Technique & Pipeline")

st.markdown("""
Cette section détaille la structure technique du projet. L'objectif était de construire un pipeline de données robuste et découplé.
""")

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
st.markdown("---")
st.subheader("🔄 Du fichier CSV à la base de données")
st.markdown("""
Le jeu de données arrive sous la forme d'un **tableau plat** : une ligne par client, avec ses 6 mois d'historique rangés en colonnes (`PAY_1` à `PAY_6`, `BILL_AMT1` à `BILL_AMT6`, `PAY_AMT1` à `PAY_AMT6`). Pour le stocker comme le ferait une banque, il est transformé en **base relationnelle** :

1. **Préparation** : le fichier d'origine reçoit un nettoyage structurel (valeurs hors nomenclature ramenées à « autres ») et devient le fichier prêt à charger ([02_01_nettoyage.ipynb](https://github.com/johan-mac-59/RiskLens_ML/blob/main/src/02_01_nettoyage.ipynb), section « Nettoyage suite à Audit »).
2. **Création des tables** à partir du script SQL ([03_02_creation_tables.sql](https://github.com/johan-mac-59/RiskLens_ML/blob/main/src/03_02_creation_tables.sql)) : tables, clés primaires et clés étrangères.
3. **Chargement** ([03_01_ingestion_donnees.py](https://github.com/johan-mac-59/RiskLens_ML/blob/main/src/03_01_ingestion_donnees.py)) : les tables de correspondance sont remplies à partir de [correspondances.json](https://github.com/johan-mac-59/RiskLens_ML/blob/main/data/correspondances.json), puis chaque client est inséré dans la table `client`.
4. **Dépliage de l'historique** : les 6 mois rangés en colonnes deviennent **6 lignes par client** dans la table `historique_mensuel`, chacune rattachée à son mois dans `dim_date`. On peut ainsi ajouter un mois sans changer la structure de la base.
""")

st.graphviz_chart(r"""
digraph {
    rankdir=LR; nodesep=0.25; ranksep=0.5;
    node [shape=box, style="rounded,filled", fillcolor="#e1f5fe", fontname="Helvetica", fontsize=10, margin="0.1,0.05"];
    edge [fontname="Helvetica", fontsize=9];
    csv [fillcolor="#fff3e0", label="CSV\n1 ligne = 1 client\n6 mois en colonnes"];
    json [fillcolor="#fff3e0", label="correspondances.json"];
    client [label="client"];
    historique [fillcolor="#b3e5fc", label="historique_mensuel\n1 ligne = 1 client × 1 mois"];
    attributs [label="genre · statut marital\nniveau d'études · défaut"];
    mois [label="dim_date · statut_paiement"];
    csv -> client [label="profil"];
    csv -> historique [label="6 mois → 6 lignes"];
    json -> attributs;
    json -> mois;
    client -> historique [dir=none, style=dashed, label="1 client : 6 mois"];
    client -> attributs [dir=none, style=dashed];
    historique -> mois [dir=none, style=dashed];
}
""", width="stretch")
st.caption("Flèches pleines : le trajet des données (le CSV et le fichier des correspondances sont chargés dans la base). Traits pointillés : les liens entre les tables. Au centre, la table des faits, l'historique mensuel, liée au mois (`dim_date`) et au statut de paiement du mois ; les tables qui décrivent le client (genre, statut marital, niveau d'études, statut de défaut) sont ses attributs et se rattachent à `client`.")

st.markdown("""
**Contrôle de cohérence** ([03_03_test_cohérence.ipynb](https://github.com/johan-mac-59/RiskLens_ML/blob/main/src/03_03_test_coh%C3%A9rence.ipynb)) : une fois le chargement terminé, la base est comparée au fichier CSV pour vérifier qu'aucune donnée n'a été perdue ni modifiée :
- **volumes** : même nombre de clients, et 6 lignes d'historique par client ;
- **totaux de contrôle** : même somme des plafonds, même somme des encours, même nombre de défauts ;
- **sondage** : quelques clients tirés au hasard, comparés champ par champ.
""")

st.markdown("---")
st.subheader("📐 Modèle de Données")
st.info("Le schéma relationnel a été conçu pour éviter la redondance et assurer l'intégrité des données via des clés étrangères.")
# Si tu as l'image locale, remplace le lien ci-dessous
st.image("https://raw.githubusercontent.com/johan-mac-59/RiskLens_ML/main/images/schema_bdd__risklens.png", width="stretch")
st.caption("Représentation conceptuelle de la BDD SQLite")

st.markdown("---")
st.subheader("🔌 L'API REST")
st.markdown("""
L'application ne lit jamais la base directement : elle passe par une **API REST** ([04_01_api.py](https://github.com/johan-mac-59/RiskLens_ML/blob/main/src/04_01_api.py)), développée avec **FastAPI** et hébergée sur **Render**. L'API reçoit chaque demande, la contrôle, interroge la base et renvoie la réponse.

**Les routes, regroupées par usage :**
- **Consultation** : structure des tables, correspondances des codifications (genre, statut marital, etc.) ;
- **Gestion des clients** : consulter, créer, modifier, supprimer un client (GET, POST, PATCH, DELETE) ;
- **Gestion de l'historique** : les mêmes opérations sur un mois d'historique, ou sur tout l'historique d'un client ;
- **Analyse** : taux de défaut d'un profil (âge, genre, niveau d'études, statut marital), utilisé par le simulateur de risque ;
- **Administration** : export complet de la base, protégé par identifiant et mot de passe.

**Contrôle des données** : chaque donnée envoyée est vérifiée par **Pydantic** avant d'atteindre la base (âge entre 18 et 120 ans, montant payé positif, codification de paiement entre -2 et 9, codes de genre ou de statut marital existants…). Une demande invalide est refusée avec un message qui indique le champ en cause.
""")

st.graphviz_chart(r"""
digraph {
    rankdir=LR; nodesep=0.3; ranksep=0.5;
    node [shape=box, style="rounded,filled", fillcolor="#e1f5fe", fontname="Helvetica", fontsize=10, margin="0.1,0.05"];
    edge [fontname="Helvetica", fontsize=9];
    app [fillcolor="#fff3e0", label="Application\nStreamlit"];
    api [fillcolor="#b3e5fc", label="API FastAPI\n(Render)\ncontrôle Pydantic"];
    bdd [label="Base SQLite"];
    app -> api [label="requête"];
    api -> bdd [label="lecture / écriture"];
    bdd -> api [style=dashed];
    api -> app [style=dashed, label="réponse"];
}
""", width="stretch")

st.markdown("""
**À tester** : la [documentation interactive de l'API](""" + f"{API_URL}/docs" + """) (Swagger) permet d'essayer chaque route, et la page **Démo de l'API** permet de le faire depuis cette application.

⏳ Le serveur se met en veille quand il n'est pas utilisé : la première requête peut prendre jusqu'à une minute.
""")
