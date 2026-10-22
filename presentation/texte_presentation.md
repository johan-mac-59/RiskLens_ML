# Texte de présentation — RiskLens ML

*Texte dit à l'oral pendant la soutenance, diapo par diapo. Les diapos sont dans `RiskLensML_Restitution.pdf`. Cette présentation s'adresse à tout public : aucune connaissance en analyse de données ni en apprentissage automatique n'est nécessaire pour la suivre.*

---

## Diapo 1 — Titre

Bonjour à toutes et à tous. Je m'appelle Johan, et je vais vous présenter RiskLens ML, mon projet de fin de bootcamp.

Au départ, il y a un jeu de données : six mois d'historique de 30 000 clients d'une banque taïwanaise, en 2005. À partir de ces données, je me suis posé une question :
« Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ? »

Tout d'abord, voici le déroulé.

---

## Diapo 2 — Sommaire

Je vais expliquer la question et son contexte. Puis le chemin du projet : comprendre les données et les corriger, repérer les clients déjà en difficulté, puis construire un modèle d'apprentissage automatique pour tous les autres. Ensuite une démonstration en direct. Enfin la réponse, ses limites, ce qu'une banque pourrait en faire, et vos questions.

---

## Diapo 3 — La question

Prenons la question morceau par morceau.

« Le défaut de paiement », c'est un client qui ne paie pas ce qu'il doit sur sa carte de crédit.

« Son comportement transactionnel des 6 derniers mois » : pour chaque client, j'ai six mois d'historique de sa carte, d'avril à septembre. Chaque mois, sa facture, ce qu'il a payé, et la note que la banque lui a mise. La question est : avec ça, peut-on deviner s'il paiera en octobre ?

« Malgré un manque d'informations économiques globales » : je n'ai pas ce que les banques utilisent d'habitude, c'est-à-dire le revenu du client, ses crédits ailleurs, ni l'état de l'économie.

Pour comprendre ces données, il faut savoir d'où elles viennent.

---

## Diapo 4 — Le contexte

Elles viennent d'une vraie banque de Taïwan, pendant une crise qu'on a appelée la crise des « Card Monsters ». Je vous la raconte en six étapes.

Dans les années 1990, le nombre de banques double, et la concurrence s'emballe. De 2002 à 2005, elles distribuent des cartes à tout le monde : en 2005, 133 cartes pour 100 adultes. Beaucoup de clients paient une carte avec une autre.

En 2005, le régulateur durcit les règles. Ce système se grippe, et c'est précisément pendant nos six mois de données que les impayés montent. Octobre, encadré en bordeaux, c'est le mois qu'on cherche à prévoir. Ensuite la crise éclate, et des chercheurs étudient ces données.

Résultat : 22 % des clients ne paient pas en octobre, plus d'un sur cinq. C'est beaucoup plus que dans une banque ordinaire. Et un point important : l'économie allait bien. C'est une crise du crédit, pas une crise économique.

Voici maintenant comment j'ai travaillé sur ces données.

---

## Diapo 5 — La démarche

J'ai d'abord vérifié les données et corrigé ce qui devait l'être. Je les ai rangées dans une base de données, l'endroit où une banque range les informations de ses clients. Puis je les ai explorées pour comprendre qui ne paie pas.

Un premier modèle a plafonné : c'est en revenant aux données que j'ai repéré les clients déjà en difficulté, que la banque peut traiter sans aucun modèle. Pour tous les autres, j'ai construit un second modèle, mis en service sur un site internet que vous verrez en direct.

Commençons par les données elles-mêmes.

---

## Diapo 6 — Les anomalies

Avant d'analyser quoi que ce soit, il faut comprendre les données. Le fichier est complet : il ne manque aucune valeur. Mais il contient des anomalies. Le tableau les liste toutes, avec ce que j'en ai fait ; au total, je garde 96 % des clients.

Je m'arrête sur ce qui compte pour la suite : les notes de la banque. Chaque mois, la banque pose une note sur chaque client ; elle l'appelle une « codification ». Deux choses posaient problème. La note « 1 » n'apparaît presque qu'en septembre, chez plus de 3 000 clients, sans explication : je l'ai corrigée, et je vous montrerai comment. Et d'avril à juin, la banque était plus souple qu'en juillet et août : j'ai appliqué la même règle de retard sur toute la période, pour qu'un même comportement reçoive la même note.

Chaque décision vient du fonctionnement de la banque, jamais du résultat qu'on cherche à prévoir : sinon, ce serait tricher.

Une fois les données comprises, je les ai explorées.

---

## Diapo 7 — Le profil et le comportement

Pour chaque information sur le client, je compare ses groupes. Pour l'âge, par exemple : les 21-25 ans, les 26-30 ans, et ainsi de suite.

Chaque barre va du groupe le moins risqué au groupe le plus risqué. Plus elle est longue, plus l'information sépare les bons et les mauvais payeurs. La ligne orange, c'est la moyenne : 22 %.

En ocre, le profil : l'âge, le genre, le niveau d'études, le statut marital. Les barres sont plutôt courtes : selon l'âge, on va de 19 à 27 %. Les études font un peu exception : un petit groupe de clients, classés « autre », ne paie pas dans 7 % des cas seulement.

