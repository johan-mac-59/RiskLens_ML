from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 3.3 : LES CODIFICATIONS
# Résultats repris des notebooks d'origine, calculés sur les données d'origine
# (avant toute correction des codifications) ; source citée à chaque fois.
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/src"
CTX = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/contexte.md"

entete_partie_3()

st.markdown("---")
st.header("3.3 Les codifications : une étiquette de la banque, à lire avec les paiements", anchor="codifications")
st.markdown(f"""
La documentation ne dit rien de -2 et 0, et la codification 1 se comporte étrangement. Pour leur donner un sens, on les confronte aux montants dus et payés, puis à l'historique des clients. Toutes les analyses portent sur les **données d'origine**, avant toute correction des codifications : l'EDA_lab ([05_01_EDA_lab.ipynb]({GH}/05_01_EDA_lab.ipynb), 29 996 clients, sans les 4 paiements géants) et l'étude de la codification 1, EDA_codification1 ([05_04_EDA_codification1.ipynb]({GH}/05_04_EDA_codification1.ipynb), sections 1 à 3, 30 000 clients).
""")

st.subheader("Ce que l'on constate")
st.markdown(f"""
En rassemblant l'audit, l'EDA_lab, l'étude de la codification 1 et celle du contentieux, les codifications de paiement présentent toute une série d'incohérences :
- **des codifications absentes de la nomenclature officielle sont massivement employées** : 0 est la plus fréquente de toutes, et -2 concerne entre 9 et 16 % des clients selon le mois (voir la page « 3.1 Audit », graphique des codifications par mois) ;
- **la codification 1, censée signaler un retard d'un mois, n'apparaît presque qu'en septembre**, le dernier mois : 12 % des clients ce mois-là, quasiment aucun avant (EDA_codification1, section 1) ;
- **des retards sont posés alors qu'aucune facture n'était due** (EDA_lab, cellule 115), et ces faux retards arrivent presque toujours par deux mois consécutifs ([05_02_EDA_contentieux.ipynb]({GH}/05_02_EDA_contentieux.ipynb), section 3.2) ;
- **à l'inverse, deux mois sans aucun paiement, alors que des factures étaient dues, laissent environ 3 clients sur 10 en codification saine** (EDA_lab, cellules 150 et 151) ;
- **des clients restent codifiés en retard après avoir payé**, et ne sortent du retard que le mois suivant (EDA_lab, cellules 92 à 96) ;
- **des codifications de retard supérieures à 2 redescendent à 2 sans aucun paiement**, alors qu'une facture était due : 393 clients sont concernés, soit 1,31 % (EDA_lab, cellules 138 et 154) ;
- **des codifications restent figées à 2 pendant les 6 mois** chez 530 clients (1,77 %), que le client paie ou non (EDA_lab, cellule 136).

Une codification de retard devrait suivre la dette du client. Ces constats montrent qu'elle ne le fait pas toujours : il faut comprendre ce qu'elle mesure vraiment.
""")

st.subheader("Comment une banque codifiait un retard en 2005")
st.markdown(f"""
Une codification n'est pas un fait brut : c'est une **étiquette posée par le système d'information de la banque**, à un moment donné ([contexte du projet]({CTX})) :
- chaque mois, la banque arrête un **relevé** : la facture, le paiement reçu, et une codification de paiement ;
- les paiements arrivant de nombreux canaux (supérettes, distributeurs, guichets, poste), les flux étaient **rapprochés en fin de mois par des traitements par lots** ;
- une hypothèse de travail en découle : la codification du dernier mois (`PAY_1`) viendrait d'une table de gestion « à chaud », encore en cours de traitement, tandis que celles des mois plus anciens (`PAY_2` à `PAY_6`) viendraient d'historiques déjà mis au propre. Si c'est le cas, `PAY_1` n'a pas tout à fait le même sens que les autres mois.
""")

