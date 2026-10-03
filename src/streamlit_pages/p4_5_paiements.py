from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 4.5 : LES PAIEMENTS (VUE D'ENSEMBLE, MOIS PAR MOIS)
# Graphiques repris du bac à sable (part des clients qui paient, ratios moyen et
# médian) ; agrégats mensuels calculés en direct sur les colonnes du CSV.
# ==============================================================================
df = load_data()

# PAY_AMTn rembourse BILL_AMT(n+1) : on ne garde, chaque mois, que les clients qui avaient une facture à payer
MOIS = [(5, 'M-5 (mai)'), (4, 'M-4 (juin)'), (3, 'M-3 (juil.)'), (2, 'M-2 (août)'), (1, 'M-1 (sept.)')]
ratio_columns = [f'ratio_PAY_BILL{n}' for n, _ in MOIS]
ratios_dus = ratios_affichables(df, ratio_columns)

lignes = []
for n, libelle in MOIS:
    facture_due = df[f'BILL_AMT{n + 1}'] > 0
    ratios = ratios_dus[f'ratio_PAY_BILL{n}'].dropna()
    lignes.append({
        'Mois': libelle,
        'factures dues': int(facture_due.sum()),
        'payeurs': int((facture_due & (df[f'PAY_AMT{n}'] > 0)).sum()),
        'moyenne': ratios.mean(),
        'mediane': ratios.median(),
        'soldees': (ratios >= 90).mean() * 100,
        'rien': (ratios == 0).mean() * 100,
        'facture_moy': df.loc[facture_due, f'BILL_AMT{n + 1}'].mean(),
        'facture_med': df.loc[facture_due, f'BILL_AMT{n + 1}'].median(),
        'paiement_moy': df.loc[facture_due, f'PAY_AMT{n}'].mean(),
        'paiement_med': df.loc[facture_due, f'PAY_AMT{n}'].median(),
    })
evolution = pd.DataFrame(lignes)
evolution['part_payeurs'] = evolution['payeurs'] / evolution['factures dues'] * 100

entete_partie_4(df)

st.markdown("---")
st.header("4.5 Les paiements : un comportement stable, alors que la dette grandit", anchor="paiements")
st.markdown(f"""
Les sous-parties précédentes ont regardé chaque client. On prend ici du recul : mois après mois, sur l'ensemble des clients qui avaient une facture à payer, combien paient, et quelle part de leur facture ? Le comportement de paiement évolue-t-il au fil des six mois ?

Chaque mois ne compte que les clients qui avaient une facture à payer ce mois-là. Les clients en **activité intermittente** (page « 4.4 La vie des comptes »), comme les comptes ouverts, dégelés ou endormis en cours de période, ne sont donc comptés que pour les mois où ils utilisent leur carte : l'effectif varie d'un mois à l'autre, de {nombre_fr(evolution['factures dues'].min())} à {nombre_fr(evolution['factures dues'].max())} clients.
""")

# ------------------------------------------------------------------------------
st.subheader("Neuf clients sur dix paient au moins une partie de leur facture, chaque mois", anchor="part-payeurs")
fig_pay = go.Figure(go.Bar(
    x=evolution['Mois'], y=evolution['part_payeurs'], marker_color=COULEURS["turquoise"],
    customdata=evolution[['payeurs', 'factures dues']].to_numpy(),
    hovertemplate="<b>%{x}</b><br>%{customdata[0]} clients sur %{customdata[1]}<br>%{y:.1f} %<extra></extra>",
))
for _, row in evolution.iterrows():
    fig_pay.add_annotation(x=row['Mois'], y=row['part_payeurs'], yshift=12, showarrow=False,
                           text=f"<b>{nombre_fr(row['part_payeurs'], 1)} %</b>", font_size=TAILLE_ETIQUETTE,
                           bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2)
fig_pay.update_layout(xaxis_title="Mois du paiement", yaxis_title="Part des clients qui paient (%)",
                      yaxis_range=[0, 105], height=450, separators=", ")
st.plotly_chart(fig_pay, width='stretch')
st.caption("Parmi les clients qui avaient une facture à payer ce mois-là (facture du mois précédent positive), part de ceux qui ont fait un paiement, quel qu'en soit le montant.")

st.markdown(f"""
D'un mois à l'autre, entre **{nombre_fr(evolution['part_payeurs'].min(), 1)} %** et **{nombre_fr(evolution['part_payeurs'].max(), 1)} %** des clients qui avaient une facture à payer font un paiement : la part est stable sur les cinq mois. À l'inverse, les mois sans aucun paiement restent rares et stables, entre {nombre_fr(evolution['rien'].min(), 1)} et {nombre_fr(evolution['rien'].max(), 1)} % des mois. Cela ne veut pas dire que ces clients sont à jour : un paiement peut ne couvrir qu'une petite partie de la facture, voire moins que la mensualité minimale.
""")

# ------------------------------------------------------------------------------
st.subheader("Une part de la facture payée qui change peu, sur une facture qui grandit", anchor="ratios-paiement")
st.markdown("En haut, le ratio de paiement : le montant payé rapporté à la facture qu'il règle (écrêté entre 0 et 200 %). En bas, les mêmes mois en NT$ : la facture due et le paiement qui la règle. À gauche les moyennes, à droite les médianes.")


def courbe(valeurs, titre_y, couleur, decimales):
    """Évolution mensuelle d'un indicateur, valeurs écrites au-dessus de chaque point."""
    fig = go.Figure(go.Scatter(
        x=evolution['Mois'], y=valeurs, mode='lines+markers+text',
        line=dict(color=couleur, width=3), marker=dict(size=9, color=couleur),
        text=[f"<b>{nombre_fr(v, decimales)} %</b>" for v in valeurs], textposition='top center',
        textfont=dict(size=TAILLE_ETIQUETTE), hovertemplate="<b>%{x}</b><br>%{y:.2f} %<extra></extra>",
    ))
    marge = (valeurs.max() - valeurs.min()) * 0.5 or 1
    fig.update_layout(xaxis_title="Mois du paiement", yaxis_title=titre_y, height=420, separators=", ",
                      yaxis_range=[max(valeurs.min() - marge, 0), valeurs.max() + marge])
    return fig




def courbes_montants(facture, paiement):
    """Facture due et paiement qui la règle, en NT$, sur le même axe."""
    fig = go.Figure()
    for valeurs, nom, couleur in ((facture, "Facture due", COULEURS["rouge_pale"]), (paiement, "Paiement", COULEURS["turquoise"])):
        fig.add_trace(go.Scatter(
            x=evolution['Mois'], y=valeurs, name=nom, mode='lines+markers+text',
            line=dict(color=couleur, width=3), marker=dict(size=9, color=couleur),
            text=[f"<b>{nombre_fr(v)}</b>" for v in valeurs], textposition='top center',
            textfont=dict(size=TAILLE_ETIQUETTE), hovertemplate="<b>%{x}</b><br>" + nom + " : %{y:,.0f} NT$<extra></extra>",
        ))
    fig.update_layout(xaxis_title="Mois du paiement", yaxis_title="Montant (NT$)", height=420, separators=", ",
                      yaxis_range=[0, facture.max() * 1.2], legend=dict(orientation="h", y=1.15), margin=dict(t=60))
    return fig


# Grille 2 x 2 en miroir : à gauche les moyennes, à droite les médianes
col_moyenne, col_mediane = st.columns(2)
with col_moyenne:
    st.markdown("#### Ratio de paiement moyen")
    st.plotly_chart(courbe(evolution['moyenne'], "Ratio de paiement moyen (%)", COULEURS["mauve"], 1), width='stretch')
with col_mediane:
    st.markdown("#### Ratio de paiement médian")
    st.plotly_chart(courbe(evolution['mediane'], "Ratio de paiement médian (%)", COULEURS["violet"], 1), width='stretch')
col_moyenne_nt, col_mediane_nt = st.columns(2)
with col_moyenne_nt:
    st.markdown("#### Facture et paiement moyens")
    st.plotly_chart(courbes_montants(evolution['facture_moy'], evolution['paiement_moy']), width='stretch', key="montants_moyens")
with col_mediane_nt:
    st.markdown("#### Facture et paiement médians")
    st.plotly_chart(courbes_montants(evolution['facture_med'], evolution['paiement_med']), width='stretch', key="montants_medians")
st.caption("Mois avec une facture due seulement ; chaque mois, la facture est celle du mois précédent, réglée par le paiement du mois. Attention aux échelles : les graphiques n'ont pas le même axe vertical.")

premier, dernier = evolution.iloc[0], evolution.iloc[-1]
st.markdown(f"""
- **La moyenne reste autour d'un tiers de la facture** ({nombre_fr(premier['moyenne'], 1)} % en mai, {nombre_fr(dernier['moyenne'], 1)} % en septembre). Elle est tirée vers le haut par les clients qui soldent leur facture, entre {nombre_fr(evolution['soldees'].min(), 1)} et {nombre_fr(evolution['soldees'].max(), 1)} % des mois selon le mois.
- **La médiane est bien plus basse et progresse un peu**, de {nombre_fr(premier['mediane'], 1)} à {nombre_fr(dernier['mediane'], 1)} % : chaque mois, dans la moitié des cas, le client ne rembourse qu'une faible part de sa facture, à la façon du crédit par mensualité vu en 4.3.

- **En montant, l'écart se creuse** : la facture due médiane passe de {nombre_fr(premier['facture_med'])} à {nombre_fr(dernier['facture_med'])} NT\\$, le paiement médian de {nombre_fr(premier['paiement_med'])} à {nombre_fr(dernier['paiement_med'])} NT\\$. L'écart entre la facture et le paiement médians grandit : de {nombre_fr(premier['facture_med'] - premier['paiement_med'])} à {nombre_fr(dernier['facture_med'] - dernier['paiement_med'])} NT\\$.

L'écart entre moyenne et médiane rappelle les deux façons d'utiliser la carte : une minorité qui solde tout, et une majorité qui ne rembourse qu'une petite part de sa facture.
""")


def progression(colonne):
    """Progression de mai à septembre, en %."""
    return (dernier[colonne] / premier[colonne] - 1) * 100


st.markdown(f"""
##### Pourquoi le ratio progresse-t-il alors que l'écart en NT\\$ se creuse ?
Les deux lignes de graphiques ne mesurent pas la même chose : **un ratio est un pourcentage**, il compare le paiement à la facture ; **les factures et les paiements sont des montants en NT\\$**.
- **Les courbes de paiement paraissent plates à cause de l'échelle** : les paiements sont environ dix fois plus petits que les factures. En pourcentage, le paiement médian progresse de **{nombre_fr(progression('paiement_med'))} %** de mai à septembre, la facture médiane de **{nombre_fr(progression('facture_med'))} %** : la part payée peut augmenter, alors que les {nombre_fr(dernier['paiement_med'] - premier['paiement_med'])} NT\\$ de paiement en plus pèsent peu face aux {nombre_fr(dernier['facture_med'] - premier['facture_med'])} NT\\$ de facture en plus. L'écart en NT\\$ grandit quand même.
- **Le ratio moyen n'est pas le paiement moyen divisé par la facture moyenne.** Le ratio est calculé client par client, puis on fait la moyenne : chaque client compte pour un, quel que soit le montant de sa facture. Les montants moyens, eux, sont tirés par les grosses factures, qui sont remboursées en plus petite part. Rapporté aux montants moyens, le paiement ne couvre que {nombre_fr(premier['paiement_moy'] / premier['facture_moy'] * 100)} % de la facture en mai, contre {nombre_fr(premier['moyenne'], 1)} % pour le ratio moyen. De même, le ratio médian n'est pas le paiement médian divisé par la facture médiane.
""")

st.info("""
**Ce que révèlent les paiements** : vu d'ensemble, le comportement de paiement ne change presque pas en six mois. Les clients paient aussi souvent, et à peu près la même part de leur facture. Mais les factures, elles, grandissent, comme l'utilisation du plafond (page « 4.2 L'usage du crédit ») : les clients paient de la même façon une dette qui grandit. La dégradation ne se lit donc pas dans les paiements eux-mêmes, mais dans l'écart qui se creuse entre ce qui est dû et ce qui est remboursé.
""")
