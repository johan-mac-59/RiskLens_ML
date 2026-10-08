import json
from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 8.1 : PEUT-ON PRÉVOIR LE DÉFAUT ? UNE RÈGLE MÉTIER, PUIS UN MODÈLE
# 1. La règle seule (partie 5) : entraînement et test recalculés en direct, données d'origine reprises de 05_02 (D19).
# 2. Le système complet sur tout le périmètre : niveaux repris de lab_ML/evaluation_finale_test.ipynb, section 6
#    (mêmes chiffres que la page 6.4), contrôlés en direct sur le dataset.
# 3. Le système du projet face au modèle brut de la démo 3, sur les 5 441 clients de la démo 1 : calcul en direct
#    (commun.py, systemes_sur_clients_demo) ; puis le comparatif global (lab_ML/comparatif_global/niveaux_de_risque_global.ipynb),
#    repris tels quels : les probabilités hors pli ne sont pas dans le dépôt.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
CONTENTIEUX = f"{GH_RACINE}/src/05_02_EDA_contentieux.ipynb"
EVALUATION = f"{GH_RACINE}/lab_ML/evaluation_finale_test.ipynb"
NIVEAUX_GLOBAL = f"{GH_RACINE}/lab_ML/comparatif_global/niveaux_de_risque_global.ipynb"
HYPOTHESES = f"{GH_RACINE}/docs/hypotheses_et_conclusions.md"
ESSAI_CTX = f"{GH_RACINE}/lab_ML/comparatif_global/essai_jeu_corrige_deux_populations.ipynb"

# ------------------------------------------------------------------------------
# 1. La règle seule (mêmes calculs que la page 5.6)
# ------------------------------------------------------------------------------
df, s12, train, test = donnees_partie_5()
# 05_02_EDA_contentieux, cellules 41 et 45 : règle appliquée aux 30 000 lignes d'origine (codifications brutes, aucun filtre)
ORIGINE = {"precision": 70.49, "captes": 32.01}


def bilan_regle(d):
    ctx = d["STATUT"] == "Au contentieux"
    return {"part_clients": ctx.mean() * 100, "precision": d.loc[ctx, "dpnm"].mean() * 100,
            "captes": d.loc[ctx, "dpnm"].sum() / d["dpnm"].sum() * 100}


b_train, b_test = bilan_regle(train), bilan_regle(test)

# ------------------------------------------------------------------------------
# 2. Le système complet sur tout le périmètre (évaluation finale, section 6 ; mêmes niveaux que la page 6.4)
# ------------------------------------------------------------------------------
NIVEAUX = [
    ("Contentieux", 3004, 2117),
    ("Très haut risque", 752, 386),
    ("Haut risque", 2057, 775),
    ("Risque modéré", 5628, 1158),
    ("Risque faible", 15761, 1536),
]
total_clients = sum(n[1] for n in NIVEAUX)
total_defauts = sum(n[2] for n in NIVEAUX)
assert (len(s12), int(s12["dpnm"].sum())) == (total_clients, total_defauts)
taux_perimetre = total_defauts / total_clients * 100
cumul_clients, cumul_defauts, etapes = 0, 0, []
# Le risque faible n'est pas signalé : on s'arrête au seuil qui trouve 60 % des défauts hors contentieux
for _, clients, defauts in NIVEAUX[:4]:
    cumul_clients += clients
    cumul_defauts += defauts
    etapes.append((cumul_defauts / total_defauts * 100, cumul_defauts / cumul_clients * 100, cumul_clients / total_clients * 100))

# ------------------------------------------------------------------------------
# 3. Le système du projet face au modèle brut, sur les mêmes clients (calcul en direct)
# ------------------------------------------------------------------------------
clients = systemes_sur_clients_demo()
y = clients["dpnm"].values
hasard = y.mean() * 100
score_projet = score_systeme_projet(clients)
bornes = json.loads((BASE_DIR / "lab_ML" / "demo_ML" / "bornes_niveaux.json").read_text(encoding="utf-8"))
# Points de décision du projet : le contentieux seul, puis chaque niveau du modèle ajouté (seuils fixés sur l'entraînement)
PALIERS = [("Contentieux seul", None), ("+ très haut risque", "tres_haut_risque"), ("+ haut risque", "haut_risque"),
           ("+ risque modéré", "risque_modere")]
