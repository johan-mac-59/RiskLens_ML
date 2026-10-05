from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 2.3 : L'API REST
# ==============================================================================
entete_partie_2()

st.header("2.3 L'API REST", anchor="api")
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
