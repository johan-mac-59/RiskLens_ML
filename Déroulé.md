## Compréhension du dataset
**Explorer le dataset, comprendre son contenu, son origine, sa signification**  
Le fichier Kaggle est une copie conforme d'un dataset de 2009 publié par des chercheur, ce dataset est un extrait anonymisé d'une banque taïwanaise.  
Il contient peu de données personnelles des clients (âge, genre, statut marital, niveau de diplome), il contient l'usage de leur carte de crédit sur les 6 derniers mois (encours, somme remboursée et éventuel retard) ; la cible est le bon paiement (0) ou le défaut de paiement (1) le mois suivant.  
Les valeurs monétaires sont en dollars taïwanais, pour information 10 000 NT$ valaient 250 €, les montants importants (jusque 1 million) sont donc plausibles.
Les colonnes 'BILL_AMT' représentent l'encours sur chacun des 6 derniers mois.  
Les colonnes 'PAY_AMT' représentent le montant payé par le client sur chacun des 6 derniers mois.
LEs colonnes 'PAY_' indique le niveau de l'éventuel retard de paiement sur chacun des 6 derniers mois.  
Après exploration, aucune autre donnée rattachée à ce dataset n'existe sur internet.  
L'enjeu ici sera donc de trouver les corrélations entre le comportement du client et le peu de données personnes présentes avec le risque de défaut de paiement.  

## Audit & Nettoyage
Pas de doublon  
Pas de valeur manquante  
Des valeurs nulles sont présentes dans les colonnes 'PAY_AMTn' et 'BILL_AMTn' et sont tout à fait jusitifiées : un client peut ne pas avoir payé ou ne pas avoir d'encours sur sa carte de crédit.  
Il existe des valeurs aberrantes au sens strict du terme (via la méthode IQR) dans les colonnes monétaires ; cependant ces montants restent plausibles et représentent une population aisée et/ou dépensière qu'il ne faut pas minimiser ni écarter.  
Les colonnes de montants sont plausibles, mais des montants négatifs apparaissent dans les colonnes de factures ('BILL_AMT'), les valeurs négatives représentent environ 2% des valeurs : **à investiguer**  
Les colonnes 'PAY_n', 'MARRIAGE', 'EDUCATION', sont des colonnes à variables catégorielles qui contiennent des valeurs non répertorisées : **à investiguer** :
- 'PAY_n' contient des '0' et '-2' qui ne correspondent à rien dans la nomenclature
- 'MARRIAGE' contient d'autres valeurs que celles prévues
- 'EDUCATION' contient également d'autres valeurs que celles prévues