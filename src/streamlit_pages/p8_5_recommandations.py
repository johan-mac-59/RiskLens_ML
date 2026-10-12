from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 8.5 : LES RECOMMANDATIONS
# Ce qu'une banque pourrait faire de ces résultats, les données qui lèveraient les limites, les pistes ouvertes,
# et les pistes envisagées puis écartées (avec la raison de chaque écart). Aucun nouveau calcul.
# Sources : pages 3.5, 6.3, 6.5, 6.6, 7.1, 8.1 à 8.4 ; lab_ML/analyse_defauts_manques.ipynb ;
# lab_ML/comparatif_global/essai_jeu_corrige_deux_populations.ipynb (sortie des clients des règles).
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
DEFAUTS_MANQUES = f"{GH_RACINE}/lab_ML/analyse_defauts_manques.ipynb"
ESSAI_REGLE = f"{GH_RACINE}/lab_ML/comparatif_global/essai_jeu_corrige_deux_populations.ipynb"

entete_partie_8()
st.markdown("---")
st.header("8.5 Les recommandations : ce qu'une banque pourrait en faire, et la suite", anchor="recommandations")
st.markdown("""
Aucune banque n'utilise ce travail : il montre une méthode et ce qu'on peut en attendre. Voici ce qu'une banque pourrait en tirer, ce qu'il faudrait pour aller plus loin, et les pistes déjà examinées.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Pour une banque : les règles d'abord, le modèle ensuite, l'humain toujours", anchor="banque")
st.markdown("""
1. **Appliquer d'abord les deux règles métier**, la population en incident et le retard imminent. Simples, explicables, sans modèle, elles repèrent près de la moitié des défauts de paiement, avec environ six prédictions justes sur dix. Les clients en incident qui recommencent à payer méritent un examen au cas par cas : ce sont eux, les fausses alertes des règles.
2. **Réserver le modèle aux autres clients, et l'utiliser par niveaux de risque.** Traiter d'abord le très haut risque, puis le haut risque. Vu du portefeuille entier, le risque modéré est moins risqué que le client moyen (page 8.4) : le signalement s'y arrête, ou se règle selon la capacité des équipes et le coût réel d'une fausse alerte face à un défaut de paiement manqué.
3. **Garder une décision humaine.** Le niveau de risque est un outil interne, pour prioriser la surveillance ; il ne se communique pas au client et ne décide seul d'aucune mesure qui le touche. C'est aussi ce qu'impose le droit (page 6.6).
4. **À score égal, choisir le modèle le plus simple**, et le plus facile à justifier devant la gestion des risques ; et se passer des données démographiques qui n'apportent rien au score : l'âge, le genre et le statut marital ont été retirés sans perte (page 6.3).
5. **Réapprendre sur des données récentes et suivre le modèle dans le temps** : mesurer chaque mois le taux de défaut de paiement de chaque niveau, et réapprendre quand il s'écarte de ce qui était attendu.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Pour aller plus loin : quatre informations à obtenir", anchor="donnees")
st.markdown("""
Les limites du projet viennent des données (page 8.4). Quatre informations, que seule la banque possède, permettraient de les lever :
- **la définition exacte du défaut de paiement noté par la banque** : impayé observé, ou statut posé par la banque ? C'est la condition de toute amélioration ;
- **les vrais encours** : le montant du relevé ne serait pas toujours la dette réelle ; on saurait alors si les défauts de paiement des clients « sans dette » sont une erreur de la cible ou une dette invisible dans les relevés ;
- **la liste des clients suivis hors du circuit normal** (recouvrement, contentieux) : elle validerait les deux règles métier, et séparerait le défaut « administratif » du vrai impayé. Elle dirait aussi ce que sont les défauts de paiement que rien n'annonçait, chez des clients au profil de bons payeurs (environ un quart des défauts de paiement des autres clients, page 6.5) : de vrais impayés, ou des statuts posés par la banque pour des raisons que les données ne montrent pas ;
- **la façon dont l'échantillon a été tiré** : avec environ un client sur cinq en défaut de paiement, il ne ressemble pas à un portefeuille réel. Savoir quels clients ont été retenus dirait si les clients ordinaires, qui paient sans incident, ont été en grande partie écartés, ce qui changerait à la fois les taux affichés et ce que les modèles ont pu apprendre (page 8.4).
""")

# ------------------------------------------------------------------------------
st.subheader("3. Les pistes ouvertes", anchor="pistes")
st.markdown(f"""
- **Une probabilité de défaut de paiement par client** (calibration), l'objectif principal de l'étude de 2009, plutôt qu'un taux par niveau de risque ; on pourrait alors comparer le projet à l'étude sur son propre terrain.
- **Sortir quelques clients des populations à risque.** Avec l'exigence retenue (ne sortir un client que s'il a au moins neuf chances sur dix de payer, car sortir à tort un client qui sera en défaut de paiement revient à abandonner une créance), aucun modèle ne trouve de client à sortir : dans ces populations, ils trient à peine mieux que le hasard (page 8.1, sous-partie 1). Une autre voie serait de demander l'**accord de plusieurs modèles de familles différentes**, comme pour la correction des codifications {codif('1')} (page 3.5), pour sortir peu de clients, mais avec une grande sûreté ; les clients sortis seraient déclarés sans défaut de paiement, sans repasser par le modèle. Deux conditions : une exigence fixée à l'avance par le métier, jamais réglée sur le résultat, et un jugement sur l'entraînement seul, le test de ces populations ayant déjà été lu.
- **Mieux corriger les codifications {codif('1')} de septembre.** Les trois modèles qui les tranchent n'utilisent que les codifications, les soldes, les paiements et le plafond (page 3.5). Des variables construites (ratios de paiement, utilisation du plafond), validées pour ce problème, pourraient les aider. Mais une seule codification changée touche tout le circuit en aval, du nettoyage au découpage du machine learning, et le test a déjà été lu : c'est une piste pour une nouvelle version du projet, avec un nouveau test. Seule la banque, enfin, peut confirmer la lecture retenue, celle d'une codification temporaire posée le temps de trancher.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Les pistes envisagées puis écartées", anchor="ecartees")
tableau_html(["Piste", "Pourquoi elle a été écartée"], [
    ["<b>Combiner plusieurs modèles</b> (vote, moyenne des probabilités)",
     f"Les cinq modèles de la version finale se partagent les clients de la même façon : sur 620 défauts de paiement analysés, 305 sont trouvés par les cinq à la fois, et 154 par aucun (<a href='{DEFAUTS_MANQUES}' target='_blank'>analyse des défauts manqués</a>). Les combiner ne ferait pas apparaître les défauts de paiement qu'aucun ne voit."],
    ["<b>Ajouter encore des variables</b>",
     "Toutes les variables construites pendant l'exploration, ajoutées ensemble puis retirées famille par famille, sont restées dans l'incertitude de la mesure (page 6.3)."],
    ["<b>Des modèles plus réglés</b>",
     "Des réglages élargis ne font pas mieux, et un modèle lancé sur les données brutes fait jeu égal avec le projet sur les mêmes clients (pages 6.3 et 8.1)."],
    ["<b>Nettoyer davantage les données</b> selon des règles métier",
     "Au-delà de ce que les paiements permettent de trancher, ce serait transformer les données en notre propre lecture : les codifications traduisent un signal de la banque, qu'on ne voit pas (page 8.3)."],
    ["<b>Recoder la cible</b>",
     "Les modèles prédiraient alors notre définition du défaut de paiement, et non plus celle de la banque : ce serait changer la question."],
    ["<b>Changer de jeu de données</b>, pour un jeu à la cible clairement définie et aux codifications documentées",
     "Le pari était de faire mieux en lisant ces données avec un regard métier : comprendre les codifications de la banque et le fonctionnement de ses comptes avant de modéliser. Il a payé en partie, avec la population en incident et le retard imminent, isolés par des règles métier qui prédisent à elles seules près de la moitié des défauts de paiement (partie 5). Ce dataset est aussi celui de l'étude de référence : en changer, c'était renoncer à s'y comparer (page 8.2)."],
    ["<b>Réentraîner le modèle sur l'entraînement et le test réunis</b>",
     "Le gain attendu reste dans le bruit, et il ne resterait plus de clients jamais vus pour juger le modèle et le montrer en direct (page 7.1)."],
], largeurs=[30, 70])
st.caption(f"Sortie des clients des populations à risque : [essai par populations]({ESSAI_REGLE}), section 3.")

st.info("""
**Ce qu'il faut retenir** : une banque appliquerait d'abord les deux règles métier, puis le modèle aux autres clients, par niveaux de risque, en s'arrêtant au haut risque, et toujours au service d'une décision humaine. Pour aller plus loin, il ne faut pas un meilleur modèle, mais de meilleures données : la définition du défaut de paiement, les vrais encours, la liste des clients en recouvrement et la façon dont l'échantillon a été tiré. Restent ouvertes la calibration, la sortie de quelques clients des populations à risque et une meilleure correction des codifications 1 ; combiner des modèles, ajouter des variables ou nettoyer davantage ont été examinés, et écartés.
""")
