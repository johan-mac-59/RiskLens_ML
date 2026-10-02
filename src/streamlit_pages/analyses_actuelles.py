from streamlit_pages.commun import *

df = load_data()
mappings = load_mappings()

# Les graphiques démographiques, le profil « critique » et le simulateur sont passés en 4.1 (p4_1_population.py)

st.subheader("Analyse des plafonds de crédit, leur utilisation et leurs liens avec le défaut de paiement")
st.markdown("#### Répartition des plafonds")

# Histogramme complet avec Plotly
fig1 = px.histogram(df['LIMIT_BAL'].dropna(), nbins=100, 
                    labels={'value': 'Montant du plafond (NT$)', 'count': 'Nombre de clients'})
fig1.update_traces(marker_color='#1f77b4', marker_line_color='white', marker_line_width=0.5)
fig1.update_layout(xaxis_title='Montant du plafond (NT$)', 
                xaxis_range=[0, 1030000],
                yaxis_title='Nombre de clients',
                showlegend=False,
                height=600)

# Formatage des axes X pour afficher les nombres complets avec espaces
fig1.update_xaxes(tickformat=',.0f', tickprefix=' ', tickangle=0)

# Ajout des lignes de moyenne et médiane
mean_val = df['LIMIT_BAL'].mean()
median_val = df['LIMIT_BAL'].median()

fig1.add_vline(x=mean_val, line_color="#ff7f0e", line_dash="dash", 
            annotation_text=f"Moyenne: {int(mean_val):,}".replace(',', ' '), 
            annotation_position="top right")

fig1.add_vline(x=median_val, line_color="#2ca02c", line_dash="dash", 
            annotation_text=f"Médiane: {int(median_val):,}".replace(',', ' '), 
            annotation_position="top left")

st.plotly_chart(fig1, width='stretch')

st.markdown(
rf"Le plafond moyen de crédit est de {f'{mean_val:,.0f}'.replace(',', ' ')} NT\$ et la médiane se situe à {f'{median_val:,.0f}'.replace(',', ' ')} NT\$."
)
total_clients = len(df)
clients_inf_500k = len(df[df['LIMIT_BAL'] <= 500000])
pourcentage = (clients_inf_500k / total_clients) * 100
st.markdown(f"Sur un total de {total_clients:,} clients, {clients_inf_500k:,} clients ont un plafond de crédit ≤ 500 000 NT$ ({pourcentage:.2f}%)")


# Histogramme du taux de dpnm par tranches de plafond
st.markdown('---')   
st.markdown("#### Le taux de défaut selon le montant autorisé de crédit")

if "dpnm" in df.columns:
    bin_size = 20000
    bins = np.arange(1, 1000001 + bin_size, bin_size)
    labels = [f"{i//1000}k-{(i+bin_size)//1000}k" for i in bins[:-1]]

    df["LIMIT_BAL_interval"] = pd.cut(
        df["LIMIT_BAL"], bins=bins, labels=labels, right=False
    )

    # Calcul simultané des taux et des effectifs
    grouped = df.groupby("LIMIT_BAL_interval", observed=False)["dpnm"]
    counts = grouped.count()
    rates = grouped.mean() * 100
    rates_values = rates.fillna(0).values

    # 1. Étiquette affichée UNIQUEMENT si 0 client
    text_labels = ["0 client" if count == 0 else "" for count in counts]

    # 2. Attribution dynamique des couleurs (Vert si 0% avec clients)
    colors = []
    for count, rate in zip(counts, rates):
        if count == 0:
            colors.append("#d3d3d3")  # Gris clair (pas de client)
        elif rate == 0:
            colors.append("#2ca02c")  # Vert pour 0% de défaut
        else:
            colors.append("#ff7f0e")  # Orange pour taux > 0%

    fig3 = go.Figure(
        data=[
            go.Bar(
                x=rates.index,
                y=rates_values,
                marker_color=colors,
                marker_line_color=colors,  # Rendre le trait à 0% bien net
                marker_line_width=2,
                text=text_labels,
                textposition="outside",
                textfont=dict(size=10, color="#7f7f7f"),
            )
        ]
    )

    max_y = max(rates_values) * 1.25 if max(rates_values) > 0 else 30

    # 3. L'axe Y démarre à -1%
    fig3.update_layout(
        xaxis_title="Intervalle de montant de crédit",
        yaxis_title="Taux de défaut mois suivant(%)",
        xaxis_tickangle=-45,
        yaxis_range=[-1, max_y],
        height=600,
    )

    st.plotly_chart(fig3, width='stretch')