# ------------------------------------------------------------------------------
st.subheader("Avant de lire les codifications : comment les clients paient-ils leur facture ?")
st.markdown("""
Le **ratio de paiement** compare, chaque mois, le montant payé à la facture qu'il règle. Il est **écrêté à 200 %** : tous les ratios supérieurs, dus le plus souvent à de très petites factures (voir la page « 3.2 Les montants »), sont regroupés dans la dernière tranche. Sa répartition montre comment les clients utilisent leur carte, et chaque barre est découpée selon la codification posée par la banque ce mois-là. Calcul fait sur les 30 000 clients des données d'origine, pour les 130 561 mois où une facture était due (de M-1 à M-5), avec la définition du ratio de l'EDA_lab ; aucun notebook ne donnant ce découpage par tranche, les comptages sont écrits ici directement.
""")
# Comptages calculés sur creditcard_pret_ingestion (données d'origine, codifications non corrigées) :
# ratio = PAY_AMTn / BILL_AMT(n+1) x 100 quand BILL_AMT(n+1) > 0, n = 1 à 5 ; tranches de ratio x codification PAY_n
tranches_ratio = ["0 %", "0 à 5 %", "5 à 10 %", "10 à 20 %", "20 à 50 %", "50 à 90 %", "90 à 110 %", "110 à 200 %", "200 % (écrêté)"]
mois_par_codif = {
    "-2": [55, 165, 49, 50, 79, 61, 8109, 365, 183],
    "0": [2749, 36564, 17692, 8565, 5431, 1608, 3683, 294, 114],
    "-1": [2062, 1202, 434, 353, 674, 800, 18064, 738, 240],
    "1": [1047, 382, 245, 124, 48, 7, 577, 69, 36],
    "2 et plus": [5205, 5620, 3439, 1471, 566, 208, 1016, 83, 35],
}
couleurs_codif = COULEURS_CODIF
totaux = [sum(v[i] for v in mois_par_codif.values()) for i in range(len(tranches_ratio))]

onglet_nb, onglet_part = st.tabs(["Nombre de mois", "Part de chaque codification"])
for onglet, en_part in ((onglet_nb, False), (onglet_part, True)):
    fig_ratio = go.Figure()
    for codif, valeurs in mois_par_codif.items():
        y = [v / tot * 100 for v, tot in zip(valeurs, totaux)] if en_part else valeurs
        fig_ratio.add_trace(go.Bar(x=tranches_ratio, y=y, name=codif, marker_color=couleurs_codif[codif]))
    fig_ratio.update_layout(barmode="stack", height=460, xaxis_title="Ratio de paiement du mois",
                            yaxis_title="Part des mois (%)" if en_part else "Nombre de mois",
                            legend_title="Codification", margin=dict(t=30))
    with onglet:
        st.plotly_chart(fig_ratio, width="stretch", key=f"ratio_{en_part}")

st.markdown("""
**Lecture croisée :**
- **Deux comportements dominent** : payer une toute petite partie de sa facture (moins de 5 %, un mois sur trois), ou la payer en totalité (90 à 110 %, un mois sur quatre). Les paiements intermédiaires sont plus rares. Le premier comportement est celui du crédit renouvelable, où la mensualité minimale ne couvre guère plus que les intérêts ; le second, celui d'un client qui utilise sa carte comme un moyen de paiement et règle tout chaque mois.
- **Les paiements partiels sont presque tous codifiés 0** (environ 80 % des mois entre 0 et 50 % payés), et **les paiements complets presque tous -1 ou -2** (plus de 8 mois sur 10 entre 90 et 110 %).
- **Quand rien n'est payé**, les codifications de retard (2 et plus) ne représentent qu'un peu moins de la moitié des mois : on y trouve aussi des 0, des -1 et des 1. Inversement, un millier de mois soldés restent codifiés en retard.

C'est sur ces tranches de ratio, et en particulier sur les seuils de 0 % et de 90 %, que s'appuient les analyses suivantes.
""")