En bleu, le comportement : le plafond de la carte, son utilisation, la façon de rembourser, les retards. Les barres sont longues : par exemple un client utilisant 100% de son plafond de crédit a deux fois plus de chances de faire défaut qu'un client qui l'utilise peu.

C'est ce constat qui guide la suite : c'est dans le comportement qu'il faut chercher.

Et parmi les comportements, un ressort plus que les autres : les retards.

---

## Diapo 8 — Les retards

Ce graphique, c'est le cœur de l'exploration.

Chaque barre, c'est la part des clients qui ne paient pas en octobre.  

J'ai rangé les clients selon le nombre de mois où la banque les a notés en retard. Sans aucun retard : 11 %. Un seul mois de retard, et on passe à un sur quatre. Six mois de retard : sept clients sur dix.

---

## Diapo 9 — La dette

Ce graphique montre la crise vue par la banque.

Chaque barre, c'est tout ce que les clients lui doivent à la fin d'un mois. La petite partie verte en bas, c'est ce qu'ils remboursent le mois suivant : environ 12 %, toujours la même proportion. Le reste, en rose, est reporté.

Résultat : la dette totale grossit d'un tiers en six mois. Les clients ne changent pas leurs habitudes, mais la dette, elle, s'envole.

Parmi ces clients, certains sont déjà en grande difficulté.

---

## Diapo 10 — Les clients en difficulté

Voici une simplification des codifications de la banque pour vous exposer les règles mises en places : 0 = client à jour de paiement, 2 ou + : clients en retard de paiement.

Première règle : deux notes de retard d'affilée, ou un retard de trois mois ou plus, et le client est en incident de paiement. C'est le client A. en incident de paiement en septembre -> le client est prédit en défaut pas la règle.  

Seconde règle : un client à jour jusqu'en août, mais déjà noté en retard en septembre, comme le client B. La banque considère déjà sa facture de septembre comme impayée : on dit qu'il est en retard imminent.

Ces deux groupes sont mis de côté par les règles et prédits en défaut, sans modèle. Résultat : ces deux groupes ne font que 17 % des clients, mais ils portent près de la moitié des défauts, et six sur dix ne paient pas en octobre.

Le client C, qui a eu un retard isolé qu'il a rattrapé, et le client D, sorti de son incident, ne sont dans aucun de ces deux groupes : ils restent dans le jeu de données.

Et pour tous les autres clients, comment fait-on ?

---

## Diapo 11 — Un modèle, c'est quoi ?

Il faut un modèle d'intelligence artificielle, plus précisément d'apprentissage automatique. C'est un programme qui apprend à partir d'exemples.

On lui montre des milliers de clients du passé dont on connaît la fin de l'histoire : ils ont payé, ou pas. Il apprend tout seul quels comportements précèdent souvent un défaut. Face à un nouveau client, il compare son historique à ce qu'il a appris, et lui donne une note de risque. Il ne dit pas « oui » ou « non » : il range les clients du plus risqué au moins risqué.

C'est comme un élève. On l'entraîne sur des exercices corrigés, puis on le note sur un examen qu'il n'a jamais vu. Ici, un client sur cinq est mis de côté dès le départ, et on ne le regarde qu'une seule fois, à la toute fin : c'est l'examen final.

Dans ce projet, les modèles servent deux fois.

---

## Diapo 12 — Corriger la note « 1 »

Pour appliquer ces règles, il a d'abord fallu régler un problème de notes de la banque. En septembre, plus de 3 000 clients ont une note « 1 » : une note d'attente, la banque n'a pas encore tranché, car le paiement d'octobre n'est pas connu.

Si le client était à jour en août, je reprends sa note d'août : c'est le client G. S'il était en retard en août, la question est : est-il sorti de son retard ? Trois modèles différents répondent, chacun a appris sur les mois où la banque a tranché elle-même. Si les trois sont d'accord, comme pour le client E, la note est corrigée : à jour. Sinon, comme pour le client F, le retard est maintenu.

---

## Diapo 13 — Le modèle classe les autres clients

Deuxième usage, le plus important : classer les clients que les règles n'ont pas retenus, ceux qui restent dans le jeu de données. Le modèle retenu s'appelle CatBoost. Il est fait d'arbres de décision : une suite de questions comme un jeu de devinettes. Chaque chemin mène à une note de risque. CatBoost en fait voter des centaines, chacun corrigeant les erreurs des précédents. À la fin, chaque client reçoit une note, et on les range du plus risqué au moins risqué.

Voici ce que donne ce classement.
---

## Diapo 14 — Les niveaux de risque

Chaque barre représente la part de clients qui ne paient pas en octobre.

Sur la gauche, les clients mis de coté par les règles métiers à l'aide de la codification de la banque.

Pour les autres clients, le modèle les range du plus risqué au moins risqué, et on les regroupe en niveaux.

