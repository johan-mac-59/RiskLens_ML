from streamlit_pages.commun import *
from sklearn.model_selection import train_test_split

# ==============================================================================
# PARTIE 6.3 : LES SCÉNARIOS
# Le socle, le scénario complet (toutes les variables construites pour le ML), puis l'élagage famille par famille :
# tous les modèles restent sur un plateau ; une fois les codifications brutes retirées (ml_3), le comportement
# du client suffit ; la version finale est ml_17 (21 variables, CatBoost modèle de décision).
# Scores repris tels quels de data/ML/resultats_scenarios.csv (méthode v9, précision des défauts prédits au
# taux de rappel minimal de 60 %, moyenne des 5 plis de validation) : ce fichier n'est pas dans le dépôt.
# Le taux de défaut de l'entraînement (précision d'un tri au hasard) est calculé en direct.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
JOURNAL_ML = f"{GH_RACINE}/lab_ML/tableau_ML.md"

df = load_data()
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
# Population du ML : sans les clients en incident à M ni en retard imminent (statut à M, comme creation_datasets_ML)
hors_ctx = s12[~s12["STATUT_INCIDENT"].isin(["En incident", "Retard imminent"])]
# Même découpage que lab_ML/creation_datasets_ML.ipynb : 80/20, stratifié sur dpnm, graine 42
train_ml, _ = train_test_split(hors_ctx, test_size=0.2, stratify=hors_ctx["dpnm"], random_state=42)
taux_hasard = train_ml["dpnm"].mean() * 100

# Scénarios dans l'ordre des notebooks : (code, libellé court, nombre de variables)
SCENARIOS = [
    ("ml_0", "socle : variables d'origine", 23),
    ("ml_1", "+ codification de septembre de la banque", 24),
    ("ml_2", "complet : toutes les variables", 53),
    ("ml_3", "− codifications brutes", 46),
    ("ml_4", "− âge, régularité des paiements", 44),
    ("ml_5", "− démographie (annulé)", 41),
    ("ml_6", "ruptures, encodage numérique", 44),
    ("ml_7", "ruptures, log signé", 44),
    ("ml_8", "− vie du compte", 41),
    ("ml_9", "− paiement résumé, type d'usage", 38),
    ("ml_10", "− rupture de comportement", 34),
    ("ml_11", "− ratios de paiement mensuels", 29),
    ("ml_12", "− utilisation du plafond (annulé)", 23),
    ("ml_13", "− indicateurs d'incident", 26),
    ("ml_14", "− indicateurs de retard", 23),
    ("ml_15", "− sexe", 22),
    ("ml_16", "− statut marital", 21),
    ("ml_17", "final : réglages élargis", 21),
]
# Score décisionnel F2 de chaque modèle à son propre rappel (au moins le taux de rappel minimal), moyenne des 5 plis,
# par modèle et par scénario (même ordre que SCENARIOS ; None : modèle retiré de l'entraînement final)
SCORE_F2 = {
    "CatBoost":                   [0.446, 0.447, 0.452, 0.453, 0.452, 0.450, 0.452, 0.452, 0.452, 0.451, 0.452, 0.452, 0.446, 0.451, 0.451, 0.451, 0.450, 0.451],
    "Régression logistique":      [0.442, 0.442, 0.449, 0.449, 0.449, 0.448, 0.450, 0.447, 0.450, 0.449, 0.450, 0.451, 0.443, 0.451, 0.451, 0.450, 0.448, 0.449],
    "SVM":                        [0.446, 0.445, 0.449, 0.448, 0.448, 0.445, 0.448, 0.448, 0.449, 0.448, 0.447, 0.447, 0.441, 0.446, 0.445, 0.444, 0.443, 0.446],
    "Réseau de neurones (MLP)":   [0.444, 0.442, 0.448, 0.444, 0.446, 0.445, 0.449, 0.443, 0.448, 0.446, 0.445, 0.448, 0.443, 0.443, 0.443, 0.436, 0.436, 0.446],
    "Plus proches voisins (KNN)": [0.443, 0.440, 0.447, 0.445, 0.444, 0.445, 0.444, 0.446, 0.447, 0.445, 0.441, 0.442, 0.439, 0.448, 0.439, 0.441, 0.444, 0.443],
    "RandomForest":               [0.436, 0.434, 0.444, 0.437, 0.444, 0.443, 0.446, 0.445, 0.446, 0.445, 0.444, 0.433, 0.433, 0.439, 0.439, 0.440, 0.437, None],
}
# Précision des défauts prédits du modèle de décision (CatBoost de ml_17) au taux de rappel minimal, en validation
PRECISION_FINALE = 22.6

entete_partie_6()
st.markdown("---")
st.header("6.3 Les scénarios : les variables de l'exploration n'apportent presque rien de plus", anchor="scenarios")

