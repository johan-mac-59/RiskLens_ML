from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 8.3 : CE QU'IL FAUT RETENIR
# Le fil du projet, une ligne par partie (reprise des titres-messages des pages), le point sur les codifications,
# puis les messages clés. Aucun nouveau calcul : effectifs lus en direct dans le dataset, le reste renvoie aux pages.
# ==============================================================================
df = load_data()

entete_partie_8()
st.markdown("---")
st.header("8.3 Ce qu'il faut retenir", anchor="a-retenir")

# ------------------------------------------------------------------------------
st.subheader("1. Le fil du projet, partie par partie", anchor="fil")
tableau_html(["Partie", "Ce qu'elle montre"], [
    ["<b>0. Accueil</b>", "Les données viennent d'une banque taïwanaise en 2005, en pleine crise des cartes de crédit : une crise du crédit, pas de l'économie."],
    ["<b>1. Les données</b>", "Six mois de factures, de paiements et de codifications par client, et un défaut de paiement en octobre 2005 dont la définition exacte n'est pas documentée."],
    ["<b>2. La base de données et l'API</b>", "Les données d'origine sont chargées dans une base relationnelle, contrôlées, et exposées par une API qui sert aussi les démonstrations."],
    ["<b>3. Comprendre le jeu de données</b>", f"Un fichier complet, mais des valeurs anormales : chaque anomalie reçoit une règle argumentée, et {nombre_fr(len(df))} clients sont gardés."],
    ["<b>4. Explorer le portefeuille</b>", "Des écarts de risque réels entre groupes de clients : le profil (âge, genre, études) ne joue que modérément ; l'utilisation du plafond, la part remboursée et surtout les retards qui durent comptent davantage."],
    ["<b>5. La population en incident</b>", "Des clients figés en retard mènent à deux populations définies par des règles métier, la population en incident et le retard imminent : peu de clients, près de la moitié des défauts de paiement, environ six prédictions justes sur dix."],
    ["<b>6. Le machine learning</b>", "Sur les autres clients, tous les modèles et toutes les variables atteignent le même plafond ; le comportement suffit, sans les codifications brutes ; le modèle retenu range les clients par niveau de risque, et une part des défauts de paiement ne s'annonce pas dans les données."],
    ["<b>7. Le déploiement</b>", "Les règles puis le modèle tournent en direct, de la base de données à la décision, sur des clients jamais vus, et retrouvent les résultats de l'évaluation."],
    ["<b>8. La réponse</b>", "Le comportement des six derniers mois classe bien les clients par niveau de risque, à un niveau comparable à l'étude de 2009 ; il ne désigne pas à coup sûr ceux qui seront en défaut de paiement."],
], largeurs=[25, 75])

# ------------------------------------------------------------------------------
st.subheader("2. Les codifications : une étiquette de la banque, à lire avec les paiements", anchor="codifications")
st.markdown(f"""
Tout au long du projet, les codifications de paiement (`PAY_1` à `PAY_6`) n'ont pas toujours été raccord avec les montants : des clients figés à {codif('2')} pendant six mois (page 5.1), des {codif('1')} que la banque n'avait pas encore tranchés (page 3.3), une règle plus souple d'avril à juin pour poser un retard, et des défauts de paiement chez des clients sans dette (page 6.5).

Ces écarts ne sont pas de simples erreurs. Une codification traduit **un signal reçu par la banque**, que les données ne montrent pas toujours, et ce signal est sérieux : parmi les clients en incident, ceux qui ont versé un paiement en août et en septembre, même partiel, sont en défaut de paiement aussi souvent que les autres (environ 60 %, page 6.5). C'est pourquoi le projet n'a corrigé que ce que les paiements permettent de trancher : les {codif('1')}, remplacés par la codification que la banque aurait posée, et les {codif('2')} d'avril à juin, uniformisés d'après les montants payés, pour qu'un même comportement donne la même codification sur toute la période (page 3.5). Tout le reste est gardé tel quel. Et les codifications ont toujours été lues **avec les paiements**, jamais seules (page 3.3).
""")

# ------------------------------------------------------------------------------
st.subheader("3. Les messages clés", anchor="messages")
st.markdown("""
1. **Des règles métier avant tout modèle.** Près de la moitié des défauts de paiement se prévoit sans machine learning, par deux règles que la banque peut appliquer et expliquer : la population en incident (deux codifications de retard d'affilée, ou une seule de 3 ou plus) et le retard imminent (pages 5.2 et 5.5).
2. **Le modèle classe, il ne désigne pas.** Il range les autres clients du très haut risque (environ quatre sur dix en défaut de paiement) au risque faible (moins d'un sur dix) ; même en tête de liste, plus d'un client sur deux paie. C'est un outil pour prioriser la surveillance, pas pour sanctionner (pages 6.4 et 8.1).
3. **Le comportement suffit à classer.** Une fois les retards repérés par les règles et par le nombre de mois en retard, les codifications brutes n'apportent plus rien ; les montants facturés et payés portent presque tout ce qui reste prévisible, et le modèle final ne garde, comme donnée démographique, que le niveau d'études (pages 6.3 et 8.1).
4. **La limite vient des données, pas des modèles.** Variables, réglages, modèle lancé sur les données brutes : tout tombe sur la même courbe, et environ un quart des défauts de paiement des autres clients ont le profil des bons clients (pages 6.5 et 8.1).
5. **La valeur du travail est dans la méthode.** À score égal, le projet apporte un système explicable : des corrections justifiées, des règles lisibles, aucun seuil réglé sur le défaut de paiement, un test lu une seule fois, et des résultats comparables à l'étude de 2009 (pages 6.2 et 8.2).
""")
