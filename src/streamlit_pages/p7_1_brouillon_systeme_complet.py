from streamlit_pages.commun import *

# ==============================================================================
# BROUILLON POUR LA PARTIE 7.1 (pas encore dans le menu)
# Section retirée de la page 6.4 le 07/10/2026, hors sujet sur une page consacrée au modèle : la règle du
# contentieux et le modèle ensemble, sur tout le périmètre, niveau par niveau (système complet).
# À intégrer à la page 7.1 quand elle sera rédigée. Chiffres repris tels quels de
# lab_ML/evaluation_finale_test.ipynb, section 6 (mêmes NIVEAUX que la page 6.4).
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
EVALUATION = f"{GH_RACINE}/lab_ML/evaluation_finale_test.ipynb"

df = load_data()
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
NIVEAUX = [
    ("Contentieux", "retiré avant le machine learning, prédit en défaut par la règle", 3004, 2117),
    ("Haut risque", "coût en fausses alertes moyen", 2809, 1161),
    ("Risque modéré", "coût en fausses alertes élevé", 5628, 1158),
    ("Risque faible", "non prédit en défaut", 15761, 1536),
]
total_clients = sum(n[2] for n in NIVEAUX)
total_defauts = sum(n[3] for n in NIVEAUX)
assert (len(s12), int(s12["dpnm"].sum())) == (total_clients, total_defauts)
taux_global = total_defauts / total_clients * 100

# ------------------------------------------------------------------------------
st.subheader("Jusqu'où signaler, contentieux compris", anchor="jusqu-ou")
cumul_clients, cumul_defauts, etapes = 0, 0, []
# Le risque faible n'est pas signalé : on s'arrête au seuil du taux de rappel minimal
for niveau, _, clients, defauts in NIVEAUX[:3]:
    cumul_clients += clients
    cumul_defauts += defauts
    etapes.append((niveau, cumul_defauts / total_defauts * 100, cumul_defauts / cumul_clients * 100, cumul_clients / total_clients * 100))
libelles = ["Contentieux<br>seul", "+ haut risque", "+ risque modéré<br>(rappel minimal)"]

col_graphe, col_texte = st.columns(2, vertical_alignment="center")
with col_graphe:
    st.plotly_chart(figure_detection(libelles, [e[1] for e in etapes], [e[2] for e in etapes], [e[3] for e in etapes], taux_global),
                    width='stretch')
with col_texte:
    st.markdown(f"""
Sur tout le portefeuille, on signale d'abord le contentieux, puis on descend d'un niveau à la fois.

- **Le contentieux seul** trouve environ **un tiers des défauts**, avec une précision de **sept sur dix**, en signalant {nombre_fr(etapes[0][3], 0)} % des clients.
- **Avec le haut risque**, plus de la moitié des défauts sont trouvés, et plus d'un client signalé sur deux est en défaut.
- **Avec le risque modéré** (le seuil du taux de rappel minimal), environ **trois quarts des défauts** sont trouvés, mais en signalant {nombre_fr(etapes[2][3], 0)} % des clients : la précision tombe à environ quatre sur dix.
- **Le risque faible n'est pas signalé** : il garde environ un quart des défauts, que le modèle ne sait pas repérer. Aller les chercher demanderait de signaler bien plus de clients, pour une précision qui se rapproche du hasard (page 6.4, section 3).

Chaque niveau ajouté rapporte de moins en moins de défauts par client signalé. **Jusqu'où signaler est un choix de la banque**, selon ce que lui coûte une fausse alerte face à un défaut manqué.
""")
st.caption(f"Valeurs cumulées : chaque étape ajoute un niveau aux précédents ; barres : part de tous les défauts détectés ; courbe : précision des clients signalés. Même périmètre que le tableau des niveaux de risque de la page 6.4. Source : [évaluation finale]({EVALUATION}), section 6.")
