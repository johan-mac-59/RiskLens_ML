from streamlit_pages.commun import *
from sklearn.model_selection import train_test_split

# ==============================================================================
# PARTIE 6.4 : LE MODÈLE RETENU, JUGÉ SUR LE TEST
# La version finale (ml_14, CatBoost et son seuil) sur le test lu une seule fois, puis la présentation par
# niveaux de risque. Chiffres repris tels quels des sorties de lab_ML/evaluation_finale_test.ipynb (sections 2,
# 3, 4 et 6) : le modèle et ses probabilités ne sont pas dans le dépôt. Effectifs du test et taux de défaut
# calculés en direct (même découpage que lab_ML/creation_datasets_ML.ipynb).
# La comparaison « règle seule / règle + modèle » est en partie 7 ; le plafond et ses causes en 6.5.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
EVALUATION = f"{GH_RACINE}/lab_ML/evaluation_finale_test.ipynb"
METHODOLOGIE = f"{GH_RACINE}/lab_ML/methodologie_ML.md"

df = load_data()
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
hors_ctx = s12[~((s12["FLAG_CTX"] == 1) & (s12["MOIS_SORTIE_CTX"] == -1))]
# Même découpage que lab_ML/creation_datasets_ML.ipynb : 80/20, stratifié sur dpnm, graine 42
_, test_ml = train_test_split(hors_ctx, test_size=0.2, stratify=hors_ctx["dpnm"], random_state=42)

# Section 6 du notebook : niveaux de risque sur tout le périmètre du ML (contentieux compris), chaque client
# classé par un modèle qui ne l'a jamais vu. (niveau, libellé, clients, défauts)
NIVEAUX = [
    ("Contentieux", "retiré avant le machine learning, prédit en défaut par la règle", 3004, 2117),
    ("Haut risque", "coût en fausses alertes moyen", 2809, 1161),
    ("Risque modéré", "coût en fausses alertes élevé", 5628, 1158),
    ("Risque faible", "non prédit en défaut", 15761, 1536),
]
total_clients = sum(n[2] for n in NIVEAUX)
total_defauts = sum(n[3] for n in NIVEAUX)
# Contrôle en direct : le périmètre du dataset doit retrouver les totaux du notebook
assert (len(s12), int(s12["dpnm"].sum())) == (total_clients, total_defauts)
assert int(((s12["FLAG_CTX"] == 1) & (s12["MOIS_SORTIE_CTX"] == -1)).sum()) == NIVEAUX[0][2]

# Section 3 du notebook : le modèle seul sur le test (hors contentieux), à plusieurs rappels, seuils fixés sur le train
# (rappel visé, rappel obtenu sur le test, précision sur le test, clients signalés sur le test), en %
RAPPELS_TEST = [(30, 30.5, 42.0, 11.6), (44, 44.4, 34.7, 20.4), (60, 60.8, 28.3, 34.3), (70, 69.6, 24.3, 45.6), (80, 78.5, 22.0, 56.9)]
taux_hasard_test = test_ml["dpnm"].mean() * 100


entete_partie_6()
st.markdown("---")
st.header("6.4 Le modèle retenu, jugé sur le test : un outil pour classer les clients par niveau de risque", anchor="test")