st.subheader("1. -2, -1 et 0 : ce que disent les montants")
st.markdown("""
Pour chaque codification, on regarde comment la facture due a été payée (EDA_lab, cellule 87, tous les mois de M-1 à M-5) :
""")
st.dataframe(pd.DataFrame({
    "Codification": ["-2", "-1", "0"],
    "Mois observés": [6114, 17993, 59085],
    "Facture payée à 90 % ou plus": ["94,1 %", "77,7 %", "4,2 %"],
    "Facture payée au centime près": ["45,5 %", "39,6 %", "1,9 %"],
}), hide_index=True, width="stretch", column_config={"Mois observés": st.column_config.Column(alignment="left")})
st.markdown("Le montant de la facture va dans le même sens : en septembre, la facture moyenne due est de 8 620 NT\\$ pour un client codifié -2, 10 927 NT\\$ pour -1, et 74 243 NT\\$ pour 0 (EDA_lab, cellule 19).")
st.markdown("""
Les profils se séparent nettement :
- **-2** : une facture faible, presque toujours soldée. Quand on ajoute les mois sans aucune facture due, **94 à 99 % des -2** correspondent à un client qui n'avait rien à payer ou qui a tout payé (EDA_lab, cellule 110).
- **-1** : une facture modeste, le plus souvent soldée dans le mois. C'est bien le « paiement à temps » de la documentation. L'idée d'un -1 qui signalerait un paiement différé d'un mois ne tient que pour une petite minorité de cas (EDA_lab, cellules 87 à 90).
- **0** : une facture importante, presque jamais soldée. Le client paie une partie de sa dette : **95 % des mois avec un paiement partiel sont codifiés 0** (EDA_lab, cellule 89). Le 0 correspond au **crédit renouvelable en cours**, le cas le plus courant pour une carte de crédit.

-1 et -2 restent difficiles à distinguer : ils décrivent tous deux des clients qui paient au comptant. Leur différence relève peut-être d'une classification interne de la banque (EDA_lab, cellule 91).
""")

# ------------------------------------------------------------------------------
st.subheader("2. La codification 1, un statut provisoire du dernier mois", anchor="codification-1")
st.markdown(f"""
Cette codification a fait l'objet d'une étude à part entière, l'EDA_codification1 ([05_04_EDA_codification1.ipynb]({GH}/05_04_EDA_codification1.ipynb)), dont les résultats sont repris ci-dessous.

La documentation présente la codification 1 comme un retard d'un mois. Pourtant, elle n'existe presque qu'en septembre, le dernier mois (EDA_codification1, section 1) :
""")
st.dataframe(pd.DataFrame(
    [["0,00 %", "0,00 %", "0,01 %", "0,01 %", "0,09 %", "12,29 %"]],
    columns=["Avril", "Mai", "Juin", "Juillet", "Août", "Septembre"], index=["Clients codifiés 1"]
), width="stretch")
st.markdown("""
L'historique montre ce qu'elle remplace. D'avril à août, un client sain passe directement en retard (2 ou plus), et un client en retard revient à une codification saine ou reste en retard : **jamais de passage par 1**. En septembre, la codification 1 prend la place **à la fois de sorties de retard et de retards maintenus**, que l'historique tranchera le mois suivant (EDA_codification1, section 1 : tableaux qui suivent les clients d'un mois à l'autre, selon leur codification du mois précédent).

Les codifications 1 de septembre forment **deux familles**, à parts presque égales (EDA_codification1, sections 2 et 3) :
""")
st.dataframe(pd.DataFrame({
    "Famille": ["1 après une codification saine", "1 après un retard"],
    "Clients": [1836, 1824],
    "Facture de septembre nulle": ["62,9 %", "0,0 %"],
    "Encours de septembre nul": ["91,9 %", "0,1 %"],
    "Facture de M-1 payée à 90 % ou plus": ["36,5 %", "0,1 %"],
}), hide_index=True, width="stretch")
st.markdown("""
- **Après une codification saine**, le client n'avait le plus souvent rien à payer : la codification 1 ressemble à une **alerte ou à un statut posé sur un compte sans dette**.
- **Après un retard**, une dette reste due, et elle n'est presque jamais soldée : c'est un **statut d'attente**, avant que la banque ne tranche entre la sortie et le maintien du retard.

L'hypothèse d'un paiement fait en supérette mais pas encore comptabilisé a été testée : **aucune trace ne la confirme**, les clients codifiés 1 n'ont pas plus de paiements que les autres clients en retard (EDA_codification1, section 3). La piste la plus solide reste celle d'un `PAY_1` encore « à chaud ».

**Exemple parlant, le client 6783** : il paie chaque mois une partie de sa facture, comme les clients codifiés 0, mais reste codifié 1 sur 4 mois, y compris en dehors de septembre.

**Malgré ces analyses poussées, la codification 1 reste inexpliquée.** On sait où elle apparaît, quand, et ce qu'elle remplace, mais pas ce qu'elle signifie pour la banque : aucune des hypothèses testées (retard d'un mois, alerte, paiement pas encore enregistré, statut d'attente) ne l'explique entièrement. Pour la plupart des codifications 1 posées après un retard, rien dans le dataset ne permet de dire si le client sortira du retard ou y restera : leur vraie situation ne peut pas être déterminée (EDA_codification1, conclusion).

**Inexpliquée, mais pas insignifiante : elle a un sens pour la banque.** Les 3 688 clients codifiés 1 en septembre ont un taux de défaut d'environ 34 %, contre 22 % pour l'ensemble des clients, soit environ 12 points de plus. Le signal vient surtout des codifications 1 posées après un retard (42,5 % de défaut), alors qu'une codification 1 posée sur un client sain qui a une dette ne signale pas de risque particulier (9,5 %). La banque ne l'attribue donc pas au hasard, même si le dataset ne permet pas de savoir ce qu'elle désigne exactement (EDA_codification1, annexe « taux de défaut des codes 1 selon l'encours de M-1 », données d'origine ; taux descriptifs, qui ne servent à fixer aucune règle).
""")

