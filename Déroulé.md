## Compréhension du dataset
**Explorer le dataset, comprendre son contenu, son origine, sa signification**  
Le fichier Kaggle est une copie conforme d'un dataset de 2005 publié par des chercheurs Yeh & Lien en 2009, ce dataset est un extrait anonymisé d'une banque taïwanaise.  
Il contient peu de données personnelles des clients (âge, genre, statut marital, niveau de diplome), il contient l'usage de leur carte de crédit sur les 6 derniers mois (encours, somme remboursée et éventuel retard) ; la cible est le bon paiement (0) ou le défaut de paiement (1) le mois suivant.  

**Contexte macroéconomique & Origine des données**
La crise des « Card Monsters » (Taïwan, 2005) : Résultat d'un octroi massif et laxiste de crédits renouvelables entre 2000 et 2005, provoquant une vague de surendettement et de défauts mi-2005.
La crise taïwanaise de 2005 présente une particularité majeure : elle n'a pas été provoquée par une dégradation des indicateurs macroéconomiques classiques. Les indicateurs macroéconomiques en 2005 étaient au vert : chômage stable et bas, inflation modérée et maîtrisée, et croissance du PIB solide.  
**Le blocage du refinancement** : Tant que les clients pouvaient ouvrir de nouvelles cartes, ils remboursaient les intérêts à 20 % d'une banque avec le cash tiré d'une autre. Dès que la Commissions Bancaire Taïwanaise a plafonné l'endettement (limite fixée à 22 fois le salaire mensuel), cette cavalerie s'est arrêtée net. Il s'agit ici d'une crise de liquidités, comme on a pu déjà en connaître et comme on pourrait encore en connaître.  
Échantillon source : Extraction de 30 000 dossiers clients anonymisés d'une grande banque taïwanaise (avril à septembre 2005).
**Objectifs de l'étude d'origine (Yeh & Lien, 2009)**
Urgence opérationnelle : Moderniser les outils d'octroi et de recouvrement pour endiguer les pertes d'exploitation en plein cœur de la crise.
Défi scientifique : Prouver la supériorité des algorithmes de Data Mining (arbres de décision, réseaux de neurones, K-NN) sur la régression logistique traditionnelle en période d'instabilité économique.

Les valeurs monétaires sont en dollars taïwanais, pour information 10 000 NT$ valaient 250 €, les montants importants (jusque 1 million) sont donc plausibles.
Les colonnes 'BILL_AMT' représentent l'encours sur chacun des 6 derniers mois.  
Les colonnes 'PAY_AMT' représentent le montant payé par le client sur chacun des 6 derniers mois.
Les colonnes 'PAY_' indique le niveau de l'éventuel retard de paiement sur chacun des 6 derniers mois.  
Il faut être vigilant sur le fait que le montant payé du mois correspond au montant du mois précédent
Après exploration, aucune autre donnée rattachée à ce dataset n'existe sur internet.  
L'enjeu ici sera donc de trouver les corrélations entre le comportement du client et le peu de données personnes présentes avec le risque de défaut de paiement.  

## Audit
Pas de doublon  
Pas de valeur manquante  
Des valeurs nulles sont présentes dans les colonnes 'PAY_AMTn' et 'BILL_AMTn' et sont tout à fait jusitifiées : un client peut ne pas avoir payé ou ne pas avoir d'encours sur sa carte de crédit.  
Il existe des valeurs aberrantes au sens strict du terme (via la méthode IQR) dans les colonnes monétaires ; cependant ces montants restent plausibles et représentent une population aisée et/ou dépensière qu'il ne faut pas minimiser ni écarter.  
Les colonnes de montants sont plausibles, mais des montants négatifs apparaissent dans les colonnes de factures ('BILL_AMT'), les valeurs négatives représentent environ 2% des valeurs : il s'agit probablement d'un avoir, un achat annulé, un remboursement pour le client
Les colonnes 'PAY_n', 'MARRIAGE', 'EDUCATION', sont des colonnes à variables catégorielles qui contiennent des valeurs non répertorisées :
- 'PAY_n' contient des '0' et '-2' qui ne correspondent à rien dans la nomenclature
- 'MARRIAGE' contient d'autres valeurs que celles prévues
- 'EDUCATION' contient également d'autres valeurs que celles prévues

