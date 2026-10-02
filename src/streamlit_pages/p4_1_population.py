from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 4.1 : LE PROFIL DES CLIENTS
# Graphiques, profil « critique » et simulateur repris de la page « Analyses
# (version actuelle) » ; tous les chiffres sont calculés en direct sur le dataset.
# ==============================================================================
df = load_data()
mappings = load_mappings()

# Mappings métiers
sex_map = mappings.get("genre", {})
marriage_map = mappings.get("statut_marital", {})
education_map = {k: v.replace("License", "Licence") for k, v in mappings.get("niveau_scolaire", {}).items()}

# Tranches d'âge : mêmes buckets que dans 05_03_EDA_storytelling (intervalles fermés à droite : 21-25, 26-30, ...),
# utilisées par les graphiques et par le simulateur
age_bins = [20, 25, 30, 35, 40, 50, 80]
age_labels = ['21-25', '26-30', '31-35', '36-40', '41-50', '51+']
df["AGE_BUCKET"] = pd.cut(df["AGE"], bins=age_bins, labels=age_labels, include_lowest=True)

taux_moyen = df["dpnm"].mean() * 100

# Effectifs et taux de défaut par catégorie, communs aux deux grilles
rates_age = df.groupby("AGE_BUCKET", observed=True)["dpnm"].agg(["size", "mean"]).reset_index()
rates_age.columns = ["Tranche", "Clients", "Taux"]

df_sex = df[df["SEX"].isin(sex_map.keys())].copy()
rates_sex = df_sex.groupby("SEX", observed=True)["dpnm"].agg(["size", "mean"]).reset_index()
rates_sex.columns = ["SEX", "Clients", "Taux"]
rates_sex["Genre"] = rates_sex["SEX"].map(sex_map)

df_edu = df[df["EDUCATION"].isin(education_map.keys())].copy()
rates_edu = df_edu.groupby("EDUCATION", observed=True)["dpnm"].agg(["size", "mean"]).reset_index()
rates_edu.columns = ["EDUCATION", "Clients", "Taux"]
rates_edu["Niveau"] = rates_edu["EDUCATION"].map(education_map)

df_mar = df[df["MARRIAGE"].isin(marriage_map.keys())].copy()
rates_mar = df_mar.groupby("MARRIAGE", observed=True)["dpnm"].agg(["size", "mean"]).reset_index()
rates_mar.columns = ["MARRIAGE", "Clients", "Taux"]
rates_mar["Statut"] = rates_mar["MARRIAGE"].map(marriage_map)

for rates in (rates_age, rates_sex, rates_edu, rates_mar):
    rates["Taux"] = rates["Taux"] * 100
    rates["Part"] = rates["Clients"] / len(df) * 100

# Les quatre graphiques, à la même place dans les deux grilles (miroir) : âge, genre / études, statut marital
GRAPHIQUES = [
    ("Tranche d'âge", rates_age, "Tranche"),
    ("Genre", rates_sex, "Genre"),
    ("Niveau d'études", rates_edu, "Niveau"),
    ("Statut marital", rates_mar, "Statut"),
]


