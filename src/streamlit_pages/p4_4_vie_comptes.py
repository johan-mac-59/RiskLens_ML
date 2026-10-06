from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 4.4 : LA VIE DES COMPTES (NOUVEAUX COMPTES, COMPTES QUI S'ENDORMENT)
# Graphiques des comptes actifs et des activations repris du bac à sable ; la
# répartition par vie du compte s'appuie sur FLAG_OUVERTURE et FLAG_DEGEL. Chiffres calculés en direct.
# ==============================================================================
df = load_data()
taux_moyen = df["dpnm"].mean() * 100

# Un compte est actif un mois donné s'il y a une facture positive ou un paiement ce mois-là
# (même critère que la règle des comptes inactifs, page 3.5)
actif = {n: (df[f'BILL_AMT{n}'] > 0) | (df[f'PAY_AMT{n}'] > 0) for n in range(1, 7)}

entete_partie_4(df)

st.markdown("---")
st.header("4.4 La vie des comptes : les nouveaux comptes ne sont pas plus risqués", anchor="vie-comptes")
st.markdown("""
D'un mois à l'autre, des comptes s'ouvrent ou se réveillent, d'autres cessent toute activité. Un compte est dit **actif** un mois donné s'il présente une facture positive ou un paiement ce mois-là, le même critère que la règle des comptes inactifs (page « 3.5 Décisions »). Un compte qui vient de s'ouvrir, ou un ancien compte qui se réveille, est-il plus risqué que les autres ?
""")

# ------------------------------------------------------------------------------
st.subheader("De plus en plus de comptes actifs au fil des mois", anchor="comptes-actifs")

# 1. Mois dans l'ordre chronologique
colonnes_mois = [(6, 'M-6 (avril)'), (5, 'M-5 (mai)'), (4, 'M-4 (juin)'), (3, 'M-3 (juil.)'), (2, 'M-2 (août)'), (1, 'M-1 (sept.)')]

total_clients = len(df)
df_actifs = pd.DataFrame({
    'Mois': [label for _, label in colonnes_mois],
    'Nombre': [int(actif[n].sum()) for n, _ in colonnes_mois],
})
df_actifs['Pourcentage'] = df_actifs['Nombre'] / total_clients * 100

# 2. Graphique : part des comptes actifs, valeur au-dessus de chaque barre
fig_actifs = go.Figure()
fig_actifs.add_trace(
    go.Bar(
        x=df_actifs['Mois'],
        y=df_actifs['Pourcentage'],
        marker_color=COULEURS["turquoise"],
        customdata=df_actifs['Nombre'],
        hovertemplate='<b>%{x}</b><br>Comptes actifs : %{customdata:,}<br>Proportion : %{y:.1f} %<extra></extra>',
    )
)
for _, row in df_actifs.iterrows():
    fig_actifs.add_annotation(x=row['Mois'], y=row['Pourcentage'], yshift=12, showarrow=False,
                              text=f"<b>{nombre_fr(row['Pourcentage'], 1)} %</b>", font_size=TAILLE_ETIQUETTE,
                              bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2)
fig_actifs.update_layout(
    xaxis_title='Mois',
    yaxis_title='Part des comptes actifs (%)',
    yaxis=dict(range=[0, 105]),
    height=450,
    separators=", ",
)
st.plotly_chart(fig_actifs, width='stretch')

st.markdown(f"""
La part des comptes actifs augmente chaque mois, de **{nombre_fr(df_actifs['Pourcentage'].iloc[0], 1)} %** en avril à **{nombre_fr(df_actifs['Pourcentage'].iloc[-1], 1)} %** en septembre. Des comptes sans activité en début de période se mettent à servir : ce sont les nouveaux comptes, ou des comptes qui se réveillent.
""")

# ------------------------------------------------------------------------------
st.subheader("Ouvertures et dégels : deux façons de devenir actif", anchor="activations")
st.markdown("""
Deux situations se distinguent parmi les comptes qui deviennent actifs pendant la période (colonnes `FLAG_OUVERTURE`, `FLAG_DEGEL` et `MOIS_ACTIVATION`, définies dans la documentation du projet) :
- une **ouverture** : un compte qui ne laisse **aucune trace** avant sa première activité. Son encours vaut 0 exactement et il n'y a aucun paiement en avril, donc ni dette ni avoir en mars non plus ; puis vient une activité (un mouvement de l'encours ou un paiement). Avec un solde à 0, on ne sait pas distinguer un compte récent d'un compte ancien resté inactif : les deux sont comptés, par convention, comme une ouverture ;
- un **dégel** : le réveil d'un compte gelé, qui a laissé **une trace avant son gel**, la preuve qu'il existait déjà : un avoir en avril, ou un mois actif juste avant le gel. Un mois est **inactif** quand il n'y a aucun paiement et que l'encours, nul ou créditeur, ne bouge pas : ni achat ni remboursement (en avril, faute de connaître mars, un encours nul ou créditeur sans paiement suffit). Le **gel** est une suite de mois inactifs. Quand on a le recul suffisant, c'est-à-dire quand on voit le mois actif qui la précède, on exige **3 mois inactifs d'affilée**. Sinon, quand le compte est inactif depuis avril (le premier mois observé), on ne peut pas savoir depuis quand il dort : on le considère gelé s'il est **inactif sur toute la durée visible**, d'avril jusqu'à son réveil. Le **réveil** est le premier mois actif qui suit le gel.

Un compte ne peut pas être à la fois une ouverture et un dégel : un compte à 0 sans paiement depuis avril, puis actif, est toujours compté comme une ouverture, puisqu'il ne laisse aucune trace avant.

Le **mois d'activation** (`MOIS_ACTIVATION`) est le mois de l'ouverture ou du réveil, de mai à septembre ; il vaut -1 pour les autres comptes. C'est lui qui place chaque compte dans les barres des deux graphiques ci-dessous.

**Effets de bord, dus à la fenêtre de 6 mois** :
- **Un compte inactif depuis avril** compte comme une ouverture ou un dégel, quelle que soit la durée de son inactivité, puisqu'on ne voit pas ce qui précède avril. Une partie de ces comptes, surtout parmi ceux qui s'activent en mai ou en juin, peut être simplement en activité intermittente, sans activité en avril, plutôt que de vraies ouvertures ou de vrais dégels.
- **Les barres des dégels ne comptent pas les mêmes gels selon le mois** : un gel dont on voit le début (commencé en mai ou après) dure au moins 3 mois et ne peut donc se terminer qu'en août ou en septembre. Les dégels de mai à juillet sont tous des comptes inactifs depuis avril ; ceux d'août et de septembre y ajoutent les gels commencés en cours de période. Les barres ne se comparent donc pas directement d'un mois à l'autre.
- **Fin de période** : un gel qui commence en juillet ou après n'a pas le temps de durer 3 mois et de se terminer avant octobre ; il n'est pas vu.
""")
NOMS_MOIS = {5: "Mai (M-5)", 4: "Juin (M-4)", 3: "Juillet (M-3)", 2: "Août (M-2)", 1: "Sept. (M-1)"}


def graphique_activation(flag, couleur):
    """Barres : comptes activés par mois ; courbe : taux de défaut ; pointillés orange : moyenne."""
    groupe = df[df[flag] == 1]
    stats = groupe.groupby('MOIS_ACTIVATION')['dpnm'].agg(['size', 'mean']).reindex([5, 4, 3, 2, 1], fill_value=0)
    stats['mean'] = stats['mean'] * 100
    mois = [NOMS_MOIS[m] for m in stats.index]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=mois, y=stats['size'], name="Comptes activés", marker_color=couleur,
                         text=[nombre_fr(n) for n in stats['size']], textposition='outside', textfont_size=TAILLE_ETIQUETTE),
                  secondary_y=False)
    fig.add_trace(go.Scatter(x=mois, y=stats['mean'], name="Taux de défaut (%)", mode='lines+markers+text',
                             line=dict(color=COULEURS["rouge_pale"], width=3), marker=dict(size=9, color=COULEURS["rouge_pale"]),
                             text=[f"<b>{nombre_fr(t, 1)} %</b>" for t in stats['mean']], textposition='top center',
                             textfont=dict(size=TAILLE_ETIQUETTE, color=COULEURS["rouge_pale"])), secondary_y=True)
    fig.add_hline(y=taux_moyen, line_dash="dash", line_width=2, line_color=COULEURS["orange"], secondary_y=True)
    fig.update_layout(height=450, separators=", ", legend=dict(orientation="h", y=1.15), margin=dict(t=60))
    fig.update_yaxes(title_text="Comptes activés", range=[0, max(stats['size'].max(), 1) * 1.25], secondary_y=False)
    fig.update_yaxes(title_text="Taux de défaut (%)", range=[0, max(stats['mean'].max(), taux_moyen) * 1.4], showgrid=False, secondary_y=True)
    return fig, len(groupe), groupe['dpnm'].mean() * 100


