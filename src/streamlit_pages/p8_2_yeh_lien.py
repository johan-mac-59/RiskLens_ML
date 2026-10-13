import json
from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 8.2 : COMPARAISON AVEC YEH ET LIEN (2009), DANS LEURS PROPRES MÉTRIQUES
# Métriques de l'étude (Tableau 1) : taux d'erreur et ratio de surface du graphique de lift (= 2 × ROC AUC − 1).
# Trois niveaux de comparaison : l'étude d'origine (fichier brut, un découpage) ; le périmètre global (le même fichier
# brut, chaque client noté par un modèle qui ne l'a pas vu : lab_ML/comparatif_global/essai_jeu_de_base.ipynb et
# essai_jeu_de_base_deux_populations.ipynb, chiffres repris tels quels, les probabilités ne sont pas dans le dépôt) ;
# le périmètre du projet (les 5 441 clients de la démo 1, jamais vus, calcul en direct, commun.py).
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
ARTICLE = "https://doi.org/10.1016/j.eswa.2007.12.020"
RESUME = f"{GH_RACINE}/docs/resume_yeh_lien_2009.md"
TABLEAU_ML_1 = f"{GH_RACINE}/lab_ML/1ere_iteration/tableau_ML.md"
ESSAI_BASE = f"{GH_RACINE}/lab_ML/comparatif_global/essai_jeu_de_base.ipynb"
ESSAI_BASE_DEUX = f"{GH_RACINE}/lab_ML/comparatif_global/essai_jeu_de_base_deux_populations.ipynb"

# Yeh et Lien (2009), Tableau 1, échantillon de validation : (méthode, taux d'erreur, ratio de surface)
YEH = [("Réseau de neurones (meilleur modèle)", 0.17, 0.54), ("Arbre de classification", 0.17, 0.536),
       ("K plus proches voisins", 0.16, 0.45), ("Régression logistique", 0.18, 0.44)]

# Périmètre global : les 30 000 clients du fichier brut, décisions hors pli (validation croisée à 5 plis), au seuil de la
# règle marginale (au plus 1 bon client signalé pour 1 défaut, à la marge, ce qui revient à chercher le taux d'erreur le plus bas).
# essai_jeu_de_base, sections 4 et « Comparaison avec l'étude d'origine » ; essai_jeu_de_base_deux_populations, section 5.
# (approche, taux d'erreur, ratio de surface)
GLOBAL = [
    ("Personne n'est déclaré en défaut", 0.221, 0.0),
    ("Codification de la banque seule (2 ou plus en septembre)", 0.180, 0.308),
    ("Codification de la banque, puis un modèle pour les autres clients (CatBoost)", 0.181, 0.564),
    ("Un modèle sur les 23 variables d'origine, tous les clients (CatBoost)", 0.182, 0.569),
]

# ------------------------------------------------------------------------------
# Périmètre du projet : les mêmes clients que la page 8.1, mesurés comme dans l'étude
# ------------------------------------------------------------------------------
clients = systemes_sur_clients_demo()
y = clients["dpnm"].values.astype(bool)
hasard = y.mean() * 100
bornes = json.loads((BASE_DIR / "lab_ML" / "demo_ML" / "bornes_niveaux.json").read_text(encoding="utf-8"))
regles = clients["regles"].values
proba_modele = np.nan_to_num(clients["proba_modele"].values)   # pas de probabilité pour les clients des règles
autres = ~regles


def taux_erreur(declares):
    """Part des clients mal classés : bons clients déclarés en défaut, et défauts non déclarés."""
    return (declares != y).mean() * 100


def ratio_regle(declares):
    """Ratio de surface d'une règle (oui / non) : part des défauts trouvés − part des bons clients signalés (= 2 × ROC AUC − 1)."""
    return declares[y].mean() - declares[~y].mean()


def meme_nombre_brut(nombre):
    """Les clients les mieux notés par le modèle brut, autant que le système du projet en déclare."""
    declares = np.zeros(len(y), dtype=bool)
    declares[np.argsort(-clients["score_brut"].values, kind="stable")[:nombre]] = True
    return declares


ratio_projet = 2 * aire_roc(y, score_systeme_projet(clients)) - 1
ratio_brut = 2 * aire_roc(y, clients["score_brut"]) - 1
paliers = {cle: regles | (proba_modele >= bornes[cle]) for cle in ("tres_haut_risque", "haut_risque")}
# Le modèle seul, sur les autres clients (hors des deux règles) : ce qui reste à trier une fois les règles appliquées
auc_modele_seul = aire_roc(y[autres], proba_modele[autres])

