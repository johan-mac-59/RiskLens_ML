from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 5.5 : PEU DE CLIENTS, BEAUCOUP DE DÉFAUTS
# Bilan des deux populations sorties du machine learning et prédites en défaut (en incident à M ; retard imminent) :
# entraînement, test et données d'origine (05_02_EDA_incidents, sections 5 et 7).
# Population en incident : entraînement et test (lu une seule fois) ; retard imminent et les deux réunis : tout le périmètre.
# Calculs en direct ; les données d'origine (30 000 lignes)
# ne sont pas dans le dépôt : leurs résultats sont repris du notebook, source citée.
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/src"
DEUX = ["En incident", "Retard imminent"]

df, s12, train, test = donnees_partie_5()

# 05_02_EDA_incidents, section 7 : les deux populations sur les 30 000 lignes d'origine (codifications brutes, aucun filtre)
ORIGINE = {"clients": 30000, "retires": 3130, "vp": 2177, "fp": 953, "precision": 69.55, "captes": 32.81, "reste": 16.59}


def bilan(d, statuts):
    """Mesures d'une règle de retrait : les clients des statuts donnés sont tous prédits en défaut."""
    retire = d['STATUT'].isin(statuts)
    y = d['dpnm']
    return {
        "clients": len(d), "retires": int(retire.sum()), "part_clients": retire.mean() * 100,
        "vp": int(y[retire].sum()), "fp": int((y[retire] == 0).sum()), "precision": y[retire].mean() * 100,
        "captes": y[retire].sum() / y.sum() * 100, "reste": y[~retire].mean() * 100, "taux": y.mean() * 100,
    }


inc_train, inc_test = bilan(train, ["En incident"]), bilan(test, ["En incident"])
inc_glob, imm_glob, deux_glob = bilan(s12, ["En incident"]), bilan(s12, ["Retard imminent"]), bilan(s12, DEUX)

entete_partie_5(df, s12, train, test)

