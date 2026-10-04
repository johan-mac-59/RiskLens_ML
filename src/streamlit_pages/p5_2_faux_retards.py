from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 5.2 : CHERCHER LE CONTENTIEUX RÉVÈLE DE FAUX RETARDS
# Ordre du raisonnement : postulat (un retard = codification 2 ou plus) → anomalies (retards posés sur une facture
# nulle : comptes (ré)activés et faux 2 ; septembre en suspens) → ce que fait la banque quand elle sort un client
# du retard → corrections décidées (banque + logique métier), inscrites au niveau 5 du nettoyage.
# La vérification des codifications 1 et le contrôle du niveau 5 sont en page 5.3, après la définition des règles.
# Sources : 05_02_EDA_contentieux (sections 3.1 à 3.3 et 6.1), 05_04_EDA_codification1 (sections 5 à 7).
# Calculé en direct sur le CSV (codifications corrigées, indicateurs du niveau 5) : profils des comptes concernés,
# sorties de retard, taux de défaut (entraînement uniquement). Les codifications d'origine ne sont ni dans le CSV
# ni dans le dépôt : les chiffres « avant correction » sont repris des notebooks, source citée (décision D19).
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/src"

df, s12, train, test = donnees_partie_5()
taux_train = train['dpnm'].mean() * 100

# Résultats repris des notebooks (codifications d'origine, absentes du CSV)
# 05_02_EDA_contentieux, cellules 8 et 9 : entrées en retard observées sur le train (cleaned3, codifications d'origine)
NB_ENTREES, NB_FAUX_2, NB_FAUX_2_PAR_DEUX, PART_INACTIFS_AVANT = 4850, 151, 148, 70.9
# 05_04_EDA_codification1, cellule 42 (et audit) : codifications 1 de septembre dans les données d'origine
NB_CODIF_1_ORIGINE = 3688
# 05_04_EDA_codification1, cellule 31 : ancienne correction (tous les 1 après un retard remis à 2), simulée sur le train
ANCIEN_AJOUTES, ANCIEN_TAUX_AJOUTES, ANCIEN_TAUX_CTX_AVANT, ANCIEN_TAUX_CTX_APRES = 1349, 42.3, 70.3, 60.2
# 05_04_EDA_codification1, cellules 36, 39 et 42 : contrôle de cleaned5 (cleaned4 avant, cleaned5 après)
CTRL_FAUX_RETARDS, CTRL_REMIS_A_2, CTRL_SOLDES = 224, 118, 5
CTRL_REMIS_DEPUIS_1, CTRL_REMIS_DEPUIS_SAIN = 73, 45
CTRL_CODIFS_MODIFIEES, CTRL_CLIENTS_MODIFIES, CTRL_RETARDS_NEUTRALISES = 566, 346, 442

# Exemples types (construits d'après les séquences observées dans l'étude, pas des clients réels).
# Colonnes : mois de la codification, d'avril (M-6) à septembre (M-1). La facture à payer un mois donné est la dette
# de la fin du mois précédent (BILL_AMT(n+1)) : c'est elle que juge la codification du mois (PAY_n)
ENTETES_MOIS = [""] + [f"M-{n}<br>{nom.lower()}" for n, nom in MOIS_CHRONO]
REACTIVE, FAUX_2 = "Compte (ré)activé", "Faux 2"
EXEMPLES = {
    REACTIVE: {"titre": "Compte (ré)activé : il se ressert de sa carte en juillet",
               "facture": ["?", "0", "0", "0", "2 500", "2 600"], "paiement": ["0", "0", "0", "0", "500", "500"],
               "banque": (-2, -2, 2, 2, 0, 0), "corrigee": (-2, -2, -2, -2, 0, 0)},
    FAUX_2: {"titre": "Faux 2 : le client vient de tout rembourser en juin",
             "facture": ["?", "15 000", "12 000", "0", "0", "0"], "paiement": ["3 000", "3 000", "12 000", "0", "0", "0"],
             "banque": (0, 0, -1, 2, 2, -2), "corrigee": (0, 0, -1, -1, -1, -2)},
}


