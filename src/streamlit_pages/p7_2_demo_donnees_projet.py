import time
import joblib
from streamlit_pages.commun import *

# ==============================================================================
# PAGE 7.2, DÉMO 1 : le système complet en direct, sur les données du projet
# Clients : ceux de l'évaluation finale (test du ML + 20 % du contentieux du périmètre), jamais vus par le modèle.
# Valeurs lues dans dataset_streamlit.csv (identique aux données du ML) ; la règle du contentieux et le modèle
# calculent en direct, à chaque clic. Fichiers préparés par lab_ML/demo_ML/creation_demo_ML.ipynb.
# Section 1 : un lot de clients injecté ; section 2 : un client à la fois.
# ==============================================================================
DOSSIER_DEMO = BASE_DIR / "lab_ML" / "demo_ML"
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
PREPARATION = f"{GH_RACINE}/lab_ML/demo_ML/creation_demo_ML.ipynb"
EVALUATION = f"{GH_RACINE}/lab_ML/evaluation_finale_test.ipynb"
PAUSE = 0.6   # secondes entre deux étapes affichées, pour que le public suive (les temps de calcul affichés sont réels)


@st.cache_resource
def charger_modele():
    return joblib.load(DOSSIER_DEMO / "model_ml_14.joblib")


enregistre = charger_modele()
bornes = json.loads((DOSSIER_DEMO / "bornes_niveaux.json").read_text(encoding="utf-8"))
liste_demo = pd.read_csv(DOSSIER_DEMO / "clients_demo.csv")
VARIABLES = enregistre["variables"]

df = load_data()
reserve = df[df["ID"].isin(liste_demo["ID"])].reset_index(drop=True)
assert len(reserve) == len(liste_demo), "Des clients de la démo manquent dans dataset_streamlit.csv"


def au_contentieux(d):
    """Règle du contentieux (définition 2 de la partie 5) : deux codifications de retard d'affilée, sans sortie constatée."""
    return (d["FLAG_CTX"] == 1) & (d["MOIS_SORTIE_CTX"] == -1)


NIVEAUX = ["Contentieux (règle)", "Très haut risque", "Haut risque", "Risque modéré", "Risque faible"]


def niveau_de_risque(d, proba):
    return np.select([au_contentieux(d), proba >= bornes["tres_haut_risque"], proba >= bornes["haut_risque"], proba >= bornes["risque_modere"]],
                     NIVEAUX[:4], NIVEAUX[4])


@st.cache_data
def taux_par_niveau():
    """Taux de défaut constaté de chaque niveau, sur tous les clients de la démo (ce sont ceux du test)."""
    hors = ~au_contentieux(reserve)
    proba = np.full(len(reserve), np.nan)
    proba[hors] = enregistre["modele"].predict_proba(reserve.loc[hors, VARIABLES])[:, 1]
    return reserve.groupby(niveau_de_risque(reserve, proba))["dpnm"].mean().mul(100).to_dict()


entete_partie_7()
st.header("7.2 Démo 1 : le système complet en direct, sur les données du projet", anchor="demo-1")
st.markdown(f"""
Le système construit dans le projet tourne ici **en direct**, en deux étapes : la **règle métier du contentieux** (partie 5), puis le **modèle de machine learning** (partie 6) pour les autres clients.

Les clients injectés viennent d'une réserve de **{nombre_fr(len(reserve))} clients** que le modèle n'a **jamais vus** : le jeu de test du machine learning, et 20 % des clients au contentieux du même périmètre, tirés de la même façon. Leurs données sont celles du projet, nettoyées, avec les colonnes créées pendant l'exploration. Leur défaut constaté en octobre 2005 n'est jamais montré au modèle : il ne sert qu'à vérifier, après coup.
""")


