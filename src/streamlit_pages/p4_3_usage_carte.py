from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 4.3 : LE TYPE D'USAGE DE LA CARTE (COMPTANT OU CRÉDIT)
# Analyses reprises du notebook storytelling (cellules 77 et 82), refaites en Plotly ;
# tous les chiffres sont calculés en direct sur le dataset.
# ==============================================================================
df = load_data()
taux_moyen = df["dpnm"].mean() * 100

# ratio_PAY_BILL_global, ratio_PAY_BILL_median, TYPE_USAGE, ratio_PAY_BILL_regularite et PAY_habituel sont lues dans le CSV :
# créées par 05_03_EDA_storytelling avant l'export (définitions dans docs/colonnes_creees.md)
ratio_columns = [f'ratio_PAY_BILL{i}' for i in range(1, 6)]

# Les graphiques n'affichent que les médianes de 0 et plus
sans_facture_sept = int((df['ratio_PAY_BILL_median'] == -1).sum())
sans_facture = sans_facture_sept + int(df['ratio_PAY_BILL_median'].isna().sum())
df_ratio = df[df['ratio_PAY_BILL_median'] >= 0].copy()
# Nombre de mois avec une facture due sur lesquels repose la médiane de chaque client
nb_mois_ratio = ratios_affichables(df, ratio_columns).notna().sum(axis=1)
peu_de_mois = int((nb_mois_ratio == 2).sum())

# Types d'usage : colonne TYPE_USAGE (tranches tirées de la forme de la répartition des ratios de paiement : pic net à 3-5 %,
# décroissance régulière jusque vers 30 %, zone clairsemée de 30 à 99 %, paiement complet concentré autour de 100 % ;
# jamais du taux de défaut). Les libellés ci-dessous servent à l'affichage et doivent rester ceux de la colonne
RIEN, DIFFICULTE, MENSUALITE, MIXTE, ELEVE, COMPTANT, AUTRE = (
    "Ne paie rien", "Client en difficulté", "Crédit par mensualité", "Usage mixte", "Remboursement élevé", "Paiement comptant",
    "Autre / non mesurable")
TYPES = [
    (RIEN, "0 %"),
    (DIFFICULTE, "moins de 3 %, moins qu'une mensualité"),
    (MENSUALITE, "3 à 6 %"),
    (MIXTE, "6 à 30 %"),
    (ELEVE, "30 à 99 %"),
    (COMPTANT, "99 à 105 %, léger trop-perçu compris"),
    (AUTRE, "une seule facture due, ou argent payé en trop encore sur la carte"),
]
TYPES_MESURES = [nom for nom, _ in TYPES if nom != AUTRE]
df_ratio['type_usage'] = pd.Categorical(df_ratio['TYPE_USAGE'], categories=[nom for nom, _ in TYPES])

stats_type = (
    df_ratio.groupby('type_usage', observed=False)['dpnm']
    .agg(clients='size', taux='mean')
    .reset_index()
)
stats_type['taux'] = stats_type['taux'] * 100
stats_type['part'] = stats_type['clients'] / stats_type['clients'].sum() * 100
# Six types dans la palette habituelle, « Autre / non mesurable » en gris
COULEURS_TYPES = dict(zip(TYPES_MESURES, px.colors.qualitative.Safe)) | {AUTRE: COULEURS["gris"]}

entete_partie_4(df)

st.markdown("---")
st.header("4.3 Le type d'usage de la carte : plus le client rembourse, moins il fait défaut", anchor="usage-carte")
st.markdown("""
Une carte de crédit s'utilise de deux façons : comme un **moyen de paiement**, en réglant toute la facture à l'échéance (paiement comptant), ou comme un **crédit**, en ne remboursant qu'une partie de la facture et en laissant le reste courir, avec des intérêts. La page « 3.3 Les codifications » a montré ces deux comportements mois par mois ; on les regarde ici client par client, pour voir s'ils sont réguliers et s'ils pèsent sur le risque.
""")

