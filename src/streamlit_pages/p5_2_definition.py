from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 5.2 : LA DÉFINITION
# Règle de 05_02_EDA_incidents (section 4, fonction statut_incident), appliquée au niveau 3 du nettoyage :
# statut à M lu dans STATUT_INCIDENT (commun.py), indicateurs lus dans le CSV (docs/colonnes_creees.md, section 2).
# Deux populations sorties du machine learning : la population en incident (règle étudiée) et le retard
# imminent (retard posé par la banque en septembre). Descriptions sur tout le périmètre, sans le défaut ;
# le taux de défaut n'est lu que sur l'entraînement.
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"

df, s12, train, test = donnees_partie_5()
statut = s12['STATUT']

entete_partie_5(df, s12, train, test)

st.markdown("---")
st.header("5.2 La définition : la population en incident, et le retard imminent à part", anchor="definition")
st.markdown(f"""
Deux populations sortent du machine learning, et sont prédites en défaut sans modèle. Elles n'ont pas la même origine :
- la **population en incident** est définie par une **règle métier**, fixée par la logique avant de regarder le défaut, et étudiée dans [05_02_EDA_incidents.ipynb]({GH}/src/05_02_EDA_incidents.ipynb) ;
- le **retard imminent** n'est pas une règle construite par le projet : c'est un **retard que la banque a déjà posé** en septembre, sur la facture qu'elle a jugée impayée en octobre.

Aucun modèle n'est nécessaire pour les repérer : les codifications suffisent. Les définitions s'appliquent aux codifications nettoyées (page « 3.5 Décisions »).
""")

# ------------------------------------------------------------------------------
st.subheader("1. Un retard isolé n'est pas un incident de paiement", anchor="retard-isole")
st.markdown(f"""
Un **retard**, c'est un mois codifié {codif('2')} ou plus. Un client passe à {codif('2')} dès qu'une facture reste impayée le mois suivant (page « 3.3 Les codifications »). Un seul retard peut venir d'un oubli, d'un paiement arrivé trop tard ou d'un mois difficile : s'il paie le mois suivant, le client revient à une codification saine. C'est un **retard régularisé**.

Un **incident de paiement**, c'est un retard qui **dure** ou qui est **grave** :
- **deux codifications de retard d'affilée** : la facture n'a pas été régularisée le mois suivant non plus ;
- **une seule codification de {codif('3')} ou plus** : un retard ne monte que d'un cran par mois (page « 3.3 Les codifications ») ; une codification de {codif('3')} suppose donc déjà deux mois de retard.
""")

