from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 5.6 : PEU DE CLIENTS, BEAUCOUP DE DÉFAUTS
# Bilan de la règle de retrait (clients au contentieux, prédits en défaut) : entraînement, test (utilisé une seule
# fois dans l'étude, règle figée) et données d'origine (05_02_EDA_contentieux, sections 7, 9 et 9.1).
# Entraînement et test recalculés en direct ; les données d'origine (30 000 lignes) ne sont pas dans le dépôt :
# leurs résultats sont repris du notebook, source citée (décision D19).
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/src"

df, s12, train, test = donnees_partie_5()

# 05_02_EDA_contentieux, cellules 41 et 45 : règle appliquée aux 30 000 lignes d'origine (codifications brutes, aucun filtre)
ORIGINE = {"clients": 30000, "ctx": 3013, "vp": 2124, "fp": 889, "precision": 70.49, "captes": 32.01, "reste": 16.72}


def bilan(d):
    """Mesures de la règle : les clients au contentieux sont tous prédits en défaut."""
    ctx = d['STATUT'] == "Au contentieux"
    y = d['dpnm']
    return {
        "clients": len(d), "ctx": int(ctx.sum()), "part_clients": ctx.mean() * 100,
        "vp": int(y[ctx].sum()), "fp": int((y[ctx] == 0).sum()), "precision": y[ctx].mean() * 100,
        "captes": y[ctx].sum() / y.sum() * 100, "reste": y[~ctx].mean() * 100, "taux": y.mean() * 100,
    }


b_train, b_test = bilan(train), bilan(test)

entete_partie_5(df, s12, train, test)

