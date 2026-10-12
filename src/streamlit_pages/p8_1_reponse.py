import json
from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 8.1 : PEUT-ON PRÉVOIR LE DÉFAUT ? UNE RÈGLE MÉTIER, PUIS UN MODÈLE
# 1. Les règles seules (partie 5) : mêmes calculs que la page 5.5, en direct ; données d'origine reprises de 05_02 (section 7).
#    Sortie des clients de la règle : essai de lab_ML/comparatif_global/essai_jeu_corrige_deux_populations.ipynb (section 3).
# 2. Le système complet sur tout le périmètre : niveaux repris de lab_ML/evaluation_finale_test.ipynb, section 6
#    (mêmes chiffres et mêmes regroupements que la page 6.4), contrôlés en direct sur le dataset.
# 3. Le système du projet face au modèle brut de la démo 3, sur les 5 441 clients de la démo 1 : calcul en direct
#    (commun.py, systemes_sur_clients_demo) ; puis le comparatif global (lab_ML/comparatif_global/niveaux_de_risque_global.ipynb),
#    repris tels quels : les probabilités hors pli ne sont pas dans le dépôt.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
INCIDENTS = f"{GH_RACINE}/src/05_02_EDA_incidents.ipynb"
EVALUATION = f"{GH_RACINE}/lab_ML/evaluation_finale_test.ipynb"
NIVEAUX_GLOBAL = f"{GH_RACINE}/lab_ML/comparatif_global/niveaux_de_risque_global.ipynb"
HYPOTHESES = f"{GH_RACINE}/docs/hypotheses_et_conclusions.md"
ESSAI_REGLE = f"{GH_RACINE}/lab_ML/comparatif_global/essai_jeu_corrige_deux_populations.ipynb"
DEUX = ["En incident", "Retard imminent"]

# ------------------------------------------------------------------------------
# 1. Les règles seules (mêmes calculs que la page 5.5)
# ------------------------------------------------------------------------------
df, s12, train, test = donnees_partie_5()
# 05_02_EDA_incidents, section 7 : les deux populations sur les 30 000 lignes d'origine (codifications brutes, aucun filtre), comme en page 5.5
ORIGINE = {"precision": 69.55, "captes": 32.81}


def bilan_regle(d, statuts):
    retire = d["STATUT"].isin(statuts)
    return {"part_clients": retire.mean() * 100, "precision": d.loc[retire, "dpnm"].mean() * 100,
            "captes": d.loc[retire, "dpnm"].sum() / d["dpnm"].sum() * 100}


b_train, b_test = bilan_regle(train, ["En incident"]), bilan_regle(test, ["En incident"])
b_imminent, b_deux = bilan_regle(s12, ["Retard imminent"]), bilan_regle(s12, DEUX)

# ------------------------------------------------------------------------------
# 2. Le système complet sur tout le périmètre (évaluation finale, section 6 ; mêmes niveaux que la page 6.4)
# ------------------------------------------------------------------------------
# Six tranches du notebook regroupées comme dans les démos (bornes 10, 30 et 60 % des défauts) : (niveau, clients, défauts)
NIVEAUX = [
    ("En incident", 3754, 2222),
    ("Retard imminent", 989, 649),
    ("Très haut risque", 783, 326),
    ("Haut risque", 1015 + 1381, 304 + 312),
    ("Risque modéré", 1501 + 1684 + 1811, 301 + 296 + 296),
    ("Risque faible", 14284, 1266),
]
total_clients = sum(n[1] for n in NIVEAUX)
total_defauts = sum(n[2] for n in NIVEAUX)
assert (len(s12), int(s12["dpnm"].sum())) == (total_clients, total_defauts)
taux_perimetre = total_defauts / total_clients * 100
# Étapes cumulées : les deux règles ensemble, puis chaque niveau signalé du modèle ; le risque faible n'est pas signalé
GROUPES_ETAPES = [NIVEAUX[0:2], NIVEAUX[2:3], NIVEAUX[3:4], NIVEAUX[4:5]]
cumul_clients, cumul_defauts, etapes = 0, 0, []
for groupe in GROUPES_ETAPES:
    cumul_clients += sum(n[1] for n in groupe)
    cumul_defauts += sum(n[2] for n in groupe)
    etapes.append((cumul_defauts / total_defauts * 100, cumul_defauts / cumul_clients * 100, cumul_clients / total_clients * 100))
