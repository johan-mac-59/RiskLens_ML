import joblib
from streamlit_pages.commun import *

# ==============================================================================
# PAGE 7.1 : l'architecture du système déployé, de la base de données à la décision
# Chiffres lus en direct dans les fichiers de la démo (lab_ML/demo_ML/, préparés par creation_demo_ML.ipynb).
# ==============================================================================
DOSSIER_DEMO = BASE_DIR / "lab_ML" / "demo_ML"
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
PREPARATION = f"{GH_RACINE}/lab_ML/demo_ML/creation_demo_ML.ipynb"


@st.cache_resource
def charger_modele():
    return joblib.load(DOSSIER_DEMO / "model_ml_14.joblib")


enregistre = charger_modele()
reserve_1 = pd.read_csv(DOSSIER_DEMO / "clients_demo.csv")
reserve_2 = pd.read_csv(DOSSIER_DEMO / "clients_bruts_demo.csv", sep=";", encoding="utf-8-sig")

entete_partie_7()
st.header("7.1 L'architecture : de la base de données à la décision", anchor="architecture")
st.markdown("""
Déployer le modèle, c'est le rendre utilisable en dehors des notebooks où il a été construit : des données arrivent, le système les traite et rend une décision, sans intervention à la main. Ici, tout le chemin est rejoué **en direct** : la lecture des clients dans la base, le nettoyage, la règle du contentieux, le modèle et la décision.
""")

# ------------------------------------------------------------------------------
st.subheader("Le chemin d'un client, de la base à la décision", anchor="chemin")
st.graphviz_chart(r"""
digraph {
    rankdir=LR; nodesep=0.25; ranksep=0.35; compound=true;
    node [shape=box, style="rounded,filled", fillcolor="#e1f5fe", fontname="Helvetica", fontsize=10, margin="0.1,0.05"];
    edge [fontname="Helvetica", fontsize=9];
    fichier [fillcolor="#eeeeee", label="Fichier d'origine\n(UCI)"];
    bdd [label="Base SQLite"];
    api [fillcolor="#b3e5fc", label="API FastAPI\n(Render)"];
    fichier -> bdd [label="ingestion"];
    bdd -> api [dir=both];
    subgraph cluster_app {
        label="Application Streamlit : traitement en direct"; fontname="Helvetica"; fontsize=10; style="rounded"; color="#888888";
        nett [fillcolor="#fff3e0", label="Nettoyage\n(niveaux 1 à 5)"];
        perim [fillcolor="#fff3e0", label="Périmètre\n(encours en\nseptembre)"];
        cols [fillcolor="#fff3e0", label="Colonnes\ndu modèle"];
        regle [fillcolor="#f3d6e0", label="Règle du\ncontentieux"];
        modele [fillcolor="#f3d6e0", label="Modèle\n(CatBoost)"];
        decision [fillcolor="#d9f0e3", label="Décision et\nniveau de risque"];
        nett -> perim -> cols -> regle;
        regle -> decision [label="au contentieux"];
        regle -> modele [label="les autres"];
        modele -> decision [label="seuil choisi"];
    }
    api -> nett [label="POST /clients/lot\nGET /client"];
    fichier -> nett [style=dashed, label="secours"];
    fichiers [shape=note, fillcolor="#ffffff", label="Modèle enregistré\net seuils"];
    fichiers -> modele [style=dotted];
}
""", width="stretch")
st.caption("Flèches pleines : le chemin normal ; tirets : le fichier d'origine, en secours si l'API ne répond pas ; pointillés : les fichiers lus par le modèle.")

# ------------------------------------------------------------------------------
st.subheader("Ce qui tourne où", anchor="ou")
tableau_html(["Composant", "Rôle", "Où il tourne", "Fichier"], [
    ["<b>Base de données</b>", "les 30 000 clients : une fiche et six mois d'historique chacun", "avec l'API, sur Render",
     "<code>database/creditcard.db</code>, créée par <code>03_01_ingestion_donnees.py</code>"],
    ["<b>API REST</b>", "lit la base et renvoie les clients : un par un, ou tout un lot en un seul appel (<code>POST /clients/lot</code>)",
     "Render (offre gratuite)", "<code>src/04_01_api.py</code>"],
    ["<b>Application</b>", "le site : elle demande les clients à l'API, puis fait tout le traitement et affiche la décision",
     "Streamlit Community Cloud", "<code>src/04_02_streamlit_app.py</code> et <code>src/streamlit_pages/</code>"],
    ["<b>Nettoyage et colonnes</b>", "mêmes règles que le projet : corrections de codification, indicateurs du contentieux, colonnes du modèle",
     "dans l'application", "page 7.3, copie de <code>02_01_nettoyage</code> et <code>creation_datasets_ML</code>"],
    ["<b>Modèle et seuils</b>", f"{enregistre['nom']} de la version <code>{enregistre['scenario']}</code>, {len(enregistre['variables'])} variables, "
     "entraîné sur le jeu d'entraînement seul ; seuils des niveaux de risque fixés sur ce même jeu", "dans l'application",
     "<code>lab_ML/demo_ML/model_ml_14.joblib</code>, <code>bornes_niveaux.json</code>"],
    ["<b>Clients de la démonstration</b>", f"{nombre_fr(len(reserve_2))} clients jamais vus par le modèle "
     f"(dont {nombre_fr(len(reserve_1))} dans le périmètre)", "dans l'application", f"<code>lab_ML/demo_ML/</code>, préparés par <a href='{PREPARATION}'>creation_demo_ML</a>"],
], largeurs=[17, 38, 17, 28])

