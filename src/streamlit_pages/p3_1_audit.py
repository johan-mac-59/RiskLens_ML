from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 3 : COMPRENDRE LE JEU DE DONNÉES
# Les données d'origine ne sont pas dans le dépôt : les résultats sont repris
# tels quels des notebooks d'origine, avec leur source.
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/src"

entete_partie_3()

# ------------------------------------------------------------------------------
# 3.1 UN FICHIER COMPLET, MAIS DES VALEURS HORS NOMENCLATURE
# ------------------------------------------------------------------------------
st.markdown("---")
st.header("3.1 Audit : un fichier complet, mais des valeurs anormales", anchor="audit")

st.markdown(f"""
La première étape est l'**audit** du fichier d'origine ([01_01_audit.ipynb]({GH}/01_01_audit.ipynb)) : on le compare à sa documentation officielle ([dataset_dictionary.md](https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/dataset_dictionary.md)), qui prévoit les valeurs suivantes.

| Colonne | Valeurs documentées |
|---|---|
| Niveau d'études (`EDUCATION`) | 1 = master ou doctorat, 2 = licence, 3 = baccalauréat, 4 = autres |
| Statut marital (`MARRIAGE`) | 1 = marié, 2 = célibataire, 3 = autres |
| Codification de paiement (`PAY_1` à `PAY_6`) | -1 = paiement à temps ; 1 à 9 = nombre de mois de retard |

✅ **Premier constat : le fichier est complet.** Aucune ligne en double, aucun identifiant en double, aucune valeur manquante.
""")

st.subheader("Le résumé statistique de l'audit fait apparaître des valeurs anormales")
st.markdown(f"Minimum, médiane et maximum dans le fichier d'origine (30 000 clients), repris du résumé statistique de l'audit ([01_01_audit.ipynb]({GH}/01_01_audit.ipynb), cellule 2) :")
st.dataframe(pd.DataFrame({
    "Colonne": ["Âge (AGE)", "Niveau d'études (EDUCATION)", "Statut marital (MARRIAGE)", "Codifications de paiement (PAY_1 à PAY_6)",
                "Plafond (LIMIT_BAL)", "Factures (BILL_AMT1 à BILL_AMT6)", "Paiements (PAY_AMT1 à PAY_AMT6)"],
    "Minimum": ["21", "0", "0", "-2", "10 000", "-339 603", "0"],
    "Médiane": ["34", "2", "2", "0", "140 000", "17 071 à 22 382", "1 500 à 2 100"],
    "Maximum": ["79", "6", "3", "8", "1 000 000", "1 664 089", "1 684 259"],
    "Ce qui est anormal": [
        "— (âges cohérents, de 21 à 79 ans)",
        "0, 5 et 6 sont absents de la documentation (1 à 4)",
        "0 est absent de la documentation (1 à 3)",
        "-2 est absent de la documentation (-1, puis 1 à 9)",
        "—",
        "des factures négatives ; une facture dépasse le plus haut plafond",
        "un paiement dépasse le plus haut plafond, à plusieurs centaines de fois la médiane",
    ],
}), hide_index=True, width="stretch")
st.caption("Montants en NT\\$. Pour les factures et les paiements, la médiane varie selon le mois : la plage indiquée va du mois le plus bas au plus haut.")

st.subheader("Le niveau d'études et le statut marital : quelques valeurs inconnues")
st.markdown("Répartition dans le fichier d'origine, avant nettoyage :")

col_edu, col_mar = st.columns(2)
with col_edu:
    st.dataframe(pd.DataFrame({
        "Niveau d'études": ["0 (hors nomenclature)", "1", "2", "3", "4", "5 (hors nomenclature)", "6 (hors nomenclature)"],
        "Clients": [14, 10585, 14030, 4917, 123, 280, 51],
        "Part": ["0,05 %", "35,28 %", "46,77 %", "16,39 %", "0,41 %", "0,93 %", "0,17 %"],
    }), hide_index=True, width="stretch")
with col_mar:
    st.dataframe(pd.DataFrame({
        "Statut marital": ["0 (hors nomenclature)", "1", "2", "3"],
        "Clients": [54, 13659, 15964, 323],
        "Part": ["0,18 %", "45,53 %", "53,21 %", "1,08 %"],
    }), hide_index=True, width="stretch")

