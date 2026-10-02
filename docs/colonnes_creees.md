# Colonnes créées : définitions et modes de calcul

Fichier de référence pour toutes les colonnes ajoutées au dataset d'origine. **Une colonne a une seule définition** : si elle est recalculée dans plusieurs fichiers, le calcul doit être identique à celui décrit ici. Toute nouvelle colonne est à ajouter dans ce fichier.

Rappel de la convention temporelle : mois 1 = M-1 (septembre 2005), 6 = M-6 (avril 2005). `PAY_n`, `PAY_AMTn` et `BILL_AMT(n+1)` vont ensemble : le paiement du mois n rembourse la facture `BILL_AMT(n+1)`, exigible au mois n.

---

## 1. Ratios

| Colonne | Définition et calcul | Créée dans | Utilisée par |
|---|---|---|---|
| `ratio_PAY_BILLn` (n = 1 à 5) | Ratio de paiement du mois n, en % : `PAY_AMTn / BILL_AMT(n+1) × 100`, écrêté entre 0 et 200. **100** si aucune facture n'était exigible (`BILL_AMT(n+1) <= 0`) : rien à payer, le client est considéré à jour. **0** si une facture était exigible et que rien n'a été payé | `src/02_01_nettoyage.ipynb` (enregistrée dans `cleaned3` et `cleaned4`) | EDA lab, storytelling, CSV Streamlit, ML (`S12_5` et suivants) |
| `ratio_PAY_BILL_global` | Part de tout le dû de la période réellement payée, en % : `(PAY_AMT1 + … + PAY_AMT5) / (BILL_AMT2 + PAY_AMT2 + … + PAY_AMT5) × 100`, écrêté entre 0 et 200. Le dénominateur est le **dû sans doublon** : une facture impayée, reportée dans la facture suivante, n'est comptée qu'une fois (facture du mois = facture précédente − paiement + nouvelles sommes dues ; la somme se simplifie en `BILL_AMT2 + PAY_AMT2..5`). Vide si ce dû est nul ou négatif. La facture de septembre (`BILL_AMT1`), payée en octobre, n'entre pas dans le calcul | Recalculée dans `05_01_EDA_lab` et `05_03_EDA_storytelling` (définie le 02/10/2026) | Départage de `ratio_PAY_BILL_median`, mesure du comportement de remboursement |
| `ratio_PAY_BILL_median` | Médiane par client de `ratio_PAY_BILL1` à `ratio_PAY_BILL5` sur les **seuls mois avec une facture due** (`BILL_AMT(n+1) > 0`). Nombre pair de mois avec deux valeurs du milieu différentes : on garde celle qui est la plus proche de `ratio_PAY_BILL_global` (la médiane reste une valeur observée, rattachée au comportement réel du client) ; égalité parfaite : médiane classique. **-1** si aucune facture n'était due d'avril à août mais qu'il y a une facture en septembre (`BILL_AMT1 > 0`) : compte qui commence à servir, sans paiement encore observable. **Vide** si aucune facture positive sur les 6 mois (ces clients sont hors du ML, déjà exclus par S12). Les graphiques n'affichent que les valeurs de 0 et plus | Recalculée dans `05_01_EDA_lab`, `05_03_EDA_storytelling` et la page Streamlit 4.3 (définie le 02/10/2026) | Types d'usage de la carte (paiement comptant, crédit), feature ML |
| `ratio_PAY_BILL_regularite` | Régularité du comportement de paiement, en % : part des mois avec une facture due (`BILL_AMT(n+1) > 0`) où `ratio_PAY_BILLn` tombe dans le **même type d'usage** que `ratio_PAY_BILL_median`. Types d'usage (tranches posées sur la répartition de tous les ratios mensuels, pas sur `dpnm`) : 0 % exactement (ne paie rien), moins de 3 % (client en difficulté, moins qu'une mensualité), 3 à moins de 6 % (crédit par mensualité), 6 à moins de 30 % (usage mixte), 30 à moins de 90 % (remboursement élevé), 90 % et plus (paiement comptant). **-1** quand `ratio_PAY_BILL_median` vaut -1, **vide** quand elle est vide. Peu informative quand moins de 3 mois sont dus (avec 1 ou 2 mois, la médiane se confond avec ces mois) ; vaut au moins 50 % par construction quand la médiane vaut 0 % ou 90 % et plus | `05_03_EDA_storytelling` (avant l'export du CSV Streamlit, définie le 02/10/2026) | Page Streamlit 4.3, feature ML |
| `ratio_PAY_to_BILL_median` | *Ancienne définition, remplacée par `ratio_PAY_BILL_median`* : médiane des 5 ratios, mois sans facture comptés à 100 % (tire les comptes récents vers le paiement comptant et crée une pointe à 50 %). Conservée seulement pour relire les modèles déjà entraînés | Notebooks ML `S12_5` à `S12_7` | Modèles `S12_5` à `S12_7` |
| `ratio_BILL_LIMITn` (n = 1 à 6) | Utilisation du plafond au mois n, en % : `BILL_AMTn / LIMIT_BAL × 100`, écrêté entre 0 (un encours négatif ne donne pas de ratio négatif) et 200 | Recalculée dans `05_01_EDA_lab`, `05_03_EDA_storytelling` (enregistrée dans le CSV Streamlit) et les notebooks ML `S12_1` et suivants | EDA, Streamlit, feature ML |
| `ratio_brut_PAY_BILLn` (n = 1 à 5) | Ratio brut `PAY_AMTn / BILL_AMT(n+1) × 100`, sans écrêtage, vide si `BILL_AMT(n+1) <= 0` | `05_01_EDA_lab` uniquement | Étude des valeurs aberrantes seulement (ne pas réutiliser ailleurs) |