# ------------------------------------------------------------------------------
st.subheader("Pourquoi ces choix", anchor="pourquoi")
st.markdown("""
- **Deux démonstrations, pour les deux types de données dont on dispose.** La démo 1 (page 7.2) part des **données nettoyées du projet**, celles de l'exploration et du machine learning : elle montre le système tel qu'il a été évalué. La démo 2 (page 7.3) part des **données brutes**, telles qu'elles sont dans la base : elle refait tout le chemin, nettoyage compris, comme face à des données nouvelles.
- **Une API plutôt qu'un accès direct aux données** : c'est ainsi qu'une banque met ses données à disposition d'un outil, sans lui ouvrir sa base. La lecture **par lot** (`POST /clients/lot`) lit des milliers de clients en un seul appel, en quelques secondes, là où la lecture client par client demande deux appels par client.
- **Le nettoyage refait en direct**, avec les mêmes règles que le projet : le modèle a appris sur des données nettoyées, il doit recevoir des données nettoyées de la même façon. Un contrôle client par client le vérifie.
- **Un choix différent de la pratique habituelle : le modèle n'est pas réentraîné.** Normalement, une fois le modèle jugé sur le test, on le réentraîne sur toutes les données, entraînement et test, pour gagner un peu en performance. Ici, on a voulu **montrer le système sur des clients que le modèle n'a jamais vus** : sur des clients appris, il paraîtrait meilleur qu'il n'est. Le modèle reste donc celui entraîné sur le seul jeu d'entraînement, et **le test sert de réserve à la démonstration**, avec assez de clients pour que les taux de défaut affichés veuillent dire quelque chose. La démonstration ne fait que rejouer le test, sans rien régler dessus.
- **Le fichier d'origine en secours** : le serveur gratuit de l'API se met en veille, et peut mettre jusqu'à une minute à répondre.
""")

# ------------------------------------------------------------------------------
st.subheader("Les conditions d'utilisation : ce que fait le système, ce qu'il ne fait pas", anchor="conditions")
tableau_html(["Ce que fait le système", "Ce qu'il ne fait pas"], [
    ["Il lit des clients au format du fichier d'origine : une fiche et six mois d'historique, d'avril à septembre 2005, avec les codifications de la banque",
     "Il ne traite pas d'autres données sans être réentraîné : une autre banque, une autre période ou d'autres codifications sortent de ce qu'il a appris"],
    ["Il applique le nettoyage du projet, puis la règle du contentieux, puis le modèle, et rend pour chaque client une décision et un niveau de risque",
     "Il ne décide pas à la place d'un humain : c'est un outil pour classer les clients et traiter d'abord les plus risqués, pas pour sanctionner"],
    ["Il déclare en défaut selon le seuil choisi par l'utilisateur, fixé à l'avance sur le jeu d'entraînement",
     "Il ne donne pas de probabilité de défaut fiable pour un client seul : il donne un niveau de risque, et le taux de défaut constaté dans ce niveau"],
    ["Il mesure, sur un lot de clients, ce que la règle et le modèle détectent, face au défaut constaté",
     "Il ne décide pas pour les clients hors du <b>périmètre</b>. Le périmètre, ce sont les clients gardés par le nettoyage qui ont un encours à rembourser fin septembre et un plafond de 500 000 NT$ au plus : c'est sur eux seuls que la règle et le modèle ont été construits. Les autres sont écartés sans décision. Le modèle pourrait techniquement les noter, mais il n'a rien appris sur eux : ses résultats y seraient moins fiables"],
    ["Il signale tout écart avec les données et les règles du projet (contrôles client par client)",
     "Il n'apprend pas en service : le modèle est figé, il ne se met pas à jour seul, et aucune décision n'est enregistrée"],
], largeurs=[50, 50])
st.markdown("""
**Pour l'utiliser correctement** : lui donner des clients au même format, choisir le seuil selon le nombre d'alertes que les équipes peuvent traiter, et ne juger ses performances que sur des clients qu'il n'a jamais vus. Aucune banque n'utilise ce système : c'est une démonstration, sur des données publiques.
""")
st.caption("Les risques du système et les mesures prises pour les limiter sont présentés en page 6.6.")