st.markdown("---")
st.header("5.5 Peu de clients, beaucoup de défauts : deux règles métier qui prédisent déjà près de la moitié des défauts", anchor="bilan")
st.markdown("""
Les deux populations sont définies, décrites et vérifiées sur l'entraînement. Elles servent à une décision simple : **les clients en incident et en retard imminent sont retirés du machine learning et prédits en défaut**, sans modèle. Cette page mesure ce que vaut cette décision, d'abord sur l'entraînement, puis sur des clients jamais vus.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Peu de clients, beaucoup de défauts", anchor="concentration")
groupes = [("En incident", inc_glob), ("Retard imminent", imm_glob), ("Les deux", deux_glob)]
fig_conc = go.Figure()
for nom, cle, couleur in (("Part des clients", "part_clients", COULEURS["gris"]), ("Part des défauts", "captes", STATUTS_CTX["En incident"])):
    valeurs = [b[cle] for _, b in groupes]
    fig_conc.add_trace(go.Bar(x=[g for g, _ in groupes], y=valeurs, name=nom, marker_color=couleur,
                              text=[f"{nombre_fr(v, 1)} %" for v in valeurs], textposition='outside',
                              textfont=dict(size=TAILLE_ETIQUETTE), hovertemplate="%{x}<br>" + nom + " : %{y:.1f} %<extra></extra>"))
fig_conc.update_layout(barmode='group', yaxis_title="Part du périmètre (%)", yaxis_range=[0, deux_glob['captes'] * 1.3],
                       height=400, separators=", ", legend=dict(orientation="h", y=1.12), margin=dict(t=50))
col_g, col_t = st.columns([3, 2])
with col_g:
    st.plotly_chart(fig_conc, width='stretch')
with col_t:
    st.markdown(f"""
- **Les clients en incident ne représentent que {nombre_fr(inc_glob['part_clients'], 1)} % du périmètre, mais {nombre_fr(inc_glob['captes'], 1)} % de ses défauts**, avec {nombre_fr(inc_glob['precision'], 1)} % de prédictions justes.
- **Le retard imminent ajoute {nombre_fr(imm_glob['part_clients'], 1)} % des clients et {nombre_fr(imm_glob['captes'], 1)} % des défauts**, avec {nombre_fr(imm_glob['precision'], 1)} % de prédictions justes.
- **Ensemble, {nombre_fr(deux_glob['part_clients'], 1)} % des clients portent {nombre_fr(deux_glob['captes'], 1)} % des défauts** : le risque est extrêmement concentré.
""")
st.caption(f"Tout le périmètre ({nombre_fr(len(s12))} clients). Le taux de défaut est mesuré, jamais utilisé pour régler une règle.")

# ------------------------------------------------------------------------------
st.subheader("2. Des résultats stables sur des clients jamais vus", anchor="stabilite")
st.markdown(f"""
Le jeu de **test** a été mis de côté dès le début de l'étude. Il n'a été utilisé **qu'une seule fois**, pour la population en incident, une fois sa règle figée, et rien n'a été ajusté ensuite ([05_02_EDA_incidents.ipynb]({GH}/05_02_EDA_incidents.ipynb), section 5).

Les deux règles ont aussi été appliquées aux **30 000 clients des données d'origine**, sans aucun nettoyage ni filtre (section 7). Ce n'est pas un test indépendant, puisque ces données contiennent l'entraînement, mais cela montre ce que donnent les règles sur le fichier tel que la banque l'a fourni.
""")


# Colonnes mises en valeur (les deux populations réunies) : fond bordeaux léger, pour les comparer d'un coup d'œil
FOND_DEUX = "background: rgba(136, 34, 85, 0.15);"


def colonne(b, style=""):
    cellules = [nombre_fr(b["clients"]), nombre_fr(b["retires"]), nombre_fr(b["vp"]), nombre_fr(b["fp"]),
                f"<b>{nombre_fr(b['precision'], 1)} %</b>", f"<b>{nombre_fr(b['captes'], 1)} %</b>", f"{nombre_fr(b['reste'], 1)} %"]
    return [(c, style) for c in cellules]


INDICATEURS = [
    "Clients du jeu", "Clients retirés (prédits en défaut)", "dont en défaut (prédictions justes)", "dont sans défaut (fausses alertes)",
    "<b>Précision</b> : part des clients retirés qui font défaut", "<b>Part des défauts du jeu captés</b>",
    "Taux de défaut des clients restants, laissés au machine learning",
]
valeurs = [colonne(inc_train), colonne(inc_test), colonne(imm_glob), colonne(deux_glob, FOND_DEUX), colonne(ORIGINE, FOND_DEUX)]
st.caption("Comment lire : une colonne par jeu de données et par population. Les deux lignes en gras sont celles qui comptent : la précision dit si la règle se trompe, la part des défauts captés dit quel poids elle a.")
tableau_html(["", "En incident, entraînement", "En incident, test", "Retard imminent", (f"<b>En incident + retard imminent</b> ({nombre_fr(len(s12))} clients)", FOND_DEUX),
              ("<b>En incident + retard imminent, données d'origine</b> (30 000 clients)", FOND_DEUX)],
             [[ind] + [v[i] for v in valeurs] for i, ind in enumerate(INDICATEURS)], largeurs=[28, 14, 14, 14, 15, 15])
st.caption("Calculés en direct, sauf les données d'origine. Retard imminent et colonne des deux populations : tout le périmètre. Données d'origine : résultats de l'étude, repris tels quels (section 7), ces données n'étant pas dans le dépôt. Sur les clients retirés, les règles prédisent tout le monde en défaut : toutes leurs erreurs sont des fausses alertes, et le rappel y vaut 100 % par construction ; il n'a donc pas de sens ici.")
st.markdown(f"""
- **La population en incident est stable sur des clients jamais vus** : {nombre_fr(inc_train['precision'], 1)} % de prédictions justes sur l'entraînement, {nombre_fr(inc_test['precision'], 1)} % sur le test, et {nombre_fr(inc_train['captes'], 1)} % contre {nombre_fr(inc_test['captes'], 1)} % des défauts captés.
- **Les deux populations réunies** : {nombre_fr(deux_glob['precision'], 1)} % de prédictions justes et {nombre_fr(deux_glob['captes'], 1)} % des défauts captés sur le périmètre. **Sur les données d'origine**, elles restent précises ({nombre_fr(ORIGINE['precision'], 1)} %) et captent {nombre_fr(ORIGINE['captes'], 1)} % des défauts : une part plus faible, car ce fichier contient aussi des clients sans dette en septembre, hors du périmètre étudié.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Le revers : des fausses alertes, et une cible imparfaite", anchor="limites")
figes = (train[[f'PAY_{i}' for i in range(1, 7)]] == 2).all(axis=1)
sains_figes = (train.loc[figes, 'dpnm'] == 0).mean() * 100
st.markdown(f"""
- **Environ {nombre_fr(100 - deux_glob['precision'], 0)} clients sur 100 retirés ne font pas défaut** ({nombre_fr(deux_glob['fp'])} sur le périmètre). C'est la contrepartie assumée de règles simples : un client qui s'en sort quand même sera traité comme un client à risque. Pour une banque, ce coût est celui d'une surveillance renforcée, à comparer au coût d'un défaut non anticipé.
- **La cible elle-même n'est pas parfaite.** La façon dont le défaut d'octobre a été noté n'est pas documentée, et ce n'est pas le simple prolongement de la codification : parmi les {nombre_fr(int(figes.sum()))} clients de l'entraînement codifiés {codif('2')} sur les 6 mois, {nombre_fr(sains_figes)} % sont notés sans défaut, alors que leur codification ne bouge jamais. Même le retard imminent, défaut d'octobre déjà codifié par la banque, ne coïncide pas avec la cible : {nombre_fr(100 - imm_glob['precision'], 0)} % de ces clients sont notés sans défaut.
- Les règles prédisent donc le défaut **tel que la banque l'a noté en octobre 2005**, pas forcément un impayé définitif.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Ce que cela change pour la suite", anchor="suite")
# Tout le périmètre : les règles sont figées, la population restante est simplement décrite
b_perimetre = deux_glob
restants = len(s12) - b_perimetre['retires']
st.markdown(f"""
Le machine learning reçoit **le dataset nettoyé, dont on retire les clients en incident et en retard imminent** : les codifications nettoyées, les montants et les colonnes créées, pour tous les autres clients. Sur le périmètre, il reste **{nombre_fr(restants)} clients à départager**, avec un taux de défaut de **{nombre_fr(b_perimetre['reste'], 1)} %**, contre {nombre_fr(b_perimetre['taux'], 1)} % avant le retrait. Cette population est plus homogène, mais aussi plus difficile : les défauts les plus visibles sont déjà traités, et il reste au modèle les **{nombre_fr(100 - b_perimetre['captes'])} % de défauts** que les règles ne captent pas. L'historique des retards de ces clients ne disparaît pas pour autant : il est résumé par les colonnes créées (page 5.2).

C'est la **première moitié de la réponse à la problématique** : sans aucun machine learning, deux règles métier explicables, fondées sur les codifications de la banque, prédisent déjà {nombre_fr(b_perimetre['captes'])} % des défauts, avec environ {nombre_fr(b_perimetre['precision'] / 10)} prédictions justes sur 10. La seconde moitié revient au modèle, sur les autres clients (partie 6).
""")

st.info(f"""
**Ce qu'il faut retenir de la partie 5** : partie de clients figés en retard au taux de défaut anormalement élevé, l'étude a défini la **population en incident** par une règle métier, deux codifications de retard d'affilée ou une seule de {codif('3')} ou plus, et mis à part le **retard imminent**, défaut d'octobre déjà codifié par la banque. Sans regarder le défaut, ces règles isolent un comportement de paiement dégradé ; avec le défaut, elles se révèlent très efficaces : {nombre_fr(b_perimetre['part_clients'])} % des clients, {nombre_fr(b_perimetre['captes'])} % des défauts, et {nombre_fr(b_perimetre['precision'] / 10)} prédictions justes sur 10, stables sur des clients jamais vus pour la population en incident. Le machine learning peut maintenant se concentrer sur le reste.
""")
