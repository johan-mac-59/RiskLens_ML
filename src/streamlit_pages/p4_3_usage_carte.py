from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 4.3 : LE TYPE D'USAGE DE LA CARTE (COMPTANT OU CRÉDIT)
# Analyses reprises du notebook storytelling (cellules 86 à 89), refaites en Plotly ;
# tous les chiffres sont calculés en direct sur le dataset.
# ==============================================================================
df = load_data()
taux_moyen = df["dpnm"].mean() * 100

# ratio_PAY_BILL_global, ratio_PAY_BILL_median, TYPE_USAGE, ratio_PAY_BILL_regularite et PAY_habituel sont lues dans le CSV :
# créées par 05_03_EDA_storytelling avant l'export (définitions dans docs/colonnes_creees.md)
ratio_columns = [f'ratio_PAY_BILL{i}' for i in range(1, 6)]

# Les graphiques n'affichent que les médianes de 0 et plus
sans_facture_sept = int((df['ratio_PAY_BILL_median'] == -1).sum())
sans_facture = sans_facture_sept + int(df['ratio_PAY_BILL_median'].isna().sum())
df_ratio = df[df['ratio_PAY_BILL_median'] >= 0].copy()
# Nombre de mois avec une facture due sur lesquels repose la médiane de chaque client
nb_mois_ratio = ratios_affichables(df, ratio_columns).notna().sum(axis=1)
peu_de_mois = int((nb_mois_ratio == 2).sum())

# Types d'usage : colonne TYPE_USAGE, construite uniquement sur les paiements (médiane du ratio de paiement, ou taux de
# remboursement global quand une seule facture est due ; jamais du taux de défaut ni des codifications).
# Les libellés ci-dessous servent à l'affichage et doivent rester ceux de la colonne
RIEN, DIFFICULTE, LENT, RAPIDE, MIXTE, COMPTANT = (
    "Ne paie rien", "Client en difficulté", "Crédit lent", "Crédit rapide", "Usage mixte", "Paiement comptant")
TYPES = [
    (RIEN, "0 %"),
    (DIFFICULTE, "plus de 0 à 3 %, moins qu'une mensualité"),
    (LENT, "plus de 3 à 6 %, autour de la mensualité minimale"),
    (RAPIDE, "plus de 6 à 15 %"),
    (MIXTE, "plus de 15 à 95 %"),
    (COMPTANT, "plus de 95 %, paiement en avance ou arrondi au-dessus compris"),
]
NOMS_TYPES = [nom for nom, _ in TYPES]
df_ratio['type_usage'] = pd.Categorical(df_ratio['TYPE_USAGE'], categories=NOMS_TYPES)
# Septième groupe, sans ratio médian (médiane à -1) : la première facture due de la période arrive en septembre.
# Il entre dans la répartition, le taux de défaut et les codifications, pas dans les analyses du ratio médian
PREMIERE = "Première facture"
NOMS_AFFICHES = NOMS_TYPES + [PREMIERE]
df['type_usage'] = pd.Categorical(df['TYPE_USAGE'], categories=NOMS_AFFICHES)

stats_type = (
    df.groupby('type_usage', observed=False)['dpnm']
    .agg(clients='size', taux='mean')
    .reset_index()
)
stats_type['taux'] = stats_type['taux'] * 100
stats_type['part'] = stats_type['clients'] / stats_type['clients'].sum() * 100
COULEURS_TYPES = dict(zip(NOMS_AFFICHES, px.colors.qualitative.Safe))

entete_partie_4(df)

st.markdown("---")
st.header("4.3 Le type d'usage de la carte : plus le client rembourse, moins il fait défaut", anchor="usage-carte")
st.markdown("""
Une carte de crédit s'utilise de deux façons : comme un **moyen de paiement**, en réglant toute la facture à l'échéance (paiement comptant), ou comme un **crédit**, en ne remboursant qu'une partie de la facture et en laissant le reste courir, avec des intérêts. La page « 3.3 Les codifications » a montré ces deux comportements mois par mois ; on les regarde ici client par client, pour voir s'ils sont réguliers et s'ils pèsent sur le risque.
""")

# ------------------------------------------------------------------------------
st.subheader("Sur 5 mois, quelle part de sa dette cumulée chaque client rembourse-t-il ?", anchor="remboursement-global")
global_affiche = df.loc[df['ratio_PAY_BILL_global'].notna(), 'ratio_PAY_BILL_global']
fig_global = px.histogram(global_affiche, labels={'value': 'Remboursements cumulés / dette cumulée sur 5 mois (%)', 'count': 'Nombre de clients'})
fig_global.update_traces(xbins=dict(start=0, end=201, size=1), marker_color=COULEURS["turquoise"], marker_line_width=0,
                         hovertemplate="Taux de %{x} % : %{y} clients<extra></extra>")
fig_global.update_layout(xaxis_title="Remboursements cumulés sur 5 mois / dette cumulée sur 5 mois (%)", yaxis_title="Nombre de clients",
                         showlegend=False, height=450)
