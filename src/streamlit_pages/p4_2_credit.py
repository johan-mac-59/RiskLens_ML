from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 4.2 : L'USAGE DU CRÉDIT
# Graphiques repris de la page « Analyses (version actuelle) » ; tous les
# chiffres sont calculés en direct sur le dataset (plafonds de 500 000 NT$ ou moins).
# ==============================================================================
df = load_data()
taux_moyen = df["dpnm"].mean() * 100

entete_partie_4(df)

st.markdown("---")
st.header("4.2 L'usage du crédit : les clients qui utilisent le plus leur plafond sont les plus risqués", anchor="credit")
st.markdown("Le plafond est le montant de crédit que la banque accorde au client ; la facture du mois, rapportée au plafond, mesure la part de ce crédit qu'il utilise réellement. Deux questions guident cette sous-partie : le montant du plafond dit-il quelque chose du risque, et l'usage qu'en fait le client en dit-il davantage ?")

# ------------------------------------------------------------------------------
st.subheader("Des plafonds surtout modestes", anchor="repartition-plafonds")

# Histogramme de répartition des plafonds (tous les clients étudiés ont un plafond <= 500 000 NT$)
fig2 = px.histogram(df['LIMIT_BAL'].dropna(), nbins=50,
                    labels={'value': 'Montant du plafond (NT$)', 'count': 'Nombre de clients'})
fig2.update_traces(marker_color=COULEURS["turquoise"], marker_line_color='white', marker_line_width=0.5)
fig2.update_layout(xaxis_title='Montant du plafond (NT$)',
                   yaxis_title='Nombre de clients',
                   xaxis_range=[0, 510000],
                   showlegend=False,
                   height=500)

# Formatage des axes X pour afficher les nombres complets avec espaces
fig2.update_xaxes(tickformat=',.0f', tickprefix=' ', tickangle=0)
fig2.update_layout(separators=", ")

# Ajout des lignes de moyenne et médiane
mean_val = df['LIMIT_BAL'].mean()
median_val = df['LIMIT_BAL'].median()

fig2.add_vline(x=mean_val, line_color=COULEURS["orange"], line_dash="dash", line_width=2,
               annotation_text=f"Moyenne : {nombre_fr(mean_val)}",
               annotation_position="top right")

fig2.add_vline(x=median_val, line_color=COULEURS["vert_fonce"], line_dash="dash", line_width=2,
               annotation_text=f"Médiane : {nombre_fr(median_val)}",
               annotation_position="top left")

st.plotly_chart(fig2, width='stretch')

part_50k = (df['LIMIT_BAL'] <= 50000).mean() * 100
st.markdown(f"""
Le plafond médian est de **{nombre_fr(median_val)} NT\\$** et le plafond moyen de {nombre_fr(mean_val)} NT\\$ : la moyenne est tirée vers le haut par les plafonds les plus élevés. Les plafonds sont souvent des montants ronds, d'où les pics, et {nombre_fr(part_50k, 1)} % des clients ont un plafond de 50 000 NT\\$ ou moins.
""")

# ------------------------------------------------------------------------------
st.subheader("Plus le plafond est petit, plus le taux de défaut est élevé", anchor="defaut-plafond")

df_plafond = df.copy()

# Tranches de 10 000 NT$ pour garder un détail fin (50 barres)
bin_size = 10000
bins = np.arange(1, 500001 + bin_size, bin_size)
labels = [f'{i//1000}k-{(i+bin_size)//1000}k' for i in bins[:-1]]

df_plafond['LIMIT_BAL_interval'] = pd.cut(
    df_plafond['LIMIT_BAL'], bins=bins, labels=labels, right=False
)

# observed=False conserve toutes les tranches jusqu'à 500k, même si sans clients
default_rates = (
    df_plafond.groupby('LIMIT_BAL_interval', observed=False)['dpnm'].mean()
    * 100
)

# Remplace les NaN (tranches sans clients) par 0
rates_values = default_rates.fillna(0).values

fig4 = go.Figure(
    data=[
        go.Bar(
            x=default_rates.index,
            y=rates_values,
            marker_color=COULEURS["rouge_pale"],
            hovertemplate="Plafond de %{x} NT$ : %{y:.1f} %<extra></extra>",
        )
    ]
)

max_y = (
    max(rates_values) * 1.25
    if len(rates_values) > 0 and max(rates_values) > 0
    else 30
)