# ------------------------------------------------------------------------------
st.subheader("1. Le principe : tout ajouter, puis élaguer", anchor="principe")
st.markdown("""
Le **socle** (`ml_0`) ne contient que les 23 variables d'origine. Le **scénario complet** (`ml_2`) y ajoute d'un coup toutes les variables construites pour le machine learning : ratios de paiement, utilisation du plafond, type d'usage de la carte, vie du compte, historique des retards et des incidents, rupture de comportement. Ce scénario est ensuite **élagué, famille de variables par famille** : chaque scénario suivant retire une famille.

Tous les modèles sont réglés et mesurés de la même façon (page 6.2) : à un **taux de rappel minimal** de 60 %, chacun est réglé pour la meilleure **précision des défauts prédits** (la part des clients signalés qui font réellement défaut), puis les modèles et les scénarios sont comparés par le **score décisionnel F2**. Le score de chaque modèle est mesuré cinq fois, sur cinq découpages différents des clients d'entraînement :
- un **ajout** n'est gardé que si son gain est régulier d'une mesure à l'autre, et non un effet du hasard du découpage ;
- un **retrait** n'est confirmé que s'il ne coûte rien de réel ; sinon, la famille revient.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Un plateau, pour tous les modèles", anchor="plateau")

libelles = [f"{code}<br>{libelle}" for code, libelle, _ in SCENARIOS]
couleurs_modeles = [COULEURS["turquoise"], COULEURS["mauve"], COULEURS["vert_fonce"],
                    COULEURS["violet"], COULEURS["olive"], COULEURS["bleu_pale"]]
fig = go.Figure()
for (modele, valeurs), couleur in zip(SCORE_F2.items(), couleurs_modeles):
    fig.add_trace(go.Scatter(
        x=libelles, y=valeurs, name=modele, mode="lines+markers", line_color=couleur,
        hovertemplate=modele + "<br>%{x}<br>Score décisionnel F2 : %{y:.3f}<extra></extra>"))
# Repères sur le meilleur modèle (CatBoost) : scénario complet, codifications brutes retirées, retrait annulé, version finale
for i, texte, decalage in [(2, "complet", -40), (3, "sans codifications brutes", -70), (12, "retrait annulé", 40), (17, "version finale", -40)]:
    fig.add_annotation(x=libelles[i], y=SCORE_F2["CatBoost"][i], text=texte, showarrow=True, arrowhead=2,
                       ax=0, ay=decalage, font_size=TAILLE_ETIQUETTE)
fig.update_layout(yaxis_title="Score décisionnel F2 (validation)", yaxis_range=[0.428, 0.462], yaxis_dtick=0.005, height=720, separators=", ",
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                  xaxis_tickangle=-45)
st.plotly_chart(fig, width='stretch')
st.caption(f"Score décisionnel F2 de chaque modèle à son propre rappel (au moins le taux de rappel minimal de 60 %), moyenne des cinq mesures sur l'entraînement ({nombre_fr(len(train_ml))} clients, sans la population en incident ni le retard imminent) : c'est le score qui a servi à comparer les scénarios (page 6.2). Axe vertical resserré sur les scores, pour rendre les écarts visibles : ils restent de l'ordre de quelques millièmes. RandomForest, toujours en dessous des autres, n'a pas été repris pour l'entraînement final (`ml_17`). Chiffres repris tels quels du fichier de résultats du machine learning, résumé dans le [journal des scénarios]({JOURNAL_ML}) : ce fichier n'est pas dans le dépôt.")

f2_min = min(v for valeurs in SCORE_F2.values() for v in valeurs if v is not None)
f2_max = max(v for valeurs in SCORE_F2.values() for v in valeurs if v is not None)
st.markdown(f"""
**Les modèles apprennent bien quelque chose** : quand on leur demande de retrouver 60 % des défauts (le taux de rappel minimal), environ {nombre_fr(PRECISION_FINALE, 0)} clients signalés sur 100 font défaut, contre {nombre_fr(taux_hasard, 0)} sur 100 pour des clients tirés au hasard. Ce chiffre dépend de la part des défauts demandée : en retrouver moins permet de ne signaler que les clients les plus risqués, et la part de vrais défauts monte ; en retrouver plus oblige à signaler davantage de bons clients, et elle baisse.

**Mais aucun scénario ne fait vraiment mieux que les autres.** Le graphique est zoomé : d'un bout à l'autre, tous modèles confondus, les scores ne varient que de {nombre_fr(f2_min, 3)} à {nombre_fr(f2_max, 3)}. La variation du score d'une mesure à l'autre, pour un même modèle et un même scénario, est de l'ordre de 0,01 : on reste presque toujours dans la zone d'incertitude de la mesure.

**Deux scénarios sortent du bruit, de peu :**
- **le scénario complet** (`ml_2`) gagne sur le socle : environ 0,006 pour le meilleur modèle, CatBoost, à quatre mesures sur cinq, et tous les modèles montent un peu. Les variables de l'exploration apportent donc quelque chose, mais très peu ;
- **retirer l'utilisation du plafond** (`ml_12`) ramène le meilleur modèle au niveau du socle, et presque tous les modèles baissent, à la limite du bruit : ce retrait a été annulé, et l'utilisation du plafond fait partie de la version finale.

Tous les autres retraits (vie du compte, comportement de paiement résumé, type d'usage, rupture de comportement, ratios de paiement mensuels, indicateurs d'incident et de retard, âge, sexe, statut marital) ne coûtent rien de réel : les modèles avaient déjà l'information ailleurs, ou elle était trop faible pour changer les prédictions. Les liens vus pendant l'exploration sont réels entre des groupes de clients (parties 4 et 5), mais ils ne suffisent pas à dire, client par client, qui fera défaut.

Il faut aussi rappeler que **cette base est la plus difficile** : les défauts les plus visibles, ceux de la population en incident et du retard imminent, sont partis aux règles métier (partie 5), et il ne reste que des clients en gestion normale, aux défauts beaucoup moins évidents.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Sans les codifications de la banque, le comportement suffit", anchor="comportement")
st.markdown(f"""
Le premier retrait est le plus parlant. `ml_3` retire du scénario complet les **codifications brutes** de la banque : `PAY_1` à `PAY_6` et la codification habituelle du client. **Le score ne bouge pas** : pour les six modèles, l'écart avec le scénario complet reste dans la zone d'incertitude de la mesure, avec 46 variables au lieu de 53.

Une fois les retards et les incidents repérés par nos indicateurs, les codifications de la banque n'apportent plus rien. Ces indicateurs ne sont pas les codifications : ce sont des **comportements tagués**, construits à partir de codifications en partie reconstruites sur ce que le client a payé (correction des {codif('1')} de septembre, uniformisation des {codif('2')} d'avril à juin, partie 3), puis lus avec nos règles (partie 5). Le nombre de mois en retard (`CUMUL_INCIDENT`) arrive en tête de ce que les modèles utilisent.

**Une fois les deux populations à risque confiées aux règles métier, le comportement du client suffit à trier les clients restants par niveau de risque.**
""")

# ------------------------------------------------------------------------------
st.subheader("4. Le choix final : le plus simple, à score égal", anchor="choix-final")
st.markdown("""
Au bout de l'élagage, `ml_16` garde le même score que le scénario complet avec **21 variables au lieu de 53**. `ml_17` reprend ces variables pour l'entraînement final, avec des réglages élargis pour chaque modèle :
- le **plafond** et les **montants d'origine** : factures et paiements des six mois ;
- l'**utilisation du plafond**, mois par mois (page 4.2) ;
- le **nombre de mois en retard** (`CUMUL_INCIDENT`, pages 4.6 et 5.2) ;
- le **niveau d'études**.

Le niveau d'études est la **seule donnée démographique restante**. L'âge, le sexe et le statut marital ont été retirés sans perte. Le niveau d'études a été retiré avec le sexe et le statut marital (`ml_5`), et cette famille a d'abord été gardée ; le sexe et le statut marital sont ensuite partis un par un, et le niveau d'études n'a pas été retiré seul.

**À score égal, le plus simple l'emporte** : moins de variables, plus faciles à expliquer et à surveiller, et un modèle qui juge surtout un client sur la façon dont il utilise et rembourse son crédit.

Dans `ml_17`, les cinq modèles sont à égalité : leur écart est plus petit que la variation d'une mesure à l'autre. **CatBoost**, en tête de cette version, a été désigné comme modèle de décision avant la lecture du test, avec le seuil qui atteint le taux de rappel minimal ; les autres sont gardés pour information.
""")
st.caption(f"Détail de chaque scénario et de chaque décision : [journal des scénarios]({JOURNAL_ML}), section 2.")

st.info(f"""
**Ce qu'il faut retenir** : toutes les variables de l'exploration ont été ajoutées, puis retirées famille par famille. Tous les modèles restent sur un plateau : pour retrouver 60 % des défauts, environ {nombre_fr(PRECISION_FINALE, 0)} clients signalés sur 100 font défaut, quel que soit le scénario, contre {nombre_fr(taux_hasard, 0)} au hasard ; cette part monte si l'on demande moins de défauts, et baisse si l'on en demande plus. Retirer les codifications brutes de la banque ne coûte rien : une fois les retards et les incidents tagués par nos indicateurs, le comportement du client suffit. La version finale est la plus simple à score égal : 21 variables (plafond, factures, paiements, utilisation du plafond, nombre de mois en retard, niveau d'études), avec CatBoost comme modèle de décision.
""")