**Règle d'affichage des ratios de paiement** (EDA lab, storytelling, Streamlit) : dans les graphiques et les statistiques affichées, un ratio n'est montré que si une facture était exigible (`BILL_AMT(n+1) > 0`), grâce à la fonction `ratios_affichables`. Le 100 % des clients sans facture reste dans la colonne (pour le ML), mais il n'est pas affiché : sinon, la baisse du nombre de comptes dormants au fil des mois déformerait les courbes d'évolution.

**Règles du contentieux** : `05_02_EDA_contentieux` n'utilise pas `ratio_PAY_BILLn`. Il calcule ses propres ratios de M-1 (`PAY_AMT1 / BILL_AMT2`) et de M-2 (`PAY_AMT2 / BILL_AMT3`), avec **0** si aucune facture n'était exigible : une facture absente n'est pas une preuve de paiement.

---

## 2. Population contentieuse (définition 2 révisée le 27/09/2026)

Calculées par `statut_ctx_regle2` dans `src/05_02_EDA_contentieux.ipynb` (section 6), à partir de `corriger_faux_codage` (section 3) et `recodage_pay1` (section 6.1, recodage du mois de transition révisé le 30/09/2026). Ces fonctions sont recopiées telles quelles dans le storytelling, et le seront dans les notebooks ML.

Colonnes listées dans l'ordre logique de calcul : chaque étape travaille sur les codes produits par la précédente. Les comptages de codes >= 2 se font toujours en dernier, sur les codes définitifs, pour ne pas compter un 2 qui serait corrigé ensuite.

