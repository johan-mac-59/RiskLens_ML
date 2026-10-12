from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 5.4 : LE RISQUE SUIT LE STATUT
# Validation de la définition avec le défaut, sur le jeu d'entraînement uniquement
# (05_02_EDA_incidents, section 4).
# Le défaut sert à vérifier que la règle a un sens, jamais à la régler. Colonnes lues dans le CSV.
# ==============================================================================
df, s12, train, test = donnees_partie_5()
taux_train = train['dpnm'].mean() * 100
MOIS_NOM = {1: "Septembre", 2: "Août", 3: "Juillet", 4: "Juin", 5: "Mai"}


def stats(d, groupes):
    """Clients et taux de défaut (%) par groupe, dans l'ordre donné."""
    t = d.groupby(groupes, observed=False)['dpnm'].agg(clients='size', taux='mean')
    t['taux'] = t['taux'] * 100
    return t


def barres_taux(t, couleurs, titre_x, hauteur=420):
    """Taux de défaut par groupe : barres, étiquette « taux (clients) », ligne orange du taux moyen de l'entraînement."""
    x = [LIBELLES_STATUTS.get(i, str(i)) for i in t.index]
    fig = go.Figure(go.Bar(x=x, y=t['taux'], marker_color=couleurs, customdata=t['clients'],
                           hovertemplate="%{x}<br>%{customdata} clients<extra></extra>"))
    fig.add_hline(y=taux_train, line_dash="dash", line_width=2, line_color=COULEURS["orange"])
    for xi, (_, row) in zip(x, t.iterrows()):
        etiquette_grise(fig, xi, row['taux'], f"{nombre_fr(row['taux'], 1)} % ({nombre_fr(row['clients'])})")
    fig.update_layout(xaxis_title=titre_x, yaxis_title="Taux de défaut de paiement (%)", yaxis_range=[0, t['taux'].max() * 1.22],
                      height=hauteur, separators=", ", margin=dict(t=20))
    return fig


entete_partie_5(df, s12, train, test)