# Taux de défaut moyen : repère sans texte, comme en 4.1
fig4.add_hline(y=taux_moyen, line_dash="dash", line_width=2, line_color=COULEURS["orange"])
fig4.update_layout(
    xaxis_title='Tranche de plafond (NT$)',
    yaxis_title='Taux de défaut (%)',
    # Un repère tous les 50 000 NT$ (une tranche sur cinq) au lieu de chaque tranche, pour la lisibilité
    xaxis=dict(tickmode='array', tickvals=labels[::5], ticktext=[f"{k * 10} k" for k in range(0, 50, 5)], tickangle=0),
    # Sol à -1 pour faire ressortir les barres à 0%
    yaxis_range=[-1, max_y],
    height=500,
    separators=", ",
)

st.plotly_chart(fig4, width='stretch')

petits = df['LIMIT_BAL'] <= 50000
grands = df['LIMIT_BAL'] > 300000
st.markdown(f"""
La tendance baissière du risque est nette : le taux de défaut atteint **{nombre_fr(df.loc[petits, 'dpnm'].mean() * 100, 1)} %** pour les plafonds de 50 000 NT\\$ ou moins, contre **{nombre_fr(df.loc[grands, 'dpnm'].mean() * 100, 1)} %** au-delà de 300 000 NT\\$ (moyenne de {nombre_fr(taux_moyen, 1)} %, en pointillés orange). La banque accorde des plafonds plus élevés aux clients qu'elle juge plus solides, et ce jugement se vérifie.
""")

# ------------------------------------------------------------------------------
st.subheader("Une utilisation du plafond très variable d'un client à l'autre", anchor="utilisation")

# Calcul de la moyenne des ratios d'utilisation pour chaque client sur les 6 mois
ratio_plafond = [
    'ratio_BILL_LIMIT1',
    'ratio_BILL_LIMIT2',
    'ratio_BILL_LIMIT3',
    'ratio_BILL_LIMIT4',
    'ratio_BILL_LIMIT5',
    'ratio_BILL_LIMIT6',
]

# Calcul de la moyenne par client sur les 6 mois
df['mean_ratio'] = df[ratio_plafond].mean(axis=1)

# Comptages spécifiques
nb_clients_zero = df[df['mean_ratio'] == 0]['mean_ratio'].count()
nb_clients_sup_120 = df[df['mean_ratio'] > 120]['mean_ratio'].count()

# Création de l'histogramme avec Plotly
fig_repartition_ratio_plafond = px.histogram(
    df['mean_ratio'].clip(upper=120),
    nbins=120,
    labels={
        'value': "Taux d'utilisation moyen du plafond (%)",
        'count': 'Nombre de clients',
    },
)

# Personnalisation du graphique
fig_repartition_ratio_plafond.update_layout(
    xaxis_title="Taux d'utilisation moyen du plafond sur 6 mois (%)",
    yaxis_title='Nombre de clients',
    height=500,
    showlegend=False,  # Masque la légende
)

fig_repartition_ratio_plafond.update_traces(
    marker_color=COULEURS["turquoise"], marker_line_color='white', marker_line_width=0.5
)

# Affichage du graphique
st.plotly_chart(fig_repartition_ratio_plafond, width='stretch')
st.caption("Utilisation du plafond : facture du mois divisée par le plafond, écrêtée entre 0 et 200 %, puis moyenne des 6 mois. Les utilisations moyennes de plus de 120 % sont regroupées dans la dernière barre.")

st.markdown(f"""
Une grande partie des clients utilise très peu son crédit, les autres s'étalent sur toute l'échelle, jusqu'au plafond et au-delà. Aux deux extrémités : {nombre_fr(nb_clients_zero)} clients ont une utilisation moyenne de 0 %, et {nombre_fr(nb_clients_sup_120)} dépassent en moyenne 120 % de leur plafond.
""")

# ------------------------------------------------------------------------------
st.subheader("Une utilisation qui augmente mois après mois", anchor="evolution-utilisation")
# 1. Alignement direct : du plus ancien (M-6 / ratio 6) au plus récent (M-1 / ratio 1)
mapping = [
    ('M-6 (avril)', 'ratio_BILL_LIMIT6'),
    ('M-5 (mai)', 'ratio_BILL_LIMIT5'),
    ('M-4 (juin)', 'ratio_BILL_LIMIT4'),
    ('M-3 (juil.)', 'ratio_BILL_LIMIT3'),
    ('M-2 (août)', 'ratio_BILL_LIMIT2'),
    ('M-1 (sept.)', 'ratio_BILL_LIMIT1')
]

labels = []
medianes_ratio_BILL_LIMIT = []

