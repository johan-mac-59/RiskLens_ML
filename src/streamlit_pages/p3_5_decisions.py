from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 3.5 : DÉCISIONS
# Uniquement les nettoyages effectués dans 02_01_nettoyage (structurel et métier),
# chacun relié à l'anomalie des pages 3.1 à 3.3 qui le justifie.
# Les règles du contentieux et du périmètre du ML sont présentées en parties 5 et 6.
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/src"

entete_partie_3()

st.markdown("---")
st.header("3.5 Décisions : une règle argumentée pour chaque anomalie", anchor="decisions")
st.markdown("""
Les pages précédentes ont relevé les anomalies et cherché à les comprendre. Cette page présente le nettoyage qui en découle : chaque correction, l'anomalie qui l'a motivée, et ce qui la justifie.

Deux points sont à garder en tête :
- **aucune décision n'est née de l'observation d'une seule variable.** C'est en croisant les codifications avec les montants, puis avec l'historique des clients, que chaque anomalie a trouvé son explication, et donc sa règle ;
- **le nettoyage se fait en deux temps.** Le **nettoyage structurel**, déjà présenté avec le chargement de la base (page « 2.1 Du fichier CSV à la base de données »), ne fait que ramener les valeurs hors nomenclature à « autres ». Le **nettoyage métier** applique ensuite les décisions issues de l'enquête.

Supprimer n'a été retenu qu'en dernier recours : une anomalie qui s'explique par un comportement réel est conservée. Seule exception : les clients aux plafonds atypiques, bien réels, mais hors de la clientèle standard sur laquelle porte l'étude (page « 3.4 Les plafonds »).
""")


def voir(page, ancre, texte):
    """Renvoi cliquable vers une section d'une autre page (ancre posée sur son sous-titre)."""
    return f'<a href="{page}#{ancre}" target="_self">{texte}</a>'


# Tableau HTML pour fixer les largeurs de colonnes
STYLE_CELLULE = "border: 1px solid rgba(128, 128, 128, 0.3); padding: 6px 8px; vertical-align: top; text-align: left;"