def exemples(avec_correction):
    """Les deux exemples côte à côte, un client par colonne, avec ou sans la ligne corrigée."""
    for colonne, ex in zip(st.columns(2), EXEMPLES.values()):
        with colonne:
            st.markdown(f"**{ex['titre']}**")
            lignes = [["Facture à payer ce mois-là (NT$)"] + ex["facture"],
                      ["Paiement fait ce mois-là (NT$)"] + ex["paiement"],
                      ["Codification de la banque"] + [cellule_codif(v) for v in ex["banque"]]]
            if avec_correction:
                lignes.append(["<b>Codification corrigée</b>"] + [cellule_codif(v) for v in ex["corrigee"]])
            tableau_html(ENTETES_MOIS, lignes, largeurs=[28] + [12] * 6)


entete_partie_5(df, s12, train, test)

st.markdown("---")
st.header("5.2 Chercher le contentieux révèle de faux retards, corrigés au nettoyage", anchor="faux-retards")
st.markdown("""
Pour définir le contentieux, l'étude part d'un postulat simple. En le confrontant aux montants, deux anomalies sont apparues avant même que la définition soit fixée. Cette page suit ce cheminement : le postulat, les anomalies, ce que fait la banque elle-même, puis les corrections décidées et leur contrôle.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Le point de départ : un retard, c'est une codification 2 ou plus", anchor="postulat")
st.markdown(f"""
La documentation du dataset présente {codif('1')} comme un retard d'un mois, {codif('2')} comme un retard de deux mois, et ainsi de suite. Mais la codification {codif('1')} n'existe presque qu'en septembre et reste un statut provisoire (page « 3.3 Les codifications »). L'étude retient donc comme **retard** une codification de {codif('2')} ou plus.

Une codification {codif('2')} signifie au moins deux échéances non réglées, soit **au minimum 60 jours de retard de paiement**. Dans la pratique bancaire actuelle, en France, un client à ce stade passe **en recouvrement**, puis **au contentieux** si sa situation ne revient pas à la normale ; sa carte est en principe bloquée avant. Les règles de la banque taïwanaise de 2005 ne sont pas connues : cette logique métier est retenue par analogie, et c'est sur elle que repose le seuil de deux codifications de retard d'affilée, soit au moins 90 jours (page 5.3).

C'est le postulat de départ : un client **entre** en retard quand sa codification passe à {codif('2')} ou plus, et la population contentieuse se cherche parmi ces retards, à commencer par les clients figés à {codif('2')} (page 5.1). Mais la codification ne suit pas toujours la dette (page « 3.3 Les codifications ») : chaque entrée en retard a donc été confrontée aux montants, une à une, sur le jeu d'entraînement.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Une anomalie : des retards posés sur une facture nulle", anchor="retards-sans-facture")
st.markdown(f"""
Sur les {nombre_fr(NB_ENTREES)} entrées en retard observées dans le jeu d'entraînement, **{NB_FAUX_2} sont posées alors que la facture à payer ce mois-là est nulle** : le client ne pouvait pas être en retard sur une somme qu'il ne devait pas. Ces retards ont un point commun frappant : **{NB_FAUX_2_PAR_DEUX} sur {NB_FAUX_2} arrivent par deux**, deux mois de suite codifiés {codif('2')} sans aucune facture à payer. {nombre_fr(PART_INACTIFS_AVANT, 1)} % concernent des comptes qui n'avaient eu aucune activité auparavant ([05_02_EDA_contentieux.ipynb]({GH}/05_02_EDA_contentieux.ipynb), cellules 8 et 9, codifications d'origine).

Une erreur de saisie se répartirait au hasard. Un schéma aussi régulier évoque plutôt **une procédure de la banque**. Ce que le client a fait le mois qui précède le premier retard distingue deux situations :
""")
tableau_html(["Situation", "Le mois qui précède le premier retard", "Lecture"], [
    [f"<b>{REACTIVE}</b>", "Aucune facture à payer et aucun paiement : le compte dormait, et il se remet à servir",
     "Une <b>mise sous surveillance</b> d'un compte qui reprend du service, pas une dette impayée"],
    [f"<b>{FAUX_2}</b>", "Une facture à payer ou un paiement : le plus souvent, le client vient de tout rembourser",
     "Le client ne peut pas être en retard sur une facture qui n'existe pas"],
], largeurs=[18, 41, 41])

st.markdown("##### Deux exemples types")
exemples(avec_correction=False)
st.caption("Exemples construits d'après les séquences les plus fréquentes de l'étude, pas des clients réels. Comment lire : la facture à payer un mois donné est la dette laissée à la fin du mois précédent, et c'est elle que juge la codification du mois (page « 1. Les données », section 1.2). « ? » : la dette de fin mars n'est pas dans les données. Dans les deux exemples, la banque pose un retard (2) deux mois de suite alors que la facture à payer est nulle. Le compte (ré)activé n'a rien à payer jusqu'en juillet : le client se ressert alors de sa carte, la dette apparaît à la fin du mois, devient la facture d'août, et il commence à la rembourser. Pourtant, la banque l'a déjà codifié en retard en juin et en juillet. Le second client, lui, venait de rembourser toute sa dette en juin.")

# Profil des comptes concernés : périmètre complet (sans le défaut), taux de défaut sur l'entraînement.
# Les clients sont repérés par les colonnes créées au nettoyage (SURVEILLANCE_RECENTE, FAUX_CODAGE)
reactive, faux_2 = s12['SURVEILLANCE_RECENTE'] == 1, s12['FAUX_CODAGE'] == 1
groupes = {"Comptes (ré)activés": reactive, "Faux 2": faux_2, "Autres clients du périmètre": ~reactive & ~faux_2}


def profil(masque):
    d = s12[masque]
    dt = train[masque.reindex(train.index)]
    return {
        "Clients (périmètre)": nombre_fr(len(d)),
        "Plafond médian (NT$)": nombre_fr(d['LIMIT_BAL'].median()),
        "Utilisation du plafond en septembre (médiane)": f"{nombre_fr(d['ratio_BILL_LIMIT1'].median(), 1)} %",
        "Dette de septembre (médiane, NT$)": nombre_fr(d['BILL_AMT1'].median()),
        "Mois sans aucun paiement, sur 6 (moyenne)": nombre_fr((d[[f'PAY_AMT{i}' for i in range(1, 7)]] == 0).sum(axis=1).mean(), 1),
        "Comptes ouverts pendant la période": f"{nombre_fr(d['FLAG_OUVERTURE'].mean() * 100)} %",
        "Taux de défaut (entraînement)": f"{nombre_fr(dt['dpnm'].mean() * 100, 1)} % ({nombre_fr(len(dt))} clients)",
    }


profils = {nom: profil(m) for nom, m in groupes.items()}
st.markdown("##### Qui sont ces comptes ?")
st.caption("Comment lire : une ligne par indicateur, une colonne par groupe de clients. Les profils portent sur tout le périmètre ; le taux de défaut, sur le seul jeu d'entraînement.")
tableau_html(["Indicateur"] + list(groupes), [[indicateur] + [profils[nom][indicateur] for nom in groupes] for indicateur in profils["Faux 2"]],
             largeurs=[34, 22, 22, 22])

p_react, p_faux, p_autres = (profils[nom] for nom in groupes)
taux_react = train.loc[train['SURVEILLANCE_RECENTE'] == 1, 'dpnm'].mean() * 100
taux_faux = train.loc[train['FAUX_CODAGE'] == 1, 'dpnm'].mean() * 100
st.markdown(f"""
- **Les comptes (ré)activés ont un profil à part** : un plafond confortable presque inutilisé ({p_react['Utilisation du plafond en septembre (médiane)']} en septembre, contre {p_autres['Utilisation du plafond en septembre (médiane)']} pour les autres clients), une petite dette, presque aucun paiement ({p_react['Mois sans aucun paiement, sur 6 (moyenne)']} mois sans paiement sur 6 en moyenne), et {p_react['Comptes ouverts pendant la période']} de comptes ouverts pendant la période (page « 4.4 La vie des comptes »). Ce sont bien des comptes qui se mettent à servir.
- **La surveillance de la banque n'était pas infondée** : {nombre_fr(taux_react, 1)} % de ces comptes font défaut, contre {nombre_fr(taux_train, 1)} % en moyenne sur l'entraînement. Mais un compte surveillé n'est pas un client en retard.
- **Les faux 2 ne signalent pas un client en difficulté** : ce sont des clients qui venaient de rembourser, et leur taux de défaut ({nombre_fr(taux_faux, 1)} %, sur {nombre_fr(int((train['FAUX_CODAGE'] == 1).sum()))} clients) reste voisin de la moyenne.
- Les effectifs sont faibles : ces taux donnent une tendance, pas une mesure précise.
""")

st.markdown("##### Ce qu'il faut en faire")
st.markdown(f"""
Ces codifications ne sont pas des retards : **elles doivent être corrigées**, sinon le contentieux compterait des retards fictifs. Reste à choisir par quelle codification les remplacer : c'est l'objet des sections suivantes.

La correction ne doit pas pour autant effacer ce que la banque a voulu signaler. **Deux colonnes sont créées** pour en garder la trace :
- `SURVEILLANCE_RECENTE` = 1 pour les comptes (ré)activés, dont la mise sous surveillance est un signal de risque ;
- `FAUX_CODAGE` = 1 pour les faux 2, par sécurité, comme indicateur à tester en machine learning.

**Une piste écartée** : un client **déjà en retard sur une vraie dette** qui la rembourse en totalité reste souvent codifié {codif('2')} quelque temps, alors qu'il ne doit plus rien : sa codification se retrouve elle aussi posée sur une facture nulle. Ces {codif('2')} ont été laissés tels quels. Maintenir un retard pendant un délai après le remboursement, avant de rouvrir la ligne de crédit, ressemble à une procédure normale de la banque. Seules les **entrées** en retard sur une facture nulle sont donc corrigées ; **un {codif('2')} qui prolonge un vrai retard n'est jamais modifié** ([05_02_EDA_contentieux.ipynb]({GH}/05_02_EDA_contentieux.ipynb), cellule 12).
""")

# ------------------------------------------------------------------------------
# Pourquoi la question ne se pose qu'en septembre : les sorties de retard sans paiement de juin, juillet et août
# sont-elles confirmées par la suite de l'historique ? (entraînement ; sortie au mois n, n = 4 à 2)
hist = []
for n in range(2, 5):
    sortie_n = (train[f'PAY_{n + 1}'] >= 2) & (train[f'PAY_{n}'] <= 0)
    sans_paiement = ((train[f'PAY_AMT{n + 1}'] == 0) & (train[f'PAY_AMT{n}'] == 0)
                     & (train[f'BILL_AMT{n + 2}'] > 0) & (train[f'BILL_AMT{n + 1}'] > 0))
    retombe = (train[[f'PAY_{k}' for k in range(1, n)]] >= 2).any(axis=1)
    for avec, m in ((False, sortie_n & sans_paiement), (True, sortie_n & ~sans_paiement)):
        hist.append({'avec_paiement': avec, 'n': int(m.sum()), 'retombe': int(retombe[m].sum()), 'defauts': int(train.loc[m, 'dpnm'].sum())})
hist = pd.DataFrame(hist).groupby('avec_paiement').sum()
hist['part_retombe'] = hist['retombe'] / hist['n'] * 100
hist['taux_defaut'] = hist['defauts'] / hist['n'] * 100
sans_p, avec_p = hist.loc[False], hist.loc[True]

st.subheader("3. Une autre sortie de retard en suspens : septembre", anchor="mois-transition")
st.markdown(f"""
Deuxième anomalie, dans l'autre sens. Ici, ce n'est pas un {codif('2')} qui pose question.

Des clients étaient en retard en août. En septembre, la banque ne les codifie plus en retard. Le plus souvent, elle leur donne la codification {codif('1')} : un **statut provisoire du dernier mois**, que l'historique n'a pas encore tranché (page « 3.3 Les codifications »). Plus rarement, elle leur donne directement {codif('-2')}, {codif('-1')} ou {codif('0')}, des codifications sans retard.

Deux questions se posent. Les paiements confirment-ils cette sortie du retard ? Et si oui, quelle codification leur donner ?

**Pourquoi la question ne se pose-t-elle qu'en septembre ?** La banque sort aussi des clients du retard les autres mois, parfois sans aucun paiement. Mais pour ces mois-là, la suite de l'historique a déjà tranché : les codifications des mois suivants disent si la sortie a tenu. Et elle tient dans les faits. Sur l'entraînement, la banque a sorti du retard {nombre_fr(sans_p['n'])} clients en juin, juillet ou août sans aucun paiement sur deux mois, alors que deux factures étaient dues, sur {nombre_fr(sans_p['n'] + avec_p['n'])} sorties de retard ces trois mois-là. Seuls {nombre_fr(sans_p['part_retombe'], 1)} % d'entre eux retombent en retard ensuite. La banque avait sans doute des raisons que le dataset ne montre pas (arrangement, plan de paiement, paiement enregistré ailleurs) : pour ces mois, sa codification peut être prise telle quelle.

**Une piste pour ces sorties de retard sans paiement : des accords de paiement.** Un échéancier ou un rééchelonnement négocié avec la banque expliquerait qu'un client sorte du retard avant tout versement, puis reste hors du retard les mois suivants. Ces clients font pourtant défaut à {nombre_fr(sans_p['taux_defaut'], 1)} % (entraînement), comme si une bonne partie des accords n'était pas tenue. Il ne s'agirait pas des dispositifs collectifs de la crise, qui arrivent après la période étudiée (décembre 2005 et février 2006, page 5.3), mais d'arrangements propres à la banque. Le dataset ne garde aucune trace de tels accords : c'est une hypothèse cohérente, pas un constat.

Septembre est différent. Le mois qui confirmerait la sortie, octobre, n'est pas dans les données. Et septembre porte un statut d'attente, la codification {codif('1')}, presque absente des autres mois.

L'enjeu est direct pour la suite. Septembre est le dernier mois connu : la définition du contentieux s'appuie sur lui pour décider de la situation d'un client à la fin de la période (page 5.3). Pour ces clients, il faut donc savoir s'ils sont **toujours en retard** ou **vraiment sortis du retard**.

Or la codification suit le paiement avec **un mois de décalage** (page « 3.3 Les codifications »). Ce que le client a payé en septembre ne se verrait que dans la codification d'octobre, qui n'est pas dans les données. L'idée est donc d'**anticiper cette codification d'octobre** à partir des paiements d'août et de septembre.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Ce que fait la banque quand elle sort un client du retard", anchor="banque")
# Sortie d'un retard : sur quelle codification le client revient-il ? (entraînement, sans le défaut)
# Sortie au mois n : PAY_(n+1) >= 2 puis PAY_n <= 0 ; codification d'avant = première codification < 2 qui précède la série
lignes = []
for n in range(1, 5):
    sortie = (train[f'PAY_{n + 1}'] >= 2) & (train[f'PAY_{n}'] <= 0)
    avant = pd.Series(np.nan, index=train.index)
    a_chercher = sortie.copy()
    for k in range(n + 2, 7):
        trouve = a_chercher & (train[f'PAY_{k}'] < 2)
        avant[trouve] = train.loc[trouve, f'PAY_{k}']
        a_chercher &= ~trouve
    # avant vide : la série de retards remonte jusqu'à avril, codification d'avant inconnue
    lignes.append(pd.DataFrame({'avant': avant[sortie].values, 'sortie': train.loc[sortie, f'PAY_{n}'].values}))
toutes_sorties = pd.concat(lignes, ignore_index=True)
sorties = toutes_sorties.dropna(subset=['avant']).astype({'avant': int})
sorties_inconnues = toutes_sorties[toutes_sorties['avant'].isna()]
nb_sorties_moins2 = int((toutes_sorties['sortie'] == -2).sum())
depuis_moins2 = sorties[sorties['avant'] == -2]['sortie'].value_counts()
sortie_inconnue_freq = sorties_inconnues['sortie'].value_counts(normalize=True) * 100
meme_codif = (sorties['avant'] == sorties['sortie']).mean() * 100
tab_sorties = pd.crosstab(sorties['avant'], sorties['sortie'], normalize='index') * 100
effectifs_avant = sorties['avant'].value_counts()

st.markdown(f"""
Pour choisir les codifications de remplacement, l'étude a d'abord regardé ce que fait la banque elle-même quand elle sort un client du retard, sur les mois où l'issue est connue. Sur les {nombre_fr(len(toutes_sorties))} sorties de retard du jeu d'entraînement, d'avril à septembre ([05_02_EDA_contentieux.ipynb]({GH}/05_02_EDA_contentieux.ipynb), cellule 31, recalculé ici) :
- **elle remet presque toujours le client sur la codification qu'il avait avant son retard** : {nombre_fr(meme_codif)} % des sorties dont on connaît cette codification (graphique ci-dessous) ;
- **elle ne le remet presque jamais à {codif('-2')}** ({nombre_fr(nb_sorties_moins2)} cas sur {nombre_fr(len(toutes_sorties))}) : les {nombre_fr(depuis_moins2.sum())} clients qui étaient à {codif('-2')} avant leur retard sont ressortis en {codif('-1')} ({nombre_fr(depuis_moins2.get(-1, 0))}) ou en {codif('0')} ({nombre_fr(depuis_moins2.get(0, 0))}) : un client qui vient de rembourser une dette n'est plus « sans consommation » ;
- **quand le retard dure depuis avril**, la codification d'avant n'est pas connue : la banque fait alors ressortir en {codif('0')} dans {nombre_fr(sortie_inconnue_freq.get(0, 0))} % des cas.
""")
st.markdown("##### En sortant d'un retard, le client revient sur sa codification d'avant")
fig_sortie = go.Figure()
for code in (-2, -1, 0):
    if code in tab_sorties.columns:
        valeurs = tab_sorties[code].reindex(tab_sorties.index, fill_value=0)
        fig_sortie.add_trace(go.Bar(
            y=[f"Avant le retard : {a}<br>({nombre_fr(effectifs_avant[a])} sorties)" for a in tab_sorties.index], x=valeurs,
            orientation='h', name=f"Sortie en {code}", marker_color=COULEURS_CODIF[str(code)],
            text=[f"{nombre_fr(v)} %" if v >= 8 else "" for v in valeurs], textposition='inside',
            textfont=dict(size=TAILLE_ETIQUETTE, color="white" if code in (-1, -2) else "black"),
            hovertemplate="%{y}<br>Sortie en " + str(code) + " : %{x:.1f} %<extra></extra>"))
# Légende sur une ligne au-dessus du graphique, ancrée par le bas pour ne pas mordre sur les barres ;
# sans titre de légende (le thème de Streamlit le place au-dessus des couleurs) : chaque couleur est nommée
fig_sortie.update_layout(barmode='stack', xaxis_title="Part des sorties de retard (%)", xaxis_range=[0, 100], height=360,
                         separators=", ", margin=dict(t=50),
                         legend=dict(orientation="h", x=0, xanchor="left", y=1.02, yanchor="bottom", traceorder="normal",
                                     title_text=""),
                         yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_sortie, width='stretch')
part_moins1 = tab_sorties.loc[-1, -1] if -1 in tab_sorties.index and -1 in tab_sorties.columns else 0
part_zero = tab_sorties.loc[0, 0] if 0 in tab_sorties.index and 0 in tab_sorties.columns else 0
st.caption(f"Comment lire : chaque barre regroupe les clients qui avaient la même codification juste avant leur retard ({codif('-2')}, {codif('-1')} ou {codif('0')}). Les couleurs montrent la codification que la banque leur a donnée en les sortant du retard. Exemple : parmi les clients à {codif('-1')} avant leur retard, {nombre_fr(part_moins1)} % ressortent en {codif('-1')}. Calcul sur le jeu d'entraînement, sans le défaut, sur les {nombre_fr(len(sorties))} sorties de retard dont on connaît la codification d'avant (les retards qui durent depuis avril sont exclus). Le groupe « avant : -2 » ne compte que {nombre_fr(effectifs_avant.get(-2, 0))} sorties.")
st.markdown(f"""
Un payeur au comptant ({codif('-1')}) redevient {codif('-1')} dans {nombre_fr(part_moins1)} % des cas, un client en crédit renouvelable ({codif('0')}) redevient {codif('0')} dans {nombre_fr(part_zero)} % des cas : **le retard ne change pas la façon dont le client utilise sa carte**, et la banque le remet là où il était.
""")

# ------------------------------------------------------------------------------
st.subheader("5. Les corrections décidées : le fonctionnement de la banque et la logique métier", anchor="corrections")
st.markdown("""
Les deux se complètent : la logique métier dit **quand** une codification de retard n'est pas crédible (pas de facture à payer, ou une facture soldée), et le fonctionnement de la banque dit **par quoi la remplacer** (la codification que le client avait avant son retard). Les corrections ne tranchent que les cas où les montants ne laissent aucun doute.
""")

st.markdown("##### Les retards posés sur une facture nulle")
st.markdown("Chaque retard posé sur une facture nulle, pour un compte (ré)activé comme pour un faux 2, est remplacé par **la dernière codification saine qui le précède** : la codification d'avant le retard, celle sur laquelle la banque remet elle-même un client qui sort d'un retard. Les retards posés ensuite sur une vraie dette ne sont jamais modifiés.")
exemples(avec_correction=True)
st.caption("Les mêmes exemples types qu'en section 2, avec la codification corrigée en dernière ligne.")

st.markdown("##### Le mois de septembre")
st.markdown(f"""
**Ce qui est corrigé** : seulement la codification de septembre (`PAY_1`), et seulement pour les clients en retard en août (`PAY_2` ≥ 2) qui ne le sont plus en septembre (`PAY_1` vaut {codif('1')}, {codif('-2')}, {codif('-1')} ou {codif('0')}). Toutes les autres codifications restent celles de la banque ; **un {codif('2')} n'est jamais modifié**.

La règle, écrite avec les colonnes du dataset (le paiement d'un mois règle la facture du mois précédent : `PAY_AMT1` règle `BILL_AMT2`) :
""")
st.code("""Si PAY_2 >= 2 et PAY_1 <= 1 :
    si PAY_AMT2 = 0 et PAY_AMT1 = 0, alors que BILL_AMT3 > 0 et BILL_AMT2 > 0   ->  PAY_1 = 2
    sinon, si PAY_AMT1 >= 90 % de BILL_AMT2                                      ->  PAY_1 = codification d'avant le retard
    sinon                                                                         ->  PAY_1 inchangé""", language=None)
tableau_html(["Ce que montrent les paiements", "Nouvelle codification de septembre", "Pourquoi"], [
    ["Aucun paiement ni en août ni en septembre, alors que deux factures étaient à payer",
     f"{codif('2')} : le client reste en retard",
     "Deux factures sont restées impayées : rien ne confirme la sortie du retard."],
    ["La facture à payer en septembre est réglée à 90 % ou plus",
     "La codification que le client avait <b>avant</b> son retard, c'est-à-dire la dernière codification saine qui précède la série de retards",
     "La facture est soldée : le client est sorti du retard (le seuil de 90 % correspond au paiement total, page « 3.3 Les codifications »). On lui donne la codification que la banque donne elle-même à un client qui sort d'un retard (section 4) : sa codification d'avant, " + codif('-1') + " s'il était à " + codif('-2') + ", " + codif('0') + " si son retard dure depuis avril."],
    ["Tous les autres cas", "Inchangée, le plus souvent " + codif('1'),
     "Un paiement partiel existe, mais rien ne permet de dire si le client sortira du retard ou y restera : la vraie situation est <b>indécidable</b>."],
], largeurs=[28, 30, 42])
st.markdown(f"Une première version de cette règle remettait d'office {codif('-2')} pour une facture soldée, et {codif('-1')} dès 10 % de paiement. L'observation de la banque l'a fait réviser : la banque ne fait presque jamais sortir en {codif('-2')}, et aucune frontière n'apparaît à 10 % (page « 3.3 Les codifications »).")

st.markdown(f"""
Ces corrections ont ensuite été inscrites dans le nettoyage, au **niveau 5** ([02_01_nettoyage.ipynb]({GH}/02_01_nettoyage.ipynb)) : les codifications corrigées remplacent celles de la banque dans les `PAY_n`, et les colonnes `SURVEILLANCE_RECENTE` et `FAUX_CODAGE` sont ajoutées. Aucun client n'est retiré. Leur vérification vient une fois les règles du contentieux posées (page 5.3).
""")

st.info(f"""
**Ce qu'il faut retenir** : en cherchant le contentieux à partir du postulat qu'un retard est une codification {codif('2')} ou plus, deux anomalies sont apparues, qui posent les bases des règles :
- **des retards posés sur une facture nulle**, en deux situations : les **comptes (ré)activés**, mis sous surveillance par la banque, et les **faux 2**, posés chez des clients qui venaient de tout rembourser. Ce ne sont pas des retards : ils sont corrigés, et deux colonnes en gardent la trace ;
- **septembre, une sortie de retard en suspens** : pour les autres mois, la suite de l'historique confirme les sorties décidées par la banque ; pour septembre, le mois qui les confirmerait manque, et la codification {codif('1')} signale une situation non tranchée. Seuls les cas où les paiements ne laissent aucun doute sont corrigés.

Dans les deux cas, la correction reprend ce que fait la banque elle-même : remettre le client sur sa codification d'avant le retard. **Un {codif('2')} posé sur une vraie dette n'est jamais modifié.** Sur ces codifications corrigées, la définition du contentieux peut être posée (page « 5.3 La définition du contentieux »).
""")