# ------------------------------------------------------------------------------
st.subheader("3. Un mois de décalage entre paiement et mise à jour", anchor="decalage")
st.markdown("""
Quand un client en retard paie, sa codification change-t-elle le mois même, ou le mois suivant ? On part des clients en retard le mois précédent, et on regarde leur codification le mois du paiement, puis le mois d'après, selon la part de la facture payée (EDA_lab, cellule 93 ; 12 420 mois étudiés, codifications 1 exclues) :
""")
tranches = ["0 %", "0 à 3 %", "3 à 5 %", "5 à 10 %", "10 à 20 %", "20 à 50 %", "50 à 90 %", "90 % et plus"]
nb_cas = [6431, 856, 2419, 1742, 654, 180, 86, 52]
sortie_meme = [40.2, 46.1, 19.3, 13.8, 10.2, 13.9, 14.0, 19.2]
sortie_suivant = [46.1, 52.2, 24.8, 26.6, 32.3, 47.8, 64.0, 76.9]
fig_dec = go.Figure()
fig_dec.add_trace(go.Bar(x=tranches, y=sortie_meme, name="Sortie du retard visible le mois du paiement", marker_color=COULEURS["rouge_pale"]))
fig_dec.add_trace(go.Bar(x=tranches, y=sortie_suivant, name="Sortie du retard visible le mois suivant", marker_color=COULEURS["mauve"],
                         text=[f"{n} cas" for n in nb_cas], textposition="outside"))
fig_dec.update_layout(barmode="group", height=460, xaxis_title="Part de la facture payée le mois n",
                      yaxis_title="Clients sortis du retard (%)", yaxis_range=[0, 90],
                      legend=dict(orientation="h", y=1.12), margin=dict(t=60))
