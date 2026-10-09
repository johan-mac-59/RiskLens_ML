import joblib
from streamlit_pages.commun import *

# ==============================================================================
# PAGE 7.1 : l'architecture du système déployé, de la base de données à la décision
# Chiffres lus en direct dans les fichiers des démos (lab_ML/demo_ML/, préparés par creation_demo_ML.ipynb et creation_demo_3.ipynb).
# ==============================================================================
DOSSIER_DEMO = BASE_DIR / "lab_ML" / "demo_ML"
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
PREPARATION = f"{GH_RACINE}/lab_ML/demo_ML/creation_demo_ML.ipynb"
PREPARATION_3 = f"{GH_RACINE}/lab_ML/demo_ML/creation_demo_3.ipynb"


@st.cache_resource
def charger_modele():
    return joblib.load(DOSSIER_DEMO / "model_ml_14.joblib")


enregistre = charger_modele()
reserve_1 = pd.read_csv(DOSSIER_DEMO / "clients_demo.csv")
reserve_2 = pd.read_csv(DOSSIER_DEMO / "clients_bruts_demo.csv", sep=";", encoding="utf-8-sig")
classes_3 = json.loads((DOSSIER_DEMO / "demo_3_classes.json").read_text(encoding="utf-8"))

entete_partie_7()
st.header("7.1 L'architecture : de la base de données à la décision", anchor="architecture")
st.markdown("""
Déployer le modèle, c'est le rendre utilisable en dehors des notebooks où il a été construit : des données arrivent, le système les traite et rend une décision, sans intervention à la main. Ici, tout le chemin est rejoué **en direct** : la lecture des clients dans la base, le nettoyage, la règle du contentieux, le modèle et la décision. Pour la démo 3, le niveau de risque de chaque client est aussi **enregistré dans la base**, comme le ferait une banque qui le recalcule chaque mois.
""")

# ------------------------------------------------------------------------------
st.subheader("Le chemin d'un client, de la base à la décision", anchor="chemin")
st.graphviz_chart(r"""
digraph {
    rankdir=LR; nodesep=0.25; ranksep=0.35; compound=true;
    node [shape=box, style="rounded,filled", fillcolor="#e1f5fe", fontname="Helvetica", fontsize=10, margin="0.1,0.05"];
    edge [fontname="Helvetica", fontsize=9];
    fichier [fillcolor="#eeeeee", label="Fichier d'origine\n(UCI)"];
    bdd [label="Base SQLite\nclients, historique,\nprédictions"];
    notebook3 [shape=note, fillcolor="#ffffff", label="Prédictions de la démo 3\n(notebook creation_demo_3)"];
    notebook3 -> bdd [label="ingestion"];
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
        brut [fillcolor="#f3d6e0", label="Démo 3 : modèle sur\nles données brutes\n(5 modèles de plis)"];
        niveau [fillcolor="#d9f0e3", label="Niveau de risque\n1/9 à 9/9"];
        brut -> niveau [label="seuil choisi"];
    }
    api -> brut [label="POST /clients/lot\n(données brutes)"];
    api -> niveau [style=dashed, label="GET /prediction\n(niveau enregistré)"];
    api -> nett [label="POST /clients/lot\nGET /client"];
    fichier -> nett [style=dashed, label="secours"];
    fichiers [shape=note, fillcolor="#ffffff", label="Modèle enregistré\net seuils"];
    fichiers -> modele [style=dotted];
}
""", width="stretch")
st.caption("Flèches pleines : le chemin normal ; tirets : le fichier d'origine en secours si l'API ne répond pas (démo 2), et le niveau de risque enregistré "
           "dans la base, relu pour contrôle (démo 3) ; pointillés : les fichiers lus par le modèle.")