col_ouverture, col_degel = st.columns(2)
with col_ouverture:
    st.markdown("#### Ouvertures de compte")
    fig_o, nb_ouvertures, taux_ouvertures = graphique_activation('FLAG_OUVERTURE', COULEURS["bleu_pale"])
    st.plotly_chart(fig_o, width='stretch')
with col_degel:
    st.markdown("#### Dégels de comptes dormants")
    fig_d, nb_degels, taux_degels = graphique_activation('FLAG_DEGEL', COULEURS["mauve"])
    st.plotly_chart(fig_d, width='stretch')
st.caption("Attention aux échelles : les deux graphiques n'ont pas le même axe des effectifs.")

st.markdown(f"""
- **Les ouvertures sont nombreuses** ({nombre_fr(nb_ouvertures)} comptes, taux de défaut de {nombre_fr(taux_ouvertures, 1)} %), **les dégels rares** ({nombre_fr(nb_degels)} comptes, {nombre_fr(taux_degels, 1)} %) : sur de si petits effectifs mensuels, les taux de défaut des dégels varient fortement d'un mois à l'autre et se lisent avec prudence.
- **La frontière entre les deux reste imparfaite** : un encours nul en avril peut aussi être celui d'un compte ancien resté vide, qui se réveille ; une partie des « ouvertures » sont donc des dégels de comptes sans encours. Certains comptes qui redémarrent peuvent aussi être des **dossiers qui ressortent d'une gestion contentieuse**, ce que le dataset ne permet pas de vérifier.
- Le taux de défaut moyen de l'ensemble des clients ({nombre_fr(taux_moyen, 1)} %) est en pointillés orange.
""")

