import json
from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 8.2 : COMPARAISON AVEC YEH ET LIEN (2009), DANS LEURS PROPRES MÉTRIQUES
# Métriques de l'étude (Tableau 1) : taux d'erreur et ratio de surface du graphique de lift (= 2 × ROC AUC − 1).
# Section 2 : calcul en direct sur les 5 441 clients de la démo 1 (règles, système du projet, modèle brut ; commun.py).
# Section 3 : la première itération du machine learning (modèle S12_6), reprise de l'ancien comparatif provisoire de
# la page 5.6 : résultats calculés hors du site sur le test de la partie 5 (modèle enregistré de l'archive
# lab_ML/1ere_iteration/, notebook ml12_6_cleaned3), repris tels quels (décision D19) ; la règle y est recalculée en direct.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
TRADUCTION = f"{GH_RACINE}/docs/traduction_DefaultCreditCardClients_yeh_2009.md"
HYPOTHESES = f"{GH_RACINE}/docs/hypotheses_et_conclusions.md"
TABLEAU_ML_1 = f"{GH_RACINE}/lab_ML/1ere_iteration/tableau_ML.md"

# Yeh et Lien (2009), Tableau 1, échantillon de validation : (méthode, taux d'erreur, ratio de surface)
YEH = [("Réseau de neurones (meilleur modèle)", 0.17, 0.54), ("Arbre de classification", 0.17, 0.536),
       ("K plus proches voisins", 0.16, 0.45), ("Régression logistique", 0.18, 0.44)]

# ------------------------------------------------------------------------------
# Section 2 : les mêmes clients que la page 8.1, mesurés comme dans l'étude
# ------------------------------------------------------------------------------
clients = systemes_sur_clients_demo()
y = clients["dpnm"].values.astype(bool)
hasard = y.mean() * 100
bornes = json.loads((BASE_DIR / "lab_ML" / "demo_ML" / "bornes_niveaux.json").read_text(encoding="utf-8"))
ctx = clients["contentieux"].values
banque = clients["PAY_1_origine"].values >= 2
six_mois = (clients[[f"PAY_{n}_origine" for n in range(1, 7)]].values >= 2).any(axis=1)


def taux_erreur(declares):
    """Part des clients mal classés : bons clients déclarés en défaut, et défauts non déclarés."""
    return (declares != y).mean() * 100


def ratio_regle(declares):
    """Ratio de surface d'une règle (oui / non) : part des défauts trouvés − part des bons clients signalés (= 2 × ROC AUC − 1)."""
    return declares[y].mean() - declares[~y].mean()


def meme_nombre_brut(nombre):
    """Les clients les mieux notés par le modèle brut, autant que le système du projet en déclare."""
    declares = np.zeros(len(y), dtype=bool)
    declares[np.argsort(-clients["score_brut"].values)[:nombre]] = True
    return declares


ratio_projet = 2 * aire_roc(y, score_systeme_projet(clients)) - 1
ratio_brut = 2 * aire_roc(y, clients["score_brut"]) - 1
paliers = {cle: ctx | (clients["proba_ml14"].values >= bornes[cle]) for cle in ("tres_haut_risque", "haut_risque")}

# ------------------------------------------------------------------------------
# Section 3 : la première itération, sur le test de la partie 5 (5 441 clients, autre tirage que la démo 1)
# ------------------------------------------------------------------------------
df, s12, train, test = donnees_partie_5()
ctx_test = test["STATUT"] == "Au contentieux"
defauts_test = int(test["dpnm"].sum())
REGLE_TEST = {"predits": int(ctx_test.sum()), "vp": int(test.loc[ctx_test, "dpnm"].sum())}
REGLE_TEST["fp"] = REGLE_TEST["predits"] - REGLE_TEST["vp"]
ML_S126 = {"predits": 1476, "vp": 764, "fp": 712, "auc": 0.80}


