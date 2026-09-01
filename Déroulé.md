## Compréhension du dataset
**Explorer le dataset, comprendre son contenu, son origine, sa signification**  
Le fichier Kaggle est une copie conforme d'un dataset de 2009 publié par des chercheur, ce dataset est un extrait anonymisé d'une banque taïwanaise.  
Il contient peu de données personnelles des clients (âge, genre, statut marital, niveau de diplome), il contient l'usage de leur carte de crédit sur les 6 derniers mois (encours, somme remboursée et éventuel retard) ; la cible est le bon paiement (0) ou le défaut de paiement (1) le mois suivant.  
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

Avant de tenter un nettoyage, je constate une tendance de codification légèrement différente de ce qui est décrit dans la documentation  
Si on écarte les erreurs humaines, informatiques et autres, il se dégage une certaine tendance concernant les valeurs de PAY_n :
- -2 correspond à des comptes majoritairement inactifs
- -1 et 0 correspondent à des comptes ayant un fonctionnement sain ne présentant pas de retard
- 1 correspond à une sorte d'alerte sur le compte (fin d'un retard, activation ou réactivation d'un compte), il ne semble pas forcemment correspondre à une échéance de retard
- 2 et + correspondent à des comptes avec retards, en effet un incident fait basculer la note directement à 2
Ces indications sont très importantes pour la représentation des ensembles et la créations des features pour les futurs modèles de prédiction

Le défaut de paiement futur 'dpnm' est de 22% dans le dataset.  
Une banque ne survivrait pas plusieurs mois avec un taux de défaillance aussi élevé, on peut s'interroger sur l'origine du dataset et de son éventuel biais, surtout mis en relation avec la forte proportion de PAY_1 = 1.  
Ceci est à mettre dans le contexte suivant : une crise importante a eu lieu en 2005 à Taïwan sur le crédit avec un emballement soudain de son usage et du taux de défaut.
Dans le jeu de données, je constate des données incohérentes :
- 24% de défaut de paiement futur sur des dossiers sans encours sur le dernier mois (2598 lignes)
- 30% de défaut de paiement futur sur des dossiers avec encours négatifs sur les 6 mois (c'est à dire que la banque doit de l'argent au client)(88 lignes)
- 37% de défaut de paiement futur sur des dossiers inactifs sur les 6 mois (866 comptes)
Aucune information n'existe sur internet ni dans l'étude originelle de 2009 sur ces incidents de paiement qui ne semblent pas concerner un encours. Je ne sais pas s'il s'agit d'une erreur d'encodage, d'un autre problème de gestion interne du compte (clôture, saisie, faillite personnelle...). Chercher à nettoyer cette donnée fausserait tout le dataset car il n'y a pas de règle trouvée à ce stade sur l'apparition de ces impayés. Si on raisonne logique métier, nous cherchons à sécuriser un encours et à prévoir le défaut de paiement réel.  
Il conviendra donc de ne pas inclure ces comptes inactifs dans les modèles d'apprentissage et de ne pas prédire le risque de défaut sur un crédit non utilisé.  
Par, un compte qui a été actif doit être inclus dans le modèle car toute information sur le passé d'un client est de la matière enrichissante.  
Plusieurs scenarii seront à prévoir pour encadrer tous les cas métiers cohérents pour ne pas fausser le modèle ni les données


## Nettoyage