from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 3 : COMPRENDRE LE JEU DE DONNÉES
# Les données d'origine ne sont pas dans le dépôt : les résultats sont repris
# tels quels des notebooks d'origine, avec leur source.
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/src"

# ------------------------------------------------------------------------------
# 3.2 LES MONTANTS
# ------------------------------------------------------------------------------
entete_partie_3()

st.markdown("---")
st.header("3.2 Les montants : erreurs de saisie ou réalité de l'époque ?", anchor="montants")
st.markdown("Chaque montant anormal relevé par l'audit est repris : que cache-t-il, et peut-on l'expliquer ?")
CTX = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/contexte.md"

st.subheader("Payer sa carte de crédit à Taïwan en 2005")
st.markdown(f"""
Pour comprendre ces montants, il faut d'abord savoir **comment on utilisait et payait une carte de crédit à Taïwan en 2005** ([contexte du projet]({CTX})) :
- **Le paiement se faisait surtout en espèces**, au comptoir des supérettes ouvertes jour et nuit (7-Eleven, FamilyMart…), avec le relevé papier et son code-barres ; mais aussi aux distributeurs automatiques, au guichet de la banque ou à la poste. Le prélèvement automatique était peu utilisé.
- **Un paiement n'était pas enregistré tout de suite** : un règlement en supérette mettait 48 à 72 heures ouvrées à parvenir à la banque, et les flux étaient rapprochés en fin de mois par des traitements par lots. Un paiement fait en fin de mois pouvait donc n'apparaître que sur le mois suivant.
- **Les saisies étaient en partie manuelles** (guichets, bureaux de poste), avec le risque d'erreurs de frappe que cela comporte.
- **C'était la crise des cartes de crédit** : les banques avaient distribué massivement des cartes et des cartes de retrait d'espèces, parfois sans contrôle de solvabilité ; certains clients retiraient de l'argent sur une carte pour en rembourser une autre. En 2005, le régulateur a plafonné l'endettement non garanti des particuliers, ce qui a pu conduire les banques à revoir les plafonds de leurs clients.
""")

st.subheader("Un premier regard : des montants très asymétriques")
st.markdown(f"""
Mois par mois, la moitié des paiements se situe sous 2 100 NT\\$, et les trois quarts sous environ 5 000 NT\\$ ; pourtant, chaque mois, le paiement maximum dépasse plusieurs centaines de milliers de NT\\$. Les factures montrent la même asymétrie, avec en plus des valeurs négatives. Quelques très gros montants suffisent à déformer les moyennes : c'est pourquoi la suite raisonne en médianes et en ratios ([01_01_audit.ipynb]({GH}/01_01_audit.ipynb), cellule 2, résumé statistique sur les 30 000 clients).
""")

# Quartiles, minimum et maximum repris du résumé statistique de l'audit (01_01_audit, cellule 2), d'avril à septembre
mois_box = ["Avril", "Mai", "Juin", "Juillet", "Août", "Septembre"]
stats_box = {
    "Factures": dict(mini=[-339603, -81334, -170000, -157264, -69777, -165580], q1=[1256, 1763, 2326.75, 2666.25, 2984.75, 3558.75],
                     med=[17071, 18104.5, 19052, 20088.5, 21200, 22381.5], q3=[49198.25, 50190.5, 54506, 60164.75, 64006.25, 67091],
                     maxi=[961664, 927171, 891586, 1664089, 983931, 964511]),
    "Paiements": dict(mini=[0] * 6, q1=[117.75, 252.5, 296, 390, 833, 1000], med=[1500, 1500, 1500, 1800, 2009, 2100],
                      q3=[4000, 4031.5, 4013.25, 4505, 5000, 5006], maxi=[528666, 426529, 621000, 896040, 1684259, 873552]),
}
fig_box = make_subplots(rows=1, cols=2, subplot_titles=["Factures (NT$)", "Paiements (NT$)"])
for col, (nom, s) in enumerate(stats_box.items(), start=1):
    fig_box.add_trace(go.Box(x=mois_box, q1=s["q1"], median=s["med"], q3=s["q3"], lowerfence=s["mini"], upperfence=s["maxi"],
                             name=nom, boxpoints=False, marker_color="#1f77b4" if col == 1 else "#ff7f0e"), row=1, col=col)
    # Médiane mise en évidence : trait rouge par-dessus chaque boîte
    fig_box.add_trace(go.Scatter(x=mois_box, y=s["med"], mode="markers", name="Médiane",
                                 marker=dict(symbol="line-ew", size=36, line=dict(width=4, color="#d62728")),
                                 hovertemplate="Médiane : %{y:,.0f}<extra></extra>"), row=1, col=col)
