from streamlit_pages.commun import *

df = load_data()
mappings = load_mappings()

# ==============================================================================
# SECTION 2 : ANALYSE & INSIGHTS
# ==============================================================================
st.title("📊 Analyse Exploratoire & Insights")
st.subheader("L'analyse par segments démographiques révèle des signaux forts :")

# Mappings métiers
sex_map = mappings.get("genre", {})
marriage_map = mappings.get("statut_marital", {})
education_map = mappings.get("niveau_scolaire", {})

# Dispositions en grille 2x2
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

# --- 1. TRANCHE D'ÂGE ---
with row1_col1:
    st.markdown("#### 📈 Le Risque par Tranche d'Âge")
    df_age = df.copy()

    # Binning automatique si la colonne AGE_BUCKET n'est pas pré-calculée
    if "AGE_BUCKET" not in df_age.columns and "AGE" in df_age.columns:
        # Mêmes buckets que dans 05_03_EDA_storytelling (intervalles fermés à droite : 21-25, 26-30, ...)
        age_bins = [20, 25, 30, 35, 40, 50, 80]
        age_labels = ['21-25', '26-30', '31-35', '36-40', '41-50', '51+']
        df_age["AGE_BUCKET"] = pd.cut(
            df_age["AGE"], bins=age_bins, labels=age_labels, include_lowest=True
        )

    if "AGE_BUCKET" in df_age.columns:
        rates_age = (
            df_age.groupby("AGE_BUCKET", observed=True)["dpnm"].mean() * 100
        ).reset_index()
        rates_age.columns = ["Tranche", "Taux"]

        fig_age = px.bar(
            rates_age,
            x="Tranche",
            y="Taux",
            labels={"Tranche": "Tranche d'âge", "Taux": "Taux de défaut mois suivant (%)"},
            color="Tranche",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_age.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
        fig_age.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            yaxis_range=[0, max(rates_age["Taux"]) * 1.25],
            height=380,
        )
        st.plotly_chart(fig_age, width='stretch')
    else:
        st.info("Données d'âge indisponibles.")

# --- 2. NIVEAU SCOLAIRE ---
with row1_col2:
    st.markdown("#### 🎓 Impact du Niveau Scolaire")
    if "EDUCATION" in df.columns:
        df_edu = df[df["EDUCATION"].isin(education_map.keys())].copy()
        rates_edu = (
            df_edu.groupby("EDUCATION", observed=True)["dpnm"].mean() * 100
        ).reset_index()
        rates_edu["Niveau"] = rates_edu["EDUCATION"].map(education_map)

        fig_edu = px.bar(
            rates_edu,
            x="Niveau",
            y="dpnm",
            labels={"Niveau": "Éducation", "dpnm": "Taux de défaut mois suivant (%)"},
            color="Niveau",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_edu.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
        fig_edu.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            yaxis_range=[0, max(rates_edu["dpnm"]) * 1.25],
            height=380,
        )
        st.plotly_chart(fig_edu, width='stretch')
    else:
        st.info("Données d'éducation indisponibles.")

# --- 3. GENRE ---
with row2_col1:
    st.markdown("#### 👫 Le Risque par Genre")
    if "SEX" in df.columns:
        df_sex = df[df["SEX"].isin(sex_map.keys())].copy()
        rates_sex = (
            df_sex.groupby("SEX", observed=True)["dpnm"].mean() * 100
        ).reset_index()
        rates_sex["Genre"] = rates_sex["SEX"].map(sex_map)

        fig_sex = px.bar(
            rates_sex,
            x="Genre",
            y="dpnm",
            labels={"Genre": "Genre", "dpnm": "Taux de défaut mois suivant (%)"},
            color="Genre",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_sex.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
        fig_sex.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            yaxis_range=[0, max(rates_sex["dpnm"]) * 1.25],
            height=380,
        )
        st.plotly_chart(fig_sex, width='stretch')
    else:
        st.info("Données de genre indisponibles.")