st.plotly_chart(fig_global, width='stretch')
st.caption("Taux de remboursement global : remboursements cumulés sur 5 mois (paiements de mai à septembre) divisés par la "
           "dette cumulée sur 5 mois (factures d'avril à août), chaque facture impayée reportée dans la suivante n'étant comptée "
           "qu'une fois ; écrêté entre 0 et 200 %. Un solde négatif n'efface aucune dette : c'est un paiement en trop, compté comme tel "
           "seulement s'il est encore sur la carte fin septembre (une avance dépensée ensuite n'est pas un trop-payé). "
           "La facture de septembre, payée en octobre, n'entre pas dans le calcul.")
pic_credit = int(np.floor(global_affiche[global_affiche < 90]).value_counts().idxmax())
part_credit_global = global_affiche.between(10, 30, inclusive="left").mean() * 100
part_solde_global = global_affiche.between(90, 110).mean() * 100
st.markdown(f"""
Avant de regarder mois par mois, une mesure simple résume le comportement de chaque client : ses **remboursements cumulés sur 5 mois**, rapportés à sa **dette cumulée sur 5 mois**, c'est-à-dire la part de tout ce qu'il a dû qu'il a réellement remboursée. Deux groupes se détachent nettement :
- **{nombre_fr(part_solde_global, 1)} %** des clients remboursent la totalité de leur dette cumulée (entre 90 et 110 %) : ils utilisent leur carte comme un moyen de paiement ;
- **{nombre_fr(part_credit_global, 1)} %** en remboursent entre 10 et 30 %, avec un pic vers {pic_credit} % : ils laissent courir leur crédit. Chaque mois, ils ne paient qu'une petite part de leur facture (3 à 5 % le plus souvent, voir plus bas) : cumulés sur 5 mois, ces petits remboursements ne couvrent qu'une fraction de leur dette cumulée.

Cette mesure absorbe le décalage d'un mois des paiements : un client qui règle tout avec un mois de retard arrive bien à 100 %.
""")

# ------------------------------------------------------------------------------
st.subheader("Deux comportements réguliers : rembourser très peu, ou tout rembourser", anchor="deux-usages")
st.markdown("On revient maintenant au **comportement mensuel** du client : non plus ce qu'il a remboursé en cumulé sur 5 mois, "
            "mais la part de sa facture qu'il paie **d'habitude, chaque mois**, mesurée par la médiane de ses ratios de paiement mensuels.")

# Histogramme du ratio de paiement médian par client (repris de la cellule 77, en Plotly)
fig_medianes = px.histogram(
    df_ratio['ratio_PAY_BILL_median'], nbins=100,
    labels={'value': 'Ratio de paiement médian du client (%)', 'count': 'Nombre de clients'},
)
# Grain de 1 % : une barre par point de pourcentage, de 0 à 200 %
fig_medianes.update_traces(xbins=dict(start=0, end=201, size=1), marker_color=COULEURS["turquoise"], marker_line_width=0,
                           hovertemplate="Ratio médian de %{x} % : %{y} clients<extra></extra>")
fig_medianes.update_layout(xaxis_title='Ratio de paiement médian du client sur les mois avec une facture due (%)',
                           yaxis_title='Nombre de clients', showlegend=False, height=500)
st.plotly_chart(fig_medianes, width='stretch')
st.caption("Ratio de paiement : montant payé divisé par la facture qu'il règle, écrêté entre 0 et 200 %. Pour chaque client, médiane des mois où une facture était due (définition ci-dessous).")

part_faible = (df_ratio['ratio_PAY_BILL_median'] <= 10).mean() * 100
part_solde = (df_ratio['ratio_PAY_BILL_median'] > 95).mean() * 100
# Clients dont la médiane classique (moyenne des deux valeurs du milieu) n'est pas une valeur observée
mediane_classique = ratios_affichables(df_ratio, ratio_columns).median(axis=1)
nb_corriges = int((mediane_classique != df_ratio['ratio_PAY_BILL_median']).sum())
pointe_50_classique = int((mediane_classique == 50).sum())
pointe_50 = int((df_ratio['ratio_PAY_BILL_median'] == 50).sum())
st.markdown(f"""
Les clients ont des **tendances d'usage** nettes : leur comportement habituel se concentre sur deux pics. **{nombre_fr(part_faible, 1)} %** des clients remboursent en général 10 % ou moins de leur facture, et **{nombre_fr(part_solde, 1)} %** la règlent en totalité (plus de 95 %). Les comportements intermédiaires sont rares. Avec un nombre pair de mois, la médiane classique fait la moyenne des deux valeurs du milieu : un client qui alterne un mois sans paiement et un mois soldé, souvent à cause du décalage d'un mois des paiements (page 3.3), obtiendrait 50 %, un comportement qu'il n'a jamais eu. Quand les deux valeurs du milieu diffèrent, on garde donc celle qui est la plus proche de son **taux de remboursement global** (graphique précédent) : tout ce qu'il a payé sur la période, rapporté à tout ce qu'il a dû. La médiane reste ainsi un ratio réellement observé, rattaché au comportement d'ensemble du client. {nombre_fr(nb_corriges)} clients sont concernés ; les clients à 50 % pile passent de {nombre_fr(pointe_50_classique)} à {nombre_fr(pointe_50)}. Ces médianes portent sur les {nombre_fr(len(df_ratio))} clients qui ont eu au moins une facture à payer d'avril à août. Les {nombre_fr(sans_facture)} autres n'ont pas de ratio mesurable et ne sont pas affichés : {nombre_fr(sans_facture_sept)} n'ont qu'une facture en septembre, dont le paiement tombe en octobre, hors période (des comptes qui commencent à servir, médiane fixée à -1 ; ils forment le groupe « {PREMIERE} », présenté plus bas avec les types d'usage), et {nombre_fr(sans_facture - sans_facture_sept)} n'ont eu aucune facture positive sur les 6 mois (page « 4.2 L'usage du crédit »).
""")

