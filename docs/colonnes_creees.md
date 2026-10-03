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

## 2. Corrections issues du contentieux et population contentieuse (niveau 5, `cleaned5`)

Le niveau 5 du nettoyage (`src/02_01_nettoyage.ipynb`) applique les corrections de codification issues de l'étude du contentieux (`05_02_EDA_contentieux`, définition 2) et ajoute les colonnes ci-dessous. **Aucun client n'est retiré.** Les fonctions (`corriger_faux_codage`, `recodage_pay1`, calcul des indicateurs) vivent dans `02_01_nettoyage`, leur source unique ; les autres notebooks lisent `cleaned5`.

**Corrections écrites directement dans les `PAY_n`** (les codifications d'origine restent dans `cleaned4`) :
1. **Faux retards neutralisés** : une série de codifications de retard (2 et plus) posée alors qu'aucune facture n'était due est remplacée par la codification saine qui la précède, que le client vienne de payer (faux codage) ou que son compte soit endormi (surveillance).
2. **Mois de transition recodé** (`PAY_1`) : chez un client en retard en août (`PAY_2 >= 2`) qui paraît sortir du retard en septembre (`PAY_1 <= 1`), `PAY_1` passe à **2** s'il n'a rien payé en août ni en septembre alors que deux factures étaient dues ; il reprend sa **codification d'avant le retard** (-2 remplacé par -1, 0 si le retard remonte à avril) s'il a payé au moins 90 % de sa facture de septembre ; il reste inchangé sinon.

Colonnes listées dans l'ordre de calcul ; les comptages se font en dernier, sur les `PAY_n` corrigés. Les colonnes de mois valent **-1 par défaut** : c'est la détection d'une sortie ou d'une régularisation qui modifie cette valeur ; aucune colonne du niveau 5 n'est vide. **L'indicateur se lit toujours en premier** : si `FLAG_CTX` (ou `FLAG_RETARD`) vaut 0, la valeur de `MOIS_SORTIE_CTX` (ou `MOIS_SORTIE_RETARD`) n'a aucune importance.

| Étape | Colonne | En clair |
|---|---|---|
| 1. Traces des corrections | `FAUX_CODAGE` | 1 si le client avait un faux retard, posé sur une facture nulle alors qu'il venait de payer ou avait un encours ; ce retard a été neutralisé dans les `PAY_n`. Peu utile pour l'analyse, la colonne est conservée par sécurité, comme feature à tester en ML |
| 1. Traces des corrections | `SURVEILLANCE_RECENTE` | 1 si le client avait un retard posé sur une facture nulle d'un compte endormi (ni paiement ni encours avant) : plutôt une mise sous surveillance qu'une dette ; ce retard a été neutralisé dans les `PAY_n` |
| 2. Contentieux | `FLAG_CTX` | 1 si le client est passé par le contentieux pendant la période : au moins deux mois de retard (2 et plus) d'affilée ; un retard isolé en avril ou en septembre compte aussi, sauf s'il est payé (voir `FLAG_RETARD`) |
| 2. Contentieux | `MOIS_SORTIE_CTX` | Pour un client passé par le contentieux : mois de sa dernière sortie, de **1** (septembre) à **5** (mai) ; **0** si sa sortie est présumée en octobre (retard payé à au moins 90 % qui termine une série) ; **-1** par défaut : pas de sortie détectée, qu'il soit encore au contentieux ou qu'il n'y soit jamais passé (à lire avec `FLAG_CTX` ; jamais vide) |
| 2. Contentieux | `FLAG_RETARD` | 1 si le client a eu un retard isolé (un seul mois à 2 ou plus) régularisé ensuite, ou un retard isolé en septembre payé à au moins 90 % |
| 2. Contentieux | `MOIS_SORTIE_RETARD` | Pour un retard isolé régularisé : mois du retour à la normale, de **1** à **4** ; **0** pour un retard isolé de septembre payé à au moins 90 % (régularisation présumée en octobre) ; **-1** par défaut : aucune régularisation détectée, y compris pour un client au contentieux à M (jamais vide) |
| 3. Comptage (en dernier) | `NB_MOIS_CTX` | Durée du dernier passage au contentieux : nombre de mois de retard (2 et plus) **consécutifs** de la dernière série qui compte comme passage au contentieux ; 0 si `FLAG_CTX = 0` ; un client avec deux passages séparés n'est compté que sur le dernier |

**Lire la situation d'un client avec les indicateurs** (aucune colonne de statut n'est nécessaire) :

| Situation du client | Indicateurs |
|---|---|
| **Au contentieux à M** (retiré du dataset ML en partie 6, prédit en défaut par la règle) | `FLAG_CTX = 1` et `MOIS_SORTIE_CTX = -1` |
| Sorti du contentieux pendant la période | `FLAG_CTX = 1` et `MOIS_SORTIE_CTX` de 1 à 5 |
| Retard payé qui termine une série (sortie présumée en octobre) | `FLAG_CTX = 1` et `MOIS_SORTIE_CTX = 0` |
| Retard isolé régularisé | `FLAG_RETARD = 1` et `MOIS_SORTIE_RETARD` de 1 à 4 |
| Retard isolé de septembre payé (régularisation présumée en octobre) | `FLAG_RETARD = 1` et `MOIS_SORTIE_RETARD = 0` |
| **Client sain** : jamais au contentieux, aucun retard sur la période | `FLAG_CTX = 0` et `FLAG_RETARD = 0` |