| Étape | Colonne | Définition |
|---|---|---|
| 1. Correction des faux 2 (`corriger_faux_codage`) | `FAUX_CODAGE` | 1 si faux 2 neutralisé chez un client qui venait de payer ou avait un encours |
| 1. Correction des faux 2 (`corriger_faux_codage`) | `SURVEILLANCE_RECENTE` | 1 si faux 2 sur compte endormi (code 2 posé sur une facture nulle, sans paiement ni encours avant) : ces codes ne comptent pas pour le CTX |
| 2. Recodage du mois de transition (`recodage_pay1`, sur les codes corrigés) | `PAY_1_recode` | PAY_1 après correction des faux 2 et recodage du mois de transition (PAY_2 >= 2 puis PAY_1 <= 1) : 2 si aucun paiement en M-1 ni en M-2 alors que deux factures étaient exigibles ; si la facture de M-1 est payée à 90 % ou plus, code d'avant le retard (premier code < 2 avant la série, -2 remplacé par -1, 0 si la série remonte à M-6) ; inchangé sinon |
| 3. Statuts (codes corrigés, `PAY_1_recode` en M-1) | `STATUT_CTX` | Statut à M : `CTX` (retiré du ML, prédit en défaut), `Retard considéré régularisé M-1`, `Sorti`, `Retard régularisé`, `Jamais CTX` |
| 3. Statuts | `SOUS_STATUT_CTX` | Détail : `CTX 6 mois`, `CTX 2 à 5 mois`, `CTX entrée en M-1`, `Retard considéré régularisé M-1 (série)` ou `(isolé)` ; sinon identique au statut |
| 3. Statuts | `FLAG_CTX` | Marqueur intemporel : 1 si deux codes >= 2 consécutifs sur les 6 mois (codes posés sur une facture nulle exclus), 2 isolé en M-6 ou en M-1 compté par défaut, sauf retard payé isolé à M-1 ; 1 aussi pour un retard payé qui termine une série |
| 3. Statuts | `MOIS_SORTIE_CTX` | Mois de la dernière sortie du CTX (1 à 5) ; **0** = sortie présumée en M (retard payé qui termine une série) ; -1 = pas de sortie (encore au CTX, ou jamais passé par le CTX) |
| 3. Statuts | `FLAG_RETARD` | 1 si retard isolé (un seul mois >= 2) régularisé sur la période, ou retard payé isolé à M-1 |
| 3. Statuts | `MOIS_SORTIE_RETARD` | Mois du retour sous 2 après le dernier retard isolé (1 à 4) ; **0** = retard payé isolé à M-1 ; -1 = aucune régularisation ; vide pour les clients au CTX |
| 4. Comptages, en dernier (codes définitifs de l'étape 3 : faux codages et comptes endormis neutralisés, `PAY_1_recode` en M-1) | `NB_MOIS_CTX` | *Définie, pas encore calculée.* Durée du dernier passage au CTX, au sens de `FLAG_CTX` : nombre de mois **consécutifs** à >= 2 de la dernière série qui compte comme passage au CTX (jusqu'à la sortie, ou jusqu'à M-1 pour un client encore au CTX). **0 si `FLAG_CTX` = 0** : un retard isolé régularisé (`FLAG_RETARD`) ou un retard payé isolé ne compte pas. 1 pour un 2 isolé en M-6 ou en M-1 compté au CTX par défaut. Non cumulée : un client avec deux passages séparés n'est compté que sur le dernier |
| 4. Comptages | `CUMUL_INCIDENT` | *Définie, pas encore calculée.* Nombre total de mois avec un code >= 2 sur les 6 mois (M-1 à M-6), consécutifs ou non. Mesure la fréquence des incidents, quand `NB_MOIS_CTX` mesure la durée du dernier passage |

**Retrait du dataset ML** : `FLAG_CTX = 1` et `MOIS_SORTIE_CTX = -1` (clients au CTX à M).
**Retard payé** : PAY_1 >= 2 mais facture payée à 90 % ou plus en M-1 ou en M-2 (ratios du contentieux ci-dessus).

---

## 3. Autres features ML

| Colonne | Définition | Créée dans |
|---|---|---|
| `PAY_habituel` | Codification de paiement habituelle du client : valeur la plus fréquente de `PAY_1` à `PAY_6`, **sur les 6 mois, qu'une facture soit due ou non** (l'ancienneté du compte ou l'absence de facture sont portées par d'autres colonnes), les codifications de retard (2 et plus) regroupées en **2**. En cas d'égalité, la plus récente des codifications à égalité (dernière situation connue par la banque). Jamais vide | `05_03_EDA_storytelling` (avant l'export du CSV Streamlit, définie le 02/10/2026) | Page Streamlit 4.3, feature ML |
| `AGE_BUCKET` | Tranches d'âge : `pd.cut(AGE, bins=[20, 25, 30, 35, 40, 50, 80])`, libellés 21-25, 26-30, 31-35, 36-40, 41-50, 51+ | `05_03_EDA_storytelling`, ML `S12_2` (scénario écarté) |
| `ACTIVATION_MONTH` | Mois de première activité après une inactivité totale sur tous les mois antérieurs (inactif = `BILL_AMT <= 0` et `PAY_AMT = 0`) : 1 à 4 = actif depuis M-1 à M-4 ; **7** = compte déjà actif avant (historique ancien) | ML `S12_6` et suivants |
| `CTX` | *Ancienne règle, abandonnée* : PAY_n = 2 sur les 6 mois, ou PAY_n = 2 avec PAY_(n+1) > 2, facture exigible `BILL_AMT(n+1)` > 0 et `PAY_AMTn` = 0. Remplacée par les colonnes de la section 2 | ML `S12_7` |

---

## 4. Colonnes intermédiaires d'analyse (non exportées)

Colonnes créées pour un graphique ou un tableau, qui ne sortent pas du notebook : `ratio_mean_client`, `ratio_max_client`, `mean_ratio`, `ratio_mean_bin`, `ratio_m1_bin`, `LIMIT_BAL_interval`, `LIMIT_BAL_bin`, `CTX_Trajectoire`, `bins`. Elles ne doivent pas être réutilisées comme features sans être d'abord définies ici.