# --- 4. STATUT MARITAL ---
with row2_col2:
    st.markdown("#### 💍 Impact du Statut Marital")
    if "MARRIAGE" in df.columns:
        df_mar = df[df["MARRIAGE"].isin(marriage_map.keys())].copy()
        rates_mar = (
            df_mar.groupby("MARRIAGE", observed=True)["dpnm"].mean() * 100
        ).reset_index()
        rates_mar["Statut"] = rates_mar["MARRIAGE"].map(marriage_map)

        fig_mar = px.bar(
            rates_mar,
            x="Statut",
            y="dpnm",
            labels={"Statut": "Statut", "dpnm": "Taux de défaut mois suivant (%)"},
            color="Statut",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_mar.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
        fig_mar.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            yaxis_range=[0, max(rates_mar["dpnm"]) * 1.25],
            height=380,
        )
        st.plotly_chart(fig_mar, width='stretch')
    else:
        st.info("Données de mariage indisponibles.")

st.markdown("---")
st.subheader("🚩 Le Profil 'Critique'")
st.warning("""
Au premier abord, les données personnelles semblaient dénués d'intéret et le [tableau de corrélation](https://raw.githubusercontent.com/johan-mac-59/RiskLens_ML/main/images/heatmap_demographique.png) ne montrait rien, mais en regardant de plus près on constate des tendances :
- Les profils jeunes, de genre masculin, mariés, avec un niveau scolaire plus faible semblent avoir un taux de défaut sensiblement supérieur au reste de la population  **
""")
st.markdown("""
Je regarde les facteurs et je les cumule :
- Taux de défaut moyen de **28%** pour les clients âgés de 25 ans et moins, possédant un bac ou une license
- Taux de défaut moyen de **32%** pour les clients âgés de 25 ans et moins, possédant un bac ou une license, mariés
- Taux de défaut moyen de **36%** pour les clients âgés de 25 ans et moins, possédant un bac ou une license, mariés, et de sexe masculin **MAIS représente seulement 53 individus**

Si on regarde ces 4 facteurs inversés :
- Taux de défaut moyen de **16%** pour un individu de sexe féminin, célibataire, âgé de plus de 25 ans et possédant un doctorat/master, avec une **population de 3246 individus**

En conclusion, nous observons une disparité majeure de risque selon le profil : le taux de défaut peut varier de 16% à 36% selon la combinaison des facteurs démographiques. Bien que le segment à haut risque soit numériquement faible, l'écart de risque est significatif, ce qui justifie l'intégration de ces variables dans mon futur modèle de scoring.
""")


# ==============================================================================
# CALCULATEUR INTERACTIF RÉEL : TAUX DE DÉFAUT PAR PROFIL
# ==============================================================================
st.markdown("---")
st.subheader("🧮 Simulateur de Risque par Profil Démographique")
st.markdown("Vous aussi, calculez le taux de défaut de paiement selon les critères démographiques choisis en direct sur la base de données")

col_sim1, col_sim2 = st.columns([1, 1])

with col_sim1:
    st.info("Sélectionnez les critères du client hypothétique.")
    
    # Conversion sécurisée des clés en entiers
    genre_map = {int(k): v for k, v in mappings.get("genre", {}).items()}
    marital_map = {int(k): v for k, v in mappings.get("statut_marital", {}).items()}
    scolaire_map = {int(k): v for k, v in mappings.get("niveau_scolaire", {}).items()}
    defaut_map = {int(k): v for k, v in mappings.get("statut_defaut", {}).items()}
    
    # Choix Âge : on offre des tranches
    age_tranches = [
        ("Tous âges", 0, 100),
        ("21-25 ans", 21, 25),
        ("26-30 ans", 26, 30),
        ("31-35 ans", 31, 35),
        ("36-40 ans", 36, 40),
        ("41-50 ans", 41, 50),
        ("51-+", 51, 80)
    ]
    
    selected_tranche = st.selectbox(
        "Tranche d'âge", 
        options=[t[0] for t in age_tranches],
        format_func=lambda x: x
    )
    
    # On récupère les bornes de la tranche sélectionnée
    age_min, age_max = next((t[1], t[2]) for t in age_tranches if t[0] == selected_tranche)

    # Genre
    genre_options = [-1] + list(genre_map.keys())
    selected_genre = st.selectbox(
        "Genre", 
        options=genre_options, 
        format_func=lambda x: f"{genre_map.get(x, 'Tous les genres')} ({x})" if x != -1 else "Tous les genres"
    )

