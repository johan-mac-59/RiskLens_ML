from streamlit_pages.commun import *
from sklearn.model_selection import train_test_split

# ==============================================================================
# PARTIE 6.2 : LA NOUVELLE DÉMARCHE
# Le redémarrage du machine learning après l'étude du contentieux : une nouvelle base (clients actifs, sans le
# contentieux à M), ce qui change par rapport à la première itération, les questions qui ont guidé la méthode.
# Une démarche, pas un journal de bord : le détail des versions de la méthode et leur effet mesuré sont dans
# lab_ML/methodologie_ML.md (section 11). Effectifs calculés en direct (population de creation_datasets_ML) ;
# les résultats des modèles sont présentés en 6.3.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
METHODOLOGIE = f"{GH_RACINE}/lab_ML/methodologie_ML.md"

df = load_data()
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
au_ctx = (s12["FLAG_CTX"] == 1) & (s12["MOIS_SORTIE_CTX"] == -1)
hors_ctx = s12[~au_ctx]
# Même découpage que lab_ML/creation_datasets_ML.ipynb : 80/20, stratifié sur dpnm, graine 42
train_ml, test_ml = train_test_split(hors_ctx, test_size=0.2, stratify=hors_ctx["dpnm"], random_state=42)

entete_partie_6()
st.markdown("---")
st.header("6.2 La nouvelle démarche : séparer le contentieux du reste", anchor="demarche")

# ------------------------------------------------------------------------------
st.subheader("1. Une nouvelle base : les clients actifs, sans le contentieux", anchor="nouvelle-base")
st.markdown(f"""
La première itération mélangeait deux populations (page 6.1). La partie 5 les a séparées : **les clients au contentieux en octobre sont confiés à la règle métier**, qui les prédit tous en défaut (page 5.6). Le machine learning reprend donc sur une base plus homogène :
- le **périmètre S12** : les clients qui ont une dette en septembre, avec un plafond de 500 000 NT$ ou moins ({nombre_fr(len(s12))} clients) ;
- **sans les {nombre_fr(au_ctx.sum())} clients au contentieux en octobre** : restent **{nombre_fr(len(hors_ctx))} clients en gestion normale**, dont {nombre_fr(hors_ctx['dpnm'].mean() * 100, 1)} % font défaut ;
- un **découpage propre au machine learning** : {nombre_fr(len(train_ml))} clients pour l'entraînement (80 %), {nombre_fr(len(test_ml))} pour le test (20 %), avec la même part de défauts dans les deux. **Le test n'est lu qu'une seule fois, à la toute fin**, sur le modèle figé : tous les choix se font sur l'entraînement.

Ces deux jeux sont créés **directement à partir du nettoyage le plus avancé** (partie 3), sans dépendre de l'exploration : n'importe qui peut les recréer à l'identique à partir des données d'origine.

Cette base est **plus difficile** que celle de la première itération : les défauts les plus faciles à repérer, ceux du contentieux, sont partis à la règle métier. Les scores des modèles y sont mécaniquement plus bas, sans que les modèles soient moins bons ; la vraie comparaison se fera sur le système complet, la règle pour le contentieux et le modèle pour le reste (partie 8).
""")

