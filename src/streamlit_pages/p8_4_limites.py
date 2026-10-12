from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 8.4 : LES LIMITES
# Ce que la réponse de la page 8.1 ne permet pas de dire : limites des données, de la réponse, de la méthode.
# Le registre complet des risques (gravité, parades) est en page 6.6 : cette page ne le répète pas.
# Taux calculés en direct sur le dataset ; niveaux de risque repris de lab_ML/evaluation_finale_test.ipynb,
# section 6 (mêmes chiffres et mêmes regroupements que les pages 6.4 et 8.1), contrôlés en direct.
# ==============================================================================
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
EVALUATION = f"{GH_RACINE}/lab_ML/evaluation_finale_test.ipynb"

df = load_data()
s12 = df[(df["BILL_AMT1"] > 0) & (df["LIMIT_BAL"] <= 500000)]
# Les deux populations des règles métier, au statut à M (comme creation_datasets_ML), et les autres clients
en_incident = s12[s12["STATUT_INCIDENT"] == "En incident"]
retard_imminent = s12[s12["STATUT_INCIDENT"] == "Retard imminent"]
hors_ctx = s12[~s12["STATUT_INCIDENT"].isin(["En incident", "Retard imminent"])]
taux_portefeuille = df["dpnm"].mean() * 100
taux_perimetre = s12["dpnm"].mean() * 100
taux_hors_ctx = hors_ctx["dpnm"].mean() * 100
fausses_alertes_incident = (1 - en_incident["dpnm"].mean()) * 100
fausses_alertes_imminent = (1 - retard_imminent["dpnm"].mean()) * 100

# Niveaux de risque sur tout le périmètre (évaluation finale, section 6 ; six tranches regroupées comme dans les démos) :
# (niveau, clients, défauts de paiement)
NIVEAUX = [("En incident", 3754, 2222), ("Retard imminent", 989, 649), ("Très haut risque", 783, 326),
           ("Haut risque", 1015 + 1381, 304 + 312), ("Risque modéré", 1501 + 1684 + 1811, 301 + 296 + 296),
           ("Risque faible", 14284, 1266)]
assert (len(s12), int(s12["dpnm"].sum())) == (sum(n[1] for n in NIVEAUX), sum(n[2] for n in NIVEAUX))
taux_niveau = {nom: defauts / clients * 100 for nom, clients, defauts in NIVEAUX}
# Jusqu'au haut risque compris : part de tous les défauts de paiement trouvés et précision (mêmes chiffres que la page 8.1)
jusqu_haut = NIVEAUX[:4]
part_defauts_haut = sum(n[2] for n in jusqu_haut) / sum(n[2] for n in NIVEAUX) * 100
precision_haut = sum(n[2] for n in jusqu_haut) / sum(n[1] for n in jusqu_haut) * 100
# Dilution (ordre de grandeur) : bons clients ordinaires ajoutés jusqu'à ce que le portefeuille nettoyé tombe à 5 % de défaut
# (taux déjà élevé pour une banque) ; le même facteur est appliqué aux bons clients laissés au machine learning, et les clients
# ajoutés, des payeurs sans incident, sont tous rangés en risque faible par le modèle. Les clients signalés ne changent pas :
# précision sur les clients laissés au machine learning à 60 % des défauts trouvés (page 6.4, évaluation finale, section 6).
TAUX_CIBLE = 5
PRECISION_60 = 22.1
defauts_df, bons_df = int(df["dpnm"].sum()), int((df["dpnm"] == 0).sum())
facteur_bons = (defauts_df / (TAUX_CIBLE / 100) - defauts_df) / bons_df     # bons clients à avoir, en multiple de l'actuel
bons_ajoutes = (facteur_bons - 1) * int((hors_ctx["dpnm"] == 0).sum())
_, faible_clients, faible_defauts = NIVEAUX[5]
taux_faible = faible_defauts / faible_clients * 100
taux_faible_dilue = faible_defauts / (faible_clients + bons_ajoutes) * 100
taux_dilue = hors_ctx["dpnm"].sum() / (len(hors_ctx) + bons_ajoutes) * 100

entete_partie_8()
st.markdown("---")
st.header("8.4 Les limites : ce que la réponse ne permet pas de dire", anchor="limites")
st.markdown("""
La réponse de la page 8.1 tient dans un cadre précis. Cette page en trace les bords : ce que les données ne permettent pas de dire, ce que la réponse elle-même laisse ouvert, et ce que la méthode aurait pu mieux faire. Le registre complet des risques, avec leur gravité et ce qui les limite, est en page 6.6.
""")

