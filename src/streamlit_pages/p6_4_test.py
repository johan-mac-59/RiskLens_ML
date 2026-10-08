from streamlit_pages.commun import *
from sklearn.model_selection import train_test_split

# ==============================================================================
# PARTIE 6.4 : LE MODÈLE RETENU, JUGÉ SUR LE TEST
# La version finale (ml_14, CatBoost et son seuil) sur le test lu une seule fois, puis la présentation par
# niveaux de risque. Chiffres repris tels quels des sorties de lab_ML/evaluation_finale_test.ipynb (sections 2,
# 3, 4 et 6) : le modèle et ses probabilités ne sont pas dans le dépôt. Effectifs du test et taux de défaut
# calculés en direct (même découpage que lab_ML/creation_datasets_ML.ipynb).
# La comparaison « règle seule / règle + modèle » est en partie 8 (conclusion) ; le plafond et ses causes en 6.5.
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
    # Haut risque du notebook (2 809 clients, 1 161 défauts) coupé en deux par une borne ajoutée après la lecture du test
    # (07/10/2026) : seuil qui détecte 10 % des défauts sur les probabilités hors pli de l'entraînement (0,7727), comme
    # les bornes de 30 % et 60 %. Sur le test seul : 144 clients, 53,5 % de défaut (très haut) ; 416, 38,0 % (haut).
    ("Très haut risque", "coût en fausses alertes faible", 752, 386),
    ("Haut risque", "coût en fausses alertes moyen", 2057, 775),
    ("Risque modéré", "coût en fausses alertes élevé", 5628, 1158),
    ("Risque faible", "non prédit en défaut", 15761, 1536),
]
total_clients = sum(n[2] for n in NIVEAUX)
total_defauts = sum(n[3] for n in NIVEAUX)
# Contrôle en direct : le périmètre du dataset doit retrouver les totaux du notebook
assert (len(s12), int(s12["dpnm"].sum())) == (total_clients, total_defauts)
assert int(((s12["FLAG_CTX"] == 1) & (s12["MOIS_SORTIE_CTX"] == -1)).sum()) == NIVEAUX[0][2]

# Le modèle seul sur tous les clients hors contentieux (24 198), chacun classé par un modèle qui ne l'a jamais vu
# (entraînement : probabilités hors pli ; test : modèle final), à partir de data/ML/comparatif_global/ml_14_global.csv
# (enregistré par lab_ML/evaluation_finale_test.ipynb, section 6) : clients rangés du plus risqué au moins risqué,
# puis coupés à chaque part de défauts détectés. (rappel, précision, clients signalés), en %
# Points de 2 en 2 % jusqu'à 14 % (au-dessous, trop peu de clients pour une précision stable), puis de 5 en 5 % ;
# à 0 %, personne n'est signalé et la précision n'existe pas
RAPPELS_HORS_CTX = [(0, None, 0.0), (2, 53.4, 0.6), (4, 54.8, 1.2), (6, 50.8, 1.9), (8, 51.0, 2.5), (10, 51.3, 3.1),
                    (12, 50.2, 3.8), (14, 49.0, 4.6), (20, 45.5, 7.0), (25, 44.0, 9.1), (30, 41.3, 11.6),
                    (35, 38.4, 14.5), (40, 35.7, 17.9), (45, 33.2, 21.6), (50, 30.9, 25.8), (55, 29.1, 30.1), (60, 27.6, 34.7),
                    (65, 25.4, 40.8), (70, 24.1, 46.3), (75, 23.1, 51.7), (80, 21.8, 58.5), (85, 20.2, 67.1), (90, 19.1, 75.0)]
# Points dont la valeur est écrite sur le graphique (les autres au survol) : 10, 30, 60 et 90 %
POINTS_ETIQUETES = [i for i, r in enumerate(RAPPELS_HORS_CTX) if r[0] in (10, 30, 60, 90)]
# Contrôle en direct : la population hors contentieux du dataset doit retrouver celle du fichier (24 198 clients, 3 855 défauts)
assert (len(hors_ctx), int(hors_ctx["dpnm"].sum())) == (24198, 3855)
taux_hasard_hors_ctx = hors_ctx["dpnm"].mean() * 100

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
col_graphe, col_texte = st.columns([3, 2], vertical_alignment="center")
with col_graphe:
    # Abscisse : part des défauts détectés (rappel), par pas de 5 % ; deux courbes : clients signalés (le coût) et précision
    fig = figure_detection([r[0] for r in RAPPELS_HORS_CTX],
                                     [r[2] for r in RAPPELS_HORS_CTX], [r[1] for r in RAPPELS_HORS_CTX], taux_hasard_hors_ctx,
                                     nom_barres="Part des clients signalés",
                                     titre_x="Part des défauts détectés (rappel)", y_max=90, hauteur=580,
                                     en_courbes=True, etiquetes=POINTS_ETIQUETES, axe_numerique=True)
    fig.add_vline(x=60, line=dict(color=COULEURS["gris"], dash="dash", width=1),
                  annotation_text="rappel minimal", annotation_position="top", annotation_font_size=TAILLE_ETIQUETTE)
    st.plotly_chart(fig, width='stretch')