# ------------------------------------------------------------------------------
st.subheader("Sur 5 mois, quelle part de sa dette cumulée chaque client rembourse-t-il ?", anchor="remboursement-global")
global_affiche = df.loc[df['ratio_PAY_BILL_global'].notna(), 'ratio_PAY_BILL_global']
fig_global = px.histogram(global_affiche, labels={'value': 'Remboursements cumulés / dette cumulée sur 5 mois (%)', 'count': 'Nombre de clients'})
fig_global.update_traces(xbins=dict(start=0, end=201, size=1), marker_color=COULEURS["turquoise"], marker_line_width=0,
                         hovertemplate="Taux de %{x} % : %{y} clients<extra></extra>")
fig_global.update_layout(xaxis_title="Remboursements cumulés sur 5 mois / dette cumulée sur 5 mois (%)", yaxis_title="Nombre de clients",
                         showlegend=False, height=450)
st.plotly_chart(fig_global, width='stretch')
st.caption("Taux de remboursement global : remboursements cumulés sur 5 mois (paiements de mai à septembre) divisés par la "
           "dette cumulée sur 5 mois (factures d'avril à août), chaque facture impayée reportée dans la suivante n'étant comptée "
           "qu'une fois ; écrêté entre 0 et 200 %. Un solde négatif n'efface aucune dette : c'est un paiement en trop, compté comme tel "
           "seulement s'il est encore sur la carte fin septembre (une avance dépensée ensuite n'est pas un trop-payé). "
           "La facture de septembre, payée en octobre, n'entre pas dans le calcul.")
pic_credit = int(np.floor(global_affiche[global_affiche < 90]).value_counts().idxmax())
part_credit_global = global_affiche.between(10, 30, inclusive="left").mean() * 100
part_solde_global = global_affiche.between(90, 110).mean() * 100
st.markdown(f"""
Avant de regarder mois par mois, une mesure simple résume le comportement de chaque client : ses **remboursements cumulés sur 5 mois**, rapportés à sa **dette cumulée sur 5 mois**, c'est-à-dire la part de tout ce qu'il a dû qu'il a réellement remboursée. Deux groupes se détachent nettement :
- **{nombre_fr(part_solde_global, 1)} %** des clients remboursent la totalité de leur dette cumulée (entre 90 et 110 %) : ils utilisent leur carte comme un moyen de paiement ;
- **{nombre_fr(part_credit_global, 1)} %** en remboursent entre 10 et 30 %, avec un pic vers {pic_credit} % : ils laissent courir leur crédit. Chaque mois, ils ne paient qu'une petite part de leur facture (3 à 5 % le plus souvent, voir plus bas) : cumulés sur 5 mois, ces petits remboursements ne couvrent qu'une fraction de leur dette cumulée.

Cette mesure absorbe le décalage d'un mois des paiements : un client qui règle tout avec un mois de retard arrive bien à 100 %.
""")

# ------------------------------------------------------------------------------
st.subheader("Deux comportements réguliers : rembourser très peu, ou tout rembourser", anchor="deux-usages")
st.markdown("On revient maintenant au **comportement mensuel** du client : non plus ce qu'il a remboursé en cumulé sur 5 mois, "
            "mais la part de sa facture qu'il paie **d'habitude, chaque mois**, mesurée par la médiane de ses ratios de paiement mensuels.")

# Histogramme du ratio de paiement médian par client (repris de la cellule 77, en Plotly)
fig_medianes = px.histogram(
    df_ratio['ratio_PAY_BILL_median'], nbins=100,
    labels={'value': 'Ratio de paiement médian du client (%)', 'count': 'Nombre de clients'},
)
# Grain de 1 % : une barre par point de pourcentage, de 0 à 200 %
fig_medianes.update_traces(xbins=dict(start=0, end=201, size=1), marker_color=COULEURS["turquoise"], marker_line_width=0,
                           hovertemplate="Ratio médian de %{x} % : %{y} clients<extra></extra>")
fig_medianes.update_layout(xaxis_title='Ratio de paiement médian du client sur les mois avec une facture due (%)',
                           yaxis_title='Nombre de clients', showlegend=False, height=500)
st.plotly_chart(fig_medianes, width='stretch')
st.caption("Ratio de paiement : montant payé divisé par la facture qu'il règle, écrêté entre 0 et 200 %. Pour chaque client, médiane des mois où une facture était due (définition ci-dessous).")