FAIBLE = NIVEAUX[5]

# ------------------------------------------------------------------------------
# 3. Le système du projet face au modèle brut, sur les mêmes clients (calcul en direct)
# ------------------------------------------------------------------------------
# Périmètre de base : le modèle brut note les 30 000 clients du fichier d'origine ; le projet ne décide que pour son périmètre.
# Fichier d'origine : 30 000 clients, 6 636 défauts (01_01_audit) ; le reste en direct (nettoyage, puis dette en septembre)
ORIGINE_FICHIER = {"clients": 30000, "defauts": 6636}
retires_nettoyage = (ORIGINE_FICHIER["clients"] - len(df), ORIGINE_FICHIER["defauts"] - int(df["dpnm"].sum()))
sans_dette = df[df["BILL_AMT1"] <= 0]
hors_perimetre = (retires_nettoyage[0] + len(sans_dette), retires_nettoyage[1] + int(sans_dette["dpnm"].sum()))
assert hors_perimetre[0] + len(s12) == ORIGINE_FICHIER["clients"] and hors_perimetre[1] + int(s12["dpnm"].sum()) == ORIGINE_FICHIER["defauts"]

clients = systemes_sur_clients_demo()
y = clients["dpnm"].values
score_projet = score_systeme_projet(clients)
score_brut = clients["score_brut"].values
bornes = json.loads((BASE_DIR / "lab_ML" / "demo_ML" / "bornes_niveaux.json").read_text(encoding="utf-8"))
regles_demo = clients["regles"].values
proba_modele = np.nan_to_num(clients["proba_modele"].values)   # pas de probabilité pour les clients des règles


def defauts_en_tete(score, nombre, masque=None):
    """Défauts parmi les « nombre » clients les mieux notés par un score (parmi ceux du masque, ou tous)."""
    idx = np.arange(len(y)) if masque is None else np.where(masque)[0]
    return int(y[idx[np.argsort(-score[idx], kind="stable")][:nombre]].sum())


# Comparaison à nombre égal d'alertes : à chaque palier, le projet signale ses clients ; le modèle brut signale autant
# de clients, les mieux notés par son score, et l'on compte les défauts trouvés de chaque côté
PALIERS = [("Règles seules", None), ("+ très haut risque", "tres_haut_risque"), ("+ haut risque", "haut_risque"),
           ("+ risque modéré", "risque_modere")]
comparaison = []   # (palier, alertes, défauts trouvés par le projet, défauts trouvés par le modèle brut)
for libelle, cle in PALIERS:
    signales = regles_demo if cle is None else (regles_demo | (proba_modele >= bornes[cle]))
    comparaison.append((libelle, int(signales.sum()), int(y[signales].sum()), defauts_en_tete(score_brut, int(signales.sum()))))
auc_projet = aire_roc(y, score_projet)
auc_brut = aire_roc(y, score_brut)
ecarts = [c[3] - c[2] for c in comparaison]   # défauts en plus pour le modèle brut (négatif : le projet devant)


def effectifs(masque):
    return [nombre_fr(int(masque.sum())), nombre_fr(int((masque & (y == 1)).sum())), nombre_fr(int((masque & (y == 0)).sum()))]


# (a) Sur les autres clients seulement (hors des deux règles), au même nombre d'alertes que chaque niveau du projet
autres = ~regles_demo
y_autres = y[autres]
NIVEAUX_AUTRES = [("Très haut risque", "tres_haut_risque"), ("+ haut risque", "haut_risque"), ("+ risque modéré (taux de rappel minimal)", "risque_modere")]
comparaison_autres = []   # (niveau, alertes, défauts trouvés par le projet, défauts trouvés par le modèle brut)
for libelle, cle in NIVEAUX_AUTRES:
    signales = autres & (proba_modele >= bornes[cle])
    comparaison_autres.append((libelle, int(signales.sum()), int(y[signales].sum()), defauts_en_tete(score_brut, int(signales.sum()), autres)))
auc_autres_projet = aire_roc(y_autres, proba_modele[autres])
auc_autres_brut = aire_roc(y_autres, score_brut[autres])
ecart_autres = max(abs(c[3] - c[2]) for c in comparaison_autres)