else:
    st.error("Aucune colonne 'dpnm' trouvée dans le DataFrame")

st.markdown("""
On constate un taux de défaut moyen qui a tendance à baisser jusqu'à 500 000 NT$ de crédit autorisé.  
Au-delà, le nombre de clients est trop faible pour établir une tendance, le taux de défaut oscille entre 0 et 25% avec un nombre très faible et parfois nul par tranche de plafond.
""")
st.markdown('---')   
st.markdown("#### Focus sur les plafonds les plus courants")

# Histogramme de répartition des plafond <= 500000
df_filtered = df[df['LIMIT_BAL'] <= 500000]
fig2 = px.histogram(df_filtered['LIMIT_BAL'].dropna(), nbins=50,
                    labels={'value': 'Montant du plafond (NT$)', 'count': 'Nombre de clients'})
fig2.update_traces(marker_color='#1f77b4', marker_line_color='white', marker_line_width=0.5)
fig2.update_layout(xaxis_title='Montant du plafond (NT$)',
                yaxis_title='Nombre de clients',
                xaxis_range=[0, 510000],
                showlegend=False,
                height=600)

# Formatage des axes X pour afficher les nombres complets avec espaces
fig2.update_xaxes(tickformat=',.0f', tickprefix=' ', tickangle=0)

# Ajout des lignes de moyenne et médiane
mean_val = df_filtered['LIMIT_BAL'].mean()
median_val = df_filtered['LIMIT_BAL'].median()

fig2.add_vline(x=mean_val, line_color="#ff7f0e", line_dash="dash", 
            annotation_text=f"Moyenne: {int(mean_val):,}".replace(',', ' '), 
            annotation_position="top right")

fig2.add_vline(x=median_val, line_color="#2ca02c", line_dash="dash", 
            annotation_text=f"Médiane: {int(median_val):,}".replace(',', ' '), 
            annotation_position="top left")

st.plotly_chart(fig2, width='stretch')

# Histogramme du taux de dpnm par tranches de plafond <= 500000
st.markdown('---')   
st.markdown("#### Le taux de défaut selon le montant autorisé de crédit (≤ 500 000 NT$)")

df_filtered = df[df['LIMIT_BAL'] <= 500000].copy()

if 'dpnm' in df_filtered.columns:
    # Tranches de 10 000 NT$ pour garder un détail fin (50 barres)
    bin_size = 10000
    bins = np.arange(1, 500001 + bin_size, bin_size)
    labels = [f'{i//1000}k-{(i+bin_size)//1000}k' for i in bins[:-1]]

    df_filtered['LIMIT_BAL_interval'] = pd.cut(
        df_filtered['LIMIT_BAL'], bins=bins, labels=labels, right=False
    )

    # observed=False conserve toutes les tranches jusqu'à 500k, même si sans clients
    default_rates = (
        df_filtered.groupby('LIMIT_BAL_interval', observed=False)['dpnm'].mean()
        * 100
    )

    # Remplace les NaN (tranches sans clients) par 0
    rates_values = default_rates.fillna(0).values

    fig4 = go.Figure(
        data=[
            go.Bar(
                x=default_rates.index,
                y=rates_values,
                marker_color='#ff7f0e'
            )
        ]
    )

    max_y = (
        max(rates_values) * 1.25
        if len(rates_values) > 0 and max(rates_values) > 0
        else 30
    )

    fig4.update_layout(
        xaxis_title='Intervalle de montant de crédit (LIMIT_BAL)',
        yaxis_title='Taux de défaut mois suivant (%)',
        xaxis_tickangle=-45,
        # Sol à -1 pour faire ressortir les barres à 0%
        yaxis_range=[-1, max_y],
        height=600,
    )

    st.plotly_chart(fig4, width='stretch')
    