# ------------------------------------------------------------------------------
st.subheader("Ce qui tourne où", anchor="ou")
tableau_html(["Composant", "Rôle", "Où il tourne", "Fichier"], [
    ["<b>Base de données</b>", "les 30 000 clients : une fiche et six mois d'historique chacun", "avec l'API, sur Render",
     "<code>database/creditcard.db</code>, créée par <code>03_01_ingestion_donnees.py</code>"],
    ["<b>Prédictions dans la base</b>", "pour chaque client, son score et son niveau de risque (1/9 à 9/9) selon le modèle de la démo 3, avec la période de calcul "
     "(table <code>prediction</code>) ; tables de correspondance <code>modele</code> et <code>classe_risque</code> (libellé, bornes, taux de défaut constaté)",
     "dans la base, sur Render", "remplies par l'ingestion, à partir du fichier produit par <code>creation_demo_3</code> (étape 10) et de <code>data/correspondances.json</code>"],
    ["<b>API REST</b>", "lit la base et renvoie les clients : un par un, ou tout un lot en un seul appel (<code>POST /clients/lot</code>) ; renvoie aussi le niveau de risque enregistré d'un client (<code>GET /prediction</code>)",
     "Render (offre gratuite)", "<code>src/04_01_api.py</code>"],
    ["<b>Application</b>", "le site : elle demande les clients à l'API, puis fait tout le traitement et affiche la décision",
     "Streamlit Community Cloud", "<code>src/04_02_streamlit_app.py</code> et <code>src/streamlit_pages/</code>"],
    ["<b>Nettoyage et colonnes</b>", "mêmes règles que le projet : corrections de codification, indicateurs du contentieux, colonnes du modèle",
     "dans l'application", "page 7.3, copie de <code>02_01_nettoyage</code> et <code>creation_datasets_ML</code>"],
    ["<b>Modèle et seuils</b>", f"{enregistre['nom']} de la version <code>{enregistre['scenario']}</code>, {len(enregistre['variables'])} variables, "
     "entraîné sur le jeu d'entraînement seul ; seuils des niveaux de risque fixés sur ce même jeu", "dans l'application",
     "<code>lab_ML/demo_ML/model_ml_14.joblib</code>, <code>bornes_niveaux.json</code>"],
    ["<b>Modèle et niveaux de risque de la démo 3</b>", f"CatBoost sur les 23 variables d'origine, en 5 modèles de plis : chaque client est noté par celui qui ne l'a pas vu ; "
     f"{len(classes_3['bornes_rappel']) + 1} niveaux de risque, fixés par lecture de la courbe de précision", "dans l'application",
     f"<code>lab_ML/demo_ML/demo_3_modeles_plis.joblib</code>, <code>demo_3_classes.json</code>, préparés par <a href='{PREPARATION_3}'>creation_demo_3</a>"],
    ["<b>Clients des démonstrations</b>", f"démos 1 et 2 : {nombre_fr(len(reserve_2))} clients jamais vus par le modèle "
     f"(dont {nombre_fr(len(reserve_1))} dans le périmètre) ; démo 3 : les 30 000 clients de la base, chacun jamais vu par le modèle qui le note",
     "dans l'application", f"<code>lab_ML/demo_ML/</code>, préparés par <a href='{PREPARATION}'>creation_demo_ML</a>"],
], largeurs=[17, 38, 17, 28])

# ------------------------------------------------------------------------------
st.subheader("Pourquoi ces choix", anchor="pourquoi")
st.markdown("""
- **Trois démonstrations.** La démo 1 (page 7.2) part des **données nettoyées du projet**, celles de l'exploration et du machine learning : elle montre le système tel qu'il a été évalué. La démo 2 (page 7.3) part des **données brutes**, telles qu'elles sont dans la base : elle refait tout le chemin, nettoyage compris, comme face à des données nouvelles. La démo 3 (page 7.4) porte sur **tout le dataset, sans le travail du projet** : un modèle entraîné sur les seules données d'origine, comparé à la règle métier ; elle répond à la problématique sur les données brutes.
- **Le niveau de risque enregistré dans la base** (démo 3) : une banque calcule le niveau de risque de ses clients une fois par période et l'enregistre, pour que ses équipes filtrent directement les clients à suivre. La table garde la période de calcul : chaque nouveau calcul ajouterait ses lignes sans effacer les précédentes. La décision « déclaré en défaut » n'est pas enregistrée : elle dépend du seuil choisi, et se déduit du niveau.
- **Une API plutôt qu'un accès direct aux données** : c'est ainsi qu'une banque met ses données à disposition d'un outil, sans lui ouvrir sa base. La lecture **par lot** (`POST /clients/lot`) lit des milliers de clients en un seul appel, en quelques secondes, là où la lecture client par client demande deux appels par client.
- **Le nettoyage refait en direct**, en mémoire, dans l'application, sans toucher à la base, avec les mêmes règles que le projet : le modèle a appris sur des données nettoyées, il doit recevoir des données nettoyées de la même façon. Un contrôle client par client le vérifie.
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
     "Il n'apprend pas en service : le modèle est figé et ne se met pas à jour seul ; seul le niveau de risque de la démo 3 est enregistré dans la base, jamais la décision"],
], largeurs=[50, 50])
st.markdown("""
**Pour l'utiliser correctement** : lui donner des clients au même format, choisir le seuil selon le nombre d'alertes que les équipes peuvent traiter, et ne juger ses performances que sur des clients qu'il n'a jamais vus. Aucune banque n'utilise ce système : c'est une démonstration, sur des données publiques.
""")
st.caption("Les risques du système et les mesures prises pour les limiter sont présentés en page 6.6.")