A très haut risque, quatre sur dix ne paient pas ; haut risque, un sur quatre ; risque modéré, moins d'un sur cinq ; risque faible, moins d'un sur dix. La ligne orange, c'est un client pris au hasard parmi ceux que classe le modèle : 14 %.

Un client « très haut risque » ne paie pas près de cinq fois plus souvent qu'un client « risque faible ». Et le modèle y arrive avec le comportement de paiement, sans l'âge, le genre ni le statut marital, et sans les notes de la banque mois par mois : il n'en garde que le nombre de mois en retard.

Tout cela tourne en direct. Je vais vous montrer.

---

## Diapo 15 — La démo

Cette partie n'est pas lue : la démonstration se fait en direct sur le site, devant le public. Voici ce qui est montré.

Je présente d'abord les deux démonstrations, toutes deux sur des clients que les modèles n'ont jamais vus : à gauche, le système du projet (les règles, puis le modèle) ; à droite, la même question posée sans mon travail, avec un modèle lancé directement sur le fichier tel qu'il a été publié.

**Démo 1 : le système du projet.** Sur le site, page 7.2, je tire un lot dans la réserve de 5 400 clients mis de côté dès le départ et je l'injecte. Le site déroule les étapes : les deux règles, puis le modèle, puis la comparaison avec ce qui s'est vraiment passé en octobre 2005. Je commente les quatre colonnes de résultats, de gauche à droite : clients en incident, clients en retard imminent, clients que le modèle déclare en défaut, clients qu'il ne déclare pas.

**Démo 2 : les 30 000 clients du fichier publié.** Sur le site, page 7.4, j'injecte les clients, lus dans la base de données par l'API. J'explique pendant le chargement qu'ils sont notés par des modèles qui ne les ont pas appris. Quand le lot est traité, je montre les neuf niveaux de risque.

**Un client au hasard.** Je tire un client, je montre sa fiche, puis je lis le verdict affiché par le site, qui compare la prévision avec ce qui s'est passé en octobre : défaut détecté, fausse alerte, défaut non détecté, ou client qui a payé.

Je reviens ensuite au diaporama.

---

## Diapo 16 — Le verdict

Alors, peut-on prévoir le défaut ? Oui, en partie. Une analyse métier, tirée des notes de retard de la banque relues avec les paiements, prévoit près de la moitié des défauts sans aucun modèle. Un modèle fondé sur le comportement de paiement classe ensuite les autres clients par niveau de risque. Le reste ne s'annonce pas dans les données.

Les deux règles signalent 17 % des clients et trouvent déjà près de la moitié des défauts. Puis on ajoute les niveaux du modèle : avec le très haut et le haut risque, on trouve près des deux tiers des défauts en signalant moins d'un client sur trois. Jusqu'où aller, c'est à la banque de le choisir, selon ce que lui coûte une fausse alerte.

Pour situer ce résultat, on peut le comparer à l'étude des chercheurs qui ont publié ces données en 2009. On se compare sur une note de classement : prenez un client qui ne paiera pas et un client qui paiera ; 79 fois sur 100, le système classe le premier comme plus risqué. Pile ou face, ce serait 50. L'étude faisait 77 : mon système fait un peu mieux, mais du même ordre.

Mais même en tête de liste du modèle, plus d'un client signalé sur deux paie. Le modèle classe les clients ; il ne désigne pas à coup sûr ceux qui ne paieront pas.

---

## Diapo 17 — Les limites

Pourquoi ne fait-il pas mieux ? Regardez le même graphique qu'avant. En gris, les écarts de risque sur tous les clients, ceux que vous avez déjà vus. En bleu, les mêmes variables, mais seulement sur les clients que les règles ont laissés au modèle.

Les écarts se réduisent. Le nombre de mois en retard séparait les clients de 11 % à 70 % ; il ne les sépare plus que de 11 % à 39 %. Le plafond de la carte allait de 12 % à 32 % ; il ne va plus que de 8 % à 20 %. Les règles ont déjà pris les cas les plus nets. Il reste au modèle des clients plus difficiles à départager, et environ un quart de leurs défauts ne s'annonce pas du tout dans les données.

Du profil, le modèle ne garde que le niveau d'études, et c'est cohérent : c'est l'information de profil qui sépare le plus ces clients, de 6 % à 15 %.  

La limite vient donc des données, pas des modèles. On ne connaît pas la définition exacte du défaut utilisée par la banque, ni le revenu des clients, ni leurs dettes dans d'autres banques, alors que la crise venait justement de là.

---

## Diapo 18 — Les recommandations

Pour conclure, ce qu'une banque pourrait en faire.

D'abord les deux règles, que n'importe quel conseiller comprend et peut appliquer. Ensuite le modèle, pour les autres clients, en traitant d'abord les plus risqués. Et toujours une personne au bout : le niveau de risque sert à choisir qui surveiller en premier, jamais à décider seul du sort d'un client. C'est aussi ce qu'impose le droit.

Et pour aller plus loin, ce n'est pas un meilleur modèle qu'il faut, mais de meilleures données.

---

## Diapo 19 — Vos questions

Merci de votre attention. Je suis à votre disposition pour vos questions. Le site et le code restent en ligne si vous voulez les explorer.