else:
    st.error("Aucune colonne 'dpnm' trouvée dans le DataFrame")
    st.write("Colonnes disponibles :", df_filtered.columns.tolist())

st.markdown("La tendance baissière du risque est bien visible sur le graphique ci-dessus.")

st.markdown('---')   
st.markdown("#### Répartition du taux moyen d'utilisation du plafond")

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
    xaxis_title="Taux d'utilisation moyen du plafond (%)",
    yaxis_title='Nombre de clients',
    height=600,
    showlegend=False,  # Masque la légende
)

fig_repartition_ratio_plafond.update_traces(
    marker_color='#1f77b4', marker_line_color='white', marker_line_width=0.5
)

# Affichage du graphique
st.plotly_chart(fig_repartition_ratio_plafond, width='stretch')

st.markdown(f"""
dont :  
- Nombre de clients avec une utilisation moyenne à 0% : {nb_clients_zero}
- Nombre de clients avec une utilisation moyenne supérieure à 120% : {nb_clients_sup_120}          
            """)
 
st.markdown('---')   
st.markdown("#### Evolution du ratio d'utilisation du plafond de crédit")
# 1. Alignement direct : du plus ancien (M-6 / ratio 6) au plus récent (M-1 / ratio 1)
mapping = [
('M-6', 'ratio_BILL_LIMIT6'),
('M-5', 'ratio_BILL_LIMIT5'),
('M-4', 'ratio_BILL_LIMIT4'),
('M-3', 'ratio_BILL_LIMIT3'),
('M-2', 'ratio_BILL_LIMIT2'),
('M-1', 'ratio_BILL_LIMIT1')
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
    line=dict(color='#1f77b4', width=3),
    marker=dict(size=8),
    text=[f'{val:.2f}%' for val in medianes_ratio_BILL_LIMIT],
    textposition="top center",
    textfont=dict(size=14, weight='bold')
))

# Configuration de l'axe Y pour avoir une échelle adaptée
max_y = max(medianes_ratio_BILL_LIMIT) if medianes_ratio_BILL_LIMIT else 100
min_y = min(medianes_ratio_BILL_LIMIT) if medianes_ratio_BILL_LIMIT else 0
fig5.update_layout(
    xaxis_title='Mois',
    yaxis_title='Ratio médian d\'utilisation (%)',
    height=600,
    showlegend=False,
    yaxis=dict(
        range=[min_y*0.9, max_y * 1.1],  # Ajout d'un espace en haut
        gridcolor='lightgray',
        gridwidth=1,
        griddash='dot'  # Style de ligne pointillée pour moins de visibilité
    ),
    xaxis=dict(
        gridcolor='lightgray',
        gridwidth=1,
        griddash='dot'
    )
)

# Ajout de la grille
fig5.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig5.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

st.plotly_chart(fig5, width='stretch')

st.markdown("Hausse constante du ratio d'utilisation de crédit sur les 6 derniers mois.")
st.markdown("Mais qui utilise le plus son crédit ?")

# Taux d'utilisation médian par tranches de plafond de crédit
st.markdown('---')   
st.markdown("#### Taux d'utilisation médian selon le montant du plafond de crédit")

# Filtrer les données pour les clients avec plafond <= 500000
df_filtered = df[df['LIMIT_BAL'] <= 500000]