part_faible = (df_ratio['ratio_PAY_BILL_median'] <= 10).mean() * 100
part_solde = df_ratio['ratio_PAY_BILL_median'].between(99, 105).mean() * 100
# Clients dont la médiane classique (moyenne des deux valeurs du milieu) n'est pas une valeur observée
mediane_classique = ratios_affichables(df_ratio, ratio_columns).median(axis=1)
nb_corriges = int((mediane_classique != df_ratio['ratio_PAY_BILL_median']).sum())
pointe_50_classique = int((mediane_classique == 50).sum())
pointe_50 = int((df_ratio['ratio_PAY_BILL_median'] == 50).sum())
st.markdown(f"""
Les clients ont des **tendances d'usage** nettes : leur comportement habituel se concentre sur deux pics. **{nombre_fr(part_faible, 1)} %** des clients remboursent en général 10 % ou moins de leur facture, et **{nombre_fr(part_solde, 1)} %** la règlent en totalité (entre 99 et 105 %). Les comportements intermédiaires sont rares. Avec un nombre pair de mois, la médiane classique fait la moyenne des deux valeurs du milieu : un client qui alterne un mois sans paiement et un mois soldé, souvent à cause du décalage d'un mois des paiements (page 3.3), obtiendrait 50 %, un comportement qu'il n'a jamais eu. Quand les deux valeurs du milieu diffèrent, on garde donc celle qui est la plus proche de son **taux de remboursement global** (graphique précédent) : tout ce qu'il a payé sur la période, rapporté à tout ce qu'il a dû. La médiane reste ainsi un ratio réellement observé, rattaché au comportement d'ensemble du client. {nombre_fr(nb_corriges)} clients sont concernés ; les clients à 50 % pile passent de {nombre_fr(pointe_50_classique)} à {nombre_fr(pointe_50)}. Ces médianes portent sur les {nombre_fr(len(df_ratio))} clients qui ont eu au moins une facture à payer d'avril à août. Les {nombre_fr(sans_facture)} autres n'ont pas de ratio mesurable et ne sont pas affichés : {nombre_fr(sans_facture_sept)} n'ont qu'une facture en septembre, dont le paiement tombe en octobre, hors période (des comptes qui commencent à servir, médiane fixée à -1), et {nombre_fr(sans_facture - sans_facture_sept)} n'ont eu aucune facture positive sur les 6 mois (page « 4.2 L'usage du crédit »).
""")

st.subheader("Six types d'usage, une catégorie à part, et un comportement plutôt régulier", anchor="regularite")
# Répartition de tous les ratios mensuels (mois avec une facture due) : elle ne dépend pas de la définition de la médiane
ratios_mensuels = pd.concat([df.loc[df[f'BILL_AMT{n + 1}'] > 0, f'ratio_PAY_BILL{n}'] for n in range(1, 6)])
partiels = np.floor(ratios_mensuels[(ratios_mensuels > 0) & (ratios_mensuels < 99)])
une_facture = int(((df_ratio['type_usage'] == AUTRE) & (nb_mois_ratio[df_ratio.index] == 1)).sum())
trop_payes = int(((df_ratio['type_usage'] == AUTRE) & (nb_mois_ratio[df_ratio.index] > 1)).sum())
mediane_haute = df_ratio['ratio_PAY_BILL_median'] > 105
avances_depensees = int((mediane_haute & (df_ratio['type_usage'] == COMPTANT)).sum())
pic = int(partiels.value_counts().idxmax())
part_pic = (partiels == pic).mean() * 100
st.markdown("Chaque client est rangé selon son ratio de paiement médian : " + " ; ".join(f"**{nom}** ({tranche})" for nom, tranche in TYPES[:-1]) + ". "
            "Les tranches ont été posées sur la répartition de **tous les ratios de paiement mensuels**, qui ne dépend pas de la façon "
            f"de calculer la médiane : parmi les paiements partiels, le point le plus fréquent est {pic} % ({nombre_fr(part_pic, 1)} % des mois), "
            "puis la fréquence décroît régulièrement jusque vers 30 %, et la zone de 30 à 99 % est clairsemée. "
            "Le paiement comptant est resserré autour de 100 % : un léger trop-perçu, jusqu'à 105 %, n'a rien de choquant "
            "(un montant arrondi au-dessus de la facture, par exemple). Les tranches ne découlent pas du taux de défaut.")
