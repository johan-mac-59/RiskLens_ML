from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 6.1 : L'HISTORIQUE DU MACHINE LEARNING
# Récit de la première itération du ML, menée avant l'étude du contentieux (D17) : démarche, enseignements,
# plafond des performances et coup d'arrêt qui a lancé l'étude du contentieux (partie 5).
# Chiffres repris tels quels de lab_ML/1ere_iteration/tableau_ML.md : les modèles et les données de cette
# itération ne sont pas dans le dépôt (décision D19). Ils décrivent le dataset AVEC la population contentieuse.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
TABLEAU_ML = f"{GH_RACINE}/lab_ML/1ere_iteration/tableau_ML.md"

entete_partie_6()
st.markdown("---")
st.header("6.1 L'historique : une première itération qui a buté sur un plafond, et mené à l'étude du contentieux", anchor="historique")

# ------------------------------------------------------------------------------
st.subheader("1. Une première itération, menée avant l'étude du contentieux", anchor="premiere-iteration")
st.markdown(f"""
Ce site suit un ordre logique : les données, leur nettoyage, l'exploration, la population contentieuse, puis le machine learning. **Dans les faits, la première itération du machine learning a eu lieu avant l'étude du contentieux** : c'est elle qui, en butant sur un plafond, a conduit à cette étude.

Cette première itération a porté sur **tout le dataset, population contentieuse comprise**, puisqu'elle n'était pas encore définie. Sa démarche :
- un découpage au hasard en un jeu d'**entraînement** (80 %) et un jeu de **test** (20 %), avec la même part de défauts dans les deux ;
- **six modèles** comparés au départ : régression logistique, SVM, réseau de neurones (MLP), plus proches voisins (KNN), forêt aléatoire (RandomForest) et CatBoost ; les trois meilleurs (CatBoost, RandomForest et régression logistique) ont ensuite été gardés pour aller plus vite ;
- des réglages (hyperparamètres) cherchés par **GridSearch**, en validation croisée sur l'entraînement ;
- un **score de décision** unique pour tout comparer : la moyenne du **ROC AUC**, qui mesure la capacité à classer les clients du plus sûr au plus risqué (la mesure utilisée, sous une autre forme, par l'étude de 2009), et du **F2**, qui pénalise fortement les défauts manqués, le risque le plus coûteux pour une banque. Seul le score en validation sert à choisir ; le test n'est qu'un contrôle.

Tout est consigné dans le [tableau de suivi de la première itération]({TABLEAU_ML}).
""")

# ------------------------------------------------------------------------------
st.subheader("2. Nettoyer, filtrer, simplifier : des performances très proches", anchor="scenarios")
st.markdown(f"""
Les premiers essais ont croisé deux leviers :
- **les niveaux de nettoyage** (page « 3.5 Décisions ») : données d'origine, puis paiements géants et comptes inactifs retirés, puis codifications {codif('1')} recalées ;
- **des scénarios** appliqués à chaque niveau : plafonner les retards à {codif('2')}, regrouper les codifications saines {codif('-2')}, {codif('-1')} et {codif('0')}, ne garder que les clients qui ont une dette en septembre, écarter les plafonds atypiques, retirer `PAY_1` ou le remplacer par un ratio de paiement.

Ce qu'ils ont appris :
- **d'un niveau de nettoyage à l'autre, les performances bougent à peine** : le nettoyage rend les données plus justes, sans que les modèles en tirent un net avantage ;
- **simplifier les codifications fait perdre de l'information** : regrouper ou plafonner les retards n'apporte rien, ou dégrade le score ;
- **`PAY_1`, la codification de septembre, est indispensable** : la retirer coûte environ 3 points de score de décision, même quand elle est corrigée ;
- **ne garder que les clients qui ont une dette en septembre relève nettement les performances**, de tous les modèles, et a un sens métier : on ne prédit pas le défaut d'un crédit qui n'est pas utilisé ;
- **écarter les plafonds atypiques** (page « 3.4 Les plafonds ») ne change presque rien au score, mais recentre les modèles sur la clientèle standard.

Ces deux filtres forment le périmètre appelé **S12**, retenu pour la suite. C'est aussi celui de l'étude du contentieux. Le filtre des clients endettés seul (`S3`) garde un score un peu plus élevé, mais l'écart est plus petit que la variation d'un pli de validation à l'autre : les deux sont à égalité, et `S12` a été préféré pour sa raison métier.
""")

