from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 6.6 : L'ÉVALUATION DES RISQUES
# Registre des risques du projet, en quatre thèmes (données, modèle, utilisation par une banque, éthique) :
# pour chaque risque, sa gravité (évaluation argumentée), ce que le projet a fait pour le limiter, et ce qu'il
# faudrait en usage réel. Aucune banque n'utilise ce travail : le site, l'API et les modèles en ligne sont des démonstrations.
# Taux de défaut et effectifs calculés en direct sur le dataset ; autres chiffres repris des pages 5.5, 6.4 et 6.5.
# ==============================================================================
df = load_data()
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
# Les deux populations des règles métier, au statut à M (comme creation_datasets_ML)
au_ctx = s12[s12["STATUT_INCIDENT"] == "En incident"]
retard_imminent = s12[s12["STATUT_INCIDENT"] == "Retard imminent"]
taux_portefeuille = df["dpnm"].mean() * 100
sans_defaut_ctx = (1 - au_ctx["dpnm"].mean()) * 100
sans_defaut_imminent = (1 - retard_imminent["dpnm"].mean()) * 100


def gravite(niveau):
    """Gravité écrite en clair, avec une pastille de couleur."""
    pastilles = {"Élevée": "🔴", "Moyenne": "🟠", "Faible": "🟢"}
    return f"{pastilles[niveau]} <b>{niveau}</b>"


ENTETES = ["Risque", "Gravité", "Ce que le projet a fait pour le limiter", "Ce qu'il faudrait en usage réel"]
LARGEURS = [27, 11, 31, 31]