st.subheader("Six types d'usage, et un comportement plutôt régulier", anchor="regularite")
# Répartition de tous les ratios mensuels (mois avec une facture due) : elle ne dépend pas de la définition de la médiane
ratios_mensuels = pd.concat([df.loc[df[f'BILL_AMT{n + 1}'] > 0, f'ratio_PAY_BILL{n}'] for n in range(1, 6)])
partiels = np.floor(ratios_mensuels[(ratios_mensuels > 0) & (ratios_mensuels <= 95)])
pic = int(partiels.value_counts().idxmax())
part_pic = (partiels == pic).mean() * 100
une_facture = int((nb_mois_ratio[df_ratio.index] == 1).sum())
arrondis = int(((df_ratio['ratio_PAY_BILL_median'] > 105) & (df_ratio['type_usage'] == COMPTANT)).sum())
# Part des clients qui ont soldé au moins une facture (un mois payé à plus de 95 %), par type d'usage
deja_solde = (ratios_affichables(df_ratio, ratio_columns) > 95).any(axis=1).groupby(df_ratio['type_usage'], observed=False).mean() * 100
# Usage mixte : quels comportements derrière la médiane ? (mois soldés, mois à 15 % ou moins, retards)
est_mixte = df_ratio['type_usage'] == MIXTE
mois_mixte = ratios_affichables(df_ratio, ratio_columns)[est_mixte]
solde_mixte, bas_mixte = (mois_mixte > 95).any(axis=1), (mois_mixte <= 15).any(axis=1)
retard_mixte = (df_ratio.loc[est_mixte, [f'PAY_{n}' for n in range(1, 7)]] >= 2).any(axis=1)
part_alterne = (solde_mixte & bas_mixte).mean() * 100          # mois soldés et mois à crédit
part_eleve = (~solde_mixte & ~bas_mixte).mean() * 100          # remboursements élevés chaque mois, sans solder
part_retard_solde = (retard_mixte & solde_mixte).mean() * 100  # un retard, et au moins une facture soldée
st.markdown("Chaque client est rangé selon son ratio de paiement médian : " + " ; ".join(f"**{nom}** ({tranche})" for nom, tranche in TYPES) + ". "
            "Les tranches ont été posées sur la répartition de **tous les ratios de paiement mensuels**, qui ne dépend pas de la façon "
            f"de calculer la médiane, et sur la logique métier : parmi les paiements partiels, le point le plus fréquent est {pic} % "
            f"({nombre_fr(part_pic, 1)} % des mois), celui de la mensualité minimale ; au-delà de 15 %, un client sur deux a déjà soldé au moins une facture : "
            "on quitte le crédit remboursé régulièrement. Les tranches ne découlent pas du taux de défaut. "
            f"Un septième groupe, **{PREMIERE}**, réunit les clients qui n'avaient aucune facture due d'avril à août : leur première facture "
            "due de la période arrive en septembre, et son paiement tombe en octobre, hors période. Ils n'ont donc pas de ratio médian, "
            "et aucune habitude de paiement n'est encore mesurable. C'est la première facture **de la période observée**, pas forcément "
            "celle de la vie du compte : le groupe mêle des ouvertures de compte et d'anciens comptes qui se réveillent.")
st.markdown(f"""
- **Le crédit lent et le crédit rapide** laissent tous deux leur dette courir : le premier paie autour du minimum, le second un peu plus. Seuls {nombre_fr(deja_solde[LENT], 0)} % et {nombre_fr(deja_solde[RAPIDE], 0)} % d'entre eux ont soldé au moins une facture sur la période, contre {nombre_fr(deja_solde[MIXTE], 0)} % dans l'usage mixte.
- **L'usage mixte** (plus de 15 à 95 %) ne décrit pas un comportement, mais plusieurs, que la médiane réunit : un payeur au comptant qui ne règle qu'une partie de sa facture certains mois, un client à crédit qui rembourse une grosse part de sa dette par anticipation, un client qui rattrape un retard. Les paiements le montrent : {nombre_fr(part_alterne, 0)} % de ces clients alternent des mois soldés et des mois à 15 % ou moins, {nombre_fr(part_eleve, 0)} % remboursent chaque mois une part élevée de leur facture sans jamais la solder, et {nombre_fr(part_retard_solde, 0)} % ont à la fois connu un retard et soldé au moins une facture.
- **Le paiement comptant** comprend les clients qui paient en avance ou arrondissent au-dessus de leur facture : {nombre_fr(arrondis)} d'entre eux ont une médiane de plus de 105 %, le plus souvent un montant rond réglé sur une petite facture. Ils n'utilisent pas le crédit.
- **Les {nombre_fr(une_facture)} clients qui n'ont qu'une facture due** sont classés selon leur taux de remboursement global (premier graphique) : une seule valeur ne fait pas une médiane.

Les types reposent **uniquement sur les paiements** : aucune codification de la banque n'y entre, ce qui permet de les confronter plus bas à ces codifications.
""")