# ------------------------------------------------------------------------------
st.subheader("3. De nouvelles variables, et un plafond invisible", anchor="plafond")
st.markdown("""
Sur ce périmètre, de nouvelles variables ont été ajoutées une à une, chacune gardée seulement si elle améliorait le score de décision : l'utilisation du plafond chaque mois, des tranches d'âge, les ratios de paiement, le ratio de paiement habituel du client (une première forme du type d'usage de la carte, page 4.3), puis l'ancienneté d'activité du compte.
""")

# Score de décision du meilleur modèle à chaque étape conservée, en validation croisée sur l'entraînement :
# scénarios retenus au nettoyage de niveau 3 (avec la base S1), puis variables gardées sur le périmètre S12
# (avec la référence S12_0 et la variable de contentieux S12_7, qui a provoqué l'arrêt). (code, libellé court, score)
scenarios_niveau3 = [
    ("S1", "base", 0.6808),
    ("S3", "dette en septembre", 0.6907),
    ("S11", "plafonds ≤ 500 000", 0.6856),
    ("S12", "S3 + S11", 0.6860),
]
etapes = [
    ("S12_0", "référence S12", 0.6865),
    ("S12_1", "+ utilisation du plafond", 0.6877),
    ("S12_5", "+ ratio de paiement habituel", 0.6878),
    ("S12_6", "+ ancienneté du compte", 0.6885),
    ("S12_7", "+ variable de contentieux", 0.6875),
]
experiences = scenarios_niveau3 + etapes
libelles = [f"{e[0]}<br>{e[1]}" for e in experiences]

fig_plafond = go.Figure(go.Bar(
    x=libelles, y=[e[2] for e in experiences], marker_color=COULEURS["turquoise"],
    text=[nombre_fr(e[2], 4) for e in experiences], textposition="outside", textfont_size=TAILLE_ETIQUETTE,
    hovertemplate="%{x}<br>Score de décision : %{y:.4f}<extra></extra>"))
# Séparation entre les deux séries d'étapes
separation = len(scenarios_niveau3) - 0.5
fig_plafond.add_vline(x=separation, line_dash="dot", line_color=COULEURS["gris"])
fig_plafond.add_annotation(x=(len(scenarios_niveau3) - 1) / 2, y=0.93, text="<b>Scénarios</b> (nettoyage de niveau 3)", showarrow=False, font_size=TAILLE_ETIQUETTE)
fig_plafond.add_annotation(x=separation + len(etapes) / 2, y=0.93, text="<b>Nouvelles variables</b> (périmètre S12)", showarrow=False, font_size=TAILLE_ETIQUETTE)
fig_plafond.update_layout(yaxis_title="Score de décision (validation)", yaxis_range=[0, 1], height=480, separators=", ", showlegend=False)
st.plotly_chart(fig_plafond, width='stretch')
st.caption(f"Score de décision du meilleur modèle à chaque étape conservée, en validation croisée sur l'entraînement, sur le dataset avec la population contentieuse. Ne figurent que les scénarios et les variables gardés (`S11`, gardé un temps, a ensuite été remplacé par `S12`, qui l'inclut), avec les deux points de départ (`S1`, `S12_0`) et la variable de contentieux (`S12_7`). Chiffres repris tels quels du [tableau de suivi de la première itération]({TABLEAU_ML}), sections 2 et 3 : ces modèles ne sont pas dans le dépôt.")

