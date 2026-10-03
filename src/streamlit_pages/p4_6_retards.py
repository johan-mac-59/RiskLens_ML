from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 4.6 : LES RETARDS
# Codifications corrigées au nettoyage (niveau 5 : faux retards neutralisés, mois de
# transition recodé). Graphiques repris du notebook storytelling (cellules 39, 41, 43) ;
# CUMUL_INCIDENT est lue dans le CSV (simple comptage créé dans le storytelling).
# Les indicateurs du contentieux ne sont pas utilisés ici : ils sont présentés en partie 5.
# ==============================================================================
df = load_data()
taux_moyen = df["dpnm"].mean() * 100

MOIS = [(6, 'M-6 (avril)'), (5, 'M-5 (mai)'), (4, 'M-4 (juin)'), (3, 'M-3 (juil.)'), (2, 'M-2 (août)'), (1, 'M-1 (sept.)')]
LIBELLE_M = 'M (oct.)'
evolution = pd.DataFrame({
    'Mois': [libelle for _, libelle in MOIS],
    'retard': [(df[f'PAY_{n}'] >= 2).mean() * 100 for n, _ in MOIS],
    'grave': [(df[f'PAY_{n}'] >= 3).mean() * 100 for n, _ in MOIS],
    'codif_3': [(df[f'PAY_{n}'] == 3).mean() * 100 for n, _ in MOIS],
    'codif_4': [(df[f'PAY_{n}'] == 4).mean() * 100 for n, _ in MOIS],
    'codif_5_plus': [(df[f'PAY_{n}'] >= 5).mean() * 100 for n, _ in MOIS],
    'codif_1': [(df[f'PAY_{n}'] == 1).mean() * 100 for n, _ in MOIS],
    'mois_retard': [int(df.loc[df[f'PAY_{n}'] >= 2, f'PAY_{n}'].sum()) for n, _ in MOIS],
    'nb_codif_1': [int((df[f'PAY_{n}'] == 1).sum()) for n, _ in MOIS],
})


def etiquette(fig, x, y, texte, yshift=12):
    """Petite étiquette grisée au-dessus d'une barre."""
    fig.add_annotation(x=x, y=y, yshift=yshift, showarrow=False, text=f"<b>{texte}</b>",
                       font_size=TAILLE_ETIQUETTE, bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2)


