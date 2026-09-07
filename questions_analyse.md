## Questions d'analyse

**En quoi ce dataset permet-il de répondre à une problématique métier réaliste ? Quelles limites identifies-tu déjà à ce stade ?**
Ce sont des données réelles dans un contexte particuliers qui peut se reproduire. Elles ne nécessitent pas les données personnelles de clients difficilement vérifiables (exemples : salaire, endettement).  
Les limites sont :
- la qualité du jeu de données lui-même et la colonne 'PAY_1' qui contient probablement un artefact de gestion courante
- la probable coexistence de clients en circuit classique avec des clients en cicruit recouvrement / contentieux
- des données incohérentes les unes par rapport aux autres pour un même client quand on regarde avec un oeil métier

**Pourquoi ce schéma relationnel (normalisation, clés, tables) est-il adapté à tes données et à leur usage futur ?**
J'ai conçu un schéma relationnel en étoile (Star Schema), standard de l'ingénierie de données et du décisionnel (BI), pour répondre à quatre enjeux clés :
1. Gestion de la temporalité et séries temporelles :
- La donnée de crédit est par nature évolutive. La création de la table de faits historique_mensuel couplée à la dimension dim_date permet de capturer la dynamique temporelle du client (1 enregistrement par mois).
- Cette structure permet de suivre l'évolution des encours, de comparer les comportements mois par mois et de réaliser des analyses de saisonnalité ou de tendances d'impayés sur n'importe quelle fenêtre de temps.
2. Dépilage et 1re Forme Normale (1FN) - Extensibilité temporelle :
- Le dataset brut étalait l'historique sur 18 colonnes répétitives (PAY_1..6, BILL_AMT1..6).
- Le dépilage dans une table de faits centralisée permet d'ajouter de futurs mois de suivi ou de nouveaux clients par simple insertion de lignes (flux horizontal), sans jamais devoir modifier la structure de la base.
3. Normalisation (3FN) et Clés (PK/FK) - Intégrité des données :
- Les codes numériques (SEX, EDUCATION, MARRIAGE, PAY_n) ont été isolés dans 5 tables de référence (genre, niveau_scolaire, statut_marital, statut_paiement, statut_defaut).
- Chaque table est sécurisée par des clés primaires (PK) et étrangères (FK), empêchant les anomalies d'insertion et garantissant l'absence d'enregistrements orphelins.
4. Adaptabilité aux usages futurs du projet :
- Business Intelligence (Power BI) : La table dim_date facilite le Time Intelligence (comparaison *M* vs *M-1*, cumuls annuels) et accélère les jointures analytiques.
- Exposition API (FastAPI) : La séparation propre entre client et historique_mensuel facilite la création des endpoints CRUD (Create, Read, Update, Delete). L'API peut ainsi lire ou mettre à jour le profil d'un client et son historique de manière fluide, sans accès direct à la base.
- Machine Learning : La structuration temporelle propre permet de calculer facilement des variables glissantes (moyennes de retards sur 3 mois, ratios d'endettement historiques) sans risque de fuite de données (data leakage).


**Quels choix as-tu faits pour organiser/sécuriser cette API, et en quoi une API répond-elle mieux à ce contexte qu'un accès direct à la base ?**


**Quelles tendances actuelles en IA/Big Data as-tu identifiées ?**


**Pourquoi ces indicateurs et ces visualisations sont-ils les plus pertinents pour répondre à la problématique posée en Semaine 1 ?**


**Pourquoi ce modèle plutôt qu'un autre au vu de tes métriques ? Quels sont les risques majeurs de ton projet et comment les limiter ?**


**Comment as-tu adapté ton discours et ton support à un public non technique ?**
