from streamlit_pages.commun import *

# ==============================================================================
# SECTION 1 : ACCUEIL & PRÉSENTATION
# ==============================================================================
st.title("🏦 RiskLens ML — Analyse & Prédiction du Risque Crédit 💳")


# ------------------------------------------------------------------------------
# Chiffres de « Ce que l'analyse va montrer », calculés en direct (parties 3 à 5)
# Données d'origine (30 000 lignes, absentes du dépôt) : taux de défaut repris de 05_02_EDA_contentieux, cellule 41
TAUX_DEFAUT_ORIGINE = 22.12
ent_accueil = load_entonnoir()
df_accueil, s12_accueil, train_accueil, test_accueil = donnees_partie_5()
# 4.3 : taux de défaut selon le type d'usage ; 4.6 : selon le nombre de mois en retard
defaut_type = df_accueil.groupby('TYPE_USAGE')['dpnm'].mean() * 100
defaut_incident = df_accueil.groupby('CUMUL_INCIDENT')['dpnm'].mean() * 100
# 4.5 : dette totale d'avril à septembre, et part remboursée le mois suivant (paiement plafonné à la dette du client)
dette_avril = df_accueil['BILL_AMT6'].clip(lower=0).sum()
dette_sept = df_accueil['BILL_AMT1'].clip(lower=0).sum()
parts_remb = [np.minimum(df_accueil[f'PAY_AMT{n - 1}'], df_accueil[f'BILL_AMT{n}'].clip(lower=0)).sum()
              / df_accueil[f'BILL_AMT{n}'].clip(lower=0).sum() * 100 for n in range(2, 7)]
# 5.6 : la règle du contentieux sur le jeu de test (utilisé une seule fois)
ctx_test = test_accueil['STATUT'] == "Au contentieux"
part_ctx = ctx_test.mean() * 100
precision_ctx = test_accueil.loc[ctx_test, 'dpnm'].mean() * 100
captes_ctx = test_accueil.loc[ctx_test, 'dpnm'].sum() / test_accueil['dpnm'].sum() * 100

st.markdown(f"""
**RiskLens ML** est une mission Data & IA complète visant à transformer des données transactionnelles historiques en un outil d'aide à la décision pour la gestion du risque crédit.
Durée prévue : 7 semaines à partir du 30 août  

Le projet suit un cycle de vie data complet : du diagnostic initial et la structuration d'une base de données relationnelle, à l'exposition des données via une API, jusqu'à la création d'un modèle prédictif et d'un dashboard interactif sous Streamlit.

### 🎯 Problématique
> **"Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ?"**

L'enjeu est de déterminer si les habitudes de paiement et l'utilisation du crédit ainsi que les informations de base d'un client sont des indicateurs suffisamment robustes pour anticiper un défaut, sans deux types d'informations que les banques utilisent d'habitude : les **données de conjoncture** (chômage, inflation, croissance) et les **données économiques du client lui-même** (revenu, autres crédits, loyer, endettement total, reste à vivre), ni score de crédit externe.

### 💥 Le contexte : la crise des *"Card Monsters"* (Taïwan, 2005)
- **L'économie allait bien** : chômage bas, inflation maîtrisée, croissance solide. La crise ne vient pas de l'économie.
- **Les banques ont distribué des cartes sans compter** : 133 cartes pour 100 adultes en 2005, avec des critères d'octroi abaissés et des taux de 17 à 20 % par an, au plafond légal. Beaucoup de clients ne pouvaient plus payer que le minimum chaque mois : on les a surnommés les « esclaves de la carte ».
- **Des clients payaient une carte avec une autre**, en multipliant les cartes dans des banques différentes : c'est la « cavalerie ».
- **En 2005, le régulateur durcit les conditions d'octroi** : la « cavalerie » se grippe et les impayés augmentent fortement au second semestre 2005, avant que la crise n'éclate au grand jour en 2006. **Le dataset couvre avril à septembre 2005, au moment où la vague monte.**

""")

# Frise de la crise : étapes d'après docs/contexte.md (dates connues à l'année près, d'où une frise par étapes)
st.graphviz_chart(r"""
digraph {
    rankdir=LR; nodesep=0.25; ranksep=0.35;
    node [shape=box, style="rounded,filled", fillcolor="#e1f5fe", fontname="Helvetica", fontsize=10, margin="0.12,0.06"];
    edge [color="#888888"];
    a [label="1990 – 2005\nLes banques distribuent\nmassivement des cartes"];
    b [label="2005\nLe régulateur durcit\nles conditions d'octroi"];
    c [fillcolor="#b3e5fc", label="Avril → septembre 2005\nLes impayés montent\n= les 6 mois du dataset"];
    d [fillcolor="#fff3e0", label="Octobre 2005\nDéfaut de paiement ?\n= la cible à prévoir"];
    e [label="2006\nLa crise éclate ;\nnégociation des dettes"];
    f [label="Au plus tard en 2006\nEndettement plafonné\nà 22 fois le revenu"];
    a -> b -> c -> d -> e -> f;
}
""", width="stretch")
st.caption("Les étapes de la crise des cartes de crédit à Taïwan et la place du dataset. Sources détaillées dans la chronologie du document de contexte du projet.")