st.markdown(f"""
Deux cas ne permettent pas de lire une habitude, et sont rangés à part, dans **{AUTRE}** :
- **une seule facture due sur la période** ({nombre_fr(une_facture)} clients) : la médiane n'est alors qu'un paiement isolé ;
- **de l'argent payé en trop, encore sur la carte fin septembre** ({nombre_fr(trop_payes)} clients) : le client paie d'habitude plus que sa facture (médiane de plus de 105 %) **et** son taux de remboursement global le confirme. Avance, erreur de saisie, avoir ? Le dataset ne permet pas de trancher : ce n'est plus l'usage d'une carte de crédit.

À l'inverse, {nombre_fr(avances_depensees)} clients dont la médiane dépasse aussi 105 % restent **au comptant** : leur taux de remboursement global ne dépasse pas 105 %, leurs trop-payés ont été dépensés ensuite ou compensés. Leur habitude est de solder leurs factures, simplement en avance certains mois.
""")

# Seuil de 3 % : part des mois codifiés en retard selon la part de la facture payée dans le mois (codification, pas défaut)
mois = pd.concat([pd.DataFrame({'ratio': df.loc[df[f'BILL_AMT{n + 1}'] > 0, f'ratio_PAY_BILL{n}'],
                                'retard': df.loc[df[f'BILL_AMT{n + 1}'] > 0, f'PAY_{n}'] >= 2}) for n in range(1, 6)])
retard_moins_1 = mois.loc[(mois['ratio'] > 0) & (mois['ratio'] < 1), 'retard'].mean() * 100
retard_3_6 = mois.loc[(mois['ratio'] >= 3) & (mois['ratio'] < 6), 'retard'].mean() * 100
st.markdown(f"Pourquoi 3 % ? Mois par mois, la banque pose un retard dans {nombre_fr(retard_moins_1, 0)} % des mois où le client paie moins de 1 % de sa facture, "
            f"mais dans {nombre_fr(retard_3_6, 0)} % seulement des mois où il en paie 3 à 6 %, une part qui ne baisse plus guère avant le paiement complet. "
            f"Le pic des ratios mensuels, autour de {pic} %, ressemble donc à la **mensualité minimale** acceptée par la banque : c'est une lecture empirique, "
            "aucune source ne donnant le minimum exigé en 2005. En dessous, le client paie moins qu'une mensualité : il est en difficulté.")

# Régularité : colonne ratio_PAY_BILL_regularite lue dans le CSV (créée par 05_03_EDA_storytelling, définie dans
# docs/colonnes_creees.md) ; le nombre de mois dus sert à ne garder que les clients avec au moins 3 mois
mois_dus = ratios_affichables(df_ratio, ratio_columns)
nb_mois_dus = mois_dus.notna().sum(axis=1)
regularite = df_ratio['ratio_PAY_BILL_regularite']
nb_conformes = (regularite * nb_mois_dus / 100).round()
assez = nb_mois_dus >= 3

st.markdown("""
Une médiane résume le comportement habituel d'un client, mais pas sa **régularité** : un client peut payer chaque mois au comptant, ou alterner crédit et comptant et tomber sur la même médiane. Pour le savoir, on compte, pour chaque client, les mois où son ratio de paiement tombe **dans la tranche de son type d'usage**. Le calcul porte sur les clients qui ont au moins 3 mois avec une facture due : avec un ou deux mois, la médiane se confond avec ces mois et la régularité ne dit rien.
""")
# Tableau HTML : les intitulés de colonnes reviennent à la ligne automatiquement
STYLE_CELLULE = "border: 1px solid rgba(128, 128, 128, 0.3); padding: 6px 8px; vertical-align: top; text-align: left;"
entetes = ["Type d'usage", "Nombre de clients (3 mois dus ou plus)", "Part moyenne des mois dans le même type d'usage",
           "Part des clients dont tous les mois avec facture sont dans le même type d'usage",
           "Part des clients dont moins de la moitié des mois avec facture y sont"]