comparaison = []
for libelle, cle in PALIERS:
    signales = clients["contentieux"].values if cle is None else (clients["contentieux"].values | (clients["proba_ml14"].values >= bornes[cle]))
    rappel = y[signales].sum() / y.sum() * 100
    precision_projet = y[signales].mean() * 100
    precision_brut, signales_brut = precision_au_rappel(y, clients["score_brut"], rappel)
    comparaison.append((libelle, rappel, precision_projet, signales.mean() * 100, precision_brut, signales_brut))
auc_projet = aire_roc(y, score_projet)
auc_brut = aire_roc(y, clients["score_brut"])
ecart_max = max(abs(c[2] - c[4]) for c in comparaison)

# Comparatif global, sur les 27 202 clients du périmètre (H13) : (approche, règle seule, + haut risque, + risque modéré),
# chaque palier en (part des défauts détectés, précision), en %
COMPARATIF_GLOBAL = [
    ("<b>Version finale du projet</b> : règle du contentieux, puis <code>ml_14</code> (21 variables)", (35.4, 70.5), (54.9, 56.4), (74.3, 38.8)),
    ("Règle du contentieux, puis un modèle sur les 23 variables d'origine", (35.4, 70.5), (55.7, 56.3), (73.4, 39.3)),
    ("Règle du contentieux, puis un modèle <b>sans aucune codification</b> (montants, plafond, démographie)", (35.4, 70.5), (55.2, 53.4), (73.4, 38.4)),
    ("Codification de la banque (2 ou plus en septembre), puis un modèle sur les 23 variables d'origine", (36.3, 69.5), (54.2, 58.4), (71.3, 41.4)),
    ("Codification de la banque, puis un modèle sans aucune codification", (36.3, 69.5), (53.3, 56.2), (71.6, 40.3)),
]