# Seuil de 3 % : part des mois codifiés en retard selon la part de la facture payée dans le mois (codification, pas défaut)
mois = pd.concat([pd.DataFrame({'ratio': df.loc[df[f'BILL_AMT{n + 1}'] > 0, f'ratio_PAY_BILL{n}'],
                                'retard': df.loc[df[f'BILL_AMT{n + 1}'] > 0, f'PAY_{n}'] >= 2}) for n in range(1, 6)])
retard_moins_1 = mois.loc[(mois['ratio'] > 0) & (mois['ratio'] < 1), 'retard'].mean() * 100
retard_3_6 = mois.loc[(mois['ratio'] >= 3) & (mois['ratio'] < 6), 'retard'].mean() * 100
st.markdown(f"Pourquoi 3 % ? Mois par mois, la banque pose un retard dans {nombre_fr(retard_moins_1, 0)} % des mois où le client paie moins de 1 % de sa facture, "
            f"mais dans {nombre_fr(retard_3_6, 0)} % seulement des mois où il en paie 3 à 6 %, une part qui ne baisse plus guère avant le paiement complet. "
            f"Le pic des ratios mensuels, autour de {pic} %, ressemble donc à la **mensualité minimale** acceptée par la banque : c'est une lecture empirique, "
            "aucune source ne donnant le minimum exigé en 2005. En dessous, le client paie moins qu'une mensualité : il est en difficulté.")

# Durée de remboursement d'une dette selon la mensualité, au taux des cartes en 2005 (17 à 20 % par an, on retient 20 %),
# sans nouveaux achats :
# mensualité constante = r / (1 - (1 + r)^-n), en % de la dette de départ, avec r le taux mensuel
TAUX_ANNUEL = 20
TAUX_MENSUEL = TAUX_ANNUEL / 100 / 12
SOURCE_TAUX = "https://www.taipeitimes.com/News/editorials/archives/2005/10/26/2003277465"


def mensualite(nb_mois):
    """Mensualité constante (en % de la dette de départ) qui rembourse la dette en nb_mois mois."""
    return TAUX_MENSUEL / (1 - (1 + TAUX_MENSUEL) ** -nb_mois) * 100


def duree_pour(pourcentage):
    """Nombre de mois à partir duquel la mensualité passe sous ce pourcentage de la dette."""
    return next(n for n in range(1, 241) if mensualite(n) <= pourcentage)


DUREES = [(48, "4 ans"), (36, "3 ans"), (24, "2 ans"), (12, "1 an"), (6, "6 mois"), (4, "4 mois (« en 4 fois »)"), (3, "3 mois (« en 3 fois »)")]
mois_3, mois_6, mois_15 = duree_pour(3), duree_pour(6), duree_pour(15)
STYLE_CELLULE_DUREE = "border: 1px solid rgba(128, 128, 128, 0.3); padding: 4px 10px; text-align: left;"
st.markdown(f"""
**Combien de temps pour rembourser ?** En 2005, les cartes de crédit taïwanaises facturaient entre 17 et 20 % d'intérêts par an ([Taipei Times, 26 octobre 2005]({SOURCE_TAUX})). Au haut de la fourchette, **{TAUX_ANNUEL} % par an**, voici la mensualité qui éteint une dette, sans nouvel achat, selon la durée choisie :
""")
st.markdown(
    '<table style="border-collapse: collapse; margin-bottom: 0.5rem;">'
    f'<thead><tr><th style="{STYLE_CELLULE_DUREE} background: rgba(128, 128, 128, 0.1);">Durée du remboursement</th>'
    f'<th style="{STYLE_CELLULE_DUREE} background: rgba(128, 128, 128, 0.1);">Mensualité, en % de la dette</th></tr></thead><tbody>'
    + "".join(f'<tr><td style="{STYLE_CELLULE_DUREE}">{libelle}</td><td style="{STYLE_CELLULE_DUREE}">{nombre_fr(mensualite(n), 1)} %</td></tr>'
              for n, libelle in DUREES)
    + "</tbody></table>",
    unsafe_allow_html=True,
)
st.markdown(f"""
Les tranches prennent alors un sens concret :
- **Crédit lent (3 à 6 %)** : une dette remboursée en {mois_6} mois à {mois_3} mois, soit jusqu'à {mois_3 // 12} ans. Avec de nouveaux achats chaque mois, elle ne s'éteint jamais : c'est le crédit renouvelable, au minimum.
- **Crédit rapide (6 à 15 %)** : un remboursement en {mois_15} à {mois_6} mois. C'est toujours du crédit, mais remboursé plus vite.
- **Usage mixte (plus de 15 %)** : moins de {mois_15} mois, jusqu'au paiement fractionné « en 3 ou 4 fois » ({nombre_fr(mensualite(4), 1)} à {nombre_fr(mensualite(3), 1)} % par mois). Ce n'est plus du crédit renouvelable, mais un achat étalé sur quelques mois, d'où un groupe où se côtoient paiements fractionnés, remboursements anticipés et paiements partiels de clients habituellement au comptant.

Le ratio rapporte chaque paiement à la facture du mois : un client qui continue d'utiliser sa carte garde une facture élevée, et son ratio reste proche de la mensualité du tableau.
""")

