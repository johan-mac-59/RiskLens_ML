from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 6.5 : POURQUOI LE MODÈLE PLAFONNE
# Un plafond quoi qu'on fasse, un tiers des défauts qui ressemblent à de bons clients (analyse des défauts manqués),
# et l'explication la plus probable : la cible suit le statut posé par la banque (hypothèse, définition non documentée).
# Profils des groupes repris tels quels de lab_ML/analyse_defauts_manques.ipynb (sections 2 à 4) : les probabilités
# hors pli ne sont pas dans le dépôt. Indices sur la cible : calculés en direct sur le dataset (portefeuille nettoyé,
# contentieux à M), sauf la codification de retard sur une dette nulle, qui porte sur les données d'origine
# (lab_ML/controles_cible.ipynb, section 3).
# Le poids du comportement face aux codifications (H6) est gardé pour la partie 8 (conclusion).
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
DEFAUTS_MANQUES = f"{GH_RACINE}/lab_ML/analyse_defauts_manques.ipynb"
CONTROLES_CIBLE = f"{GH_RACINE}/lab_ML/controles_cible.ipynb"
HYPOTHESES = f"{GH_RACINE}/docs/hypotheses_et_conclusions.md"

df = load_data()
au_ctx = df[(df["FLAG_CTX"] == 1) & (df["MOIS_SORTIE_CTX"] == -1)]
sans_dette = df[df["BILL_AMT1"] <= 0]
ctx_qui_paie = au_ctx[(au_ctx["PAY_AMT1"] > 0) & (au_ctx["PAY_AMT2"] > 0)]
# Clients actifs (S12), avec et sans le contentieux à M : même population, seul le contentieux change
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
s12_hors_ctx = s12[~((s12["FLAG_CTX"] == 1) & (s12["MOIS_SORTIE_CTX"] == -1))]
utilisation = s12["BILL_AMT1"] / s12["LIMIT_BAL"] * 100
# Liens de l'exploration (partie 4) : (lien, libellé du groupe le moins risqué, filtre, libellé du plus risqué, filtre, verdict)
LIENS = [
    ("Type d'usage de la carte (page 4.3)", "paiement comptant", s12["TYPE_USAGE"] == "Paiement comptant",
     "crédit lent", s12["TYPE_USAGE"] == "Crédit lent", "presque effacé"),
    ("Utilisation du plafond en septembre (page 4.2)", "moins de 30 %", utilisation < 30,
     "90 % et plus", utilisation >= 90, "réduit"),
    ("Plafond (page 4.2)", "200 000 à 500 000 NT$", s12["LIMIT_BAL"] > 200000,
     "50 000 NT$ ou moins", s12["LIMIT_BAL"] <= 50000, "se maintient"),
    ("Retards passés (page 4.6)", "aucun mois en retard", s12["CUMUL_INCIDENT"] == 0,
     f"au moins un mois en retard ({codif('2')} ou plus)", s12["CUMUL_INCIDENT"] >= 1, "diminue, mais reste le plus fort"),
]

entete_partie_6()
st.markdown("---")
st.header("6.5 Pourquoi le modèle plafonne : une part des défauts ne s'annonce pas dans les données", anchor="plafond")

