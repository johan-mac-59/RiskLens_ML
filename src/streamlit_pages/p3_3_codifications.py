from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 3.3 : LES CODIFICATIONS
# Résultats repris des notebooks d'origine, calculés sur les données d'origine
# (30 000 clients, avant toute correction des codifications) ; source citée à chaque fois.
# Lecture des colonnes (page 1.2) : PAY_n juge la facture BILL_AMTn sur le paiement du mois suivant PAY_AMT(n-1).
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/src"

entete_partie_3()

st.markdown("---")
st.header("3.3 Les codifications : une étiquette de la banque, à lire avec les paiements", anchor="codifications")
st.markdown(f"""
Les codifications posent deux problèmes face à leur documentation :
- **-2 et 0 n'y figurent pas**, alors qu'ils sont parmi les plus fréquents (page « 3.1 Audit ») ;
- **la codification 1 y figure, mais ne représente pas ce que la documentation annonce** : présentée comme un retard d'un mois, elle n'est presque jamais posée d'avril à août, puis concerne 12 % des clients en septembre, sans correspondre à aucune situation de paiement.

Pour savoir ce que la banque a voulu dire, chaque codification est confrontée à la facture qu'elle juge et au paiement fait le mois suivant (page « 1. Les données », section 1.2). Toutes les analyses portent sur les **données d'origine**, avant toute correction : l'EDA_lab ([05_01_EDA_lab.ipynb]({GH}/05_01_EDA_lab.ipynb), partie « Les codifications face aux factures et aux paiements » et partie « Les ratios de paiement ») et l'étude de la codification 1, EDA_codification1 ([05_04_EDA_codification1.ipynb]({GH}/05_04_EDA_codification1.ipynb)).

Lues avec le bon paiement, la plupart des incohérences apparentes disparaissent : les codifications décrivent le paiement du client. Il reste deux vraies questions, qui ont chacune donné un niveau du nettoyage.
""")