fig_box.update_layout(height=520, showlegend=False, margin=dict(t=50))
st.plotly_chart(fig_box, width="stretch")
st.caption("Boîte : du premier au troisième quartile ; trait rouge : la médiane. Moustaches : du minimum au maximum du mois.")
st.markdown("Ces deux graphiques sont peu lisibles, et c'est précisément ce qu'ils montrent : pour les factures comme pour les paiements, les boîtes, qui contiennent la moitié des montants, sont écrasées au ras de l'axe, tandis que les moustaches montent jusqu'à des valeurs des centaines de fois plus élevées. **L'immense majorité des flux est faite de petits montants, et quelques valeurs se détachent très loin au-dessus.** À défaut d'être des anomalies, ces montants extrêmes sont au moins des **valeurs atypiques** : la suite cherche à savoir lesquelles sont des erreurs et lesquelles reflètent une réalité.")

st.subheader("1. Quatre paiements géants")
st.markdown(f"""
Seuls 4 clients ont un paiement de plus de 1 000 000 NT\\$, tous enregistrés le même mois (août), et chacun plusieurs fois supérieur au plafond de la carte ([05_01_EDA_lab.ipynb]({GH}/05_01_EDA_lab.ipynb), cellule 3) :
""")
st.dataframe(pd.DataFrame({
    "Client (ID)": [5297, 25732, 28004, 28717],
    "Plafond (NT$)": [500000, 80000, 510000, 340000],
    "Paiement d'août (NT$)": [1684259, 1024516, 1227082, 1215471],
    "Soit, en fois le plafond": ["3,4", "12,8", "2,4", "3,6"],
}), hide_index=True, width="stretch")
st.markdown("""
Dépasser son plafond de quelques dizaines de pourcents est possible avec une carte de crédit ; payer plusieurs fois le plafond autorisé, en un seul mois, ne l'est pas. Ces 4 lignes ressemblent fortement à des erreurs. Entre 500 000 et 1 000 000 NT\\$, en revanche, le constat est plus nuancé : 7 autres clients y ont un paiement, qui va de 0,7 à 1,7 fois leur plafond (lab, cellule 5). Ces dépassements restent modérés, loin des multiples observés chez les 4 clients précédents.
""")

st.subheader("2. Des factures et des paiements au-delà du plafond")
st.markdown("""
Les autres dépassements restent rares (lab, cellules 8 et 9, sur 29 996 clients, les 4 paiements géants étant mis de côté) :
""")
st.dataframe(pd.DataFrame({
    "Dépassement": ["Une facture au-delà de 2,1 fois le plafond", "Un paiement d'au moins 1,2 fois le plafond", "Un paiement d'au moins 2,1 fois le plafond"],
    "Clients": [40, 78, 12],
}), hide_index=True, width="stretch")
st.markdown(f"""
Dans le crédit renouvelable, dépasser son plafond est rare mais possible ; au-delà de 120 %, c'est difficile. Pourtant, ce seuil serait trop sévère ici : des clients paient en avance, d'autres remboursent toute leur carte chaque mois, et un paiement fait en fin de mois en supérette peut n'être enregistré que le mois suivant. Pour les plus gros écarts, deux explications restent possibles mais invérifiables : une **baisse du plafond** par la banque pendant la période, plausible en pleine crise, quand le régulateur resserre l'endettement ; ou une **erreur de saisie** au guichet (un montant multiplié par 100, ou saisi deux fois). La lecture des lignes concernées ne montre pas d'aberration flagrante : ces dépassements traduisent plutôt un usage intensif de la carte (lab, cellules 10, 160 et 162).

**Une hypothèse de fond : le plafond n'est pas une vérité intemporelle.** Le dataset ne donne qu'**un seul plafond par client**, sans date. Il s'agit vraisemblablement du plafond en vigueur au mois M, quand les données ont été extraites, mais rien ne dit qu'il était le même d'avril à septembre. En pleine crise, une banque pouvait réduire le plafond d'un client en difficulté, ou l'ajuster après une revue de ses revenus. Une facture d'avril qui dépasse le plafond de septembre n'est donc pas forcément une anomalie : le plafond d'avril était peut-être plus élevé. Se fier à ce plafond comme référence pour les 6 mois est une erreur à éviter ; c'est aussi une précaution pour toute mesure de l'utilisation du plafond dans le temps (lab, cellule 10).
""")