# (b) Sur les populations des règles : au palier des règles seules, le modèle brut signale autant de clients que les règles
ordre_brut = np.argsort(-score_brut, kind="stable")
signales_brut_regles = np.zeros(len(y), dtype=bool)
signales_brut_regles[ordre_brut[:int(regles_demo.sum())]] = True
sortis = regles_demo & ~signales_brut_regles
sortis_defauts, sortis_sains = int((sortis & (y == 1)).sum()), int((sortis & (y == 0)).sum())

# Comparatif global, sur les 27 202 clients du périmètre (H13) : (approche, règle seule, + haut risque, + risque modéré),
# chaque palier en (part des défauts détectés, précision), en %
COMPARATIF_GLOBAL = [
    ("<b>Version finale du projet</b> : règles métier (population en incident, retard imminent), puis <code>ml_17</code> (21 variables)", (48.1, 60.5), (63.8, 48.1), (78.8, 36.4)),
    ("Règles métier, puis un modèle sur les 23 variables d'origine", (48.1, 60.5), (63.4, 48.9), (78.2, 36.0)),
    ("Règles métier, puis un modèle <b>sans aucune codification</b> (montants, plafond, démographie)", (48.1, 60.5), (63.1, 47.7), (78.1, 35.5)),
    ("Codification de la banque (2 ou plus en septembre), puis un modèle sur les 23 variables d'origine", (36.3, 69.5), (54.2, 58.2), (71.4, 41.2)),
    ("Codification de la banque, puis un modèle sans aucune codification", (36.3, 69.5), (53.2, 56.2), (71.5, 40.4)),
]

# ==============================================================================
entete_partie_8()
st.markdown("---")
st.header("8.1 Peut-on prévoir le défaut ? Une règle métier, puis un modèle", anchor="reponse")
st.markdown("""
La réponse se construit en deux temps, dans l'ordre du projet : d'abord des **règles métier**, sans aucun machine learning, pour deux populations, la population en incident et le retard imminent (partie 5) ; puis un **modèle** pour tous les autres clients (partie 6). Cette page mesure ce que vaut chacun, puis ce que vaut le tout face à un modèle lancé directement sur les données brutes.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Premier temps : des règles métier, sans machine learning", anchor="regle")
st.markdown(f"""
Deux règles métier prédisent en défaut tous les clients qu'elles retiennent (partie 5) : la **population en incident** à M (deux codifications de retard d'affilée, ou une seule de {codif('3')} ou plus, page 5.2) et le **retard imminent** (un seul retard, posé en septembre après un mois d'août sain : la banque a déjà jugé la facture de septembre impayée). Elles n'ont été réglées sur aucun défaut : elles viennent de la logique métier, et le défaut n'a servi qu'à les vérifier.
- **Elles retiennent peu de clients** : environ {nombre_fr(b_deux['part_clients'], 0)} % des clients actifs.
- **Elles ont raison environ six fois sur dix** : {nombre_fr(b_train['precision'], 1)} % des clients en incident font défaut sur l'entraînement, {nombre_fr(b_test['precision'], 1)} % sur le test, jamais vu ; {nombre_fr(b_imminent['precision'], 1)} % des clients en retard imminent ; {nombre_fr(b_deux['precision'], 1)} % pour les deux réunies, et {nombre_fr(ORIGINE['precision'], 1)} % sur les 30 000 clients des données d'origine, sans aucun nettoyage.
- **Elles trouvent à elles seules près de la moitié des défauts** : {nombre_fr(b_deux['captes'], 1)} % des défauts des clients actifs, dont {nombre_fr(b_test['captes'], 1)} % pour la seule population en incident sur le test.

**Sans aucun modèle, deux règles fondées sur les codifications de la banque prédisent donc déjà près de la moitié des défauts**, et n'importe quel conseiller peut les appliquer et les expliquer. Ces codifications ne reflètent pas toujours fidèlement le comportement du client : ce sont des étiquettes posées par la banque, parfois en décalage avec les paiements (page 3.3). C'est pourquoi les règles les lisent après correction (codifications {codif('1')} de septembre corrigées, codifications {codif('2')} d'avril à juin uniformisées d'après les montants payés, page 3.5). Cette part des défauts est donc prévue par **l'étiquette de la banque**, relue avec les paiements, plus que par le comportement lui-même.
""")
st.caption(f"Entraînement et test du découpage de la partie 5 : calculés en direct (détail en page 5.5). Données d'origine : résultats de l'étude, repris tels quels ([05_02_EDA_incidents.ipynb]({INCIDENTS}), section 7).")
st.markdown(f"""
**Pourquoi prédire en défaut ces deux populations entières, sans exception ?** Environ {nombre_fr(100 - b_train['precision'], 0)} clients en incident sur 100 et {nombre_fr(100 - b_imminent['precision'], 0)} clients en retard imminent sur 100 ne font pas défaut : des modèles ont donc été entraînés sur chacune de ces populations, pour repérer les clients à en sortir. Avec une exigence métier stricte, ne sortir un client que s'il a au moins neuf chances sur dix de payer, car sortir à tort un client qui sera en défaut revient à abandonner une créance, **aucun modèle ne trouve de clients à sortir** : ils gardent la quasi-totalité de chaque population en défaut. Les modèles y trient à peine mieux que le hasard (ROC AUC d'environ 0,6 en incident, de 0,53 à 0,63 en retard imminent), avec ou sans les codifications : rien dans les six mois de données ne distingue les clients qui paieront. **Les règles restent donc la seule décision défendable** pour ces clients.
""")
st.caption(f"Essai mené sur chacune des deux populations du dataset nettoyé, avec quatre modèles et trois jeux de variables (toutes, sans les codifications, codifications seules), chaque client noté par un modèle qui ne l'a pas vu : [essai par populations]({ESSAI_REGLE}), section 3 ; chiffres repris tels quels, les probabilités ne sont pas dans le dépôt.")

# ------------------------------------------------------------------------------
st.subheader("2. Deuxième temps : le modèle sur les autres clients, et jusqu'où signaler", anchor="systeme")
libelles = ["Règles<br>seules", "+ très haut<br>risque", "+ haut risque", "+ risque modéré"]
col_graphe, col_texte = st.columns(2, vertical_alignment="center")
with col_graphe:
    st.plotly_chart(figure_detection(libelles, [e[0] for e in etapes], [e[1] for e in etapes], taux_perimetre,
                                     info_survol=("Clients signalés", [e[2] for e in etapes]), etiquettes_barres_dedans=True, hauteur=530),
                    width='stretch')
with col_texte:
    st.markdown(f"""