def tableau_decisions(lignes):
    """Une ligne par correction : (anomalie, décision, pourquoi, renvoi vers la page où l'anomalie est détectée)."""
    entete = "".join(f'<th style="{STYLE_CELLULE} background: rgba(128, 128, 128, 0.1);">{titre}</th>'
                     for titre in ("Anomalie", "Décision", "Pourquoi"))
    corps = "".join(
        f'<tr><td style="{STYLE_CELLULE}">{anomalie} <em>(détectée en {renvoi})</em></td>'
        f'<td style="{STYLE_CELLULE}">{decision}</td><td style="{STYLE_CELLULE}">{pourquoi}</td></tr>'
        for anomalie, decision, pourquoi, renvoi in lignes
    ).replace("$", "&#36;")
    st.markdown(
        '<table style="width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 1rem;">'
        '<colgroup><col style="width: 28%"><col style="width: 25%"><col style="width: 47%"></colgroup>'
        f"<thead><tr>{entete}</tr></thead><tbody>{corps}</tbody></table>",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------------------
st.subheader("Le nettoyage structurel")
tableau_decisions([
    ("Niveau d'études à 0, 5 ou 6, statut marital à 0 : valeurs absentes de la documentation",
     "Ramenées à « autres » (4 pour le niveau d'études, 3 pour le statut marital)",
     "Leur sens est inconnu, elles concernent peu de clients (345 pour le niveau d'études, 54 pour le statut marital), et la catégorie « autres » existe déjà. Supprimer ces clients aurait fait perdre leurs données de paiement sans raison.",
     voir("p3_1_audit", "etudes-statut", "3.1")),
])

# ------------------------------------------------------------------------------
st.subheader("Le nettoyage métier")
tableau_decisions([
    ("4 paiements de plus de 1 000 000 NT$, de 2,4 à 12,8 fois le plafond",
     "Les 4 clients sont supprimés",
     "Payer plusieurs fois son plafond en un seul mois n'est pas possible avec une carte de crédit : ce sont des erreurs.",
     voir("p3_2_montants", "paiements-geants", "3.2, point 1")),
    ("Des clients sans aucune facture ni aucun paiement sur 6 mois, parfois notés en défaut",
     "Les 860 comptes inactifs sont supprimés",
     "Règle métier et de bon sens. Un défaut de paiement suppose une somme due : un compte sans aucun encours ni paiement sur 6 mois n'a rien à rembourser, et son défaut est improbable au sens même de la cible. Il n'y a rien à en apprendre, pas même pour un modèle de machine learning, qui apprendrait du bruit. Enfin, le projet cherche à prédire le défaut à partir du comportement de paiement : un compte inactif n'a pas de comportement à observer, il ne répond donc pas à la problématique.",
     voir("p3_1_audit", "sans-facture", "3.1")),
    ("Le client 6783 paie chaque mois mais reste codifié 1 sur 4 mois",
     "Codifications remises à 0",
     "Cas isolé et erreur évidente : son comportement est celui d'un crédit renouvelable codifié 0.",
     voir("p3_3_codifications", "codification-1", "3.3, point 2")),
    ("Des codifications 1 posées alors qu'aucune facture n'était due",
     "Remplacées par la codification du mois précédent (0 si elle est elle-même un 1 sans facture)",
     "Pas de retard possible sans somme due. Ces corrections ne créent aucun retard (2 et plus).",
     voir("p3_3_codifications", "codification-1", "3.3, point 2") + " ; " + voir("p3_3_codifications", "dette", "point 4")),
    ("Des codifications 1 en septembre sur une facture soldée, chez un client sain le mois d'avant",
     "Remplacées par la codification du mois précédent ; les autres codifications 1 de septembre (dette due, non soldée) sont maintenues",
     "Une facture payée à 90 % ou plus est soldée : le seuil correspond au paiement total, où les codifications passent nettement de 0 à -1. Pour les autres, rien ne permet de dire si le client sortira du retard ou y restera : la vraie codification est indéterminable, et la codification 1 porte un signal de risque pour la banque.",
     voir("p3_3_codifications", "codification-1", "3.3, point 2")),
    ("Des ratios de paiement démesurés (jusqu'à 500 100 %)",
     "Un ratio de paiement unique (<code>ratio_PAY_BILLn</code>), écrêté entre 0 et 200 %, et fixé à 100 % quand aucune facture n'était due",
     "Les ratios extrêmes viennent surtout de très petites factures (payer 1 000 NT$ pour une facture de 5 NT$ donne 20 000 %) : ils déforment les moyennes et les graphiques sans rien dire de plus sur le client, qui a de toute façon largement remboursé. Sans facture due, il n'y avait rien à payer : le client est à jour. Dans les graphiques, le ratio n'est affiché que si une facture était due.",
     voir("p3_2_montants", "ratios", "3.2, point 3")),
    ("Une poignée de clients aux plafonds de plus de 500 000 NT$, au-delà d'une cassure brutale de la répartition des plafonds",
     "Les 204 clients concernés sont supprimés (206 dans les données d'origine, dont 2 déjà retirés plus haut : un paiement géant et un compte inactif)",
     "Une clientèle haut de gamme : un plafond de plus d'une année de salaire moyen, un crédit peu utilisé, et trop peu de clients pour qu'un modèle apprenne leur comportement propre. Un modèle prédictif doit se concentrer sur la clientèle standard. Le seuil vient de la cassure de la répartition et de la logique métier, pas d'un calcul de performance.",
     voir("p3_4_plafonds", "cassure", "3.4")),
])

st.markdown("""
**Tout le reste est conservé tel quel** : les codifications -2 et 0, les dépassements de plafond, les factures négatives, les paiements faits alors que rien n'était dû, les erreurs de saisie probables ou indétectables, et les codifications qui ne suivent pas la dette. Les pages 3.2 et 3.3 ont montré qu'elles décrivent, pour la plupart, des comportements réels de l'époque ou le fonctionnement du système d'information de la banque, et non des erreurs.
""")

# ------------------------------------------------------------------------------
st.subheader("Des décisions révisées en chemin")
st.markdown("""
Ce nettoyage n'a pas été fixé d'un seul coup. Plusieurs règles ont été revues, certaines à plusieurs reprises, parce qu'une découverte faite plus tard dans le projet contredisait une hypothèse de départ : des seuils ont été abandonnés, des calculs unifiés, des corrections remplacées. Les règles présentées ici sont leur version finale ; les découvertes qui les ont fait évoluer seront racontées au fil des parties suivantes.
""")

st.info("""
**Ce qu'il faut retenir** : très peu de lignes sont supprimées (4 paiements géants, 860 comptes sans aucune activité et 204 clients aux plafonds atypiques), quelques codifications sont corrigées quand la logique métier ne laisse aucun doute, et tout le reste est conservé, parce qu'il décrit des comportements réels de l'époque. La population étudiée dans l'analyse exploratoire compte ainsi 28 932 clients sur 30 000.
""")
st.markdown(f"Le code de toutes ces corrections est consultable dans le notebook de nettoyage : [02_01_nettoyage.ipynb]({GH}/02_01_nettoyage.ipynb).")