# ------------------------------------------------------------------------------
st.subheader("1. -2, -1 et 0 : ce que disent les montants", anchor="sains")
st.markdown("Pour chaque codification saine, la facture qu'elle juge et la part de cette facture payée le mois suivant (EDA_lab, cellules 22, 24, 86 et 116 ; avril à août, mois où le paiement suivant est connu) :")
st.dataframe(pd.DataFrame({
    "Codification": ["-2", "-1", "0"],
    "La facture du mois": ["Absente (nulle ou négative) dans 56 à 71 % des cas selon le mois", "Modeste : 9 000 à 11 000 NT$ en moyenne", "Importante : 58 000 à 75 000 NT$ en moyenne"],
    "Part payée le mois suivant, quand une facture est due": ["100 % (médiane) : facture soldée", "100 % (médiane) : facture soldée", "4,9 % (médiane) ; la moitié des factures entre 3,7 et 9,5 %"],
}), hide_index=True, width="stretch")
st.markdown("""
- **-2** : un mois sans facture, ou une facture soldée le mois suivant. Les deux réunis couvrent 97 à 98 % des -2 d'avril à août (97 % en août) : le client n'a pas de crédit à rembourser.
- **-1** : une facture modeste, soldée le mois suivant. C'est bien le « paiement à temps » de la documentation.
- **0** : une grosse facture, payée en partie, le plus souvent autour de la mensualité minimale (3 à 5 %). C'est le **crédit renouvelable en cours**, le cas le plus courant.

-2 et 0 sont absents de la documentation, mais pas des erreurs : ils décrivent deux façons de se servir de sa carte.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Quand la banque pose et lève un retard", anchor="retard")
st.markdown("Pour les factures de mai à août, la part payée le mois suivant, et ce que la banque en a fait : la mise en retard d'un client sain le mois précédent, et la sortie du retard d'un client déjà en retard (EDA_lab, partie « Les ratios de paiement », cellules 92 et 107 ; codifications 1 écartées) :")
# Parts reprises de l'EDA_lab, cellules 92 (clients sains le mois précédent) et 107 (clients en retard le mois précédent)
tranches = ["Rien payé", "Moins de 3 %", "3 à 5 %", "5 à 10 %", "10 à 20 %", "20 à 30 %", "30 à 40 %",
            "40 à 50 %", "50 à 60 %", "60 à 70 %", "70 à 80 %", "80 à 90 %", "90 % et plus"]
mis_en_retard = [72.2, 16.4, 0.6, 0.9, 0.8, 0.2, 0.6, 0.3, 0.6, 1.2, 0.8, 0.6, 0.1]
nb_sains = [5302, 3798, 27683, 14948, 6926, 2503, 1330, 932, 776, 491, 369, 320, 26120]
sortie = [0.1, 1.8, 2.1, 39.6, 52.0, 57.8, 64.9, 58.6, 48.5, 50.0, 46.3, 71.4, 97.9]
nb_retard = [3644, 449, 2419, 3307, 2031, 510, 188, 116, 101, 34, 41, 56, 862]
fig_retard = go.Figure()
fig_retard.add_trace(go.Bar(x=tranches, y=mis_en_retard, name="Client sain : mis en retard", marker_color=COULEURS_CODIF["2 et plus"],
                            customdata=nb_sains, hovertemplate="%{x}<br>Mis en retard : %{y:.1f} %<br>%{customdata} factures<extra></extra>"))
fig_retard.add_trace(go.Bar(x=tranches, y=sortie, name="Client en retard : sort du retard", marker_color=COULEURS_CODIF["-1"],
                            customdata=nb_retard, hovertemplate="%{x}<br>Sort du retard : %{y:.1f} %<br>%{customdata} factures<extra></extra>"))
fig_retard.update_layout(barmode="group", height=460, xaxis_title="Part de la facture payée le mois suivant",
                         yaxis_title="Part des factures (%)", yaxis_range=[0, 100],
                         legend=dict(orientation="h", y=1.12), margin=dict(t=60))
st.plotly_chart(fig_retard, width="stretch")
st.caption("Clients sains le mois précédent : 91 498 factures ; clients en retard le mois précédent : 13 758 factures. Les tranches de moins de 100 factures sont moins fiables.")
st.markdown(f"""
- **Ne rien payer fait tomber en retard** ; dès la mensualité minimale (3 % de la facture), un client sain n'est presque jamais mis en retard.
- **Solder sa facture fait sortir du retard** presque à chaque fois. Entre les deux, environ un client sur deux en sort ; payer seulement la mensualité ne suffit pas à rattraper l'arriéré.
- **La codification avance d'un cran par mois au plus** : un client sain ne passe jamais directement à 3, et un retard ne saute jamais de cran ([01_01_audit.ipynb]({GH}/01_01_audit.ipynb), partie « Temporalité des colonnes »). La banque met donc ses codifications à jour chaque mois.

La frontière est nette : la codification de retard suit le paiement de la facture.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Une règle plus souple d'avril à juin", anchor="tolerance")
st.markdown("Le même comportement ne donne pourtant pas toujours le même résultat. Parmi les clients sains qui ne paient rien de leur facture le mois suivant, part mise en retard selon le mois (EDA_lab, partie « Les ratios de paiement », cellule 109) :")
st.dataframe(pd.DataFrame(
    [["43,5 %", "63,3 %", "98,3 %", "98,4 %"]],
    columns=["Mai", "Juin", "Juillet", "Août"], index=["Client sain, rien payé : mis en retard"]
), width="stretch")
st.markdown("""
- **En juillet et en août, la règle est stricte** : presque tous les impayés sont mis en retard, dès 100 NT$ de facture (EDA_lab, partie « Les codifications face aux factures et aux paiements », cellule 32). Un paiement de moins de 1,5 % de la facture, ou de moins de 1 000 NT$, est presque toujours mis en retard ; pour rester sain dans 98 % des cas, il faut payer environ 3 % de la facture (EDA_lab, cellules 98 et 105).
- **En avril, mai et juin, la banque est plus souple** : une grande partie des impayés reste codifiée saine, d'autant plus que la facture est petite, et payer environ 1,5 % de la facture suffit à rester sain.
""")
st.markdown("**En juillet-août, le montant payé compte aussi.** Parmi les clients sains le mois précédent qui paient entre 3 et 10 % de leur facture (assez, en part de la facture), part mise en retard selon le montant payé (EDA_lab, cellule 105 ; factures d'au moins 100 NT$) :")
# Regroupement des tranches « 3 à 5 % » et « 5 à 10 % » du tableau juillet-août de l'EDA_lab, cellule 105 (moyenne pondérée par le nombre de factures)
st.dataframe(pd.DataFrame({
    "Montant payé": ["Moins de 1 000 NT$", "1 000 NT$ pile", "1 001 à 1 500 NT$", "Plus de 1 500 NT$"],
    "Factures": [34, 224, 2681, 18315],
    "Mis en retard": ["97,1 %", "26,3 %", "1,5 %", "0,4 %"],
}), hide_index=True, width="stretch", column_config={"Factures": st.column_config.Column(alignment="left")})
st.caption("Pourcentages calculés en regroupant les tranches « 3 à 5 % » et « 5 à 10 % » de part payée du tableau juillet-août de la cellule 105.")
st.markdown("""
En juillet-août, il faut donc payer à la fois une part de la facture (au moins 1,5 % environ) et un montant d'au moins 1 000 NT$, ou la facture entière si elle est plus petite ; entre 1 000 et 1 500 NT$, c'est une zone grise. En mai-juin, ce plancher n'existe pas : seule la part payée compte. Le plancher ne touche que quelques centaines de factures, car presque tous les clients qui paient 3 % ou plus de leur facture paient aussi plus de 1 000 NT$.

La banque a donc resserré sa règle en juillet, en pleine crise, en part comme en montant. Pour un modèle, le même comportement (ne pas payer) donnerait un retard en août mais pas en mai.

**Règle retenue (niveau 3 du nettoyage)** : d'avril à juin, une facture positive payée à moins de 1,5 % le mois suivant, chez un client codifié -1, 0 ou 1 ce mois-là et -1 ou 0 le mois précédent, est codifiée 2, comme le fait la banque à partir de juillet. Le seuil de 1,5 % est celui que la banque appliquait déjà avant juillet, sans le plancher de 1 000 NT$, qui n'existait pas encore. Exception : après un -2, la banque accepte un paiement différé de plus d'un mois sans poser de retard (EDA_lab, cellule 102) ; ces clients ne sont pas touchés.

Les retards posés sur une facture nulle ne sont pas, eux, des anomalies : ce sont tous de nouveaux retards, suivis d'une facture et d'un retard qui continue le mois suivant. Le client se ressert de sa carte et ne paie pas (EDA_lab, cellules 29 et 30).
""")

# ------------------------------------------------------------------------------
st.subheader("4. La codification 1, un code d'attente du paiement d'octobre", anchor="codification-1")
st.markdown(f"""
La documentation présente la codification 1 comme un retard d'un mois. Pourtant, elle n'existe presque qu'en septembre, et elle ne dit rien du paiement : ce n'est pas une situation du client, mais une décision que la banque n'a pas encore prise. Part des clients codifiés 1 et des clients en retard, mois par mois ([01_01_audit.ipynb]({GH}/01_01_audit.ipynb), cellule 9) :
""")
# Parts (%) reprises de 01_01_audit, cellule 9 (30 000 clients) ; 2 et plus = 100 - (-2, -1, 0 et 1)
mois_1 = ["Avril", "Mai", "Juin", "Juillet", "Août", "Septembre"]
part_1 = [0.00, 0.00, 0.01, 0.01, 0.09, 12.29]
part_retard = [round(100 - sum(v), 2) for v in zip([16.32, 15.15, 14.49, 13.62, 12.61, 9.20], [19.13, 18.46, 18.96, 19.79, 20.17, 18.95],
                                                   [54.29, 56.49, 54.85, 52.55, 52.43, 49.12], part_1)]
fig_1 = go.Figure()
fig_1.add_trace(go.Bar(x=mois_1, y=part_retard, name="En retard (2 et plus)", marker_color=COULEURS_CODIF["2 et plus"],
                       text=[f"{v:.1f} %".replace(".", ",") for v in part_retard], textposition="outside"))
fig_1.add_trace(go.Bar(x=mois_1, y=part_1, name="Codifiés 1", marker_color=COULEURS_CODIF["1"],
                       text=[f"{v:.1f} %".replace(".", ",") if v >= 1 else "" for v in part_1], textposition="outside"))
fig_1.update_layout(barmode="group", height=420, xaxis_title="Mois", yaxis_title="Part des clients (%)", yaxis_range=[0, 18],
                    legend=dict(orientation="h", y=1.12), margin=dict(t=60))
st.plotly_chart(fig_1, width="stretch")
st.caption("D'avril à août, la codification 1 concerne au plus 0,09 % des clients (28 clients en août).")
st.markdown(f"""
La codification de septembre (`PAY_1`) juge la facture de fin septembre sur le paiement d'octobre, absent du dataset. Si les données ont été extraites avant que ce paiement soit traité, la banque ne pouvait pas encore trancher : le 1 marque cette attente (EDA_codification1, sections 1, 2 et 6).
- **D'avril à août, personne ne passe par 1** : un client sain reste sain ou passe directement en retard, un client en retard en sort ou y reste. En septembre, le 1 prend la place **à la fois de sorties du retard et de retards maintenus**.
- **Deux sortes de 1** : après un retard en août, la facture reste due et la question est ouverte (le client sort-il du retard ?) ; après un mois sain, le 1 porte surtout sur des clients **sans facture de septembre**, pour qui il n'y a presque rien à juger.

**Une étude complète les remplace (niveau 2 du nettoyage)** : chaque 1 reçoit la codification que la banque aurait posée, d'après l'EDA_codification1 et les modèles de [02_02_modele_sorties_retard.ipynb]({GH}/02_02_modele_sorties_retard.ipynb). Les quelques 1 d'avril à août sont tranchés avec le paiement du mois suivant ; en septembre, un 1 après un mois sain reprend la codification d'août, et un 1 après un retard est estimé, sortie ou retard maintenu, par trois modèles appris sur les clients que la banque a tranchés. La codification de la banque reste conservée à part (`PAY_1_original`). Cette codification de septembre corrigée est une **estimation**, pas la décision de la banque.
""")

# ------------------------------------------------------------------------------
st.subheader("5. Des retards figés", anchor="retards-figes")
st.markdown("""
Un client qui ne paie pas voit son retard monter d'un cran chaque mois. Pourtant, **530 clients restent codifiés 2 pendant les 6 mois**, qu'ils paient un peu ou rien du tout (EDA_lab, partie « Les retards sur les six mois », cellule 130). La codification semble décrochée du paiement, comme si ces clients étaient gérés hors du circuit normal, par exemple par un service de recouvrement. Ces clients, avec tous ceux dont le retard s'installe, sont étudiés dans la partie 5, consacrée à la population en incident.
""")

st.info("""
**Ce que révèlent les codifications** : lues avec la facture qu'elles jugent et le paiement du mois suivant, elles décrivent le comportement du client : -2 pas de crédit à rembourser, -1 une facture soldée, 0 un crédit renouvelable, 2 et plus un impayé. Deux points demandent une correction : la banque a été plus souple d'avril à juin qu'à partir de juillet (niveau 3), et la codification 1 attend en septembre un paiement d'octobre que le dataset ne contient pas (niveau 2). Les règles qui en découlent sont détaillées sur la page « 3.5 Décisions ».
""")
