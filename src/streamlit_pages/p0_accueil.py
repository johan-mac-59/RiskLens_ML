from streamlit_pages.commun import *

# ==============================================================================
# SECTION 1 : ACCUEIL & PRÉSENTATION
# ==============================================================================
st.title("🏦 RiskLens ML — Analyse & Prédiction du Risque Crédit 💳")


st.markdown(f"""
**RiskLens ML** est une mission Data & IA complète visant à transformer des données transactionnelles historiques en un outil d'aide à la décision pour la gestion du risque crédit.
Durée prévue : 7 semaines à partir du 30 août  

Le projet suit un cycle de vie data complet : du diagnostic initial et la structuration d'une base de données relationnelle, à l'exposition des données via une API, jusqu'à la création d'un modèle prédictif et d'un dashboard décisionnel.

### 🎯 Problématique
> **"Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ?"**

L'enjeu est de déterminer si les habitudes de paiement et l'utilisation du crédit ainsi que les informations de bases d'un client sont des indicateurs suffisamment robustes pour anticiper un défaut, sans avoir accès à des données macro-économiques ou des scores de crédit externes.

### 💥 Le contexte : la crise des *"Card Monsters"* (Taïwan, 2005)
- **L'économie allait bien** : chômage bas, inflation maîtrisée, croissance solide. La crise ne vient pas de l'économie.
- **Les banques ont distribué des cartes sans compter**, y compris aux étudiants et aux petits revenus, au taux maximal autorisé (près de 20 %). Les mensualités minimales couvraient à peine les intérêts.
- **Beaucoup de clients payaient une carte avec une autre**, certains cumulant plus de dix cartes dans des banques différentes.
- **En 2005, le régulateur a plafonné l'endettement** : cette « cavalerie » s'est arrêtée net et une vague d'impayés a suivi, d'avril à octobre 2005. **C'est exactement la période couverte par le dataset.**

### 📚 Le dataset et l'étude de référence
Ce dataset est la base de données publique qui résulte de [l'étude scientifique de I-Cheng Yeh et Che-hui Lien (2009)](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/DefaultCreditCardClients_yeh_2009.pdf) (traduit en français [ici](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/traduction_DefaultCreditCardClients_yeh_2009.md)). En pleine crise, une banque taïwanaise a confié aux chercheurs un échantillon anonymisé de 30 000 clients. Cette étude comparait plusieurs modèles pour repérer les clients à risque. Le meilleur, un réseau de neurones, obtenait un score de 0.54, ce qui correspond à un **AUC de 0.77**. L'AUC mesure la capacité d'un modèle à distinguer les bons payeurs des futurs défaillants. Mon but est de dépasser ce score.
Ma démarche adopte un prisme résolument **orienté métier**. En combinant un nettoyage rigoureux des données et un pilotage par un score maître (moyenne du ROC AUC et du F2 score, qui privilégie le Recall), je cherche à optimiser la détection réelle des risques de défaut, garantissant ainsi une performance robuste et réellement actionnable pour la gestion des risques bancaires.

### 🔎 Ce que l'analyse va montrer
1. Le portefeuille se dégrade mois après mois.
2. Le profil du client donne des signaux réels, mais faibles.
3. Les données se lisent avec un œil de banquier : certaines codifications ne disent pas ce qu'elles semblent dire.
4. Le comportement de paiement donne les signaux les plus forts.
5. Une petite partie des clients, déjà au contentieux, concentre une grande part des défauts.


#### 🕵️‍♂️ Pour aller plus loin : Les coulisses de la donnée

Pour découvrir comment des détails logistiques de l'époque (comme les règlements en espèces dans les supérettes 7-Eleven créant des décalages sur la variable `PAY_1`) ou les parallèles avec le **Buy Now, Pay Later (BNPL)** actuel éclairent ce projet d'un point de vue purement métier :
📖 [Lire le contexte du projet](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/contexte.md)
""")



st.markdown("**🚀 Objectif ML Engineer :** Mon but est de dépasser le score de référence de 2009 (ratio de surface de 0.54, soit un AUC de 0.77) avec un **score maître** qui combine le ROC AUC et le F2 score (le F2 privilégie le Recall). En banque, oublier un client à risque (Faux Négatif) coûte bien plus cher que de suspecter un client sûr (Faux Positif).")

st.markdown("---")
st.subheader("🛠️ Roadmap du Projet")
cols_road = st.columns(5)
steps = ["Audit & Cadrage", "Modélisation BDD", "Développement API", "EDA & Storytelling", "ML & Prédiction"]
for i, step in enumerate(steps):
    cols_road[i].markdown(f"**{i+1}. {step}**")
    cols_road[i].markdown("✅" if i < 3 else "⏳")