st.plotly_chart(fig_dec, width="stretch")
st.markdown("""
- **La sortie du retard se lit surtout le mois suivant le paiement** : à paiement égal, elle est presque toujours plus fréquente un mois plus tard. La codification est mise à jour avec un mois de décalage sur le paiement.
- **Plus le client paie, plus il sort du retard, mais sans frontière nette.** Dès que le ratio de paiement du mois dépasse 5 %, la part des clients sortis du retard le mois suivant augmente à chaque tranche : environ un quart entre 5 et 10 % de ratio, un tiers entre 10 et 20 %, près de la moitié entre 20 et 50 %, deux tiers entre 50 et 90 %. Aucune tranche ne marque un saut brutal : il n'existe pas de montant à partir duquel la sortie serait automatique.
- **Même une facture soldée ne suffit pas toujours.** Avec un ratio de paiement de 90 % ou plus, environ un quart des clients reste codifié en retard le mois suivant. Deux explications sont possibles : un **arriéré plus ancien**, qui reste dû même après le paiement de la facture du mois et que le dataset ne montre pas ; ou un **artefact de codification**, une mise à jour défaillante ou plus tardive encore que le décalage d'un mois.
- **Près de la moitié des clients qui n'ont rien payé ce mois-là sortent quand même du retard** le mois suivant.

Les tranches élevées comptent peu de cas : les pourcentages y sont moins solides (EDA_lab, cellules 96 à 105).
""")

st.markdown("""
**Validation croisée : quel paiement fait sortir du retard ?** Pour les mêmes cas, on calcule la part des clients sortis du retard au mois n (`PAY_n`) de deux façons : selon le ratio de paiement du **mois même** (n), puis selon celui du **mois précédent** (numéroté n+1, les mois du dataset allant du plus récent au plus ancien). Si la codification suit le paiement avec un mois de retard, c'est le paiement du mois précédent qui doit expliquer la sortie. Calcul fait sur les données de l'EDA_lab (29 996 clients), pour les clients en retard le mois précédent avec deux factures dues ; aucun notebook ne présentant ce croisement, les résultats sont écrits ici directement.
""")
# Calcul : départ PAY_(n+1) >= 2, factures BILL_AMT(n+2) > 0 et BILL_AMT(n+1) > 0, n = 1 à 4 ; mois codifiés 1 (PAY_n = 1) exclus.
# Ratio du mois précédent : PAY_AMT(n+1) / BILL_AMT(n+2) ; ratio du mois même : PAY_AMTn / BILL_AMT(n+1) ; sortie : PAY_n <= 0.
tranches_reg = ["0 %", "0 à 10 %", "10 à 50 %", "50 à 90 %", "90 % et plus"]
# Taux de sortie du retard au mois n (PAY_n <= 0) selon chacun des deux ratios, sur les mêmes 12 668 cas
sortie_selon_meme = [34.5, 17.5, 8.4, 29.2, 25.5]
nb_selon_meme = [6211, 5078, 1215, 113, 51]
sortie_selon_prec = [13.9, 22.3, 36.5, 65.8, 79.2]
nb_selon_prec = [4037, 6510, 1162, 152, 807]
fig_reg = go.Figure()
fig_reg.add_trace(go.Bar(x=tranches_reg, y=sortie_selon_meme, name="Selon le ratio de paiement du mois même (n)",
                         marker_color=COULEURS["rouge_pale"], text=[f"{n} cas" for n in nb_selon_meme], textposition="outside"))
fig_reg.add_trace(go.Bar(x=tranches_reg, y=sortie_selon_prec, name="Selon le ratio de paiement du mois précédent (n+1)",
                         marker_color=COULEURS["mauve"], text=[f"{n} cas" for n in nb_selon_prec], textposition="outside"))
fig_reg.update_layout(barmode="group", height=460, xaxis_title="Ratio de paiement",
                      yaxis_title="Clients sortis du retard au mois n (%)", yaxis_range=[0, 95],
                      legend=dict(orientation="h", y=1.12), margin=dict(t=60))