with col_texte:
    st.markdown(f"""
Le seuil du taux de rappel minimal n'est qu'un point parmi d'autres. En le déplaçant, on choisit la part des défauts à aller chercher, sur les seuls clients hors contentieux :
- **jusqu'à 10 % des défauts** : on ne signale que 3 % des clients, les plus risqués, et la précision reste stable autour de **un sur deux** : même tout en haut de la liste, rien n'est sûr ;
- **30 %** : environ un client sur dix est signalé, et **quatre sur dix** sont en défaut ;
- **60 %** (le taux de rappel minimal) : un client sur trois est signalé, et la précision tombe à **un sur quatre** ;
- **80 % puis 90 %** : il faut signaler plus de la moitié, puis les trois quarts des clients, pour une précision qui se rapproche du hasard ({nombre_fr(taux_hasard_hors_ctx, 0)} %, la ligne orange).

La précision forme donc un petit plateau en tête de liste, puis descend presque en ligne droite vers le hasard, pendant que la part des clients signalés grimpe de plus en plus vite : chaque défaut supplémentaire coûte de plus en plus de bons clients signalés à tort.
""")
st.caption(f"Tous les clients hors contentieux ({nombre_fr(len(hors_ctx))}), chacun classé par un modèle qui ne l'a jamais vu : probabilités hors pli pour l'entraînement, modèle final pour le test. Les clients sont rangés du plus risqué au moins risqué, puis la liste est coupée à chaque part de défauts. Le test seul donne les mêmes valeurs, à un point près. Source : [évaluation finale]({EVALUATION}), section 6 (notes de risque enregistrées).")
st.markdown("""
**Avec le recul, vouloir attraper 60 % des défauts restants était trop ambitieux.** L'objectif paraissait réaliste au départ : les meilleurs modèles l'atteignaient dès le premier essai, sans réglage particulier. Mais à ce niveau, un client signalé sur quatre seulement est en défaut, et aucune des variables essayées n'a relevé cette précision (page 6.3). Plutôt qu'un seul seuil, le résultat se présente donc **par niveaux de risque**, qui distinguent la tête de liste, où le modèle est le plus précis, du reste des clients signalés.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Les niveaux de risque : la vraie façon d'utiliser le modèle", anchor="niveaux")
st.markdown("""
Les niveaux se lisent à partir du **taux de rappel minimal**. Le modèle prédit en défaut un client dont la probabilité dépasse le seuil qui détecte 60 % des défauts hors contentieux. Ces clients signalés sont répartis selon la part des défauts qu'ils apportent, en suivant le graphique :
- la **tête de liste**, les 10 premiers pourcents des défauts, où la précision forme un plateau : c'est le **très haut risque** ;
- les clients suivants, jusqu'à 30 % des défauts : c'est le **haut risque** ;
- le reste des clients signalés, de 30 à 60 % : c'est le **risque modéré**.

En dessous du seuil, les clients ne sont pas prédits en défaut : c'est le **risque faible**, où se trouvent les 40 % de défauts que le modèle manque. Au-dessus de tout, les clients au contentieux restent confiés à la **règle métier** (partie 5). Toutes les bornes sont fixées sur l'entraînement ; celles de 30 % et 60 % l'ont été avant la lecture du test, celle de 10 % après, au vu de la courbe, sans rien changer au modèle ni à son seuil. Le test la confirme : sur ses seuls clients, le très haut risque fait défaut à 53,5 %.
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
- **très haut risque** : un client sur deux, environ 3 % des clients hors contentieux : une action prioritaire ;
- **haut risque** : près de quatre sur dix, une surveillance renforcée ;
- **risque modéré** : deux sur dix, à peine plus que la moyenne des clients hors contentieux (environ 16 %) ; chaque défaut trouvé coûte environ quatre bons clients signalés, une simple vigilance ;
- **risque faible** : un sur dix, pas d'action.
""")

st.markdown("""
Un client du très haut risque fait défaut environ **cinq fois plus souvent** qu'un client du risque faible (51 % contre 10 %) : le modèle **classe** bien les clients. Mais même au très haut risque, un client sur deux paie : c'est un outil pour **prioriser** la surveillance, pas pour sanctionner un client. **Jusqu'où signaler est un choix de la banque**, selon ce que lui coûte une fausse alerte face à un défaut manqué.
""")

st.info("""
**Ce qu'il faut retenir** : lu une seule fois, le test valide le modèle : sur des clients jamais vus, il retrouve les résultats de la validation, sans surapprentissage caché. Sur toute la liste des clients hors contentieux, la précision forme un plateau en tête de liste, où environ la moitié des clients signalés font défaut, puis descend presque en ligne droite vers le hasard à mesure qu'on va chercher plus de défauts. Le modèle s'utilise donc par niveaux de risque, du très haut risque (la moitié des clients en défaut) au risque faible (un sur dix), à côté du contentieux confié à la règle métier ; jusqu'où signaler reste un choix de la banque.
""")