# ==============================================================================
entete_partie_8()
st.markdown("---")
st.header("8.2 Comparaison avec Yeh et Lien (2009), dans leurs propres métriques", anchor="yeh-lien")
st.markdown(f"""
Ce dataset vient de l'étude de **I-Cheng Yeh et Che-hui Lien (2009)**, qui comparait six méthodes pour repérer les clients à risque ([article]({ARTICLE}), [résumé en français]({RESUME})). C'est le repère naturel du projet. L'étude ne publie ni rappel ni précision : seulement **deux mesures**, que cette page reprend telles quelles :
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
st.subheader("2. Dans les métriques de l'étude, à trois niveaux", anchor="metriques")
st.markdown("""
Pour comparer ce qui est comparable, les résultats sont donnés à trois niveaux, du plus proche de l'étude au plus proche du projet :
- **l'étude d'origine** : le fichier brut, ses 30 000 clients, un seul découpage ;
- **le périmètre global** : **le même fichier brut**, les mêmes 30 000 clients, sans nettoyage ; chaque client est noté par un modèle qui ne l'a pas vu (validation croisée à 5 plis). Seul le découpage diffère de l'étude : c'est la comparaison la plus directe ;
- **le périmètre du projet** : les clients gardés par le nettoyage qui ont une dette en septembre (page 8.1, sous-partie 3), mesurés sur les clients de la démo 1, qu'aucun modèle n'a vus.
""")
lignes = [[("<b>Étude d'origine</b><br><small>fichier brut, 30 000 clients, un découpage</small>" if i == 0 else ""),
           f"Yeh et Lien : {nom}", f"{nombre_fr(e * 100, 0)} %", nombre_fr(r, 2) if r != 0.536 else "0,536"] for i, (nom, e, r) in enumerate(YEH)]
lignes += [[("<b>Périmètre global</b><br><small>même fichier brut, 30 000 clients, 5 plis</small>" if i == 0 else ""),
            nom, f"{nombre_fr(e * 100, 1)} %", nombre_fr(r, 2) if r else "0"] for i, (nom, e, r) in enumerate(GLOBAL)]
lignes += [
    [f"<b>Périmètre du projet</b><br><small>{nombre_fr(len(clients))} clients de la démo 1, jamais vus</small>",
     "Personne n'est déclaré en défaut", f"{nombre_fr(taux_erreur(np.zeros(len(y), dtype=bool)), 1)} %", "0"],
    ["", "<b>Règles métier seules</b> (population en incident, retard imminent)", f"<b>{nombre_fr(taux_erreur(regles), 1)} %</b>", nombre_fr(ratio_regle(regles), 2)],
    ["", "<b>Système du projet</b> : règles, puis <code>ml_17</code><br><small>taux d'erreur avec le très haut risque, puis avec le haut risque</small>",
     f"<b>{nombre_fr(taux_erreur(paliers['tres_haut_risque']), 1)} %</b> ; {nombre_fr(taux_erreur(paliers['haut_risque']), 1)} %", f"<b>{nombre_fr(ratio_projet, 2)}</b>"],
    ["", "Modèle brut (23 variables d'origine, page 8.1)<br><small>autant de clients déclarés que le système du projet</small>",
     f"{nombre_fr(taux_erreur(meme_nombre_brut(int(paliers['tres_haut_risque'].sum()))), 1)} % ; {nombre_fr(taux_erreur(meme_nombre_brut(int(paliers['haut_risque'].sum()))), 1)} %",
     nombre_fr(ratio_brut, 2)],
]
tableau_html(["Niveau", "Approche", "Taux d'erreur", "Ratio de surface (qualité du tri)"], lignes, largeurs=[22, 44, 16, 18])
st.caption(f"Étude d'origine : Tableau 1, échantillon de validation ([article]({ARTICLE}), [résumé en français]({RESUME})). Périmètre global : chiffres repris tels quels des essais sur le fichier brut ([un modèle sur tous les clients]({ESSAI_BASE}) ; [codification de la banque, puis un modèle]({ESSAI_BASE_DEUX})), au seuil qui ne signale un client que s'il a au moins une chance sur deux d'être en défaut, ce qui revient à chercher le taux d'erreur le plus bas ; les probabilités ne sont pas dans le dépôt. Périmètre du projet : calcul en direct ; le taux d'erreur y est donné aux paliers du projet (seuils fixés sur l'entraînement, page 6.4). Pour une règle (oui / non), le ratio de surface vaut la part des défauts trouvés moins la part des bons clients signalés.")
st.markdown(f"""
- **Sur le même fichier que l'étude, le tri est un peu meilleur** : un ratio de surface de 0,56 à 0,57, contre 0,54 pour son meilleur modèle, que les clients à risque soient séparés par la codification de la banque ou non. L'écart est faible, et attendu avec des modèles plus récents.
- **Sur le périmètre du projet, le tri est du même ordre** : {nombre_fr(ratio_projet, 2)} pour le système du projet, {nombre_fr(ratio_brut, 2)} pour le modèle brut, sur les mêmes clients. Le nettoyage et le travail du projet ne déplacent pas ce niveau (page 8.1, sous-partie 3) : **la limite vient des données**, pas des modèles (page 6.5).
- **Pour le taux d'erreur, tous les niveaux sont du même ordre, pas au-dessus de l'étude** : environ 18 %, comme la régression logistique de l'étude, un peu au-dessus de ses meilleures méthodes (16 à 17 %). Cette mesure favorise les systèmes qui déclarent peu de clients : déclarer tout le monde sain donne déjà environ 22 % d'erreur, et chercher plus de défauts l'augmente (avec le haut risque, {nombre_fr(taux_erreur(paliers['haut_risque']), 0)} %). L'étude elle-même la jugeait « insuffisante » sur des données déséquilibrées.
- **Sans aucun modèle, des règles sur les codifications sont déjà au niveau de l'étude en taux d'erreur** : la codification de la banque sur le fichier brut (18,0 %), les règles métier sur le périmètre du projet ({nombre_fr(taux_erreur(regles), 1)} %). Elles trient mal en revanche (ratio de surface bas), puisqu'elles ne rangent pas les clients qu'elles ne retiennent pas.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Et la première itération du machine learning ?", anchor="premiere-iteration")
st.markdown(f"""
La première itération (page 6.1) semblait mieux trier les clients que le modèle actuel. Mais elle apprenait et se mesurait sur tous les clients du périmètre, **populations à risque comprises**, faciles à repérer. Elle se compare donc au **système complet** du projet, qui trie lui aussi ces populations, et non à son modèle seul : sur les clients de la démo, le système complet trie avec un AUC d'environ {nombre_fr((ratio_projet + 1) / 2, 2)}.

Une fois les deux populations à risque confiées aux règles, **le modèle seul, sur les autres clients, ne trie plus qu'avec un AUC d'environ {nombre_fr(auc_modele_seul, 2)}** : le bon tri d'ensemble vient en grande partie de ces populations. Les clients restants sont plus difficiles à départager (page 6.5).
""")
st.caption(f"Système complet et modèle seul : calcul en direct sur les clients de la démo 1. Première itération : [tableau de suivi]({TABLEAU_ML_1}) ; ses modèles ne sont pas déployés avec le site.")

# ------------------------------------------------------------------------------
st.subheader("4. Défi relevé ?", anchor="defi")
st.markdown(f"""
**Oui, de peu.** Sur le même fichier que l'étude, le tri atteint un AUC d'environ 0,78, et le système du projet un AUC d'environ {nombre_fr((ratio_projet + 1) / 2, 2)} sur ses clients de test, contre 0,77 pour le meilleur modèle de l'étude. L'écart est petit, attendu avec des modèles plus récents, et la comparaison reste indicative : autre découpage, autre objectif.

Le défi a surtout montré autre chose : **tous les modèles plafonnent autour de 0,78 d'AUC**, quelle que soit l'approche, jusqu'au modèle lancé sur les données brutes. Dépasser nettement l'étude n'était pas possible avec ces données.

**La vraie différence est ailleurs** : des règles métier, sans modèle, sont déjà au niveau de l'étude en taux d'erreur, et le projet dit ce que l'étude ne publiait pas, la précision et la part des défauts trouvés à chaque niveau de risque (page 8.1), c'est-à-dire ce qu'une banque a besoin de savoir pour décider jusqu'où signaler.
""")

st.info(f"""
**Défi relevé, de peu** : un AUC d'environ 0,78 sur le même fichier que l'étude, et d'environ {nombre_fr((ratio_projet + 1) / 2, 2)} pour le système du projet sur ses clients de test, contre 0,77 pour l'étude de 2009. Tous les modèles plafonnant autour de 0,78, la limite vient des données ; l'apport du projet est des règles métier, au niveau de l'étude en taux d'erreur sans aucun modèle, et des niveaux de risque dont on connaît la précision.
""")