# ------------------------------------------------------------------------------
st.subheader("2. Ce qui change par rapport à la première itération", anchor="changements")
st.markdown("Les données changent, et la méthode aussi : elle devient automatique, reproductible et tracée.")
tableau_html(["", "Première itération", "Nouvelle démarche"], [
    ["<b>Population</b>", "Tout le dataset, contentieux compris", "Clients actifs en gestion normale ; le contentieux est confié à la règle métier"],
    ["<b>Préparation des variables</b>", "Codifications de paiement traitées comme des catégories ordonnées : un retard rare, absent des clients d'apprentissage, pouvait être lu comme celui d'un excellent payeur",
     "Codifications traitées comme des nombres (un cran par mois de retard) ; paiements passés au logarithme, pour que les petits et moyens paiements ne soient pas écrasés par quelques très gros remboursements ; toutes les variables mises à la même échelle"],
    ["<b>Réglage des modèles</b>", "Recherche (GridSearch), puis grilles retouchées à la main pour limiter le surapprentissage",
     "Une boucle automatique : elle corrige elle-même ses grilles, tour après tour, et s'arrête quand le modèle est stable"],
    ["<b>Point de décision</b>", "Seuil de 0,5 pour tous les modèles : chacun trouvait une part différente des défauts",
     "Un <b>taux de rappel minimal</b>, exigence métier : chaque modèle doit trouver au moins cette part des défauts ; son seuil en découle"],
    ["<b>Score pour régler les modèles</b>", "Moyenne du ROC AUC et du F2 score au seuil de 0,5",
     "La <b>précision des défauts prédits</b> à ce point : la part des clients prédits en défaut qui font réellement défaut"],
    ["<b>Surapprentissage</b>", "Surveillé à l'œil, avec une limite fixe",
     "Une limite relative, appliquée par la boucle, et un plancher pour que le modèle apprenne quand même"],
    ["<b>Classement des modèles</b>", "Le score de décision", "Un « score décisionnel F2 », calculé à la fin, qui réunit précision et part des défauts trouvés"],
    ["<b>Traçabilité</b>", "Un tableau de suivi tenu à la main",
     "Résultats de chaque modèle enregistrés à chaque lancement, avec la trace du code et des données qui les ont produits ; chaque évolution de la méthode est datée et mesurée"],
], largeurs=[20, 37, 43])
st.caption(f"Détail de la méthode, de ses versions successives et de leur effet mesuré : [méthodologie du machine learning]({METHODOLOGIE}).")