def ligne_test(nom, r, auc=None):
    fn = defauts_test - r["vp"]
    return [nom, nombre_fr(r["predits"]), nombre_fr(r["vp"]), f"{nombre_fr(r['vp'] / r['predits'] * 100, 1)} %",
            f"{nombre_fr(r['vp'] / defauts_test * 100, 1)} %", f"{nombre_fr((r['fp'] + fn) / len(test) * 100, 1)} %",
            nombre_fr(2 * auc - 1, 2) if auc else nombre_fr(r["vp"] / defauts_test - r["fp"] / (len(test) - defauts_test), 2)]


# ==============================================================================
entete_partie_8()
st.markdown("---")
st.header("8.2 Comparaison avec Yeh et Lien (2009), dans leurs propres métriques", anchor="yeh-lien")
st.markdown(f"""
Ce dataset vient de l'étude de **I-Cheng Yeh et Che-hui Lien (2009)**, qui comparait six méthodes pour repérer les clients à risque ([traduction en français]({TRADUCTION})). C'est le repère naturel du projet. L'étude ne publie ni rappel ni précision : seulement **deux mesures**, que cette page reprend telles quelles :
- le **taux d'erreur** : la part des clients mal classés, qu'ils soient déclarés en défaut à tort ou que leur défaut soit manqué ;
- le **ratio de surface** du graphique de lift : la qualité du tri, de 0 (au hasard) à 1 (tri parfait). Il se convertit directement en ROC AUC : ratio de surface = 2 × AUC − 1, soit un AUC de 0,77 pour le meilleur modèle de l'étude.
""")

# ------------------------------------------------------------------------------
st.markdown("""
**Le défi fixé au départ** (page d'accueil) : dépasser le score de référence de l'étude, un AUC de 0,77.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Avant tout chiffre : une comparaison qui ne peut pas être exacte", anchor="precautions")
st.markdown("""
- **L'objectif n'était pas le même.** L'étude de Yeh et Lien cherche d'abord à **estimer au mieux la probabilité de défaut** de chaque client, et à bien les trier. Mon étude, ce projet, cherche à **détecter** les défauts et à ranger les clients par niveau de risque, pour qu'une banque sache qui surveiller en priorité : ses modèles donnent plus de poids aux défauts, et leurs probabilités ne sont pas faites pour être lues telles quelles (page 6.6).
- **Les modèles ont progressé depuis.** L'étude a été publiée en 2009, mais menée bien avant : son texte parle des impayés dont le pic est « attendu » au troisième trimestre de 2006, et l'article est enregistré par l'éditeur dès la fin de 2007 (référence doi:10.1016/j.eswa.2007.12.020). Son meilleur modèle est donc un réseau de neurones de 2006-2007 ; le modèle du projet, CatBoost, appartient à une famille de modèles (le boosting d'arbres) devenue courante après l'étude, comme la validation croisée et le réglage automatique.
- **Les clients et les traitements diffèrent.** L'étude utilise un seul découpage entre entraînement et validation, et ne décrit ni ses réglages ni son traitement des données ; son article contient aussi des incohérences (25 000 clients annoncés, contre 30 000 dans le fichier). Le projet nettoie les données, retire des clients et mesure sur ses propres clients de test.

Les chiffres ci-dessous **situent** le projet face à l'étude ; ils ne permettent pas de dire lequel est meilleur au centième près.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Dans les métriques de l'étude", anchor="metriques")
st.markdown(f"""
Le projet est mesuré sur les **{nombre_fr(len(clients))} clients de la page 8.1**, qu'aucun de ses modèles n'a vus, dont {nombre_fr(hasard, 1)} % en défaut. Deux règles très simples, calculées sur les codifications d'origine, servent de repère : elles ne demandent ni nettoyage ni modèle.
""")
lignes = [[f"<b>Yeh et Lien : {nom}</b><br><small>autre échantillon, validation</small>", f"{nombre_fr(e * 100, 0)} %", nombre_fr(r, 2) if r != 0.536 else "0,536"]
          for nom, e, r in YEH]
