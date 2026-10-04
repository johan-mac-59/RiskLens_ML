from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 5.1 : LA GENÈSE
# Introduction de la partie 5 : anomalies de l'EDA_lab qui ont lancé l'étude (cellules 131 à 147, données d'origine,
# chiffres repris tels quels : ces données ne sont pas dans le dépôt, décision D19), hypothèse des deux systèmes
# d'information, plafond du ML (première itération, sans chiffres), étude du contentieux et niveau 5, périmètre (clients sans dette en septembre : calcul en direct, descriptif)
# et méthode (périmètre et découpage identiques aux notebooks d'étude et du ML).
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
GH = f"{GH_RACINE}/src"

df, s12, train, test = donnees_partie_5()

entete_partie_5(df, s12, train, test, renvoi_genese=False)
st.markdown("---")
st.header("5.1 La genèse : des anomalies de codification à l'étude du contentieux", anchor="genese")

# ------------------------------------------------------------------------------
st.subheader("1. Une succession d'anomalies", anchor="anomalies")
st.markdown(f"""
Tout est parti d'anomalies dans les codifications de retard, relevées les unes après les autres pendant l'analyse exploratoire de travail (EDA_lab, sur les données d'origine) :
1. **des retards posés alors qu'aucune facture n'était due** : 363 clients, deux fois plus souvent en défaut que la moyenne (44 %), avec une codification qui ne dépasse jamais {codif('2')} (cellules 131 et 132) ;
2. **des clients figés à {codif('2')}** : 530 clients restent codifiés {codif('2')} pendant les 6 mois, sans jamais monter ni redescendre, qu'ils paient ou non, et **77,55 % d'entre eux font défaut** (cellule 136). C'est le déclic : ce comportement ressemble à une **gestion contentieuse**, celle de dossiers sortis du circuit normal et suivis à part, par exemple par un service de recouvrement (cellule 137) ;
3. **des retards qui redescendent à {codif('2')} sans aucun paiement**, alors qu'une facture était due : 393 clients, dont 68,7 % font défaut (cellule 138) ;
4. **une dette qui gonfle sans paiement** : chez les clients figés à {codif('2')}, elle augmente dans 87 % des mois sans paiement, au rythme des intérêts et des frais (cellule 146).

Le dataset ne dit pas si ces comptes sont gelés, confiés au recouvrement ou gérés autrement (cellule 147).
""")

