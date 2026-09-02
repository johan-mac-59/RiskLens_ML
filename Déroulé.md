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

## EDA
Je constate une tendance de codification des colonnes 'PAY_n' légèrement différente de ce qui est décrit dans la documentation  
Si on écarte les erreurs humaines, informatiques et autres, il se dégage une certaine tendance concernant les valeurs de PAY_n :
- -2 correspond à des comptes majoritairement inactifs
- -1 et 0 correspondent à des comptes ayant un fonctionnement sain ne présentant pas de retard
- 1 correspond à une sorte d'alerte sur le compte (fin d'un retard, activation ou réactivation d'un compte), il ne semble pas forcemment correspondre à une échéance de retard
- 2 et + correspondent à des comptes avec retards, en effet un incident fait basculer la note directement à 2
Ces indications sont très importantes pour la représentation des ensembles et la créations des features pour les futurs modèles de prédiction

Le taux d'incident de paiement est divisé par 2,5 en cas d'encours nul ou négatif [il devrait idéalement tomber à 0% alors qu'il est présent à hauteur de 4%]. Cela laisse supposer que des dossiers avec encours nul ou négatif sont gérés en dehors du circuit classique, par exemple en recouvrement ou contentieux,  cela expliquerait la présence d'incidents fluctuant. Il ne sera pas question de nettoyage pour ces données qui sont un bruit certes mais représentent un nombre de lignes restreints.  Pour l'apprentissage des modèles, il sera intéressant d'exclure les comptes dits inactifs pour 2 raisons :
- écarter les comptes réellement inactifs sans activité car ils n'apportent pas d'informations intéressantes et n'ont pas besoin de prédiction de défaut
- écarter les comptes gelés, gérés ailleurs qui affichent un comportement de défaut mais qui n'apportent aucune information d'apprentissage pour le modèle en l'absence d'encours et de montants payés

Le défaut de paiement futur 'dpnm' est de 22% dans le dataset.  
Une banque ne survivrait pas plusieurs mois avec un taux de défaillance aussi élevé, on peut s'interroger sur l'origine du dataset et de son éventuel biais, surtout mis en relation avec la forte proportion de PAY_1 = 1.  
Ceci est à mettre dans le contexte suivant : une crise importante a eu lieu en 2005 à Taïwan sur le crédit avec un emballement soudain de son usage et du taux de défaut.
Dans le jeu de données, je constate des données incohérentes :
- 24% de défaut de paiement futur sur des dossiers sans encours sur le dernier mois (2598 lignes)
- 30% de défaut de paiement futur sur des dossiers avec encours négatifs sur les 6 mois (c'est à dire que la banque doit de l'argent au client)(88 lignes)
- 37% de défaut de paiement futur sur des dossiers inactifs sur les 6 mois (866 comptes)
Aucune information n'existe sur internet ni dans l'étude originelle de 2009 sur ces incidents de paiement qui ne semblent pas concerner un encours. Je ne sais pas s'il s'agit d'une erreur d'encodage, d'un autre problème de gestion interne du compte (clôture, saisie, faillite personnelle...). Chercher à nettoyer cette donnée fausserait tout le dataset car il n'y a pas de règle trouvée à ce stade sur l'apparition de ces impayés. Si on raisonne logique métier, nous cherchons à sécuriser un encours et à prévoir le défaut de paiement réel.  
Il conviendra donc de ne pas inclure ces comptes inactifs dans les modèles d'apprentissage et de ne pas prédire le risque de défaut sur un crédit non utilisé.  
Par contre, un compte qui a été actif doit être inclus dans le modèle car toute information sur le passé d'un client est de la matière enrichissante.  
Plusieurs scenarii seront à prévoir pour encadrer tous les cas métiers cohérents pour ne pas fausser le modèle ni les données

J'analyse le code '1' dans PAY_n, je commence par sa répartition dans le dataset : il représente 12% des valeurs de PAY_1, les autres colonnes n'en possèdent pas ou très peu (moins de 0.1%).  
Ce code 1 n'est jamais suivi par autre chose que lui-même. De plus, il suit principalement un compte inactif, un compte activé/réactivé ou un compte en incidents.  
Deux hypothèses apparaissent :
- le code 1 est une alerte interne ou externe sur le compte
- le code 1 vient d'autre chose ou est une codification temporaire (relance du client, incident administratif/financier en cours)
Je n'envisage aucune correction de cette valeur, les indications que j'ai dans le dataset montre que le code 1 ne précède rien d'autres que 1.
La brusque envolée perçue peut etre le but de l'étude originelle de ce dataset, un réel emballement des impayés au plus fort de la crise de 2005. Cela pourrait finalement correspondre à un impayé de 30 jours comme l'indique la nomenclature.  
Le traitement de cette colonne avec cette donnée particulière sera à encoder de manière spécifique pour le ML.  

**Aberrations détectées :** éventuelles à traiter
- 9 lignes présentant des montants payés et dus anormalement élevés par rapport à leur plafond, et par rapport au reste des valeurs présentes dans le datase
- 692 lignes présentant des paiements sur des comptes à encours négatifs : expliqués majoritairement par des paiements supérieurs aux sommes dues




## Problèmes rencontrés
Comprendre la logique du dataset, la logique de la codification des impayés a pris énormément de temps. La documentation liée à ce dataset ne correspondait pas à ce que je pouvais constater tant dans l'étendue des valeurs codées que dans leur signification.
Le dataset date de 2005 et l'équipe de recherche n'indique pas l'origine exacte des données, en tous cas elle n'indique pas si plusieurs tables ont servi à synthétiser ce jeu de données.  
Le mode de fonctionnement de l'époque est assez opaque dans la gestion du crédit et la codification qui en découle