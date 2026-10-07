from streamlit_pages.commun import *
from sklearn.model_selection import train_test_split

# ==============================================================================
# PARTIE 6.3 : LES SCÉNARIOS
# Les groupes de variables de l'exploration ajoutés au socle, scénario par scénario : tous les modèles restent
# sur un plateau, et la version finale est la plus simple à score égal (ml_14, 21 variables, sans démographie).
# Scores repris tels quels de data/ML/resultats_scenarios.csv (méthode v8, précision des défauts prédits au
# taux de rappel minimal de 60 %, moyenne des 5 plis de validation) : ce fichier n'est pas dans le dépôt.
# Le taux de défaut de l'entraînement (précision d'un tri au hasard) est calculé en direct.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
JOURNAL_ML = f"{GH_RACINE}/lab_ML/tableau_ML.md"
HYPOTHESES = f"{GH_RACINE}/docs/hypotheses_et_conclusions.md"

df = load_data()
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
hors_ctx = s12[~((s12["FLAG_CTX"] == 1) & (s12["MOIS_SORTIE_CTX"] == -1))]
# Même découpage que lab_ML/creation_datasets_ML.ipynb : 80/20, stratifié sur dpnm, graine 42
train_ml, _ = train_test_split(hors_ctx, test_size=0.2, stratify=hors_ctx["dpnm"], random_state=42)
taux_hasard = train_ml["dpnm"].mean() * 100

# Scénarios dans l'ordre des notebooks : (code, libellé court, nombre de variables)
SCENARIOS = [
    ("ml_0", "socle : variables d'origine", 23),
    ("ml_1", "+ ratios de paiement mensuels", 28),
    ("ml_2", "+ traces des corrections", 25),
    ("ml_3", "+ utilisation du plafond", 29),
    ("ml_4", "+ taux de paiement global, vie du compte", 27),
    ("ml_5", "+ ratio de paiement médian, vie du compte", 27),
    ("ml_6", "+ type d'usage, vie du compte", 26),
    ("ml_7", "ml_4 + régularité, type d'usage", 29),
    ("ml_8", "ml_4 + historique des retards", 32),
    ("ml_9", "ml_4 + résumé des codifications", 29),
    ("ml_10", "ml_4 + rupture de comportement", 32),
    ("ml_11", "toutes les variables", 54),
    ("ml_12", "élagué : 21 variables", 21),
    ("ml_13", "élagué lisible : 25 variables", 25),
    ("ml_14", "ml_12, réglages élargis", 21),
    ("ml_15", "duel : 54 variables, réglages élargis", 54),
]
# Score décisionnel F2 de chaque modèle à son propre rappel (au moins le taux de rappel minimal), moyenne des 5 plis,
# par modèle et par scénario (même ordre que SCENARIOS ; None : modèle retiré en phase finale)
SCORE_F2 = {
    "CatBoost":                   [0.482, 0.484, 0.481, 0.485, 0.484, 0.482, 0.482, 0.483, 0.484, 0.485, 0.482, 0.486, 0.485, 0.484, 0.485, 0.486],
    "Régression logistique":      [0.482, 0.481, 0.482, 0.487, 0.482, 0.483, 0.483, 0.482, 0.484, 0.484, 0.482, 0.489, 0.482, 0.482, 0.482, 0.489],
    "RandomForest":               [0.479, 0.480, 0.479, 0.478, 0.480, 0.479, 0.479, 0.480, 0.482, 0.482, 0.478, 0.483, 0.484, 0.483, 0.484, 0.483],
    "Réseau de neurones (MLP)":   [0.477, 0.475, 0.482, 0.481, 0.476, 0.479, 0.479, 0.480, 0.480, 0.484, 0.479, 0.479, 0.472, 0.481, 0.480, 0.485],
    "SVM":                        [0.478, 0.478, 0.479, 0.478, 0.478, 0.478, 0.478, 0.477, 0.481, 0.482, 0.477, 0.483, 0.479, 0.477, None, None],
    "Plus proches voisins (KNN)": [0.479, 0.481, 0.478, 0.478, 0.482, 0.481, 0.481, 0.480, 0.483, 0.482, 0.481, 0.479, 0.481, 0.480, None, None],
}

entete_partie_6()
st.markdown("---")
st.header("6.3 Les scénarios : les variables de l'exploration n'apportent presque rien de plus", anchor="scenarios")