# Vérifier si la colonne existe
if 'ratio_BILL_LIMIT1' in df_filtered.columns:
    # Création des tranches de plafond
    bin_size = 10000
    bins = np.arange(1, 500002, bin_size)  # Commence à 0 au lieu de 1
    labels = [f'{i}-{i+bin_size-1}' for i in bins[:-1]]
    
    # Assigner chaque client à une tranche
    df_filtered['LIMIT_BAL_bin'] = pd.cut(df_filtered['LIMIT_BAL'], 
                                        bins=bins, labels=labels, right=False)
    
    # Calculer le taux d'utilisation médian par tranche
    usage_by_bin = df_filtered.groupby('LIMIT_BAL_bin')['ratio_BILL_LIMIT1'].median().reset_index()
    
    # Création du graphique avec Plotly
    fig6 = go.Figure(data=[go.Bar(
        x=usage_by_bin['LIMIT_BAL_bin'],
        y=usage_by_bin['ratio_BILL_LIMIT1'],
        marker_color='#9932CC'
    )])
    
    # Personnalisation du graphique
    fig6.update_layout(
        title='Taux d\'utilisation du plafond par tranches de plafond (dernier mois)',
        xaxis_title='Tranches de plafond (NT$)',
        yaxis_title='Taux d\'utilisation médian (%)',
        height=600,
        xaxis_tickangle=-45
    )
    
    # Gestion explicite des ticks pour s'assurer que tous les intervalles s'affichent
    fig6.update_xaxes(
        tickvals=list(range(len(usage_by_bin))),
        ticktext=usage_by_bin['LIMIT_BAL_bin'],
        tickangle=-45
    )
    
    st.plotly_chart(fig6, width='stretch')
    
else:
    st.error("La colonne 'ratio_BILL_LIMIT1' n'existe pas dans le DataFrame")
    st.write("Colonnes disponibles :", df_filtered.columns.tolist())

st.markdown("Sur le dernier mois, les crédits les plus petits (jusque 150 000 NT$) sont les plus utilisés en ratio.")
st.markdown("A partir de 200 000 NT$, les utilisations deviennent très faibles")
st.markdown("On a vu que les crédits de plus petits montants sont les plus risqués, mais est-ce la bonne variable à mettre en corrélation avec le défaut de paiement ?")

st.markdown('---')   
st.markdown("#### Taux de défaut de paiement selon l'utilisation moyenne du plafond")

ratio_cols = [f"ratio_BILL_LIMIT{i}" for i in range(1, 7)]

# Vérification de la présence des colonnes nécessaires
if all(col in df.columns for col in ratio_cols) and "dpnm" in df.columns:
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

    # Étiquettes personnalisées au-dessus des barres
    text_labels = [
        f"{row['taux_defaut']:.1f}%<br>(n={int(row['nb_clients'])})"
        for _, row in stats_defaut.iterrows()
    ]

    fig_defaut_ratio_plafond = go.Figure()

    fig_defaut_ratio_plafond.add_trace(
        go.Bar(
            x=stats_defaut["ratio_mean_bin"],
            y=stats_defaut["taux_defaut"],
            marker_color='#ff7f0e',
            text=text_labels,
            textposition="outside",
            textfont=dict(size=14),
        )
    )

    max_y = (
        max(stats_defaut["taux_defaut"]) * 1.25
        if max(stats_defaut["taux_defaut"]) > 0
        else 30
    )

    fig_defaut_ratio_plafond.update_layout(
        xaxis_title="Tranche d'utilisation moyenne sur 6 mois (%)",
        yaxis_title="Taux de défaut mois suivant(%)",
        height=600,
        showlegend=False,
    )

    # Affichage Streamlit adaptatif
    st.plotly_chart(fig_defaut_ratio_plafond, width='stretch')
else:
    st.error(
    "Colonnes de ratio ou colonne cible 'dpnm' manquantes dans le DataFrame."
    ) 

st.markdown("""
Malgré les nettoyages effectués sur le jeu de données, des artéfacts subsistent avec des encours nuls ou négatifs qui ressortent en paiement (ici 106 clients concernés). Il s'agit évidemment d'une donnée à ne pas prendre en compte pour regarder la tendance.  
La tendance est claire : plus un client utilise son autorisation de crédit, plus son taux de défaut augmente.  
**Le seul montant du plafond ne peut pas expliquer le risque de crédit, on voit ici que le ratio de son utilisation est également en corrélation forte avec le risque d'impayé futur.**
""")

st.markdown('---')
st.subheader("🚧 Analyse du comportement de paiement en cours")
