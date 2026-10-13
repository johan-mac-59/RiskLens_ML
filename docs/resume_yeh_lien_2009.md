# Yeh et Lien (2009) : résumé en français

**Article résumé** : I-Cheng Yeh et Che-hui Lien (2009), « The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients », *Expert Systems with Applications*, vol. 36, n° 2, p. 2473-2480, [doi:10.1016/j.eswa.2007.12.020](https://doi.org/10.1016/j.eswa.2007.12.020). © 2007 Elsevier Ltd.

L'article se consulte chez l'éditeur, par le lien DOI ci-dessus ; une copie en PDF est en ligne [ici](https://bradzzz.gitbooks.io/ga-dsi-seattle/content/dsi/dsi_05_classification_databases/2.1-lesson/assets/datasets/DefaultCreditCardClients_yeh_2009.pdf). Cette page en donne un résumé en français. Les citations sont reprises mot pour mot dans la langue de l'article, avec leur page, suivies d'une traduction entre parenthèses.

---

## 1. Le contexte

L'étude se place en pleine crise des cartes de crédit à Taïwan. Pour gagner des parts de marché, les banques ont distribué des cartes à des clients qui n'avaient pas les moyens de rembourser, et beaucoup de porteurs se sont lourdement endettés. Les auteurs écrivent que « the credit card issuers in Taiwan faced the cash and credit card debt crisis and the delinquency is expected to peak in the third quarter of 2006 » (p. 2473) (les émetteurs de cartes de crédit à Taïwan ont fait face à la crise de la dette des cartes de crédit et de retrait, et les impayés devraient atteindre leur pic au troisième trimestre 2006).

Pour eux, une banque doit prévoir le risque en amont plutôt que gérer la crise en aval, à partir des informations dont elle dispose sur ses clients : relevés, paiements, historique de remboursement.

## 2. La question posée

Les auteurs défendent une idée centrale : pour gérer le risque, une probabilité de défaut de paiement vaut mieux qu'un simple classement en « risqué / pas risqué ». Ils l'écrivent ainsi : « From the perspective of risk control, estimating the probability of default will be more meaningful than classifying customers into the binary results – risky and non-risky » (p. 2473) (du point de vue du contrôle des risques, estimer la probabilité de défaut a plus de sens que classer les clients en deux catégories, risqués et non risqués).

L'article répond à deux questions :
1. les six méthodes comparées classent-elles les clients avec la même justesse ?
2. la probabilité de défaut de paiement qu'elles calculent reflète-t-elle la probabilité réelle ?

## 3. Les données

Les données viennent d'une grande banque taïwanaise : « Our study took payment data in October, 2005, from an important bank (a cash and credit card issuer) in Taiwan » (p. 2475) (notre étude a pris les données de paiement d'octobre 2005 d'une banque importante, émettrice de cartes de crédit et de retrait, à Taïwan).

- **La cible** est le défaut de paiement (oui = 1, non = 0) : « Among the total 25,000 observations, 5529 observations (22.12%) are the cardholders with default payment » (p. 2475) (sur 25 000 observations au total, 5 529, soit 22,12 %, sont des porteurs en défaut de paiement).
- **Les 23 variables explicatives** : le plafond de crédit (qui inclut les cartes supplémentaires de la famille), le sexe, le niveau d'études, la situation familiale, l'âge, puis, d'avril à septembre 2005, l'état de remboursement de chaque mois, le montant de chaque relevé et le montant de chaque paiement.
- **L'échelle de l'état de remboursement** : « −1 = pay duly; 1 = payment delay for one month; 2 = payment delay for two months; ... ; 8 = payment delay for eight months; 9 = payment delay for nine months and above » (p. 2475) (−1 = paiement en règle ; 1 = retard de paiement d'un mois ; 2 = retard de deux mois ; … ; 9 = retard de neuf mois et plus).
- Les données sont tirées au hasard en deux groupes, l'un pour entraîner les modèles, l'autre pour les valider. L'article ne donne pas la taille de chaque groupe.

## 4. Les six méthodes comparées

| Méthode | Principe, en une phrase |
|---|---|
| k plus proches voisins | Un client prend la classe la plus fréquente parmi les clients qui lui ressemblent le plus |
| Régression logistique | Une formule simple qui donne une probabilité, mais qui gère mal les effets non linéaires et les interactions entre variables |
| Analyse discriminante | Proche de la régression logistique, elle cherche à séparer au mieux les deux groupes |
| Bayésien naïf | Il suppose que chaque variable agit indépendamment des autres |
| Réseau de neurones | Il apprend des relations non linéaires entre les variables, sans donner de formule simple |
| Arbre de classification | Une suite de questions sur une variable à la fois, facile à lire mais sensible aux données d'apprentissage |

## 5. Comment les modèles sont mesurés

Les auteurs écartent le taux d'erreur. Comme la plupart des clients ne sont pas en défaut de paiement, un modèle peut se tromper peu tout en repérant mal les clients à risque : « most records in the data set of credit card customers are non-risky (87.88%); therefore, the error rate is insensitive to classification accuracy of models » (p. 2475) (la plupart des clients du jeu de données ne sont pas risqués, 87,88 % ; le taux d'erreur est donc peu sensible à la justesse du classement des modèles).

Ils utilisent à la place le **rapport d'aire** de la courbe de gain (« lift chart »). On classe les clients du plus risqué au moins risqué selon le modèle, puis on compte combien de défauts de paiement on trouve au fur et à mesure. Le rapport d'aire compare la courbe du modèle à celle d'un modèle parfait : 0 = pas mieux que le hasard, 1 = modèle parfait.

## 6. Les résultats du classement

Sur l'échantillon de validation (tableau 1, p. 2477) :

| Méthode | Taux d'erreur | Rapport d'aire |
|---|---|---|
| Réseau de neurones | 0,17 | **0,54** |
| Arbre de classification | 0,17 | 0,536 |
| Bayésien naïf | 0,21 | 0,53 |
| k plus proches voisins | 0,16 | 0,45 |
| Régression logistique | 0,18 | 0,44 |
| Analyse discriminante | 0,26 | 0,43 |

Les taux d'erreur sont proches d'une méthode à l'autre, alors que les rapports d'aire s'écartent davantage. Le réseau de neurones arrive en tête.

**Lecture du projet** : le rapport d'aire d'une courbe de gain est ce qu'on appelle aussi le coefficient de Gini. Il se convertit en AUC par AUC = (1 + rapport d'aire) / 2 : le 0,54 du réseau de neurones correspond donc à une **AUC de 0,77**. Cette conversion est celle du projet ; l'article ne donne pas d'AUC.

## 7. La probabilité de défaut de paiement

La probabilité réelle de défaut de paiement d'un client n'est pas connue : on sait seulement s'il a été en défaut ou non. Les auteurs proposent donc une méthode pour l'estimer, la **méthode de lissage par tri** (« Sorting Smoothing Method ») :
1. on range les clients de validation selon la probabilité donnée par le modèle ;
2. pour chaque client, la probabilité « réelle » estimée est la part de défauts de paiement parmi lui et ses voisins dans ce classement (50 de chaque côté).

On compare ensuite, client par client, la probabilité du modèle à cette probabilité estimée. Si le modèle est juste, les points s'alignent sur une droite de pente 1 qui passe par 0.

Seul le réseau de neurones remplit ces conditions : pente 0,998, ordonnée à l'origine 0,0145 et R² de 0,965 (tableau 2, p. 2479). Les autres méthodes classent parfois bien les clients, mais leurs probabilités sont trop hautes ou trop basses.

## 8. La conclusion des auteurs

Le réseau de neurones est le meilleur des six, à la fois pour classer les clients et pour donner une probabilité de défaut de paiement fiable. D'où leur recommandation : « Therefore, artificial neural networks should be employed to score clients instead of other data mining techniques, such as logistic regression » (p. 2479) (les réseaux de neurones devraient donc être utilisés pour noter les clients, plutôt que d'autres techniques comme la régression logistique).

## 9. Points à garder en tête en lisant l'article avec le dataset publié

- **Le nombre de clients** : l'article décrit 25 000 observations, le dataset publié en contient 30 000.
- **La part de clients risqués** : l'article annonce 22,12 % de clients en défaut de paiement (p. 2475), puis, sur la même page, 87,88 % de clients non risqués, soit 12,12 % de risqués. Les deux chiffres ne concordent pas.
- **Les codifications** : l'échelle de l'article va de −1 à 9. Le dataset publié contient aussi les valeurs −2 et 0, que l'article ne décrit pas. De même, il contient des niveaux d'études (0, 5, 6) et une situation familiale (0) absents de la description.
- **La cible** : l'article ne précise pas comment la banque a décidé qu'un client était en défaut de paiement (montant, durée de retard, date exacte).
- **Le découpage** : l'article compare les six méthodes sur un seul tirage entraînement / validation, sans en donner la taille.
