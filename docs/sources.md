# Sources du projet

Toutes les sources extérieures citées dans le projet, rassemblées en un seul endroit. Pour chacune : ce qu'elle appuie et où elle est utilisée (pages du site Streamlit, documents du dépôt ; l'accueil et le README reprennent les faits sans lien vers chaque source).

Les faits sur la crise de 2005 s'appuient de préférence sur des sources de l'époque (2004 à 2008). Les sources plus récentes sont signalées comme telles.

---

## 1. Les données et l'étude de référence

| Source | Ce qu'elle appuie | Utilisée dans |
|---|---|---|
| I-Cheng Yeh et Che-hui Lien (2009), « The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients », *Expert Systems with Applications*, vol. 36, n° 2, p. 2473-2480, [doi:10.1016/j.eswa.2007.12.020](https://doi.org/10.1016/j.eswa.2007.12.020) ([PDF](DefaultCreditCardClients_yeh_2009.pdf), [traduction](traduction_DefaultCreditCardClients_yeh_2009.md)) | L'étude d'origine du dataset : ses modèles, son AUC de 0,77 (le défi du projet) ; menée en 2006-2007 (article enregistré fin 2007), publiée en 2009 | accueil, 8.2, README, `contexte.md`, `hypotheses_et_conclusions.md` |
| [UCI Machine Learning Repository, « Default of Credit Card Clients »](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) | Le dataset publié (30 000 clients) et son dictionnaire | `contexte.md`, `dataset_dictionary.md` |
| [Kaggle, « Default of Credit Card Clients »](https://www.kaggle.com/datasets/mariosfish/default-of-credit-card-clients/data) | La copie du dataset à télécharger pour reproduire le projet | README (installation) |

## 2. Le contexte de la crise des cartes de crédit (Taïwan, 2005)

### Sources de l'époque

| Source | Ce qu'elle appuie | Utilisée dans |
|---|---|---|
| [Banque centrale de Taïwan, rapport annuel 2005](https://www.cbc.gov.tw/public/data/publications/year2005/05ar_i-1.pdf) | Une économie saine en 2005 : chômage 4,13 %, inflation 2,30 %, croissance 4,09 % | accueil, `contexte.md` |
| [Banque centrale de Taïwan, rapport annuel 2005, politique monétaire](https://www.cbc.gov.tw/public/data/publications/year2005/05ar_iii-2.pdf) | Pas de choc monétaire : taux d'escompte relevé par petites hausses, 2,125 % en septembre 2005 | `contexte.md` |
| [Taipei Times, 14 juillet 2004](https://www.taipeitimes.com/News/biz/archives/2004/07/14/2003178964) | Le plafond légal des taux à 20 % | accueil, `contexte.md` |
| [Taipei Times, « Consumer credit crisis threatens », 26 octobre 2005](https://www.taipeitimes.com/News/editorials/archives/2005/10/26/2003277465) | Taux de 17 à 20 % par an, 800 milliards de NT$ de dettes de cartes, 600 000 NT$ de dette moyenne | accueil, 4.3, `contexte.md` |
| [Taipei Times, « Credit-card segment under pressure », 30 décembre 2005](https://www.taipeitimes.com/News/biz/archives/2005/12/30/2003286657) | Décembre 2005 : mécanisme d'aide aux débiteurs et hausse des mensualités minimales, après les six mois du dataset | 5.3, `contexte.md` |
| [Taipei Times, « The dark side of outsourcing debt », 8 mars 2006](https://www.taipeitimes.com/News/editorials/archives/2006/03/08/2003296330) | Février 2006 : accord des banques sous l'égide de la FSC sur la négociation des dettes | 5.3, `contexte.md` |
| [Taipei Times, « No card slaves, just credit abusers », 11 mars 2006](https://www.taipeitimes.com/News/editorials/archives/2006/03/11/2003296845) | Les « esclaves de la carte », qui ne payaient plus que le minimum | accueil, `contexte.md` |
| [Electronic Payments International, « Taiwan's credit crisis: the calm after the storm »](https://www.electronicpaymentsinternational.com/country-surveys/taiwans-credit-crisis-the-calm-after-the-storm/) (20 février 2007) | 133 cartes pour 100 Taïwanais de plus de 15 ans en septembre 2005 | accueil, `contexte.md` |
| [Tsai C.-W. (2007), « Dispute Resolution Mechanisms in the Resolution of 2006 Taiwan Card-debt Problems », Université nationale de Taïwan](https://scholars.lib.ntu.edu.tw/entities/publication/4417ce50-afcf-4c34-b1e5-a164858b09f0) | Créances douteuses en forte hausse au second semestre 2005 ; provisions des banques de 71 à 162,9 milliards de NT$ ; mécanisme de négociation de 2006 | accueil (frise), `contexte.md` |
| [FSC (Banking Bureau), notice du 7 janvier 2008 sur la règle DBR22](https://law.banking.gov.tw/chi/NewsContent.aspx?msgid=1018) | Le plafond d'endettement à 22 fois le revenu mensuel, en vigueur au plus tard en septembre 2006 | accueil (frise), `contexte.md` |

### Sources postérieures

| Source | Ce qu'elle appuie | Utilisée dans |
|---|---|---|
| [Seven Pillars Institute, « The Taiwan Credit Card Crisis »](https://sevenpillarsinstitute.org/case-studies/taiwans-credit-card-crisis/) (5 octobre 2011) | Nouvelles banques autorisées à partir de 1990 ; critères d'octroi abaissés ; mesures de la FSC en 2005 (conditions d'octroi, publicité, recouvrement, intérêts composés) | accueil, `contexte.md` |
| [CTBC Bank, FAQ sur le paiement en supérette](https://service.ctbcbank.com/FAQ/Page01?kmid=4666) (pratique actuelle, citée à titre indicatif) | Le délai d'enregistrement d'un paiement en supérette | `contexte.md` |

## 3. Les montants de 2005, pour les lire en euros et en salaires

| Source | Ce qu'elle appuie | Utilisée dans |
|---|---|---|
| [Banque centrale européenne, taux de change annuel moyen EUR/TWD](https://data.ecb.europa.eu/data/datasets/EXR/EXR.A.TWD.EUR.SP00.A) | 1 € valait en moyenne 40,00 NT$ en 2005 | 3.4 |
| [Ministère du Travail de Taïwan, tableau des salaires moyens](https://statdb.mol.gov.tw/html/trend/104/51410.pdf) (d'après l'enquête sur les salaires de la DGBAS) | Salaire mensuel moyen de l'industrie et des services : 43 159 NT$ en 2005 | 3.4 |

## 4. Le cadre juridique (droit français et européen en vigueur)

| Source | Ce qu'elle appuie | Utilisée dans |
|---|---|---|
| [Code pénal, article 225-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000045391831) | Les critères de discrimination, dont le sexe, la situation de famille et l'âge | 6.6 |
| [RGPD, articles 9 et 22 (présentation de la CNIL)](https://www.cnil.fr/fr/reglement-europeen-protection-donnees) | Les données sensibles ; le droit de ne pas faire l'objet d'une décision entièrement automatisée | 6.6 |
| [Règlement européen sur l'intelligence artificielle (AI Act), règlement (UE) 2024/1689, annexe III](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:32024R1689) | L'évaluation de la solvabilité des personnes, classée parmi les systèmes à haut risque | 6.6 |

## 5. La méthode

| Source | Ce qu'elle appuie | Utilisée dans |
|---|---|---|
| Claude Nadeau et Yoshua Bengio (2003), « Inference for the Generalization Error », *Machine Learning*, vol. 52, n° 3, p. 239-281, [doi:10.1023/A:1024068626366](https://doi.org/10.1023/A:1024068626366) | Le test t corrigé, pour comparer deux modèles en validation croisée répétée (duel fin des scénarios) | 6.3, `hypotheses_et_conclusions.md` |

---

*Liens vérifiés le 09/10/2026.*