# Régularité : colonne ratio_PAY_BILL_regularite lue dans le CSV (créée par 05_03_EDA_storytelling, définie dans
# docs/colonnes_creees.md) ; le nombre de mois dus sert à ne garder que les clients avec au moins 3 mois
mois_dus = ratios_affichables(df_ratio, ratio_columns)
nb_mois_dus = mois_dus.notna().sum(axis=1)
regularite = df_ratio['ratio_PAY_BILL_regularite']
nb_conformes = (regularite * nb_mois_dus / 100).round()
assez = nb_mois_dus >= 3

st.markdown("""
Une médiane résume le comportement habituel d'un client, mais pas sa **régularité** : un client peut payer chaque mois au comptant, ou alterner crédit et comptant et tomber sur la même médiane. Pour le savoir, on compte, pour chaque client, les mois où son ratio de paiement tombe **dans la tranche de son type d'usage**. Le calcul porte sur les clients qui ont au moins 3 mois avec une facture due : avec un ou deux mois, la médiane se confond avec ces mois et la régularité ne dit rien.
""")
# Tableau HTML : les intitulés de colonnes reviennent à la ligne automatiquement
STYLE_CELLULE = "border: 1px solid rgba(128, 128, 128, 0.3); padding: 6px 8px; vertical-align: top; text-align: left;"
entetes = ["Type d'usage", "Nombre de clients (3 mois dus ou plus)", "Part moyenne des mois dans le même type d'usage",
           "Part des clients dont tous les mois avec facture sont dans le même type d'usage",
           "Part des clients dont moins de la moitié des mois avec facture y sont"]
lignes_html = ""
for nom in NOMS_TYPES:
    groupe = regularite[assez & (df_ratio['type_usage'] == nom)]
    valeurs = [nom, nombre_fr(len(groupe)), f"{nombre_fr(groupe.mean(), 1)} %",
               f"{nombre_fr((groupe == 100).mean() * 100, 1)} %", f"{nombre_fr((groupe < 50).mean() * 100, 1)} %"]
    lignes_html += "<tr>" + "".join(f'<td style="{STYLE_CELLULE}">{v}</td>' for v in valeurs) + "</tr>"
st.markdown(
    '<table style="width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 0.5rem;">'
    # Colonnes 1 et 2 plus étroites, pour laisser la place aux intitulés longs des colonnes 3 à 5
    '<colgroup><col style="width: 16%"><col style="width: 14%"><col style="width: 22%"><col style="width: 24%"><col style="width: 24%"></colgroup>'
    "<thead><tr>" + "".join(f'<th style="{STYLE_CELLULE} background: rgba(128, 128, 128, 0.1);">{e}</th>' for e in entetes)
    + f"</tr></thead><tbody>{lignes_html}</tbody></table>",
    unsafe_allow_html=True,
)
st.caption(f"Pour « {RIEN} » et « {COMPTANT} », la dernière colonne vaut 0 % par construction : quand la médiane vaut 0 % (ou plus de 95 %), "
           "au moins la moitié des mois valent 0 % (ou plus de 95 %).")

cinq = nb_mois_dus == 5
part_3_sur_5 = (nb_conformes[cinq] >= 3).mean() * 100
part_5_sur_5 = (nb_conformes[cinq] == 5).mean() * 100
regul = {nom: regularite[assez & (df_ratio['type_usage'] == nom)].mean() for nom in NOMS_TYPES}
# Payeurs au comptant : part de ceux dont tous les mois avec facture sont au comptant, et nature de leurs écarts
comptant = assez & (df_ratio['type_usage'] == COMPTANT)
part_comptant_tous = (regularite[comptant] == 100).mean() * 100
ecarts = mois_dus[comptant].stack()
ecarts = ecarts[ecarts <= 95]
part_ecarts_zero = (ecarts == 0).mean() * 100
part_ecarts_partiel = 100 - part_ecarts_zero
st.markdown(f"""
- **Le comportement de paiement est majoritairement récurrent** : parmi les clients qui ont 5 mois avec une facture due, {nombre_fr(part_3_sur_5, 0)} % ont au moins 3 mois sur 5 dans la tranche de leur type d'usage, et {nombre_fr(part_5_sur_5, 0)} % les ont tous.
- **Les comportements nets sont les plus stables** : en moyenne, {nombre_fr(regul[COMPTANT], 0)} % des mois d'un client au paiement comptant restent dans son type d'usage, {nombre_fr(regul[LENT], 0)} % pour le crédit lent et {nombre_fr(regul[RIEN], 0)} % pour ceux qui ne paient rien. Le paiement comptant reste pourtant une **habitude plus qu'une règle** : {nombre_fr(part_comptant_tous, 0)} % seulement des payeurs au comptant soldent tous leurs mois avec facture ; les autres ont un ou deux mois où ils ne paient pas au comptant. Ces mois-là, ils règlent seulement une partie de leur facture dans {nombre_fr(part_ecarts_partiel, 0)} % des cas, et ne paient rien dans {nombre_fr(part_ecarts_zero, 0)} % des cas.
- **Le crédit rapide et le client en difficulté sont moins stables** ({nombre_fr(regul[RAPIDE], 0)} % et {nombre_fr(regul[DIFFICULTE], 0)} % des mois dans leur type d'usage) : ces clients changent plus souvent de façon de payer. **L'usage mixte** ({nombre_fr(regul[MIXTE], 0)} %) l'est par construction : il réunit des clients qui paient tantôt peu, tantôt tout.
""")