## Nettoyage
D'après l'audit réalisé, les corrections suivantes sont appliquées :
1. 'MARRIAGE' doit être compris dans [1, 2, 3], tout ce qui est en dehors de cette liste sera placé en '3' = 'autres'
2. 'EDUCATION' doit être compris dans [1, 2, 3, 4], tout ce qui est en dehors de cette liste sera placé en '4' = 'autres'
3. les colonnes 'PAY_n' nécessitent une investigation poussée pour bien comprendre le mécanisme de mise en défaut, les valeurs hors périmètre
Aucun autre nettoyage n'est effectué à ce stade.  
Après l'EDA, des corrections cumulatives (niveaux 1 à 3) sont ajoutées dans le notebook de nettoyage :
- niveau 1 : suppression des 4 lignes avec un paiement supérieur à 1 000 000 NT$ et des comptes inactifs (aucune facture positive sur les 6 mois et aucun paiement de mai à septembre : le paiement d'avril, `PAY_AMT6`, rembourse une facture antérieure à la période et ne compte pas), correction du client 6783
- niveaux 2 et 3 : correction des PAY_n = 1 (voir « La codification PAY_n = 1 » dans la partie EDA)

## Modélisation et ingestion des données dans la BDD
modélisation du schéma relationnel en étoiles via la méthode MERISE
création d'un fichier de correspondances JSON (évolutivité future sans toucher au script)
création des tables et peuplement des tables de correspondances via un script SQL et un fichier JSON orchestré via un script Python
Ingestion des données seulement corrigées des données n'existant pas dans la nomenclature (les 30 000 lignes sont ingérées à ce stade) via un script Python
Création d'un pipeline pour création des tables et peuplement de la base de données, sécurité implémentée avec confirmation utilisateur via l'interface
Tests de cohérence entre la BDD et le dataset

## API avec FastAPI
création d'une API en local pour accéder à la base de données
chargement de l'API via la commande Bash 'uvicorn src.04_01_api:app --reload'
**Implémentations de GET :**
- nom des tables et de leurs colonnes, client via son ID : '@app.get("/tables")'
- informations d'un client via son ID : '@app.get("/client/{client_id}")'
- informations historiques sur un mois pour un client : '@app.get("/historique_mensuel/{client_id}/{mois}/{annee}")'
- informations sur tout l'historique transactionnel d'un client : '@app.get("/historique_mensuel/{client_id}")'
- information sur 5 données en même temps permettant de sortir des stats : '@app.get("/analyze/risk-by-profile")''
**Implémentations de POST :**
- création d'un client avec ces caractéristiques obligatoires et optionnelles : '@app.post("/client/")'
- création d'un historique mensuel pour un client via son ID : '@app.post("/historique_mensuel/")'
**Implémentations de PATCH :**
- modifier les données d'un client via son ID : '@app.patch("/client/{client_id}")'
- modifier les données d'un historique mensuel via client_id, mois et annee : '@app.patch("/historique_mensuel/{client_id}/{mois}/{annee}")'
**Implémentations de DELETE :**
- suppression d'une ligne d'historique mensuel par l'ID du client, le mois et l'année : '@app.delete("/historique_mensuel/")'
- suppression de tout l'historique transactionnel d'un client par son ID : '@app.delete("/historique_mensuel/client/{client_id}")'
- supprimer un client via son ID ainsi que tout son historique transactionnel : '@app.delete("/client/{client_id}")'
**Implémentations de Routes Admin :**
- Télécharger la base de données après identification sécurisée : '@app.get("/admin/telecharger-db")'

## EDA
Notebooks : [EDA laboratoire](/src/05_01_EDA_lab.ipynb) (exploration), [EDA codification 1](/src/05_04_EDA_codification1.ipynb) (étude dédiée des PAY_n = 1), [EDA contentieux](/src/05_02_EDA_contentieux.ipynb) (population contentieuse).

### Lecture des codifications PAY_n
Je constate une codification des colonnes 'PAY_n' différente de ce qui est décrit dans la documentation. Si on écarte les erreurs humaines, informatiques et autres, il se dégage une tendance claire, confirmée par les montants :
- **-2** : le client n'a pas utilisé sa carte à crédit sur le mois. 95 % de cette codification s'explique par un paiement comptant ou un encours nul ou négatif ; elle concerne donc beaucoup de comptes peu ou pas actifs.
- **-1** : la facture est payée en totalité. Les ratios de paiement se concentrent à 100 % ; quand rien n'est payé le mois même, la facture est presque toujours réglée le mois suivant (paiement enregistré avec un mois de décalage).
- **0** : utilisation à crédit (crédit renouvelable) sans retard : le plus souvent, le client paie au moins le minimum, autour de 3 à 5 % de son solde (quelques vrais non-paiements restent codés 0).
- **1** : pas une échéance de retard, mais un statut provisoire du dernier mois (voir plus bas).
- **2 et plus** : comptes en retard ; un incident fait basculer la note directement à 2.

La frontière entre 0 et -1 est une marche nette à 100 % de la facture payée : c'est ce qui justifie le seuil de 90 % (facture soldée) utilisé dans le nettoyage et dans les règles du contentieux.  
Ces indications sont très importantes pour la représentation des ensembles et la création des features pour les futurs modèles de prédiction.

### Comptes sans encours et comptes inactifs
Le taux d'incident sur la période (part des codifications PAY_n = 2) est divisé par 2,5 quand la facture exigible est nulle ou négative [il devrait idéalement tomber à 0 % alors qu'il reste de l'ordre de 4 %]. Cela laisse supposer que des dossiers avec encours nul ou négatif sont gérés en dehors du circuit classique, par exemple en recouvrement ou contentieux, ce qui expliquerait la présence d'incidents fluctuants.

Le défaut de paiement à M ('dpnm') est de 22 % dans le dataset.  
Une banque ne survivrait pas plusieurs mois avec un taux de défaillance aussi élevé, on peut s'interroger sur l'origine du dataset et de son éventuel biais, surtout mis en relation avec la forte proportion de PAY_1 = 1.  
Ceci est à mettre dans le contexte suivant : une crise importante a eu lieu en 2005 à Taïwan sur le crédit avec un emballement soudain de son usage et du taux de défaut.  
Dans le jeu de données, je constate des données incohérentes :
- 24 % de défaut de paiement à M sur des dossiers sans encours sur le dernier mois (2598 lignes)
- 30 % de défaut de paiement à M sur des dossiers avec encours négatifs sur les 6 mois (c'est-à-dire que la banque doit de l'argent au client) (88 lignes)
- 36 % de défaut de paiement à M sur des dossiers inactifs sur les 6 mois (941 comptes : aucune facture positive, et aucun paiement en dehors du règlement d'une facture antérieure à la période)

Aucune information n'existe sur internet ni dans l'étude originelle de 2009 sur ces incidents de paiement qui ne semblent pas concerner un encours. Je ne sais pas s'il s'agit d'une erreur d'encodage ou d'un autre problème de gestion interne du compte (clôture, saisie, faillite personnelle...). Chercher à nettoyer cette donnée fausserait tout le dataset car il n'y a pas de règle trouvée à ce stade sur l'apparition de ces impayés. Si on raisonne logique métier, nous cherchons à sécuriser un encours et à prévoir le défaut de paiement réel. Pour l'apprentissage des modèles :
- les comptes réellement inactifs sont écartés : ils n'apportent pas d'information et n'ont pas besoin de prédiction de défaut (supprimés au nettoyage, niveau 1) ;
- les comptes gelés, gérés ailleurs, qui affichent un comportement de défaut sans encours ni montants payés n'apportent aucune information d'apprentissage : on ne prédit pas le risque de défaut sur un crédit non utilisé ;
- un compte qui a été actif reste dans le modèle, car toute information sur le passé d'un client est de la matière enrichissante.

Plusieurs scénarios sont prévus pour encadrer tous les cas métiers cohérents sans fausser le modèle ni les données.

### La codification PAY_n = 1
**Premières observations (EDA lab)**  
La codification 1 représente 12 % des valeurs de PAY_1 ; les autres colonnes n'en possèdent pas ou très peu (moins de 0,1 %). Elle suit principalement un compte inactif, un compte activé ou réactivé, ou un compte en incidents. Deux hypothèses sont apparues : une alerte interne ou externe sur le compte, ou une codification temporaire (relance du client, incident administratif ou financier en cours). J'avais aussi envisagé un vrai impayé de 30 jours, comme l'indique la nomenclature, qui traduirait l'emballement des impayés au plus fort de la crise de 2005 : l'étude dédiée a écarté cette lecture.

Pourquoi nettoyer la colonne PAY_1 de ses 1 ? Les graphiques sont faussés sur ce mois, et le poids de cette colonne dans la décision des modèles varie à mesure que je la rectifie. D'autres features en dépendent (fréquence des incidents, cumul des codifications de retard d'un client).

**Étude dédiée** : [EDA codification 1](/src/05_04_EDA_codification1.ipynb)  
J'ai repris toutes les analyses sur les PAY_n = 1 dans un notebook dédié pour trancher une fois pour toutes les corrections à garder.
- PAY_1 = 1 est un **statut provisoire du dernier mois** : il n'existe presque qu'en M-1 et prend la place, en attendant, de sorties comme de retards maintenus que l'historique tranche ensuite. Ce n'est pas un retard d'un mois au sens de la documentation.
- **Après une codification saine**, c'est une alerte ou un statut posé sur un compte sans dette ou dont la facture est soldée : le nettoyage les corrige, et ces clients se comportent ensuite comme des clients sains.
- **Après un retard**, c'est un statut d'attente, avec une dette toujours due et des paiements partiels, dont l'issue n'est pas encore visible.

**Corrections retenues (validées par l'étude dédiée)**, dans le notebook de nettoyage :
- niveau 1 : le client 6783 a une codification PAY = 1 sur 4 mois alors qu'il paie chaque mois : sa codification est remise à 0 ;
- niveau 2 : PAY_n = 1 sur une facture exigible nulle (BILL_AMT(n+1) <= 0) : PAY_n reprend la codification précédente PAY_(n+1), en cascade de PAY_5 vers PAY_1 (passes de vérification jusqu'à ce qu'aucune correction ne s'effectue) ; les PAY_n = 1 restants sur une facture nulle (quand la codification précédente est elle-même un 1) passent à 0. Pas de retard possible sans facture due ;
- niveau 3 : si PAY_1 = 1, PAY_2 <= 0 et ratio_PAY_BILL1 >= 90 % (facture exigible BILL_AMT2 > 0), alors PAY_1 = PAY_2 : le client a soldé sa facture, il reprend sa codification antérieure ;
- dans tous les autres cas (remboursement partiel ou nul), impossible de déterminer la vraie codification : PAY_1 = 1 est maintenu.

Après le niveau 2, il reste 15 lignes avec une codification 1 en PAY_2 ou PAY_3 et 2512 lignes avec PAY_1 = 1 (8,6 % du dataset) ; après le niveau 3, il reste 1842 lignes avec PAY_1 = 1 (6,3 %), presque toutes après un retard (mois de transition, traité par le contentieux).

*Ancienne version abandonnée (seuils à 4 % / 10 % et PAY_1 = PAY_2 si PAY_2 >= 2) : elle créait des PAY_1 = 2 qui faisaient entrer des clients à tort dans la population contentieuse (CTX).*

**Les PAY_1 = 1 restants** : on ne peut pas les transformer davantage. Hors facture soldée (retour à la codification d'avant le retard) et absence de paiement sur deux factures dues (remise à 2), traitées au mois de transition par le contentieux, PAY_1 = 1 reste un statut d'attente. Cette codification est à encoder de manière spécifique pour le ML, et un modèle pourrait en départager une partie (piste d'amélioration). Deux features en découlent : la durée du dernier passage au CTX et le cumul des incidents sur 6 mois.

### Décalage entre paiements et codification, sortie d'un retard
- La codification est mise à jour avec **un mois de décalage** sur les paiements : un remboursement fait au mois n ne se voit dans la codification que le mois suivant. Il faut donc toujours regarder 2 mois avant de conclure à une absence de paiement ou à une sortie de retard.
- J'ai cherché une règle de sortie de retard autre que le paiement (ratio de paiement sur un et deux mois, évolution du solde, niveau de la série de retards) : rien de probant. La sortie augmente progressivement avec ce que le client a payé, sans frontière nette ; seule la règle métier d'une dette réglée à 90 % ou plus tient. Seuls les retards profonds (codification à 4 ou plus) sortent nettement plus rarement, ce qui est attendu mais ne fait pas une règle.
- Une partie des sorties se fait sans paiement visible (arrangement, plan de paiement, recouvrement...), et à l'inverse des clients qui ont remboursé restent codés en retard : payer n'est pas le seul facteur de sortie de la codification 2, et le dataset ne permet pas de voir le reste.
- Des comptes en incidents voient ainsi leur note de risque fortement diminuer sans paiement effectif.

### Aberrations détectées (éventuelles à traiter)
- 9 lignes présentant des montants payés et dus anormalement élevés par rapport à leur plafond, et par rapport au reste des valeurs présentes dans le dataset
- 692 lignes présentant des paiements sur des comptes à encours négatifs : expliqués majoritairement par des paiements supérieurs aux sommes dues

### Population contentieuse (CTX)
[EDA contentieux](/src/05_02_EDA_contentieux.ipynb)  
Une poche de clients au taux de défaut très élevé plafonnait les performances du ML. Je l'isole par une règle métier : ces clients sont retirés du dataset ML et prédits en défaut.  
Méthode : split train / test fait avant toute analyse, règles justifiées par la logique métier, `dpnm` utilisé uniquement pour valider sur le train, test utilisé une seule fois.  
Définition retenue (définition 2) :
- correction des faux 2 : un code 2 posé sur une facture nulle est neutralisé chez un client qui venait de payer (flag faux codage) et ne compte pas non plus pour le CTX sur un compte endormi (flag surveillance récente, cumulable avec un passage au CTX si d'autres 2 surviennent sur une vraie dette)
- mois de transition (PAY_2 >= 2 puis PAY_1 <= 1) : PAY_1 est remis à 2 si deux factures exigibles sont restées impayées (aucun paiement en M-1 ni en M-2), revient à la codification d'avant le retard si la facture de M-1 est soldée (90 % ou plus), et reste inchangé sinon
- dans l'historique, un passage au CTX nécessite deux codes >= 2 successifs ; un 2 isolé est un retard régularisé ; un 2 isolé en M-6 est considéré comme un passage au CTX (M-7 inconnu)
- à M-1, tout code >= 2 place au CTX, sauf facture payée à 90 % ou plus en M-1 ou M-2 (retard payé) : un retard isolé est codé comme une régularisation présumée ; un retard qui termine une série garde la trace du passage au CTX, avec une sortie présumée en M

Les autres clients restent dans le ML avec des indicateurs de leur historique : antériorité et mois de sortie du CTX, retard régularisé et mois de régularisation (le retard payé à M-1 est codé avec un mois de sortie 0 : régularisation présumée s'il est isolé, sortie du CTX présumée s'il termine une série), surveillance récente, faux codage.  
La codification des retards est très incohérente (un même code 2 recouvre un vrai retard, une surveillance de compte réactivé, un décalage de mise à jour...) : j'ai gardé les codes de la banque autant que possible et ne les corrige que lorsque les montants les contredisent.


## Restitution décisionnelle Power BI
- **Connexion SQLite via Python** : Ingestion automatique de l'ensemble des tables sans dépendance ODBC externe.
- **Validation du modèle** : Vérification des cardinalités (1:N) et du filtrage croisé sur le schéma en étoile.
- **Validation du pipeline** : Test d'intégration bout en bout sur données brutes (actualisation dynamique garantie après EDA).
- **Versionnement** : Intégration du rapport `.pbix` dans le dépôt Git (`power_bi/`).


## Machine Learning
Journal détaillé des expérimentations : [tableau ML](/lab_ML/1ere_iteration/tableau_ML.md) (première itération)
- Premiers essais sur les niveaux de nettoyage 0 à 3 et plusieurs scénarios de population, pilotés par un score de décision (moyenne du ROC AUC et du F2 score)
- Feature engineering sur le niveau 3 et le périmètre `S12` (encours positif à M-1, plafond <= 500 000 NT$)
- La variable `CTX` ajoutée en `S12_7` révèle une population contentieuse qui plafonne les modèles : étude dédiée (voir EDA, population contentieuse)
- Redémarrage : le ML repart sur le dataset nettoyé de sa population contentieuse, les clients au CTX étant prédits en défaut par la règle métier. La règle seule sert de référence de départ ; le système complet (règle + modèle) sera évalué sur le même jeu de test

## Déploiement en ligne
- Test déploiement sur Render avec BDD en ligne OK
- Test déploiement sur Streamlit Community Cloud OK
- API fonction get_metadata_mappings() : sert de passerelle dynamique entre les tables de correspondances et Streamlit (à mettre à jour si une nouvelle table est créée)
- Zone Administrateur sécurisée avec une fonction API dédiée


## Problèmes rencontrés
Comprendre la logique du dataset, la logique de la codification des impayés a pris énormément de temps. La documentation liée à ce dataset ne correspondait pas à ce que je pouvais constater tant dans l'étendue des valeurs codées que dans leur signification.
Le dataset date de 2005 et l'équipe de recherche n'indique pas l'origine exacte des données, en tous cas elle n'indique pas si plusieurs tables ont servi à synthétiser ce jeu de données.  
Le mode de fonctionnement de l'époque est assez opaque dans la gestion du crédit et la codification qui en découle
L'utilisation de 2 scores et du recall pour comparer les performances des modèles en apprentissage automatique était problématique. J'ai fait le choix de basculer sur F2 score pour intégrer plus fortement le recall dans l'évaluation du modèle, tout en conservant le ROC AUC. Je fais ainsi une moyenne qui est un score maîitre cohérent pour décider de la performance d'un modèle et de la pertinence d'une feature intégrée ou modifiée.