st.subheader("Les codifications de paiement : -2 et 0, absentes de la documentation, dominent")
st.markdown(f"""
La documentation ne prévoit ni **-2** ni **0** pour la codification de paiement. Pourtant, **0 est de loin la codification la plus fréquente**, et **-2 est loin d'être marginale**.
Répartition par mois dans le fichier d'origine ([05_04_EDA_codification1.ipynb]({GH}/05_04_EDA_codification1.ipynb), section 1) :
""")

# Parts (%) reprises de 05_04_EDA_codification1, section 1 (30 000 clients, fichier d'origine)
mois = ["M-6 (avril)", "M-5 (mai)", "M-4 (juin)", "M-3 (juil.)", "M-2 (août)", "M-1 (sept.)"]
repartition = pd.DataFrame({
    -2: [16.32, 15.15, 14.49, 13.62, 12.61, 9.20],
    -1: [19.13, 18.46, 18.96, 19.79, 20.17, 18.95],
    0: [54.29, 56.49, 54.85, 52.55, 52.43, 49.12],
    1: [0.00, 0.00, 0.01, 0.01, 0.09, 12.29],
    2: [9.22, 8.75, 10.53, 12.73, 13.09, 8.89],
    3: [0.61, 0.59, 0.60, 0.80, 1.09, 1.07],
}, index=mois)
familles = {
    "-2 (absente de la documentation)": repartition[-2],
    "0 (absente de la documentation)": repartition[0],
    "-1": repartition[-1],
    "1": repartition[1],
    "2 et plus": 100 - repartition[[-2, -1, 0, 1]].sum(axis=1),
}
couleurs = [COULEURS_CODIF["-2"], COULEURS_CODIF["0"], COULEURS_CODIF["-1"], COULEURS_CODIF["1"], COULEURS_CODIF["2 et plus"]]

fig_codif = go.Figure()
for (nom, valeurs), couleur in zip(familles.items(), couleurs):
    fig_codif.add_trace(go.Bar(x=mois, y=valeurs, name=nom, marker_color=couleur,
                               text=[f"{v:.1f} %" if v >= 3 else "" for v in valeurs], textposition="inside"))
fig_codif.update_layout(barmode="stack", yaxis_title="Part des clients (%)", xaxis_title="Mois",
                        legend_title="Codification", height=450, margin=dict(t=30))
st.plotly_chart(fig_codif, width="stretch")

st.markdown("""
Autres constats de l'enquête :
- **9 821 clients** sont codifiés **0 sur les 6 mois**, et **2 109 clients -2 sur les 6 mois** (EDA_lab, cellules 12 et 16 ; chiffres identiques sur les 30 000 clients du fichier d'origine) : ces valeurs non documentées ne sont pas des cas isolés.
- **Le nom des colonnes diffère aussi** : le dictionnaire du dataset appelle `PAY_0` la codification de septembre. Elle est renommée `PAY_1` dans ce projet, pour suivre la numérotation des factures (`BILL_AMT1`) et des paiements (`PAY_AMT1`).
""")

st.subheader("Des factures négatives")
st.markdown(f"Part des factures négatives selon le mois, dans le fichier d'origine ([01_01_audit.ipynb]({GH}/01_01_audit.ipynb), cellule 8) :")
st.dataframe(pd.DataFrame(
    [["2,29 %", "2,18 %", "2,25 %", "2,18 %", "2,23 %", "1,97 %"]],
    columns=mois, index=["Factures négatives"]
), width="stretch")
st.markdown("Ces montants négatifs sont étudiés avec les autres montants (page « 3.2 Les montants »).")

