from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 8.5 : LES RECOMMANDATIONS
# Ce qu'une banque pourrait faire de ces résultats, les données qui lèveraient les limites, les pistes ouvertes,
# et les pistes envisagées puis écartées (avec la raison de chaque écart). Aucun nouveau calcul.
# Sources : docs/hypotheses_et_conclusions.md (H2, sections 6 à 8), README (axes d'amélioration), pages 5.1, 6.5, 6.6, 7.1.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
HYPOTHESES = f"{GH_RACINE}/docs/hypotheses_et_conclusions.md"
DEFAUTS_MANQUES = f"{GH_RACINE}/lab_ML/analyse_defauts_manques.ipynb"

entete_partie_8()
st.markdown("---")
st.header("8.5 Les recommandations : ce qu'une banque pourrait en faire, et la suite", anchor="recommandations")
st.markdown("""
Aucune banque n'utilise ce travail : il montre une méthode et ce qu'on peut en attendre. Voici ce qu'une banque pourrait en tirer, ce qu'il faudrait pour aller plus loin, et les pistes déjà examinées.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Pour une banque : la règle d'abord, le modèle ensuite, l'humain toujours", anchor="banque")
st.markdown("""
1. **Appliquer d'abord la règle du contentieux.** Simple, explicable, sans modèle, elle repère un tiers des défauts avec sept prédictions justes sur dix. Les clients au contentieux qui recommencent à payer méritent un examen au cas par cas : ce sont eux, les fausses alertes de la règle.
2. **Réserver le modèle aux autres clients, et l'utiliser par niveaux de risque.** Traiter d'abord le très haut risque, puis le haut risque. Vu du portefeuille entier, le risque modéré est moins risqué que le client moyen (page 8.4) : le signalement s'y arrête, ou se règle selon la capacité des équipes et le coût réel d'une fausse alerte face à un défaut manqué.
3. **Garder une décision humaine.** Le niveau de risque est un outil interne, pour prioriser la surveillance ; il ne se communique pas au client et ne décide seul d'aucune mesure qui le touche. C'est aussi ce qu'impose le droit (page 6.6).
4. **À score égal, choisir le modèle le plus simple**, et le plus facile à justifier devant la gestion des risques ; et se passer des données démographiques, qui n'apportent rien au score (page 6.3).
5. **Réapprendre sur des données récentes et suivre le modèle dans le temps** : mesurer chaque mois le taux de défaut de chaque niveau, et réapprendre quand il s'écarte de ce qui était attendu.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Pour aller plus loin : quatre informations à obtenir", anchor="donnees")
st.markdown("""
Les limites du projet viennent des données (page 8.4). Quatre informations, que seule la banque possède, permettraient de les lever :
- **la définition exacte du défaut** : défaut de paiement observé, ou statut posé par la banque ? C'est la condition de toute amélioration ;
- **les vrais encours** : le montant du relevé ne serait pas toujours la dette réelle ; on saurait alors si les défauts des clients « sans dette » sont une erreur de la cible ou une dette invisible dans les relevés ;
- **la liste des clients suivis hors du circuit normal** (recouvrement, contentieux) : elle validerait la règle du contentieux, et séparerait le défaut « administratif » du vrai défaut de paiement. Elle dirait aussi ce que sont les défauts que rien n'annonçait, chez des clients hors contentieux au profil de bons payeurs (environ un tiers de leurs défauts, page 6.5) : de vrais impayés, ou des statuts posés par la banque pour des raisons que les données ne montrent pas.
- **la façon dont l'échantillon a été tiré** : avec environ un client sur cinq en défaut, il ne ressemble pas à un portefeuille réel. Savoir quels clients ont été retenus dirait si les clients ordinaires, qui paient sans incident, ont été en grande partie écartés, ce qui changerait à la fois les taux affichés et ce que les modèles ont pu apprendre (page 8.4).
""")

# ------------------------------------------------------------------------------
st.subheader("3. Les pistes ouvertes", anchor="pistes")
st.markdown(f"""
- **Une probabilité de défaut par client** (calibration), l'objectif principal de l'étude de 2009, plutôt qu'un taux par niveau de risque ; on pourrait alors comparer le projet à l'étude sur son propre terrain.
- **Comprendre la codification {codif('1')}**, deux lectures sont possibles (pages 5.2 et 5.3). **Si c'est une codification temporaire**, posée le temps que la banque tranche, un modèle pourrait être entraîné à retrouver la codification définitive (sortie du retard ou retour au retard) à partir de la durée du retard, des paiements et de l'évolution du solde : hors dette soldée ou absence totale de paiement, aucune règle métier ne le permet. Il faudrait pour cela connaître la codification des mois suivants, absente du dataset. **Si c'est une codification à part entière**, dont le sens n'est simplement pas documenté, il n'y a rien à corriger : elle se garde telle quelle. Seule la banque peut dire laquelle des deux lectures est la bonne.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Les pistes envisagées puis écartées", anchor="ecartees")
tableau_html(["Piste", "Pourquoi elle a été écartée"], [
    ["<b>Combiner plusieurs modèles</b> (vote, moyenne des probabilités)",
     f"Les quatre modèles retenus se partagent les clients de la même façon : sur 771 défauts analysés, 410 sont trouvés par les quatre à la fois, et 248 par aucun (<a href='{DEFAUTS_MANQUES}' target='_blank'>analyse des défauts manqués</a>). Les combiner ne ferait pas apparaître les défauts qu'aucun ne voit."],
    ["<b>Ajouter encore des variables</b>",
     "Les seize scénarios, des ratios de paiement à l'historique des retards, sont tous restés dans l'incertitude de la mesure, même mesurés finement (page 6.3)."],
    ["<b>Des modèles plus puissants</b>",
     "Poussés sans frein contre le surapprentissage, ils ne font pas mieux ; un modèle lancé sur les données brutes fait jeu égal avec le projet (pages 6.5 et 8.1)."],
    ["<b>Nettoyer davantage les données</b> selon des règles métier",
     "Au-delà des anomalies indéfendables, ce serait transformer les données en notre propre lecture : les codifications traduisent un signal de la banque, qu'on ne voit pas (page 8.3)."],
    ["<b>Recoder la cible</b>",
     "Les modèles prédiraient alors notre définition du défaut, et non plus celle de la banque : ce serait changer la question."],
    ["<b>Changer de jeu de données</b>, pour un jeu à la cible clairement définie et aux codifications documentées",
     "Le pari était de faire mieux en lisant ces données avec un regard métier : comprendre les codifications de la banque et le fonctionnement de ses comptes avant de modéliser. Il a payé en partie, avec la population contentieuse, isolée par une règle métier qui prédit à elle seule un tiers des défauts (partie 5). Ce dataset est aussi celui de l'étude de référence : en changer, c'était renoncer à s'y comparer (page 8.2)."],
    ["<b>Un modèle pour sortir des clients du contentieux</b>",
     "Avec l'exigence métier, ne sortir un client que s'il a au moins neuf chances sur dix de payer (sortir à tort un client en défaut revient à abandonner une créance), aucun modèle ne trouve de client à sortir : au contentieux, ils trient à peine mieux que le hasard (page 8.1)."],
    ["<b>Isoler l'effet des seules corrections du nettoyage</b>",
     "Elles touchent très peu de clients, et l'écart attendu serait plus petit que l'incertitude de la mesure ; les essais du comparatif ne montrent déjà que des écarts minimes."],
    ["<b>Réentraîner le modèle sur l'entraînement et le test réunis</b>",
     "Le gain attendu reste dans le bruit, et il ne resterait plus de clients jamais vus pour juger le modèle et le montrer en direct (page 7.1)."],
], largeurs=[30, 70])
st.caption(f"Raisonnement complet et sources de chaque piste : [hypothèses et conclusions]({HYPOTHESES}), sections 1, 4, 6 et 7.")

st.info("""
**Ce qu'il faut retenir** : une banque appliquerait d'abord la règle du contentieux, puis le modèle aux autres clients, par niveaux de risque, en s'arrêtant au haut risque, et toujours au service d'une décision humaine. Pour aller plus loin, il ne faut pas un meilleur modèle, mais de meilleures données : la définition du défaut, les vrais encours, la liste des clients en recouvrement et la façon dont l'échantillon a été tiré. Combiner des modèles, ajouter des variables ou nettoyer davantage ont été examinés, et écartés.
""")
