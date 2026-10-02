from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 1 : LES DONNÉES, CE QU'ON MESURE
# Sources : dictionnaire du dataset (docs/dataset_dictionary.md, page UCI), résumé statistique
# de l'audit (01_01_audit, cellule 2) et contexte du projet (docs/contexte.md)
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"

st.title("📋 1. Les données : ce qu'on mesure")
st.markdown(f"""
Le jeu de données décrit **30 000 clients** d'une banque taïwanaise, titulaires d'une carte de crédit, suivis **d'avril à septembre 2005**. Pour chacun, il indique s'il a fait **défaut de paiement le mois suivant, en octobre 2005** : c'est ce que le projet cherche à prévoir. Les définitions ci-dessous sont celles de la documentation officielle du dataset ([dictionnaire des données]({GH}/docs/dataset_dictionary.md), d'après la page de l'UCI Machine Learning Repository).
""")

# ------------------------------------------------------------------------------
st.header("1.1 Ce que contient une ligne", anchor="variables")
st.markdown("Une ligne correspond à un client. Elle réunit son profil, son plafond, six mois d'historique et la cible :")
st.markdown("""
| Colonne | Signification | Valeurs documentées |
|---|---|---|
| `LIMIT_BAL` | Plafond de la carte, crédit du client et de sa famille (cartes supplémentaires) compris | Montant en NT\\$ |
| `SEX` | Genre | 1 = homme, 2 = femme |
| `EDUCATION` | Niveau d'études | 1 = master ou doctorat, 2 = licence, 3 = baccalauréat, 4 = autres |
| `MARRIAGE` | Statut marital | 1 = marié, 2 = célibataire, 3 = autres |
| `AGE` | Âge | En années |
| `PAY_1` à `PAY_6` | Codification de paiement du mois : un nombre posé par la banque pour décrire la situation de paiement du client | -1 = paiement à temps ; 1 à 9 = nombre de mois de retard |
| `BILL_AMT1` à `BILL_AMT6` | Montant du relevé du mois : la dette totale du client à la date du relevé | Montant en NT\\$ |
| `PAY_AMT1` à `PAY_AMT6` | Montant payé au cours du mois | Montant en NT\\$ |
| `dpnm` | Défaut de paiement le mois suivant (octobre 2005) : la cible à prévoir | 1 = défaut, 0 = pas de défaut |
""")
st.markdown("**À quoi ressemble le fichier ?** Cinq lignes tirées au hasard dans le fichier d'origine, telles qu'elles se présentent :")
# 5 lignes tirées au hasard dans le fichier d'origine (sample(5, random_state=42)), classées par ID
extrait = pd.DataFrame({
    "ID": [2309, 2665, 22405, 23398, 25059], "LIMIT_BAL": [30000, 50000, 150000, 70000, 130000], "SEX": [1, 2, 2, 2, 1],
    "EDUCATION": [2, 2, 1, 3, 3], "MARRIAGE": [2, 2, 2, 1, 2], "AGE": [25, 36, 26, 32, 49],
    "PAY_1": [0, 0, 0, 0, 0], "PAY_2": [0, 0, 0, 0, 0], "PAY_3": [0, 0, 0, 0, 0],
    "PAY_4": [0, 0, 0, 0, 0], "PAY_5": [0, 0, 0, 0, 0], "PAY_6": [0, 2, 0, 0, -1],
    "BILL_AMT1": [8864, 94228, 136736, 70122, 20678], "BILL_AMT2": [10062, 47635, 125651, 69080, 18956],
    "BILL_AMT3": [11581, 42361, 116684, 68530, 16172], "BILL_AMT4": [12580, 19574, 101581, 69753, 16898],
    "BILL_AMT5": [13716, 20295, 77741, 70111, 11236], "BILL_AMT6": [14828, 19439, 77264, 70212, 6944],
    "PAY_AMT1": [1500, 2000, 4486, 2431, 1610], "PAY_AMT2": [2000, 1500, 4235, 3112, 1808],
    "PAY_AMT3": [1500, 1000, 3161, 3000, 7014], "PAY_AMT4": [1500, 1800, 2647, 2438, 27],
    "PAY_AMT5": [1500, 0, 2669, 2500, 7011], "PAY_AMT6": [2000, 1000, 2669, 2554, 4408], "dpnm": [0, 1, 0, 0, 0],
})
# Tableau HTML dans un cadre défilant, avec une barre de défilement horizontale large et bien visible
st.markdown("""
<style>
.defilement { overflow-x: scroll; padding-bottom: 8px; }
.defilement::-webkit-scrollbar { height: 24px; }
.defilement::-webkit-scrollbar-track { background: rgba(136, 136, 136, 0.25); border-radius: 12px; }
.defilement::-webkit-scrollbar-thumb { background: #44AA99; border-radius: 12px; }
@supports (-moz-appearance: none) { .defilement { scrollbar-width: auto; scrollbar-color: #44AA99 rgba(136, 136, 136, 0.25); } }
.extrait-table { border-collapse: collapse; white-space: nowrap; font-size: 15px; }
.extrait-table th, .extrait-table td { padding: 4px 10px; text-align: right; border-bottom: 1px solid rgba(136, 136, 136, 0.35); }
.extrait-table th { font-weight: 600; }
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="defilement">' + extrait.to_html(index=False, border=0, classes="extrait-table") + '</div>', unsafe_allow_html=True)
st.caption("25 colonnes : l'identifiant, 5 colonnes de profil et de plafond, 18 colonnes d'historique (6 mois × codification, facture et paiement) et la cible. Faire défiler le tableau vers la droite, avec la barre sous le tableau, pour voir toutes les colonnes.")

st.markdown("""
Les mois sont numérotés **du plus récent au plus ancien** : 1 = septembre, 2 = août… 6 = avril. La documentation appelle `PAY_0` la codification de septembre et « default payment next month » la cible ; le fichier Kaggle utilisé les nomme déjà `PAY_1`, ce qui suit la numérotation des factures et des paiements, et `dpnm`.

Les montants sont en **dollars taïwanais (NT\\$)**.
""")

# ------------------------------------------------------------------------------
st.header("1.2 Six mois d'historique : quelle facture paie quel paiement ?", anchor="frise")
st.markdown("""
Une facture de carte de crédit se règle le mois suivant. Le paiement d'un mois ne rembourse donc pas la facture de ce mois, mais celle du mois précédent. C'est la clé pour lire l'historique, et pour comprendre la suite de l'analyse :
""")
st.graphviz_chart(r"""
digraph {
    rankdir=LR; nodesep=0.3; ranksep=0.4;
    node [shape=box, style="rounded,filled", fillcolor="#e1f5fe", fontname="Helvetica", fontsize=10, margin="0.1,0.05"];
    edge [fontname="Helvetica", fontsize=9];
    aout [label="Facture d'août\nBILL_AMT2"];
    sept [fillcolor="#b3e5fc", label="Septembre\npaiement PAY_AMT1\ncodification PAY_1"];
    fsept [label="Facture de septembre\nBILL_AMT1"];
    oct [fillcolor="#fff3e0", label="Octobre\ndéfaut de paiement ?\n(cible dpnm)"];
    aout -> sept [label="payée en"];
    sept -> fsept [style=dashed, label="nouveau relevé"];
    fsept -> oct [label="à payer en"];
}
""", width="stretch")
st.markdown("Le même enchaînement se répète chaque mois :")
st.dataframe(pd.DataFrame({
    "Mois": ["Septembre", "Août", "Juillet", "Juin", "Mai", "Avril"],
    "Codification du mois": ["PAY_1", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"],
    "Paiement du mois": ["PAY_AMT1", "PAY_AMT2", "PAY_AMT3", "PAY_AMT4", "PAY_AMT5", "PAY_AMT6"],
    "Facture qu'il règle (relevé du mois précédent)": ["BILL_AMT2 (août)", "BILL_AMT3 (juillet)", "BILL_AMT4 (juin)",
                                                       "BILL_AMT5 (mai)", "BILL_AMT6 (avril)", "relevé de mars (absent du dataset)"],
}), hide_index=True, width="stretch")
st.markdown("""
Autrement dit, la codification, le paiement et la facture d'un même mois vont ensemble : `PAY_n`, `PAY_AMTn` et `BILL_AMT(n+1)`. La dernière facture, celle de septembre (`BILL_AMT1`), est à payer en octobre : c'est sur ce paiement que porte le défaut à prévoir.
""")

# ------------------------------------------------------------------------------
st.header("1.3 Ce que les données ne disent pas", anchor="limites")
st.markdown(f"""
Le jeu de données décrit le comportement des clients avec leur carte, mais il laisse dans l'ombre plusieurs informations qu'une banque utiliserait pour juger d'un risque :
- **aucun revenu**, ni aucun endettement auprès d'autres banques ;
- **aucune dépense du mois** : le relevé donne la dette totale du client à une date, pas ce qu'il a dépensé dans le mois. Une dette qui augmente peut venir de nouveaux achats comme d'intérêts et de frais de retard, sans qu'on puisse les distinguer ;
- **un seul plafond par client**, sans date : on ne sait pas s'il a changé pendant les six mois ;
- **ni la date ni la règle des codifications de paiement** : le dataset donne leur valeur, pas la façon dont la banque les pose ;
- **une définition de la cible non documentée** : on sait seulement qu'elle indique un défaut de paiement le mois suivant, sans savoir comment la banque l'a attribuée (voir la section « Limites de la définition de dpnm » du [document de contexte]({GH}/docs/contexte.md)) ;
- **une seule banque, en pleine crise** : les comportements observés sont ceux d'avril à octobre 2005, au moment de la crise des cartes de crédit à Taïwan.

Ces limites accompagnent toute la suite de l'analyse.
""")

# ------------------------------------------------------------------------------
st.header("1.4 Portrait du fichier d'origine", anchor="portrait")
st.markdown(f"Quelques repères sur les 30 000 clients, avant tout nettoyage ([01_01_audit.ipynb]({GH}/src/01_01_audit.ipynb), résumé statistique) :")
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Clients", "30 000")
col_b.metric("Défaut de paiement en octobre", "22,12 %")
col_c.metric("Âge médian", "34 ans", help="De 21 à 79 ans")
col_d.metric("Plafond médian", "140 000 NT$", help="De 10 000 à 1 000 000 NT$")
st.markdown("""
Un peu plus d'un client sur cinq (6 636 clients) fait défaut de paiement en octobre. La répartition détaillée des variables, et leurs valeurs anormales, sont présentées dans l'audit (page « 3.1 Audit »).
""")