# ------------------------------------------------------------------------------
st.subheader("Ouvertures, dégels, comptes endormis : le poids de chaque situation", anchor="comptes-endormis")

# Groupes exclusifs selon la vie du compte sur les 6 mois
endormi = (actif[3] | actif[4] | actif[5] | actif[6]) & ~actif[1] & ~actif[2] & ~(df['FLAG_OUVERTURE'] == 1) & ~(df['FLAG_DEGEL'] == 1)
toujours = pd.concat(actif.values(), axis=1).all(axis=1) & ~(df['FLAG_OUVERTURE'] == 1) & ~(df['FLAG_DEGEL'] == 1)
GROUPES = [
    ("Actifs sur les 6 mois", toujours),
    # Ordre d'affichage : les dégels entre deux grandes parts, pour séparer les petites étiquettes du disque
    ("Dégels", (df['FLAG_DEGEL'] == 1)),
    ("Ouvertures", (df['FLAG_OUVERTURE'] == 1)),
    ("Comptes endormis", endormi),
    ("Activité intermittente", ~(toujours | (df['FLAG_OUVERTURE'] == 1) | (df['FLAG_DEGEL'] == 1) | endormi)),
]
stats_vie = pd.DataFrame({
    'groupe': [nom for nom, _ in GROUPES],
    'clients': [int(m.sum()) for _, m in GROUPES],
    'taux': [df.loc[m, 'dpnm'].mean() * 100 for _, m in GROUPES],
})
stats_vie['part'] = stats_vie['clients'] / len(df) * 100

st.markdown("""
Cinq situations, attribuées dans cet ordre (un client n'appartient qu'à une seule) :
- **Ouverture** : aucune trace avant la première activité (encours de 0 exactement et aucun paiement en avril), puis une activité (mouvement de l'encours ou paiement) de mai à septembre ;
- **Dégel** : réveil, de mai à septembre, d'un compte gelé qui existait déjà (un avoir en avril, ou un mois actif avant le gel) : 3 mois inactifs d'affilée quand on a le recul suffisant, sinon inactif sur toute la durée visible depuis avril (définition ci-dessus) ;
- **Compte endormi** : une activité entre avril et juillet, puis plus aucune facture positive ni aucun paiement en août et en septembre ; deux mois sans activité sont exigés, et non un seul, parce qu'un paiement peut être enregistré avec un mois de décalage (page « 3.3 Les codifications ») ;
- **Actifs sur les 6 mois** : une facture positive ou un paiement chaque mois ;
- **Activité intermittente** : tous les autres comptes, actifs dès avril mais avec au moins un mois sans activité en cours de période ; une situation difficile à mesurer, à cause des délais d'enregistrement des paiements.
""")