# ==============================================================================
# 1. UN LOT DE CLIENTS
# ==============================================================================
st.subheader("1. Injecter un lot de clients", anchor="lot")
col_lot, col_legende = st.columns([2, 1])
with col_lot:
    CHOIX = CHOIX_DEMO
    TAILLES = [200, 500, 1000, 2000, len(reserve)]
    c1, c2 = st.columns(2)
    taille = c1.select_slider("Nombre de clients injectés", TAILLES, value=TAILLES[0],
                              format_func=lambda t: f"{nombre_fr(t)} (toute la réserve)" if t == len(reserve) else nombre_fr(t))
    choix = c2.radio("Part des défauts que la banque veut détecter avec le modèle (seuils fixés sur le jeu d'entraînement ; 60 % : seuil retenu pour l'apprentissage)", list(CHOIX), index=3)

    if "historique_lots" not in st.session_state:
        st.session_state.historique_lots = []

    if st.button("▶️ Injecter le lot", type="primary"):
        numero = len(st.session_state.historique_lots) + 1
        regle_seule = CHOIX[choix] == "regle_seule"
        seuil = None if regle_seule else bornes[CHOIX[choix]]
        with st.status(f"Traitement du lot n° {numero}…", expanded=True) as statut:
            lot = reserve.sample(n=taille, random_state=numero) if taille < len(reserve) else reserve
            st.write(f"📥 **{nombre_fr(len(lot))} clients injectés**, tirés au hasard dans la réserve (tirage n° {numero}).")
            time.sleep(PAUSE)
            regle = au_contentieux(lot)
            st.write(f"⚖️ **Étape 1, règle du contentieux** : {nombre_fr(regle.sum())} clients au contentieux, prédits en défaut et retirés.")
            time.sleep(PAUSE)
            hors_ctx = lot[~regle]
            if regle_seule:
                signale = np.zeros(len(hors_ctx), dtype=bool)
                st.write(f"🤖 **Étape 2, le modèle** : non utilisé ({choix}) ; les {nombre_fr(len(hors_ctx))} clients hors contentieux ne sont pas déclarés en défaut.")
            else:
                debut = time.perf_counter()
                proba = enregistre["modele"].predict_proba(hors_ctx[VARIABLES])[:, 1]
                duree = (time.perf_counter() - debut) * 1000
                st.write(f"🤖 **Étape 2, le modèle** : {nombre_fr(len(hors_ctx))} scores de risque calculés en {nombre_fr(duree, 0)} millisecondes.")
                time.sleep(PAUSE)
                signale = proba >= seuil
                st.write(f"🚩 **Décision** (seuil {nombre_fr(seuil, 3)}, {choix}) : {nombre_fr(signale.sum())} clients déclarés en défaut, {nombre_fr((~signale).sum())} non déclarés.")
            time.sleep(PAUSE)
            st.write("🔍 **Vérification** : comparaison avec le défaut constaté en octobre 2005.")
            statut.update(label=f"Lot n° {numero} traité", state="complete", expanded=False)

        groupes = {"Contentieux (règle)": lot[regle], "Déclarés en défaut par le modèle": hors_ctx[signale], "Non déclarés en défaut par le modèle": hors_ctx[~signale]}
        taux = {nom: (g["dpnm"].mean() * 100 if len(g) else np.nan) for nom, g in groupes.items()}
        detectes = groupes["Contentieux (règle)"]["dpnm"].sum() + groupes["Déclarés en défaut par le modèle"]["dpnm"].sum()
        st.session_state.dernier_lot = {"numero": numero, "choix": choix, "groupes": {n: (len(g), int(g["dpnm"].sum())) for n, g in groupes.items()},
                                        "total": (len(lot), int(lot["dpnm"].sum()))}
        st.session_state.historique_lots.append({
            "Lot": numero, "Clients": len(lot), "Part visée": choix,
            **{f"{n} : taux constaté (%)": round(t, 1) for n, t in taux.items()},
            "Défauts détectés, système complet (%)": round(detectes / lot["dpnm"].sum() * 100, 1),
            "Défauts manqués, parmi les non déclarés (%)": round(groupes["Non déclarés en défaut par le modèle"]["dpnm"].sum() / lot["dpnm"].sum() * 100, 1)})

    if "dernier_lot" in st.session_state:
        dernier = st.session_state.dernier_lot
        st.markdown(f"**Résultat du lot n° {dernier['numero']}** ({dernier['choix']})")
        noms = list(dernier["groupes"])
        couleurs = [NIVEAUX_DEMO["Contentieux (règle)"][0], couleur_signales(CHOIX[dernier["choix"]]), NIVEAUX_DEMO["Risque faible"][0]]
        colonnes = st.columns(3)
        for col, nom, couleur in zip(colonnes, noms, couleurs):
            clients, defauts = dernier["groupes"][nom]
            col.markdown(f"<div style='border-left: 6px solid {couleur}; padding-left: 10px;'><b>{nom}</b></div>", unsafe_allow_html=True)
            carte_chiffre(col, "Clients", nombre_fr(clients), couleur)
            carte_chiffre(col, "Taux de défaut constaté", f"{nombre_fr(defauts / clients * 100, 1)} %" if clients else "–", couleur,
                          aide="Part des clients du groupe en défaut constaté en octobre 2005.")
            carte_chiffre(col, "Part des défauts du lot", f"{nombre_fr(defauts)} sur {nombre_fr(dernier['total'][1])}, soit {nombre_fr(defauts / dernier['total'][1] * 100, 0)} %", couleur,
                          aide="Défauts constatés dans ce groupe, sur tous les défauts constatés du lot.")
        total_clients, total_defauts = dernier["total"]
        ctx_n, ctx_d = dernier["groupes"][noms[0]]
        fig = figure_entonnoir([("Clients injectés", total_clients, total_defauts, COULEURS["bleu_pale"]),
                                ("Hors contentieux, vers le modèle", total_clients - ctx_n, total_defauts - ctx_d, COULEURS["bleu_pale"]),
                                ("Non déclarés en défaut par le modèle", *dernier["groupes"]["Non déclarés en défaut par le modèle"], NIVEAUX_DEMO["Risque faible"][0])], 380)
        st.caption(f"Taux de défaut constaté de tout le lot : {nombre_fr(total_defauts / total_clients * 100, 1)} % (ce que donnerait un tirage au hasard).")

