from streamlit_pages.commun import *

# ==============================================================================
# PARTIE 3.4 : LES PLAFONDS
# Résultats repris de l'EDA_lab (cellules 204 et 205), calculés sur les 30 000
# clients des données d'origine (fichier absent du dépôt).
# ==============================================================================
BCE = "https://data.ecb.europa.eu/data/datasets/EXR/EXR.A.TWD.EUR.SP00.A"
SALAIRES = "https://statdb.mol.gov.tw/html/trend/104/51410.pdf"

entete_partie_3()

st.markdown("---")
st.header("3.4 Les plafonds : une poignée de clients hors de la clientèle standard", anchor="plafonds")
st.markdown("""
Le plafond (`LIMIT_BAL`) est le montant de crédit que la banque accorde à chaque client sur sa carte. Il varie de 10 000 à 1 000 000 NT\\$ (page « 3.1 Audit »). Tous ces clients relèvent-ils de la même clientèle ?
""")

st.subheader("Une cassure brutale au-delà de 500 000 NT\\$", anchor="cassure")
st.markdown("Répartition des plafonds par tranches de 50 000 NT\\$, sur les 30 000 clients des données d'origine :")

# Comptages repris de l'EDA_lab, cellule 204 : LIMIT_BAL par tranches de 50 000 NT$ (bornes hautes incluses)
tranches = [f"{b // 1000} à {(b + 50000) // 1000} k" for b in range(0, 1000000, 50000)]
clients = [7676, 4822, 3902, 3978, 2905, 2154, 1206, 1553, 573, 1025,
           76, 51, 37, 19, 17, 5, 0, 0, 0, 1]
couleurs = [COULEURS["turquoise"]] * 10 + [COULEURS["rouge_pale"]] * 10

fig_plafonds = go.Figure(go.Bar(
    x=tranches, y=clients, marker_color=couleurs,
    text=[f"{n}" if i >= 10 else "" for i, n in enumerate(clients)], textposition="outside",
    hovertemplate="Plafond de %{x} NT$<br>%{y} clients<extra></extra>",
))
fig_plafonds.add_vline(x=9.5, line_dash="dash", line_color=COULEURS["gris"])
fig_plafonds.add_annotation(x=9.5, y=max(clients), text="500 000 NT$", showarrow=False, xanchor="left", yanchor="top")
fig_plafonds.update_layout(height=460, xaxis_title="Plafond (milliers de NT$)", yaxis_title="Nombre de clients",
                           xaxis_tickangle=-45, margin=dict(t=30))
st.plotly_chart(fig_plafonds, width="stretch")
st.caption("Tranches de 50 000 NT\\$, borne haute incluse (la tranche « 450 à 500 k » contient les plafonds de 500 000 NT\\$). En rouge : les plafonds de plus de 500 000 NT\\$. Répartition calculée sur les 30 000 clients des données d'origine (EDA_lab, cellule 204).")

st.markdown("""
- **Jusqu'à 500 000 NT\\$, les clients se répartissent sur toutes les tranches** : 1 025 clients encore entre 450 000 et 500 000 NT\\$, dont 722 pile à 500 000 NT\\$, un palier rond que la banque semble utiliser comme plafond de référence.
- **Juste au-delà, la répartition s'effondre** : 76 clients entre 500 000 et 550 000 NT\\$, puis de moins en moins à chaque tranche, 5 entre 750 000 et 800 000 NT\\$, **personne entre 800 000 et 1 000 000 NT\\$**, et **un seul client à 1 000 000 NT\\$**.
- Au total, **206 clients, soit 0,69 %**, ont un plafond de plus de 500 000 NT\\$ : une poignée de clients, étalés à eux seuls sur la moitié de l'échelle des plafonds.
""")