lignes_html = ""
for nom in TYPES_MESURES:
    groupe = regularite[assez & (df_ratio['type_usage'] == nom)]
    valeurs = [nom, nombre_fr(len(groupe)), f"{nombre_fr(groupe.mean(), 1)} %",
               f"{nombre_fr((groupe == 100).mean() * 100, 1)} %", f"{nombre_fr((groupe < 50).mean() * 100, 1)} %"]
    lignes_html += "<tr>" + "".join(f'<td style="{STYLE_CELLULE}">{v}</td>' for v in valeurs) + "</tr>"
st.markdown(
    '<table style="width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 0.5rem;">'
    # Colonnes 1 et 2 plus étroites, pour laisser la place aux intitulés longs des colonnes 3 à 5
    '<colgroup><col style="width: 16%"><col style="width: 14%"><col style="width: 22%"><col style="width: 24%"><col style="width: 24%"></colgroup>'
    "<thead><tr>" + "".join(f'<th style="{STYLE_CELLULE} background: rgba(128, 128, 128, 0.1);">{e}</th>' for e in entetes)
    + f"</tr></thead><tbody>{lignes_html}</tbody></table>",
    unsafe_allow_html=True,
)
st.caption(f"Pour « {RIEN} », la dernière colonne vaut 0 % par construction : quand la médiane vaut 0 %, au moins la moitié des mois valent 0 %. "
           f"« {AUTRE} » n'a pas de régularité : il n'y a pas d'habitude à laquelle comparer les mois.")

cinq = nb_mois_dus == 5
part_3_sur_5 = (nb_conformes[cinq] >= 3).mean() * 100
part_5_sur_5 = (nb_conformes[cinq] == 5).mean() * 100
regul = {nom: regularite[assez & (df_ratio['type_usage'] == nom)].mean() for nom in TYPES_MESURES}
# Payeurs au comptant : part de ceux dont tous les mois avec facture sont au comptant, et nature de leurs écarts
comptant = assez & (df_ratio['type_usage'] == COMPTANT)
part_comptant_tous = (regularite[comptant] == 100).mean() * 100
ecarts = mois_dus[comptant].stack()
ecarts = ecarts[(ecarts < 99) | (ecarts > 105)]
part_ecarts_zero = (ecarts == 0).mean() * 100
part_ecarts_trop = (ecarts > 105).mean() * 100
part_ecarts_partiel = 100 - part_ecarts_zero - part_ecarts_trop
st.markdown(f"""
- **Le comportement de paiement est majoritairement récurrent** : parmi les clients qui ont 5 mois avec une facture due, {nombre_fr(part_3_sur_5, 0)} % ont au moins 3 mois sur 5 dans la tranche de leur type d'usage, et {nombre_fr(part_5_sur_5, 0)} % les ont tous.
- **Les comportements nets sont les plus stables** : en moyenne, {nombre_fr(regul[COMPTANT], 0)} % des mois d'un client au paiement comptant restent dans son type d'usage, {nombre_fr(regul[MENSUALITE], 0)} % pour le crédit par mensualité et {nombre_fr(regul[RIEN], 0)} % pour ceux qui ne paient rien. Le paiement comptant reste pourtant une **habitude plus qu'une règle** : {nombre_fr(part_comptant_tous, 0)} % seulement des payeurs au comptant soldent tous leurs mois avec facture ; les autres ont un ou deux mois où ils ne paient pas au comptant. Ces mois-là, ils règlent seulement une partie de leur facture dans {nombre_fr(part_ecarts_partiel, 0)} % des cas, ne paient rien dans {nombre_fr(part_ecarts_zero, 0)} % des cas, et paient plus que leur facture (plus de 105 %) dans {nombre_fr(part_ecarts_trop, 0)} % des cas.
- **Le remboursement élevé et le client en difficulté sont des comportements de passage** ({nombre_fr(regul[ELEVE], 0)} % et {nombre_fr(regul[DIFFICULTE], 0)} % des mois dans leur type d'usage) : ces clients alternent entre plusieurs façons de payer.
""")