# ------------------------------------------------------------------------------
st.subheader("Le type d'usage et le taux de défaut", anchor="defaut-usage")
col_repartition, col_taux = st.columns(2)
with col_repartition:
    st.markdown("#### Répartition des clients")
    fig_types = px.pie(stats_type, names='type_usage', values='clients', color='type_usage', color_discrete_map=COULEURS_TYPES)
    fig_types.update_traces(sort=False, direction="clockwise", textposition="outside", automargin=True,  # marges élargies pour que les étiquettes ne soient pas coupées
                            text=[lib.replace(" : ", " :<br>") if " : " in lib else lib.replace(" ", "<br>", 1) for lib in stats_type["type_usage"].astype(str)],
                            texttemplate="%{text}<br>%{percent:.1%}", textfont_size=TAILLE_ETIQUETTE,
                            hovertemplate="%{label} : %{value} clients (%{percent:.1%})<extra></extra>")
    fig_types.update_layout(showlegend=False, height=420, separators=", ", margin=dict(t=40, b=40, l=80, r=80))
    st.plotly_chart(fig_types, width='stretch')

with col_taux:
    st.markdown("#### Taux de défaut")
    fig_taux = px.bar(stats_type, x='type_usage', y='taux', color='type_usage', color_discrete_map=COULEURS_TYPES,
                      labels={'type_usage': "Type d'usage", 'taux': 'Taux de défaut (%)'})
    # Taux de défaut moyen en pointillés orange ; valeurs dans de petites étiquettes, devant la ligne (comme en 4.1 et 4.2)
    fig_taux.add_hline(y=taux_moyen, line_dash="dash", line_width=2, line_color=COULEURS["orange"])
    for _, row in stats_type.iterrows():
        fig_taux.add_annotation(x=row['type_usage'], y=row['taux'], yshift=12, showarrow=False,
                                text=f"<b>{nombre_fr(row['taux'], 1)} %</b>", font_size=TAILLE_ETIQUETTE,
                                bgcolor="rgba(128, 128, 128, 0.25)", borderpad=2)
    # Ordonnée : 10 % de marge au-dessus de la plus haute colonne
    fig_taux.update_layout(showlegend=False, height=420, yaxis_range=[0, stats_type['taux'].max() * 1.1],
                           xaxis_tickangle=-30, xaxis_title=None)
    st.plotly_chart(fig_taux, width='stretch')

ligne = stats_type.set_index('type_usage')
part_credit = ligne.loc[[LENT, RAPIDE], 'part'].sum()
# Première facture : composition selon la vie du compte (FLAG_OUVERTURE, FLAG_DEGEL, page 4.4)
premiere = df['type_usage'] == PREMIERE
part_ouverture_premiere = (df.loc[premiere, 'FLAG_OUVERTURE'] == 1).mean() * 100
part_degel_premiere = (df.loc[premiere, 'FLAG_DEGEL'] == 1).mean() * 100
st.markdown(f"""
- **La carte est d'abord un crédit** : {nombre_fr(part_credit, 1)} % des clients remboursent d'habitude entre 3 et 15 % de leur facture, contre {nombre_fr(ligne.loc[COMPTANT, 'part'], 1)} % qui la règlent au comptant. À eux seuls, {nombre_fr(ligne.loc[LENT, 'part'], 1)} % des clients remboursent autour de la mensualité minimale : c'est le crédit lent.
- **Plus le client rembourse, moins il fait défaut** : le taux de défaut passe de **{nombre_fr(ligne.loc[RIEN, 'taux'], 1)} %** pour les clients qui ne paient rien et **{nombre_fr(ligne.loc[DIFFICULTE, 'taux'], 1)} %** pour les clients en difficulté, à **{nombre_fr(ligne.loc[LENT, 'taux'], 1)} %** pour le crédit lent et **{nombre_fr(ligne.loc[RAPIDE, 'taux'], 1)} %** pour le crédit rapide, puis **{nombre_fr(ligne.loc[MIXTE, 'taux'], 1)} %** pour l'usage mixte et **{nombre_fr(ligne.loc[COMPTANT, 'taux'], 1)} %** pour le paiement comptant (moyenne de {nombre_fr(taux_moyen, 1)} %, en pointillés orange).
- **Le taux de défaut de l'usage mixte est une moyenne de situations différentes** : un payeur au comptant qui a réglé une partie de sa facture un mois et un client qui rattrape un retard n'ont pas le même risque. Ses {nombre_fr(ligne.loc[MIXTE, 'clients'])} clients font en moyenne presque aussi peu défaut que les payeurs au comptant, mais ce chiffre ne décrit le risque d'aucun profil en particulier.
- **Ne rien payer est le signal le plus fort**, mais il concerne peu de clients ({nombre_fr(ligne.loc[RIEN, 'clients'])}).
- **{PREMIERE} : un petit groupe, pas forcément de nouveaux clients, au risque proche de la moyenne.** Ses {nombre_fr(ligne.loc[PREMIERE, 'clients'])} clients ({nombre_fr(ligne.loc[PREMIERE, 'part'], 1)} % du total) n'ont eu leur première facture due qu'en septembre : leur façon de payer n'est pas encore connue. {nombre_fr(part_ouverture_premiere, 0)} % sont des ouvertures de compte, {nombre_fr(part_degel_premiere, 0)} % d'anciens comptes qui se réveillent, et les autres d'anciens comptes actifs, avec un avoir et sans facture due (page « 4.4 La vie des comptes ») ; les ouvertures elles-mêmes peuvent cacher d'anciens comptes restés à 0. Leur taux de défaut ({nombre_fr(ligne.loc[PREMIERE, 'taux'], 1)} %) est proche de la moyenne ({nombre_fr(taux_moyen, 1)} %) : l'arrivée d'une première facture n'est pas, en soi, un signal de risque.
""")