# ------------------------------------------------------------------------------
st.subheader("3. Les questions qui ont guidé la méthode", anchor="questions")
st.markdown(f"""
La méthode ne s'est pas écrite d'un trait : elle s'est construite en relançant le même premier scénario, sur les seules variables d'origine, et en répondant à quatre questions.

**Pourquoi des modèles qui classent bien les clients ne trouvaient-ils presque aucun défaut ?**
Au seuil de 0,5, le SVM, les plus proches voisins (KNN) et le réseau de neurones ne trouvaient presque aucun défaut, alors qu'ils rangeaient les clients du plus sûr au plus risqué presque aussi bien que les meilleurs modèles. Leurs probabilités restaient simplement basses : peu de clients passaient au-dessus de 0,5. Le seuil commun les jugeait mal. **On ne juge donc plus les modèles au même seuil, mais à la même part de défauts trouvés** : chaque modèle a son propre seuil.

**Quelle part des défauts viser ?**
On fixe un **taux de rappel minimal** : la part des défauts que la banque exige au moins de repérer. C'est une **exigence métier**, pas un réglage cherché pour flatter les résultats. Il a été fixé à **60 % des défauts hors contentieux** : c'est le niveau que les meilleurs modèles (CatBoost et RandomForest) atteignaient déjà au premier essai sur cette nouvelle base, au seuil de 0,5, sans être réglés pour ça. L'objectif paraissait donc réaliste, et il avait vocation à être relevé si les performances le permettaient. Il ne l'a jamais été : la page 6.3 montre pourquoi. Viser plus haut a un prix, à arbitrer selon ce que la banque peut suivre : plus de défauts trouvés, mais plus de clients signalés à tort. À l'extrême, le réglage qui maximise le F2 score signalait la majorité des clients.

**Le but est alors fixé : à ce taux de rappel tenu, faire monter la précision des défauts prédits**, c'est-à-dire signaler le moins possible de bons clients pour trouver ces 60 % de défauts. C'est ce que cherchent les scénarios (page 6.3).

**Comment apprendre une logique, et non le dataset, sans empêcher d'apprendre ?**
Un modèle qui réussit beaucoup mieux sur les clients qu'il a vus que sur les autres apprend par cœur. La boucle limite donc l'écart entre les deux et, quand il est trop grand, simplifie le modèle au tour suivant. Mais trop simplifier mène à l'excès inverse : un modèle qui ne fait plus mieux que le hasard. **Un plancher l'empêche** : un réglage doit battre le hasard pour compter. Entre les deux bornes, le modèle apprend une logique, pas le dataset.

**Comment classer des modèles qui ne trouvent pas exactement la même part des défauts ?**
Certains modèles ne savent pas s'arrêter pile au taux de rappel minimal : beaucoup de clients ont exactement la même probabilité, et le seuil les prend tous. On les mesure à leur vrai point de fonctionnement, sans tronquer leurs prédictions. Pour les classer, un **« score décisionnel F2 »** est calculé à la fin, pour chaque modèle, à sa propre part de défauts trouvés : à part égale, la meilleure précision gagne ; à précision égale, la plus grande part de défauts trouvés gagne. Il ne sert qu'au classement final et à la comparaison des scénarios : les modèles sont réglés sur la précision.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Enrichir le socle, scénario par scénario", anchor="scenarios")
st.markdown("""
**La méthode a d'abord été éprouvée sur un socle** : les seules variables d'origine du dataset. Le meilleur modèle, CatBoost, n'y a pas progressé : il garde la performance de l'ajustement à la main, mais **sans surapprentissage**, donc avec un score enfin crédible. Ce qui a changé, ce sont les autres modèles. Jugés au même taux de rappel minimal, puis nourris de variables mises en forme (codifications traitées comme des nombres, paiements et factures passés au logarithme), ils l'ont tous rejoint : **les six modèles sont à égalité**, et la régression logistique, le plus simple et le plus explicable, fait jeu égal avec le plus complexe.

**La méthode est fiable, rigoureuse et reproductible, et elle met chaque modèle en pleine possession de ses moyens, sans en désavantager aucun.** Elle a alors été figée : elle n'a plus changé d'un scénario à l'autre. Le socle a donné ce que ses variables permettaient ; pour monter plus haut, il faut de nouvelles informations.

**Les scénarios ont ensuite enrichi ce socle, petit groupe de variables par petit groupe.** Ces variables venaient en grande partie de l'**exploration déjà réalisée**, qui les a construites et en a montré le lien avec le risque :
- l'**utilisation du plafond**, mois par mois (page 4.2) ;
- les **ratios de paiement** et le **type d'usage de la carte**, du paiement comptant au crédit qui ne se rembourse pas (page 4.3), avec la régularité du comportement de paiement ;
- la **codification habituelle** du client, hors retards ;
- la **vie du compte** : ouverture ou réveil pendant la période (page 4.4) ;
- l'**historique des retards** : leur nombre, leur durée, la sortie d'un retard (pages 4.6 et 5.3).

D'autres variables ont été créées au fil des résultats, comme des signaux de rupture de comportement.

**Chaque groupe devait faire ses preuves** : il n'était gardé que s'il apportait un **gain réel** par rapport au scénario de référence, régulier d'une mesure à l'autre, et non un effet du hasard. Tous les scénarios ont été mesurés avec la même méthode et le même taux de rappel minimal : ils se comparent directement. Une fois toutes les variables essayées, celles qui n'apportaient rien ont été retirées, pour un modèle plus simple ; le test n'a été lu qu'à ce moment-là, une seule fois. Les scénarios et le modèle retenu sont présentés en 6.3, le test en 6.4.
""")

st.info("""
**Ce qu'il faut retenir** : le machine learning reprend sur les seuls clients en gestion normale, le contentieux étant confié à la règle métier. La méthode devient automatique et reproductible : chaque modèle doit atteindre un taux de rappel minimal, exigence métier, et il est réglé pour être le plus précis possible à ce point, sans apprendre le dataset par cœur ni cesser d'apprendre, puis classé par un score décisionnel F2. Chaque choix répond à une question concrète posée par les premiers résultats. Sur le socle, elle a mis les six modèles à égalité, sans en désavantager aucun. Les scénarios ont ensuite enrichi le socle, groupe de variables par groupe de variables, chacun gardé seulement s'il apportait un gain réel.
""")