st.subheader("3. Des ratios de paiement démesurés")
st.markdown("""
Le ratio de paiement compare le montant payé à la facture qu'il règle. 486 clients ont au moins un mois où ils paient plus de 2,1 fois leur facture (ratio supérieur à 210 %) (lab, cellule 61). Certaines lignes révèlent une erreur de saisie probable, comme le client 344 :
""")
st.dataframe(pd.DataFrame({
    "Mois": ["Avril", "Mai"],
    "Facture (NT$)": [1005, -1005],
    "Paiement (NT$)": [1898, 101005],
}), hide_index=True, width="stretch")
st.markdown(f"""
En mai, ce client paie 101 005 NT\\$ pour une facture de 1 005 NT\\$ : un « 100 » s'est probablement glissé devant le montant, et sa facture devient négative. Mais ces cas restent isolés. La plupart des ratios extrêmes viennent de **très petites factures** : payer 1 000 NT\\$ pour une facture de 5 NT\\$ donne déjà un ratio de 20 000 %. Quand on ne garde que les factures d'au moins 100 NT\\$, il ne reste que 48 cas où le client paie plus de 10 fois sa facture (ratio supérieur à 1 000 %) sur toute la période (lab, cellule 65), et ils ne présentent pas d'anomalie visible.

Le décalage d'enregistrement des paiements explique une bonne part de ces écarts : un paiement réglé en espèces en fin de mois et enregistré le mois suivant fait apparaître un mois de paiement trop élevé, et un mois sans paiement. Corriger ces lignes une à une est impossible ; il faut plutôt limiter le poids des valeurs extrêmes (lab, cellules 60, 62 et 66).

**Les erreurs de saisie plus discrètes sont indétectables.** Un « 100 » ajouté devant un montant saute aux yeux ; un chiffre inversé ou un montant faussé de quelques centaines de NT\\$ se fond au contraire dans les montants ordinaires. Rien ne permet de distinguer une telle erreur d'un paiement réel : ce type d'erreur ne peut pas être repéré, et donc pas être nettoyé. Il fait partie du bruit que les données gardent quoi qu'on fasse.
""")

st.subheader("4. Des valeurs négatives")
st.markdown(f"""
Aucun paiement n'est négatif (le minimum est 0), mais environ 2 % des factures le sont chaque mois (3.1). Une facture négative est un **solde créditeur** : la banque doit de l'argent au client. Trois situations se distinguent :
- **un remboursement supérieur au dû** : les 692 clients qui paient alors qu'aucune facture n'était due ont, pour la plupart, simplement trop remboursé, et leur facture suivante devient négative (lab, cellules 51 et 53). C'est cohérent avec un paiement en espèces au comptoir, souvent d'un montant arrondi, ou avec un paiement fait avant l'enregistrement du précédent ;
- **un solde créditeur qui dort** : 63 clients ont une facture négative et identique sur les 6 mois, dont 48 sans aucun paiement (lab, cellules 190 et 191). C'est un avoir resté sur un compte inactif, sans aucune dette envers la banque (lab, cellule 194) ;
- **un solde créditeur qui varie** : le client continue d'utiliser sa carte, son solde repasse ensuite au-dessus de zéro ; ce sont des clients actifs (lab, cellule 196).

Ces situations sont plausibles : les factures négatives sont conservées. Elles n'entrent simplement pas dans le ratio de paiement, calculé seulement quand une facture est due.
""")

st.info("""
**Ce que révèlent les montants** : très peu d'erreurs franches (4 paiements géants, quelques montants probablement mal saisis, les erreurs plus discrètes restant indétectables), et surtout des comportements réels de l'époque : paiements en avance ou en retard, remboursements supérieurs au dû, soldes créditeurs, usage intensif de la carte. Plutôt que de supprimer ces clients, il faut limiter l'influence des valeurs extrêmes. Les règles retenues sont détaillées en 3.3.
""")