# 2. Calcul séquentiel
for label, col in mapping:
    if col in df.columns:
        labels.append(label)
        medianes_ratio_BILL_LIMIT.append(df[col].median())

# 3. Tracé avec Plotly
fig5 = go.Figure()

# Ajout de la ligne principale
fig5.add_trace(go.Scatter(
    x=labels,
    y=medianes_ratio_BILL_LIMIT,
    mode='lines+markers+text',
    line=dict(color=COULEURS["mauve"], width=3),
    marker=dict(size=8),
    text=[f'{nombre_fr(val, 1)} %' for val in medianes_ratio_BILL_LIMIT],
    textposition="top center",
    textfont=dict(size=TAILLE_ETIQUETTE, weight='bold')
))

# Configuration de l'axe Y pour avoir une échelle adaptée
max_y = max(medianes_ratio_BILL_LIMIT) if medianes_ratio_BILL_LIMIT else 100
min_y = min(medianes_ratio_BILL_LIMIT) if medianes_ratio_BILL_LIMIT else 0
fig5.update_layout(
    xaxis_title='Mois',
    yaxis_title='Utilisation médiane du plafond (%)',
    height=500,
    showlegend=False,
    yaxis=dict(range=[min_y * 0.9, max_y * 1.1]),  # Ajout d'un espace en haut
)

st.plotly_chart(fig5, width='stretch')

st.markdown(f"""
Hausse constante de l'utilisation du crédit sur les 6 mois : l'utilisation médiane du plafond passe de **{nombre_fr(medianes_ratio_BILL_LIMIT[0], 1)} %** en avril à **{nombre_fr(medianes_ratio_BILL_LIMIT[-1], 1)} %** en septembre. Les clients s'endettent davantage d'un mois à l'autre, en pleine crise des cartes de crédit. Mais qui utilise le plus son crédit ?
""")

# ------------------------------------------------------------------------------
st.subheader("Les petits plafonds sont les plus utilisés", anchor="utilisation-plafond")

df_filtered = df.copy()

# Création des tranches de plafond (mêmes tranches que le taux de défaut selon le plafond)
bin_size = 10000
bins = np.arange(1, 500001 + bin_size, bin_size)
labels = [f'{i//1000}k-{(i+bin_size)//1000}k' for i in bins[:-1]]

# Assigner chaque client à une tranche
df_filtered['LIMIT_BAL_bin'] = pd.cut(df_filtered['LIMIT_BAL'],
                                      bins=bins, labels=labels, right=False)

# Calculer le taux d'utilisation médian par tranche
usage_by_bin = df_filtered.groupby('LIMIT_BAL_bin', observed=False)['ratio_BILL_LIMIT1'].median().reset_index()

# Création du graphique avec Plotly
fig6 = go.Figure(data=[go.Bar(
    x=usage_by_bin['LIMIT_BAL_bin'],
    y=usage_by_bin['ratio_BILL_LIMIT1'],
    marker_color=COULEURS["violet"],
    hovertemplate="Plafond de %{x} NT$ : %{y:.1f} %<extra></extra>",
)])

# Personnalisation du graphique
fig6.update_layout(
    xaxis_title='Tranche de plafond (NT$)',
    yaxis_title='Utilisation médiane du plafond en septembre (%)',
    height=500,
    # Un repère tous les 50 000 NT$ (une tranche sur cinq) au lieu de chaque tranche, pour la lisibilité
    xaxis=dict(tickmode='array', tickvals=labels[::5], ticktext=[f"{k * 10} k" for k in range(0, 50, 5)], tickangle=0),
    separators=", ",
)

st.plotly_chart(fig6, width='stretch')

util_petits = df.loc[df['LIMIT_BAL'] <= 150000, 'ratio_BILL_LIMIT1'].median()
util_grands = df.loc[df['LIMIT_BAL'] >= 200000, 'ratio_BILL_LIMIT1'].median()
st.markdown(f"""
En septembre, les plus petits plafonds sont les plus utilisés : utilisation médiane de **{nombre_fr(util_petits, 1)} %** jusqu'à 150 000 NT\\$, contre **{nombre_fr(util_grands, 1)} %** à partir de 200 000 NT\\$. On a vu que les petits plafonds sont les plus risqués : est-ce le montant du plafond qui compte, ou l'usage qu'en fait le client ?
""")

# ------------------------------------------------------------------------------
st.subheader("Plus le plafond est utilisé, plus le taux de défaut est élevé", anchor="defaut-utilisation")

ratio_cols = [f"ratio_BILL_LIMIT{i}" for i in range(1, 7)]