st.markdown("---")
st.header("5.6 Peu de clients, beaucoup de défauts : une règle métier qui prédit déjà un tiers des défauts", anchor="bilan")
st.markdown("""
La règle est maintenant définie, décrite et vérifiée sur l'entraînement. Elle sert à une décision simple : **les clients au contentieux sont retirés du machine learning et prédits en défaut**, sans modèle. Cette page mesure ce que vaut cette décision, d'abord sur l'entraînement, puis sur des clients que la règle n'a jamais vus.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Un client sur dix, un tiers des défauts", anchor="concentration")
jeux = ["Entraînement", "Test"]
bilans = [b_train, b_test]
fig_conc = go.Figure()
for nom, cle, couleur in (("Part des clients du jeu", "part_clients", COULEURS["gris"]), ("Part des défauts du jeu", "captes", STATUTS_CTX["Au contentieux"])):
    valeurs = [b[cle] for b in bilans]
    fig_conc.add_trace(go.Bar(x=jeux, y=valeurs, name=nom, marker_color=couleur,
                              text=[f"{nombre_fr(v, 1)} %" for v in valeurs], textposition='outside',
                              textfont=dict(size=TAILLE_ETIQUETTE), hovertemplate="%{x}<br>" + nom + " : %{y:.1f} %<extra></extra>"))
fig_conc.update_layout(barmode='group', yaxis_title="Part captée par les clients au contentieux (%)", yaxis_range=[0, max(b['captes'] for b in bilans) * 1.3],
                       height=400, separators=", ", legend=dict(orientation="h", y=1.12), margin=dict(t=50))
col_g, col_t = st.columns([3, 2])
with col_g:
    st.plotly_chart(fig_conc, width='stretch')
with col_t:
    st.markdown(f"""
- **Les clients au contentieux ne représentent que {nombre_fr(b_train['part_clients'], 1)} % de l'entraînement, mais {nombre_fr(b_train['captes'], 1)} % de ses défauts.** Le risque est extrêmement concentré.
- **Sur ces clients, la règle se trompe peu** : {nombre_fr(b_train['precision'], 1)} % d'entre eux font défaut. Autrement dit, sur 10 clients que la règle prédit en défaut, environ {nombre_fr(b_train['precision'] / 10)} le sont vraiment.
- **Le résultat est le même sur le test** : {nombre_fr(b_test['part_clients'], 1)} % des clients, {nombre_fr(b_test['captes'], 1)} % des défauts, {nombre_fr(b_test['precision'], 1)} % de prédictions justes.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Une règle stable sur des clients qu'elle n'a jamais vus", anchor="stabilite")
st.markdown(f"""
Le jeu de **test** a été mis de côté dès le début de l'étude. Il n'a été utilisé **qu'une seule fois**, une fois la règle figée, et rien n'a été ajusté ensuite ([05_02_EDA_contentieux.ipynb]({GH}/05_02_EDA_contentieux.ipynb), section 7). C'est ce qui garantit que la règle n'a pas été taillée sur mesure pour les clients étudiés. Cette page ne fait qu'en afficher le résultat.

La règle a aussi été appliquée aux **30 000 clients des données d'origine**, sans aucun nettoyage ni filtre (section 9). Ce n'est pas un test indépendant, puisque ces données contiennent l'entraînement, mais cela montre ce que donne la règle sur le fichier tel que la banque l'a fourni.
""")


def colonne(b, origine=False):
    return [nombre_fr(b["clients"]), nombre_fr(b["ctx"]),
            f"{nombre_fr(b['ctx'] / b['clients'] * 100, 1)} %",
            nombre_fr(b["vp"]), nombre_fr(b["fp"]),
            f"<b>{nombre_fr(b['precision'], 1)} %</b>", f"<b>{nombre_fr(b['captes'], 1)} %</b>", f"{nombre_fr(b['reste'], 1)} %"]


INDICATEURS = [
    "Clients du jeu", "Clients au contentieux (prédits en défaut)", "Part des clients",
    "dont en défaut (prédictions justes)", "dont sans défaut (fausses alertes)",
    "<b>Précision</b> : part des clients au contentieux qui font défaut", "<b>Part des défauts du jeu captés</b> par la règle",
    "Taux de défaut des clients restants, laissés au machine learning",
]
valeurs = [colonne(b_train), colonne(b_test), colonne(ORIGINE)]
st.caption("Comment lire : une colonne par jeu de données. Les deux lignes en gras sont celles qui comptent : la précision dit si la règle se trompe, la part des défauts captés dit quel poids elle a.")
tableau_html(["", f"Entraînement ({nombre_fr(len(train))} clients)", f"Test ({nombre_fr(len(test))} clients)", "Données d'origine (30 000 clients, étude)"],
             [[ind] + [v[i] for v in valeurs] for i, ind in enumerate(INDICATEURS)], largeurs=[37, 21, 21, 21])
st.caption("Entraînement et test : calculés en direct. Données d'origine : résultats de l'étude, repris tels quels (cellules 41 et 45), ces données n'étant pas dans le dépôt. Sur les clients qu'elle traite, la règle prédit tout le monde en défaut : toutes ses erreurs sont des fausses alertes, et le rappel y vaut 100 % par construction ; il n'a donc pas de sens ici.")
st.markdown(f"""
- **La précision est stable** : {nombre_fr(b_train['precision'], 1)} % sur l'entraînement, {nombre_fr(b_test['precision'], 1)} % sur le test, {nombre_fr(ORIGINE['precision'], 1)} % sur les données d'origine. Elle tient quel que soit le découpage, et même sur des données non nettoyées.
- **Elle capte environ un tiers des défauts** : {nombre_fr(b_train['captes'], 1)} % sur l'entraînement, {nombre_fr(b_test['captes'], 1)} % sur le test. Sur les données d'origine ({nombre_fr(ORIGINE['captes'], 1)} %), la part est un peu plus faible, car ce fichier contient aussi des clients sans dette en septembre, hors du périmètre étudié.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Le revers : des fausses alertes, et une cible imparfaite", anchor="limites")
figes = (train[[f'PAY_{i}' for i in range(1, 7)]] == 2).all(axis=1)
sains_figes = (train.loc[figes, 'dpnm'] == 0).mean() * 100
st.markdown(f"""
- **Environ {nombre_fr(100 - b_train['precision'], 0)} clients sur 100 placés au contentieux ne font pas défaut** ({nombre_fr(b_train['fp'])} sur l'entraînement). C'est la contrepartie assumée d'une règle simple : un client qui s'en sort quand même sera traité comme un client à risque. Pour une banque, ce coût est celui d'une surveillance renforcée, à comparer au coût d'un défaut non anticipé.
- **La cible elle-même n'est pas parfaite.** La façon dont le défaut d'octobre a été noté n'est pas documentée, et ce n'est pas le simple prolongement de la codification : parmi les {nombre_fr(int(figes.sum()))} clients de l'entraînement codifiés {codif('2')} sur les 6 mois, {nombre_fr(sains_figes)} % sont notés sans défaut, alors que leur codification ne bouge jamais. Une partie des fausses alertes vient peut-être de là ([05_02_EDA_contentieux.ipynb]({GH}/05_02_EDA_contentieux.ipynb), cellule 28).
- La règle prédit donc le défaut **tel que la banque l'a noté en octobre 2005**, pas forcément un impayé définitif.
- **Une piste pour la suite** : si le défaut d'octobre mêlait de vrais défauts et des statuts provisoires, comme la codification {codif('1')} de septembre, encore non tranchée par la banque, alors un modèle n'apprendrait plus seulement à prédire le défaut, mais aussi **la prochaine codification de la banque**. Ce serait un tout autre modèle, avec une autre question. Le dataset ne permet pas de le vérifier : la règle de calcul du défaut n'est pas documentée.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Ce que cela change pour la suite", anchor="suite")
# Tout le périmètre : la règle est figée et le test a déjà servi, la population restante est simplement décrite
b_perimetre = bilan(s12)
restants = len(s12) - b_perimetre['ctx']
st.markdown(f"""
Le machine learning reçoit **le dataset nettoyé, dont on retire les clients au contentieux** : les codifications corrigées au niveau 5, les montants et les colonnes créées, pour tous les autres clients. Sur le périmètre, il reste **{nombre_fr(restants)} clients à départager**, avec un taux de défaut de **{nombre_fr(b_perimetre['reste'], 1)} %**, contre {nombre_fr(b_perimetre['taux'], 1)} % avant le retrait. Cette population est plus homogène, mais aussi plus difficile : les défauts les plus visibles sont déjà traités, et il reste au modèle les **{nombre_fr(100 - b_perimetre['captes'])} % de défauts** que la règle ne capte pas. L'historique des retards de ces clients ne disparaît pas pour autant : il reste dans leurs codifications, et il est résumé par les colonnes créées (page 5.3).

C'est la **première moitié de la réponse à la problématique** : sans aucun machine learning, une règle métier explicable, fondée sur les codifications de la banque et sur les paiements, prédit déjà un tiers des défauts, avec environ {nombre_fr(b_test['precision'] / 10)} prédictions justes sur 10. La seconde moitié revient au modèle, sur les autres clients (partie 6), et le tout sera comparé aux résultats publiés en 2009 (partie 7).
""")

# ------------------------------------------------------------------------------
st.subheader("5. Comparatif provisoire : la règle, la première itération du machine learning, l'étude de 2009", anchor="comparatif")
# Résultats calculés hors du site, sur le même jeu de test que la règle (5 441 clients) : le modèle S12_6 de la première
# itération (lab_ML/corrections_niveau3/best_models/model_S126_corrections_niveau3.joblib, notebook ml12_6_cleaned3, même
# périmètre S12 et même découpage) et les règles simples sur les codifications brutes de cleaned3. Ni le modèle ni cleaned3
# ne sont déployés avec le site : chiffres repris tels quels (décision D19). Yeh et Lien (2009) : Tableau 1 de l'étude.
ML_S126 = {"predits": 1476, "vp": 764, "fp": 712, "auc": 0.80}
SIMPLE_6_MOIS = {"predits": 1597, "vp": 780, "fp": 817}
SIMPLE_SEPTEMBRE = {"predits": 634, "vp": 450, "fp": 184}
YEH_ERREUR, YEH_RATIO_SURFACE = 17, 0.54
# Entraînement : clients que les corrections retirent de « 2 en septembre » ou y ajoutent (calcul hors site, cleaned3 / cleaned5)
DIFF_TRAIN = {"brut": (2486, 1719), "retires": (180, 78), "retires_payes": (142, 58), "retires_faux2": (38, 20), "ajoutes": (97, 49)}

defauts_test = int(test['dpnm'].sum())


def ligne_comparatif(nom, predits, vp, fp, detail=""):
    fn = defauts_test - vp
    return [f"<b>{nom}</b>{detail}", nombre_fr(predits), nombre_fr(vp), f"{nombre_fr(vp / predits * 100, 1)} %" if predits else "–",
            f"{nombre_fr(vp / defauts_test * 100, 1)} %", f"{nombre_fr((fp + fn) / len(test) * 100, 1)} %"]


st.markdown(f"""
*Section provisoire, en attendant la partie 6.* Pour situer la règle, on la compare, **sur le même jeu de test** ({nombre_fr(len(test))} clients, dont {nombre_fr(defauts_test)} en défaut), au meilleur modèle de la première itération du machine learning sur le même périmètre (S12_6, CatBoost), à deux règles simples, et à l'étude de référence de 2009.
""")
tableau_html(["Approche", "Clients prédits en défaut", "Défauts trouvés", "Précision", "Part des défauts trouvés (rappel)", "Taux d'erreur"], [
    ligne_comparatif("Règle du contentieux", b_test['ctx'], b_test['vp'], b_test['fp']),
    ligne_comparatif("Machine learning, première itération", ML_S126['predits'], ML_S126['vp'], ML_S126['fp'], "<br><small>meilleur modèle du périmètre (S12_6, CatBoost)</small>"),
    ligne_comparatif("Règle simple : une codification 2 ou plus sur les 6 mois", SIMPLE_6_MOIS['predits'], SIMPLE_6_MOIS['vp'], SIMPLE_6_MOIS['fp'], "<br><small>codifications brutes</small>"),
    ligne_comparatif("Règle simple : codification 2 ou plus en septembre", SIMPLE_SEPTEMBRE['predits'], SIMPLE_SEPTEMBRE['vp'], SIMPLE_SEPTEMBRE['fp'], "<br><small>codifications brutes</small>"),
    ["<b>Personne en défaut</b>", "0", "0", "–", "0 %", f"{nombre_fr(defauts_test / len(test) * 100, 1)} %"],
    ["<b>Yeh et Lien (2009)</b><br><small>réseau de neurones, autre échantillon</small>", "non publié", "non publié", "non publiée", "non publiée",
     f"{YEH_ERREUR} %<br><small>ratio de surface {nombre_fr(YEH_RATIO_SURFACE, 2)}, soit un AUC d'environ 0,77</small>"],
], largeurs=[30, 13, 12, 12, 15, 18])
st.caption("Règle du contentieux : calcul en direct. Machine learning et règles simples : calculés hors du site sur le même jeu de test (modèle enregistré de la première itération, rechargé ; codifications brutes du nettoyage de niveau 3), repris tels quels. Le taux d'erreur compte toutes les erreurs : les clients sains prédits en défaut, et les défauts manqués. Pour une règle, les clients qu'elle ne retient pas sont comptés comme prédits sains. Yeh et Lien (2009) ne publient ni précision ni nombre de défauts détectés : seule la comparaison du taux d'erreur est possible, sur un échantillon différent.")
st.markdown(f"""
- **Le modèle de la première itération avait déjà « trouvé » le contentieux** : il prédit en défaut tous les clients que la règle place au contentieux, et retrouve donc les mêmes défauts. Il en ajoute {nombre_fr(ML_S126['vp'] - b_test['vp'])}, au prix de {nombre_fr(ML_S126['fp'] - b_test['fp'])} fausses alertes supplémentaires. Il trouve plus de défauts, mais se trompe beaucoup plus souvent : sa précision tombe à {nombre_fr(ML_S126['vp'] / ML_S126['predits'] * 100, 1)} %. C'est ce qui expliquait l'effet nul de la variable contentieux ajoutée au modèle (page 5.1).
- **Face à l'étude de 2009**, la règle seule a un taux d'erreur ({nombre_fr((b_test['fp'] + defauts_test - b_test['vp']) / len(test) * 100, 1)} %) du même ordre que le meilleur modèle de Yeh et Lien ({YEH_ERREUR} %), sans aucun modèle. La comparaison reste indicative : les échantillons diffèrent. Le modèle de la première itération a un meilleur AUC sur le test (environ {nombre_fr(ML_S126['auc'], 2)}), mais un taux d'erreur plus élevé, car il est réglé pour trouver le plus de défauts possible.
- **La règle du contentieux fait jeu égal avec une règle très simple, « codification 2 ou plus en septembre »**, détaillée ci-dessous.
""")

st.markdown("##### Les corrections rendent-elles la règle moins bonne ?")
brut_n, brut_d = DIFF_TRAIN['brut']
st.markdown("Sur le jeu d'entraînement, là où une règle se juge, voici ce qui distingue la règle du contentieux de la règle simple « codification 2 ou plus en septembre » appliquée aux codifications brutes :")
tableau_html(["Clients (entraînement)", "Clients", "En défaut", "Taux de défaut"], [
    ["Règle simple : codification 2 ou plus en septembre", nombre_fr(brut_n), nombre_fr(brut_d), f"{nombre_fr(brut_d / brut_n * 100, 1)} %"],
    ["<b>Règle du contentieux</b>", nombre_fr(b_train['ctx']), nombre_fr(b_train['vp']), f"<b>{nombre_fr(b_train['precision'], 1)} %</b>"],
    ["Retirés par les corrections", nombre_fr(DIFF_TRAIN['retires'][0]), nombre_fr(DIFF_TRAIN['retires'][1]), f"{nombre_fr(DIFF_TRAIN['retires'][1] / DIFF_TRAIN['retires'][0] * 100, 1)} %"],
    ["... dont retards payés", nombre_fr(DIFF_TRAIN['retires_payes'][0]), nombre_fr(DIFF_TRAIN['retires_payes'][1]), f"{nombre_fr(DIFF_TRAIN['retires_payes'][1] / DIFF_TRAIN['retires_payes'][0] * 100, 1)} %"],
    ["... dont faux 2 de septembre corrigés", nombre_fr(DIFF_TRAIN['retires_faux2'][0]), nombre_fr(DIFF_TRAIN['retires_faux2'][1]), f"{nombre_fr(DIFF_TRAIN['retires_faux2'][1] / DIFF_TRAIN['retires_faux2'][0] * 100, 1)} %"],
    ["Ajoutés par les corrections (remis à 2 en septembre)", nombre_fr(DIFF_TRAIN['ajoutes'][0]), nombre_fr(DIFF_TRAIN['ajoutes'][1]), f"{nombre_fr(DIFF_TRAIN['ajoutes'][1] / DIFF_TRAIN['ajoutes'][0] * 100, 1)} %"],
], largeurs=[52, 16, 16, 16])
st.markdown(f"""
- **Statistiquement, c'est un match nul** : la règle du contentieux est un peu plus précise ({nombre_fr(b_train['precision'], 1)} % contre {nombre_fr(brut_d / brut_n * 100, 1)} %) et trouve un peu moins de défauts ({nombre_fr(b_train['vp'])} contre {nombre_fr(brut_d)}). Des écarts d'un point, sur quelques dizaines de clients, relèvent du bruit.
- **Les corrections retirent bien quelques défauts de la règle, mais ne les perdent pas.** Les clients retirés comme ajoutés ont un risque intermédiaire (40 à 53 %) : moins que le contentieux, mais bien plus que la population laissée au modèle. Leur classement ne se décide pas sur le défaut, mais sur la logique métier : une facture payée ne justifie pas le contentieux, deux factures impayées le justifient. Les clients retirés sont confiés au machine learning, avec leurs traces dans les colonnes créées.
- **L'apport des corrections est ailleurs** : elles expliquent ce que recouvre le retard, assainissent tout l'historique (sorties, durées, retards isolés) et fournissent les colonnes que reçoit le modèle. C'est en partie 6 que se mesurera leur effet sur la prédiction.
""")

st.info(f"""
**Ce qu'il faut retenir de la partie 5** : partie de clients figés en retard au taux de défaut anormalement élevé, l'étude des codifications de retard a d'abord corrigé de faux retards, puis défini le contentieux par une règle métier : au moins deux codifications de retard d'affilée, ou un retard en septembre dont la suite est inconnue ; la sortie est celle que décide la banque, sauf en septembre, où une facture payée suffit. Sans regarder le défaut, cette règle isole un comportement de paiement dégradé ; avec le défaut, elle se révèle très efficace : environ {nombre_fr(b_test['part_clients'])} % des clients, un tiers des défauts, et {nombre_fr(b_test['precision'] / 10)} prédictions justes sur 10, stables sur des clients jamais vus. Le machine learning peut maintenant se concentrer sur le reste.
""")
