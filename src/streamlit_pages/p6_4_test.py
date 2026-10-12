from streamlit_pages.commun import *
from sklearn.model_selection import train_test_split

# ==============================================================================
# PARTIE 6.4 : LE MODÈLE RETENU, JUGÉ SUR LE TEST
# La version finale (ml_17, CatBoost et son seuil) sur le test lu une seule fois, puis la présentation par
# niveaux de risque. Chiffres repris tels quels des sorties de lab_ML/evaluation_finale_test.ipynb (sections 2,
# 3, 4 et 6) : le modèle et ses probabilités ne sont pas dans le dépôt. Effectifs du test et taux de défaut
# calculés en direct (même découpage que lab_ML/creation_datasets_ML.ipynb).
# La comparaison « règles seules / règles + modèle » est en partie 8 (conclusion) ; le plafond et ses causes en 6.5.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
EVALUATION = f"{GH_RACINE}/lab_ML/evaluation_finale_test.ipynb"

df = load_data()
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
# Population du ML : sans les clients en incident à M ni en retard imminent (statut à M, comme creation_datasets_ML)
regles = s12["STATUT_INCIDENT"].isin(["En incident", "Retard imminent"])
hors_ctx = s12[~regles]
# Même découpage que lab_ML/creation_datasets_ML.ipynb : 80/20, stratifié sur dpnm, graine 42
_, test_ml = train_test_split(hors_ctx, test_size=0.2, stratify=hors_ctx["dpnm"], random_state=42)

# Section 6 du notebook : niveaux de risque sur tout le périmètre du ML (les deux populations des règles comprises),
# chaque client classé par un modèle qui ne l'a jamais vu. Les six tranches du notebook (10 % des défauts de
# l'entraînement chacune) sont regroupées comme dans les démos (bornes_niveaux.json : 10, 30 et 60 %) :
# très haut = tranche 1, haut = tranches 2 et 3, modéré = tranches 4 à 6. (niveau, libellé, clients, défauts)
NIVEAUX = [
    ("En incident", "règle métier, prédit en défaut", 3754, 2222),
    ("Retard imminent", "règle métier, prédit en défaut", 989, 649),
    ("Très haut risque", "tête de liste, jusqu'à 10 % des défauts", 783, 326),
    ("Haut risque", "de 10 à 30 % des défauts", 1015 + 1381, 304 + 312),
    ("Risque modéré", "de 30 à 60 % des défauts", 1501 + 1684 + 1811, 301 + 296 + 296),
    ("Risque faible", "non prédit en défaut", 14284, 1266),
]
total_clients = sum(n[2] for n in NIVEAUX)
total_defauts = sum(n[3] for n in NIVEAUX)
# Contrôles en direct : le périmètre du dataset doit retrouver les totaux du notebook
assert (len(s12), int(s12["dpnm"].sum())) == (total_clients, total_defauts)
for statut, (_, _, clients, defauts) in zip(["En incident", "Retard imminent"], NIVEAUX[:2]):
    population = s12[s12["STATUT_INCIDENT"] == statut]
    assert (len(population), int(population["dpnm"].sum())) == (clients, defauts)

# Le modèle seul sur tous les clients laissés au ML (22 459), chacun classé par un modèle qui ne l'a jamais vu
# (entraînement : probabilités hors pli ; test : modèle de décision), à partir de data/ML/comparatif_global/ml_17_global.csv
# (enregistré par lab_ML/evaluation_finale_test.ipynb, section 6) : clients rangés du plus risqué au moins risqué,
# puis coupés à chaque part de défauts détectés. (rappel, précision, clients signalés), en %
# Points de 2 en 2 % jusqu'à 14 % (au-dessous, trop peu de clients pour une précision stable), puis de 5 en 5 % ;
# à 0 %, personne n'est signalé et la précision n'existe pas
RAPPELS_HORS_CTX = [(0, None, 0.0), (2, 45.0, 0.6), (4, 42.7, 1.3), (6, 43.5, 1.9), (8, 42.9, 2.6), (10, 42.4, 3.3),
                    (12, 40.1, 4.1), (14, 38.7, 5.0), (20, 35.5, 7.8), (25, 32.1, 10.8), (30, 29.7, 13.9),
                    (35, 27.6, 17.5), (40, 26.6, 20.8), (45, 25.2, 24.7), (50, 24.1, 28.7), (55, 23.1, 32.9), (60, 22.1, 37.4),
                    (65, 21.2, 42.4), (70, 20.4, 47.5), (75, 19.7, 52.5), (80, 18.8, 58.9), (85, 17.9, 65.6), (90, 17.0, 73.2)]
