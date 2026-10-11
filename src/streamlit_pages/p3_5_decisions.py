from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 3.5 : DÉCISIONS
# Uniquement les nettoyages effectués dans 02_01_nettoyage (structurel, puis métier en trois niveaux),
# chacun relié à l'anomalie des pages 3.1 à 3.4 qui le justifie.
# Les règles de la population en incident et du périmètre du ML sont présentées en parties 5 et 6.
# ==============================================================================
GH = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/src"

entete_partie_3()

# Effectifs de chaque étape, enregistrés par 02_01_nettoyage : aucun dénombrement écrit à la main
ent = load_entonnoir()
NB_GEANTS = nombre_fr(ent.loc['sans_paiements_geants', 'retires'])
NB_INACTIFS = nombre_fr(ent.loc['sans_comptes_inactifs', 'retires'])
NB_PLAFONDS = nombre_fr(ent.loc['sans_plafonds_atypiques', 'retires'])
NB_PLAFONDS_ORIGINE = ent['plafonds_atypiques_origine'].iloc[0]
NB_ETUDIES = nombre_fr(ent.loc['sans_plafonds_atypiques', 'clients'])
NB_ORIGINE = nombre_fr(ent.loc['origine', 'clients'])

st.markdown("---")
st.header("3.5 Décisions : une règle argumentée pour chaque anomalie", anchor="decisions")
st.markdown("""
Les pages précédentes ont relevé les anomalies et cherché à les comprendre. Cette page présente le nettoyage qui en découle : chaque correction, l'anomalie qui l'a motivée, et ce qui la justifie.

Deux points sont à garder en tête :
- **aucune décision n'est née de l'observation d'une seule variable.** C'est en croisant les codifications avec les montants, puis avec l'historique des clients, que chaque anomalie a trouvé son explication, et donc sa règle ;
- **le nettoyage se fait en deux temps.** Le **nettoyage structurel**, déjà présenté avec le chargement de la base (page « 2.1 Du fichier CSV à la base de données »), ne fait que ramener les valeurs hors nomenclature à « autres ». Le **nettoyage métier** applique ensuite les décisions issues de l'enquête, en trois niveaux : le niveau 1 retire quelques clients, le niveau 2 remplace les codifications 1, le niveau 3 uniformise les retards d'avril à juin. Aucun client n'est retiré aux niveaux 2 et 3.

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
st.subheader("Le nettoyage métier, niveau 1 : quelques clients retirés")
tableau_decisions([
    (f"{NB_GEANTS} paiements de plus de 1 000 000 NT$, de 2,4 à 12,8 fois le plafond",
     f"Les {NB_GEANTS} clients sont supprimés",
     "Payer plusieurs fois son plafond en un seul mois n'est pas possible avec une carte de crédit : ce sont des erreurs.",
     voir("p3_2_montants", "paiements-geants", "3.2, point 1")),
    ("Des clients sans aucune facture positive sur 6 mois et sans paiement pendant la période, parfois notés en défaut",
     f"Les {NB_INACTIFS} comptes inactifs sont supprimés",
     "Règle métier et de bon sens. Un défaut de paiement suppose une somme due : un compte sans aucun encours ni paiement sur 6 mois n'a rien à rembourser, et son défaut est improbable au sens même de la cible. Il n'y a rien à en apprendre, pas même pour un modèle de machine learning, qui apprendrait du bruit. Enfin, le projet cherche à prédire le défaut à partir du comportement de paiement : un compte inactif n'a pas de comportement à observer, il ne répond donc pas à la problématique. Un paiement en avril ne compte pas : il règle la facture de mars, antérieure à la période, dont on ne voit pas le montant. Un client qui solde une dette ancienne, puis n'utilise plus sa carte pendant les 6 mois, est donc lui aussi inactif.",
     voir("p3_1_audit", "sans-facture", "3.1")),
    ("Une poignée de clients aux plafonds de plus de 500 000 NT$, au-delà d'une cassure brutale de la répartition des plafonds",
     f"Les {NB_PLAFONDS} clients concernés sont supprimés ({nombre_fr(NB_PLAFONDS_ORIGINE)} dans les données d'origine, dont {nombre_fr(NB_PLAFONDS_ORIGINE - ent.loc['sans_plafonds_atypiques', 'retires'])} déjà retirés par les règles précédentes)",
     "Une clientèle haut de gamme : un plafond de plus d'une année de salaire moyen, un crédit peu utilisé, et trop peu de clients pour qu'un modèle apprenne leur comportement propre. Un modèle prédictif doit se concentrer sur la clientèle standard. Le seuil vient de la cassure de la répartition et de la logique métier, pas d'un calcul de performance.",
     voir("p3_4_plafonds", "cassure", "3.4")),
])

st.subheader("Le nettoyage métier, niveau 2 : la codification 1 remplacée")
tableau_decisions([
    ("Quelques dizaines de codifications 1 d'avril à août, chez une poignée de clients",
     "Tranchées avec le paiement du mois suivant : la dernière codification saine si le solde suivant est nul, celle du mois précédent si aucune facture n'était due, puis client par client",
     "Pour ces mois, le paiement qui règle la facture est connu : on peut dire quelle codification la banque aurait posée.",
     voir("p3_3_codifications", "codification-1", "3.3, point 4")),
    ("Des codifications 1 en septembre chez des clients sains en août, le plus souvent sans facture de septembre",
     "Remplacées par la codification d'août",
     "Il n'y a presque rien à juger, et d'un mois au suivant la grande majorité des clients sains le restent.",
     voir("p3_3_codifications", "codification-1", "3.3, point 4")),
    ("Des codifications 1 en septembre chez des clients en retard en août : sortie du retard ou retard maintenu, en attente du paiement d'octobre",
     "Sortie du retard (-1) si les trois modèles de 02_02 l'annoncent, sinon retard maintenu (2) ; la codification de la banque est gardée dans <code>PAY_1_original</code>",
     f"Le paiement d'octobre est absent du dataset : la sortie est estimée à partir de l'historique du client, par trois modèles appris sur les clients que la banque a tranchés (<a href=\"{GH}/02_02_modele_sorties_retard.ipynb\">02_02_modele_sorties_retard.ipynb</a>). C'est une estimation, pas la décision de la banque.",
     voir("p3_3_codifications", "codification-1", "3.3, point 4")),
])

st.markdown(f"""
**Comment la sortie du retard est estimée.** Pour un client codifié 1 en septembre et en retard en août, la vraie question est : le client sort-il du retard ? La réponse dépend du paiement d'octobre, absent du dataset. Elle est donc **estimée par apprentissage automatique**, utilisé ici comme un outil de nettoyage : il prédit une codification, jamais le défaut de paiement, et n'utilise pas la cible. Trois modèles de familles différentes apprennent à reconnaître une sortie du retard sur les clients que la banque a tranchés (clients en retard le mois précédent, en septembre, août et juillet), à partir de leur historique de codifications, de factures et de paiements. **Un client n'est déclaré sorti du retard que si les trois modèles sont d'accord** : un choix de prudence, peu de sorties annoncées, mais fiables. Sinon, le retard est maintenu.

Résultat vérifié une seule fois, sur des clients mis de côté et jamais appris ([02_02_modele_sorties_retard.ipynb]({GH}/02_02_modele_sorties_retard.ipynb), section 5 bis) :
""")
st.dataframe(pd.DataFrame({
    "Décision": ["Un seul modèle (selon le modèle)", "Les trois modèles d'accord (règle retenue)"],
    "Sorties annoncées vraies": ["80 à 84 %", "85 % (86 sur 101)"],
    "Vraies sorties retrouvées": ["85 à 87 %", "83,5 %"],
}), hide_index=True, width="stretch")
st.markdown("""
Sur l'ensemble des clients mis de côté, la codification de septembre ainsi estimée est la bonne dans 91 % des cas, contre 89,6 % en recopiant simplement celle d'août. Elle reste une **estimation**, pas la décision de la banque.
""")
with st.expander("Comment les trois modèles décident"):
    st.markdown("""
- **Trois familles de modèles**, pour ne pas dépendre d'une seule façon d'apprendre : un réseau de neurones (MLP), un modèle à arbres de décision (CatBoost) et un SVM.
- **Le seuil de chaque modèle** : les clients sont rangés du plus probablement sorti au moins probable, et le modèle annonce des sorties tant qu'une sortie y reste au moins aussi probable qu'un maintien (au moins une vraie sortie sur deux parmi les derniers clients annoncés).
- **La règle commune** : sortie si les trois modèles l'annoncent. Le tableau ci-dessous, mesuré sur les clients d'apprentissage (chaque client jugé par des modèles qui ne l'ont pas appris), montre pourquoi : quand les trois sont d'accord, près de 9 annonces sur 10 sont de vraies sorties ; dès qu'un modèle n'est pas d'accord, c'est moins d'une sur deux.
""")
    # Repris de 02_02_modele_sorties_retard, section 4 (recoupement des votes, clients en retard en août, septembre)
    st.dataframe(pd.DataFrame({
        "Sortie annoncée par": ["Les trois modèles", "Deux modèles", "Un seul modèle", "Aucun modèle"],
        "Clients": [308, 33, 36, 1658],
        "Vraies sorties": [272, 8, 9, 55],
        "Part de vraies sorties": ["88,3 %", "24,2 %", "25,0 %", "3,3 %"],
    }), hide_index=True, width="stretch")
    st.caption("Source : 02_02_modele_sorties_retard.ipynb, section 4 ; lignes à deux et à un modèle regroupées.")


st.subheader("Le nettoyage métier, niveau 3 : les retards d'avril à juin uniformisés")
tableau_decisions([
    ("En avril, mai et juin, une partie des clients qui ne paient presque rien de leur facture reste codifiée saine ; à partir de juillet, la banque les met presque tous en retard",
     "D'avril à juin, une facture positive payée à moins de 1,5 % le mois suivant, chez un client à -1, 0 ou 1 ce mois-là et à -1 ou 0 le mois précédent, est codifiée 2",
     "Le même comportement doit donner la même codification sur toute la période. Le seuil de 1,5 % est celui que la banque appliquait déjà avant juillet, sans le plancher de 1 000 NT$, qui n'existait pas encore. Après un -2, la banque accepte un paiement différé : ces clients ne sont pas touchés.",
     voir("p3_3_codifications", "tolerance", "3.3, point 3")),
])

st.markdown("""
**Tout le reste est conservé tel quel** : les codifications -2 et 0, les retards posés sur une facture nulle, les retards figés, les dépassements de plafond, les factures négatives, les paiements faits alors que rien n'était dû, les ratios de paiement démesurés et les erreurs de saisie probables ou indétectables. Les pages 3.2 et 3.3 ont montré qu'ils décrivent, pour la plupart, des comportements réels de l'époque ou le fonctionnement du système d'information de la banque, et non des erreurs.
""")

# ------------------------------------------------------------------------------
st.subheader("Des décisions révisées en chemin")
st.markdown("""
Ce nettoyage n'a pas été fixé d'un seul coup. Plusieurs règles ont été revues, certaines à plusieurs reprises, parce qu'une découverte faite plus tard dans le projet contredisait une hypothèse de départ : des seuils ont été abandonnés, des calculs unifiés, des corrections remplacées. Les règles présentées ici sont leur version finale ; les découvertes qui les ont fait évoluer seront racontées au fil des parties suivantes.
""")

# Entonnoir des populations, à côté de « Ce qu'il faut retenir » : effectifs lus dans le fichier du nettoyage
etapes = ["Données d'origine", f"Sans les {NB_GEANTS} paiements géants", f"Sans les {NB_INACTIFS} comptes inactifs",
          f"Sans les {NB_PLAFONDS} plafonds atypiques"]
effectifs = ent["clients"].tolist()
# Forme d'entonnoir stylisée (tranches de même hauteur) : les effectifs réels sont écrits dans chaque tranche
fig_entonnoir = go.Figure(go.Funnelarea(
    values=[1] * len(etapes),
    # Dernière tranche : la population étudiée dans l'analyse exploratoire
    text=[f"{etape}<br><b>{n:,}</b> clients".replace(",", " ") for etape, n in zip(etapes[:-1], effectifs[:-1])]
         + [f"{etapes[-1]}<br>Population étudiée : <b>{effectifs[-1]:,}</b> clients".replace(",", " ")],
    textinfo="text", textfont=dict(size=16, color=["white", "black", "white", "white"]),
    marker=dict(colors=[COULEURS["gris"], COULEURS["bleu_pale"], COULEURS["turquoise"], COULEURS["vert_fonce"]]),
    baseratio=0.5, aspectratio=0.8, hoverinfo="skip", showlegend=False,
))
fig_entonnoir.update_layout(height=430, margin=dict(t=10, b=10, l=10, r=10))

st.write("")  # espace pour séparer la conclusion de la section précédente
col_retenir, col_entonnoir = st.columns([2, 3], vertical_alignment="center")
with col_entonnoir:
    st.plotly_chart(fig_entonnoir, width="stretch")
with col_retenir:
    st.info(f"""
**Ce qu'il faut retenir** : très peu de lignes sont supprimées ({NB_GEANTS} paiements géants, {NB_INACTIFS} comptes sans aucune activité et {NB_PLAFONDS} clients aux plafonds atypiques), les codifications 1 sont remplacées (niveau 2), les retards d'avril à juin sont uniformisés sur la règle que la banque suit à partir de juillet (niveau 3), et tout le reste est conservé, parce qu'il décrit des comportements réels de l'époque. La population étudiée dans l'analyse exploratoire compte ainsi {NB_ETUDIES} clients sur {NB_ORIGINE}.
""")
st.markdown(f"Le code de toutes ces corrections est consultable dans le notebook de nettoyage : [02_01_nettoyage.ipynb]({GH}/02_01_nettoyage.ipynb).")