st.subheader("Une clientèle aisée", anchor="clientele-aisee")
st.markdown(f"""
Pour se représenter ces montants, on les convertit en euros de 2005 et en mois de salaire taïwanais de 2005 :
- **taux de change** : 1 € valait en moyenne **40,00 NT\\$** en 2005 (Banque centrale européenne, [taux de change annuel moyen EUR/TWD]({BCE})) ;
- **salaire** : le salaire mensuel moyen de l'industrie et des services était de **43 159 NT\\$** en 2005 (ministère du Travail de Taïwan, d'après l'enquête sur les salaires de la DGBAS, l'office statistique taïwanais : [tableau des salaires moyens]({SALAIRES})). Cette source donne le salaire moyen, pas le salaire médian.
""")
st.dataframe(pd.DataFrame({
    "Plafond": ["Plafond médian de l'ensemble des clients", "Seuil de 500 000 NT$", "Plafond médian des clients au-delà de 500 000 NT$", "Plafond maximum"],
    "En NT$": ["140 000", "500 000", "580 000", "1 000 000"],
    "En euros de 2005": ["3 500 €", "12 500 €", "14 500 €", "25 000 €"],
    "En mois de salaire moyen de 2005": ["3,2 mois", "11,6 mois", "13,4 mois", "23,2 mois"],
}), hide_index=True, width="stretch")
st.markdown("""
Le client type dispose d'un plafond d'environ trois mois de salaire. Au-delà de 500 000 NT\\$, le plafond dépasse **une année entière de salaire moyen**, et va jusqu'à deux ans. Une banque n'accorde pas de tels montants sans revenus ou patrimoine en rapport : ces clients appartiennent vraisemblablement à une **clientèle haut de gamme**. Le dataset ne donne ni les revenus ni le patrimoine (page « 1. Les données ») : c'est le niveau du plafond lui-même qui le suggère.
""")

st.subheader("Des clients qui utilisent moins leur crédit", anchor="usage")
st.markdown("Pour chaque client, on retient sa facture la plus élevée sur les 6 mois, rapportée à son plafond : c'est la part maximale de son crédit qu'il a utilisée.")
st.dataframe(pd.DataFrame({
    "Clients": ["Plafond de 500 000 NT$ ou moins", "Plafond de plus de 500 000 NT$"],
    "Nombre": ["29 794", "206"],
    "Usage maximal médian du plafond": ["43,3 %", "21,1 %"],
    "N'ont jamais utilisé plus de 10 % du plafond": ["28,9 %", "35,9 %"],
    "Ont utilisé au moins la moitié du plafond": ["46,7 %", "30,1 %"],
}), hide_index=True, width="stretch")
st.caption("Calcul fait sur les 30 000 clients des données d'origine : facture maximale de BILL_AMT1 à BILL_AMT6, divisée par le plafond (EDA_lab, cellule 205).")
st.markdown("""
Les clients aux plafonds élevés **utilisent deux fois moins leur crédit** : la moitié d'entre eux n'a jamais dépassé 21 % de son plafond, contre 43 % pour les autres clients. Plus d'un sur trois s'en sert à peine, et moins d'un sur trois en utilise la moitié. Leur carte ressemble davantage à un moyen de paiement disponible qu'à un crédit dont ils auraient besoin.
""")

st.subheader("Le point de vue de la banque", anchor="banque")
st.markdown("""
Une banque ne gère pas sa clientèle haut de gamme comme sa clientèle standard : offres, interlocuteurs et suivi du risque lui sont propres. Un modèle prédictif doit, de la même façon, être construit pour la masse des clients standard et appliqué à eux seuls :
- **ces clients ont un comportement différent** : un plafond de plus d'un an de salaire, un crédit peu utilisé ;
- **ils sont trop peu nombreux** pour qu'un modèle apprenne leur comportement propre : 206 clients, répartis sur une échelle de plafonds aussi large que celle des 29 794 autres ;
- **appliquer à cette clientèle un modèle appris sur les clients standard** reviendrait à juger son risque avec des repères qui ne sont pas les siens.

Le seuil de 500 000 NT\\$ ne vient pas d'un calcul de performance : il découle de la cassure de la répartition des plafonds et de cette logique métier.
""")

st.info("""
**Ce que révèlent les plafonds** : au-delà de 500 000 NT\\$, la répartition des plafonds s'effondre brutalement. Une poignée de clients, 0,69 %, dispose d'un plafond supérieur à une année de salaire moyen et utilise peu son crédit : une clientèle haut de gamme, au comportement différent de la clientèle standard sur laquelle porte l'étude. La règle qui en découle est détaillée sur la page « 3.5 Décisions ».
""")