with col_sim2:
    # Scolaire
    edu_options = [-1] + list(scolaire_map.keys())
    selected_edu = st.selectbox(
        "Niveau Scolaire", 
        options=edu_options, 
        format_func=lambda x: f"{scolaire_map.get(x, 'Tous niveaux')} ({x})" if x != -1 else "Tous niveaux"
    )

    # Mariage
    marital_options = [-1] + list(marital_map.keys())
    selected_marital = st.selectbox(
        "Statut Marital", 
        options=marital_options, 
        format_func=lambda x: f"{marital_map.get(x, 'Tous statuts')} ({x})" if x != -1 else "Tous statuts"
    )

# Bouton de calcul
if st.button("🔍 Calculer le taux de défaut", type="primary", width='stretch'):
    
    # Préparation des paramètres pour l'API
    params = {}
    if selected_genre != -1:
        params["gender_code"] = selected_genre
    if selected_edu != -1:
        params["education_level"] = selected_edu
    if selected_marital != -1:
        params["marital_status"] = selected_marital
    
    # Ajout des tranches d'âge
    params["age_min"] = age_min
    params["age_max"] = age_max

    try:
        with st.spinner("Interrogation de la BDD en temps réel..."):
            res = requests.get(f"{API_URL}/analyze/risk-by-profile", params=params, timeout=API_TIMEOUT)
            
            if res.status_code == 200:
                data = res.json()
                
                if "error" in data:
                    st.error(f"Erreur API : {data['error']}")
                elif data["total_clients"] == 0:
                    st.warning("Aucun client ne correspond exactement à ces critères combinés. Essayez d'élargir les tranches.")
                else:
                    # Affichage des résultats
                    col_res1, col_res2 = st.columns(2)
                    
                    with col_res1:
                        st.metric(
                            label="Nombre de clients ciblés",
                            value=f"{data['total_clients']}"
                        )
                    
                    with col_res2:
                        risk_pct = data['default_rate_pct']
                        
                        st.metric(
                            label="Taux de défaut observé",
                            value=f"{risk_pct}%",
                            delta_color="inverse" # Rouge si haut, vert si bas
                        )
                    
                    st.info(f"Sur ces {data['total_clients']} clients, **{data['defaut_count']}** ont présenté un défaut de paiement le mois suivant.")
                    
                    # Visualisation contextuelle simple
                    if risk_pct:
                        # On ajoute une barre visuelle pour comparer à la moyenne globale de la BDD
                        global_avg = load_global_default_rate()
                        col_viz1, col_viz2 = st.columns([3, 1])
                        with col_viz1:
                            st.progress(risk_pct/100, f"Risque du profil ({risk_pct}%) vs Moyenne ({global_avg}%)")
                        with col_viz2:
                            delta_val = risk_pct - global_avg
                            st.metric(label="Écart à la moyenne", value=f"{delta_val:+.1f}%")

            else:
                st.error(f"Impossible de joindre l'API pour le calcul. Code erreur : {res.status_code}")
                # Afficher les détails de l'erreur si disponible
                try:
                    error_data = res.json()
                    st.error(f"Détails de l'erreur : {error_data}")
                except:
                    st.error("Aucun détail d'erreur disponible")

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur réseau lors du calcul : {e}")
    except Exception as e:
        st.error(f"Erreur lors du calcul : {e}")
        import traceback
        st.text_area("Détails de l'erreur", value=traceback.format_exc(), height=200)
        

st.markdown('---')        
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