df_ratio = df.copy()

# Calcul du ratio moyen par client sur les 6 mois
df_ratio["ratio_mean_client"] = df_ratio[ratio_cols].mean(axis=1)

# Utilisation de -inf et +inf pour inclure tous les profils (ex: négatifs ou > 200%)
bins = [-np.inf, 0.0, 10, 30, 50, 70, 90, 110, np.inf]
labels = [
    "0%",
    ">0-10%",
    "10-30%",
    "30-50%",
    "50-70%",
    "70-90%",
    "90-110%",
    ">110%",
]

df_ratio["ratio_mean_bin"] = pd.cut(
    df_ratio["ratio_mean_client"],
    bins=bins,
    labels=labels,
    include_lowest=True,
)

# Agrégation : effectifs et taux de défaut moyen
stats_defaut = (
    df_ratio.groupby("ratio_mean_bin", observed=False)["dpnm"]
    .agg(nb_clients="count", taux_defaut=lambda x: x.mean() * 100)
    .reset_index()
)

stats_defaut["taux_defaut"] = stats_defaut["taux_defaut"].fillna(0)

fig_defaut_ratio_plafond = go.Figure()

fig_defaut_ratio_plafond.add_trace(
    go.Bar(
        x=stats_defaut["ratio_mean_bin"],
        y=stats_defaut["taux_defaut"],
        marker_color=COULEURS["rouge_pale"],
        hoverinfo="skip",
    )
)

# Taux de défaut moyen en pointillés orange ; valeurs dans de petites étiquettes, devant la ligne (comme en 4.1)
fig_defaut_ratio_plafond.add_hline(y=taux_moyen, line_dash="dash", line_width=2, line_color=COULEURS["orange"])
for _, row in stats_defaut.iterrows():
    fig_defaut_ratio_plafond.add_annotation(
        x=row["ratio_mean_bin"], y=row["taux_defaut"], yshift=20, showarrow=False,
        text=f"<b>{nombre_fr(row['taux_defaut'], 1)} %<br>({nombre_fr(row['nb_clients'])} clients)</b>",
        bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2, font_size=TAILLE_ETIQUETTE,
    )

fig_defaut_ratio_plafond.update_layout(
    xaxis_title="Tranche d'utilisation moyenne du plafond sur 6 mois",
    yaxis_title="Taux de défaut (%)",
    yaxis_range=[0, max(stats_defaut["taux_defaut"]) * 1.3],
    height=500,
    showlegend=False,
)

st.plotly_chart(fig_defaut_ratio_plafond, width='stretch')

zero = stats_defaut.iloc[0]
bas = stats_defaut.iloc[2]
haut = stats_defaut.iloc[-2]
st.markdown(f"""
La tendance est claire : au-delà d'une utilisation faible, plus un client utilise son plafond, plus son taux de défaut augmente, de **{nombre_fr(bas['taux_defaut'], 1)} %** entre 10 et 30 % d'utilisation à **{nombre_fr(haut['taux_defaut'], 1)} %** entre 90 et 110 %.

**La première barre est à part.** Ses {nombre_fr(zero['nb_clients'])} clients n'ont eu aucune facture positive sur les 6 mois : ils ont payé pendant la période alors que rien n'était dû, ce qui laisse des soldes créditeurs (page « 3.2 Les montants »). Ils ne doivent rien à la banque, et pourtant {nombre_fr(zero['nb_clients'] * zero['taux_defaut'] / 100)} d'entre eux sont notés en défaut en octobre. Pour ces clients, le défaut ne peut pas venir d'une facture impayée. Deux explications sont possibles, sans qu'aucune ne puisse être vérifiée, la définition de la cible n'étant pas documentée (page « 1. Les données ») :
- **un artefact** : une valeur 1 posée dans la cible sans avoir été vérifiée à la date d'extraction du fichier ;
- **un autre sens du mot « défaut »** pour la banque : une clôture administrative du compte, une saisie, une faillite personnelle, c'est-à-dire un événement de gestion plutôt qu'un retard de paiement.

Ce petit groupe ne reflète donc pas la tendance, et il rappelle que la cible elle-même doit être lue avec prudence.
""")

st.info("""
**Ce que révèle l'usage du crédit** : le montant du plafond seul n'explique pas le risque. Les petits plafonds sont plus risqués, mais ce sont aussi les plus utilisés ; et plus un client utilise son crédit, plus son taux de défaut est élevé. L'utilisation du plafond, qui augmente mois après mois, est un signal de risque plus parlant que le plafond lui-même.
""")