# ------------------------------------------------------------------------------
st.subheader("1. Le principe : ajouter des variables, groupe par groupe", anchor="principe")
st.markdown("""
Chaque scénario ajoute au socle (les 23 variables d'origine) un petit groupe de variables construites pendant l'exploration : ratios de paiement, utilisation du plafond, type d'usage de la carte, vie du compte, historique des retards, rupture de comportement. Tous les modèles sont réglés et mesurés de la même façon (page 6.2) : à un **taux de rappel minimal** de 60 %, chacun est réglé pour la meilleure **précision des défauts prédits** (la part des clients signalés qui font réellement défaut), puis les modèles et les scénarios sont comparés par le **score décisionnel F2**. Le score de chaque modèle est mesuré cinq fois, sur cinq découpages différents des clients d'entraînement : un groupe n'est gardé que si son gain est régulier d'une mesure à l'autre, et non un effet du hasard du découpage.
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
# Repère : ml_4, seul scénario retenu (meilleur modèle : CatBoost)
fig.add_annotation(x=libelles[4], y=SCORE_F2["CatBoost"][4], text="retenu comme référence", showarrow=True, arrowhead=2,
                   ax=0, ay=-40, font_size=TAILLE_ETIQUETTE)
fig.update_layout(yaxis_title="Score décisionnel F2 (validation)", yaxis_range=[0.468, 0.495], yaxis_dtick=0.005, height=720, separators=", ",
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                  xaxis_tickangle=-45)
st.plotly_chart(fig, width='stretch')
st.caption(f"Score décisionnel F2 de chaque modèle à son propre rappel (au moins le taux de rappel minimal de 60 %), moyenne des cinq mesures sur l'entraînement ({nombre_fr(len(train_ml))} clients hors contentieux) : c'est le score qui a servi à comparer les scénarios (page 6.2). Axe vertical resserré sur les scores, pour rendre les écarts visibles : ils restent de l'ordre de quelques millièmes. SVM et KNN, en dehors des trois meilleurs, ont été retirés pour les deux derniers scénarios. Chiffres repris tels quels du fichier de résultats du machine learning, résumé dans le [journal des scénarios]({JOURNAL_ML}) : ce fichier n'est pas dans le dépôt.")

st.markdown(f"""
**Les modèles apprennent bien quelque chose** : environ 27 clients signalés sur 100 font défaut, contre {nombre_fr(taux_hasard, 0)} sur 100 pour des clients tirés au hasard.

**Mais aucun groupe de variables ne fait vraiment mieux que le socle.** Le graphique est zoomé : d'un bout à l'autre, les scores ne varient que de 0,472 à 0,489, soit moins de deux centièmes. C'est du même ordre que la variation du score d'une mesure à l'autre pour un même modèle et un même scénario (environ 0,01) : quel que soit le scénario ou le modèle, on reste constamment dans la zone d'incertitude de la mesure, où un écart ne se distingue pas du hasard du découpage.

**Pourquoi `ml_4` a-t-il été retenu, alors que d'autres scénarios montent plus haut ?** La règle ne regarde pas la hauteur d'une courbe, mais la **régularité du gain** : `ml_4` (le taux de paiement global) ne gagne que 0,002 sur le socle, mais il gagne à chacune des cinq mesures ; `ml_3`, plus haut sur le graphique, ne gagne pas à toutes. Ce gain reste minuscule : `ml_4` a surtout servi de **référence** pour comparer les scénarios suivants, et sa variable a ensuite été retirée à l'élagage. La version finale ne la garde pas. Même avec toutes les variables à la fois (`ml_11`, 54 variables), le meilleur modèle ne s'écarte pas du plateau.

**Les variables essayées étaient de deux sortes :**
- certaines **décrivent le client** : son usage de la carte, l'utilisation de son plafond, la part de ses factures qu'il rembourse ;
- d'autres **cherchent un signal d'alerte**, un comportement inhabituel qui pourrait annoncer le défaut : une dette qui monte d'un coup en septembre, des paiements récents qui baissent par rapport à l'habitude du client (`ml_10`), un historique de retards (`ml_8`).

Ni les unes ni les autres ne font mieux. Leur effet **dépend du modèle** : un groupe aide parfois l'un (l'historique des retards et le résumé des codifications aident le SVM, toutes les variables ensemble aident la régression logistique), parfois aucun. **Sur le moment, on ne savait pas pourquoi.** Chaque modèle lit les données à sa façon, et deux raisons, impossibles à départager, pouvaient jouer :
- le modèle avait **déjà trouvé** cette information dans les montants et les codifications d'origine ;
- le signal était **trop rare ou trop faible**, ou **son lien avec le défaut n'était pas là** : il ne suffisait pas à changer les prédictions.

Une chose était sûre : **les liens vus pendant l'exploration ne se sont pas montrés aussi forts qu'espéré.** Ils sont réels entre des groupes de clients (parties 4 et 5), mais ils ne suffisent pas à dire, client par client, qui fera défaut.