st.markdown(f"""
### 📚 Le dataset et l'étude de référence
Ce dataset est la base de données publique qui résulte de [l'étude scientifique de I-Cheng Yeh et Che-hui Lien (2009)](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/DefaultCreditCardClients_yeh_2009.pdf) (traduit en français [ici](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/traduction_DefaultCreditCardClients_yeh_2009.md)). En pleine crise, une banque taïwanaise a confié aux chercheurs un échantillon anonymisé de 30 000 clients. Cette étude comparait plusieurs modèles pour repérer les clients à risque. Le meilleur, un réseau de neurones, obtenait un score de 0,54, ce qui correspond à un **AUC de 0,77**. L'AUC mesure la capacité d'un modèle à distinguer les bons payeurs des futurs défaillants.

Ma démarche adopte un prisme résolument **orienté métier**. En combinant une compréhension approfondie du jeu de données (le fonctionnement de la banque, de ses codifications et des paiements de l'époque), un nettoyage rigoureux fondé sur des règles métier et une exigence posée avant tout modèle, un **taux de rappel minimal** (le modèle du projet doit trouver au moins une part fixée des défauts), je cherche à optimiser la détection réelle des risques de défaut, garantissant ainsi une performance robuste et réellement actionnable pour la gestion des risques bancaires.

**🚀 Objectif ML Engineer :** Mon but est de dépasser le score de référence de l'étude de 2009 (un AUC de 0,77). En banque, oublier un client à risque (Faux Négatif) coûte bien plus cher que de suspecter un client sûr (Faux Positif).

### 🔎 Ce que l'analyse va montrer
L'analyse est terminée, du nettoyage au déploiement. Voici ses conclusions, partie par partie :
- **Les données (partie 1)** : {nombre_fr(ent_accueil.loc['origine', 'clients'])} clients d'une banque taïwanaise, suivis d'avril à septembre 2005, en pleine crise des cartes de crédit. {nombre_fr(TAUX_DEFAUT_ORIGINE, 1)} % font défaut en octobre, un taux bien plus élevé que celui d'un portefeuille bancaire ordinaire.
- **La base de données et l'API (partie 2)** : les données sont rangées dans une base relationnelle et exposées par une API REST, comme dans le système d'information d'une banque.
- **Comprendre le jeu de données (partie 3)** : un fichier complet, mais des anomalies à expliquer avant toute analyse. Les codifications de paiement ne sont pas un fait brut : c'est une étiquette de la banque, mise à jour avec un mois de décalage sur le paiement. Très peu de lignes sont retirées ({nombre_fr(ent_accueil.loc['sans_paiements_geants', 'retires'])} paiements géants, {nombre_fr(ent_accueil.loc['sans_comptes_inactifs', 'retires'])} comptes inactifs, {nombre_fr(ent_accueil.loc['sans_plafonds_atypiques', 'retires'])} plafonds atypiques) : il reste {nombre_fr(ent_accueil.loc['sans_plafonds_atypiques', 'clients'])} clients.
- **L'analyse exploratoire (partie 4)** : le profil des clients ne pèse que modérément sur le risque ; ce sont les comportements qui comptent. Un client qui ne rembourse rien fait défaut à {nombre_fr(defaut_type.get('Ne paie rien', 0))} %, un payeur au comptant à {nombre_fr(defaut_type.get('Paiement comptant', 0))} %. La dette totale des clients augmente de {nombre_fr((dette_sept / dette_avril - 1) * 100)} % en six mois, alors qu'ils n'en remboursent chaque mois que {nombre_fr(min(parts_remb))} à {nombre_fr(max(parts_remb))} %. Et le risque grimpe avec les codifications de retard accumulées : de {nombre_fr(defaut_incident.get(0, 0))} % sans aucune à {nombre_fr(defaut_incident.get(6, 0))} % pour un retard sur les six mois.
- **La population contentieuse (partie 5)** : des clients figés en retard et un modèle qui plafonnait ont conduit à isoler une sous-population par une **règle métier explicable**, deux codifications de retard d'affilée, soit au moins 90 jours. Sur des clients jamais vus, elle ne retient que {nombre_fr(part_ctx)} % des clients, mais {nombre_fr(precision_ctx)} % d'entre eux font défaut, et elle capte ainsi {nombre_fr(captes_ctx)} % des défauts, sans aucun modèle.
- **Le machine learning (partie 6)** : sur les autres clients, tous les modèles et toutes les variables atteignent le même plafond. Le modèle retenu, sans aucune donnée démographique, range les clients par niveau de risque, du très haut risque (un client sur deux en défaut) au risque faible (un sur dix). Environ un tiers des défauts ont le profil des bons clients et ne s'annoncent pas dans les données.
- **Le déploiement (partie 7)** : la règle puis le modèle tournent en direct, de la base de données à la décision, sur des clients jamais vus, et retrouvent les résultats de l'évaluation.
- **La réponse (partie 8)** : oui, en partie. Le comportement des six derniers mois prévoit une grande part des défauts et classe les clients par niveau de risque, avec un AUC un peu au-dessus du 0,77 de l'étude : défi relevé, de peu. Il ne désigne pas à coup sûr ceux qui feront défaut.


#### 🕵️‍♂️ Pour aller plus loin : Les coulisses de la donnée

Pour découvrir comment des détails logistiques de l'époque (comme les règlements en espèces dans les supérettes 7-Eleven, qui créent des décalages dans l'enregistrement des paiements sur les comptes, et des erreurs de saisie) ou les parallèles avec le **Buy Now, Pay Later (BNPL)** actuel éclairent ce projet d'un point de vue purement métier :
📖 [Lire le contexte du projet](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/contexte.md) · 📚 [Toutes les sources du projet](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/sources.md)
""")