# ------------------------------------------------------------------------------
st.subheader("Le type d'usage et le taux de défaut", anchor="defaut-usage")
col_repartition, col_taux = st.columns(2)
with col_repartition:
    st.markdown("#### Répartition des clients")
    fig_types = px.pie(stats_type, names='type_usage', values='clients', color='type_usage', color_discrete_map=COULEURS_TYPES)
    fig_types.update_traces(sort=False, direction="clockwise", textposition="outside", automargin=True,  # marges élargies pour que les étiquettes ne soient pas coupées
                            text=[lib.replace(" : ", " :<br>") if " : " in lib else lib.replace(" ", "<br>", 1) for lib in stats_type["type_usage"].astype(str)],
                            texttemplate="%{text}<br>%{percent:.1%}", textfont_size=TAILLE_ETIQUETTE,
                            hovertemplate="%{label} : %{value} clients (%{percent:.1%})<extra></extra>")
    fig_types.update_layout(showlegend=False, height=420, separators=", ", margin=dict(t=40, b=40, l=80, r=80))
    st.plotly_chart(fig_types, width='stretch')

with col_taux:
    st.markdown("#### Taux de défaut")
    fig_taux = px.bar(stats_type, x='type_usage', y='taux', color='type_usage', color_discrete_map=COULEURS_TYPES,
                      labels={'type_usage': "Type d'usage", 'taux': 'Taux de défaut (%)'})
    # Taux de défaut moyen en pointillés orange ; valeurs dans de petites étiquettes, devant la ligne (comme en 4.1 et 4.2)
    fig_taux.add_hline(y=taux_moyen, line_dash="dash", line_width=2, line_color=COULEURS["orange"])
    for _, row in stats_type.iterrows():
        fig_taux.add_annotation(x=row['type_usage'], y=row['taux'], yshift=12, showarrow=False,
                                text=f"<b>{nombre_fr(row['taux'], 1)} %</b>", font_size=TAILLE_ETIQUETTE,
                                bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2)
    # Ordonnée : 10 % de marge au-dessus de la plus haute colonne
    fig_taux.update_layout(showlegend=False, height=420, yaxis_range=[0, stats_type['taux'].max() * 1.1],
                           xaxis_tickangle=-30, xaxis_title=None)
    st.plotly_chart(fig_taux, width='stretch')

ligne = stats_type.set_index('type_usage')
part_credit = ligne.loc[[MENSUALITE, MIXTE], 'part'].sum()
st.markdown(f"""
- **La carte est d'abord un crédit** : {nombre_fr(part_credit, 1)} % des clients remboursent entre 3 et 30 % de leur facture, contre {nombre_fr(ligne.loc[COMPTANT, 'part'], 1)} % qui la règlent au comptant. À eux seuls, {nombre_fr(ligne.loc[MENSUALITE, 'part'], 1)} % des clients remboursent d'habitude 3 à 6 % de leur facture, la tranche du pic des ratios mensuels : celle du crédit par mensualité.
- **Plus le client rembourse, moins il fait défaut** : le taux de défaut passe de **{nombre_fr(ligne.loc[RIEN, 'taux'], 1)} %** pour les clients qui ne paient rien et **{nombre_fr(ligne.loc[DIFFICULTE, 'taux'], 1)} %** pour les clients en difficulté, à **{nombre_fr(ligne.loc[MENSUALITE, 'taux'], 1)} %** pour le crédit par mensualité, **{nombre_fr(ligne.loc[MIXTE, 'taux'], 1)} %** pour l'usage mixte, puis **{nombre_fr(ligne.loc[ELEVE, 'taux'], 1)} %** pour le remboursement élevé et **{nombre_fr(ligne.loc[COMPTANT, 'taux'], 1)} %** pour le paiement comptant (moyenne de {nombre_fr(taux_moyen, 1)} %, en pointillés orange).
- **L'usage mixte et le remboursement élevé restent ambigus** : paiement en plusieurs fois, rattrapage partiel d'un retard, paiement anticipé… Le remboursement élevé concerne peu de clients ({nombre_fr(ligne.loc[ELEVE, 'clients'])}), mais son risque est déjà proche de celui du paiement comptant.
- **Ne rien payer est le signal le plus fort**, mais il concerne peu de clients ({nombre_fr(ligne.loc[RIEN, 'clients'])}).
- **« {AUTRE} » ({nombre_fr(ligne.loc[AUTRE, 'clients'])} clients, {nombre_fr(ligne.loc[AUTRE, 'taux'], 1)} % de défaut)** est montré pour mémoire : un groupe hétérogène (une seule facture due, ou de l'argent payé en trop), qu'on n'interprète pas comme un comportement.
""")

