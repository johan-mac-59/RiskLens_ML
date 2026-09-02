



## Explicationss sur la crise des cartes de crédit de Taïwan

La crise taïwanaise de 2005 présente une particularité majeure : elle n'a pas été provoquée par une dégradation des indicateurs macroéconomiques classiques. Les chiffres fondamentaux du pays étaient au vert.
Les indicateurs macroéconomiques en 2005 (stables)
Chômage : Stable et bas, oscillant autour de 4 %.
Inflation : Modérée et maîtrisée (entre 1 % et 2 %).
Croissance du PIB : Solide (environ 4 à 5 % par an).
Les vrais facteurs de la crise (structurels et microéconomiques)
Dérégulation et guerre d'octroi : Les banques ont distribué massivement des cartes de crédit et des cartes de retrait de cash (cash cards) sans contrôle de solvabilité, ciblant même les étudiants et les faibles revenus.
Effet boule de neige des taux d'intérêt : Les taux du crédit renouvelable (revolving) atteignaient le plafond légal de 20 %. Dès que le capital emprunté augmentait, les intérêts dépassaient la capacité de remboursement des ménages.
Cavalerie bancaire (Card Monsters) : Les clients utilisaient la fonction de retrait d'une nouvelle carte pour payer les mensualités d'une ancienne carte. Un même individu pouvait accumuler plus de dix cartes dans des établissements différents.
Rupture par resserrement réglementaire : En 2005, la Financial Supervisory Commission (FSC) a imposé un ratio maximal d'endettement non garanti (plafonné à 22 fois le salaire mensuel). Cette mesure a brutalement bloqué la cavalerie des emprunteurs, déclenchant la vague d'impayés observée entre avril et octobre 2005.
Même si le cadre prudentiel des banques traditionnelles s'est renforcé, la mécanique de la crise taïwanaise — accumulation de dettes non garanties masquées, concurrence d'octroi et rupture brutale d'accès au crédit — se reproduit régulièrement sous de nouvelles formes.

**Origine de la crise**
Les taux d'intérêt de la Banque centrale n'ont pas bondi. Il n'y a eu aucun choc monétaire macroéconomique : le taux directeur taïwanais est resté bas et très stable (autour de 2 % en 2005).
Le problème est venu du coût effectif du crédit revolving et de son mode de calcul :
Le taux plafond déjà au maximum (20 %) : Les banques appliquaient déjà quasi systématiquement le taux usuraire maximal autorisé par la loi (près de 20 % par an) sur les soldes de cartes de crédit et de retrait d'espèces (cash cards).
L'effet de capitalisation des intérêts : Les taux n'ont pas augmenté, mais la masse d'intérêts composés a explosé. Les mensualités minimales exigées par les banques étaient si faibles qu'elles ne couvraient souvent que les agios, sans amortir le capital.
Le blocage du refinancement : Tant que les clients pouvaient ouvrir de nouvelles cartes, ils remboursaient les intérêts à 20 % d'une banque avec le cash tiré d'une autre. Dès que la FSC a plafonné l'endettement (limite fixée à 22 fois le salaire mensuel), cette cavalerie s'est arrêtée net.
C'est donc le cumul d'intérêts déjà très élevés (20 %) associé à la fermeture du robinet du crédit qui a provoqué la vague de défauts, et non une hausse des taux du marché


## Fonctionnement des cartes de crédits à Taïwan en 2005
En 2005 à Taïwan, le règlement des factures de cartes de crédit et de cash cards reposait majoritairement sur du liquide et des canaux physiques décentralisés :
- Les Convenience Stores (7-Eleven, FamilyMart, Hi-Life) : C'était le canal prédominant. Les clients recevaient leur relevé mensuel papier muni d'un code-barres, se rendaient en supérette ouverte 24/7 et régulaient leur facture en espèces directement au comptoir.
- Les guichets automatiques (ATM) : Grâce à un réseau d'interbancarité très développé, les clients régulaient leurs cartes via virement interbancaire à l'ATM ou par dépôt d'espèces dans les bornes.
- Le guichet bancaire et la Poste (Chunghwa Post) : Paiement traditionnel en agence, en espèces ou par chèque.
- Le prélèvement automatique : Moins plébiscité pour le crédit renouvelable, car la plupart des Card Monsters cumulaient des cartes dans des banques où ils ne possédaient aucun compte courant.