Pour les autres clients, le modèle ne dit pas « défaut » ou « pas défaut » : il les **range du plus au moins risqué**, en niveaux de risque (page 6.4). Sur tout le portefeuille, on signale d'abord les deux populations des règles, puis on descend d'un niveau à la fois.

- **Les règles seules** trouvent près de **la moitié des défauts** ({nombre_fr(etapes[0][0], 0)} %), avec une précision d'environ **six sur dix**, en signalant {nombre_fr(etapes[0][2], 0)} % des clients.
- **Avec le très haut risque**, la tête de liste du modèle, {nombre_fr(etapes[1][0], 0)} % des défauts sont trouvés, avec une précision encore de {nombre_fr(etapes[1][1], 0)} %.
- **Avec le haut risque**, près des deux tiers des défauts sont trouvés ({nombre_fr(etapes[2][0], 0)} %), et environ un client signalé sur deux est en défaut.
- **Avec le risque modéré**, le dernier niveau signalé, près de **quatre défauts sur cinq** sont trouvés ({nombre_fr(etapes[3][0], 0)} %), mais en signalant {nombre_fr(etapes[3][2], 0)} % des clients : la précision tombe à un peu plus d'un sur trois. Le modèle s'arrête là : son seuil a été fixé pour trouver 60 % des défauts des clients laissés au machine learning, l'objectif retenu dès le départ (page 6.2).
- **Le risque faible n'est pas signalé** : il garde environ un défaut sur cinq, mais seulement {nombre_fr(FAIBLE[2] / FAIBLE[1] * 100, 0)} % de ses clients font défaut. Aller les chercher coûterait trop cher : il faudrait signaler beaucoup plus de clients, avec une précision qui se rapproche du hasard à mesure qu'on descend vers les derniers clients de la liste (page 6.4, sous-partie 3). Une partie de ces défauts ont d'ailleurs le profil des bons clients, et aucun modèle ne les distingue (page 6.5).