# ------------------------------------------------------------------------------
st.subheader("1. Les limites des données", anchor="donnees")
st.markdown(f"""
- **Le défaut de paiement n'est pas défini.** On ne sait pas comment la banque a noté le défaut de paiement d'octobre 2005. Plusieurs indices laissent penser qu'il suit son étiquette plutôt qu'un impayé observé (page 6.5). Le projet prédit donc **le défaut de paiement tel que la banque l'a noté**, pas forcément un impayé définitif.
- **Un taux de défaut de paiement irréaliste.** {nombre_fr(taux_portefeuille, 0)} % des clients sont en défaut de paiement : aucune banque ne tiendrait longtemps à ce niveau, même en pleine crise. L'échantillon a sans doute été sélectionné, d'une façon que l'étude ne décrit pas, et les défauts de paiement y sont probablement sur-représentés. **Les taux affichés décrivent cet échantillon, pas la banque** : appliqué tel quel à un vrai portefeuille, le modèle surestimerait le risque. Le biais touche aussi ce que les modèles ont pu apprendre : si l'échantillon a écarté une grande partie des clients ordinaires, qui paient sans incident, il ne montre qu'une partie du portefeuille, et les modèles ont appris à départager des clients plus risqués et plus semblables entre eux que dans la réalité. C'est une hypothèse, que les données seules ne permettent pas de vérifier : on ne sait pas comment l'échantillon a été tiré. Un ordre de grandeur montre combien l'effet serait fort. Pour que ce portefeuille ne compte plus que {TAUX_CIBLE} % de défauts de paiement, un taux déjà élevé pour une banque, il faudrait **{nombre_fr(facteur_bons, 1)} fois plus de bons clients**. Supposons que les clients ajoutés soient des payeurs ordinaires, sans incident : le modèle les range en risque faible, sous son seuil. Au seuil qui trouve 60 % des défauts de paiement des clients laissés au machine learning, rien ne change pour les clients signalés : mêmes défauts de paiement trouvés, mêmes fausses alertes, et toujours {nombre_fr(PRECISION_60, 1)} % de clients en défaut de paiement (page 6.4). Mais le taux de défaut de paiement de ces clients tombe de {nombre_fr(taux_hors_ctx, 1)} % à {nombre_fr(taux_dilue, 1)} % : le modèle ne fait plus {nombre_fr(PRECISION_60 / taux_hors_ctx, 1)} fois mieux que le hasard, mais {nombre_fr(PRECISION_60 / taux_dilue, 0)} fois mieux. Et les défauts de paiement que le modèle ne sait pas repérer se diluent : le risque faible passe de {nombre_fr(taux_faible, 1)} % à {nombre_fr(taux_faible_dilue, 1)} % de défaut de paiement. **Avec un échantillon plus proche d'un vrai portefeuille, le même modèle paraîtrait donc bien plus utile** : la sélection a pu rendre la tâche plus difficile qu'elle ne l'est pour une banque.
- **Une seule banque, un seul semestre, en pleine crise.** Rien ne garantit que ces résultats valent tels quels pour une autre banque, une autre période ou un autre pays. Ils ne sont pas pour autant dépassés : une crise du crédit à la consommation peut se reproduire ailleurs, sous d'autres formes. Les chiffres décrivent ce portefeuille ; la méthode, elle, peut servir ailleurs, à condition d'être revalidée sur les données de la banque concernée.
- **Aucune donnée économique du client.** Ni revenu, ni autres crédits, ni loyer, ni endettement total, ni reste à vivre : la banque ne voit que ses propres comptes, alors que la crise de 2005 est née d'un endettement réparti entre plusieurs banques (partie 0). Une partie des défauts de paiement reste sans doute hors de portée pour cette raison. Les données de conjoncture (chômage, inflation, croissance) manquent aussi, mais elles ne pouvaient rien départager sur une seule période ; elles comptent pour appliquer un modèle à une autre période.
- **Une population en incident reconstruite.** La population en incident et le retard imminent sont déduits des codifications par des règles métier ; la banque ne les a jamais confirmés. Une vraie liste des clients en recouvrement permettrait de les valider.
""")