# ==============================================================================
entete_partie_8()
st.markdown("---")
st.header("8.1 Peut-on prévoir le défaut ? Une règle métier, puis un modèle", anchor="reponse")
st.markdown("""
La réponse se construit en deux temps, dans l'ordre du projet : d'abord une **règle métier**, sans aucun machine learning, pour les clients au contentieux (partie 5) ; puis un **modèle** pour tous les autres (partie 6). Cette page mesure ce que vaut chacun, puis ce que vaut le tout face à un modèle lancé directement sur les données brutes.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Premier temps : une règle métier, sans machine learning", anchor="regle")
st.markdown(f"""
La règle du contentieux (deux codifications de retard d'affilée, sans sortie constatée, page 5.3) prédit en défaut tous les clients qu'elle retient. Elle n'a été réglée sur aucun défaut : elle vient de la logique métier, et le défaut n'a servi qu'à la vérifier.
- **Elle retient peu de clients** : environ {nombre_fr(b_test['part_clients'], 0)} % des clients actifs.
- **Elle a raison sept fois sur dix** : {nombre_fr(b_train['precision'], 1)} % de ces clients font défaut sur l'entraînement, {nombre_fr(b_test['precision'], 1)} % sur le test, jamais vu, et {nombre_fr(ORIGINE['precision'], 1)} % sur les 30 000 clients des données d'origine, sans aucun nettoyage.
- **Elle trouve à elle seule environ un tiers des défauts** : {nombre_fr(b_train['captes'], 1)} % sur l'entraînement, {nombre_fr(b_test['captes'], 1)} % sur le test.

**Sans aucun modèle, une règle fondée sur les codifications de la banque prédit donc déjà un tiers des défauts**, et n'importe quel conseiller peut l'appliquer et l'expliquer. Ces codifications ne reflètent pas fidèlement le comportement du client : ce sont des étiquettes posées par la banque, parfois en décalage avec les paiements (pages 3.3 et 5.2). C'est pourquoi la règle les lit après correction des faux retards, et en tenant compte des paiements de septembre. Ce tiers des défauts est donc prévu par **l'étiquette de la banque**, plus que par le comportement lui-même.
""")
st.caption(f"Entraînement et test du découpage de la partie 5 : calculés en direct (détail en page 5.6). Données d'origine : résultats de l'étude, repris tels quels ([05_02_EDA_contentieux.ipynb]({CONTENTIEUX}), cellules 41 et 45).")
st.markdown(f"""
**Pourquoi prédire en défaut tout le contentieux, sans exception ?** Trois clients au contentieux sur dix ne font pas défaut : des modèles ont donc été entraînés sur ces seuls clients, pour repérer ceux qui vont en sortir. Avec une exigence métier stricte, ne sortir un client du contentieux que s'il a au moins neuf chances sur dix de payer, car sortir à tort un client qui sera en défaut revient à abandonner une créance, **aucun modèle ne trouve de clients à sortir** sans risquer de sortir des clients en défaut. Au contentieux, les modèles trient à peine mieux que le hasard (ROC AUC d'environ 0,55 à 0,61), avec ou sans les codifications : rien dans les six mois de données ne distingue les clients qui paieront. **La règle reste donc la seule décision défendable** pour ces clients.
""")
st.caption(f"Essai mené sur les clients au contentieux du dataset nettoyé, avec quatre modèles et trois jeux de variables (toutes, sans les codifications, codifications seules), chaque client noté par un modèle qui ne l'a pas vu : [essai à deux populations]({ESSAI_CTX}), section 3 ; chiffres repris tels quels, les probabilités ne sont pas dans le dépôt. Raisonnement : [hypothèses et conclusions]({HYPOTHESES}), H10.")

# ------------------------------------------------------------------------------
st.subheader("2. Deuxième temps : le modèle sur les autres clients, et jusqu'où signaler", anchor="systeme")
libelles = ["Contentieux<br>seul", "+ très haut<br>risque", "+ haut risque", "+ risque modéré"]
col_graphe, col_texte = st.columns(2, vertical_alignment="center")
with col_graphe:
    st.plotly_chart(figure_detection(libelles, [e[0] for e in etapes], [e[1] for e in etapes], taux_perimetre,
                                     info_survol=("Clients signalés", [e[2] for e in etapes]), etiquettes_barres_dedans=True),
                    width='stretch')
with col_texte:
    st.markdown(f"""
Pour les autres clients, le modèle ne dit pas « défaut » ou « pas défaut » : il les **range du plus au moins risqué**, en niveaux de risque (page 6.4). Sur tout le portefeuille, on signale d'abord le contentieux, puis on descend d'un niveau à la fois.

- **Le contentieux seul** trouve environ **un tiers des défauts**, avec une précision de **sept sur dix**, en signalant {nombre_fr(etapes[0][2], 0)} % des clients.
- **Avec le très haut risque**, la tête de liste du modèle, {nombre_fr(etapes[1][0], 0)} % des défauts sont trouvés, avec une précision encore de {nombre_fr(etapes[1][1], 0)} %.
- **Avec le haut risque**, plus de la moitié des défauts sont trouvés, et plus d'un client signalé sur deux est en défaut.
- **Avec le risque modéré**, le dernier niveau signalé, environ **trois quarts des défauts** sont trouvés, mais en signalant {nombre_fr(etapes[3][2], 0)} % des clients : la précision tombe à environ quatre sur dix. Le modèle s'arrête là : son seuil a été fixé pour trouver 60 % des défauts des clients hors contentieux, l'objectif retenu dès le départ (page 6.2).
- **Le risque faible n'est pas signalé** : il garde environ un quart des défauts, mais seulement {nombre_fr(NIVEAUX[4][2] / NIVEAUX[4][1] * 100, 0)} % de ses clients font défaut. Aller les chercher coûterait trop cher : il faudrait signaler beaucoup plus de clients, avec une précision qui se rapproche du hasard à mesure qu'on descend vers les derniers clients de la liste (page 6.4, section 3). Une partie de ces défauts ont d'ailleurs le profil des bons clients, et aucun modèle ne les distingue (page 6.5).

Chaque niveau ajouté rapporte de moins en moins de défauts par client signalé. **Jusqu'où signaler est un choix de la banque**, selon ce que lui coûte une fausse alerte face à un défaut manqué.
""")
st.caption(f"Valeurs cumulées : chaque étape ajoute un niveau aux précédents ; barres : part de tous les défauts détectés ; courbe : précision des défauts prédits. Tout le périmètre ({nombre_fr(total_clients)} clients avec une dette en septembre et un plafond de 500 000 NT$ ou moins), chaque client classé par un modèle qui ne l'a jamais vu ; mêmes chiffres que le tableau des niveaux de risque de la page 6.4. Source : [évaluation finale]({EVALUATION}), section 6.")

# ------------------------------------------------------------------------------
st.subheader("3. Le travail du projet fait-il mieux qu'un modèle lancé sur les données brutes ?", anchor="modele-brut")
st.markdown(f"""
Le projet a pris un long chemin : nettoyage, étude du contentieux, colonnes construites, scénarios. Un modèle lancé directement sur les 23 variables d'origine, sans rien de tout cela, ferait-il moins bien ? Pour le savoir, les deux systèmes sont comparés **sur les mêmes clients**, les {nombre_fr(len(clients))} clients de la démo 1, qu'**aucun des deux n'a vus** à l'entraînement :
- le **système du projet** : la règle du contentieux, puis le modèle retenu (`ml_14`) pour les autres clients (démo 1, page 7.2) ;
- le **modèle brut** : un CatBoost entraîné sur les 30 000 clients d'origine, sans nettoyage ni règle, chaque client noté par un modèle qui ne l'a pas vu (démo 3, page 7.4).

Pour comparer équitablement, on demande au modèle brut de trouver **la même part des défauts** que le système du projet à chacun de ses paliers, puis on compare la précision des deux. Le calcul est fait en direct.
""")
fig = go.Figure()
x = [c[0] for c in comparaison]
for nom, i, couleur in (("Système du projet (règle + modèle)", 2, COULEURS["bordeaux"]), ("Modèle brut (23 variables d'origine)", 4, COULEURS["bleu_pale"])):
    valeurs = [c[i] for c in comparaison]
    fig.add_trace(go.Bar(x=x, y=valeurs, name=nom, marker_color=couleur, text=[f"{nombre_fr(v, 0)} %" for v in valeurs],
                         textposition="outside", textfont=dict(size=TAILLE_ETIQUETTE), cliponaxis=False,
                         hovertemplate="%{x}<br>" + nom + " : %{y:.1f} %<extra></extra>"))
fig.add_hline(y=hasard, line=dict(color=COULEURS["orange"], dash="dot", width=2))
fig.add_trace(go.Scatter(x=[None], y=[None], name=f"Au hasard ({nombre_fr(hasard, 0)} %)", mode="lines",
                         line=dict(color=COULEURS["orange"], dash="dot", width=2)))
fig.update_xaxes(type="category")
fig.update_layout(barmode="group", yaxis_title="Précision des défauts prédits (%)", yaxis_range=[0, 100], height=430, separators=", ",
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
col_graphe, col_tableau = st.columns([3, 2], vertical_alignment="center")
with col_graphe:
    st.plotly_chart(fig, width='stretch')
with col_tableau:
    tableau_html(["Palier du projet", "Part des défauts trouvés", "Précision : projet", "Précision : modèle brut"],
                 [[c[0].replace("<br>", " "), f"{nombre_fr(c[1], 0)} %", f"{nombre_fr(c[2], 1)} %", f"{nombre_fr(c[4], 1)} %"] for c in comparaison]
                 + [["<b>Qualité du tri</b> (ROC AUC)", "—", nombre_fr(auc_projet, 3), nombre_fr(auc_brut, 3)]],
                 largeurs=[34, 22, 22, 22])
st.caption(f"{nombre_fr(len(clients))} clients, dont {nombre_fr(int(y.sum()))} en défaut ({nombre_fr(hasard, 1)} %) : le test du machine learning et 20 % des clients au contentieux du périmètre, tirés de la même façon. Paliers du projet : seuils du modèle fixés sur l'entraînement (page 6.4). Modèle brut : clients rangés selon son score, signalés jusqu'à trouver la même part des défauts. ROC AUC : probabilité qu'un client en défaut soit rangé avant un bon client (0,5 au hasard, 1 pour un tri parfait) ; pour le projet, le contentieux est rangé en tête, ex aequo. Le modèle brut a appris sur plus de clients (environ 24 000 par modèle, contentieux compris, contre environ 19 000 pour le projet).")
st.markdown(f"""
**Les deux systèmes font jeu égal.** À chaque palier, les précisions ne s'écartent que de {nombre_fr(ecart_max, 1)} points au plus, tantôt dans un sens, tantôt dans l'autre, et la qualité du tri est la même. Sur environ {nombre_fr(round(y.sum(), -2))} défauts, de tels écarts ne se distinguent pas du hasard de l'échantillon.

Ce n'est pas un hasard de ces clients-là. Le comparatif global du projet, mené sur tout le périmètre avec plusieurs façons de séparer le contentieux et plusieurs jeux de variables, arrive au même constat : **toutes les approches tombent sur la même courbe**.
""")
tableau_html(["Approche", "Règle seule", "+ haut risque", "+ risque modéré"],
             [[nom] + [f"{nombre_fr(p[0], 1)} % des défauts<br>précision {nombre_fr(p[1], 1)} %" for p in paliers] for nom, *paliers in COMPARATIF_GLOBAL],
             largeurs=[40, 20, 20, 20])
st.caption(f"Tout le périmètre (27 202 clients), chaque client classé par un modèle qui ne l'a pas vu. Trois paliers : la règle seule, puis les clients du modèle jusqu'à 30 % des défauts hors contentieux (haut risque, très haut risque compris), puis jusqu'à 60 % (risque modéré). Chiffres repris tels quels du [comparatif des niveaux de risque]({NIVEAUX_GLOBAL}) : les probabilités des modèles ne sont pas dans le dépôt. Raisonnement complet : [hypothèses et conclusions]({HYPOTHESES}), H12 et H13.")
st.markdown("""
Trois enseignements :
- **Le travail sur les variables n'a pas déplacé la courbe** : la version finale fait comme un modèle sur les 23 variables d'origine, à chaque palier.
- **La règle du contentieux et la codification de la banque se valent** : la codification de septembre retient un peu plus de clients, et un peu plus de fausses alertes ; c'est un autre point de la même courbe.
- **Le comportement seul fait presque aussi bien** : sans aucune codification, avec les seuls montants (factures et paiements), le plafond et la démographie, le modèle trouve autant de défauts, pour une précision à peine plus basse. Une fois le contentieux mis à part, ce sont les montants qui portent l'essentiel de ce qui est prévisible.

**Ce que le projet apporte n'est donc pas un meilleur score, mais un système défendable, à score égal** :
- un tiers des défauts est expliqué par une **règle métier lisible**, sans modèle ;
- le modèle du projet n'utilise **aucune donnée démographique**, alors que le modèle brut se sert du genre, de l'âge, du niveau d'études et du statut marital (page 6.6) ;
- les données sont **nettoyées**, chaque correction justifiée, et chaque client reçoit un **niveau de risque** que l'on peut expliquer.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Le verdict", anchor="verdict")
taux_tres_haut = NIVEAUX[1][2] / NIVEAUX[1][1] * 100
taux_faible = NIVEAUX[4][2] / NIVEAUX[4][1] * 100
# Le verdict de la problématique, dans l'encadré bleu : c'est l'essentiel de la page et du site.
# La problématique citée en tête de l'encadré est écrite en 20 px (16 px pour le reste du texte).
st.markdown("<style>.st-key-verdict blockquote p { font-size: 20px; }</style>", unsafe_allow_html=True)
st.container(key="verdict").info(f"""
> *« Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ? »*

**Oui, en partie : on peut prévoir une grande part des défauts, mais pas le défaut de chaque client.** Le verdict se lit en reprenant la question, morceau par morceau.

**« Prévoir le défaut » : oui, pour une part importante des défauts.**
- La règle du contentieux, sans aucun modèle, trouve environ un tiers des défauts ({nombre_fr(b_test['captes'], 1)} % sur le test), avec {nombre_fr(b_test['precision'], 1)} % de prédictions justes.
- Le modèle y ajoute les clients les plus risqués parmi les autres. Avec le très haut et le haut risque, **{nombre_fr(etapes[2][0], 0)} % des défauts du portefeuille sont trouvés**, en signalant {nombre_fr(etapes[2][2], 0)} % des clients, dont **{nombre_fr(etapes[2][1], 0)} % sont réellement en défaut**, contre {nombre_fr(taux_perimetre, 0)} % pour des clients tirés au hasard.
- Le modèle sépare nettement les clients : un client du très haut risque fait défaut **{nombre_fr(taux_tres_haut / taux_faible, 0)} fois plus souvent** qu'un client du risque faible ({nombre_fr(taux_tres_haut, 0)} % contre {nombre_fr(taux_faible, 0)} %).

**« D'un client » : non, pas à coup sûr.** Même en tête de liste, un client signalé sur deux paie. Et environ un tiers des défauts des clients hors contentieux ont exactement le profil des bons clients : pas de retard, un paiement en septembre, la même note donnée par les modèles ; aucun modèle ne les distingue (page 6.5). Le comportement **classe** les clients par niveau de risque ; il ne **désigne** pas celui qui fera défaut. Pour une banque, c'est un outil pour prioriser la surveillance, pas pour décider seul du sort d'un client.

**« Uniquement sur son comportement transactionnel » : oui, mais à nuancer.** Les six mois de données mêlent deux choses : le **comportement du client** (factures, paiements, plafond) et les **codifications**, l'étiquette que la banque pose sur ses retards, qui ne reflète pas toujours fidèlement ses paiements. Le tiers de défauts trouvé par la règle vient d'abord de cette étiquette. Pour les autres clients, en revanche, le comportement seul fait presque aussi bien que les codifications : les montants facturés et payés portent l'essentiel de ce qui reste prévisible (section 3). Le modèle retenu n'utilise d'ailleurs aucune donnée démographique : ni l'âge, ni le genre, ni le niveau d'études, ni le statut marital.

**« Malgré un manque d'informations économiques globales » : ce manque-là n'a presque pas pesé.** Les modèles des banques tiennent compte de la conjoncture (chômage, inflation, croissance) ; **le projet n'a intégré aucune donnée économique de l'époque**. Ici, elle ne pouvait rien départager : les six mois de données couvrent la même période pour tous les clients, qui vivent tous la même conjoncture. Et en 2005, l'économie taïwanaise allait bien : la crise venait du crédit, pas de l'économie (partie 0). Sans ces informations, le projet atteint le niveau de l'étude de 2009 (page 8.2), et tous les modèles essayés tombent sur la même courbe (section 3). Leur absence pèserait ailleurs : un modèle qui ignore la conjoncture ne vaut pas tel quel pour une autre période.

**Ce qui manque davantage, ce sont les données économiques du client lui-même** : son revenu, ses autres crédits, son loyer, son endettement total, son reste à vivre. Le dataset n'en contient aucune. Or la crise de 2005 est née d'un endettement réparti entre plusieurs banques, des clients payant une carte avec une autre (partie 0) : la banque ne voit ici que ses propres comptes. On ne peut pas mesurer ce que ces données auraient apporté, mais une partie des défauts qui ne s'annoncent pas dans l'historique (page 6.5) pourrait s'y cacher, à côté d'un défaut dont la définition n'est pas documentée.
""")
