from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 2.1 : DU FICHIER CSV À LA BASE DE DONNÉES
# ==============================================================================
entete_partie_2()

st.header("2.1 Du fichier CSV à la base de données", anchor="chargement")
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