# ------------------------------------------------------------------------------
st.subheader("Le type d'usage et les codifications de la banque", anchor="usage-codifications")
st.markdown("""
La page « 3.3 Les codifications » a donné un sens aux codifications à partir des paiements de chaque mois. On vérifie ici ce sens client par client : pour chaque type d'usage, quelle codification la banque pose-t-elle le plus souvent ? Pour chaque client, on retient sa **codification la plus fréquente** sur les 6 mois, qu'une facture soit due ou non. Une codification est une étiquette, pas une quantité : on ne calcule pas sa médiane. Comme les types d'usage ne reposent que sur les paiements, ce croisement est une **vérification indépendante** : si les types ont un sens, la banque doit les codifier différemment.
""")

# Codification la plus fréquente : colonne PAY_habituel lue dans le CSV (créée par 05_03_EDA_storytelling, définie dans
# docs/colonnes_creees.md : PAY_1 à PAY_6, retards regroupés en 2, égalité tranchée par le mois le plus récent)
ORDRE_CODIF = ["-2", "-1", "0", "1", "2 et plus"]
df['codif_habituelle'] = df['PAY_habituel'].map({-2: "-2", -1: "-1", 0: "0", 1: "1", 2: "2 et plus"})
parts_codif = (pd.crosstab(df['type_usage'], df['codif_habituelle'], normalize='index') * 100)
parts_codif = parts_codif.reindex(index=NOMS_AFFICHES, columns=ORDRE_CODIF, fill_value=0)

fig_codif = go.Figure()
for valeur_codif in ORDRE_CODIF:
    fig_codif.add_trace(go.Bar(
        y=parts_codif.index, x=parts_codif[valeur_codif], name=valeur_codif, orientation='h',
        marker_color=COULEURS_CODIF[valeur_codif],
        text=[f"{nombre_fr(v, 0)} %" if v >= 5 else "" for v in parts_codif[valeur_codif]], textposition="inside", textfont_size=TAILLE_ETIQUETTE,
        hovertemplate="%{y}<br>Codification habituelle " + valeur_codif + " : %{x:.1f} % des clients<extra></extra>",
    ))
# Nombre de clients au bout de chaque barre, pour montrer le poids de chaque type d'usage
clients_type = stats_type.set_index('type_usage')['clients']
for type_usage in parts_codif.index:
    fig_codif.add_annotation(x=101, y=type_usage, xanchor="left", showarrow=False,
                             text=f"<b>{nombre_fr(clients_type[type_usage])} clients</b>", font_size=TAILLE_ETIQUETTE)
fig_codif.update_layout(barmode="stack", height=520, xaxis_title="Part des clients (%)",
                        xaxis=dict(range=[0, 125], tickvals=[0, 20, 40, 60, 80, 100]),
                        yaxis=dict(autorange="reversed", title=None), legend_title="Codification la plus fréquente",
                        # entrywidth : espace après chaque libellé, pour que chaque carré reste collé à sa signification
                        legend=dict(orientation="h", y=1.12, itemwidth=30, entrywidth=90),
                        margin=dict(t=60), separators=", ", font_size=14)
st.plotly_chart(fig_codif, width='stretch')
st.caption("Codification la plus fréquente de chaque client de PAY_1 à PAY_6, qu'une facture soit due ou non ; en cas d'égalité, la plus récente des codifications à égalité.")