st.markdown("---")
st.subheader("🛠️ La démarche du projet")
st.graphviz_chart(r"""
digraph {
    rankdir=TB; nodesep=0.35; ranksep=0.45;
    node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10, margin="0.12,0.06"];
    edge [color="#888888", fontname="Helvetica", fontsize=9];

    donnees [fillcolor="#d9f0e3", label="✅ Données brutes\n30 000 clients (UCI)"];
    audit [fillcolor="#d9f0e3", label="✅ Audit et\nnettoyage structurel\n(niveau 0)"];
    bdd [fillcolor="#d9f0e3", label="✅ Base SQLite\net API REST"];
    eda1 [fillcolor="#d9f0e3", label="✅ Analyse\nexploratoire"];
    nett [fillcolor="#d9f0e3", label="✅ Nettoyage\nniveaux 1 à 3"];
    ml1 [fillcolor="#eeeeee", label="⏹ Machine learning\n1re itération"];
    blocage [style="rounded,filled,dashed", fillcolor="#fde2e4", color="#CC6677", label="Blocage : les performances plafonnent,\nune sous-population est détectée"];
    eda2 [fillcolor="#d9f0e3", label="✅ Analyse\ndu contentieux"];
    ctx [fillcolor="#d9f0e3", label="✅ Définition métier\ndu contentieux\n(nettoyage niveau 5)"];
    ml2 [fillcolor="#d9f0e3", label="✅ Machine learning\n2e itération,\nsur les autres clients"];
    deploi [fillcolor="#d9f0e3", label="✅ Déploiement :\nrègle + modèle en direct,\nde la base à la décision"];
    dash [shape=plaintext, style="", label="✅ Dashboard Streamlit, construit au fil de l'analyse,\npuis slides de restitution qui le résument"];
    dash_fin [shape=none, label="", width=0, height=0, margin=0];

    // Ligne 1 : le premier parcours ; ligne 2 : le blocage ; ligne 3 : le second parcours ; ligne 4 : Streamlit
    {rank=same; donnees -> audit -> bdd -> eda1 -> nett -> ml1;}
    {rank=same; blocage;}
    {rank=same; eda2 -> ctx -> ml2 -> deploi;}
    {rank=same; dash -> dash_fin [style=dashed, penwidth=1.5];}

    ml1 -> blocage;
    blocage -> eda2;

    // Colonnes alignées (liaisons invisibles)
    eda1 -> eda2 [style=invis, weight=20]; nett -> ctx [style=invis, weight=20];
    blocage -> ml2 [style=invis, weight=20]; eda2 -> dash [style=invis, weight=20]; deploi -> dash_fin [style=invis, weight=20];
}
""", width="stretch")
st.caption("✅ fait ; ⏹ arrêté.")

st.markdown("---")
st.subheader("⚙️ Les outils du projet")
st.markdown("""
- **Analyse des données :** Pandas, NumPy, Matplotlib, Seaborn, Plotly
- **Machine learning :** Scikit-Learn, CatBoost
- **Base de données :** SQLite (modèle relationnel)
- **API :** FastAPI, avec Pydantic pour le contrôle des données
- **Application :** Streamlit
- **Mise en ligne :** Render (API) et Streamlit Cloud (application)
""")