st.markdown("---")
st.header("5.4 Le défaut confirme la définition : très fréquent en incident et en retard imminent, et d'autant plus que le retard a duré", anchor="risque")
st.markdown(f"""
La définition est fixée (page 5.2) et les comportements qu'elle sépare sont distincts (page 5.3). Vient maintenant le défaut, mais **uniquement sur le jeu d'entraînement** ({nombre_fr(len(train))} clients, {nombre_fr(taux_train, 1)} % de défaut en moyenne) : il sert à vérifier que la règle a un sens métier, pas à la régler. Aucun seuil n'a été modifié au vu de ces résultats.

Sur tous les graphiques, l'étiquette donne le taux de défaut et, entre parenthèses, le nombre de clients ; la ligne orange en pointillés marque le taux moyen de l'entraînement.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Un risque très différent d'un statut à l'autre", anchor="statuts")
par_statut = stats(train, train['STATUT']).reindex(NOMS_STATUTS)
st.plotly_chart(barres_taux(par_statut, list(STATUTS_CTX.values()), "Statut à la fin de la période", 440), width='stretch')
ctx, imm, sorti, isole, aucun = (par_statut.loc[nom] for nom in NOMS_STATUTS)
st.markdown(f"""
- **En incident, {nombre_fr(ctx['taux'], 1)} % des clients font défaut**, soit {nombre_fr(ctx['taux'] / aucun['taux'], 1)} fois plus que les clients jamais en retard ({nombre_fr(aucun['taux'], 1)} %). Retirer ces clients du machine learning pour les prédire en défaut se justifie.
- **En retard imminent, {nombre_fr(imm['taux'], 1)} % des clients font défaut**, encore plus qu'en incident. Ce n'est pas une prédiction : ce retard est le **défaut d'octobre déjà codifié par la banque**, sur la facture de septembre restée impayée. Il recoupe donc la cible sans la recopier : {nombre_fr(100 - imm['taux'], 0)} % de ces clients ne sont pas notés en défaut, et la définition exacte de la cible n'est pas documentée. Les prédire en défaut sans modèle va de soi.
- **Avoir été en incident ne suffit pas à faire défaut** : les clients sortis de l'incident ({nombre_fr(sorti['taux'], 1)} %) restent bien au-dessus de la moyenne, mais très loin des clients encore en incident. Ce qui compte, c'est d'être encore en retard en septembre.
- **Un retard régularisé pèse moins qu'un passage en incident** : {nombre_fr(isole['taux'], 1)} % de défaut, contre {nombre_fr(sorti['taux'], 1)} % pour les clients sortis de l'incident. C'est la confirmation, par le défaut, du choix fait en page 5.2 : une seule codification de retard n'est pas un incident de paiement.
""")

# ------------------------------------------------------------------------------
st.subheader("2. En septembre : même un seul retard est très risqué", anchor="duree-incident")
# Retard en cours en septembre : nombre de mois de retard (2 et plus) consécutifs jusqu'à septembre (PAY_1, PAY_2...)
en_cours = train[train['STATUT'].isin(["En incident", "Retard imminent"])]
duree = pd.Series(0, index=en_cours.index)
encore = pd.Series(True, index=en_cours.index)
for n in range(1, 7):
    encore &= en_cours[f'PAY_{n}'] >= 2
    duree += encore.astype(int)
groupes_duree = pd.Series(np.select([en_cours['STATUT'] == "Retard imminent", duree == 6],
                                    ["Retard imminent (septembre seul)", "En incident, les 6 mois"], default="En incident, 2 à 5 mois"),
                          index=en_cours.index)
ordre_duree = ["Retard imminent (septembre seul)", "En incident, 2 à 5 mois", "En incident, les 6 mois"]
par_duree = stats(en_cours, pd.Categorical(groupes_duree, categories=ordre_duree))
col_g, col_t = st.columns([3, 2])
with col_g:
    st.plotly_chart(barres_taux(par_duree, [STATUTS_CTX["Retard imminent"], STATUTS_CTX["En incident"], STATUTS_CTX["En incident"]],
                                "Durée du retard en cours en septembre"), width='stretch')
imm_d, milieu, six = (par_duree.iloc[i] for i in range(3))
with col_t:
    st.markdown(f"""
- **Les clients en retard sur les 6 mois sont les plus risqués** : {nombre_fr(six['taux'], 1)} % de défaut. C'est le noyau dur, celui des clients figés en retard qui a lancé l'étude.
- **Un seul retard en septembre suffit** : {nombre_fr(imm_d['taux'], 1)} % de défaut pour le retard imminent, puisque ce retard est le défaut d'octobre codifié par la banque.
- Entre les deux, les retards de 2 à 5 mois ont un risque voisin ({nombre_fr(milieu['taux'], 1)} %) : c'est la présence d'un retard en septembre qui fait le risque, plus que sa durée.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Sortis de l'incident : le risque grandit avec la durée du passage", anchor="sortis")
st.markdown("Pour les clients sortis de l'incident pendant la période, deux informations sont disponibles : **combien de mois ils y ont passé** (`NB_MOIS_INCIDENT`) et **quand ils en sont sortis** (`MOIS_SORTIE_INCIDENT`). Les deux sont liées : un long passage ne peut s'être terminé que récemment (cinq codifications de retard d'affilée finissent forcément en septembre). Les deux graphiques les montrent séparément, le tableau croisé les démêle.")
sortis = train[train['STATUT'] == "Sorti de l'incident"]
par_nb = stats(sortis, sortis['NB_MOIS_INCIDENT'].astype(int))
par_mois = stats(sortis, sortis['MOIS_SORTIE_INCIDENT'].astype(int)).sort_index(ascending=False)   # chronologique : mai -> septembre
par_mois.index = [MOIS_NOM[m] for m in par_mois.index]
col_nb, col_mois = st.columns(2)
with col_nb:
    st.markdown("#### Selon la durée du passage")
    st.plotly_chart(barres_taux(par_nb, STATUTS_CTX["Sorti de l'incident"], "Mois passés en incident (NB_MOIS_INCIDENT)"), width='stretch')
with col_mois:
    st.markdown("#### Selon le mois de sortie")
    st.plotly_chart(barres_taux(par_mois, STATUTS_CTX["Sorti de l'incident"], "Mois de la dernière sortie (MOIS_SORTIE_INCIDENT)"), width='stretch')

# Tableau croisé : taux de défaut (nombre de clients) selon la durée et le mois de sortie
croise_taux = pd.crosstab(sortis['NB_MOIS_INCIDENT'].astype(int), sortis['MOIS_SORTIE_INCIDENT'].astype(int), values=sortis['dpnm'], aggfunc='mean') * 100
croise_n = pd.crosstab(sortis['NB_MOIS_INCIDENT'].astype(int), sortis['MOIS_SORTIE_INCIDENT'].astype(int))
ordre_mois = sorted(croise_taux.columns, reverse=True)
croise_taux, croise_n = croise_taux[ordre_mois], croise_n.reindex(columns=ordre_mois)
texte = [[f"{nombre_fr(t, 1)} %<br>({nombre_fr(n)})" if pd.notna(t) else "" for t, n in zip(lt, ln)]
         for lt, ln in zip(croise_taux.values, croise_n.values)]
st.markdown("#### Les deux effets démêlés : taux de défaut selon la durée du passage et le mois de sortie")
fig_croise = go.Figure(go.Heatmap(
    z=croise_taux.values, x=[MOIS_NOM[m] for m in ordre_mois], y=[f"{d} mois" for d in croise_taux.index],
    text=texte, texttemplate="%{text}", textfont=dict(size=TAILLE_ETIQUETTE),
    colorscale=[[0, "#F6E8EE"], [1, COULEURS["bordeaux"]]], colorbar=dict(title="Défaut (%)"),
    hovertemplate="Durée %{y}, sortie en %{x}<br>%{text}<extra></extra>", xgap=3, ygap=3))
fig_croise.update_layout(xaxis_title="Mois de la dernière sortie", yaxis_title="Durée du passage (NB_MOIS_INCIDENT)", height=430,
                         separators=", ", margin=dict(t=20))
st.plotly_chart(fig_croise, width='stretch')
st.caption("Comment lire : chaque case donne le taux de défaut des clients sortis de l'incident, et entre parenthèses leur nombre. Les cases vides sont impossibles (un passage de 5 mois ne peut se terminer qu'en septembre) ou inexistantes. Les couleurs foncées signalent les taux les plus élevés.")

col_sept = croise_taux[1].dropna() if 1 in croise_taux.columns else pd.Series(dtype=float)
nb_min, nb_max = par_nb.iloc[0], par_nb.iloc[-1]
st.markdown(f"""
- **Plus le passage en incident a duré, plus le risque est élevé** : de {nombre_fr(nb_min['taux'], 1)} % pour un seul mois à {nombre_fr(nb_max['taux'], 1)} % pour cinq mois. À mois de sortie égal, l'effet demeure : parmi les clients sortis en septembre, le défaut passe de {nombre_fr(col_sept.iloc[0], 1)} % ({col_sept.index[0]} mois de passage) à {nombre_fr(col_sept.iloc[-1], 1)} % ({col_sept.index[-1]} mois).
- **Une sortie récente reste fragile** : les clients sortis en septembre font défaut à {nombre_fr(par_mois.loc['Septembre', 'taux'], 1)} %, contre {nombre_fr(par_mois.loc['Mai', 'taux'], 1)} % pour ceux sortis en mai. Entre les deux, l'effet du mois de sortie est moins régulier que celui de la durée.
- **Le passage d'un seul mois ne concerne que les retards isolés d'avril**, comptés en incident par prudence, faute de connaître mars (page 5.2) : leur risque, le plus bas des clients sortis, se rapproche de celui des retards isolés. C'est vraisemblablement un mélange de vrais retards isolés et de fins de séries commencées avant avril. La règle n'est pas modifiée pour autant : on ne change pas une décision métier au vu du défaut.
- La durée (`NB_MOIS_INCIDENT`) apporte donc une information que le mois de sortie (`MOIS_SORTIE_INCIDENT`) n'a pas : les deux sont transmis au machine learning.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Retards isolés : le risque s'efface avec le temps", anchor="retards-isoles")
isoles = train[train['STATUT'] == "Retard régularisé"]
par_regul = stats(isoles, isoles['MOIS_SORTIE_RETARD'].astype(int)).sort_index(ascending=False)
par_regul.index = [MOIS_NOM[m] for m in par_regul.index]
col_g4, col_t4 = st.columns([3, 2])
with col_g4:
    st.plotly_chart(barres_taux(par_regul, STATUTS_CTX["Retard régularisé"], "Mois de la régularisation (MOIS_SORTIE_RETARD)"), width='stretch')
with col_t4:
    plus_ancien, plus_recent = par_regul.iloc[0], par_regul.iloc[-1]
    st.markdown(f"""
- **Plus la régularisation est ancienne, plus le risque baisse** : {nombre_fr(plus_recent['taux'], 1)} % de défaut pour un retard régularisé en septembre, {nombre_fr(plus_ancien['taux'], 1)} % pour un retard régularisé en {par_regul.index[0].lower()}, {'sous' if plus_ancien['taux'] < taux_train else 'au-dessus de'} la moyenne de l'entraînement.
- Un retard isolé, une fois réglé, s'efface donc progressivement : c'est le comportement d'un retard ponctuel, pas d'un incident de paiement.
""")

# ==============================================================================
# SIMULATEUR : TAUX DE DÉFAUT PAR PROFIL, EN INCIDENT ET EN RETARD IMMINENT À M (DATASET STREAMLIT COMPLET)
# (fonction simulateur_profil de commun.py, la même qu'en 4.1, avec le choix de la population)
# ==============================================================================
pop_incident = df[df["STATUT_INCIDENT"] == "En incident"]
pop_imminent = df[df["STATUT_INCIDENT"] == "Retard imminent"]
pop_deux = df[df["STATUT_INCIDENT"].isin(["En incident", "Retard imminent"])]
simulateur_profil(pop_incident, "simulateur-incident", "", "", populations={
    "En incident": (pop_incident, f"en direct sur les {nombre_fr(len(pop_incident))} clients en incident en septembre", "des clients en incident"),
    "Retard imminent": (pop_imminent, f"en direct sur les {nombre_fr(len(pop_imminent))} clients en retard imminent en septembre", "des clients en retard imminent"),
    "Les deux": (pop_deux, f"en direct sur les {nombre_fr(len(pop_deux))} clients en incident ou en retard imminent en septembre", "des deux populations"),
})

st.info(f"""
**Ce qu'il faut retenir** : le défaut, regardé sur le seul jeu d'entraînement, confirme la définition sans l'avoir guidée. La population en incident ({nombre_fr(ctx['taux'], 1)} %) et le retard imminent ({nombre_fr(imm['taux'], 1)} %) concentrent un risque très élevé. Les autres statuts s'échelonnent nettement en dessous, et dans chacun, le risque dépend de la durée du retard et de l'ancienneté de la sortie : une information graduée, transmise au machine learning par les colonnes de l'historique des retards.
""")