st.subheader("Des paiements sans commune mesure avec les factures")
st.markdown(f"""
On compare chaque paiement à la facture qu'il règle : le paiement d'un mois (`PAY_AMTn`) rembourse la facture du mois précédent (`BILL_AMT(n+1)`). Ce **ratio de paiement** (montant payé divisé par la facture à régler, en %), calculé quand une facture est due, atteint des valeurs démesurées (définitions de l'EDA_lab, [05_01_EDA_lab.ipynb]({GH}/05_01_EDA_lab.ipynb), cellules 52, 55 et 58 ; calcul refait sur les 30 000 clients, l'EDA_lab ayant mis de côté les 4 clients aux paiements géants) :
""")
st.dataframe(pd.DataFrame({
    "Mois du paiement": ["M-5 (mai)", "M-4 (juin)", "M-3 (juil.)", "M-2 (août)", "M-1 (sept.)"],
    "Ratio de paiement médian": ["5,59 %", "5,17 %", "6,17 %", "7,75 %", "7,83 %"],
    "Ratio de paiement maximum": ["69 066 %", "12 971 %", "444 433 %", "500 100 %", "444 433 %"],
}), hide_index=True, width="stretch")
st.markdown("""
Sur l'ensemble des mois, le ratio de paiement médian est de 6,57 %, mais **90 clients** ont au moins un mois où ils paient plus de 10 fois leur facture (ratio supérieur à 1 000 %), et le maximum atteint **500 100 %**.

Des paiements arrivent même **alors qu'aucune facture n'était due** (facture nulle ou négative) : **692 clients** sont concernés au moins une fois, soit 2,31 % des clients :
""")
st.dataframe(pd.DataFrame(
    [[177, 178, 171, 161, 146]],
    columns=["M-5 (mai)", "M-4 (juin)", "M-3 (juil.)", "M-2 (août)", "M-1 (sept.)"],
    index=["Paiements sur une facture nulle ou négative"]
), width="stretch")

st.subheader("Des clients sans facture, pourtant notés en défaut")
st.markdown(f"""
La facture de fin septembre (`BILL_AMT1`) est celle à payer en octobre, le mois sur lequel porte le défaut de paiement à prédire. Pourtant, des clients qui n'ont rien à payer en octobre sont notés en défaut, plus souvent même que l'ensemble des clients ([05_01_EDA_lab.ipynb]({GH}/05_01_EDA_lab.ipynb), cellules 40, 42 et 43). L'EDA_lab calcule sur 29 996 clients, après le retrait de 4 clients aux paiements géants ; ces 4 clients ont tous des factures positives, les chiffres sont donc identiques sur les 30 000 clients du fichier d'origine :
""")
st.dataframe(pd.DataFrame({
    "Situation": ["Facture de septembre nulle ou négative", "Factures négatives sur les 6 mois", "Factures nulles sur les 6 mois", "Ensemble des clients"],
    "Clients": [2598, 88, 866, 30000],
    "Notés en défaut": [643, 26, 317, 6636],
    "Taux de défaut": ["24,75 %", "29,55 %", "36,61 %", "22,12 %"],
}), hide_index=True, width="stretch")
st.caption("Taux de défaut descriptifs : ils ne servent à fixer aucune règle.")

st.subheader("Et maintenant ?")
st.markdown("""
J'ai ouvert ce jeu de données en pensant trouver un terrain propre. Je pensais que les codifications respecteraient leur documentation, et que les quelques anomalies se régleraient par des calculs : un filtre, une correction, une moyenne. Le constat est tout autre. Le fichier est complet, mais il ne dit pas ce qu'il semble dire. Des codifications absentes de la documentation concernent la majorité des clients. Des paiements dépassent de loin les factures, ou arrivent alors que rien n'était dû. Et des clients qui n'avaient rien à payer sont pourtant notés en défaut.

Corriger le niveau d'études et le statut marital était simple. Pour le reste, la tentation aurait été de supprimer tout ce qui dérange. C'est l'inverse que j'ai fait. Ces incohérences ne sont pas du bruit à effacer : elles sont la trace d'un fonctionnement réel. Pour prédire le risque, il fallait d'abord comprendre tout un système :
- **un pays, à une époque donnée** : Taïwan en 2005, en pleine crise des cartes de crédit, avec un régulateur qui resserre brutalement l'accès au crédit ;
- **un système bancaire** : des banques en concurrence pour distribuer des cartes, puis confrontées à une vague d'impayés ;
- **le système d'information d'une banque** : quand et comment une codification est mise à jour, ce que reflète un relevé mensuel, ce qu'un retard d'enregistrement peut produire ;
- **un moyen de paiement** : la carte de crédit de l'époque, avec des factures souvent réglées en espèces en supérette et des paiements comptabilisés avec un temps de retard.

J'ai donc quitté les mathématiques pour l'enquête. Je me suis renseigné sur l'époque, la crise et le fonctionnement des cartes à Taïwan, puis j'ai confronté chaque hypothèse aux données, en revenant à des cas concrets quand les chiffres seuls ne suffisaient pas.

La suite raconte cette enquête : ce que révèlent les montants (page « 3.2 Les montants ») et les codifications (page « 3.3 Les codifications ») quand on les lit en tenant compte de ce contexte, puis les règles qui en sont sorties (page « 3.4 Décisions »).
""")