col_repartition, col_taux = st.columns(2)
with col_repartition:
    st.markdown("#### Répartition des comptes")
    fig_vie = px.pie(stats_vie, names='groupe', values='clients', color='groupe',
                     color_discrete_sequence=px.colors.qualitative.Safe)
    fig_vie.update_traces(sort=False, direction="clockwise", textposition="outside", automargin=True,  # marges élargies pour que les étiquettes ne soient pas coupées
                          # Étiquettes sur une seule ligne, et petites parts placées à droite (rotation) : elles s'étagent
                          # verticalement au lieu de s'empiler
                          rotation=90, texttemplate="%{label} : %{percent:.1%}", textfont_size=TAILLE_ETIQUETTE,
                          hovertemplate="%{label} : %{value} clients (%{percent:.1%})<extra></extra>")
    fig_vie.update_layout(showlegend=False, height=420, separators=", ", margin=dict(t=40, b=40, l=80, r=80))
    st.plotly_chart(fig_vie, width='stretch')

with col_taux:
    st.markdown("#### Taux de défaut de paiement")
    fig_taux_vie = px.bar(stats_vie, x='groupe', y='taux', color='groupe',
                          color_discrete_sequence=px.colors.qualitative.Safe,
                          labels={'groupe': 'Vie du compte', 'taux': 'Taux de défaut (%)'})
    fig_taux_vie.add_hline(y=taux_moyen, line_dash="dash", line_width=2, line_color=COULEURS["orange"])
    for _, row in stats_vie.iterrows():
        fig_taux_vie.add_annotation(x=row['groupe'], y=row['taux'], yshift=12, showarrow=False,
                                    text=f"<b>{nombre_fr(row['taux'], 1)} %</b>", font_size=TAILLE_ETIQUETTE,
                                    bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2)
    fig_taux_vie.update_layout(showlegend=False, height=420, yaxis_range=[0, stats_vie['taux'].max() * 1.3],
                               xaxis_tickangle=-30, xaxis_title=None)
    st.plotly_chart(fig_taux_vie, width='stretch')

vie = stats_vie.set_index('groupe')
dette_octobre = int((df.loc[endormi, 'BILL_AMT1'] > 0).sum())
st.markdown(f"""
- **La grande majorité des comptes vit sur toute la période** ({nombre_fr(vie.loc['Actifs sur les 6 mois', 'part'], 1)} %), avec un taux de défaut proche de la moyenne ({nombre_fr(vie.loc['Actifs sur les 6 mois', 'taux'], 1)} %).
- **Ouvertures et dégels n'ont pas le même poids** : {nombre_fr(vie.loc['Ouvertures', 'clients'])} ouvertures ({nombre_fr(vie.loc['Ouvertures', 'part'], 1)} % des comptes, {nombre_fr(vie.loc['Ouvertures', 'taux'], 1)} % de défaut) contre {nombre_fr(vie.loc['Dégels', 'clients'])} dégels seulement ({nombre_fr(vie.loc['Dégels', 'part'], 1)} %, {nombre_fr(vie.loc['Dégels', 'taux'], 1)} % de défaut, sur un effectif trop faible pour conclure).
- **Les comptes endormis** ({nombre_fr(vie.loc["Comptes endormis", 'clients'])} clients) ne sont pas étudiés pour leur risque : {"aucun d'entre eux n'a de facture à payer en octobre, donc rien à rembourser" if dette_octobre == 0 else f"seuls {nombre_fr(dette_octobre)} d'entre eux ont une facture à payer en octobre"}, et pourtant {nombre_fr(vie.loc["Comptes endormis", 'taux'], 1)} % sont notés en défaut : c'est une **anomalie**, comme pour les clients sans facture de la page « 4.2 L'usage du crédit ». Ce défaut ne peut pas venir d'une facture impayée : il peut s'agir d'un artefact de la cible, ou d'un événement de gestion (clôture du compte, saisie, faillite personnelle) que le dataset ne montre pas.
""")

st.info("""
**Ce que révèle la vie des comptes** : de plus en plus de comptes sont actifs au fil des mois, mais l'ouverture ou le réveil d'un compte ne s'accompagne pas d'un risque plus élevé : l'ancienneté récente n'est pas un signal de défaut. Les comptes endormis, eux, n'ont plus de dette : ceux qui sont pourtant notés en défaut sont une anomalie, qui rappelle une fois encore que la cible doit être lue avec prudence.
""")