Il faut aussi rappeler que **cette base est la plus difficile** : les défauts les plus visibles, ceux du contentieux, sont partis à la règle métier (partie 5), et il ne reste que des clients en gestion normale, aux défauts beaucoup moins évidents. L'explication du plateau n'est venue qu'après, une fois le modèle figé : elle fait l'objet de la page 6.5.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Le choix final : pas le score le plus haut, mais le plus simple à égalité", anchor="choix-final")
st.markdown("""
Puisque tout se vaut, l'**élagage** a retiré les variables qui n'apportaient rien (`ml_12`), sans perte de score, puis l'élargissement des réglages des modèles (`ml_14`) n'a pas changé le meilleur score. Restent **21 variables** :
- les **montants d'origine** : plafond, factures et paiements des six mois ;
- les **codifications de paiement** `PAY_1` à `PAY_6` ;
- deux **résumés des codifications** : `PAY_habituel` (la codification la plus fréquente du client sur les six mois) et `CUMUL_INCIDENT` (le nombre de mois en retard).

**Aucune donnée démographique** n'en fait partie : ni l'âge, ni le genre, ni le niveau d'études, ni le statut marital. Leur lien avec le défaut existe (page 4.1), mais il est faible et déjà porté par le comportement : les retirer ne coûte rien, et le modèle ne juge plus un client sur ce qu'il est, mais sur la façon dont il utilise et rembourse son crédit.
""")

st.markdown("**Pourtant, `ml_14` n'a pas le score le plus haut du graphique.** La régression logistique sur toutes les variables (`ml_11`, puis `ml_15` avec les réglages élargis) fait un peu mieux. Un duel, prévu avant d'en connaître le résultat, a opposé les deux versions :")
tableau_html(["", "<code>ml_14</code> (retenu)", "<code>ml_15</code>"], [
    ["<b>Variables</b>", "21, sans démographie", "54, démographie comprise"],
    ["<b>Meilleur modèle</b>", "CatBoost : 0,485", "Régression logistique : 0,489"],
    ["<b>Écart, mesure habituelle</b> (5 mesures)", "référence", "+0,004, meilleur dans 3 mesures sur 5 : dans la zone d'incertitude"],
    ["<b>Écart, mesure fine</b> (50 mesures)", "référence", "+0,0026, meilleur dans 31 mesures sur 50 ; test statistique bien en dessous du seuil fixé à l'avance : dans la zone d'incertitude"],
], largeurs=[30, 30, 40])
st.markdown("""
Trois raisons font choisir `ml_14` :
- **l'écart n'est pas un vrai gain.** La règle, fixée dès le début, ne retient une version plus complexe que sur un gain régulier d'une mesure à l'autre. Ici, l'écart est plus petit que la variation entre deux mesures, et la mesure fine le confirme : il ne se distingue pas du hasard du découpage ;
- **le meilleur score d'un plateau est flatteur** : c'est le « piège du gagnant ». Parmi des dizaines de candidats à égalité (16 scénarios, jusqu'à six modèles chacun), le plus haut l'est en partie par chance. La preuve : l'avance de `ml_15` fond de 0,004 à 0,0026 dès qu'on la mesure plus finement ;
- **à score égal, le plus simple l'emporte** : 21 variables au lieu de 54, plus faciles à expliquer et à surveiller, et aucune donnée démographique.

Dans `ml_14`, les quatre modèles restants sont eux aussi à égalité. **CatBoost**, en tête de cette version, a été désigné comme modèle de décision avant la lecture du test, avec le seuil qui atteint le taux de rappel minimal ; les autres sont gardés pour information. Il est jugé sur le test en page 6.4.
""")
st.caption(f"Détail de chaque scénario et de chaque décision : [journal des scénarios]({JOURNAL_ML}), section 2. Duel fin : `lab_ML/duel_fin_ml14_ml15.ipynb` (validation croisée répétée, test t corrigé de Nadeau et Bengio). Raisonnement complet : [hypothèses et conclusions]({HYPOTHESES}), H8, H9 et H14.")

st.info("""
**Ce qu'il faut retenir** : ajouter les variables de l'exploration, qu'elles décrivent le client ou cherchent un signal d'alerte, groupe par groupe ou toutes ensemble, ne fait pas sortir les modèles d'un plateau : environ 27 clients signalés sur 100 font défaut, quel que soit le scénario, et tous les écarts restent dans la zone d'incertitude de la mesure. Leur effet varie d'un modèle à l'autre, sans jamais dépasser le bruit : les liens vus pendant l'exploration distinguent des groupes, ils ne suffisent pas à prédire le défaut de chaque client. La version finale est donc la plus simple : 21 variables, sans aucune donnée démographique, avec CatBoost comme modèle de décision.
""")