def grille(valeur):
    """Grille 2 × 2 : répartition des clients (valeur = « Part ») ou taux de défaut (valeur = « Taux »)."""
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    for col, (titre, rates, x) in zip((row1_col1, row1_col2, row2_col1, row2_col2), GRAPHIQUES):
        with col:
            st.markdown(f"#### {titre}")
            if valeur == "Part":
                # Répartition : disque, mêmes couleurs par catégorie que les barres du taux de défaut (même ordre)
                fig = px.pie(
                    rates,
                    names=x,
                    values="Clients",
                    color=x,
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig.update_traces(
                    sort=False, direction="clockwise", textinfo="label+percent", textposition="outside",
                    texttemplate="%{label}<br>%{percent:.1%}", textfont_size=14,  # 2 px de plus que la taille par défaut (12)
                    hovertemplate="%{label} : %{value} clients (%{percent:.1%})<extra></extra>",
                )
                fig.update_layout(showlegend=False, height=380, separators=", ", margin=dict(t=40, b=40, l=60, r=60))
            else:
                fig = px.bar(
                    rates,
                    x=x,
                    y=valeur,
                    labels={x: titre, valeur: "Taux de défaut (%)"},
                    color=x,
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                # Taux de défaut moyen : repère sans texte, au premier plan (la valeur est donnée dans le texte)
                fig.add_hline(y=taux_moyen, line_dash="dash", line_width=2, line_color=COULEURS["orange"])
                # Valeurs dans de petites étiquettes : les annotations s'affichent devant la ligne de moyenne
                for categorie, taux in zip(rates[x], rates["Taux"]):
                    fig.add_annotation(x=categorie, y=taux, text=f"{nombre_fr(taux, 1)} %", showarrow=False, yshift=12,
                                       bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2, font_size=13)
                fig.update_layout(
                    showlegend=False,
                    coloraxis_showscale=False,
                    yaxis_range=[0, max(rates[valeur]) * 1.25],
                    height=380,
                )
            st.plotly_chart(fig, width='stretch', key=f"{valeur}_{x}")


entete_partie_4(df)

st.markdown("---")
st.header("4.1 Le profil des clients : des écarts de risque réels, mais modérés", anchor="profil")
st.markdown("Le dataset décrit chaque client par quatre informations personnelles : son âge, son genre, son niveau d'études et son statut marital. Avant de regarder le risque, il faut savoir comment la clientèle se répartit : un taux de défaut élevé n'a pas le même poids sur un groupe de quelques centaines de clients que sur un groupe de plusieurs milliers.")

# ------------------------------------------------------------------------------
st.subheader("Qui sont les clients ?", anchor="repartition")
grille("Part")

majoritaires = []
for titre, rates, x in GRAPHIQUES:
    ligne = rates.loc[rates["Part"].idxmax()]
    majoritaires.append(f"{titre.lower()} : {ligne[x]} ({nombre_fr(ligne['Part'], 1)} %)")
st.markdown(f"""
La clientèle type est **jeune ou d'âge moyen, plutôt féminine et diplômée** : catégorie la plus représentée par variable, {", ".join(majoritaires)}. Les catégories « autres » du niveau d'études et du statut marital, regroupées au nettoyage (page « 3.5 Décisions »), ne pèsent chacune que quelques pourcents des clients.
""")

# ------------------------------------------------------------------------------
st.subheader("Le taux de défaut selon le profil", anchor="risque")
grille("Taux")

ecarts = []
for titre, rates, x in GRAPHIQUES:
    bas, haut = rates.loc[rates["Taux"].idxmin()], rates.loc[rates["Taux"].idxmax()]
    ecarts.append(f"- **{titre}** : de {nombre_fr(bas['Taux'], 1)} % ({bas[x]}) à {nombre_fr(haut['Taux'], 1)} % ({haut[x]})")
st.markdown(f"Pris un par un, les facteurs font varier le taux de défaut autour de la moyenne de {nombre_fr(taux_moyen, 1)} % (pointillés orange) :\n" + "\n".join(ecarts))
st.markdown("""
Les écarts existent, mais restent modérés : aucune information personnelle, prise seule, ne sépare nettement les clients à risque des autres. Les taux les plus extrêmes portent souvent sur les plus petits groupes, comme les catégories « autres », dont le taux est moins fiable.
""")

# ------------------------------------------------------------------------------
st.subheader("Cumuler les facteurs : des écarts plus nets, sur de petits groupes", anchor="profil-critique")


def profil(masque):
    """Effectif et taux de défaut d'un sous-groupe."""
    return masque.sum(), df.loc[masque, "dpnm"].mean() * 100


jeunes = (df["AGE"] <= 25) & df["EDUCATION"].isin([2, 3])
n1, t1 = profil(jeunes)
n2, t2 = profil(jeunes & (df["MARRIAGE"] == 1))
n3, t3 = profil(jeunes & (df["MARRIAGE"] == 1) & (df["SEX"] == 1))
n5, t5 = profil((df["AGE"] <= 25) & (df["EDUCATION"] == 3) & (df["MARRIAGE"] == 1) & (df["SEX"] == 1))
n4, t4 = profil((df["SEX"] == 2) & (df["MARRIAGE"] == 2) & (df["AGE"] > 25) & (df["EDUCATION"] == 1))

st.info("""
Au premier abord, les informations personnelles semblaient sans intérêt : le [tableau de corrélation](https://raw.githubusercontent.com/johan-mac-59/RiskLens_ML/main/images/heatmap_demographique.png) ne montrait rien. En regardant de plus près, des tendances apparaissent : les clients jeunes, hommes, mariés, avec un niveau d'études moins élevé, semblent avoir un taux de défaut sensiblement supérieur au reste de la population.
""")
st.markdown(f"""
Je regarde les facteurs et je les cumule :
- taux de défaut de **{nombre_fr(t1, 1)} %** pour les clients de 25 ans et moins, titulaires du baccalauréat ou d'une licence ({nombre_fr(n1)} clients) ;
- **{nombre_fr(t2, 1)} %** si, en plus, ils sont mariés ({nombre_fr(n2)} clients) ;
- **{nombre_fr(t3, 1)} %** si, en plus, ce sont des hommes, **mais pour seulement {nombre_fr(n3)} clients** ;
- **{nombre_fr(t5, 1)} %** pour les seuls titulaires du baccalauréat parmi eux, **mais pour {nombre_fr(n5)} clients seulement**.

Si on regarde ces 4 facteurs inversés, le taux de défaut tombe à **{nombre_fr(t4, 1)} %** pour les femmes célibataires de plus de 25 ans titulaires d'un master ou d'un doctorat ({nombre_fr(n4)} clients).

Le taux de défaut peut donc varier de {nombre_fr(t4, 0)} % à {nombre_fr(t3, 0)} % selon la combinaison des facteurs, et jusqu'à {nombre_fr(t5, 0)} % sur une poignée de clients, trop peu pour en tirer une règle. Le profil le plus risqué est numériquement faible, mais l'écart est net : ces informations ont leur place dans le futur modèle, en complément du comportement de paiement.
""")


# ==============================================================================
# CALCULATEUR INTERACTIF : TAUX DE DÉFAUT PAR PROFIL, CALCULÉ SUR LE DATASET
# (même interface que le simulateur de la démo de l'API, qui interroge la base)
# ==============================================================================
st.subheader("🧮 Simulateur de risque par profil", anchor="simulateur")
st.markdown(f"Vous aussi, calculez le taux de défaut de paiement selon les critères choisis, en direct sur les {nombre_fr(len(df))} clients étudiés.")

st.info("Sélectionnez les critères du client hypothétique.")
col_sim1, col_sim2 = st.columns([1, 1])

with col_sim1:

    # Conversion sécurisée des clés en entiers
    genre_map = {int(k): v for k, v in sex_map.items()}
    marital_map = {int(k): v for k, v in marriage_map.items()}
    scolaire_map = {int(k): v for k, v in education_map.items()}

    # Choix Âge : les mêmes tranches que les graphiques (AGE_BUCKET)
    selected_tranche = st.selectbox(
        "Tranche d'âge",
        options=["Tous âges"] + age_labels,
        format_func=lambda x: x if x == "Tous âges" else f"{x} ans"
    )

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
        "Niveau d'études",
        options=edu_options,
        format_func=lambda x: f"{scolaire_map.get(x, 'Tous niveaux')} ({x})" if x != -1 else "Tous niveaux"
    )

    # Mariage
    marital_options = [-1] + list(marital_map.keys())
    selected_marital = st.selectbox(
        "Statut marital",
        options=marital_options,
        format_func=lambda x: f"{marital_map.get(x, 'Tous statuts')} ({x})" if x != -1 else "Tous statuts"
    )

# Bouton de calcul
if st.button("🔍 Calculer le taux de défaut", type="primary", width='stretch'):

    # Filtre du dataset selon les critères choisis
    masque = pd.Series(True, index=df.index)
    if selected_tranche != "Tous âges":
        masque &= df["AGE_BUCKET"] == selected_tranche
    if selected_genre != -1:
        masque &= df["SEX"] == selected_genre
    if selected_edu != -1:
        masque &= df["EDUCATION"] == selected_edu
    if selected_marital != -1:
        masque &= df["MARRIAGE"] == selected_marital

    total_clients = int(masque.sum())
    if total_clients == 0:
        st.warning("Aucun client ne correspond exactement à ces critères combinés. Essayez d'élargir les tranches.")
    else:
        defaut_count = int(df.loc[masque, "dpnm"].sum())
        risk_pct = round(defaut_count / total_clients * 100, 2)

        # Affichage des résultats
        col_res1, col_res2 = st.columns(2)

        with col_res1:
            st.metric(
                label="Nombre de clients ciblés",
                value=nombre_fr(total_clients)
            )

        with col_res2:
            st.metric(
                label="Taux de défaut observé",
                value=f"{nombre_fr(risk_pct, 2)} %",
                delta_color="inverse"  # Rouge si haut, vert si bas
            )

        st.info(f"Sur ces {nombre_fr(total_clients)} clients, **{nombre_fr(defaut_count)}** ont fait défaut de paiement en octobre.")

        # Barre visuelle pour comparer à la moyenne des clients étudiés
        global_avg = round(taux_moyen, 2)
        col_viz1, col_viz2 = st.columns([3, 1])
        with col_viz1:
            st.progress(risk_pct / 100, f"Risque du profil ({nombre_fr(risk_pct, 2)} %) contre moyenne ({nombre_fr(global_avg, 2)} %)")
        with col_viz2:
            delta_val = round(risk_pct - global_avg, 1) + 0.0
            st.metric(label="Écart à la moyenne", value=f"{delta_val:+.1f} points".replace(".", ","))
