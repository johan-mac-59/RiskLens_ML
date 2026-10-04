from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 5.4 : DES COMPORTEMENTS DISTINCTS, SANS REGARDER LE DÉFAUT
# Reprend la description des statuts de 05_02_EDA_contentieux (section 4), sur tout le périmètre et sans dpnm.
# Indicateurs construits sur les seuls montants (plafond, dette, paiements, TYPE_USAGE) : la comparaison avec un
# statut défini sur les codifications est donc une vérification indépendante. Colonnes lues dans le CSV.
# ==============================================================================
df, s12, train, test = donnees_partie_5()
statut = s12['STATUT']

# Types d'usage : mêmes libellés, même ordre et mêmes couleurs que la page 4.3
NOMS_TYPES = ["Ne paie rien", "Client en difficulté", "Crédit lent", "Crédit rapide", "Usage mixte", "Paiement comptant"]
COULEURS_TYPES = dict(zip(NOMS_TYPES, px.colors.qualitative.Safe))

mois_sans_paiement = (s12[[f'PAY_AMT{i}' for i in range(1, 7)]] == 0).sum(axis=1)
# Ratio de paiement médian : -1 (compte qui commence à servir) et vide (aucune facture) ne sont pas des ratios
ratio_median = s12['ratio_PAY_BILL_median'].where(s12['ratio_PAY_BILL_median'] >= 0)
# Retard payé en septembre : part des clients actifs les six mois, et part des payeurs au comptant (TYPE_USAGE)
masque_paye = statut == "Retard payé en septembre"
actifs_6 = pd.concat([(s12[f'BILL_AMT{n}'] != 0) | (s12[f'PAY_AMT{n}'] > 0) for n in range(1, 7)], axis=1).all(axis=1)
paye_actifs = actifs_6[masque_paye].mean() * 100
paye_comptant = (s12.loc[masque_paye, 'TYPE_USAGE'] == "Paiement comptant").mean() * 100
indicateurs = pd.DataFrame({
    'clients': statut.value_counts(),
    'plafond': s12.groupby(statut, observed=False)['LIMIT_BAL'].median(),
    'utilisation': s12.groupby(statut, observed=False)['ratio_BILL_LIMIT1'].median(),
    'ratio': ratio_median.groupby(statut, observed=False).median(),
    'sans_paiement': mois_sans_paiement.groupby(statut, observed=False).mean(),
}).reindex(NOMS_STATUTS)

entete_partie_5(df, s12, train, test)

st.markdown("---")
st.header("5.4 Des comportements distincts, sans même regarder le défaut", anchor="comportements")
st.markdown(f"""
La définition du contentieux s'appuie sur les codifications de la banque. Avant de la juger sur le défaut, une question se pose : **les statuts décrivent-ils de vrais comportements, ou seulement des étiquettes ?** Si la règle ne faisait que recopier une codification, rien ne distinguerait les clients au contentieux des autres dans leurs montants.

On compare donc les statuts sur des indicateurs construits **uniquement sur les montants** (plafond, dette, paiements), sans aucune codification ni le défaut. Tout le périmètre est utilisé ({nombre_fr(len(s12))} clients).
""")


def barres_statuts(colonne, titre_y, decimales=0, suffixe=""):
    """Un indicateur par statut, en barres colorées selon le statut, valeurs dans de petites étiquettes."""
    valeurs = indicateurs[colonne]
    x = [LIBELLES_STATUTS[nom] for nom in NOMS_STATUTS]
    fig = go.Figure(go.Bar(x=x, y=valeurs, marker_color=list(STATUTS_CTX.values()),
                           customdata=indicateurs['clients'], hovertemplate="%{x}<br>%{customdata} clients<extra></extra>"))
    for nom, v in valeurs.items():
        etiquette_grise(fig, LIBELLES_STATUTS[nom], v, f"{nombre_fr(v, decimales)}{suffixe}")
    fig.update_layout(yaxis_title=titre_y, yaxis_range=[0, valeurs.max() * 1.25], height=400, separators=", ",
                      xaxis=dict(tickangle=0), margin=dict(t=20))
    return fig