lignes += [
    ["Personne n'est déclaré en défaut", f"{nombre_fr(taux_erreur(np.zeros(len(y), dtype=bool)), 1)} %", "0"],
    [f"Règle simple : au moins un retard (2 ou plus) sur les 6 mois<br><small>codifications d'origine</small>", f"{nombre_fr(taux_erreur(six_mois), 1)} %", nombre_fr(ratio_regle(six_mois), 2)],
    [f"Règle simple : la codification de la banque, 2 ou plus en septembre<br><small>codifications d'origine</small>", f"{nombre_fr(taux_erreur(banque), 1)} %", nombre_fr(ratio_regle(banque), 2)],
    ["<b>Règle du contentieux seule</b> (projet, sans modèle)", f"<b>{nombre_fr(taux_erreur(ctx), 1)} %</b>", nombre_fr(ratio_regle(ctx), 2)],
    ["<b>Système du projet</b> : règle, puis <code>ml_14</code><br><small>taux d'erreur avec le très haut risque, puis avec le haut risque</small>",
     f"<b>{nombre_fr(taux_erreur(paliers['tres_haut_risque']), 1)} %</b> ; {nombre_fr(taux_erreur(paliers['haut_risque']), 1)} %", f"<b>{nombre_fr(ratio_projet, 2)}</b>"],
    ["Modèle brut (23 variables d'origine, page 8.1)<br><small>autant de clients déclarés que le système du projet</small>",
     f"{nombre_fr(taux_erreur(meme_nombre_brut(int(paliers['tres_haut_risque'].sum()))), 1)} % ; {nombre_fr(taux_erreur(meme_nombre_brut(int(paliers['haut_risque'].sum()))), 1)} %",
     nombre_fr(ratio_brut, 2)],
]
tableau_html(["Approche", "Taux d'erreur", "Ratio de surface (qualité du tri)"], lignes, largeurs=[56, 22, 22])
st.caption(f"Yeh et Lien : Tableau 1 de l'étude, échantillon de validation ([traduction]({TRADUCTION})). Projet : calcul en direct. Pour une règle (oui / non), le ratio de surface vaut la part des défauts trouvés moins la part des bons clients signalés. Le taux d'erreur dépend du nombre de clients déclarés : l'étude ne dit pas à quel seuil elle le mesure ; ici, il est donné aux paliers du projet (seuils fixés sur l'entraînement, page 6.4).")
st.markdown(f"""
- **Pour trier les clients, le projet fait un peu mieux que l'étude** : un ratio de surface de {nombre_fr(ratio_projet, 2)}, contre 0,54 pour son meilleur modèle (un AUC d'environ {nombre_fr((ratio_projet + 1) / 2, 2)} contre 0,77). L'écart est faible, et attendu avec des modèles plus récents ; le modèle brut fait de même ({nombre_fr(ratio_brut, 2)}). Que l'écart reste si petit confirme que **la limite vient des données**, pas des modèles (page 6.5).
- **Pour le taux d'erreur, le projet est au même niveau, pas au-dessus** : environ {nombre_fr(taux_erreur(paliers['tres_haut_risque']), 0)} %, comme le réseau de neurones de l'étude (17 %). Cette mesure favorise les systèmes qui déclarent peu de clients : déclarer tout le monde sain donne déjà {nombre_fr(hasard, 0)} % d'erreur, et chercher plus de défauts l'augmente (avec le haut risque, {nombre_fr(taux_erreur(paliers['haut_risque']), 0)} %). L'étude elle-même la jugeait « insuffisante » sur des données déséquilibrées.
- **Sans aucun modèle, la règle du contentieux atteint déjà le taux d'erreur de l'étude** ({nombre_fr(taux_erreur(ctx), 1)} %), tout comme la codification de septembre de la banque. Une règle plus large, comme « au moins un retard sur les 6 mois », trouve bien plus de défauts, d'où un meilleur ratio de surface, mais elle fait plus d'erreurs que de ne déclarer personne : ses fausses alertes sont trop nombreuses.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Et la première itération du machine learning ?", anchor="premiere-iteration")
st.markdown(f"""
Avant l'étude du contentieux, la première itération du machine learning avait atteint un meilleur tri sur le même périmètre (page 6.1). Son meilleur modèle, entraîné sur le même périmètre **incluant la population contentieuse**, pas encore définie à l'époque, est comparé ici à la règle du contentieux sur le **test de la partie 5** ({nombre_fr(len(test))} clients, dont {nombre_fr(defauts_test)} en défaut ; un autre tirage que les clients de la section 2).
""")
tableau_html(["Approche", "Clients prédits en défaut", "Défauts trouvés", "Précision", "Part des défauts trouvés", "Taux d'erreur", "Ratio de surface"], [
    ligne_test("<b>Règle du contentieux</b>", REGLE_TEST),
    ligne_test("<b>Machine learning, première itération</b><br><small>meilleur modèle du périmètre (S12_6, CatBoost), entraîné sur le périmètre incluant la population contentieuse</small>", ML_S126, ML_S126["auc"]),
], largeurs=[30, 12, 11, 11, 12, 12, 12])
st.caption(f"Règle du contentieux : calcul en direct. Première itération : modèle enregistré de l'archive, rechargé et appliqué hors du site au même test, repris tel quel ; ce modèle n'est pas déployé avec le site ([tableau de suivi de la première itération]({TABLEAU_ML_1})).")
st.markdown(f"""
- **Le modèle de la première itération avait déjà « trouvé » le contentieux** : il prédit en défaut tous les clients que la règle place au contentieux, et retrouve donc les mêmes défauts. Il en ajoute {nombre_fr(ML_S126['vp'] - REGLE_TEST['vp'])}, au prix de {nombre_fr(ML_S126['fp'] - REGLE_TEST['fp'])} fausses alertes supplémentaires : sa précision tombe à {nombre_fr(ML_S126['vp'] / ML_S126['predits'] * 100, 1)} %.
- C'est ce qui expliquait l'effet nul de la variable de contentieux ajoutée à ce modèle (page 6.1) : il repérait déjà ces clients par leurs codifications. Son bon tri venait **en grande partie du contentieux**, facile à repérer ; sans lui, l'AUC des modèles passe d'environ 0,78 à environ 0,71, quel que soit le modèle ([hypothèses et conclusions]({HYPOTHESES}), H11). Les clients restants sont plus difficiles à départager (page 6.5).
""")

# ------------------------------------------------------------------------------
st.subheader("4. Défi relevé ?", anchor="defi")
st.markdown(f"""
**Oui, de peu.** Le système du projet trie les clients avec un AUC d'environ {nombre_fr((ratio_projet + 1) / 2, 2)} (ratio de surface de {nombre_fr(ratio_projet, 2)}), contre 0,77 pour le meilleur modèle de l'étude. L'écart est petit, attendu avec des modèles plus récents, et la comparaison reste indicative : autres clients, autre objectif.

Le défi a surtout montré autre chose : **tous les modèles plafonnent autour de 0,78 à 0,80 d'AUC**, quelle que soit l'approche, jusqu'au modèle lancé sur les données brutes. Dépasser nettement l'étude n'était pas possible avec ces données.

**La vraie différence est ailleurs** : une règle métier, sans modèle, atteint déjà le taux d'erreur de l'étude, et le projet dit ce que l'étude ne publiait pas, la précision et la part des défauts trouvés à chaque niveau de risque (page 8.1), c'est-à-dire ce qu'une banque a besoin de savoir pour décider jusqu'où signaler.
""")

st.info(f"""
**Défi relevé, de peu** : un AUC d'environ {nombre_fr((ratio_projet + 1) / 2, 2)} contre 0,77 pour l'étude de 2009, sur d'autres clients et avec un autre objectif. Tous les modèles plafonnant autour de 0,78 à 0,80, la limite vient des données ; l'apport du projet est une règle métier qui atteint seule le taux d'erreur de l'étude, et des niveaux de risque dont on connaît la précision.
""")