Chaque niveau ajouté rapporte de moins en moins de défauts par client signalé. **Jusqu'où signaler est un choix de la banque**, selon ce que lui coûte une fausse alerte face à un défaut manqué.
""")
st.caption(f"Valeurs cumulées : chaque étape ajoute un niveau aux précédents ; barres : part de tous les défauts détectés ; courbe : précision des défauts prédits. Tout le périmètre ({nombre_fr(total_clients)} clients avec une dette en septembre et un plafond de 500 000 NT$ ou moins), chaque client classé par un modèle qui ne l'a jamais vu ; mêmes chiffres que le tableau des niveaux de risque de la page 6.4. Source : [évaluation finale]({EVALUATION}), section 6.")

# ------------------------------------------------------------------------------
st.subheader("3. Le travail du projet fait-il mieux qu'un modèle lancé sur les données brutes ?", anchor="modele-brut")
st.markdown(f"""
Le projet a pris un long chemin : nettoyage, étude de la population en incident, colonnes construites, scénarios. Un modèle lancé directement sur les 23 variables d'origine, sans rien de tout cela, ferait-il moins bien ?

**D'abord, les deux n'ont pas le même périmètre.** Le modèle brut note les {nombre_fr(ORIGINE_FICHIER['clients'])} clients du fichier d'origine. Le projet ne décide que pour son périmètre, les {nombre_fr(len(s12))} clients gardés par le nettoyage qui ont une dette en septembre : pour les {nombre_fr(hors_perimetre[0])} autres ({nombre_fr(retires_nettoyage[0])} retirés au nettoyage, {nombre_fr(len(sans_dette))} sans dette en septembre), il ne rend **aucune décision**, et ces clients portent {nombre_fr(hors_perimetre[1])} défauts, soit {nombre_fr(hors_perimetre[1] / ORIGINE_FICHIER['defauts'] * 100, 0)} % de tous les défauts du fichier. C'est un choix métier (partie 3) : on ne prédit pas le défaut d'un crédit qui n'est pas utilisé, et les comptes atypiques sont mis à part. La comparaison sur tout le fichier d'origine, ces clients compris, est celle de la démo 3 (page 7.4).

Ici, les deux systèmes sont donc comparés **dans le périmètre du projet, sur les mêmes clients** : les {nombre_fr(len(clients))} clients de la démo 1, qu'**aucun des deux n'a vus** à l'entraînement :
- le **système du projet** : les règles métier (population en incident, retard imminent), puis le modèle retenu (`ml_17`) pour les autres clients (démo 1, page 7.2) ;
- le **modèle brut** : un CatBoost entraîné sur les 30 000 clients d'origine, sans nettoyage ni règle, chaque client noté par un modèle qui ne l'a pas vu (démo 3, page 7.4).