# ------------------------------------------------------------------------------
st.subheader("Le type d'usage et les codifications de la banque", anchor="usage-codifications")
st.markdown("""
La page « 3.3 Les codifications » a donné un sens aux codifications à partir des paiements de chaque mois. On vérifie ici ce sens client par client : pour chaque type d'usage, quelle codification la banque pose-t-elle le plus souvent ? Pour chaque client, on retient sa **codification la plus fréquente** sur les 6 mois, qu'une facture soit due ou non. Une codification est une étiquette, pas une quantité : on ne calcule pas sa médiane.
""")

# Codification la plus fréquente : colonne PAY_habituel lue dans le CSV (créée par 05_03_EDA_storytelling, définie dans
# docs/colonnes_creees.md : PAY_1 à PAY_6, retards regroupés en 2, égalité tranchée par le mois le plus récent)
ORDRE_CODIF = ["-2", "-1", "0", "1", "2 et plus"]
df_ratio['codif_habituelle'] = df_ratio['PAY_habituel'].map({-2: "-2", -1: "-1", 0: "0", 1: "1", 2: "2 et plus"})
parts_codif = (pd.crosstab(df_ratio['type_usage'], df_ratio['codif_habituelle'], normalize='index') * 100)
parts_codif = parts_codif.reindex(index=[t[0] for t in TYPES], columns=ORDRE_CODIF, fill_value=0)

fig_codif = go.Figure()
for valeur_codif in ORDRE_CODIF:
    fig_codif.add_trace(go.Bar(
        y=parts_codif.index, x=parts_codif[valeur_codif], name=valeur_codif, orientation='h',
        marker_color=COULEURS_CODIF[valeur_codif],
        text=[f"{nombre_fr(v, 0)} %" if v >= 5 else "" for v in parts_codif[valeur_codif]], textposition="inside", textfont_size=TAILLE_ETIQUETTE,
        hovertemplate="%{y}<br>Codification habituelle " + valeur_codif + " : %{x:.1f} % des clients<extra></extra>",
    ))
# Nombre de clients au bout de chaque barre, pour montrer le poids de chaque type d'usage
clients_type = stats_type.set_index('type_usage')['clients']
for type_usage in parts_codif.index:
    fig_codif.add_annotation(x=101, y=type_usage, xanchor="left", showarrow=False,
                             text=f"<b>{nombre_fr(clients_type[type_usage])} clients</b>", font_size=TAILLE_ETIQUETTE)
fig_codif.update_layout(barmode="stack", height=520, xaxis_title="Part des clients (%)",
                        xaxis=dict(range=[0, 125], tickvals=[0, 20, 40, 60, 80, 100]),
                        yaxis=dict(autorange="reversed", title=None), legend_title="Codification la plus fréquente",
                        # entrywidth : espace après chaque libellé, pour que chaque carré reste collé à sa signification
                        legend=dict(orientation="h", y=1.12, itemwidth=30, entrywidth=90),
                        margin=dict(t=60), separators=", ", font_size=14)
st.plotly_chart(fig_codif, width='stretch')
st.caption("Codification la plus fréquente de chaque client de PAY_1 à PAY_6, qu'une facture soit due ou non ; en cas d'égalité, la plus récente des codifications à égalité.")