def barres_mensuelles(valeurs, titre_y, couleur, decimales=1, suffixe=" %"):
    """Évolution mensuelle en barres, valeurs dans de petites étiquettes."""
    fig = go.Figure(go.Bar(x=evolution['Mois'], y=valeurs, marker_color=couleur,
                           hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>"))
    for mois, v in zip(evolution['Mois'], valeurs):
        etiquette(fig, mois, v, f"{nombre_fr(v, decimales)}{suffixe}")
    fig.update_layout(xaxis_title="Mois", yaxis_title=titre_y, yaxis_range=[0, max(valeurs) * 1.25],
                      height=420, separators=", ")
    return fig


entete_partie_4(df)

st.markdown("---")
st.header("4.6 Les retards : plus nombreux, plus graves, et plus risqués quand ils durent", anchor="retards")
st.markdown(f"""
Un client est dit **en retard** un mois donné quand sa codification de paiement vaut {codif('2')} ou plus. Les codifications utilisées ici sont celles corrigées au nettoyage : les retards posés alors qu'aucune facture n'était due ont été neutralisés, et le mois de transition de septembre recodé selon les paiements (page « 3.5 Décisions »).

La codification {codif('1')} est traitée à part : c'est une **codification non statuée**. Elle n'existe presque qu'en septembre, comme un statut d'attente que la banque n'a pas encore tranché (page « 3.3 Les codifications »). Même après le recodage du nettoyage, une partie reste indécidable : **on ne peut pas être sûr qu'il s'agisse d'impayés, mais ce sont des impayés potentiels**.
""")

# ------------------------------------------------------------------------------
st.subheader("De plus en plus de clients en retard, jusqu'au défaut d'octobre", anchor="part-retards")
x_mois = list(evolution['Mois']) + [LIBELLE_M]
vide = [None]
fig_retard = go.Figure()
fig_retard.add_trace(go.Bar(x=x_mois, y=list(evolution['retard']) + vide, name="En retard (2 et plus)",
                            marker_color=COULEURS["rouge_pale"], hovertemplate="<b>%{x}</b><br>En retard : %{y:.1f} %<extra></extra>"))
fig_retard.add_trace(go.Bar(x=x_mois, y=list(evolution['codif_1']) + vide, name="Impayés potentiels (codification 1, non statuée)",
                            marker_color=COULEURS["jaune"], hovertemplate="<b>%{x}</b><br>Impayés potentiels : %{y:.2f} %<extra></extra>"))
fig_retard.add_trace(go.Bar(x=x_mois, y=[None] * len(evolution) + [taux_moyen], name="Défaut de paiement en octobre (cible)",
                            marker_color=COULEURS["mauve"], hovertemplate="<b>%{x}</b><br>Défaut de paiement : %{y:.1f} %<extra></extra>"))
for _, row in evolution.iterrows():
    if row['codif_1'] >= 1:
        # Mois où la codification 1 pèse : étiquette du retard dans la barre, impayés potentiels au-dessus
        fig_retard.add_annotation(x=row['Mois'], y=row['retard'] / 2, showarrow=False, text=f"<b>{nombre_fr(row['retard'], 1)} %</b>",
                                  font_size=TAILLE_ETIQUETTE, bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2)
        etiquette(fig_retard, row['Mois'], row['retard'] + row['codif_1'], f"+ {nombre_fr(row['codif_1'], 1)} % d'impayés potentiels", yshift=24)
    else:
        etiquette(fig_retard, row['Mois'], row['retard'] + row['codif_1'], f"{nombre_fr(row['retard'], 1)} %")
etiquette(fig_retard, LIBELLE_M, taux_moyen, f"{nombre_fr(taux_moyen, 1)} % de défaut")
fig_retard.update_layout(barmode="stack", xaxis_title="Mois", yaxis_title="Part des clients (%)",
                         yaxis_range=[0, taux_moyen * 1.2], height=480, separators=", ",
                         legend=dict(orientation="h", y=1.12), margin=dict(t=60))
st.plotly_chart(fig_retard, width='stretch')
st.caption("Le défaut de paiement d'octobre est la cible du dataset : ce n'est pas une codification, et sa définition exacte n'est pas documentée. Il est placé à la suite des mois pour montrer l'aboutissement de la courbe, pas comme une mesure identique.")

aout = evolution.iloc[4]
sept = evolution.iloc[5]
avril = evolution.iloc[0]
st.markdown(f"""
- **Les retards progressent** : la part des clients en retard passe de **{nombre_fr(avril['retard'], 1)} %** en avril à **{nombre_fr(aout['retard'], 1)} %** en août, en pleine crise des cartes de crédit.
- **Septembre semble marquer une pause** ({nombre_fr(sept['retard'], 1)} %), mais c'est trompeur : {nombre_fr(sept['codif_1'], 1)} % des clients y portent encore la codification non statuée {codif('1')}. Avec ces impayés potentiels, on atteindrait **{nombre_fr(sept['retard'] + sept['codif_1'], 1)} %**, plus que tous les mois précédents.
- **En octobre, {nombre_fr(taux_moyen, 1)} % des clients font défaut** : la marche est haute depuis septembre, mais elle prolonge la montée des retards et des impayés potentiels.
""")

# ------------------------------------------------------------------------------
st.subheader("Une codification dont la logique semble changer avec le temps", anchor="logique-codification")
st.markdown(f"""
La page « 3.3 Les codifications » a montré que la codification est mise à jour avec un mois de décalage sur le paiement, et que des retards redescendent à {codif('2')} sans aucun paiement. Vus mois par mois, ces écarts ne sont pas répartis au hasard : **la façon de codifier semble évoluer au fil des six mois**.
""")

# Clients en retard grave (3 et plus) qui ne paient rien deux mois de suite alors que deux factures étaient dues
# (décalage d'un mois de la codification : on regarde le paiement du mois précédent et celui du mois même)
CATEGORIES = [("s'aggrave", COULEURS["bordeaux"]), ("reste au même niveau", COULEURS["gris"]),
              ("redescend à un retard plus faible", COULEURS["orange"]), ("redescend à une codification saine", COULEURS["turquoise"])]
lignes = []
for n, libelle in MOIS[2:]:
    avant, apres = df[f'PAY_{n + 1}'], df[f'PAY_{n}']
    sans_paiement = ((avant >= 3) & (df[f'BILL_AMT{n + 2}'] > 0) & (df[f'BILL_AMT{n + 1}'] > 0)
                     & (df[f'PAY_AMT{n + 1}'] == 0) & (df[f'PAY_AMT{n}'] == 0))
    a, b = avant[sans_paiement], apres[sans_paiement]
    nb = len(a)
    lignes.append({'Mois': libelle, 'nb': nb,
                   "s'aggrave": (b > a).sum() / nb * 100,
                   "reste au même niveau": (b == a).sum() / nb * 100,
                   "redescend à un retard plus faible": ((b >= 1) & (b < a)).sum() / nb * 100,
                   "redescend à une codification saine": (b <= 0).sum() / nb * 100,
                   'vers_2': (b == 2).sum() / nb * 100})
devenir = pd.DataFrame(lignes)

col_profondeur, col_devenir = st.columns(2)
with col_profondeur:
    st.markdown("#### Retards graves, selon leur profondeur")
    fig_grave = go.Figure()
    for colonne, nom, couleur in (('codif_3', "3", COULEURS["rouge_pale"]), ('codif_4', "4", COULEURS["bordeaux"]),
                                  ('codif_5_plus', "5 et plus", COULEURS["violet"])):
        fig_grave.add_trace(go.Bar(x=evolution['Mois'], y=evolution[colonne], name=nom, marker_color=couleur,
                                   hovertemplate="<b>%{x}</b><br>" + nom + " : %{y:.2f} %<extra></extra>"))
    for _, row in evolution.iterrows():
        etiquette(fig_grave, row['Mois'], row['grave'], f"{nombre_fr(row['grave'], 2)} %")
    fig_grave.update_layout(barmode="stack", xaxis_title="Mois", yaxis_title="Part des clients (%)",
                            yaxis_range=[0, evolution['grave'].max() * 1.25], height=460, separators=", ",
                            legend=dict(orientation="h", y=1.12, title_text="Codification : "), margin=dict(t=60))
    st.plotly_chart(fig_grave, width='stretch')
with col_devenir:
    st.markdown("#### Deux mois sans paiement : que devient un retard grave ?")
    fig_devenir = go.Figure()
    for nom, couleur in CATEGORIES:
        fig_devenir.add_trace(go.Bar(x=devenir['Mois'], y=devenir[nom], name=nom, marker_color=couleur,
                                     customdata=devenir['nb'], hovertemplate="<b>%{x}</b><br>" + nom + " : %{y:.1f} %<br>sur %{customdata} clients<extra></extra>",
                                     text=[f"{nombre_fr(v)} %" if v >= 8 else "" for v in devenir[nom]], textposition='inside',
                                     textfont=dict(size=TAILLE_ETIQUETTE)))
    fig_devenir.update_layout(barmode="stack", xaxis_title="Mois", yaxis_title="Part des clients (%)", yaxis_range=[0, 100],
                              height=460, separators=", ", legend=dict(orientation="h", y=1.22), margin=dict(t=90))
    st.plotly_chart(fig_devenir, width='stretch')
st.caption("À droite : clients codifiés 3 ou plus le mois précédent, qui n'ont rien payé ni le mois précédent ni ce mois-ci alors que deux factures étaient dues (la codification suit le paiement avec un mois de décalage, page « 3.3 Les codifications »). Septembre compte aussi les codifications 1 recodées en 2 au nettoyage. Attention aux échelles : les deux graphiques n'ont pas le même axe vertical.")

premier_dev, aout_dev = devenir.iloc[0], devenir.iloc[2]
plus_faible_3 = evolution.iloc[3]['codif_5_plus']
st.markdown(f"""
- **Les retards les plus profonds se raréfient à partir de juillet (M-3)** : les codifications {codif('5')} et plus concernent {nombre_fr(evolution.iloc[2]['codif_5_plus'], 2)} % des clients en juin, puis {nombre_fr(plus_faible_3, 2)} % en juillet et {nombre_fr(aout['codif_5_plus'], 2)} % en août, alors que les retards, eux, augmentent.
- **Ce n'est pas parce que ces dossiers se régularisent.** Chez les clients en retard grave qui ne paient rien deux mois de suite, la codification devrait s'aggraver d'un cran. En juin, elle **reste au même niveau** dans {nombre_fr(premier_dev['reste au même niveau'])} % des cas ; en août, cela n'arrive presque plus ({nombre_fr(aout_dev['reste au même niveau'])} %), et la codification **redescend** dans {nombre_fr(aout_dev['redescend à un retard plus faible'] + aout_dev['redescend à une codification saine'])} % des cas, le plus souvent à {codif('2')} ({nombre_fr(aout_dev['vers_2'])} %), sans aucun paiement.
- **Août (`PAY_2`) est le mois charnière** : c'est là que les retards redescendent à {codif('2')} sans raison apparente, comme l'avait déjà repéré l'EDA_lab sur des dossiers dont l'encours ne bouge pas. Tout se passe comme si la banque avait changé sa façon de codifier les dossiers en souffrance, ou les avait confiés à une autre gestion qui les ramène à {codif('2')}.

Pour la lecture des retards, il faut donc garder en tête qu'**une codification de retard plus faible ne veut pas dire une dette plus faible**, surtout sur les derniers mois.
""")

# ------------------------------------------------------------------------------
st.subheader("Le retard total, tel que l'affiche la codification", anchor="mois-retard")
# Simulation : chaque codification 1 non statuée comptée comme un mois de retard, empilée au-dessus
fig_total = go.Figure()
fig_total.add_trace(go.Bar(x=evolution['Mois'], y=evolution['mois_retard'], name="Mois de retard (codification 2 et plus)",
                           marker_color=COULEURS["violet"], hovertemplate="<b>%{x}</b><br>Mois de retard : %{y}<extra></extra>"))
fig_total.add_trace(go.Bar(x=evolution['Mois'], y=evolution['nb_codif_1'], name="Impayés potentiels (codification 1, comptée 1 mois)",
                           marker_color=COULEURS["jaune"], hovertemplate="<b>%{x}</b><br>Impayés potentiels : %{y}<extra></extra>"))
for _, row in evolution.iterrows():
    total = row['mois_retard'] + row['nb_codif_1']
    if row['nb_codif_1'] / total >= 0.02:
        fig_total.add_annotation(x=row['Mois'], y=row['mois_retard'] / 2, showarrow=False, text=f"<b>{nombre_fr(row['mois_retard'])}</b>",
                                 font_size=TAILLE_ETIQUETTE, bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2)
        etiquette(fig_total, row['Mois'], total, f"+ {nombre_fr(row['nb_codif_1'])} impayés potentiels", yshift=24)
    else:
        etiquette(fig_total, row['Mois'], total, nombre_fr(row['mois_retard']))
fig_total.update_layout(barmode="stack", xaxis_title="Mois", yaxis_title="Mois de retard cumulés (tous clients)",
                        yaxis_range=[0, (evolution['mois_retard'] + evolution['nb_codif_1']).max() * 1.2], height=460,
                        separators=", ", legend=dict(orientation="h", y=1.12), margin=dict(t=60))
st.plotly_chart(fig_total, width='stretch')
st.caption("Simulation : chaque codification 1 non statuée est comptée comme un mois de retard, pour montrer le retard éventuellement non comptabilisé. Ce n'est pas un fait établi : une partie de ces clients n'est sans doute pas en impayé.")
st.markdown(f"""
En additionnant, chaque mois, les mois de retard que la codification attribue aux clients en retard, la dette en souffrance grossit de {nombre_fr(evolution['mois_retard'].iloc[0])} mois en avril à {nombre_fr(evolution['mois_retard'].iloc[4])} en août. **Ce chiffre sous-estime sans doute la réalité** : il suppose que la codification compte fidèlement les mois de retard, alors que des retards graves redescendent sans paiement, comme on vient de le voir, et que d'autres restent à {codif('2')} pendant des mois sans s'aggraver, même quand le client ne paie rien. Il ne compte pas non plus les impayés potentiels de septembre : en les ajoutant à raison d'un mois chacun, septembre atteindrait {nombre_fr(evolution['mois_retard'].iloc[5] + evolution['nb_codif_1'].iloc[5])} mois de retard, contre {nombre_fr(evolution['mois_retard'].iloc[5])} sans eux. Il donne une tendance, pas une mesure exacte.
""")

# ------------------------------------------------------------------------------
st.subheader("Plus un client accumule les mois de retard, plus il fait défaut", anchor="cumul-retards")
st.markdown("Pour chaque client, on compte les mois en retard (2 et plus) sur les 6 mois, consécutifs ou non (colonne `CUMUL_INCIDENT`, définie dans la documentation du projet). Les codifications 1 non statuées n'y sont pas comptées.")
stats_cumul = df.groupby('CUMUL_INCIDENT')['dpnm'].agg(nb_clients='size', taux='mean').reindex(range(7), fill_value=0).reset_index()
stats_cumul['taux'] = stats_cumul['taux'] * 100
stats_cumul['part'] = stats_cumul['nb_clients'] / len(df) * 100

col_repartition, col_taux = st.columns(2)
with col_repartition:
    st.markdown("#### Répartition des clients")
    fig_rep = go.Figure(go.Bar(x=stats_cumul['CUMUL_INCIDENT'].astype(str), y=stats_cumul['part'], marker_color=COULEURS["turquoise"],
                               customdata=stats_cumul['nb_clients'], hovertemplate="%{x} mois : %{customdata} clients<extra></extra>"))
    for _, row in stats_cumul.iterrows():
        etiquette(fig_rep, str(int(row['CUMUL_INCIDENT'])), row['part'], f"{nombre_fr(row['part'], 1)} %")
    fig_rep.update_layout(xaxis_title="Nombre de mois en retard sur 6 mois", yaxis_title="Part des clients (%)",
                          yaxis_range=[0, stats_cumul['part'].max() * 1.2], height=420, separators=", ")
    st.plotly_chart(fig_rep, width='stretch')
with col_taux:
    st.markdown("#### Taux de défaut de paiement")
    fig_cumul = go.Figure(go.Bar(x=stats_cumul['CUMUL_INCIDENT'].astype(str), y=stats_cumul['taux'], marker_color=COULEURS["rouge_pale"],
                                 hoverinfo="skip"))
    fig_cumul.add_hline(y=taux_moyen, line_dash="dash", line_width=2, line_color=COULEURS["orange"])
    for _, row in stats_cumul.iterrows():
        etiquette(fig_cumul, str(int(row['CUMUL_INCIDENT'])), row['taux'], f"{nombre_fr(row['taux'], 1)} %")
    fig_cumul.update_layout(xaxis_title="Nombre de mois en retard sur 6 mois", yaxis_title="Taux de défaut de paiement (%)",
                            yaxis_range=[0, stats_cumul['taux'].max() * 1.2], height=420, separators=", ")
    st.plotly_chart(fig_cumul, width='stretch')

sans, un, six = stats_cumul.iloc[0], stats_cumul.iloc[1], stats_cumul.iloc[6]
st.markdown(f"""
- **La plupart des clients n'ont aucun retard** ({nombre_fr(sans['part'], 1)} %), avec un taux de défaut de {nombre_fr(sans['taux'], 1)} %, bien sous la moyenne ({nombre_fr(taux_moyen, 1)} %, ligne en pointillés).
- **Un seul mois de retard suffit à faire monter le risque** : {nombre_fr(un['taux'], 1)} % de défaut. Il grimpe ensuite avec chaque mois de retard supplémentaire, jusqu'à **{nombre_fr(six['taux'], 1)} %** pour les {nombre_fr(six['nb_clients'])} clients en retard tous les mois.
""")

# ------------------------------------------------------------------------------
st.subheader("Des clients figés en retard", anchor="retards-figes")
figes = pd.concat([df[f'PAY_{n}'] == 2 for n in range(1, 7)], axis=1).all(axis=1)
st.markdown(f"""
Parmi les clients en retard tous les mois, **{nombre_fr(figes.sum())} sont codifiés {codif('2')} sur les 6 mois**, sans jamais monter ni redescendre, qu'ils paient un peu ou rien du tout (page « 3.3 Les codifications »). Leur taux de défaut atteint **{nombre_fr(df.loc[figes, 'dpnm'].mean() * 100, 1)} %**. Avec les retards qui redescendent à {codif('2')} sans paiement, ils dessinent des dossiers sortis du circuit normal et gérés à part, par exemple par un service de recouvrement. Ces clients, et plus largement ceux dont les retards s'installent, ne se lisent pas avec la seule nomenclature des codifications : la partie 5 leur est consacrée.
""")

st.info(f"""
**Ce que révèlent les retards** : les retards deviennent plus nombreux au fil des mois, septembre ajoute des impayés potentiels que la banque n'a pas encore statués, et le risque monte avec chaque mois de retard accumulé, jusqu'au défaut d'octobre.

Mais les codifications de retard ne suivent pas une logique métier simple :
- la codification {codif('2')} n'était peut-être pas « deux mois de retard » : la codification {codif('1')} n'est jamais utilisée avant septembre, et un client sain passe directement à {codif('2')} ;
- au lieu d'augmenter d'un cran à chaque mois impayé, les codifications {codif('2')} et plus se figent ou redescendent sans aucun paiement, surtout sur les derniers mois.

Les codifications de retard ne suivent donc pas une progression mathématique linéaire. Il a fallu investiguer davantage pour comprendre la population liée à cette codification incomprise : c'est l'objet de la partie 5.
""")