La question est celle d'une banque : **avec le même nombre d'alertes, combien de défauts chaque système trouve-t-il ?** À chaque palier, le projet signale ses clients ; le modèle brut en signale autant, les mieux notés par son score. Le calcul est fait en direct.
""")
fig = go.Figure()
x = [c[0] for c in comparaison]
for nom, i, couleur in (("Système du projet (règles + modèle)", 2, COULEURS["vert_fonce"]), ("Modèle brut (23 variables d'origine)", 3, COULEURS["gris"])):
    valeurs = [c[i] for c in comparaison]
    fig.add_trace(go.Bar(x=x, y=valeurs, name=nom, marker_color=couleur, text=[nombre_fr(v) for v in valeurs],
                         textposition="outside", textfont=dict(size=TAILLE_ETIQUETTE), cliponaxis=False,
                         customdata=[c[1] for c in comparaison],
                         hovertemplate="%{x}<br>" + nom + " : %{y} défauts trouvés<br>pour %{customdata} alertes<extra></extra>"))
fig.add_hline(y=int(y.sum()), line=dict(color=COULEURS["orange"], dash="dot", width=2))
fig.add_trace(go.Scatter(x=[None], y=[None], name=f"Tous les défauts ({nombre_fr(int(y.sum()))})", mode="lines",
                         line=dict(color=COULEURS["orange"], dash="dot", width=2)))
fig.update_xaxes(type="category")
fig.update_layout(barmode="group", yaxis_title="Défauts trouvés (nombre)", yaxis_range=[0, y.sum() * 1.1], height=430, separators=", ",
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
col_graphe, col_tableau = st.columns([3, 2], vertical_alignment="center")
with col_graphe:
    st.plotly_chart(fig, width='stretch')
with col_tableau:
    tableau_html(["Palier du projet", "Alertes", "Défauts trouvés : projet", "Défauts trouvés : modèle brut"],
                 [[c[0], nombre_fr(c[1]), nombre_fr(c[2]), nombre_fr(c[3])] for c in comparaison]
                 + [["<b>Qualité du tri</b> (ROC AUC)", "—", nombre_fr(auc_projet, 3), nombre_fr(auc_brut, 3)]],
                 largeurs=[31, 19, 25, 25])
st.caption(f"{nombre_fr(len(clients))} clients, dont {nombre_fr(int(y.sum()))} en défaut (ligne orange) : le test du machine learning et 20 % des clients de chacune des deux populations des règles du périmètre, tirés de la même façon. Paliers du projet : seuils du modèle fixés sur l'entraînement (page 6.4). Modèle brut : autant de clients signalés que le projet, les mieux notés par son score. ROC AUC : probabilité qu'un client en défaut soit rangé avant un bon client (0,5 au hasard, 1 pour un tri parfait) ; pour le projet, les deux populations des règles sont rangées en tête, ex aequo. Le modèle brut a appris sur plus de clients (environ 24 000 par modèle, population en incident et retard imminent compris, contre environ 18 000 pour le projet).")
st.markdown(f"""
**Vue d'ensemble : avec le même nombre d'alertes, les deux systèmes trouvent presque autant de défauts.** L'écart va de {nombre_fr(min(ecarts))} à {nombre_fr(max(ecarts))} défauts, sur {nombre_fr(int(y.sum()))} : le plus grand, {nombre_fr(ecarts[0])} défauts en plus pour le modèle brut, est au palier des règles seules ; au dernier palier, le projet en trouve {nombre_fr(-ecarts[-1]) if ecarts[-1] < 0 else 'autant ou moins'}{' de plus' if ecarts[-1] < 0 else ''}. La qualité du tri est proche ({nombre_fr(auc_projet, 3)} contre {nombre_fr(auc_brut, 3)}).

Cette vue d'ensemble mélange pourtant deux terrains. Le modèle du projet est réglé pour retrouver 60 % des défauts **des autres clients** ; le modèle brut classe **tous les clients**, y compris les deux populations des règles, où les défauts se repèrent facilement. Pour comparer à armes égales, il faut les séparer.
""")
st.markdown(f"""
**(a) Sur les autres clients : les deux modèles se valent.** Hors des deux règles, avec le même nombre d'alertes que chaque niveau du projet :
""")
tableau_html(["Niveaux signalés", "Alertes", "Défauts trouvés : modèle du projet", "Défauts trouvés : modèle brut"],
             [[c[0], nombre_fr(c[1]), nombre_fr(c[2]), nombre_fr(c[3])] for c in comparaison_autres]
             + [["<b>Qualité du tri</b> (ROC AUC)", "—", nombre_fr(auc_autres_projet, 3), nombre_fr(auc_autres_brut, 3)]],
             largeurs=[34, 16, 25, 25])
st.caption(f"Les {nombre_fr(int(autres.sum()))} clients de la démo 1 hors des deux règles (le test du machine learning), dont {nombre_fr(int(y_autres.sum()))} en défaut. Le modèle brut signale autant de ces clients que le projet, les mieux notés par son score. Calculé en direct.")
st.markdown(f"""
Sur le même terrain, les deux modèles ne s'écartent que de {nombre_fr(ecart_autres)} défaut{'s' if ecart_autres >= 2 else ''} au plus, et la qualité du tri est la même : **le travail du projet n'a pas fait un meilleur modèle, mais pas un moins bon non plus**, avec moins de variables et sans le genre, l'âge ni le statut marital.