# Légende remplie après le choix du seuil (colonne de droite)
with col_legende:
    legende_niveaux(taux_par_niveau(), CHOIX[choix])

# Entonnoir, récipient et performance du dernier lot : toute la largeur de la page
if "dernier_lot" in st.session_state:
    col_entonnoir, col_recipient = st.columns([3, 2])
    col_entonnoir.plotly_chart(fig, width='stretch')
    col_recipient.plotly_chart(figure_recipient(dernier["groupes"], couleur_signales(CHOIX[dernier["choix"]]), 380), width='stretch')
    tableau_performance(dernier["groupes"])

if st.session_state.historique_lots:
    st.subheader("Les lots déjà injectés", anchor="historique")
    st.markdown("""
Relancez plusieurs lots de **200 clients**, puis de **toute la réserve** : sur un petit lot, les taux de défaut constatés changent beaucoup d'un tirage à l'autre, car chaque groupe ne compte que quelques dizaines de clients, parfois moins. Sur toute la réserve, ils retrouvent ceux de l'[évaluation finale]({}). **Un taux ne veut rien dire sans assez de clients derrière.**
""".format(EVALUATION))
    st.dataframe(pd.DataFrame(st.session_state.historique_lots), hide_index=True, width='stretch')
    if st.button("Effacer les lots"):
        st.session_state.historique_lots = []
        st.session_state.pop("dernier_lot", None)
        st.rerun()

# ==============================================================================
# 2. UN CLIENT À LA FOIS
# ==============================================================================
st.subheader("2. Un client à la fois", anchor="client")
ORIGINES = {"Tous les clients de la réserve": None, "Parmi les clients au contentieux": True, "Parmi les autres clients": False}
origine = st.radio("Tirer le client", list(ORIGINES), horizontal=True)

if st.button("🎲 Afficher le détail d'un client", type="primary"):
    st.session_state.numero_client = st.session_state.get("numero_client", 0) + 1
    vivier = reserve if ORIGINES[origine] is None else reserve[au_contentieux(reserve) == ORIGINES[origine]]
    st.session_state.client_id = int(vivier.sample(n=1, random_state=st.session_state.numero_client)["ID"].iloc[0])
    st.session_state.revele = False