pc = parts_codif
st.markdown(f"""
Les codifications suivent de près le type d'usage, et confirment la lecture de la page 3.3 :
- **les clients au comptant sont habituellement codifiés {codif('-1')} ou {codif('-2')}** pour {nombre_fr(pc.loc[COMPTANT, ['-2', '-1']].sum(), 0)} % d'entre eux : ni l'un ni l'autre n'utilise le crédit. {codif('-1')} désigne une facture payée à temps ; {codif('-2')} un crédit non utilisé, que le client ait tout payé ou n'ait rien eu à payer, d'où sa présence sur les comptes peu actifs (la codification la plus fréquente porte ici sur les 6 mois, y compris les mois sans facture) ;
- **les clients à crédit sont habituellement codifiés {codif('0')}** : {nombre_fr(pc.loc[LENT, '0'], 0)} % des clients pour le crédit lent, {nombre_fr(pc.loc[RAPIDE, '0'], 0)} % pour le crédit rapide. Le {codif('0')} est bien le crédit renouvelable en cours ;
- **l'usage mixte est surtout vu en crédit par la banque** : {nombre_fr(pc.loc[MIXTE, '0'], 0)} % de ses clients sont habituellement codifiés {codif('0')}, ce qui va avec les remboursements anticipés et les rattrapages, et {nombre_fr(pc.loc[MIXTE, ['-2', '-1']].sum(), 0)} % {codif('-1')} ou {codif('-2')}, des payeurs au comptant qui ont payé en partie certains mois ;
- **les clients qui ne paient rien sont habituellement codifiés en retard ({codif('2 et plus')})** pour {nombre_fr(pc.loc[RIEN, '2 et plus'], 0)} % d'entre eux, et les clients en difficulté mêlent crédit ({codif('0')}) et retards ({nombre_fr(pc.loc[DIFFICULTE, '2 et plus'], 0)} %) ;
- **le groupe « {PREMIERE} » est habituellement codifié {codif('-2')}** pour {nombre_fr(pc.loc[PREMIERE, '-2'], 1)} % de ses clients : c'est cohérent avec l'absence d'encours avant septembre, le crédit n'ayant pas été utilisé.

**Ces rapprochements portent sur des comportements habituels**, la médiane du ratio de paiement d'un côté et la codification la plus fréquente de l'autre, et non sur chaque mois : un même client peut payer au comptant un mois, à crédit le suivant, et recevoir des codifications différentes d'un mois à l'autre. Ils confirment les grandes lignes de la lecture de {codif('-2')}, {codif('-1')} et {codif('0')}, sans permettre de conclure sur le cas d'un client en particulier. La codification {codif('1')} et les codifications de retard demandent une étude à part : elles sont reprises avec les retards, en 4.6, puis avec la population contentieuse, en partie 5.
""")

st.markdown(f"""
**Un comportement médian, à lire avec prudence.** Chaque client est classé selon la médiane de ses ratios de paiement, c'est-à-dire son comportement le plus habituel, pas chacun de ses mois :
- **la médiane gomme les mois qui sortent de l'habitude** : un client qui ne paie rien trois mois et solde sa facture les deux autres a une médiane de 0 %, et se retrouve parmi ceux qui ne paient rien ;
- **elle repose parfois sur peu de mois** : un compte récemment ouvert ou un compte qui s'endort n'a que deux mois avec une facture due, et sa médiane dépend alors de deux paiements. C'est le cas de {nombre_fr(peu_de_mois)} clients. Ceux qui n'en ont qu'un sont classés selon leur taux de remboursement global.

Ce classement sert donc à observer une **tendance** : elle est nette, mais ce n'est qu'une tendance, qui ne décrit pas chaque client mois par mois.
""")

st.info(f"""
**Ce que révèle le type d'usage** : chaque client a une façon habituelle d'utiliser sa carte, comme moyen de paiement ou comme crédit. Les usages sont bien tranchés aux extrémités, paiement comptant d'un côté, crédit lent de l'autre, avec entre les deux un crédit rapide qui rembourse un peu plus vite. L'usage mixte, lui, n'est pas un profil : il réunit des comportements variés (paiement partiel d'un payeur au comptant, remboursement anticipé, rattrapage d'un retard), et une partie des écarts vient aussi de la qualité des données (paiements enregistrés en décalé). Que le client tienne ou non son habitude, le risque ne trompe pas : le taux de défaut d'un client en crédit lent ({nombre_fr(ligne.loc[LENT, 'taux'], 1)} %) atteint {nombre_fr(ligne.loc[LENT, 'taux'] / ligne.loc[COMPTANT, 'taux'], 1)} fois celui d'un client au comptant ({nombre_fr(ligne.loc[COMPTANT, 'taux'], 1)} %). Les clients qui ne paient rien sont les plus risqués, mais minoritaires, et le dataset ne dit pas d'où vient leur situation. Ce comportement de remboursement, propre à chaque client, est une information à donner au futur modèle. Il éclaire aussi la codification de la banque : les codifications {codif('-2')} et {codif('0')}, absentes de la documentation officielle, et {codif('-1')} correspondent, dans les grandes lignes, à un usage habituel de la carte (paiement comptant pour {codif('-1')}, paiement comptant ou absence de dette pour {codif('-2')}, crédit renouvelable pour {codif('0')}), sans que cela vaille pour chaque mois de chaque client. La codification {codif('1')} et les retards restent, eux, à approfondir.
""")