**(b) Sur les populations des règles : le gain du modèle brut a un prix que le projet refuse.** Au palier des règles seules, avec autant d'alertes que les deux règles, voici ce que le modèle brut fait de leurs clients :
""")
tableau_html(["", "Clients", "dont en défaut", "dont sans défaut"], [
    ["<b>Clients des deux règles</b> (population en incident, retard imminent)", *effectifs(regles_demo)],
    ["… que le modèle brut garde", *effectifs(regles_demo & signales_brut_regles)],
    ["<b>… que le modèle brut laisse partir</b>", *effectifs(sortis)],
    ["Clients hors des règles que le modèle brut signale à leur place", *effectifs(~regles_demo & signales_brut_regles)],
], largeurs=[46, 18, 18, 18])
st.caption(f"Les {nombre_fr(len(clients))} clients de la démo 1, calculé en direct. Modèle brut : autant de clients signalés que les deux règles, les mieux notés par son score.")
st.markdown(f"""
Pour trouver ses {nombre_fr(ecarts[0])} défauts de plus, le modèle brut **sort {nombre_fr(int(sortis.sum()))} clients des règles, dont {nombre_fr(sortis_defauts)} vrais défauts** : environ un défaut pour {nombre_fr(sortis_sains / sortis_defauts, 1) if sortis_defauts else '—'} clients sans défaut. Il signale à leur place autant de clients ordinaires, parmi lesquels il trouve plus de défauts. Or l'exigence fixée par le métier, avant tout calcul, ne sort un client de ces populations que s'il a au moins **neuf chances sur dix** d'être sans défaut (sous-partie 1) : sortir à tort un client en incident revient à abandonner une créance déjà jugée en retard. Compter seulement les défauts trouvés met sur le même plan un défaut abandonné dans ces populations et un défaut manqué ailleurs ; ce n'est pas le critère du projet, qui donne aux deux erreurs un coût différent.

**L'avance du modèle brut au premier palier ne vient donc pas d'un meilleur modèle : elle vient seulement de sa façon de traiter les populations des règles, en abandonnant des clients dont une part importante ne paiera pas, ce que l'exigence métier refuse.** Les règles n'abandonnent personne, et restent explicables.

Ce n'est pas un hasard de ces clients-là. Le comparatif global du projet, mené sur tout le périmètre avec deux façons de séparer les clients à risque (les règles métier, ou la seule codification de la banque) et plusieurs jeux de variables, arrive au même constat : **toutes les approches tombent sur la même courbe**.
""")
tableau_html(["Approche", "Règles seules", "+ haut risque", "+ risque modéré"],
             [[nom] + [f"{nombre_fr(p[0], 1)} % des défauts<br>précision {nombre_fr(p[1], 1)} %" for p in paliers] for nom, *paliers in COMPARATIF_GLOBAL],
             largeurs=[40, 20, 20, 20])
st.caption(f"Tout le périmètre (27 202 clients), chaque client classé par un modèle qui ne l'a pas vu. Trois paliers : la règle seule, puis les clients du modèle jusqu'à 30 % des défauts des autres clients (haut risque, très haut risque compris), puis jusqu'à 60 % (risque modéré). Chiffres repris tels quels du [comparatif des niveaux de risque]({NIVEAUX_GLOBAL}), sur les clients communs à toutes les approches : les probabilités des modèles ne sont pas dans le dépôt.")
st.markdown(f"""
Trois enseignements :
- **Le travail sur les variables n'a pas déplacé la courbe** : la version finale fait comme un modèle sur les 23 variables d'origine, à chaque palier.
- **Les règles métier et la codification de la banque se valent** : la codification de septembre retient moins de clients, avec plus de précision, mais trouve moins de défauts ; une fois le modèle ajouté, c'est un autre point de la même courbe. Les règles métier vont plus loin : elles retiennent aussi des clients que la banque codifie {codif('1')} en septembre, jugés en retard une fois cette codification corrigée (page 3.5).
- **Le comportement seul fait presque aussi bien** : sans aucune codification, avec les seuls montants (factures et paiements), le plafond et la démographie, le modèle trouve autant de défauts, pour une précision à peine plus basse. Une fois les populations à risque mises à part, ce sont les montants qui portent l'essentiel de ce qui est prévisible.