if "client_id" in st.session_state:
    client = reserve[reserve["ID"] == st.session_state.client_id]
    c = client.iloc[0]
    st.markdown(f"#### Client n° {int(c['ID'])}, plafond de crédit : {nombre_fr(c['LIMIT_BAL'])} NT$")
    tableau_html(["", *[m for _, m in MOIS_CHRONO]], [
        ["<b>Codification du mois (PAY_n)</b>", *[cellule_codif(c[f"PAY_{n}"]) for n, _ in MOIS_CHRONO]],
        ["<b>Facture en fin de mois (NT$)</b>", *[nombre_fr(c[f"BILL_AMT{n}"]) for n, _ in MOIS_CHRONO]],
        ["<b>Paiement du mois (NT$)</b>", *[nombre_fr(c[f"PAY_AMT{n}"]) for n, _ in MOIS_CHRONO]],
    ], largeurs=[28] + [12] * 6)
    st.caption("Une facture de fin de mois est due le mois suivant : le paiement d'un mois rembourse la facture du mois précédent. "
               "Codifications de la banque : 2 et plus, retard de deux mois ou plus ; les autres valeurs ne sont pas des retards (page 3.3).")

    st.markdown("**Étape 1, règle du contentieux**")
    if au_contentieux(client).iloc[0]:
        niveau = NIVEAUX[0]
        encadre_niveau(niveau, f"⚖️ Client **au contentieux** : retard de deux mois ou plus pendant au moins deux mois d'affilée, sans sortie constatée "
                       f"({int(c['NB_MOIS_CTX'])} mois au contentieux). Il est prédit en défaut par la règle, sans passer par le modèle.")
    else:
        st.markdown("✅ Pas au contentieux : le client passe au modèle.")
        st.markdown("**Étape 2, le modèle**")
        proba = enregistre["modele"].predict_proba(client[VARIABLES])[:, 1]
        niveau = niveau_de_risque(client, proba)[0]
        signale = niveau in SIGNALES_DEMO[CHOIX[choix]]
        encadre_niveau(niveau, f"🤖 Niveau de risque : **{niveau}**. Client **{'déclaré' if signale else 'non déclaré'} en défaut par le modèle** "
                               + mention_seuil(choix))
    st.markdown(f"Dans la réserve, le taux de défaut constaté des clients de ce niveau est de **{nombre_fr(taux_par_niveau()[niveau], 1)} %**.")
    st.caption("Le modèle ne donne pas une probabilité fiable pour un client seul (les défauts ont plus de poids pendant l'apprentissage) : "
               "on affiche le niveau de risque, et le taux de défaut constaté dans ce niveau.")

    if st.button("🔍 Révéler ce qui s'est passé en octobre 2005"):
        st.session_state.revele = True
    if st.session_state.get("revele"):
        if c["dpnm"] == 1:
            st.error("Le client a été **en défaut de paiement** en octobre 2005.")
        else:
            st.success("Le client **n'a pas été en défaut de paiement** en octobre 2005.")

# ------------------------------------------------------------------------------
st.markdown("---")
ref = liste_demo.set_index("ID").loc[reserve.loc[~au_contentieux(reserve), "ID"], VARIABLES]
identique = np.allclose(reserve.loc[~au_contentieux(reserve), VARIABLES].to_numpy(dtype=float), ref.to_numpy(dtype=float))
st.caption(("✅" if identique else "⚠️") + f" Contrôle : les {len(VARIABLES)} variables du modèle lues ici sont "
           + ("identiques" if identique else "**différentes de celles**") + " au jeu de test du machine learning. "
           f"Modèle : CatBoost de la version `ml_14`, entraîné sur le jeu d'entraînement seul ; seuils fixés sur ce même jeu. "
           f"Fichiers de la démo (modèle, seuils, liste des clients) : [préparation]({PREPARATION}).")
