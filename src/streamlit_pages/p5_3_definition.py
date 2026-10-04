from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 5.3 : LA DÉFINITION DU CONTENTIEUX
# Définition 2, retenue (05_02_EDA_contentieux, section 6), appliquée aux codifications corrigées (niveau 5).
# Statuts lus dans les indicateurs du niveau 5 (statut_contentieux, commun.py) ; aucune colonne créée.
# Page sans le défaut : la règle est décrite, illustrée et dénombrée sur tout le périmètre ; sa validation
# avec le taux de défaut vient en 5.5 (entraînement) et 5.6 (test).
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
PAY_COLS = [f'PAY_{n}' for n, _ in MOIS_CHRONO]   # avril (PAY_6) -> septembre (PAY_1)

df, s12, train, test = donnees_partie_5()

# Résultats repris des notebooks pour la section 6 (codifications d'origine, absentes du CSV : décision D19)
# 05_04_EDA_codification1, cellule 42 (et audit) : codifications 1 de septembre dans les données d'origine
NB_CODIF_1_ORIGINE = 3688
# 05_04_EDA_codification1, cellule 31 : ancienne correction (tous les 1 après un retard remis à 2), simulée sur le train
ANCIEN_AJOUTES, ANCIEN_TAUX_AJOUTES, ANCIEN_TAUX_CTX_AVANT, ANCIEN_TAUX_CTX_APRES = 1349, 42.3, 70.3, 60.2
# 05_04_EDA_codification1, cellules 36, 39 et 42 : contrôle de cleaned5 (cleaned4 avant, cleaned5 après)
CTRL_FAUX_RETARDS, CTRL_REMIS_A_2, CTRL_SOLDES = 224, 118, 5
CTRL_REMIS_DEPUIS_1, CTRL_REMIS_DEPUIS_SAIN = 73, 45
CTRL_CODIFS_MODIFIEES, CTRL_CLIENTS_MODIFIES, CTRL_RETARDS_NEUTRALISES = 566, 346, 442
taux_train = train['dpnm'].mean() * 100

# 05_02_EDA_contentieux, cellule 14 (train, codifications d'origine) : clients avec un seul mois de retard, hors septembre
UN_SEUL_RETARD, SUR_VRAIE_FACTURE, SUR_FACTURE_NULLE, EN_AVRIL = 2146, 1738, 1, 407

entete_partie_5(df, s12, train, test)