# ------------------------------------------------------------------------------
st.subheader("1. Le test, lu une seule fois", anchor="lecture-unique")
st.markdown(f"""
Le test ({nombre_fr(len(test_ml))} clients hors contentieux, dont {nombre_fr(test_ml['dpnm'].sum())} défauts) a été mis de côté dès le départ et n'a servi à **aucun choix** : ni les variables, ni les réglages, ni le modèle, ni le seuil. **Tout a été fixé avant de le lire** : la version `ml_14`, CatBoost comme modèle de décision, le seuil qui détecte 60 % des défauts de l'entraînement (le taux de rappel minimal), et les bornes des niveaux de risque présentés plus bas. Le test n'a été lu qu'une fois, et aucun choix n'a été revu après.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Le test confirme la validation", anchor="resultat")
tableau_html(["Mesure", "Validation (entraînement)", "Test", "Marge d'incertitude du test"], [
    ["<b>Part des défauts détectés</b> (rappel)", "60,0 %", "<b>60,8 %</b>", "57,4 à 64,2 %"],
    ["<b>Précision des défauts prédits</b>", "27,3 %", "<b>28,3 %</b>", "26,1 à 30,4 %"],
    ["<b>Part des clients signalés</b>", "35,0 %", "<b>34,3 %</b>", "33,0 à 35,7 %"],
    ["<b>Score décisionnel F2</b>", "0,484", "<b>0,494</b>", "0,467 à 0,521"],
], largeurs=[34, 22, 16, 28])
st.caption(f"Marge d'incertitude : intervalle à 95 %, obtenu en tirant 2 000 fois des clients du test au hasard. Source : [évaluation finale]({EVALUATION}), section 2.")
st.markdown("""
Sur des clients qu'il n'a jamais vus, le modèle fait **ce que la validation annonçait**, et même un peu mieux : il détecte environ 6 défauts sur 10, et **environ un client signalé sur quatre est réellement en défaut**. Aucun surapprentissage caché : la méthode mesurait juste.

Les trois autres modèles, réentraînés pour information, restent au même niveau sur le test (score décisionnel F2 de 0,487 à 0,493) : l'égalité vue pendant les scénarios se confirme.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Le modèle seul : plus on cherche de défauts, plus chacun coûte", anchor="cout")
col_graphe, col_texte = st.columns(2, vertical_alignment="center")
with col_graphe:
    st.plotly_chart(figure_detection([f"{r[0]} %" + ("<br>(rappel minimal)" if r[0] == 60 else "") for r in RAPPELS_TEST],
                                     [r[1] for r in RAPPELS_TEST], [r[2] for r in RAPPELS_TEST], [r[3] for r in RAPPELS_TEST],
                                     taux_hasard_test), width='stretch')
with col_texte:
    st.markdown(f"""
Le seuil du taux de rappel minimal n'est qu'un point parmi d'autres. En le déplaçant, on choisit la part des défauts à aller chercher, sur les seuls clients hors contentieux :
- **30 % des défauts** : on ne signale que la tête de liste, environ un client sur dix, et **quatre signalés sur dix** sont en défaut ;
- **44 %** : un client sur cinq est signalé, un sur trois est en défaut ;
- **60 %** (le taux de rappel minimal) : un client sur trois est signalé, et la précision tombe à **un sur quatre** ;
- **70 % puis 80 %** : il faut signaler près de la moitié, puis plus de la moitié des clients, pour une précision qui se rapproche du hasard ({nombre_fr(taux_hasard_test, 0)} %, la ligne orange).

Chaque défaut supplémentaire coûte de plus en plus de bons clients signalés à tort.
""")
st.caption(f"Test seul ({nombre_fr(len(test_ml))} clients hors contentieux). Pour chaque part de défauts visée, le seuil est fixé sur l'entraînement, puis appliqué au test. Source : [évaluation finale]({EVALUATION}), section 3.")
st.markdown("""
**Avec le recul, vouloir attraper 60 % des défauts restants était trop ambitieux.** L'objectif paraissait réaliste au départ : les meilleurs modèles l'atteignaient dès le premier essai, sans réglage particulier. Mais à ce niveau, un client signalé sur quatre seulement est en défaut, et les scénarios ont montré que les modèles tiraient déjà des données tout ce qu'elles pouvaient leur apprendre : aucune variable n'a relevé cette précision (page 6.3). Plutôt qu'un seul seuil, le résultat se présente donc **par niveaux de risque**, qui distinguent la tête de liste, où le modèle est fiable, du reste des clients signalés.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Les niveaux de risque : la vraie façon d'utiliser le modèle", anchor="niveaux")
st.markdown("""
Les niveaux se lisent à partir du **taux de rappel minimal**. Le modèle prédit en défaut un client dont la probabilité dépasse le seuil qui détecte 60 % des défauts hors contentieux. Ces clients signalés sont coupés en deux :
- la **tête de liste**, les clients les plus risqués, qui apportent la première moitié de ces défauts (30 % des défauts hors contentieux) : c'est le **haut risque** ;
- le reste des clients signalés, qui apporte l'autre moitié (de 30 à 60 %) : c'est le **risque modéré**.

En dessous du seuil, les clients ne sont pas prédits en défaut : c'est le **risque faible**, où se trouvent les 40 % de défauts que le modèle manque. Au-dessus de tout, les clients au contentieux restent confiés à la **règle métier** (partie 5). Les bornes ont été fixées sur l'entraînement.
""")
lignes = []
for niveau, precision_libelle, clients, defauts in NIVEAUX:
    taux = defauts / clients * 100
    cout = nombre_fr((100 - taux) / taux, 1) if niveau != "Risque faible" else "—"
    lignes.append([f"<b>{niveau}</b> ({precision_libelle})", nombre_fr(clients), f"<b>{nombre_fr(taux, 1)} %</b>",
                   f"{nombre_fr(defauts / total_defauts * 100, 1)} %", cout])
tableau_html(["Niveau", "Clients", "Taux de défaut", "Part de tous les défauts", "Bons clients signalés à tort, pour un défaut trouvé"],
             lignes, largeurs=[34, 12, 14, 18, 22])
st.caption(f"Tout le périmètre du machine learning ({nombre_fr(total_clients)} clients avec une dette en septembre et un plafond de 500 000 NT$ ou moins, contentieux compris) : le test seul est petit, ce tableau décrit le portefeuille entier. Chaque client y est classé par un modèle qui ne l'a jamais vu à l'entraînement, et le test seul retrouve les mêmes taux. Bons clients signalés à tort pour un défaut trouvé : (100 − taux de défaut) / taux de défaut. Source : [évaluation finale]({EVALUATION}), sections 5 et 6.")
st.markdown("""
Chaque niveau appelle une réponse différente :
- **contentieux** : sept clients sur dix font défaut, une action forte se justifie ;
- **haut risque** : quatre sur dix, une surveillance renforcée ;
- **risque modéré** : deux sur dix, à peine plus que la moyenne ; chaque défaut trouvé coûte environ quatre bons clients signalés, une simple vigilance ;
- **risque faible** : un sur dix, pas d'action.
""")

st.markdown("""
Du haut risque au risque faible, le taux de défaut va de 1 à 4 : le modèle **classe** bien les clients. Mais même au haut risque, la majorité des clients paient : c'est un outil pour **prioriser** la surveillance, pas pour sanctionner un client. **Jusqu'où signaler est un choix de la banque**, selon ce que lui coûte une fausse alerte face à un défaut manqué.
""")

st.info("""
**Ce qu'il faut retenir** : lu une seule fois, sur des clients jamais vus, le test confirme la validation : le modèle détecte environ 6 défauts sur 10 hors contentieux, et un client signalé sur quatre est réellement en défaut. Plus on cherche de défauts, plus chacun coûte de fausses alertes : le modèle s'utilise donc par niveaux de risque, du contentieux (sept défauts sur dix) au risque faible (un sur dix), et c'est à la banque de choisir jusqu'où elle signale.
""")