# ------------------------------------------------------------------------------
st.subheader("2. Les limites de la réponse", anchor="reponse")
st.markdown(f"""
- **Environ un quart des défauts de paiement des autres clients restent imprévisibles** avec ces données : ils ont le profil des bons clients, et aucun modèle ne les distingue (page 6.5). La réponse « oui, en partie » ne s'améliorera pas avec un meilleur modèle, seulement avec d'autres données.
- **Les règles métier ont leurs fausses alertes** : {nombre_fr(fausses_alertes_incident, 0)} % des clients en incident et {nombre_fr(fausses_alertes_imminent, 0)} % des clients en retard imminent ne sont pas en défaut de paiement. Pour eux, les règles déclenchent une surveillance qui n'était pas nécessaire, et aucun modèle ne sait les repérer à l'avance (page 8.1).
- **La comparaison avec l'étude de 2009 situe, elle ne départage pas** : autre découpage, autre objectif, autres traitements (page 8.2).
- **Jusqu'où signaler dépend du point de vue.** Le modèle signale des clients jusqu'à trouver 60 % des défauts de paiement des clients laissés au machine learning, l'objectif fixé au départ (page 6.2). Ce choix a été jugé face à ces seuls clients, dont {nombre_fr(taux_hors_ctx, 1)} % sont en défaut de paiement : le risque modéré ({nombre_fr(taux_niveau['Risque modéré'], 1)} %) y reste au-dessus du hasard. Mais **vu du portefeuille entier**, où {nombre_fr(taux_perimetre, 1)} % des clients sont en défaut de paiement, le risque modéré est **sous la moyenne** : le signaler revient à surveiller des clients moins risqués que le client moyen. Vu de la banque, le signalement s'arrêterait plutôt au **haut risque**, avec {nombre_fr(part_defauts_haut, 0)} % des défauts de paiement trouvés et environ un client signalé sur deux en défaut de paiement ({nombre_fr(precision_haut, 0)} %, page 8.1).
""")
st.caption(f"Taux de défaut de paiement de tout le périmètre ({nombre_fr(len(s12))} clients du niveau 3 du nettoyage avec une somme à devoir en septembre), des clients laissés au machine learning et des deux populations des règles : calculés en direct. Taux des niveaux de risque : chaque client classé par un modèle qui ne l'a jamais vu ([évaluation finale]({EVALUATION}), section 6 ; mêmes chiffres que la page 6.4).")

# ------------------------------------------------------------------------------
st.subheader("3. Les limites de la méthode : ce que le projet referait autrement", anchor="methode")
st.markdown(f"""
La méthode a tenu ses principes : aucune règle ni aucun seuil réglé sur le défaut de paiement, un test lu une seule fois, où la précision et la qualité du tri confirment la validation, des choix tracés. Le résultat n'aurait sans doute pas changé, mais le chemin aurait pu être plus court :
- **Mesurer tôt la part de défauts de paiement imprévisibles.** Elle n'a été estimée qu'à la fin (page 6.5) ; connue dès les premiers scénarios, elle aurait annoncé le plafond.
- **Mesurer plus finement dès le départ.** Avec cinq mesures par scénario, la plupart des écarts entre scénarios sont restés plus petits que l'incertitude de la mesure (page 6.3) : des mesures plus fines auraient permis de trancher plus vite.
- **Refaire une courte exploration sur la population du machine learning**, une fois les deux populations des règles retirées : une partie des liens de l'exploration s'y efface (page 6.5), ce qui annonçait quelles variables avaient une chance d'aider.
- **Appliquer « à score égal, le plus simple » au choix du modèle**, pas seulement aux variables : à égalité, la régression logistique, plus facile à expliquer, aurait été le choix cohérent plutôt que CatBoost (page 6.6).
- **Estimer une probabilité de défaut de paiement par client** (calibration), l'objectif principal de l'étude de 2009 : le projet donne un niveau de risque et son taux observé, pas une probabilité individuelle.

Enfin, certains chiffres du machine learning sont **repris tels quels** de fichiers du machine learning qui ne sont pas publiés avec le site ; les légendes le signalent, et les contrôles en direct vérifient qu'ils portent bien sur les mêmes clients.
""")

st.info(f"""
**Ce qu'il faut retenir** : la réponse vaut pour cet échantillon, avec sa définition du défaut de paiement, inconnue, et son taux de défaut de paiement irréaliste ({nombre_fr(taux_portefeuille, 0)} %) : elle décrit une méthode et ce qu'on peut en attendre, pas le risque d'une banque d'aujourd'hui. Environ un quart des défauts de paiement des autres clients restent hors de portée de ces données. Vu du portefeuille entier, le signalement s'arrêterait plutôt au haut risque. Le chemin aurait pu être plus court, mais les principes de la méthode ont tenu.
""")
