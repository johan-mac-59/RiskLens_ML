from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 5.5 : LE RISQUE SUIT LE STATUT
# Validation de la définition avec le défaut, sur le jeu d'entraînement uniquement
# (05_02_EDA_contentieux, section 6 ; 05_04_EDA_codification1, section 5.1 pour NB_MOIS_CTX).
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
st.header("5.5 Le défaut confirme la définition : très fréquent au contentieux, et d'autant plus que le retard a duré", anchor="risque")
st.markdown(f"""
La définition est fixée (page 5.3) et les comportements qu'elle sépare sont distincts (page 5.4). Vient maintenant le défaut, mais **uniquement sur le jeu d'entraînement** ({nombre_fr(len(train))} clients, {nombre_fr(taux_train, 1)} % de défaut en moyenne) : il sert à vérifier que la règle a un sens métier, pas à la régler. Aucun seuil n'a été modifié au vu de ces résultats.

Sur tous les graphiques, l'étiquette donne le taux de défaut et, entre parenthèses, le nombre de clients ; la ligne orange en pointillés marque le taux moyen de l'entraînement.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Un risque très différent d'un statut à l'autre", anchor="statuts")
par_statut = stats(train, train['STATUT']).reindex(NOMS_STATUTS)
st.plotly_chart(barres_taux(par_statut, list(STATUTS_CTX.values()), "Statut à la fin de la période", 440), width='stretch')
ctx, paye, sorti, isole, aucun = (par_statut.loc[nom] for nom in NOMS_STATUTS)
st.markdown(f"""
- **Au contentieux, {nombre_fr(ctx['taux'], 1)} % des clients font défaut**, soit {nombre_fr(ctx['taux'] / aucun['taux'], 1)} fois plus que les clients sans incident ({nombre_fr(aucun['taux'], 1)} %). Retirer ces clients du machine learning pour les prédire en défaut se justifie.
- **Avoir été en retard ne suffit pas à faire un contentieux** : les clients sortis du contentieux ({nombre_fr(sorti['taux'], 1)} %) et ceux qui ont payé leur retard de septembre ({nombre_fr(paye['taux'], 1)} %) restent bien au-dessus de la moyenne, mais très loin du contentieux. Ce qui compte, c'est d'y être encore en septembre.
- **Un retard isolé pèse moins qu'un vrai passage au contentieux** : {nombre_fr(isole['taux'], 1)} % de défaut, contre {nombre_fr(sorti['taux'], 1)} % pour les clients sortis du contentieux. C'est la confirmation, par le défaut, du choix fait en page 5.3 : une seule codification de retard n'est pas un contentieux.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Au contentieux : même une entrée récente est très risquée", anchor="duree-contentieux")
ctx_train = train[train['STATUT'] == "Au contentieux"]
groupes_duree = pd.Series(np.select([ctx_train['NB_MOIS_CTX'] == 1, ctx_train['NB_MOIS_CTX'] == 6],
                                    ["Entrés en septembre (1 mois)", "Les 6 mois"], default="2 à 5 mois"), index=ctx_train.index)
groupes_duree = pd.Categorical(groupes_duree, categories=["Entrés en septembre (1 mois)", "2 à 5 mois", "Les 6 mois"])
par_duree = stats(ctx_train, groupes_duree)
col_g, col_t = st.columns([3, 2])
with col_g:
    st.plotly_chart(barres_taux(par_duree, STATUTS_CTX["Au contentieux"], "Durée du passage en cours au contentieux (NB_MOIS_CTX)"), width='stretch')
entre, milieu, six = (par_duree.iloc[i] for i in range(3))
with col_t:
    st.markdown(f"""
- **Les clients en retard sur les 6 mois sont les plus risqués** : {nombre_fr(six['taux'], 1)} % de défaut. C'est le noyau dur, celui des clients figés en retard qui a lancé l'étude.
- **Même une entrée en septembre est déjà très risquée** : {nombre_fr(entre['taux'], 1)} % de défaut, sur une seule codification {codif('2')} en septembre, soit au moins 60 jours sans paiement, dont on ne connaît pas la suite. Placer ces clients au contentieux par défaut est donc prudent, et cohérent avec le défaut observé.
- Entre les deux, les passages de 2 à 5 mois ont un risque voisin ({nombre_fr(milieu['taux'], 1)} %) : au contentieux, c'est la présence en septembre qui fait le risque, plus que la durée.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Sortis du contentieux : le risque grandit avec la durée du passage", anchor="sortis")
st.markdown("Pour les clients sortis du contentieux pendant la période, deux informations sont disponibles : **combien de temps ils y sont restés** (`NB_MOIS_CTX`) et **quand ils en sont sortis** (`MOIS_SORTIE_CTX`). Les deux sont liées : un long passage ne peut s'être terminé que récemment (cinq codifications de retard d'affilée finissent forcément en septembre). Les deux graphiques les montrent séparément, le tableau croisé les démêle.")
sortis = train[train['STATUT'] == "Sorti du contentieux"]
par_nb = stats(sortis, sortis['NB_MOIS_CTX'].astype(int))
par_mois = stats(sortis, sortis['MOIS_SORTIE_CTX'].astype(int)).sort_index(ascending=False)   # chronologique : mai -> septembre
par_mois.index = [MOIS_NOM[m] for m in par_mois.index]
col_nb, col_mois = st.columns(2)
with col_nb:
    st.markdown("#### Selon la durée du passage")
    st.plotly_chart(barres_taux(par_nb, STATUTS_CTX["Sorti du contentieux"], "Mois de retard consécutifs (NB_MOIS_CTX)"), width='stretch')
with col_mois:
    st.markdown("#### Selon le mois de sortie")
    st.plotly_chart(barres_taux(par_mois, STATUTS_CTX["Sorti du contentieux"], "Mois de la dernière sortie (MOIS_SORTIE_CTX)"), width='stretch')

# Tableau croisé : taux de défaut (nombre de clients) selon la durée et le mois de sortie
croise_taux = pd.crosstab(sortis['NB_MOIS_CTX'].astype(int), sortis['MOIS_SORTIE_CTX'].astype(int), values=sortis['dpnm'], aggfunc='mean') * 100
croise_n = pd.crosstab(sortis['NB_MOIS_CTX'].astype(int), sortis['MOIS_SORTIE_CTX'].astype(int))
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
fig_croise.update_layout(xaxis_title="Mois de la dernière sortie", yaxis_title="Durée du passage (NB_MOIS_CTX)", height=430,
                         separators=", ", margin=dict(t=20))
st.plotly_chart(fig_croise, width='stretch')
st.caption("Comment lire : chaque case donne le taux de défaut des clients sortis du contentieux, et entre parenthèses leur nombre. Les cases vides sont impossibles (un passage de 5 mois ne peut se terminer qu'en septembre) ou inexistantes. Les couleurs foncées signalent les taux les plus élevés.")

col_sept = croise_taux[1].dropna() if 1 in croise_taux.columns else pd.Series(dtype=float)
nb_min, nb_max = par_nb.iloc[0], par_nb.iloc[-1]
st.markdown(f"""
- **Plus le passage au contentieux a duré, plus le risque est élevé** : de {nombre_fr(nb_min['taux'], 1)} % pour un seul mois à {nombre_fr(nb_max['taux'], 1)} % pour cinq mois. À mois de sortie égal, l'effet demeure : parmi les clients sortis en septembre, le défaut passe de {nombre_fr(col_sept.iloc[0], 1)} % ({col_sept.index[0]} mois de passage) à {nombre_fr(col_sept.iloc[-1], 1)} % ({col_sept.index[-1]} mois).
- **Une sortie récente reste fragile** : les clients sortis en septembre font défaut à {nombre_fr(par_mois.loc['Septembre', 'taux'], 1)} %, contre {nombre_fr(par_mois.loc['Mai', 'taux'], 1)} % pour ceux sortis en mai. Entre les deux, l'effet du mois de sortie est moins régulier que celui de la durée.
- **Le passage d'un seul mois ne concerne que les retards isolés d'avril**, comptés au contentieux par prudence (page 5.3) : leur risque, le plus bas des clients sortis, se rapproche de celui des retards isolés. C'est vraisemblablement un mélange de vrais retards isolés et de fins de séries commencées avant avril. La règle n'est pas modifiée pour autant : on ne change pas une décision métier au vu du défaut.
- La durée (`NB_MOIS_CTX`) apporte donc une information que le mois de sortie (`MOIS_SORTIE_CTX`) n'a pas : les deux sont transmis au machine learning.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Retards isolés : le risque s'efface avec le temps", anchor="retards-isoles")
isoles = train[train['STATUT'] == "Retard isolé régularisé"]
par_regul = stats(isoles, isoles['MOIS_SORTIE_RETARD'].astype(int)).sort_index(ascending=False)
par_regul.index = [MOIS_NOM[m] for m in par_regul.index]
col_g4, col_t4 = st.columns([3, 2])
with col_g4:
    st.plotly_chart(barres_taux(par_regul, STATUTS_CTX["Retard isolé régularisé"], "Mois de la régularisation (MOIS_SORTIE_RETARD)"), width='stretch')
with col_t4:
    plus_ancien, plus_recent = par_regul.iloc[0], par_regul.iloc[-1]
    st.markdown(f"""
- **Plus la régularisation est ancienne, plus le risque baisse** : {nombre_fr(plus_recent['taux'], 1)} % de défaut pour un retard régularisé en septembre, {nombre_fr(plus_ancien['taux'], 1)} % pour un retard régularisé en {par_regul.index[0].lower()}, {'sous' if plus_ancien['taux'] < taux_train else 'au-dessus de'} la moyenne de l'entraînement.
- Un retard isolé, une fois réglé, s'efface donc progressivement : c'est le comportement d'un incident ponctuel, pas d'un contentieux.
""")

# ------------------------------------------------------------------------------
st.subheader("5. Un retard posé sur une facture payée n'est pas anodin", anchor="retard-facture-payee")
# Entrées en retard (PAY_n >= 2 alors que PAY_(n+1) < 2) posées sur une facture réelle (BILL_AMT(n+1) > 0) payée en entier
# le mois même (PAY_AMTn >= BILL_AMT(n+1)) et le mois précédent (facture nulle ou payée en entier) : la codification suit
# le paiement avec un mois de décalage, d'où les deux mois. Historique : mai à août (n = 5 à 2) ; septembre : n = 1.
# Ces codifications ne sont pas corrigées (05_02_EDA_contentieux, cellule 18) : on mesure seulement leur risque.


def retard_sur_facture_payee(d, mois):
    trouve = pd.Series(False, index=d.index)
    for n in mois:
        entree = (d[f'PAY_{n}'] >= 2) & (d[f'PAY_{n + 1}'] < 2) & (d[f'BILL_AMT{n + 1}'] > 0)
        paye = d[f'PAY_AMT{n}'] >= d[f'BILL_AMT{n + 1}']
        precedent = ((d[f'BILL_AMT{n + 2}'] <= 0) | (d[f'PAY_AMT{n + 1}'] >= d[f'BILL_AMT{n + 2}'])) if n + 2 <= 6 else True
        trouve |= entree & paye & precedent
    return trouve


historique_paye = retard_sur_facture_payee(train, range(2, 6))
septembre_paye = retard_sur_facture_payee(train, [1])
comptant_sain = (train['STATUT'] == "Aucun incident") & (train['TYPE_USAGE'] == "Paiement comptant")
GROUPES_PAYE = [
    ("Retard posé sur une facture payée, de mai à août", historique_paye),
    ("Retard posé sur une facture payée, en septembre", septembre_paye),
    ("Comparaison : payeurs au comptant sans incident", comptant_sain),
    ("Comparaison : au contentieux", train['STATUT'] == "Au contentieux"),
]
st.markdown(f"""
Il existe des retards posés sur une facture **réelle, payée en entier**, le mois même et le mois précédent : le client a tout réglé, et la banque le codifie pourtant en retard. Ces codifications **n'ont pas été corrigées**, et c'est un choix ([05_02_EDA_contentieux.ipynb](https://github.com/johan-mac-59/RiskLens_ML/blob/main/src/05_02_EDA_contentieux.ipynb), cellule 18).

Les règles de codification de la banque n'ont pas pu être entièrement percées, et la première itération du machine learning laissait déjà pressentir qu'elles portaient une information plus profonde que les montants. L'étude a donc cherché à **modifier le moins possible les codifications** : seuls les retards indéfendables, posés sur une facture nulle, sont corrigés (page 5.2), et même eux laissent une trace dans des colonnes créées pour l'occasion. Les autres anomalies, comme celle-ci, restent telles quelles ; elles sont simplement classées par les règles du contentieux. Que valent-elles face au défaut ?
""")
tableau_html(["Groupe (entraînement)", "Clients", "Taux de défaut"],
             [[nom, nombre_fr(int(m.sum())), f"<b>{nombre_fr(train.loc[m, 'dpnm'].mean() * 100, 1)} %</b>"] for nom, m in GROUPES_PAYE],
             largeurs=[60, 20, 20])
st.caption("Comment lire : une entrée en retard (codification 2 ou plus, alors que le client n'était pas en retard le mois d'avant) posée sur une facture réelle payée en entier ce mois-là, et dont la facture du mois précédent était nulle ou payée en entier aussi. La codification suivant le paiement avec un mois de décalage, on vérifie les deux mois. Jeu d'entraînement uniquement.")
t_hist, t_sept, t_comptant, t_ctx = (train.loc[m, 'dpnm'].mean() * 100 for _, m in GROUPES_PAYE)
part_comptant_avant = sum(((train[f'PAY_{n}'] >= 2) & (train[f'PAY_{n + 1}'] == -1)).astype(int) for n in range(2, 6))[historique_paye].gt(0).mean() * 100
st.markdown(f"""
- **Ces clients font défaut à {nombre_fr(t_hist, 1)} % (de mai à août) et {nombre_fr(t_sept, 1)} % (en septembre)**, soit plus de deux fois plus que des payeurs au comptant sans incident ({nombre_fr(t_comptant, 1)} %), alors que leurs montants sont irréprochables. Ce sont presque tous des payeurs au comptant : {nombre_fr(part_comptant_avant)} % étaient codifiés {codif('-1')} juste avant leur retard.
- **Leur risque reste loin de celui du contentieux** ({nombre_fr(t_ctx, 1)} %) : la plupart sont classés en retard isolé régularisé ou sortis du contentieux, des statuts dont le risque est du même ordre. La règle les range donc déjà au bon niveau, sans règle supplémentaire.
- **La codification porte un signal que les montants ne montrent pas** : un paiement rejeté après coup, un incident sur un autre produit, une procédure interne de la banque… Le dataset ne permet pas de savoir lequel. Corriger ces retards aurait effacé ce signal ; ils restent dans les données, et le machine learning dispose à la fois des codifications et des montants.
""")

# ==============================================================================
# SIMULATEUR : TAUX DE DÉFAUT PAR PROFIL, PARMI LES CLIENTS AU CONTENTIEUX À M (DATASET STREAMLIT COMPLET)
# (fonction simulateur_profil de commun.py, la même qu'en 4.1)
# ==============================================================================
ctx_dataset = df[(df["FLAG_CTX"] == 1) & (df["MOIS_SORTIE_CTX"] == -1)]
simulateur_profil(ctx_dataset, "simulateur-contentieux",
                  f"en direct sur les {nombre_fr(len(ctx_dataset))} clients au contentieux en septembre",
                  "des clients au contentieux")

st.info(f"""
**Ce qu'il faut retenir** : le défaut, regardé sur le seul jeu d'entraînement, confirme la définition sans l'avoir guidée. Le contentieux concentre un risque très élevé ({nombre_fr(ctx['taux'], 1)} %), y compris pour les clients qui y entrent en septembre. Les autres statuts s'échelonnent nettement en dessous, et dans chacun, le risque dépend de la durée du retard et de l'ancienneté de la sortie : une information graduée, transmise au machine learning par les indicateurs du contentieux. Enfin, même un retard posé sur une facture payée signale un risque deux fois plus élevé : la codification porte une information que les montants ne montrent pas. Reste à vérifier que la règle tient sur des clients qu'elle n'a jamais vus : c'est le test de la page suivante.
""")