# ------------------------------------------------------------------------------
st.subheader("1. Au contentieux : des plafonds plus bas, et largement utilisés", anchor="credit")
col_plafond, col_utilisation = st.columns(2)
with col_plafond:
    st.markdown("#### Plafond médian")
    st.plotly_chart(barres_statuts('plafond', "Plafond médian (NT$)"), width='stretch')
with col_utilisation:
    st.markdown("#### Utilisation du plafond en septembre (médiane)")
    st.plotly_chart(barres_statuts('utilisation', "Dette de septembre / plafond (%)", 1, " %"), width='stretch')
ctx, aucun, sorti, isole, paye = (indicateurs.loc[nom] for nom in
                                  ("Au contentieux", "Aucun incident", "Sorti du contentieux", "Retard isolé régularisé", "Retard payé en septembre"))
st.markdown(f"""
- **Les clients au contentieux ont un plafond médian de {nombre_fr(ctx['plafond'])} NT\$**, contre {nombre_fr(aucun['plafond'])} NT\$ pour les clients sans incident : la banque leur accorde moins de crédit. Le dataset ne dit pas si ce plafond a été fixé ainsi dès l'ouverture du compte ou réduit après les premiers incidents.
- **Ils en utilisent la plus grande partie** : leur dette de septembre en représente {nombre_fr(ctx['utilisation'], 1)} % (médiane), contre {nombre_fr(aucun['utilisation'], 1)} % pour les clients sans incident. Les clients sortis du contentieux ({nombre_fr(sorti['utilisation'], 1)} %) et ceux qui ont eu un retard isolé ({nombre_fr(isole['utilisation'], 1)} %) se placent entre les deux.
- Le lien entre un crédit très utilisé et le risque, vu en page « 4.2 L'usage du crédit », se retrouve ici sous la forme d'un statut.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Au contentieux : des paiements plus faibles et plus rares", anchor="paiements")
col_ratio, col_sans = st.columns(2)
with col_ratio:
    st.markdown("#### Ratio de paiement médian")
    st.plotly_chart(barres_statuts('ratio', "Part de la facture payée chaque mois (médiane, %)", 1, " %"), width='stretch')
with col_sans:
    st.markdown("#### Mois sans aucun paiement, sur 6")
    st.plotly_chart(barres_statuts('sans_paiement', "Nombre moyen de mois sans paiement", 1), width='stretch')
st.caption("Ratio de paiement médian : part de la facture payée, médiane des mois où une facture était due (colonne ratio_PAY_BILL_median, page « 4.3 Le type d'usage de la carte »). Les comptes qui commencent tout juste à servir, sans ratio mesurable, sont exclus de ce graphique.")
st.markdown(f"""
- **Les clients au contentieux remboursent chaque mois une petite part de leur facture** : {nombre_fr(ctx['ratio'], 1)} % en médiane, autour de la mensualité minimale, contre {nombre_fr(aucun['ratio'], 1)} % pour les clients sans incident.
- **Ils passent aussi plus de mois sans rien payer** : {nombre_fr(ctx['sans_paiement'], 1)} mois sur 6 en moyenne, contre {nombre_fr(aucun['sans_paiement'], 1)} pour les clients sans incident.
- **Les clients au retard payé en septembre forment un petit groupe à part** ({nombre_fr(paye['clients'])} clients), avec deux valeurs atypiques. **Leur ratio de paiement médian atteint {nombre_fr(paye['ratio'])} %** : ce n'est pas le reflet d'un seul mois. Le ratio est la médiane de tous les mois où une facture était due, et {nombre_fr(paye_actifs)} % de ces clients ont été actifs les six mois. La plupart sont des **payeurs au comptant**, qui règlent leur facture en entier chaque mois ({nombre_fr(paye_comptant)} % de paiement comptant, graphique ci-dessous). **Leur plafond est presque inutilisé en septembre** ({nombre_fr(paye['utilisation'], 1)} %) pour une raison voisine : payeurs au comptant, ils ne laissent pas leur dette s'accumuler d'un mois sur l'autre. Leur retard de septembre, posé sur une facture réglée, ressemble à un incident ponctuel plutôt qu'à une dette qui s'installe : c'est bien pour cela que la règle ne les place pas au contentieux. Il n'est pas anodin pour autant (page 5.5).
""")

# ------------------------------------------------------------------------------
st.subheader("3. Le type d'usage de la carte confirme la différence", anchor="type-usage")
st.markdown("Le type d'usage (page « 4.3 Le type d'usage de la carte ») résume le comportement de paiement habituel de chaque client à partir des seuls montants. Il permet de vérifier, de façon indépendante, ce que recouvre chaque statut.")
types = pd.crosstab(statut, pd.Categorical(s12['TYPE_USAGE'], categories=NOMS_TYPES), normalize='index').reindex(NOMS_STATUTS) * 100
fig_types = go.Figure()
for nom_type in NOMS_TYPES:
    valeurs = types[nom_type]
    fig_types.add_trace(go.Bar(y=NOMS_STATUTS, x=valeurs, orientation='h', name=nom_type, marker_color=COULEURS_TYPES[nom_type],
                               text=[f"{nombre_fr(v)} %" if v >= 6 else "" for v in valeurs], textposition='inside',
                               textfont=dict(size=TAILLE_ETIQUETTE),
                               hovertemplate="%{y}<br>" + nom_type + " : %{x:.1f} %<extra></extra>"))
fig_types.update_layout(barmode='stack', xaxis_title="Part des clients du statut (%)", xaxis_range=[0, 100], height=420,
                        separators=", ", legend=dict(orientation="h", y=1.15, traceorder="normal"), margin=dict(t=70),
                        yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_types, width='stretch')
st.caption("Comment lire : chaque barre fait 100 % et répartit les clients d'un statut selon leur type d'usage. Mêmes couleurs que la page 4.3. Les clients sans type d'usage (aucune facture mesurable) ne sont pas comptés.")
t_ctx, t_aucun, t_paye, t_sorti = (types.loc[nom] for nom in ("Au contentieux", "Aucun incident", "Retard payé en septembre", "Sorti du contentieux"))
st.markdown(f"""
- **Au contentieux, le crédit lent domine** ({nombre_fr(t_ctx['Crédit lent'])} % des clients), et **{nombre_fr(t_ctx['Ne paie rien'])} % ne paient rien du tout**. Le paiement comptant y est presque absent ({nombre_fr(t_ctx['Paiement comptant'], 1)} %).
- **Chez les clients sans incident, le paiement comptant est fréquent** ({nombre_fr(t_aucun['Paiement comptant'])} %), et ceux qui ne paient rien sont rarissimes ({nombre_fr(t_aucun['Ne paie rien'], 1)} %).
- **Les clients sortis du contentieux gardent un profil de crédit** (crédit lent ou rapide pour {nombre_fr(t_sorti['Crédit lent'] + t_sorti['Crédit rapide'])} %), mais paient davantage que ceux qui y sont encore : {nombre_fr(t_sorti['Paiement comptant'], 1)} % de paiement comptant contre {nombre_fr(t_ctx['Paiement comptant'], 1)} %, et {nombre_fr(t_sorti['Ne paie rien'], 1)} % qui ne paient rien contre {nombre_fr(t_ctx['Ne paie rien'], 1)} %.
- **Le retard payé en septembre concerne surtout des payeurs au comptant** ({nombre_fr(t_paye['Paiement comptant'])} %), ce qui confirme qu'il ne s'agit pas d'un contentieux.
""")

st.info(f"""
**Ce qu'il faut retenir** : sans jamais regarder le défaut, et sur des indicateurs qui ne doivent rien aux codifications, les statuts se distinguent nettement. Les clients au contentieux ont des plafonds plus bas, largement utilisés, et ne remboursent qu'une petite part de leur facture, quand ils paient. Les clients sans incident sont à l'opposé, et les clients sortis du contentieux entre les deux. La règle isole donc **un comportement de paiement réellement dégradé**, et pas seulement une étiquette de la banque. Reste à vérifier que ce comportement se traduit dans le défaut : c'est l'objet de la page suivante.
""")