La durée d'un passage au contentieux (6 mois, 2 à 5 mois, entrée en septembre) se lit avec `NB_MOIS_CTX`.

**Retard payé** : retard en septembre (`PAY_1 >= 2`) mais facture payée à au moins 90 % en août ou en septembre. Dans ces règles, un ratio de paiement sans facture due vaut 0 : une facture absente n'est pas une preuve de paiement.

*Colonnes abandonnées (02/10/2026), citées dans d'anciens notebooks* : `PAY_1_recode` (la correction est écrite directement dans `PAY_1`), `STATUT_CTX` et `SOUS_STATUT_CTX` (redondantes : les statuts se lisent avec `FLAG_CTX`, `MOIS_SORTIE_CTX`, `FLAG_RETARD`, `MOIS_SORTIE_RETARD` et `NB_MOIS_CTX`).

---

## 3. Autres features ML

| Colonne | Définition | Créée dans |
|---|---|---|
| `PAY_habituel` | Codification de paiement habituelle du client : valeur la plus fréquente de `PAY_1` à `PAY_6`, **sur les 6 mois, qu'une facture soit due ou non** (l'ancienneté du compte ou l'absence de facture sont portées par d'autres colonnes), les codifications de retard (2 et plus) regroupées en **2**. En cas d'égalité, la plus récente des codifications à égalité (dernière situation connue par la banque). Jamais vide | `05_03_EDA_storytelling` (avant l'export du CSV Streamlit, définie le 02/10/2026) | Page Streamlit 4.3, feature ML |
| `CUMUL_INCIDENT` | Nombre total de mois en retard (codification 2 et plus) de `PAY_1` à `PAY_6`, consécutifs ou non ; de 0 à 6, jamais vide. Simple colonne de comptage, sans aucune règle du contentieux : elle se calcule sur les `PAY_n` du dataset lu et suit donc son niveau de nettoyage (aujourd'hui `cleaned5`, le niveau retenu comme le plus pertinent) : la fréquence des retards, quand `NB_MOIS_CTX` mesure la durée du dernier passage au contentieux | `05_03_EDA_storytelling` (avant l'export, déplacée du niveau 5 le 03/10/2026) | Page Streamlit 4.6, feature ML |
| `FLAG_OUVERTURE` | 1 si le compte s'ouvre pendant la période : `BILL_AMT6 = 0` et `PAY_AMT6 = 0` en avril (sans dette ni avoir, donc rien en mars non plus), puis une activité de mai à septembre (mouvement de l'encours `BILL_AMTn ≠ BILL_AMT(n+1)` ou paiement `PAY_AMTn > 0`) ; 0 sinon, et d'office si `BILL_AMT6 ≠ 0` | `05_03_EDA_storytelling` (avant l'export, définie le 02/10/2026) | Page Streamlit 4.4, feature ML |
| `FLAG_DEGEL` | 1 si un compte dormant créditeur se réveille : `BILL_AMT6 < 0` et `PAY_AMT6 = 0` en avril, puis une activité de mai à septembre (même critère) ; 0 sinon. Ne peut pas valoir 1 en même temps que `FLAG_OUVERTURE` | `05_03_EDA_storytelling` (avant l'export, définie le 02/10/2026) | Page Streamlit 4.4, feature ML |
| `MOIS_ACTIVATION` | n (1 à 5) : mois M-n de la première activité quand `FLAG_OUVERTURE` ou `FLAG_DEGEL` vaut 1 ; **0** sinon (comptes déjà actifs en avril). Remplace `ACTIVATION_MONTH` | `05_03_EDA_storytelling` (avant l'export, définie le 02/10/2026) | Page Streamlit 4.4, feature ML |
| `AGE_BUCKET` | Tranches d'âge : `pd.cut(AGE, bins=[20, 25, 30, 35, 40, 50, 80])`, libellés 21-25, 26-30, 31-35, 36-40, 41-50, 51+ | `05_03_EDA_storytelling`, ML `S12_2` (scénario écarté) |
| `ACTIVATION_MONTH` | *Plus utilisée, remplacée par `FLAG_OUVERTURE`, `FLAG_DEGEL` et `MOIS_ACTIVATION` (02/10/2026) ; conservée pour relire les modèles `S12_6` et suivants.* Mois de première activité après une inactivité totale sur tous les mois antérieurs (inactif = `BILL_AMT <= 0` et `PAY_AMT = 0`) : 1 à 4 = actif depuis M-1 à M-4 ; **7** = compte déjà actif avant (historique ancien) | ML `S12_6` et suivants |
| `CTX` | *Ancienne règle, abandonnée* : PAY_n = 2 sur les 6 mois, ou PAY_n = 2 avec PAY_(n+1) > 2, facture exigible `BILL_AMT(n+1)` > 0 et `PAY_AMTn` = 0. Remplacée par les colonnes de la section 2 | ML `S12_7` |

---

## 4. Colonnes intermédiaires d'analyse (non exportées)

Colonnes créées pour un graphique ou un tableau, qui ne sortent pas du notebook : `ratio_mean_client`, `ratio_max_client`, `mean_ratio`, `ratio_mean_bin`, `ratio_m1_bin`, `LIMIT_BAL_interval`, `LIMIT_BAL_bin`, `CTX_Trajectoire`, `bins`. Elles ne doivent pas être réutilisées comme features sans être d'abord définies ici.