st.markdown("---")
st.header("5.3 La définition du contentieux : deux mois de retard d'affilée, et une sortie confirmée par les paiements", anchor="definition")
st.markdown("""
Les codifications sont désormais corrigées (page « 5.2 Chercher le contentieux révèle de faux retards »). Reste à dire, pour chaque client, s'il est au contentieux. Toute la définition repose sur une idée métier : **le contentieux, c'est un retard qui s'installe, pas un incident ponctuel**. Elle a été fixée par la logique, avant de regarder le défaut ; sa validation vient ensuite, en pages 5.5 et 5.6.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Un retard isolé n'est pas un contentieux", anchor="retard-isole")
st.markdown(f"""
Un client peut n'avoir qu'**un seul mois** de retard sur toute la période. Dans l'étude, {nombre_fr(UN_SEUL_RETARD)} clients de l'entraînement étaient dans ce cas : quand on peut le vérifier, ce retard porte presque toujours sur **une vraie facture** ({nombre_fr(SUR_VRAIE_FACTURE)} cas, contre {SUR_FACTURE_NULLE} seul sur une facture nulle ; les {EN_AVRIL} retards d'avril ne sont pas vérifiables, faute de connaître mars). Le client a payé en retard, puis a régularisé le mois suivant : c'est le **fonctionnement normal d'un crédit** ([05_02_EDA_contentieux.ipynb]({GH}/src/05_02_EDA_contentieux.ipynb), cellules 14 et 15).

À l'inverse, **deux mois de retard d'affilée** signifient que la dette n'a pas été régularisée le mois suivant. Une codification {codif('2')} correspond déjà, a priori, à au moins 60 jours sans paiement (page 5.2) : deux codifications {codif('2')} d'affilée signifient donc **au moins 90 jours de retard**. Le retard s'installe. C'est ce seuil, et non un retard ponctuel, que l'étude a **choisi comme frontière entre la gestion standard et le contentieux**. Le dataset ne dit pas où la banque place elle-même cette frontière : c'est une définition de travail, fondée sur la logique métier.
""")

# ------------------------------------------------------------------------------
st.subheader("2. La règle, en clair", anchor="regle")
st.markdown(f"""
La règle s'applique aux codifications **déjà corrigées** en page 5.2. Pour mémoire :
- les retards posés sur une facture nulle (comptes (ré)activés et faux 2) sont remplacés par la dernière codification sans retard ; ils ne comptent donc pas comme des retards, et deux colonnes en gardent la trace (`SURVEILLANCE_RECENTE`, `FAUX_CODAGE`) ;
- en septembre, un client en retard en août que la banque ne codifie plus en retard est remis à {codif('2')} s'il n'a rien payé sur deux factures dues, et remis sur sa codification d'avant le retard s'il a soldé sa facture ; sinon, sa codification reste celle de la banque ;
- aucun {codif('2')} posé sur une vraie dette n'est modifié.
""")
st.caption("Comment lire : une ligne par situation, avec le classement du client et les indicateurs du dataset qui la retranscrivent (définitions complètes dans docs/colonnes_creees.md). Un retard est une codification 2 ou plus.")
tableau_html(["Situation sur les 6 mois", "Classement", "Indicateurs"], [
    ["<b>Au moins deux mois de retard d'affilée</b>", "Passage au contentieux", "<code>FLAG_CTX</code> = 1"],
    ["Après ce passage, la codification redescend sous 2", "Sorti du contentieux, le mois du retour",
     "<code>MOIS_SORTIE_CTX</code> = 1 (septembre) à 5 (mai)"],
    ["<b>Un seul mois de retard</b>, suivi d'un retour sous 2", "Retard isolé régularisé : ce n'est pas un contentieux",
     "<code>FLAG_RETARD</code> = 1 et <code>MOIS_SORTIE_RETARD</code> = mois du retour (1 à 4)"],
    ["Un retard isolé en <b>avril</b>, premier mois observé", "Compté comme un passage au contentieux, par prudence : mars n'est pas observé, et ce retard peut terminer une série plus longue",
     "<code>FLAG_CTX</code> = 1"],
    ["<b>En retard en septembre</b>, dernier mois observé, que ce retard soit isolé ou non", "<b>Au contentieux</b> à la fin de la période. D'abord par prudence, car la suite n'est pas connue ; ensuite parce que la codification suit le paiement avec un mois de décalage : un retard codifié en septembre traduit déjà au moins 60 jours sans paiement, et il atteindrait les 90 jours en octobre si rien n'est payé. Ces clients sont retirés du machine learning et prédits en défaut",
     "<code>FLAG_CTX</code> = 1 et <code>MOIS_SORTIE_CTX</code> = -1"],
    ["... sauf si la facture a été payée à <b>90 % ou plus</b> en août ou en septembre", "Retard payé : régularisation présumée en octobre (la codification suit le paiement avec un mois de décalage)",
     "<code>MOIS_SORTIE_CTX</code> = 0 (fin d'une série) ou <code>MOIS_SORTIE_RETARD</code> = 0 (retard isolé)"],
    ["Aucune codification de retard sur les six mois", "<b>Aucun incident</b>", "<code>FLAG_CTX</code> = 0 et <code>FLAG_RETARD</code> = 0"],
], largeurs=[34, 38, 28])
st.markdown(f"""
Quatre précisions :
- **La population « au contentieux » regroupe les clients supposés être toujours au contentieux en octobre**, le mois du défaut (`FLAG_CTX` = 1 et `MOIS_SORTIE_CTX` = -1). Elle **n'inclut pas** les clients passés par le contentieux puis sortis pendant la période, ni ceux dont le retard est payé : ils gardent `FLAG_CTX` = 1, mais restent dans le machine learning, avec leur mois de sortie.
- **« Aucun incident » veut dire aucune codification de retard sur les six mois** (`CUMUL_INCIDENT` = 0, page 4.6). Un client sorti du contentieux n'a plus de retard en septembre, mais il a eu des incidents : il est classé « sorti du contentieux », et ses colonnes gardent la trace de son passage (`FLAG_CTX` = 1).
- **C'est une décision de traitement**, pas une observation : le dataset ne donne pas la situation d'octobre. Elle s'appuie sur la dernière situation connue, celle de septembre.
- **La durée du dernier passage au contentieux** est comptée en mois de retard consécutifs (`NB_MOIS_CTX`) : de 1 (entrée en septembre, ou retard isolé d'avril) à 6 (en retard sur toute la période).
""")

# ------------------------------------------------------------------------------
st.subheader("3. De vrais clients, une situation chacun", anchor="exemples")
statut = s12['STATUT']
duree = s12['NB_MOIS_CTX']
codes = s12[PAY_COLS]
ratio_sept = s12['PAY_AMT1'] / s12['BILL_AMT2'].where(s12['BILL_AMT2'] > 0) * 100
ratio_aout = s12['PAY_AMT2'] / s12['BILL_AMT3'].where(s12['BILL_AMT3'] > 0) * 100
# Un exemple par situation : le premier client du périmètre (par numéro) qui correspond, avec des codifications de 2 au plus
simple = (codes <= 2).all(axis=1)
SITUATIONS = [
    ("Au contentieux, depuis les 6 mois", (statut == "Au contentieux") & (duree == 6) & simple,
     "En retard sur toute la période, figé à 2 : le cas qui a lancé l'étude"),
    ("Au contentieux, entré pendant la période", (statut == "Au contentieux") & duree.between(3, 4) & simple & (s12['PAY_6'] <= 0),
     "Plusieurs mois de retard d'affilée, toujours en retard en septembre"),
    ("Au contentieux, entré en septembre", (statut == "Au contentieux") & (duree == 1) & (codes.iloc[:, :5] <= 0).all(axis=1),
     "Un seul retard, mais en septembre : la suite n'est pas connue"),
    ("Retard payé en septembre", (statut == "Retard payé en septembre") & (s12['PAY_2'] >= 2) & simple,
     "En retard en septembre, mais la facture est payée à 90 % ou plus"),
    # Sortie en août ou en juillet, confirmée par les mois suivants (aucun retard ensuite)
    ("Sorti du contentieux", (statut == "Sorti du contentieux") & duree.between(2, 3) & s12['MOIS_SORTIE_CTX'].between(2, 3) & simple
     & (codes != 1).all(axis=1) & (s12['PAY_6'] <= 0) & (s12[['PAY_1', 'PAY_2']] <= 0).all(axis=1),
     "Deux mois de retard d'affilée ou plus, puis retour à une codification sans retard, confirmé par les mois suivants"),
    ("Retard isolé régularisé", (statut == "Retard isolé régularisé") & s12['MOIS_SORTIE_RETARD'].between(2, 3) & simple,
     "Un seul mois de retard, régularisé le mois suivant"),
    ("Aucun incident", (statut == "Aucun incident") & (codes.nunique(axis=1) >= 2),
     "Aucune codification de retard sur les six mois"),
]
lignes_exemples, lignes_colonnes = [], []
COLONNES_CTX = [("FLAG_CTX", 0), ("MOIS_SORTIE_CTX", -1), ("NB_MOIS_CTX", 0), ("FLAG_RETARD", 0), ("MOIS_SORTIE_RETARD", -1)]


def part_payee(ratio):
    """Part de la facture payée, ou mention quand aucune facture n'était à payer."""
    return "pas de facture" if pd.isna(ratio) else f"{nombre_fr(ratio)} %"


for nom, masque, pourquoi in SITUATIONS:
    if not masque.any():
        continue
    i = s12.index[masque][0]
    client = f"<b>{nom}</b><br><small>client n° {int(s12.at[i, 'ID'])}</small>"
    if nom == "Retard payé en septembre":
        mois_paye = "août" if ratio_aout[i] >= 90 else "septembre"
        pourquoi = (f"Codifié en retard en septembre, mais la facture à payer en {mois_paye} est réglée à "
                    f"{nombre_fr(ratio_aout[i] if mois_paye == 'août' else ratio_sept[i])} % : le retard est considéré comme payé, "
                    "et la sortie du retard est présumée en octobre")
    lignes_exemples.append([client] + [cellule_codif(s12.at[i, c]) for c in PAY_COLS] + [pourquoi])
    # Les mêmes clients dans les colonnes créées : en gras, les valeurs qui diffèrent de la valeur par défaut
    lignes_colonnes.append([client, part_payee(ratio_aout[i]), part_payee(ratio_sept[i])]
                           + [(f"<b>{int(s12.at[i, c])}</b>" if s12.at[i, c] != defaut else str(int(s12.at[i, c])), "text-align: center;")
                              for c, defaut in COLONNES_CTX])
st.caption("Comment lire : une ligne par client réel du périmètre, ses codifications corrigées d'avril à septembre, puis la raison de son classement. Chaque exemple est le premier client, par numéro, qui correspond à la situation.")
tableau_html(["Situation"] + [nom for _, nom in MOIS_CHRONO] + ["Pourquoi"], lignes_exemples, largeurs=[22] + [8] * 6 + [30])
st.markdown("##### Les mêmes clients : paiements des derniers mois et colonnes créées")
tableau_html(["Situation", "Facture à payer en août : part payée", "Facture à payer en septembre : part payée"] + [f"<code>{c}</code>" for c, _ in COLONNES_CTX],
             lignes_colonnes, largeurs=[22, 12, 12, 10, 12, 10, 10, 12])
st.caption("Comment lire : la part payée rapporte le paiement du mois à la facture à payer ce mois-là. Les colonnes créées valent par défaut 0 (FLAG_CTX, NB_MOIS_CTX, FLAG_RETARD) ou -1 (colonnes de mois) ; en gras, les valeurs modifiées par un événement. Mois de sortie : 1 = septembre, 2 = août…, 0 = sortie présumée en octobre. Le client au contentieux garde MOIS_SORTIE_CTX = -1 : il n'est pas sorti.")

# ------------------------------------------------------------------------------
st.subheader("4. La population ainsi définie", anchor="population")
rep = statut.value_counts().reindex(NOMS_STATUTS).fillna(0).astype(int)
part = rep / len(s12) * 100

passe_ctx = (s12['FLAG_CTX'] == 1).mean() * 100

# 4.1 Répartition des statuts : disque à gauche, interprétation à droite
col_disque, col_texte = st.columns([1, 1], vertical_alignment="center")
with col_disque:
    st.markdown("#### Les clients du périmètre, selon leur statut")
    fig_rep = go.Figure(go.Pie(labels=NOMS_STATUTS, values=rep.values, marker=dict(colors=list(STATUTS_CTX.values())),
                               hole=0.45, sort=False, direction="clockwise", texttemplate="%{percent:.1%}",
                               textfont=dict(size=TAILLE_ETIQUETTE), insidetextorientation="horizontal",
                               hovertemplate="%{label}<br>%{value} clients (%{percent:.1%})<extra></extra>"))
    fig_rep.update_layout(height=430, separators=", ", legend=dict(orientation="h", y=-0.05), margin=dict(t=20, b=20, l=10, r=10))
    st.plotly_chart(fig_rep, width='stretch')
with col_texte:
    st.markdown(f"""
- **{nombre_fr(rep['Au contentieux'])} clients sont au contentieux** à la fin de la période, soit **{nombre_fr(part['Au contentieux'], 1)} %** du périmètre. Ce sont eux que la règle retire du machine learning.
- **{nombre_fr(passe_ctx, 1)} % des clients sont passés par le contentieux** à un moment des 6 mois (`FLAG_CTX` = 1) : ceux qui y sont encore, mais aussi ceux qui en sont sortis ({nombre_fr(part['Sorti du contentieux'], 1)} % du périmètre) et quelques retards payés qui terminent une série. Le contentieux n'est pas un état définitif.
- **{nombre_fr(part['Retard isolé régularisé'], 1)} % ont eu un retard isolé**, régularisé ensuite, et {nombre_fr(part['Retard payé en septembre'], 1)} % un retard de septembre déjà payé.
- **{nombre_fr(part['Aucun incident'], 1)} % des clients n'ont aucun incident** : aucune codification de retard sur les six mois, une fois les faux retards neutralisés.
""")
st.caption(f"Tout le périmètre ({nombre_fr(len(s12))} clients, dette positive en septembre), sans le défaut. Un client qui a connu plusieurs situations est classé selon la plus récente et la plus grave : par exemple, un retard isolé suivi d'un passage au contentieux compte comme un passage au contentieux.")

# 4.2 Entrées mois par mois : premier mois de retard, et passage au contentieux (deuxième mois de retard d'affilée)
# Entrée en retard au mois n : PAY_n >= 2 alors que PAY_(n+1) < 2 (mai à septembre ; avril n'a pas de mois précédent)
# Entrée au contentieux au mois n : deuxième mois de retard d'affilée atteint, PAY_n >= 2, PAY_(n+1) >= 2 et PAY_(n+2) < 2
# (juin à septembre ; en mai, le début de la série n'est pas connu)
MOIS_ENTREE = [(5, "Mai"), (4, "Juin"), (3, "Juillet"), (2, "Août"), (1, "Septembre")]
entrees = pd.DataFrame([{
    'mois': nom,
    'retard': int(((s12[f'PAY_{n}'] >= 2) & (s12[f'PAY_{n + 1}'] < 2)).sum()),
    'contentieux': int(((s12[f'PAY_{n}'] >= 2) & (s12[f'PAY_{n + 1}'] >= 2) & (s12[f'PAY_{n + 2}'] < 2)).sum()) if n + 2 <= 6 else np.nan,
} for n, nom in MOIS_ENTREE])
# Part des nouveaux retards d'un mois qui atteignent le deuxième mois d'affilée le mois suivant
entrees['passage'] = entrees['contentieux'] / entrees['retard'].shift(1) * 100

st.markdown("#### Mois par mois : entrées en retard et entrées au contentieux")
fig_entrees = go.Figure()
fig_entrees.add_trace(go.Bar(x=entrees['mois'], y=entrees['retard'], name="Entrée en retard (premier mois de retard)",
                             marker_color=COULEURS["rouge_pale"], hovertemplate="<b>%{x}</b><br>Entrées en retard : %{y}<extra></extra>"))
fig_entrees.add_trace(go.Bar(x=entrees['mois'], y=entrees['contentieux'], name="Entrée au contentieux (deuxième mois de retard d'affilée)",
                             marker_color=STATUTS_CTX["Au contentieux"], hovertemplate="<b>%{x}</b><br>Entrées au contentieux : %{y}<extra></extra>"))
# Étiquettes écrites à la main : aucune pour l'entrée au contentieux de mai, non mesurable
for trace, colonne in zip(fig_entrees.data, ('retard', 'contentieux')):
    trace.text = ["" if pd.isna(v) else nombre_fr(v) for v in entrees[colonne]]
    trace.textposition = "outside"
    trace.textfont = dict(size=TAILLE_ETIQUETTE)
fig_entrees.update_layout(barmode='group', xaxis_title="Mois", yaxis_title="Nombre de clients", separators=", ",
                          yaxis_range=[0, entrees['retard'].max() * 1.2], height=430,
                          legend=dict(orientation="h", x=0, xanchor="left", y=1.02, yanchor="bottom", title_text=""), margin=dict(t=50))
st.plotly_chart(fig_entrees, width='stretch')
st.caption("Comment lire : pour chaque mois, le nombre de clients qui entrent en retard (codification 2 ou plus, alors qu'ils ne l'étaient pas le mois d'avant), et le nombre de clients qui atteignent ce mois-là leur deuxième mois de retard d'affilée, seuil d'entrée au contentieux. Codifications corrigées, tout le périmètre, sans le défaut. Avril n'a pas de mois précédent, et en mai le début d'une série de retards n'est pas connu : l'entrée au contentieux n'y est pas mesurable.")
passages = entrees['passage'].dropna()
juin_aout = passages.iloc[:-1]
sept_e = entrees.iloc[-1]
st.markdown(f"""
- **Les entrées en retard augmentent au fil des mois** : {nombre_fr(entrees['retard'].iloc[0])} en mai, {nombre_fr(entrees['retard'].max())} au plus haut ({entrees.loc[entrees['retard'].idxmax(), 'mois'].lower()}). C'est la montée des retards vue en page 4.6.
- **Le passage au contentieux suit la même pente, avec un mois de décalage** : d'un mois sur l'autre, entre {nombre_fr(juin_aout.min())} et {nombre_fr(juin_aout.max())} % des clients entrés en retard sont encore en retard le mois suivant, et franchissent ainsi le seuil du contentieux. La proportion est stable : c'est le nombre de nouveaux retards qui fait grossir le contentieux, pas une aggravation du comportement.
- **Septembre fait exception** : seuls {nombre_fr(sept_e['passage'])} % des retards d'août atteignent un deuxième mois en septembre. Une partie d'entre eux porte la codification provisoire {codif('1')}, que la banque n'a pas encore tranchée (page 5.2). À l'inverse, les {nombre_fr(sept_e['retard'])} retards qui commencent en septembre sont comptés au contentieux, sauf quand la facture a été payée (retard payé) : par prudence, faute de connaître la suite, et parce que la codification suit le paiement avec un mois de décalage. Un retard codifié en septembre traduit déjà au moins 60 jours sans paiement.
""")

# 4.3 Population contentieuse mois par mois : au contentieux au mois n = au moins le deuxième mois de retard d'affilée,
# PAY_n >= 2 et PAY_(n+1) >= 2 (mai à septembre ; avril n'est pas mesurable, mars étant inconnu).
# Septembre : on passe de ce décompte à la population retenue à la fin de la période (règle de la page) en retirant les
# retards payés en fin de série et en ajoutant les premiers retards de septembre non payés, comptés par prudence
MOIS_STOCK = [(5, "Mai"), (4, "Juin"), (3, "Juillet"), (2, "Août"), (1, "Septembre")]
stock = pd.DataFrame([{'mois': nom, 'clients': int(((s12[f'PAY_{n}'] >= 2) & (s12[f'PAY_{n + 1}'] >= 2)).sum())}
                      for n, nom in MOIS_STOCK])
serie_sept = (s12['PAY_1'] >= 2) & (s12['PAY_2'] >= 2)
paye_serie = int((serie_sept & (s12['MOIS_SORTIE_CTX'] == 0)).sum())
prudence = int(((s12['PAY_1'] >= 2) & (s12['PAY_2'] < 2) & (statut == "Au contentieux")).sum())
nb_retenus = int((statut == "Au contentieux").sum())
LIBELLE_FIN = "Fin de période<br>(population retenue)"

st.markdown("#### La population contentieuse, mois par mois")
col_stock, col_stock_texte = st.columns([2, 1], vertical_alignment="center")
with col_stock:
    fig_stock = go.Figure()
    fig_stock.add_trace(go.Bar(x=list(stock['mois']) + [LIBELLE_FIN], y=list(stock['clients']) + [nb_retenus - prudence],
                               name="Au moins deux mois de retard d'affilée", marker_color=STATUTS_CTX["Au contentieux"],
                               hovertemplate="%{x}<br>%{y} clients<extra></extra>"))
    fig_stock.add_trace(go.Bar(x=[LIBELLE_FIN], y=[prudence], name="Premier retard en septembre (compté au contentieux)",
                               marker=dict(color=STATUTS_CTX["Au contentieux"], opacity=0.55, pattern_shape="/"),
                               hovertemplate="%{x}<br>%{y} clients<extra></extra>"))
    for _, row in stock.iterrows():
        etiquette_grise(fig_stock, row['mois'], row['clients'], nombre_fr(row['clients']))
    etiquette_grise(fig_stock, LIBELLE_FIN, nb_retenus, nombre_fr(nb_retenus))
    fig_stock.update_layout(barmode='stack', xaxis_title="Mois", yaxis_title="Clients au contentieux", separators=", ",
                            yaxis_range=[0, max(stock['clients'].max(), nb_retenus) * 1.2], height=440,
                            legend=dict(orientation="h", x=0, xanchor="left", y=1.02, yanchor="bottom", title_text=""), margin=dict(t=50))
    st.plotly_chart(fig_stock, width='stretch')
with col_stock_texte:
    mai_s, aout_s, sept_s = stock.iloc[0], stock.iloc[3], stock.iloc[4]
    st.markdown(f"""
- **De mai à août, la population contentieuse grossit chaque mois** : de {nombre_fr(mai_s['clients'])} à {nombre_fr(aout_s['clients'])} clients, soit {nombre_fr((aout_s['clients'] / mai_s['clients'] - 1) * 100)} % de plus.
- **Septembre semble marquer une baisse** ({nombre_fr(sept_s['clients'])} clients), mais une partie des retards d'août y porte la codification provisoire {codif('1')}, que la banque n'a pas encore tranchée.
- **La population retenue à la fin de la période** ({nombre_fr(nb_retenus)} clients) part de septembre : on retire les {nombre_fr(paye_serie)} retards payés en fin de série, et on ajoute les {nombre_fr(prudence)} premiers retards de septembre : la suite n'est pas connue, et la codification suit le paiement avec un mois de décalage, si bien qu'un retard de septembre traduit déjà au moins 60 jours sans paiement.
""")
st.caption("Comment lire : chaque mois, le nombre de clients au contentieux, c'est-à-dire en retard ce mois-là pour au moins le deuxième mois d'affilée. Codifications corrigées, tout le périmètre, sans le défaut. Avril n'est pas mesurable : on ne sait pas si son retard prolonge un retard de mars. La dernière barre est la population retenue par la règle, celle qui est retirée du machine learning.")

# Ce que deviennent, le mois suivant, les clients au contentieux d'un mois donné (codifications corrigées, sans le défaut)
LIBELLES_TRANSITION = [(4, "Mai → juin"), (3, "Juin → juillet"), (2, "Juillet → août"), (1, "Août → septembre")]
lignes_transition, transitions = [], {}
for n, libelle in LIBELLES_TRANSITION:
    au_ctx = (s12[f'PAY_{n + 2}'] >= 2) & (s12[f'PAY_{n + 1}'] >= 2)     # au contentieux le mois n+1
    suivant, avant = s12.loc[au_ctx, f'PAY_{n}'], s12.loc[au_ctx, f'PAY_{n + 1}']
    t = {'n': int(au_ctx.sum()), 'reste': (suivant >= 2).mean() * 100, 'un': (suivant == 1).mean() * 100,
         'sain': (suivant <= 0).mean() * 100, 'redescend': ((suivant == 2) & (avant > 2)).mean() * 100,
         'nb_un': int((suivant == 1).sum())}
    transitions[libelle] = t
    lignes_transition.append([f"<b>{libelle}</b> ({nombre_fr(t['n'])} clients)", f"{nombre_fr(t['reste'], 1)} %",
                              f"{nombre_fr(t['un'], 1)} %", f"{nombre_fr(t['sain'], 1)} %", f"{nombre_fr(t['redescend'], 1)} %"])
st.markdown("##### Pourquoi septembre baisse : ce que deviennent, le mois suivant, les clients au contentieux")
tableau_html(["Au contentieux le premier mois, et le mois suivant :", "toujours en retard", f"passés à la codification {codif('1')}",
              "revenus à une codification sans retard", f"dont : un retard de 3 ou plus redescendu à {codif('2')}"],
             lignes_transition, largeurs=[30, 16, 18, 18, 18])
st.caption("Comment lire : on part des clients au contentieux un mois donné, et on regarde leur codification le mois suivant ; chaque ligne fait 100 % pour les trois premières colonnes. La dernière colonne isole, parmi ceux restés en retard, les retards de 3 ou plus redescendus à 2. Codifications corrigées, tout le périmètre, sans le défaut.")
historique = [transitions[l] for _, l in LIBELLES_TRANSITION[:-1]]
septembre_t = transitions["Août → septembre"]
st.markdown(f"""
- **De mai à août, la mécanique est stable** : chaque mois, {nombre_fr(min(t['reste'] for t in historique))} à {nombre_fr(max(t['reste'] for t in historique))} % des clients au contentieux le restent, et {nombre_fr(min(t['sain'] for t in historique))} à {nombre_fr(max(t['sain'] for t in historique))} % en sortent. Seul leur nombre augmente.
- **En septembre, la codification {codif('1')} apparaît d'un coup** : {nombre_fr(septembre_t['un'], 1)} % des clients au contentieux en août y passent. Elle prend la place **à la fois des maintiens** (seuls {nombre_fr(septembre_t['reste'])} % restent en retard) **et des sorties** ({nombre_fr(septembre_t['sain'])} % seulement reviennent sans retard). La baisse de septembre n'est donc pas une amélioration : c'est un **changement de codification**, une situation que la banque n'a pas encore tranchée (page 5.2).
- **Les retards qui redescendent à {codif('2')} progressent lentement** ({nombre_fr(historique[0]['redescend'], 1)} % entre mai et juin, {nombre_fr(septembre_t['redescend'], 1)} % entre août et septembre) : la façon de codifier les dossiers en souffrance semble évoluer au fil des mois (page 4.6).
- **La dernière barre ne compense pas cette baisse.** Les {nombre_fr(septembre_t['nb_un'])} clients restés à {codif('1')} en septembre (la règle de septembre a déjà remis à {codif('2')} ceux qui n'avaient rien payé sur deux factures) sont traités comme sortis du contentieux. Ce traitement a été vérifié : leur risque est proche de celui des clients sortis du retard (section 6). Les {nombre_fr(prudence)} premiers retards de septembre ajoutés à la population retenue sont d'autres clients, dont le **premier** retard tombe en septembre.

**Une hypothèse sur ces changements de codification** : d'après le Seven Pillars Institute, l'autorité de supervision taïwanaise (FSC) demande en 2005 aux banques de mettre en place un système de négociation avec leurs débiteurs, et interdit le recouvrement abusif ([« The Taiwan Credit Card Crisis »](https://sevenpillarsinstitute.org/case-studies/taiwans-credit-card-crisis/), voir aussi la page d'accueil). Des arrangements de ce type pourraient faire redescendre ou mettre en attente des codifications sans paiement. Mais la source ne date pas ces mesures dans l'année, et le mécanisme officiel de négociation n'est mis en place qu'en 2006 (Tsai, 2007) : c'est une piste cohérente, pas un constat.
""")

# ------------------------------------------------------------------------------
st.subheader("5. Ce que la définition transmet au machine learning", anchor="indicateurs")
st.markdown(f"""
Les clients au contentieux sont traités par la règle. Pour tous les autres, l'historique de leurs retards reste une information précieuse : il est transmis au modèle sous forme d'indicateurs, calculés au nettoyage (niveau 5) et définis une seule fois dans [docs/colonnes_creees.md]({GH}/docs/colonnes_creees.md).
""")
st.markdown(f"""
**Pourquoi créer ces colonnes ?** Elles ont été pensées pour deux usages à la fois.

*Classer la population.* À elles seules, elles disent dans quelle situation se trouve chaque client à la fin de la période : au contentieux (`FLAG_CTX` = 1 et `MOIS_SORTIE_CTX` = -1), sorti du contentieux, avec un retard payé, avec un retard isolé régularisé, ou sans aucun retard. Ce sont elles qui définissent la population retirée du machine learning, et elles rendent la règle **traçable** : la situation de chaque client se retrouve sans refaire le calcul. Elles servent aussi à **ne rien perdre en corrigeant** : `SURVEILLANCE_RECENTE` et `FAUX_CODAGE` gardent la trace de ce que la banque avait signalé avant la correction.

*Nourrir le machine learning.* Pour les clients qui restent dans le modèle, elles résument l'historique des retards en informations lisibles (passé par le contentieux ou non, combien de temps, quand il en est sorti, ou un simple retard isolé), là où les codifications brutes mêlent retards réels, statuts provisoires et retards figés. Le risque varie avec cet historique (page 5.5) : ce sont de nouvelles variables, testées en partie 6, et c'est le modèle qui dira si elles améliorent la prédiction.
""")
st.markdown("Chaque colonne part d'une **valeur par défaut**, celle d'un client à qui il n'est rien arrivé ; c'est seulement la détection d'un événement (un passage au contentieux, une sortie, un retard isolé, un retard posé sur une facture nulle) qui la modifie. Aucune colonne n'est jamais vide. Les colonnes de mois se lisent toujours avec leur indicateur : si `FLAG_CTX` vaut 0, la valeur de `MOIS_SORTIE_CTX` n'a pas de sens.")
tableau_html(["Colonne", "Valeur par défaut", "Ce qui la modifie, et ce qu'elle dit du client"], [
    ["<code>FLAG_CTX</code>", "0", "1 si le client est passé par le contentieux pendant la période"],
    ["<code>MOIS_SORTIE_CTX</code>", "-1 (pas de sortie)", "Mois de sa dernière sortie du contentieux : 1 (septembre) à 5 (mai), ou 0 si sa sortie est présumée en octobre (retard payé en fin de série). Reste à -1 pour un client encore au contentieux, comme pour un client qui n'y est jamais passé"],
    ["<code>NB_MOIS_CTX</code>", "0", "Durée de son dernier passage au contentieux, en mois de retard consécutifs (1 à 6)"],
    ["<code>FLAG_RETARD</code>", "0", "1 si le client a eu un retard isolé, régularisé ensuite"],
    ["<code>MOIS_SORTIE_RETARD</code>", "-1 (pas de régularisation)", "Mois de la régularisation de ce retard isolé : 1 à 4, ou 0 si elle est présumée en octobre (retard isolé de septembre payé)"],
    ["<code>SURVEILLANCE_RECENTE</code>", "0", "1 pour un compte (ré)activé dont un retard posé sur une facture nulle a été corrigé (page 5.2)"],
    ["<code>FAUX_CODAGE</code>", "0", "1 pour un faux 2 corrigé (page 5.2)"],
], largeurs=[24, 18, 58])

# ------------------------------------------------------------------------------
st.subheader("6. Vérifications : les codifications 1 laissées telles quelles, et le nettoyage", anchor="verifications")
st.markdown("La définition posée, deux vérifications restent à faire : les codifications 1 que la règle de septembre laisse telles quelles ne cachent-elles pas des retards ? Et le nettoyage applique-t-il exactement les corrections décidées en page 5.2 ?")
# Validation sur l'entraînement : clients en retard en août, selon leur codification de septembre
aout = train[train['PAY_2'] >= 2]
GROUPES_SEPT = [
    ("Revenus à une codification saine", aout['PAY_1'] <= 0, STATUTS_CTX["Retard isolé régularisé"]),
    ("Restés codifiés 1 (indécidables)", aout['PAY_1'] == 1, COULEURS["gris"]),
    ("Toujours en retard (2 et plus)", aout['PAY_1'] >= 2, STATUTS_CTX["Au contentieux"]),
]
stats_sept = pd.DataFrame([{'groupe': nom, 'clients': int(m.sum()), 'taux': aout.loc[m, 'dpnm'].mean() * 100, 'couleur': c}
                           for nom, m, c in GROUPES_SEPT])

st.markdown("##### Les codifications 1 restantes ont le risque des clients sortis du retard")
st.markdown(f"On part ici des {nombre_fr(len(aout))} clients du **jeu d'entraînement** (le seul où l'on regarde le défaut) qui étaient **en retard en août**, depuis un mois ou plus : un point de départ plus large que le tableau des transitions, qui partait des seuls clients au contentieux, sur tout le périmètre. Ce qui les distingue, c'est leur codification de septembre, une fois les corrections appliquées. Si les codifications 1 laissées telles quelles cachaient des retards, elles auraient le risque des clients restés en retard.")
fig_sept = go.Figure(go.Bar(x=stats_sept['groupe'], y=stats_sept['taux'], marker_color=stats_sept['couleur'],
                            customdata=stats_sept['clients'], hovertemplate="%{x}<br>%{customdata} clients<extra></extra>"))
fig_sept.add_hline(y=taux_train, line_dash="dash", line_width=2, line_color=COULEURS["orange"])
for _, row in stats_sept.iterrows():
    etiquette_grise(fig_sept, row['groupe'], row['taux'], f"{nombre_fr(row['taux'], 1)} % ({nombre_fr(row['clients'])} clients)")
fig_sept.update_layout(xaxis_title="Codification de septembre (clients en retard en août)", yaxis_title="Taux de défaut de paiement (%)",
                       yaxis_range=[0, stats_sept['taux'].max() * 1.2], height=420, separators=", ")
st.plotly_chart(fig_sept, width='stretch')
st.caption(f"Jeu d'entraînement uniquement. Ligne en pointillés : taux de défaut moyen de l'entraînement ({nombre_fr(taux_train, 1)} %).")

sain, un, retard = stats_sept.iloc[0], stats_sept.iloc[1], stats_sept.iloc[2]
restants = int((df['PAY_1'] == 1).sum())
st.markdown(f"""
- **Les clients restés codifiés {codif('1')} font défaut à {nombre_fr(un['taux'], 1)} %**, un niveau proche des clients revenus à une codification saine ({nombre_fr(sain['taux'], 1)} %), et loin de ceux toujours en retard ({nombre_fr(retard['taux'], 1)} %). Les traiter comme sortis du retard, ce que fait la règle, est donc cohérent.
- **Les codifications {codif('1')} restent pour la plupart indécidables** : sur les {nombre_fr(NB_CODIF_1_ORIGINE)} de septembre dans les données d'origine, {nombre_fr(restants)} sont toujours là après tout le nettoyage, soit {nombre_fr(restants / NB_CODIF_1_ORIGINE * 100, 1)} %. Seuls les montants permettent de trancher, et ils le font rarement : le niveau 5 n'en remet qu'une petite minorité à {codif('2')}.
- **Une piste pour la suite** : un modèle de machine learning pourrait départager une partie de ces codifications {codif('1')} restantes, entre une vraie sortie du retard et un retard toujours en cours, en combinant la durée du retard, les paiements et l'évolution de la dette. Les règles métier, elles, ne tranchent que les cas où les paiements ne laissent aucun doute ([05_04_EDA_codification1.ipynb]({GH}/src/05_04_EDA_codification1.ipynb), conclusion).
- **L'ancienne correction a été abandonnée à raison.** Une version antérieure du nettoyage remettait à {codif('2')} toutes les codifications {codif('1')} qui suivent un retard. Simulée sur l'entraînement, elle ajoutait {nombre_fr(ANCIEN_AJOUTES)} clients au contentieux, avec seulement {nombre_fr(ANCIEN_TAUX_AJOUTES, 1)} % de défaut, et faisait chuter le taux de défaut du contentieux de {nombre_fr(ANCIEN_TAUX_CTX_AVANT, 1)} % à {nombre_fr(ANCIEN_TAUX_CTX_APRES, 1)} % : elle mélangeait des clients sortis du retard au vrai contentieux ([05_04_EDA_codification1.ipynb]({GH}/src/05_04_EDA_codification1.ipynb), cellule 31).
""")

st.markdown("##### Le niveau 5 du nettoyage : les corrections bien appliquées")
# Tous les clients au contentieux ont une dette en septembre : ils sont tous dans le périmètre
nb_ctx = int((s12['STATUT'] == "Au contentieux").sum())
st.markdown(f"""
Les corrections de la page 5.2 ont été inscrites dans le nettoyage, au **niveau 5** ([02_01_nettoyage.ipynb]({GH}/src/02_01_nettoyage.ipynb)) : les codifications corrigées remplacent celles de la banque dans les `PAY_n`, et les colonnes du contentieux sont ajoutées, dont `SURVEILLANCE_RECENTE` et `FAUX_CODAGE`. **Aucun client n'est retiré.** Toutes les analyses s'appuient désormais sur ces codifications corrigées, y compris la partie 4.

Un programme qui modifie des données peut se tromper de trois façons : oublier des cas, créer des erreurs, ou déformer la population. Le niveau 5 a été contrôlé sur ces trois points, en comparant les données avant et après les corrections ([05_04_EDA_codification1.ipynb]({GH}/src/05_04_EDA_codification1.ipynb), section 7, cellules 36, 39 et 42) :
""")
tableau_html(["Question", "Ce qui a été vérifié", "Résultat"], [
    ["<b>Rien n'a été oublié ?</b>",
     f"Cas à corriger avant les corrections : {CTRL_FAUX_RETARDS} retards posés sur une facture nulle, {CTRL_REMIS_A_2} mois de septembre sans aucun paiement sur deux factures à payer, {CTRL_SOLDES} mois de septembre avec une facture soldée. Après : aucun. Une seconde application des règles ne change plus aucune codification.",
     ("✅ Aucun cas oublié", "white-space: nowrap;")],
    ["<b>Aucune erreur créée ?</b>",
     f"{nombre_fr(CTRL_CODIFS_MODIFIEES)} codifications modifiées chez {CTRL_CLIENTS_MODIFIES} clients (environ 1 %), toutes expliquées par une règle : {CTRL_RETARDS_NEUTRALISES} retards {codif('2')} posés sur une facture nulle remplacés, {CTRL_REMIS_DEPUIS_1} codifications {codif('1')} et {CTRL_REMIS_DEPUIS_SAIN} codifications saines remises à {codif('2')}, quelques retours à la codification d'avant le retard. Les sept colonnes ajoutées par le niveau 5 (<code>SURVEILLANCE_RECENTE</code>, <code>FAUX_CODAGE</code>, <code>FLAG_CTX</code>, <code>MOIS_SORTIE_CTX</code>, <code>FLAG_RETARD</code>, <code>MOIS_SORTIE_RETARD</code>, <code>NB_MOIS_CTX</code>) ont été recalculées avec les fonctions de l'étude du contentieux : aucun écart, client par client.",
     ("✅ Aucune modification sans explication", "")],
    ["<b>La population n'est pas déformée ?</b>",
     f"Même population contentieuse que la règle étudiée ({nombre_fr(nb_ctx)} clients au contentieux), et les codifications {codif('1')} laissées telles quelles ont le risque de clients sortis du retard (ci-dessus).",
     ("✅ Population conservée", "")],
], largeurs=[20, 60, 20])
st.caption("Les retards qui restent posés sur une facture nulle après le nettoyage ne sont pas des erreurs : ils prolongent une série commencée sur une vraie dette (seules les entrées en retard sur une facture nulle sont corrigées).")


st.info(f"""
**Ce qu'il faut retenir** : un client est au contentieux quand son retard s'installe, c'est-à-dire au moins deux mois de retard d'affilée, ou un retard en septembre dont on ne connaît pas la suite. Il n'en sort que si sa codification redescend, ou si sa facture est payée. Ainsi définie, la population contentieuse rassemble {nombre_fr(part['Au contentieux'], 1)} % du périmètre. Reste à vérifier qu'elle décrit un vrai comportement, et pas seulement une étiquette de la banque : c'est l'objet de la page suivante, avant même de regarder le défaut.
""")