# Points dont la valeur est écrite sur le graphique (les autres au survol) : 10, 30, 60 et 90 %
POINTS_ETIQUETES = [i for i, r in enumerate(RAPPELS_HORS_CTX) if r[0] in (10, 30, 60, 90)]
# Contrôle en direct : la population laissée au ML du dataset doit retrouver celle du fichier (22 459 clients, 3 101 défauts)
assert (len(hors_ctx), int(hors_ctx["dpnm"].sum())) == (22459, 3101)
taux_hasard_hors_ctx = hors_ctx["dpnm"].mean() * 100

entete_partie_6()
st.markdown("---")
st.header("6.4 Le modèle retenu, jugé sur le test : un outil pour classer les clients par niveau de risque", anchor="test")

# ------------------------------------------------------------------------------
st.subheader("1. Le test, lu une seule fois", anchor="lecture-unique")
st.markdown(f"""
Le test ({nombre_fr(len(test_ml))} clients laissés au machine learning, dont {nombre_fr(test_ml['dpnm'].sum())} défauts) a été mis de côté dès le départ et n'a servi à **aucun choix** : ni les variables, ni les réglages, ni le modèle, ni le seuil. **Tout a été fixé avant de le lire** : la version `ml_17`, CatBoost comme modèle de décision, le seuil qui détecte 60 % des défauts de l'entraînement (le taux de rappel minimal), et les bornes des niveaux de risque présentés plus bas. Le test n'a été lu qu'une fois, et aucun choix n'a été revu après.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Sur le test : la précision tient, le rappel est un peu en dessous", anchor="resultat")
tableau_html(["Mesure", "Validation (entraînement)", "Test", "Marge d'incertitude du test"], [
    ["<b>Part des défauts détectés</b> (rappel)", "60,0 %", "<b>55,8 %</b>", "51,9 à 59,8 %"],
    ["<b>Précision des défauts prédits</b>", "22,6 %", "<b>21,9 %</b>", "19,9 à 24,0 %"],
    ["<b>Part des clients signalés</b>", "36,7 %", "<b>35,2 %</b>", "33,7 à 36,6 %"],
    ["<b>Score décisionnel F2</b>", "0,451", "<b>0,426</b>", "0,396 à 0,455"],
    ["<b>ROC AUC</b> (capacité à classer les clients)", "0,690", "<b>0,675</b>", "0,652 à 0,697"],
], largeurs=[34, 22, 16, 28])
st.caption(f"Marge d'incertitude : intervalle à 95 %, obtenu en tirant 2 000 fois des clients du test au hasard. Source : [évaluation finale]({EVALUATION}), section 2.")
st.markdown(f"""
Sur des clients qu'il n'a jamais vus, le modèle **classe les clients comme la validation l'annonçait** : la précision, la part des clients signalés et le ROC AUC restent dans leur marge d'incertitude, tout près des valeurs de la validation. **Environ un client signalé sur cinq est réellement en défaut**, contre {nombre_fr(taux_hasard_hors_ctx, 0)} sur 100 au hasard.

**Le rappel est un peu en dessous** : au seuil fixé sur l'entraînement, le modèle détecte {nombre_fr(55.8, 1)} % des défauts du test, et sa marge d'incertitude s'arrête juste sous les 60 % visés. Le seuil vient de l'entraînement, le test a ses propres clients : sur ceux-là, il signale un peu moins de clients et retrouve un peu moins de défauts qu'annoncé. Le score décisionnel F2, qui réunit rappel et précision, baisse avec lui.

Les quatre autres modèles, réentraînés pour information, restent au même niveau sur le test (score décisionnel F2 de 0,413 à 0,441). Leur ordre change, mais tous restent dans la marge d'incertitude du modèle de décision : l'égalité vue pendant les scénarios se confirme.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Le modèle seul : plus on cherche de défauts, plus chacun coûte", anchor="cout")
col_graphe, col_texte = st.columns([3, 2], vertical_alignment="center")
with col_graphe:
    # Abscisse : part des défauts détectés (rappel) ; deux courbes : clients signalés (le coût) et précision
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
Le seuil du taux de rappel minimal n'est qu'un point parmi d'autres. En le déplaçant, on choisit la part des défauts à aller chercher, sur les seuls clients laissés au machine learning :
- **jusqu'à 10 % des défauts** : on ne signale que 3 % des clients, les plus risqués, et la précision reste stable autour de **quatre sur dix** : même tout en haut de la liste, rien n'est sûr ;
- **30 %** : environ un client sur sept est signalé, et **trois sur dix** sont en défaut ;
- **60 %** (le taux de rappel minimal) : plus d'un client sur trois est signalé, et la précision tombe à **un peu plus d'un sur cinq** ;
- **80 % puis 90 %** : il faut signaler plus de la moitié, puis près des trois quarts des clients, pour une précision qui se rapproche du hasard ({nombre_fr(taux_hasard_hors_ctx, 0)} %, la ligne orange).

La précision forme donc un petit plateau en tête de liste, puis descend vers le hasard, pendant que la part des clients signalés grimpe de plus en plus vite : chaque défaut supplémentaire coûte de plus en plus de bons clients signalés à tort.
""")
st.caption(f"Tous les clients laissés au machine learning ({nombre_fr(len(hors_ctx))}), chacun classé par un modèle qui ne l'a jamais vu : probabilités hors pli pour l'entraînement, modèle de décision pour le test. Les clients sont rangés du plus risqué au moins risqué, puis la liste est coupée à chaque part de défauts. Le test seul donne des valeurs proches, un peu plus hautes en tête de liste (environ 46 % de précision jusqu'à 10 % des défauts). Source : [évaluation finale]({EVALUATION}), sections 3 et 6 (notes de risque enregistrées).")
st.markdown("""
**Avec le recul, vouloir attraper 60 % des défauts restants était trop ambitieux.** L'objectif paraissait réaliste au départ : les meilleurs modèles l'atteignaient dès le premier essai, sans réglage particulier. Mais à ce niveau, un peu plus d'un client signalé sur cinq seulement est en défaut, et aucune des variables essayées n'a relevé cette précision (page 6.3). Plutôt qu'un seul seuil, le résultat se présente donc **par niveaux de risque**, qui distinguent la tête de liste, où le modèle est le plus précis, du reste des clients signalés.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Les niveaux de risque : la vraie façon d'utiliser le modèle", anchor="niveaux")
st.markdown("""
Les niveaux se lisent à partir du **taux de rappel minimal**. Le modèle prédit en défaut un client dont la probabilité dépasse le seuil qui détecte 60 % des défauts de l'entraînement. Ces clients signalés sont répartis selon la part des défauts qu'ils apportent, en suivant le graphique :
- la **tête de liste**, les 10 premiers pourcents des défauts, où la précision forme un plateau : c'est le **très haut risque** ;
- les clients suivants, jusqu'à 30 % des défauts : c'est le **haut risque** ;
- le reste des clients signalés, de 30 à 60 % : c'est le **risque modéré**.

En dessous du seuil, les clients ne sont pas prédits en défaut : c'est le **risque faible**, où se trouvent les défauts que le modèle manque. Au-dessus de tout, les clients **en incident** et en **retard imminent** restent confiés aux **règles métier** (partie 5). Toutes les bornes sont fixées sur l'entraînement, avant la lecture du test ; ce sont celles des démos (partie 7).
""")
lignes = []
for niveau, precision_libelle, clients, defauts in NIVEAUX:
    taux = defauts / clients * 100
    cout = nombre_fr((100 - taux) / taux, 1) if niveau != "Risque faible" else "—"
    lignes.append([f"<b>{niveau}</b> ({precision_libelle})", nombre_fr(clients), f"<b>{nombre_fr(taux, 1)} %</b>",
                   f"{nombre_fr(defauts / total_defauts * 100, 1)} %", cout])
tableau_html(["Niveau", "Clients", "Taux de défaut", "Part de tous les défauts", "Bons clients signalés à tort, pour un défaut trouvé"],
             lignes, largeurs=[34, 12, 14, 18, 22])
st.caption(f"Tout le périmètre du machine learning ({nombre_fr(total_clients)} clients avec une dette en septembre et un plafond de 500 000 NT$ ou moins, population en incident et retard imminent compris) : le test seul est petit, ce tableau décrit le portefeuille entier. Chaque client y est classé par un modèle qui ne l'a jamais vu à l'entraînement. Sur le test seul, les taux de défaut sont proches : 46,1 % au très haut risque, 27,3 % au haut risque, 15,3 % au risque modéré, 9,4 % au risque faible. Bons clients signalés à tort pour un défaut trouvé : (100 − taux de défaut) / taux de défaut. Source : [évaluation finale]({EVALUATION}), sections 5 et 6.")

taux_niveau = {n[0]: n[3] / n[2] * 100 for n in NIVEAUX}
st.markdown(f"""
Chaque niveau appelle une réponse différente :
- **en incident** et **retard imminent** : six clients sur dix font défaut, ou plus ; une action forte se justifie ;
- **très haut risque** : environ quatre clients sur dix, environ 3 % des clients laissés au machine learning : une action prioritaire ;
- **haut risque** : environ un sur quatre, une surveillance renforcée ;
- **risque modéré** : moins de deux sur dix, à peine plus que la moyenne des clients laissés au machine learning ({nombre_fr(taux_hasard_hors_ctx, 0)} %) ; chaque défaut trouvé coûte plus de quatre bons clients signalés, une simple vigilance ;
- **risque faible** : moins d'un sur dix, pas d'action.

Un client du très haut risque fait défaut environ **{nombre_fr(taux_niveau['Très haut risque'] / taux_niveau['Risque faible'], 0)} fois plus souvent** qu'un client du risque faible ({nombre_fr(taux_niveau['Très haut risque'], 0)} % contre {nombre_fr(taux_niveau['Risque faible'], 0)} %) : le modèle **classe** bien les clients. Mais même au très haut risque, plus d'un client sur deux paie : c'est un outil pour **prioriser** la surveillance, pas pour sanctionner un client. **Jusqu'où signaler est un choix de la banque**, selon ce que lui coûte une fausse alerte face à un défaut manqué.
""")

st.info("""
**Ce qu'il faut retenir** : lu une seule fois, le test confirme que le modèle classe les clients comme la validation l'annonçait : précision et capacité à classer tiennent sur des clients jamais vus. Au seuil fixé sur l'entraînement, il retrouve un peu moins de défauts que prévu (56 % au lieu de 60 %). Sur toute la liste des clients laissés au machine learning, la précision forme un plateau en tête de liste, où environ quatre clients signalés sur dix font défaut, puis descend vers le hasard à mesure qu'on va chercher plus de défauts. Le modèle s'utilise donc par niveaux de risque, du très haut risque (quatre clients sur dix en défaut) au risque faible (moins d'un sur dix), à côté de la population en incident et du retard imminent, confiés aux règles métier ; jusqu'où signaler reste un choix de la banque.
""")