**Ce que le projet apporte n'est donc pas un meilleur score, mais un système défendable, à score égal** :
- près de la moitié des défauts est expliquée par des **règles métier lisibles**, sans modèle ;
- le modèle du projet n'utilise, comme donnée démographique, que le **niveau d'études**, alors que le modèle brut se sert aussi du genre, de l'âge et du statut marital (pages 6.3 et 6.6) ;
- les données sont **nettoyées**, chaque correction justifiée, et chaque client reçoit un **niveau de risque** que l'on peut expliquer.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Le verdict", anchor="verdict")
taux_tres_haut = NIVEAUX[2][2] / NIVEAUX[2][1] * 100
taux_faible = FAIBLE[2] / FAIBLE[1] * 100
# Le verdict de la problématique, dans l'encadré bleu : c'est l'essentiel de la page et du site.
# La problématique citée en tête de l'encadré est écrite en 20 px (16 px pour le reste du texte).
st.markdown("<style>.st-key-verdict blockquote p { font-size: 20px; }</style>", unsafe_allow_html=True)
st.container(key="verdict").info(f"""
> *« Peut-on prévoir le défaut de paiement d'un client en se basant uniquement sur son comportement transactionnel des 6 derniers mois, malgré un manque d'informations économiques globales ? »*

**Oui, en partie : on peut prévoir une grande part des défauts, mais pas le défaut de chaque client.** Le verdict se lit en reprenant la question, morceau par morceau.

**« Prévoir le défaut » : oui, pour une part importante des défauts.**
- La règle du contentieux, sans aucun modèle, trouve environ un tiers des défauts ({nombre_fr(b_test['captes'], 1)} % sur le test), avec {nombre_fr(b_test['precision'], 1)} % de prédictions justes.
- Le modèle y ajoute les clients les plus risqués parmi les autres. Avec le très haut et le haut risque, **{nombre_fr(etapes[2][0], 0)} % des défauts du portefeuille sont trouvés**, en signalant {nombre_fr(etapes[2][2], 0)} % des clients, dont **{nombre_fr(etapes[2][1], 0)} % sont réellement en défaut**, contre {nombre_fr(taux_perimetre, 0)} % pour des clients tirés au hasard.
- Le modèle sépare nettement les clients : un client du très haut risque fait défaut **{nombre_fr(taux_tres_haut / taux_faible, 0)} fois plus souvent** qu'un client du risque faible ({nombre_fr(taux_tres_haut, 0)} % contre {nombre_fr(taux_faible, 0)} %).

**« D'un client » : non, pas à coup sûr.** Même en tête de liste, un client signalé sur deux paie. Et environ un tiers des défauts des clients hors contentieux ont exactement le profil des bons clients : pas de retard, un paiement en septembre, la même note donnée par les modèles ; aucun modèle ne les distingue (page 6.5). Le comportement **classe** les clients par niveau de risque ; il ne **désigne** pas celui qui fera défaut. Pour une banque, c'est un outil pour prioriser la surveillance, pas pour décider seul du sort d'un client.

**« Uniquement sur son comportement transactionnel » : oui, mais à nuancer.** Les six mois de données mêlent deux choses : le **comportement du client** (factures, paiements, plafond) et les **codifications**, l'étiquette que la banque pose sur ses retards, qui ne reflète pas toujours fidèlement ses paiements. Le tiers de défauts trouvé par la règle vient d'abord de cette étiquette. Pour les autres clients, en revanche, le comportement seul fait presque aussi bien que les codifications : les montants facturés et payés portent l'essentiel de ce qui reste prévisible (section 3). Le modèle retenu n'utilise d'ailleurs aucune donnée démographique : ni l'âge, ni le genre, ni le niveau d'études, ni le statut marital.

**« Malgré un manque d'informations économiques globales » : ce manque-là n'a presque pas pesé.** Les modèles des banques tiennent compte de la conjoncture (chômage, inflation, croissance) ; **le projet n'a intégré aucune donnée économique de l'époque**. Ici, elle ne pouvait rien départager : les six mois de données couvrent la même période pour tous les clients, qui vivent tous la même conjoncture. Et en 2005, l'économie taïwanaise allait bien : la crise venait du crédit, pas de l'économie (partie 0). Sans ces informations, le projet atteint le niveau de l'étude de 2009 (page 8.2), et tous les modèles essayés tombent sur la même courbe (section 3). Leur absence pèserait ailleurs : un modèle qui ignore la conjoncture ne vaut pas tel quel pour une autre période.

**Ce qui manque davantage, ce sont les données économiques du client lui-même** : son revenu, ses autres crédits, son loyer, son endettement total, son reste à vivre. Le dataset n'en contient aucune. Or la crise de 2005 est née d'un endettement réparti entre plusieurs banques, des clients payant une carte avec une autre (partie 0) : la banque ne voit ici que ses propres comptes. On ne peut pas mesurer ce que ces données auraient apporté, mais une partie des défauts qui ne s'annoncent pas dans l'historique (page 6.5) pourrait s'y cacher, à côté d'un défaut dont la définition n'est pas documentée.
""")