# ------------------------------------------------------------------------------
st.subheader("2. La règle, en clair", anchor="regle")
tableau_html(["Ce que montrent les codifications", "Situation du client", "Ce que gardent les colonnes"], [
    ["<b>Deux codifications de retard d'affilée</b>, ou une codification de 3 ou plus", "Passage en incident de paiement",
     "<code>FLAG_INCIDENT</code> = 1"],
    ["Après ce passage, la codification redescend sous 2", "<b>Sorti de l'incident</b>, le mois du retour",
     "<code>MOIS_SORTIE_INCIDENT</code> = 1 (septembre) à 5 (mai)"],
    ["<b>Une seule codification de retard</b>, suivie d'un retour sous 2", "<b>Retard régularisé</b> : ce n'est pas un incident",
     "<code>FLAG_RETARD</code> = 1, <code>MOIS_SORTIE_RETARD</code> = 1 à 5"],
    ["<b>En avril</b>, premier mois observé (mars n'est pas connu) : une codification de 3 ou plus",
     "Passage en incident", "<code>FLAG_INCIDENT</code> = 1"],
    ["<b>En avril</b>, une seule codification 2", "Retard régularisé si le paiement d'avril couvre la facture de mai, sinon passage en incident : ce 2 peut terminer une série commencée en mars",
     "<code>FLAG_RETARD</code> = 1, ou <code>FLAG_INCIDENT</code> = 1"],
    ["<b>En septembre</b>, deux codifications de retard d'affilée (août et septembre), ou une codification de 3 ou plus",
     "<b>En incident</b> à la fin de la période", "<code>FLAG_INCIDENT</code> = 1 et <code>MOIS_SORTIE_INCIDENT</code> = -1"],
    ["<b>En septembre</b>, une codification 2 après un mois d'août sain", "<b>Retard imminent</b>, population à part",
     "<code>FLAG_RETARD_IMMINENT</code> = 1"],
    ["Aucune codification de retard sur les six mois", "<b>Jamais en retard</b>",
     "<code>FLAG_INCIDENT</code>, <code>FLAG_RETARD</code> et <code>FLAG_RETARD_IMMINENT</code> = 0"],
], largeurs=[38, 34, 28])
st.markdown(f"""
- **Un client n'a qu'une situation à la fin de la période** : la plus récente l'emporte. Un client sorti de l'incident au printemps puis en retard imminent en septembre est classé en retard imminent, et garde la trace de son incident passé (`FLAG_INCIDENT` = 1).
- **La population en incident et le retard imminent ne se recoupent jamais** : un client sain en août ne peut pas être à {codif('3')} en septembre, puisqu'un retard ne monte que d'un cran par mois.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Deux populations sorties du machine learning, pour deux raisons différentes", anchor="deux-populations")
st.markdown(f"""
- **La population en incident** repose sur une règle construite par le projet : un retard qui dure, ou qui est grave, signale un client qui ne parvient plus à rembourser. La règle a été fixée par la logique, puis vérifiée sur l'entraînement et validée une seule fois sur le test.
- **Le retard imminent** ne repose sur aucune règle du projet. La codification de septembre juge la facture de fin septembre sur le paiement d'octobre (page « 1. Les données ») : un {codif('2')} posé en septembre veut dire que la banque a **déjà constaté** que cette facture n'était pas payée en octobre, le mois du défaut. Le projet ne fait que lire ce que la banque a déjà décidé.
""")
# Taux de défaut lus sur l'entraînement seulement : ils vérifient les deux définitions, ils n'en ont fixé aucune
verif = train.groupby('STATUT', observed=False)['dpnm'].agg(clients='size', taux='mean')
verif['taux'] = verif['taux'] * 100
taux_train = train['dpnm'].mean() * 100
ctx_v, imm_v = verif.loc["En incident"], verif.loc["Retard imminent"]
st.markdown(f"""
Le défaut, regardé sur le seul jeu d'entraînement, le vérifie : **{nombre_fr(ctx_v['taux'], 1)} %** des {nombre_fr(ctx_v['clients'])} clients en incident font défaut, et **{nombre_fr(imm_v['taux'], 1)} %** des {nombre_fr(imm_v['clients'])} clients en retard imminent, contre {nombre_fr(taux_train, 1)} % pour l'ensemble de l'entraînement.

Aucun modèle n'est donc nécessaire pour **repérer** ces deux populations. Un modèle pourrait seulement, dans un second temps, chercher à en retirer des clients qui paieront : c'est une piste qui reste ouverte.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Les populations ainsi définies", anchor="population")
rep = statut.value_counts().reindex(NOMS_STATUTS, fill_value=0)
part = rep / len(s12) * 100
# Disque des cinq statuts (1/3), à côté de la population en incident mois par mois (2/3)
fig_rep = go.Figure(go.Pie(
    labels=NOMS_STATUTS, values=rep.values, sort=False, direction='clockwise', hole=0,
    marker=dict(colors=[STATUTS_CTX[n] for n in NOMS_STATUTS]),
    texttemplate="%{percent:.1%}", textposition='inside', insidetextorientation='horizontal',
    hovertemplate="%{label} : %{value} clients (%{percent:.1%})<extra></extra>"))
fig_rep.update_layout(height=440, separators=", ", margin=dict(t=30, b=10, l=10, r=10),
                      legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"))

# Population en incident mois par mois : en incident au mois n = PAY_n et PAY_(n+1) >= 2, ou PAY_n >= 3
MOIS_STOCK = [(5, "Mai"), (4, "Juin"), (3, "Juillet"), (2, "Août"), (1, "Septembre")]
en_incident = [int((((s12[f'PAY_{n}'] >= 2) & (s12[f'PAY_{n + 1}'] >= 2)) | (s12[f'PAY_{n}'] >= 3)).sum()) for n, _ in MOIS_STOCK]
nb_imminent = int((statut == "Retard imminent").sum())
# Clients en incident à M dont la codification de septembre posée par la banque était un 1 (tranché en retard maintenu au niveau 2)
nb_un_tranches = int(((s12['PAY_1_original'] == 1) & (statut == "En incident")).sum())
fig_stock = go.Figure()
fig_stock.add_trace(go.Bar(x=[m for _, m in MOIS_STOCK], y=en_incident, name="En incident", marker_color=STATUTS_CTX["En incident"],
                           text=[nombre_fr(v) for v in en_incident], textposition='outside',
                           hovertemplate="<b>%{x}</b><br>En incident : %{y}<extra></extra>"))
fig_stock.add_trace(go.Bar(x=["Septembre"], y=[nb_imminent], name="Retard imminent (septembre)", marker_color=STATUTS_CTX["Retard imminent"],
                           text=[nombre_fr(nb_imminent)], textposition='outside',
                           hovertemplate="<b>%{x}</b><br>Retard imminent : %{y}<extra></extra>"))
fig_stock.update_layout(barmode='group', xaxis_title="Mois", yaxis_title="Clients", yaxis_range=[0, max(en_incident) * 1.2],
                        height=440, separators=", ", legend=dict(orientation="h", y=1.12), margin=dict(t=60))

col_disque, col_mois = st.columns([1, 2])
with col_disque:
    st.markdown("##### La situation de chaque client à la fin de la période")
    st.plotly_chart(fig_rep, width='stretch')
with col_mois:
    st.markdown("##### La population en incident, mois par mois")
    st.plotly_chart(fig_stock, width='stretch')
st.caption(f"Tout le périmètre ({nombre_fr(len(s12))} clients, dette positive en septembre), sans le défaut. À gauche, chaque client est classé selon sa situation à la fin de la période. À droite, chaque mois, les clients en incident ce mois-là : en retard pour au moins le deuxième mois d'affilée, ou codifiés 3 ou plus ; avril n'est pas mesurable, faute de connaître mars ; en septembre, le retard imminent est montré à part.")
st.markdown(f"""
- **{nombre_fr(rep['En incident'])} clients sont en incident** à la fin de la période, soit **{nombre_fr(part['En incident'], 1)} %** du périmètre, et **{nombre_fr(rep['Retard imminent'])} clients en retard imminent** ({nombre_fr(part['Retard imminent'], 1)} %). Ce sont eux qui sortent du machine learning.
- **La population en incident grossit de mai à septembre**, de {nombre_fr(en_incident[0])} à {nombre_fr(en_incident[-1])} clients, en pleine crise des cartes de crédit. Le saut de septembre vient en partie des codifications {codif('1')} posées par la banque après un retard : faute du paiement d'octobre, elles ont été tranchées avec prudence, en retard maintenu sauf si les trois modèles annonçaient une sortie (page « 3.5 Décisions »). {nombre_fr(nb_un_tranches)} clients en incident à la fin de la période sont dans ce cas. Placer un client sous surveillance coûte moins cher à une banque que de laisser un impayé s'installer.
- **Être passé par un incident n'est pas un état définitif** : {nombre_fr(rep["Sorti de l'incident"])} clients en sont sortis pendant la période ({nombre_fr(part["Sorti de l'incident"], 1)} %), et {nombre_fr(rep['Retard régularisé'])} ont régularisé un retard isolé ({nombre_fr(part['Retard régularisé'], 1)} %). Ils restent dans le machine learning.
""")

# ------------------------------------------------------------------------------
st.subheader("5. Ce que la définition transmet au machine learning", anchor="indicateurs")
st.markdown(f"""
Pour les clients qui restent dans le modèle, l'historique de leurs retards reste une information précieuse : il est transmis sous forme de colonnes, calculées au niveau 3 du nettoyage et définies une seule fois dans [docs/colonnes_creees.md]({GH}/docs/colonnes_creees.md). Chaque colonne part d'une **valeur par défaut**, celle d'un client à qui il n'est rien arrivé ; aucune n'est jamais vide.
""")
tableau_html(["Colonne", "Valeur par défaut", "Ce qu'elle dit"], [
    ["<code>FLAG_INCIDENT</code>", "0", "1 si le client est passé par un incident de paiement pendant la période"],
    ["<code>MOIS_SORTIE_INCIDENT</code>", "-1 (pas de sortie)", "Mois de sa dernière sortie de l'incident : 1 (septembre) à 5 (mai)"],
    ["<code>NB_MOIS_INCIDENT</code>", "0", "Nombre de mois passés en incident, tous les passages comptés"],
    ["<code>FLAG_RETARD</code>", "0", "1 si le client a régularisé un retard isolé"],
    ["<code>MOIS_SORTIE_RETARD</code>", "-1 (pas de régularisation)", "Mois du retour sous 2 après un retard isolé : 1 (septembre) à 5 (mai)"],
    ["<code>NB_MOIS_RETARD</code>", "0", "Nombre de mois de retard isolé"],
    ["<code>CUMUL_INCIDENT</code>", "0", "Nombre total de mois en retard : la somme des deux comptages précédents"],
], largeurs=[26, 22, 52])
st.markdown("""
Deux colonnes servent seulement à **trier** les clients, et n'entrent pas dans le modèle : `STATUT_INCIDENT`, la situation de chaque client en clair, et `FLAG_RETARD_IMMINENT`. Les clients en incident à la fin de la période et en retard imminent sont retirés du jeu du machine learning ; pour tous les autres, les colonnes ci-dessus résument l'historique des retards en informations lisibles, là où les codifications brutes mêlent retards réels et retards figés.
""")

st.info(f"""
**Ce qu'il faut retenir** : un client est en incident de paiement quand son retard dure, deux codifications de retard d'affilée, ou qu'il est grave, une codification de {codif('3')} ou plus. Le retard imminent, un seul retard posé par la banque en septembre, est une population à part : la banque a déjà jugé la facture de septembre impayée. Ensemble, ces deux populations rassemblent {nombre_fr(part['En incident'] + part['Retard imminent'], 1)} % du périmètre ; elles sont prédites en défaut sans modèle, et tous les autres clients passent au machine learning avec l'historique de leurs retards.
""")
