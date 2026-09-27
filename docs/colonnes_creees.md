# Colonnes créées : définitions et modes de calcul

Fichier de référence pour toutes les colonnes ajoutées au dataset d'origine. **Une colonne a une seule définition** : si elle est recalculée dans plusieurs fichiers, le calcul doit être identique à celui décrit ici. Toute nouvelle colonne est à ajouter dans ce fichier.

Rappel de la convention temporelle : mois 1 = M-1 (septembre 2005), 6 = M-6 (avril 2005). `PAY_n`, `PAY_AMTn` et `BILL_AMT(n+1)` vont ensemble : le paiement du mois n rembourse la facture `BILL_AMT(n+1)`, exigible au mois n.

---

## 1. Ratios

| Colonne | Définition et calcul | Créée dans | Utilisée par |
|---|---|---|---|
| `ratio_PAY_BILLn` (n = 1 à 5) | Ratio de paiement du mois n, en % : `PAY_AMTn / BILL_AMT(n+1) × 100`, écrêté entre 0 et 200. **100** si aucune facture n'était exigible (`BILL_AMT(n+1) <= 0`) : rien à payer, le client est considéré à jour. **0** si une facture était exigible et que rien n'a été payé | `src/02_01_nettoyage.ipynb` (enregistrée dans `cleaned3`) | EDA lab, storytelling, CSV Streamlit, ML (`S12_5` et suivants) |
| `ratio_PAY_to_BILL_median` | Médiane par client de `ratio_PAY_BILL1` à `ratio_PAY_BILL5` (valeurs à 100 comprises) | Recalculée dans `05_01_EDA_lab`, `05_03_EDA_storytelling` et les notebooks ML `S12_5` à `S12_7` | Types d'usage de la carte (paiement comptant, crédit), feature ML |
| `ratio_BILL_LIMITn` (n = 1 à 6) | Utilisation du plafond au mois n, en % : `BILL_AMTn / LIMIT_BAL × 100`, écrêté entre 0 (un encours négatif ne donne pas de ratio négatif) et 200 | Recalculée dans `05_01_EDA_lab`, `05_03_EDA_storytelling` (enregistrée dans le CSV Streamlit) et les notebooks ML `S12_1` et suivants | EDA, Streamlit, feature ML |
| `ratio_brut_PAY_BILLn` (n = 1 à 5) | Ratio brut `PAY_AMTn / BILL_AMT(n+1) × 100`, sans écrêtage, vide si `BILL_AMT(n+1) <= 0` | `05_01_EDA_lab` uniquement | Étude des valeurs aberrantes seulement (ne pas réutiliser ailleurs) |

**Règle d'affichage des ratios de paiement** (EDA lab, storytelling, Streamlit) : dans les graphiques et les statistiques affichées, un ratio n'est montré que si une facture était exigible (`BILL_AMT(n+1) > 0`), grâce à la fonction `ratios_affichables`. Le 100 % des clients sans facture reste dans la colonne (pour le ML), mais il n'est pas affiché : sinon, la baisse du nombre de comptes dormants au fil des mois déformerait les courbes d'évolution.

**Règles du contentieux** : `05_02_EDA_contentieux` n'utilise pas `ratio_PAY_BILLn`. Il calcule ses propres ratios de M-1 (`PAY_AMT1 / BILL_AMT2`) et de M-2 (`PAY_AMT2 / BILL_AMT3`), avec **0** si aucune facture n'était exigible : une facture absente n'est pas une preuve de paiement.

---

## 2. Population contentieuse (définition 2 révisée le 27/09/2026)

Calculées par `statut_ctx_regle2` dans `src/05_02_EDA_contentieux.ipynb` (section 6), à partir de `corriger_faux_codage` et `recodage_pay1` (section 3). Ces fonctions sont recopiées telles quelles dans le storytelling, et le seront dans les notebooks ML.

