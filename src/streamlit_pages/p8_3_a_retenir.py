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
    ["<b>1. Les données</b>", "Six mois de factures, de paiements et de codifications par client, et un défaut en octobre 2005 dont la définition exacte n'est pas documentée."],
    ["<b>2. La base de données et l'API</b>", "Les données d'origine sont chargées dans une base relationnelle, contrôlées, et exposées par une API qui sert aussi les démonstrations."],
    ["<b>3. Comprendre le jeu de données</b>", f"Un fichier complet, mais des valeurs anormales : chaque anomalie reçoit une règle argumentée, et {nombre_fr(len(df))} clients sont gardés."],
    ["<b>4. Explorer le portefeuille</b>", "Des écarts de risque réels entre groupes de clients : le profil (âge, genre, études) ne joue que modérément ; l'utilisation du plafond, la part remboursée et surtout les retards qui durent comptent davantage."],
    ["<b>5. La population contentieuse</b>", "Des clients figés en retard forment une population à part, définie par une règle métier : peu de clients, un tiers des défauts, sept prédictions justes sur dix."],
    ["<b>6. Le machine learning</b>", "Sur les autres clients, tous les modèles et toutes les variables atteignent le même plafond ; le modèle retenu range les clients par niveau de risque, et une part des défauts ne s'annonce pas dans les données."],
    ["<b>7. Le déploiement</b>", "La règle puis le modèle tournent en direct, de la base de données à la décision, sur des clients jamais vus, et retrouvent les résultats de l'évaluation."],
    ["<b>8. La réponse</b>", "Le comportement des six derniers mois classe bien les clients par niveau de risque, à un niveau comparable à l'étude de 2009 ; il ne désigne pas à coup sûr ceux qui feront défaut."],
], largeurs=[25, 75])

# ------------------------------------------------------------------------------
st.subheader("2. Les codifications : une étiquette de la banque, à prendre au sérieux", anchor="codifications")
st.markdown(f"""
Tout au long du projet, les codifications de paiement (`PAY_1` à `PAY_6`) n'ont pas toujours été raccord avec les montants : des retards posés sur des factures payées ou nulles (page 5.2), des clients figés à {codif('2')} pendant six mois (page 5.1), des {codif('1')} de septembre que la banque n'a pas encore tranchés (pages 5.2 et 5.3), des défauts chez des clients sans dette (page 5.1).

Ces écarts ne sont pas de simples erreurs. Une codification traduit **un signal reçu par la banque**, que les données ne montrent pas, et ce signal est sérieux : le défaut en dépend fortement, même quand la facture a été payée (page 5.5). C'est pourquoi le projet n'a corrigé que **l'indéfendable**, les retards posés sur une facture nulle, et a gardé tout le reste. C'est aussi pourquoi les codifications ont été lues **avec les paiements**, jamais seules (page 3.3).
""")

# ------------------------------------------------------------------------------
st.subheader("3. Les messages clés", anchor="messages")
st.markdown("""
1. **Une règle métier avant tout modèle.** Un tiers des défauts se prévoit sans machine learning, par une règle que la banque peut appliquer et expliquer : deux codifications de retard d'affilée (pages 5.3 et 5.6).
2. **Le modèle classe, il ne désigne pas.** Il range les clients du très haut risque (un sur deux en défaut) au risque faible (un sur dix) ; même en tête de liste, un client sur deux paie. C'est un outil pour prioriser la surveillance, pas pour sanctionner (pages 6.4 et 8.1).
3. **Le comportement suffit à classer.** Les montants facturés et payés portent presque tout ce qui est prévisible, sans les données démographiques, que le modèle final n'utilise pas (pages 6.3 et 8.1).
4. **La limite vient des données, pas des modèles.** Variables, réglages, modèles plus puissants, modèle lancé sur les données brutes : tout tombe sur la même courbe, et environ un tiers des défauts ont le profil des bons clients (pages 6.5 et 8.1).
5. **La valeur du travail est dans la méthode.** À score égal, le projet apporte un système explicable : des corrections justifiées, une règle lisible, aucun seuil réglé sur le défaut, un test lu une seule fois, et des résultats comparables à l'étude de 2009 (pages 6.2 et 8.2).
""")

st.info("""
**Ce qu'il faut retenir** : peut-on prévoir le défaut d'un client à partir de son seul comportement des six derniers mois ? Oui pour une part importante des défauts : un tiers par une simple règle métier, et le reste rangé par niveau de risque par un modèle, au niveau de l'étude de 2009. Non pour tous : une part des défauts ne s'annonce pas dans ces données. Le comportement classe les clients ; il ne désigne pas à coup sûr ceux qui feront défaut.
""")