**Le lien direct avec les artefacts du dataset**
Ce mode de paiement physique et morcelé éclaire directement les anomalies observées dans le SI :
- Décalage de compensation (Clearing Lag) : Un règlement effectué le dernier jour du mois dans un 7-Eleven mettait 48 à 72 heures ouvrées à être télétransmis et comptabilisé par la banque émettrice. Lors du tirage de la photo comptable, le client avait payé, mais le système enregistrait un retard technique temporaire (probable PAY_1 = 1).
- Logistique de la cavalerie : Pour maintenir leur crédit, les emprunteurs retiraient des billets aux ATM via la cash card d'une première banque, puis marchaient jusqu'à la supérette la plus proche pour déposer ces espèces au comptoir de la seconde banque.
- Traitements par lots (Batch processing) : Le flux d'informations provenant des réseaux de supérettes et des banques tierces était réconcilié en fin de mois par des traitements batch, créant ce décalage d'un mois entre la table de gestion à chaud (PAY_1) et les historiques apurés (PAY_2 à PAY_6).


## Recherche de Yeh & Lien

Le choix de ce jeu de données et la réalisation de l'étude par I-Cheng Yeh et Che-hui Lien reposent sur un contexte macroéconomique et bancaire très précis :

1. La crise des cartes de crédit à Taïwan (2005–2006)
En 2005, Taïwan a été frappée par une crise majeure du crédit à la consommation (surnommée la crise du « Card Monster »). Entre 2000 et 2005, les banques taïwanaises se sont livrées une concurrence féroce en distribuant massivement des cartes de crédit et des crédits renouvelables (revolving) avec des critères d'octroi très laxistes. Résultat : une explosion des défauts de paiement et du surendettement à l'échelle nationale à partir de mi-2005.

2. La volonté de la banque et l'objectif de l'étude
C'est dans ce climat de crise qu'une grande banque taïwanaise a fourni un échantillon anonymisé de 30 000 clients à l'équipe de recherche. L'objectif était double :
Urgence opérationnelle : La banque cherchait à moderniser ses outils d'octroi et de recouvrement pour endiguer la hausse des pertes d'exploitation.
Problématique scientifique : Les chercheurs voulaient démontrer qu'en période de crise, les techniques de Data Mining (réseaux de neurones, arbres de décision, K-NN) surpassaient les modèles statistiques traditionnels comme la régression logistique pour prédire le défaut du mois suivant (octobre 2005).

Ce que mesure réellement dpnm  
Dans le protocole de Yeh & Lien, $dpnm = 1$ indique uniquement un manquement sur l'échéance d'octobre 2005. Il s'agit d'un premier niveau d'impayé (30 jours). Un client étiqueté $dpnm = 1$ en octobre pouvait très bien régulariser sa situation en novembre.


## Dans quels cas cette crise pourrait survenir à nouveau ?

1. Les nouveaux vecteurs de risque
L'essor du BNPL (Buy Now, Pay Later) : Le paiement fractionné accordé en quelques clics sans vérification approfondie de solvabilité crée le même risque d'empilement de dettes. Un utilisateur peut cumuler des échéances sur Klarna, Paypal ou Alma sans qu'aucun organisme n'ait une vision globale de son encours.
Le crédit mobile dans les pays émergents : Dans plusieurs économies en développement (Asie du Sud-Est, Afrique de l'Est, Amérique latine), la numérisation du crédit via des applications mobiles a provoqué des vagues d'endettement rapide chez des populations peu accoutumées au produit, rappelant le marché taïwanais de 2005.
L'absence de Credit Bureau centralisé : Dans les pays qui ne disposent pas d'un fichier central des crédits aux particuliers (ou dont les données ne sont pas consolidées en temps réel), la cavalerie bancaire reste techniquement possible.

2. Les conditions nécessaires à son apparition
Pour qu'une crise similaire éclate, il faut la réunion de deux facteurs :
Un angle mort réglementaire : Une innovation financière (crédit revolving en 2005, fintech/BNPL aujourd'hui) qui échappe temporairement à la supervision globale de l'exposition par individu.
Un choc de fermeture du robinet : Un resserrement soudain de la distribution de crédit (intervention du régulateur, remontée des taux ou resserrement des liquidités par les investisseurs) qui empêche les emprunteurs de refinancer leurs dettes à court terme.

C'est d'ailleurs pour éviter ce scénario que certaines autorités réglementaires de plusieurs pays encadrent désormais très strictement le crédit à la consommation et les solutions de paiement fractionné.