| Colonne | Définition |
|---|---|
| `PAY_1_recode` | PAY_1 après correction des faux 2 et recodage du mois de transition (PAY_2 >= 2 puis PAY_1 <= 1) : 2 si aucun paiement en M-1 ni en M-2 alors que deux factures étaient exigibles ; -2 si le ratio de M-1 est >= 90 % ; -1 s'il est >= 10 % ; inchangé sinon |
| `STATUT_CTX` | Statut à M : `CTX` (retiré du ML, prédit en défaut), `Retard considéré régularisé M-1`, `Sorti`, `Retard régularisé`, `Jamais CTX` |
| `SOUS_STATUT_CTX` | Détail : `CTX 6 mois`, `CTX 2 à 5 mois`, `CTX entrée en M-1`, `Retard considéré régularisé M-1 (série)` ou `(isolé)` ; sinon identique au statut |
| `FLAG_CTX` | Marqueur intemporel : 1 si deux codes >= 2 consécutifs sur les 6 mois (codes posés sur une facture nulle exclus), 2 isolé en M-6 ou en M-1 compté par défaut, sauf retard payé isolé à M-1 ; 1 aussi pour un retard payé qui termine une série |
| `MOIS_SORTIE_CTX` | Mois de la dernière sortie du CTX (1 à 5) ; **0** = sortie présumée en M (retard payé qui termine une série) ; -1 = pas de sortie (encore au CTX, ou jamais passé par le CTX) |
| `FLAG_RETARD` | 1 si retard isolé (un seul mois >= 2) régularisé sur la période, ou retard payé isolé à M-1 |
| `MOIS_SORTIE_RETARD` | Mois du retour sous 2 après le dernier retard isolé (1 à 4) ; **0** = retard payé isolé à M-1 ; -1 = aucune régularisation ; vide pour les clients au CTX |
| `SURVEILLANCE_RECENTE` | 1 si faux 2 sur compte endormi (code 2 posé sur une facture nulle, sans paiement ni encours avant) : ces codes ne comptent pas pour le CTX |
| `FAUX_CODAGE` | 1 si faux 2 neutralisé chez un client qui venait de payer ou avait un encours |

**Retrait du dataset ML** : `FLAG_CTX = 1` et `MOIS_SORTIE_CTX = -1` (clients au CTX à M).
**Retard payé** : PAY_1 >= 2 mais facture payée à 90 % ou plus en M-1 ou en M-2 (ratios du contentieux ci-dessus).

---

## 3. Autres features ML

| Colonne | Définition | Créée dans |
|---|---|---|
| `AGE_BUCKET` | Tranches d'âge : `pd.cut(AGE, bins=[20, 25, 30, 35, 40, 50, 80])`, libellés 21-25, 26-30, 31-35, 36-40, 41-50, 51+ | `05_03_EDA_storytelling`, ML `S12_2` (scénario écarté) |
| `ACTIVATION_MONTH` | Mois de première activité après une inactivité totale sur tous les mois antérieurs (inactif = `BILL_AMT <= 0` et `PAY_AMT = 0`) : 1 à 4 = actif depuis M-1 à M-4 ; **7** = compte déjà actif avant (historique ancien) | ML `S12_6` et suivants |
| `CTX` | *Ancienne règle, abandonnée* : PAY_n = 2 sur les 6 mois, ou PAY_n = 2 avec PAY_(n+1) > 2, facture exigible `BILL_AMT(n+1)` > 0 et `PAY_AMTn` = 0. Remplacée par les colonnes de la section 2 | ML `S12_7` |

---

## 4. Colonnes intermédiaires d'analyse (non exportées)

Colonnes créées pour un graphique ou un tableau, qui ne sortent pas du notebook : `ratio_mean_client`, `ratio_max_client`, `mean_ratio`, `ratio_mean_bin`, `ratio_m1_bin`, `LIMIT_BAL_interval`, `LIMIT_BAL_bin`, `CTX_Trajectoire`, `bins`. Elles ne doivent pas être réutilisées comme features sans être d'abord définies ici.