# ------------------------------------------------------------------------------
st.subheader("1. Un plafond, quoi qu'on fasse", anchor="constat")
st.markdown("""
Les pages précédentes ont montré le même plafond sous plusieurs angles :
- **ni les variables** construites pendant l'exploration, **ni des réglages élargis**, ni la version à 54 variables ne font sortir les modèles de la zone d'incertitude (page 6.3) ; des modèles plus puissants, sans frein contre le surapprentissage, ne font pas mieux non plus ;
- **même la tête de liste reste incertaine** : les clients que le modèle juge les plus risqués ne font défaut qu'une fois sur deux, et la précision descend ensuite presque en ligne droite (page 6.4). Le modèle ne trouve aucun groupe de clients dont il soit presque sûr.

La question devient donc : **le plafond vient-il des modèles, ou des données ?** Pour y répondre, une analyse a été menée une fois le modèle figé, comme le ferait un analyste de risque : regarder de près les défauts que les modèles ne trouvent pas.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Un tiers des défauts ressemblent à de bons clients", anchor="defauts-manques")
st.markdown("""
Une partie de l'entraînement (un quart des clients) a été mise de côté **avant** l'analyse. Sur ses 771 défauts, les quatre modèles retenus, chacun à son seuil du taux de rappel minimal, se partagent nettement les rôles :
- **410 défauts sont trouvés par les quatre modèles à la fois** ;
- **248 défauts, environ un tiers, ne sont trouvés par aucun**.

Les modèles s'accordent donc sur qui est repérable et qui ne l'est pas. Qui sont ces défauts que personne ne trouve ?
""")
tableau_html(["Indicateur", "Défauts manqués", "Bons clients non signalés", "Défauts détectés"], [
    ["<b>Plafond</b>", "150 000 NT$", "200 000 NT$", "60 000 NT$"],
    ["<b>Facture de septembre</b>", "47 941 NT$", "48 533 NT$", "13 112 NT$"],
    ["<b>Paiement de septembre</b>", "3 361 NT$", "4 100 NT$", "1 280 NT$"],
    ["<b>Type d'usage de la carte</b> (page 4.3), trois usages principaux",
     "Comptant : 23 %<br>Crédit lent : 53 %<br>Crédit rapide : 13 %",
     "Comptant : 25 %<br>Crédit lent : 48 %<br>Crédit rapide : 15 %",
     "Comptant : 24 %<br>Crédit lent : 31 %<br>Crédit rapide : 22 %"],
    [f"<b>Au moins un mois en retard sur les six</b> (codification {codif('2')} ou plus)", "0 %", "0,2 %", "64 %"],
    ["<b>Probabilité moyenne donnée par les modèles</b>", "0,31", "0,29", "0,54"],
], largeurs=[37, 21, 21, 21])
st.caption(f"Partie d'analyse : un quart de l'entraînement, tiré au hasard avant l'analyse (même part de défauts), soit 4 839 clients dont 771 défauts. Un client est signalé si au moins un des quatre modèles le signale. Montants : valeurs médianes ; type d'usage et retards : part des clients du groupe, recalculée à partir des mêmes groupes que le notebook (pour les retards, le notebook ne donne que la médiane du nombre de mois en retard : 0, 0 et 1). Source : [analyse des défauts manqués]({DEFAUTS_MANQUES}), sections 2 et 3.")
st.markdown("""
**Les défauts manqués ont le profil des bons clients, pas celui des défauts détectés** : un plafond et des factures du même ordre, un paiement en septembre, aucun retard sur les six mois, et la même probabilité donnée par les modèles. Sur 9 indicateurs comparés, ils sont plus proches des bons clients sur 8. Seule l'utilisation du plafond est un peu plus élevée chez eux, un signal trop faible pour les distinguer.

**Rien, dans leurs six mois d'historique, n'annonçait leur défaut.** Aucun modèle ne pouvait les trouver, et aucune variable ne pouvait les révéler : c'est ce qui rend la base sans le contentieux si difficile à départager, et ce qui fixe le plafond.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Sans le contentieux, une partie des liens de l'exploration s'efface", anchor="liens")
st.markdown("""
Dans le tableau précédent, environ un quart de chaque groupe paie au comptant, défauts compris, alors que la page 4.3 présentait ces clients comme les meilleurs payeurs. Ce n'est pas une contradiction : **l'exploration (partie 4) a été menée sur tout le portefeuille, contentieux compris**, alors que le machine learning travaille sans lui. Sur les mêmes clients actifs, avec puis sans le contentieux :
""")
def taux(filtre, population):
    return population[filtre.reindex(population.index)]["dpnm"].mean() * 100
lignes_liens = []
for lien, bas, filtre_bas, haut, filtre_haut, verdict in LIENS:
    avec = (taux(filtre_bas, s12), taux(filtre_haut, s12))
    sans = (taux(filtre_bas, s12_hors_ctx), taux(filtre_haut, s12_hors_ctx))
    lignes_liens.append([f"<b>{lien}</b><br>{bas} / {haut}",
                         f"{nombre_fr(avec[0], 1)} % / {nombre_fr(avec[1], 1)} %",
                         f"{nombre_fr(sans[0], 1)} % / {nombre_fr(sans[1], 1)} %",
                         f"{nombre_fr(avec[1] / avec[0], 1)} → {nombre_fr(sans[1] / sans[0], 1)} fois", f"<b>{verdict}</b>"])
tableau_html(["Lien de l'exploration (groupe le moins risqué / le plus risqué)", "Taux de défaut, avec le contentieux",
              "Taux de défaut, sans le contentieux", "Écart (le plus risqué / le moins risqué)", "Le lien"],
             lignes_liens, largeurs=[30, 17, 17, 18, 18])
st.caption(f"Clients actifs (dette en septembre, plafond de 500 000 NT$ ou moins) : {nombre_fr(len(s12))} clients avec le contentieux, {nombre_fr(len(s12_hors_ctx))} sans. Calculé en direct sur le dataset.")
st.markdown("""
Une partie des écarts vus pendant l'exploration était **portée par le contentieux**, dont les clients utilisent souvent leur carte en crédit et en limite de plafond. Sans lui, le type d'usage ne distingue presque plus les clients, et l'utilisation du plafond beaucoup moins. Les liens qui tiennent, le plafond et les retards passés, sont justement ceux que garde la version finale (page 6.3).

**Avec le recul, une exploration courte refaite sur la population du machine learning**, une fois le contentieux retiré, aurait annoncé avant les scénarios quelles variables avaient une chance d'aider.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Une explication probable : le défaut suit le statut posé par la banque", anchor="cible")
st.markdown("""
Pourquoi des clients sans aucun signe de difficulté font-ils défaut ? La définition exacte du défaut dans ce dataset n'est pas documentée (page 1.3). Plusieurs indices suggèrent qu'il suit **l'étiquette posée par la banque** plutôt qu'un défaut de paiement observé. **C'est une hypothèse**, que les données seules ne permettent pas de confirmer.
""")
tableau_html(["Indice", "Groupe", "Taux de défaut", "Comparé à"], [
    ["<b>Ne rien devoir protège à peine du défaut</b>", f"Clients sans dette en septembre ({nombre_fr(len(sans_dette))})",
     f"<b>{nombre_fr(sans_dette['dpnm'].mean() * 100, 1)} %</b>", f"{nombre_fr(df['dpnm'].mean() * 100, 1)} % pour tous les clients"],
    ["<b>Au contentieux, payer ne change rien</b>", f"Clients au contentieux qui ont payé en août et en septembre ({nombre_fr(len(ctx_qui_paie))})",
     f"<b>{nombre_fr(ctx_qui_paie['dpnm'].mean() * 100, 1)} %</b>", f"{nombre_fr(au_ctx['dpnm'].mean() * 100, 1)} % pour tout le contentieux"],
    [f"<b>Un retard codifié sur une dette nulle annonce presque autant de défauts qu'un vrai retard</b>",
     f"Clients codifiés {codif('2')} ou plus en septembre, sans facture due en août (63, données d'origine)",
     "<b>63,5 %</b>", f"69,6 % pour tous les clients codifiés {codif('2')} ou plus"],
], largeurs=[30, 34, 13, 23])
st.caption(f"Portefeuille nettoyé ({nombre_fr(len(df))} clients) pour les deux premières lignes, calculées en direct ; données d'origine pour la troisième (effectif petit : un ordre de grandeur). Source : [contrôles de la cible]({CONTROLES_CIBLE}), sections 1 à 3 ; raisonnement complet : [hypothèses et conclusions]({HYPOTHESES}), H3.")
st.markdown("""
Si cette hypothèse est juste, **un client étiqueté par la banque n'a pas de porte de sortie**, quel que soit son comportement de paiement, et un client sans difficulté visible peut être déclaré en défaut pour une raison que les données ne montrent pas. Aucun modèle ne peut prévoir cela à partir des factures et des paiements : une part de la cible est **imprévisible avec ces données**.
""")

# ------------------------------------------------------------------------------
st.subheader("5. Ce qui lèverait cette limite", anchor="pistes")
st.markdown("""
Trois informations, absentes du dataset, permettraient d'aller plus loin :
- **la définition exacte du défaut** et la façon dont il est attribué ;
- **les vrais encours** : le montant du relevé ne serait pas toujours la dette réelle du client ; certains défauts, chez des clients sans dette affichée, le laissent penser ;
- **la liste des clients suivis hors du circuit normal** (recouvrement, contentieux), qui permettrait de valider la définition du contentieux (partie 5) et de séparer le défaut « administratif » du vrai défaut de paiement.
""")

st.info("""
**Ce qu'il faut retenir** : le plafond ne vient pas des modèles, mais des données. Environ un tiers des défauts ont exactement le profil des bons clients : pas de retard, un paiement en septembre, la même probabilité donnée par les modèles. Rien ne les annonçait. L'explication la plus probable, à confirmer, est que le défaut suit l'étiquette posée par la banque plutôt qu'un défaut de paiement observé : une part de la cible est alors imprévisible avec ces données, quel que soit le modèle.
""")
