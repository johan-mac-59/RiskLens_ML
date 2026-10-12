from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 6.5 : POURQUOI LE MODÈLE PLAFONNE
# Un plafond quoi qu'on fasse, un quart des défauts qui ressemblent à de bons clients (analyse des défauts manqués),
# et l'explication la plus probable : la cible suit le statut posé par la banque (hypothèse, définition non documentée).
# Profils des groupes repris tels quels de lab_ML/analyse_defauts_manques.ipynb (sections 2 à 4, version ml_17) : les
# probabilités hors pli ne sont pas dans le dépôt. Indices sur la cible : calculés en direct sur le dataset (portefeuille
# nettoyé, population en incident à M lue dans STATUT_INCIDENT).
# Le poids du comportement face aux codifications (H6) est gardé pour la partie 8 (conclusion).
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
DEFAUTS_MANQUES = f"{GH_RACINE}/lab_ML/analyse_defauts_manques.ipynb"
HYPOTHESES = f"{GH_RACINE}/docs/hypotheses_et_conclusions.md"

df = load_data()
au_ctx = df[df["STATUT_INCIDENT"] == "En incident"]
sans_dette = df[df["BILL_AMT1"] <= 0]
ctx_qui_paie = au_ctx[(au_ctx["PAY_AMT1"] > 0) & (au_ctx["PAY_AMT2"] > 0)]
# Clients actifs (S12), avec et sans la population en incident et le retard imminent : seules ces deux populations changent
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
s12_hors_ctx = s12[~s12["STATUT_INCIDENT"].isin(["En incident", "Retard imminent"])]
utilisation = s12["BILL_AMT1"] / s12["LIMIT_BAL"] * 100
# Liens de l'exploration (partie 4) : (lien, libellé du groupe le moins risqué, filtre, libellé du plus risqué, filtre, verdict)
LIENS = [
    ("Type d'usage de la carte (page 4.3)", "paiement comptant", s12["TYPE_USAGE"] == "Paiement comptant",
     "crédit lent", s12["TYPE_USAGE"] == "Crédit lent", "effacé"),
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
- **ni les variables** construites pendant l'exploration, ajoutées toutes ensemble puis retirées famille par famille, **ni des réglages élargis** ne font sortir les modèles de la zone d'incertitude (page 6.3) ;
- **même la tête de liste reste incertaine** : les clients que le modèle juge les plus risqués ne font défaut qu'environ quatre fois sur dix, et la précision descend ensuite vers le hasard (page 6.4). Le modèle ne trouve aucun groupe de clients dont il soit presque sûr.

La question devient donc : **le plafond vient-il des modèles, ou des données ?** Pour y répondre, une analyse a été menée une fois le modèle figé, comme le ferait un analyste de risque : regarder de près les défauts que les modèles ne trouvent pas.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Un quart des défauts ressemblent à de bons clients", anchor="defauts-manques")
st.markdown("""
Une partie de l'entraînement (un quart des clients) a été mise de côté **avant** l'analyse. Sur ses 620 défauts, les cinq modèles de la version finale, chacun à son seuil du taux de rappel minimal, se partagent nettement les rôles :
- **305 défauts, environ la moitié, sont trouvés par les cinq modèles à la fois** ;
- **154 défauts, environ un quart, ne sont trouvés par aucun**.

Les modèles s'accordent donc sur qui est repérable et qui ne l'est pas. Qui sont ces défauts que personne ne trouve ?
""")
tableau_html(["Indicateur", "Défauts manqués", "Bons clients non signalés", "Défauts détectés"], [
    ["<b>Plafond</b>", "185 000 NT$", "210 000 NT$", "80 000 NT$"],
    ["<b>Facture de septembre</b>", "32 983 NT$", "42 627 NT$", "10 213 NT$"],
    ["<b>Paiement de septembre</b>", "3 547 NT$", "4 777 NT$", "1 507 NT$"],
    ["<b>Type d'usage de la carte</b> (page 4.3), trois usages principaux",
     "Comptant : 33 %<br>Crédit lent : 45 %<br>Crédit rapide : 13 %",
     "Comptant : 29 %<br>Crédit lent : 41 %<br>Crédit rapide : 17 %",
     "Comptant : 33 %<br>Crédit lent : 29 %<br>Crédit rapide : 17 %"],
    ["<b>Aucun paiement en septembre</b>", "0 %", "0,4 %", "19 %"],
    ["<b>Compte ouvert pendant les six mois</b>", "3 %", "3 %", "15 %"],
    ["<b>Probabilité moyenne donnée par les modèles</b>", "0,21", "0,19", "0,35"],
], largeurs=[37, 21, 21, 21])
st.caption(f"Partie d'analyse : un quart de l'entraînement, tiré au hasard avant l'analyse (même part de défauts), soit 4 491 clients dont 620 défauts. Un client est signalé si au moins un des cinq modèles le signale. Montants : valeurs médianes ; type d'usage, paiement et ouverture du compte : part des clients du groupe. Source : [analyse des défauts manqués]({DEFAUTS_MANQUES}), sections 2 et 3.")
st.markdown("""
**Les défauts manqués ont le profil des bons clients, pas celui des défauts détectés** : un plafond et des factures du même ordre, un paiement en septembre pour tous, un compte ancien, pas de retard sur les six mois, et une probabilité donnée par les modèles proche de celle des bons clients. Sur 9 indicateurs comparés, ils sont plus proches des bons clients sur 6 ; les trois autres (part de la facture payée, part du dû remboursée, utilisation du plafond) ne séparent presque aucun groupe : les écarts y sont minimes, d'un côté comme de l'autre. Seul un « crédit lent » un peu plus fréquent apparaît chez eux, un signal trop faible pour les distinguer.

**Rien, dans leurs six mois d'historique, n'annonçait leur défaut.** Aucun modèle ne pouvait les trouver, et aucune variable ne pouvait les révéler : c'est ce qui rend la base sans la population en incident ni le retard imminent si difficile à départager, et ce qui fixe le plafond.
""")

# ------------------------------------------------------------------------------
st.subheader("3. Sans la population en incident ni le retard imminent, une partie des liens de l'exploration s'efface", anchor="liens")
st.markdown("""
Dans le tableau précédent, environ un tiers de chaque groupe paie au comptant, défauts compris, alors que la page 4.3 présentait ces clients comme les meilleurs payeurs. Ce n'est pas une contradiction : **l'exploration (partie 4) a été menée sur tout le portefeuille, population en incident et retard imminent compris**, alors que le machine learning travaille sans eux. Sur les mêmes clients actifs, avec puis sans ces deux populations :
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
tableau_html(["Lien de l'exploration (groupe le moins risqué / le plus risqué)", "Taux de défaut, avec les deux populations",
              "Taux de défaut, sans les deux populations", "Écart (le plus risqué / le moins risqué)", "Le lien"],
             lignes_liens, largeurs=[30, 17, 17, 18, 18])
st.caption(f"Clients actifs (dette en septembre, plafond de 500 000 NT$ ou moins) : {nombre_fr(len(s12))} clients avec la population en incident et le retard imminent, {nombre_fr(len(s12_hors_ctx))} sans. Calculé en direct sur le dataset.")
st.markdown("""
Une partie des écarts vus pendant l'exploration était **portée par la population en incident et le retard imminent**, dont les clients utilisent souvent leur carte en crédit et en limite de plafond. Sans eux, le type d'usage ne distingue plus les clients, et l'utilisation du plafond beaucoup moins. Les liens qui tiennent le mieux, le plafond et les retards passés, sont justement ceux que garde la version finale, avec l'utilisation du plafond (page 6.3).

**Avec le recul, une exploration courte refaite sur la population du machine learning**, une fois ces deux populations retirées, aurait annoncé avant les scénarios quelles variables avaient une chance d'aider.
""")

# ------------------------------------------------------------------------------
st.subheader("4. Une explication probable : le défaut suit le statut posé par la banque", anchor="cible")
st.markdown("""
Pourquoi des clients sans aucun signe de difficulté font-ils défaut ? La définition exacte du défaut dans ce dataset n'est pas documentée (page 1.3). Plusieurs indices suggèrent qu'il suit **l'étiquette posée par la banque** plutôt qu'un défaut de paiement observé. **C'est une hypothèse**, que les données seules ne permettent pas de confirmer.
""")
tableau_html(["Indice", "Groupe", "Taux de défaut", "Comparé à"], [
    ["<b>Ne rien devoir protège à peine du défaut</b>", f"Clients sans dette en septembre ({nombre_fr(len(sans_dette))})",
     f"<b>{nombre_fr(sans_dette['dpnm'].mean() * 100, 1)} %</b>", f"{nombre_fr(df['dpnm'].mean() * 100, 1)} % pour tous les clients"],
    ["<b>En incident, payer ne change rien</b>", f"Clients en incident à M qui ont payé en août et en septembre ({nombre_fr(len(ctx_qui_paie))})",
     f"<b>{nombre_fr(ctx_qui_paie['dpnm'].mean() * 100, 1)} %</b>", f"{nombre_fr(au_ctx['dpnm'].mean() * 100, 1)} % pour toute la population en incident à M"],
], largeurs=[30, 34, 13, 23])
st.caption(f"Portefeuille nettoyé ({nombre_fr(len(df))} clients), calculé en direct. Raisonnement complet : [hypothèses et conclusions]({HYPOTHESES}), H3.")
st.markdown("""
Si cette hypothèse est juste, **un client étiqueté par la banque n'a pas de porte de sortie**, quel que soit son comportement de paiement, et un client sans difficulté visible peut être déclaré en défaut pour une raison que les données ne montrent pas. Aucun modèle ne peut prévoir cela à partir des factures et des paiements : une part de la cible est **imprévisible avec ces données**.
""")

# ------------------------------------------------------------------------------
st.subheader("5. Ce qui lèverait cette limite", anchor="pistes")
st.markdown("""
Trois informations, absentes du dataset, permettraient d'aller plus loin :
- **la définition exacte du défaut** et la façon dont il est attribué ;
- **les vrais encours** : le montant du relevé ne serait pas toujours la dette réelle du client ; certains défauts, chez des clients sans dette affichée, le laissent penser ;
- **la liste des clients suivis hors du circuit normal** (recouvrement, contentieux), qui permettrait de valider la définition de la population en incident (partie 5) et de séparer le défaut « administratif » du vrai défaut de paiement.
""")

st.info("""
**Ce qu'il faut retenir** : le plafond ne vient pas des modèles, mais des données. Environ un quart des défauts ont le profil des bons clients : pas de retard, un paiement en septembre, une probabilité donnée par les modèles proche de la leur. Rien ne les annonçait. L'explication la plus probable, à confirmer, est que le défaut suit l'étiquette posée par la banque plutôt qu'un défaut de paiement observé : une part de la cible est alors imprévisible avec ces données, quel que soit le modèle.
""")