ecart_total = max(e[2] for e in etapes) - min(e[2] for e in etapes)
st.markdown(f"""
**Ajouter de l'information ne fait plus monter le score ; en retirer le fait baisser.** Parmi les scénarios, seuls les filtres de population relèvent un peu le score : les clients endettés (`S3`) et, moins nettement, les plafonds de 500 000 NT$ ou moins. Les simplifications des codifications le laissent au même niveau ou le dégradent, et retirer la codification de septembre le fait chuter d'environ 3 points (scénarios écartés, absents du graphique).

**Sur le périmètre S12, le score ne bouge plus.** D'une nouvelle variable à l'autre, il reste entre {nombre_fr(min(e[2] for e in etapes), 4)} et {nombre_fr(max(e[2] for e in etapes), 4)} : un écart de {nombre_fr(ecart_total, 4)}, plus petit que la variation du score d'un pli de validation à l'autre (de l'ordre de 0,006 à 0,009 pour le ROC AUC et le F2). Impossible de distinguer une vraie amélioration du hasard du découpage. Rendre les modèles plus complexes, par exemple avec des arbres plus profonds, n'apportait que du **surapprentissage** : le modèle apprend par cœur les clients de l'entraînement, sans mieux prédire les autres. Les modèles butaient sur un **plafond invisible**.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Le coup d'arrêt : une variable de contentieux sans effet", anchor="arret")
st.markdown(f"""
En parallèle, l'analyse exploratoire avait repéré des clients **figés à {codif('2')}** sur les six mois, qui font défaut à 77,55 % (page 5.1). Une variable a alors été ajoutée aux modèles pour les signaler (scénario `S12_7`) : un client figé à {codif('2')}, ou dont le retard redescend à {codif('2')} sans paiement. Les clients ainsi signalés faisaient défaut à **71,27 %**.

**Et pourtant, le score n'a pas bougé.** Les arbres de décision utilisaient à peine cette variable, et élargir leurs réglages n'y a rien changé. Les modèles avaient sans doute déjà repéré ces clients par leurs codifications : la variable ne leur apprenait rien de neuf.

Le diagnostic : **le dataset mélangeait deux populations**, des clients en gestion normale et des clients en gestion contentieuse, au comportement et au risque très différents. Un seul modèle les apprend mal ensemble, et il passe surtout son effort à reconnaître les seconds, ce qu'une règle métier fait de façon plus simple et explicable. Plutôt que de forcer les modèles, **le machine learning a été arrêté** pour comprendre cette population, la définir et la traiter à part : c'est **l'étude du contentieux, présentée en partie 5**.

La variable de `S12_7` reposait sur une première définition, abandonnée depuis : la définition retenue est celle de la page 5.3.
""")

st.info("""
**Ce qu'il faut retenir** : la première itération du machine learning, menée sur tout le dataset, a comparé six modèles, plusieurs niveaux de nettoyage et de nombreux scénarios. Elle a fixé le périmètre (les clients qui ont une dette, hors plafonds atypiques), confirmé le poids de la codification de septembre, puis buté sur un plafond : ni les nouvelles variables, ni une variable de contentieux ne faisaient progresser les modèles. Ce blocage a révélé deux populations mélangées et lancé l'étude du contentieux (partie 5).
""")


# ==============================================================================
# SIMULATEUR : TAUX DE DÉFAUT PAR PROFIL, SUR LA POPULATION LAISSÉE AU MACHINE LEARNING
# Dataset Streamlit, périmètre S12 (dette en septembre, plafond <= 500 000 NT$), sans les clients au contentieux à M :
# la population de lab_ML/creation_datasets_ML.ipynb (train + test). Fonction simulateur_profil de commun.py (4.1, 5.5)
# ==============================================================================
df = load_data()
hors_ctx = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)
              & ~((df["FLAG_CTX"] == 1) & (df["MOIS_SORTIE_CTX"] == -1))]
simulateur_profil(hors_ctx, "simulateur-ml",
                  f"en direct sur les {nombre_fr(len(hors_ctx))} clients hors du contentieux, ceux qu'étudie le machine learning",
                  "des clients hors du contentieux")