st.plotly_chart(fig_reg, width="stretch")
st.caption("12 668 cas étudiés. Les mois codifiés 1 sont exclus, faute de pouvoir dire s'il s'agit d'un retard ou d'une sortie : 1 791 cas, dont 1 787 en septembre (PAY_1), où cette codification est concentrée. Les tranches de moins de 100 cas sont moins fiables.")
st.markdown("""
- **C'est le paiement du mois précédent qui fait sortir du retard** (barres mauves) : la sortie progresse avec ce paiement : environ 14 % des clients sortent du retard quand ils n'ont rien payé le mois précédent, 37 % entre 10 et 50 % de ratio, 66 % entre 50 et 90 %, et 79 % quand ils ont soldé leur facture.
- **Le paiement du mois même n'explique pas la sortie** (barres rouges) : aucune progression n'apparaît, payer davantage le mois même ne fait pas sortir du retard ce mois-là.
- **Le décalage d'un mois est ainsi démontré** : la codification d'un mois reflète le paiement du mois précédent.

Conclusion pratique : pour juger si un client a payé, **il faut regarder 2 mois de paiement**, jamais un seul.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Des codifications qui ne suivent pas toujours la dette", anchor="dette")
st.markdown("""
Une codification de retard devrait accompagner une dette. Ce n'est pas toujours le cas. **Des retards sont posés alors qu'aucune facture n'était due** (EDA_lab, cellule 115) :
""")
st.dataframe(pd.DataFrame({
    "Mois": ["Septembre (PAY_1)", "Août (PAY_2)", "Juillet (PAY_3)", "Juin (PAY_4)", "Mai (PAY_5)"],
    "Mois sans facture due": [3173, 3525, 3870, 4161, 4708],
    "Codifiés 1": ["37,03 %", "0,34 %", "0 %", "0 %", "0 %"],
    "Codifiés 2": ["1,99 %", "5,05 %", "4,42 %", "2,62 %", "1,30 %"],
}), hide_index=True, width="stretch")
st.markdown("""
À l'inverse, **deux mois de suite sans aucun paiement, alors que des factures étaient dues, ne donnent pas toujours une codification de retard** : sur 1 411 cas, 425 restent codifiés sains (-2, -1 ou 0), soit environ 3 sur 10 (EDA_lab, cellules 150 et 151).

La codification reflète donc ce que la banque a enregistré, au moment où elle l'a enregistré, et pas toujours l'état réel de la dette.
""")

# ------------------------------------------------------------------------------
st.subheader("5. Des retards qui se figent ou redescendent sans paiement", anchor="retards-figes")
st.markdown("""
Logiquement, un client qui ne paie pas voit son retard s'aggraver d'un cran chaque mois ; c'est ce qu'on observe chez une partie des clients. Mais deux comportements ne suivent pas cette logique (EDA_lab, cellules 136 à 154) :
- **393 clients voient leur codification de retard redescendre à 2 sans aucun paiement**, alors qu'une facture était due : le retard diminue sans que la dette ait été réglée ;
- **530 clients restent codifiés 2 pendant les 6 mois**, que le client paie un peu ou rien du tout, alors que leur dette augmente dans la plupart des mois sans paiement.

Dans les deux cas, la codification semble **décrochée du comportement de paiement**, comme si ces clients étaient gérés en dehors du circuit normal, par exemple par un service de recouvrement. Le dataset ne permet pas de le vérifier directement. Ces clients sont étudiés plus en détail dans l'analyse exploratoire (page « 4.6 Les clients figés en retard »), puis dans la définition de la population contentieuse (partie 5).
""")

st.info("""
**Ce que révèlent les codifications** : derrière des nombres sans documentation se cachent des comportements cohérents. -2 et -1 décrivent des clients qui paient au comptant, 0 un crédit renouvelable en cours. Mais la codification est une étiquette du système d'information : la codification 1 est un statut provisoire du dernier mois, la mise à jour suit le paiement avec un mois de décalage, certaines codifications ne correspondent pas à la dette réelle, et d'autres se figent ou redescendent sans paiement. Pour juger du risque, il faut donc lire les codifications avec les montants et sur plusieurs mois. Les règles qui en découlent sont détaillées sur la page « 3.5 Décisions ».
""")