entete_partie_6()
st.markdown("---")
st.header("6.6 L'évaluation des risques : ce qui peut tromper, et comment le limiter", anchor="risques")
st.markdown("""
**Aucune banque n'utilise ce travail.** Le site, l'API et les modèles mis en ligne sont des démonstrations, construites sur des données publiques. Les risques ci-dessous sont donc ceux du projet lui-même, et ceux qu'une banque prendrait si elle utilisait ce travail. Pour chacun : sa **gravité**, ce que le projet a fait pour le **limiter**, et ce qu'il faudrait faire **en usage réel**.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Les données", anchor="donnees")
tableau_html(ENTETES, [
    ["<b>Une cible non documentée</b> : on ne sait pas comment la banque a attribué le défaut", gravite("Élevée"),
     "Les règles et les seuils ne sont jamais réglés sur la cible ; la limite est montrée et testée (pages 1.3 et 6.5) ; les résultats sont présentés comme des taux observés",
     "Obtenir la définition exacte du défaut avant toute utilisation"],
    [f"<b>Un échantillon peu représentatif</b> : {nombre_fr(taux_portefeuille, 0)} % de défaut, bien au-dessus de ce qu'une banque peut supporter durablement", gravite("Élevée"),
     "Les taux affichés décrivent l'échantillon, pas la banque ; aucun chiffre n'est présenté comme celui d'un portefeuille réel",
     "Réapprendre sur un portefeuille représentatif : appliqué tel quel, le modèle surestimerait le risque"],
    ["<b>Des données de 2005</b>, en pleine crise des cartes de crédit, d'une seule banque", gravite("Élevée"),
     "Le contexte de la crise est expliqué (partie 0) ; aucune conclusion n'est étendue à d'autres périodes ou d'autres banques",
     "Revalider sur les données de la banque concernée : une crise du crédit à la consommation peut se reproduire ailleurs, sous d'autres formes ; la méthode peut servir, les chiffres décrivent ce portefeuille"],
    ["<b>Des valeurs incohérentes</b> : montants aberrants, codifications posées sur des dettes nulles", gravite("Moyenne"),
     "Nettoyage par niveaux, chaque correction justifiée par la logique métier et documentée (partie 3)",
     "Valider les corrections avec les équipes de la banque"],
    ["<b>Une population en incident reconstruite</b> à partir des codifications, jamais confirmée par la banque", gravite("Moyenne"),
     "Définition par une règle métier, vérifiée sans la cible puis avec elle (pages 5.3 à 5.5)",
     "Comparer la règle à la vraie liste des clients en recouvrement"],
], largeurs=LARGEURS)

# ------------------------------------------------------------------------------
st.subheader("2. Le modèle", anchor="modele")
tableau_html(ENTETES, [
    ["<b>Une précision limitée</b> : au taux de rappel minimal, un peu plus d'un client signalé sur cinq seulement est en défaut", gravite("Moyenne"),
     "Présentation par niveaux de risque, du très haut risque (environ quatre sur dix en défaut) au risque faible (page 6.4) ; cause du plafond recherchée (page 6.5)",
     "Choisir le niveau de signalement selon le coût réel d'une fausse alerte et d'un défaut manqué"],
    ["<b>Un modèle qui apprend par cœur</b> l'entraînement (surapprentissage)", gravite("Faible"),
     "Écart entre entraînement et validation borné par la boucle de réglage ; test lu une seule fois, où précision et capacité à classer restent dans leur marge d'incertitude (pages 6.2 et 6.4)",
     "Mesurer à nouveau la performance sur chaque nouvelle période"],
    ["<b>Un seuil qui retrouve moins de défauts que prévu</b> : fixé sur l'entraînement pour en trouver 60 %, il en trouve 55,8 % sur le test", gravite("Faible"),
     "Écart mesuré sur le test et affiché avec sa marge d'incertitude, sans recaler le seuil après coup (page 6.4)",
     "Recaler le seuil sur des données récentes, puis suivre chaque mois la part des défauts réellement trouvés"],
    ["<b>Un choix trop flatteur</b> parmi des modèles à égalité (piège du gagnant)", gravite("Faible"),
     "Règle fixée dès le départ ; à égalité, le moins de variables ; modèle de décision désigné avant la lecture du test (page 6.3)",
     "—"],
    ["<b>Des probabilités trompeuses</b> : les probabilités brutes du modèle sont gonflées par le poids donné aux défauts", gravite("Moyenne"),
     "Jamais affichées : on donne le taux de défaut observé du niveau du client",
     "Calibrer les probabilités avant de les montrer"],
], largeurs=LARGEURS)

# ------------------------------------------------------------------------------
st.subheader("3. L'utilisation par une banque (déploiement)", anchor="deploiement")
tableau_html(ENTETES, [
    ["<b>Une dérive dans le temps</b> : les clients, l'économie et les règles changent", gravite("Élevée"),
     "Hors du champ du projet : données d'un seul semestre",
     "Suivre chaque mois le taux de défaut de chaque niveau, et réapprendre quand il s'écarte"],
    ["<b>Une décision automatique</b> prise sur la seule sortie du modèle", gravite("Élevée"),
     "Le modèle est présenté comme un outil de priorisation, pas de sanction (page 6.4)",
     "Garder une décision humaine pour toute mesure qui touche le client"],
    [f"<b>Les fausses alertes des règles métier</b> : {nombre_fr(sans_defaut_ctx, 0)} % des clients en incident à M et {nombre_fr(sans_defaut_imminent, 0)} % des clients en retard imminent ne font pas défaut", gravite("Moyenne"),
     "Taux mesurés et affichés (pages 5.4 et 5.5) ; les règles restent la seule décision défendable avec ces données",
     "Examiner au cas par cas les clients en incident qui paient"],
    ["<b>Trop d'alertes à traiter</b> : pour trouver 60 % des défauts des clients laissés au machine learning (le taux de rappel minimal), le modèle en signale plus d'un tiers, soit environ 8 400 clients", gravite("Moyenne"),
     "Niveaux de risque, pour traiter d'abord la tête de liste (page 6.4)",
     "Dimensionner le signalement selon la capacité des équipes"],
    ["<b>Une prédiction en ligne mal lue</b> : un visiteur peut prendre la sortie du modèle pour une vraie probabilité de défaut", gravite("Moyenne"),
     "Afficher le niveau de risque du client et le taux de défaut observé de ce niveau, jamais la probabilité brute",
     "Calibrer les probabilités avant de les montrer"],
    ["<b>Une démonstration trop belle</b> : prédire sur des clients que le modèle a appris donne un résultat flatteur", gravite("Moyenne"),
     "Démonstrations (partie 7) uniquement sur des clients jamais appris : le jeu de test et des clients retirés avant le machine learning ; le modèle n'est pas réentraîné",
     "Juger le modèle uniquement sur des clients jamais vus"],
    ["<b>Un modèle en ligne différent du modèle évalué</b>, s'il est réentraîné sur plus de données", gravite("Faible"),
     "Le modèle en ligne est celui évalué sur le test, sans réentraînement : le score annoncé est le sien",
     "Évaluer chaque nouvelle version avant de la mettre en service"],
    ["<b>Une base de démonstration ouverte</b> : l'API laisse tout visiteur lire et modifier la base", gravite("Faible"),
     "Choix assumé : données publiques et anonymes, base réinitialisée à chaque mise en veille du serveur, formats contrôlés à l'entrée, lecture par lot ouverte pour la démonstration (partie 7), téléchargement complet réservé à l'administrateur, protégé par un identifiant et un mot de passe (partie 2)",
     "Des accès par rôle (lecture, écriture, administration), attribués par le système d'information"],
], largeurs=LARGEURS)

# ------------------------------------------------------------------------------
st.subheader("4. L'éthique", anchor="ethique")
tableau_html(ENTETES, [
    ["<b>Une discrimination directe</b> par l'âge, le genre, le niveau d'études ou le statut marital", gravite("Faible"),
     "L'âge, le genre et le statut marital sont retirés du modèle final, sans perte de score ; le niveau d'études, qui ne figure pas parmi les critères de l'article 225-1 du Code pénal, reste dans le modèle (page 6.3)",
     "Ne les utiliser que si leur lien avec le risque est objectivement justifié : le droit de la non-discrimination encadre l'usage du sexe, de l'âge ou de la situation de famille (en France, article 225-1 du Code pénal), sans l'interdire dans tous les cas"],
    ["<b>Un modèle difficile à expliquer</b> aux équipes de gestion des risques", gravite("Moyenne"),
     "Dans la version finale (21 variables), CatBoost, retenu parce qu'il était en tête, est moins lisible que la régression logistique, à égalité avec lui (page 6.3). La règle « à score égal, le plus simple » a été appliquée aux variables, pas au choix du modèle ; fixé avant la lecture du test, ce choix n'a pas été revu",
     "À performance égale, préférer le modèle le plus explicable, et pouvoir justifier auprès de la gestion des risques le niveau attribué à chaque client"],
    ["<b>Le droit du client</b> à comprendre et à contester une décision", gravite("Moyenne"),
     "Sans objet dans une démonstration",
     "Le client a le droit de ne pas faire l'objet d'une décision fondée exclusivement sur un traitement automatisé ; quand une telle décision est permise (contrat, consentement), il peut obtenir une intervention humaine, exprimer son point de vue et la contester (RGPD, article 22)"],
    ["<b>Des données personnelles</b>", gravite("Faible"),
     "Données publiques et anonymes, sans nom ni identifiant réel",
     "Respecter le RGPD (base légale, accès, durée de conservation)"],
    ["<b>Un système d'IA à haut risque</b> au sens du droit européen", gravite("Moyenne"),
     "Sans objet dans une démonstration ; la démarche est documentée et tracée (méthodologie, journal)",
     "L'évaluation de la solvabilité des particuliers ou de leur note de crédit est classée à haut risque par le règlement européen sur l'IA (règlement (UE) 2024/1689, annexe III, point 5 b) : documentation, contrôle humain et suivi obligatoires"],
], largeurs=LARGEURS)

st.caption("Textes cités : [Code pénal, article 225-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000045391831) (critères de discrimination, dont le sexe, la situation de famille et l'âge) ; [RGPD, articles 9 et 22](https://www.cnil.fr/fr/reglement-europeen-protection-donnees) (catégories particulières de données, qui ne comprennent ni l'âge ni le genre ; décision individuelle automatisée) ; [règlement européen sur l'IA, annexe III](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1689) (systèmes à haut risque, point 5 b). Rappels généraux, qui ne remplacent pas l'avis d'un juriste.")

# ------------------------------------------------------------------------------
st.subheader("5. Les risques majeurs", anchor="majeurs")
st.markdown("""
Trois risques dominent, et aucun ne vient du code ou des modèles :
- **la cible n'est pas documentée** : tant qu'on ne sait pas ce que « défaut » veut dire pour la banque, aucun résultat ne peut être pris pour argent comptant ;
- **les données ne ressemblent pas à un portefeuille d'aujourd'hui** : une seule banque, en 2005, en pleine crise, avec un taux de défaut irréaliste ;
- **une décision automatique serait dangereuse** : le modèle range les clients du plus au moins risqué, mais même en tête de liste, plus d'un client sur deux paie.

Ils se limitent par la même voie : un modèle réappris sur les données récentes et documentées d'une banque, suivi dans le temps, et utilisé pour prioriser le travail des équipes, jamais pour décider seul.
""")

st.info("""
**Ce qu'il faut retenir** : le projet a limité les risques qui dépendaient de lui (pas de seuil réglé sur la cible, test lu une seule fois, âge, genre et statut marital retirés, probabilités brutes jamais affichées, base de démonstration ouverte mais sans enjeu). Les risques majeurs viennent des données : une cible non documentée et un échantillon de 2005 peu représentatif. Utilisé tel quel, ce modèle ne serait pas fiable ; il montre une méthode et ses limites, et ne s'emploierait que réappris sur des données récentes, suivi dans le temps et au service d'une décision humaine.
""")