# ------------------------------------------------------------------------------
st.subheader("2. Un modèle de machine learning bloqué sous un plafond invisible", anchor="plafond-ml")
st.markdown(f"""
Avant même l'étude du contentieux, une première série de modèles de machine learning avait été entraînée (partie 6). Elle butait sur un **plafond invisible** : d'un nettoyage à l'autre, d'un scénario à l'autre, la détection du défaut ne progressait plus. Rendre les modèles plus complexes, par exemple en augmentant la profondeur des arbres de décision, n'apportait que du **surapprentissage** : le modèle apprend par cœur les clients de l'entraînement, sans mieux prédire les nouveaux.

Une première version d'un **détecteur de contentieux** a alors été ajoutée aux modèles, sous la forme d'une variable : un client figé à {codif('2')} sur les 6 mois, ou dont le retard redescend à {codif('2')} sans paiement. Ces clients faisaient très souvent défaut, et pourtant **le résultat n'a pas bougé** : les arbres utilisaient à peine cette variable, et élargir leurs réglages n'a rien changé ([tableau de suivi du ML]({GH_RACINE}/lab_ML/1ere_iteration/tableau_ML.md), scénario `S12_7`).

Le diagnostic : **le dataset était trop hétérogène**. Il mélangeait deux populations au comportement très différent, des clients gérés normalement et des clients au contentieux, qu'un seul modèle ne parvient pas à apprendre ensemble. Plutôt que de forcer le modèle, il fallait comprendre cette sous-population, la définir par une règle métier et la traiter à part. Le récit complet de cette première itération d'apprentissage automatique est fait en partie 6.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Une hypothèse : deux systèmes d'information dans un même fichier", anchor="hypothese")
st.markdown(f"""
Une hypothèse d'ensemble relie ces anomalies : **le dataset mêlerait deux systèmes d'information**. D'un côté, le système de gestion courante, qui fait évoluer la codification avec les paiements. De l'autre, un circuit de recouvrement ou de contentieux, où les dossiers sont suivis à part : le client y garde une codification de retard figée, conservée dans le fichier pour le suivi, mais qui ne réagit plus à ses paiements. Plusieurs indices vont dans ce sens :
- des codifications figées à {codif('2')}, ou qui redescendent à {codif('2')} sans paiement, comme si le dossier avait quitté le circuit normal (pages « 3.3 Les codifications » et « 4.6 Les retards ») ;
- une façon de codifier qui change en cours de période, nettement à partir d'août (page « 4.6 Les retards ») ;
- une codification {codif('1')} qui n'existe presque qu'en septembre, comme si le dernier mois venait d'une table de gestion « à chaud » et les mois précédents d'historiques déjà consolidés (page « 3.3 Les codifications ») ;
- des faux retards posés par deux, sur des comptes sans dette, qui ressemblent à une procédure plutôt qu'à des erreurs isolées (page 5.2).
- des clients sans aucune dette, et souvent sans aucun retard, pourtant notés en défaut, comme si le défaut était décidé ailleurs (section 5 de cette page).

Ce n'est qu'une hypothèse : la documentation du dataset ne dit rien de son système d'origine, et elle ne peut pas être vérifiée. Mais elle explique pourquoi les codifications ne se lisent pas seules, et pourquoi toute la suite s'appuie sur les paiements pour les confirmer.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Une étude du contentieux, puis des corrections inscrites au nettoyage", anchor="etude")
st.markdown(f"""
Les anomalies de codification, reprises dans les pages « 3.3 Les codifications » et « 4.6 Les retards », et le plafond du machine learning ont lancé **l'étude du contentieux** ([05_02_EDA_contentieux.ipynb]({GH}/05_02_EDA_contentieux.ipynb)). En cherchant à le définir, elle a d'abord mis au jour de faux retards et un mois de septembre en suspens, puis abouti à une définition. Les corrections qui en découlent ont ensuite été inscrites dans le nettoyage (niveau 5), qui ajoute aussi les indicateurs du contentieux.

**Le but** : repérer les clients en gestion contentieuse par une **règle métier** simple et explicable, les prédire en défaut sans modèle, et laisser au machine learning une population au comportement plus homogène (partie 6).
""")

# ------------------------------------------------------------------------------
st.subheader("5. Le périmètre : les clients qui ont une dette", anchor="perimetre")
sans_dette = df['BILL_AMT1'] <= 0
nb_nul, nb_avoir = int((df['BILL_AMT1'] == 0).sum()), int((df['BILL_AMT1'] < 0).sum())
taux_sans, taux_avec = df.loc[sans_dette, 'dpnm'].mean() * 100, df.loc[~sans_dette, 'dpnm'].mean() * 100
# Clients sans dette notés en défaut : ont-ils un retard sur la période ? leur dette d'août a-t-elle disparu sans paiement ?
sd = df[sans_dette]
defaut_sd = sd['dpnm'] == 1
sans_retard = ~(sd[[f'PAY_{i}' for i in range(1, 7)]] >= 2).any(axis=1)
part_defauts_sans_retard = (defaut_sd & sans_retard).sum() / defaut_sd.sum() * 100
dette_aout = sd['BILL_AMT2'] > 0
nb_disparues = int((dette_aout & (sd['PAY_AMT1'] < 0.9 * sd['BILL_AMT2'])).sum())
taux_soldee = sd.loc[dette_aout & (sd['PAY_AMT1'] >= 0.9 * sd['BILL_AMT2']), 'dpnm'].mean() * 100
st.markdown(f"""
Le risque d'une banque, c'est l'**encours** : l'argent prêté qui n'est pas encore remboursé. L'étude se concentre donc sur les clients qui ont une dette en septembre (`BILL_AMT1` > 0) : **{nombre_fr(len(s12))} clients** sur les {nombre_fr(len(df))} de la population retenue. On ne prédit pas le défaut d'un crédit qui n'est pas utilisé.

**Ce choix laisse de côté une question troublante.** {nombre_fr(int(sans_dette.sum()))} clients n'ont aucune dette en septembre ({nombre_fr(nb_nul)} avec un solde nul, {nombre_fr(nb_avoir)} avec un solde créditeur, c'est-à-dire une avance en leur faveur), et pourtant **{nombre_fr(taux_sans, 1)} % d'entre eux sont notés en défaut en octobre**, presque autant que les clients endettés ({nombre_fr(taux_avec, 1)} %). Que peut-on ne pas rembourser quand on ne doit rien ? Une dette apparue en octobre, des frais, ou une définition du défaut qui ne repose pas seulement sur la dette : le dataset ne permet pas de trancher. Ces dossiers sans encours n'ont pas été étudiés ici : l'étude s'est concentrée sur ce qui fait le risque d'une banque, l'encours. Ils restent une piste ouverte, et un signe de plus que la cible n'est pas entièrement documentée.

Quelques constats orientent tout de même la lecture. **{nombre_fr(part_defauts_sans_retard)} % de ces défauts concernent des clients qui n'ont eu aucun retard** sur les six mois. Ce ne sont pas des comptes gelés avec une dette mise de côté : seules {nombre_fr(nb_disparues)} dettes d'août disparaissent en septembre sans avoir été payées, et les clients qui viennent de solder leur facture d'août font défaut à {nombre_fr(taux_soldee, 1)} %. Rien, ni la dette ni les codifications de ce compte, n'explique donc leur défaut. **Il serait noté dans un autre système que celui de la carte** : par exemple un statut du client à l'échelle de la banque, ou un autre crédit chez elle. C'est une autre forme de la gestion multiple du fichier évoquée plus haut (section 3), qui ne peut pas non plus être vérifiée.
""")
st.caption("Taux de défaut calculé sur toute la population retenue, à titre descriptif : ces clients sont hors du périmètre étudié, et ce chiffre ne sert à fixer aucune règle.")

# ------------------------------------------------------------------------------
st.subheader("6. La méthode", anchor="methode")
st.markdown(f"""
La même sur toutes les pages de cette partie :
- les règles sont fixées par la **logique métier**, jamais en cherchant le seuil qui « marche le mieux » sur le défaut ;
- l'étude du contentieux part des données du **nettoyage de niveau 3** (`cleaned3`). C'est sur ces données qu'elle a fixé ses règles et repéré les codifications à corriger. Ces corrections ont ensuite été ajoutées au nettoyage, au **niveau 5** (page 5.2). Les chiffres de cette partie sont calculés sur ces données corrigées : ce sont les mêmes clients, et on retrouve exactement les résultats de l'étude ;
- avant toute analyse, le périmètre est découpé au hasard en un jeu d'**entraînement** (80 %, {nombre_fr(len(train))} clients) et un jeu de **test** (20 %, {nombre_fr(len(test))} clients), avec la même part de défauts dans les deux (découpage stratifié, tirage fixé pour être reproductible). C'est le même découpage que dans les notebooks d'étude et de machine learning ;
- les descriptions, faites **sans regarder le défaut**, portent sur tout le périmètre. Le **taux de défaut** (part des clients en défaut de paiement en octobre 2005, le mois qui suit les six mois de données) n'est calculé que **sur l'entraînement**, pour vérifier qu'une règle a un sens ; le test n'a servi **qu'une seule fois**, une fois la règle figée (page 5.6).
""")

st.info(f"""
**Ce qu'il faut retenir** : deux signaux ont lancé l'étude. Des clients figés en retard, au taux de défaut anormalement élevé, ont révélé des codifications qui ne suivent plus les paiements, peut-être parce que le fichier mêle la gestion courante et un suivi à part, celui du contentieux. Et un modèle de machine learning plafonnait sur un dataset trop hétérogène, sans qu'une simple variable de contentieux y change rien. L'étude qui en découle se concentre sur les {nombre_fr(len(s12))} clients qui ont une dette, valide ses règles sur l'entraînement et ne regarde le test qu'une fois. Les défauts de clients sans dette restent une question ouverte.
""")