pc = parts_codif
st.markdown(f"""
Les codifications suivent de près le type d'usage, et confirment la lecture de la page 3.3 :
- **les clients au comptant sont habituellement codifiés {codif('-1')} ou {codif('-2')}** pour {nombre_fr(pc.loc[COMPTANT, ['-2', '-1']].sum(), 0)} % d'entre eux : {codif('-1')} désigne le paiement comptant, et {codif('-2')} aussi, mais pas seulement : comme l'ont montré les EDA, un {codif('-2')} qui n'est pas un paiement comptant correspond surtout à un compte sans encours, qui n'avait rien à payer (la codification la plus fréquente porte ici sur les 6 mois, y compris les mois sans facture) ;
- **les clients à crédit sont habituellement codifiés {codif('0')}** : {nombre_fr(pc.loc[MENSUALITE, '0'], 0)} % des clients pour le crédit par mensualité, {nombre_fr(pc.loc[MIXTE, '0'], 0)} % pour l'usage mixte. Le {codif('0')} est bien le crédit renouvelable en cours ;
- **le remboursement élevé mêle les deux** : {nombre_fr(pc.loc[ELEVE, '0'], 0)} % des clients habituellement codifiés {codif('0')} et {nombre_fr(pc.loc[ELEVE, ['-2', '-1']].sum(), 0)} % {codif('-1')} ou {codif('-2')}, un comportement intermédiaire entre crédit et comptant, qu'aucun autre type d'usage ne montre ;
- **les clients qui ne paient rien sont habituellement codifiés en retard ({codif('2 et plus')})** pour {nombre_fr(pc.loc[RIEN, '2 et plus'], 0)} % d'entre eux, et les clients en difficulté mêlent crédit ({codif('0')}) et retards ({nombre_fr(pc.loc[DIFFICULTE, '2 et plus'], 0)} %).

**Ces rapprochements portent sur des comportements habituels**, la médiane du ratio de paiement d'un côté et la codification la plus fréquente de l'autre, et non sur chaque mois : un même client peut payer au comptant un mois, à crédit le suivant, et recevoir des codifications différentes d'un mois à l'autre. Ils confirment les grandes lignes de la lecture de {codif('-2')}, {codif('-1')} et {codif('0')}, sans permettre de conclure sur le cas d'un client en particulier. La codification {codif('1')} et les codifications de retard demandent une étude à part : elles sont reprises avec les retards, en 4.6, puis avec la population contentieuse, en partie 5.
""")

st.markdown(f"""
**Un comportement médian, à lire avec prudence.** Chaque client est classé selon la médiane de ses ratios de paiement, c'est-à-dire son comportement le plus habituel, pas chacun de ses mois :
- **la médiane gomme les mois qui sortent de l'habitude** : un client qui ne paie rien trois mois et solde sa facture les deux autres a une médiane de 0 %, et se retrouve parmi ceux qui ne paient rien ;
- **elle repose parfois sur peu de mois** : un compte récemment ouvert ou un compte qui s'endort n'a que deux mois avec une facture due, et sa médiane dépend alors de deux paiements. C'est le cas de {nombre_fr(peu_de_mois)} clients. Ceux qui n'en ont qu'un sont rangés à part, dans « {AUTRE} ».

Ce classement sert donc à observer une **tendance** : elle est nette, mais ce n'est qu'une tendance, qui ne décrit pas chaque client mois par mois.
""")

st.info(f"""
**Ce que révèle le type d'usage** : chaque client a une façon habituelle d'utiliser sa carte, comme moyen de paiement ou comme crédit. Les usages sont bien tranchés aux extrémités, paiement comptant d'un côté, crédit par mensualité de l'autre ; entre les deux, des clients s'en écartent, par un vrai changement de comportement ou à cause de la qualité des données (paiements enregistrés en décalé). Que le client tienne ou non son habitude, le risque ne trompe pas : le taux de défaut d'un client à crédit par mensualité ({nombre_fr(ligne.loc[MENSUALITE, 'taux'], 1)} %) atteint {nombre_fr(ligne.loc[MENSUALITE, 'taux'] / ligne.loc[COMPTANT, 'taux'], 1)} fois celui d'un client au comptant ({nombre_fr(ligne.loc[COMPTANT, 'taux'], 1)} %). Les clients qui ne paient rien sont les plus risqués, mais minoritaires, et le dataset ne dit pas d'où vient leur situation. Ce comportement de remboursement, propre à chaque client, est une information à donner au futur modèle. Il éclaire aussi la codification de la banque : les codifications {codif('-2')} et {codif('0')}, absentes de la documentation officielle, et {codif('-1')} correspondent, dans les grandes lignes, à un usage habituel de la carte (paiement comptant pour {codif('-1')}, paiement comptant ou absence de dette pour {codif('-2')}, crédit renouvelable pour {codif('0')}), sans que cela vaille pour chaque mois de chaque client. La codification {codif('1')} et les retards restent, eux, à approfondir.
""")
