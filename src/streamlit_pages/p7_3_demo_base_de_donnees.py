import time
import joblib
from streamlit_pages.commun import *

# ==============================================================================
# PAGE 7.3, DÉMO 2 : test grandeur nature, à partir de la base de données (API), fichier d'origine en secours
# Tout est refait en direct : nettoyage (niveaux 1 à 5 de src/02_01_nettoyage.ipynb), périmètre, colonnes du modèle
# (lab_ML/creation_datasets_ML.ipynb), règle du contentieux, modèle. Les fonctions de traitement (commun.py) sont des copies de ces
# notebooks : le contrôle en bas de page compare, client par client, le résultat au jeu de données du projet.
# Clients : ceux de la démo 1 (jamais vus par le modèle) et 20 % des clients retirés avant le ML
# (lab_ML/demo_ML/creation_demo_ML.ipynb, section 5).
# ==============================================================================
DOSSIER_DEMO = BASE_DIR / "lab_ML" / "demo_ML"
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
PREPARATION = f"{GH_RACINE}/lab_ML/demo_ML/creation_demo_ML.ipynb"
NETTOYAGE = f"{GH_RACINE}/src/02_01_nettoyage.ipynb"
EVALUATION = f"{GH_RACINE}/lab_ML/evaluation_finale_test.ipynb"
PAUSE = 0.6   # secondes entre deux étapes affichées, pour que le public suive (les temps de calcul affichés sont réels)


@st.cache_resource
def charger_modele():
    return joblib.load(DOSSIER_DEMO / "model_ml_14.joblib")


# ==============================================================================
enregistre = charger_modele()
VARIABLES = enregistre["variables"]
bornes = json.loads((DOSSIER_DEMO / "bornes_niveaux.json").read_text(encoding="utf-8"))
CHEMIN_BRUTS = DOSSIER_DEMO / "clients_bruts_demo.csv"
reserve = pd.read_csv(CHEMIN_BRUTS, sep=";", encoding="utf-8-sig")

GROUPES = ["Retiré par le nettoyage", "Sans encours en septembre", "Contentieux (règle)",
           "Très haut risque", "Haut risque", "Risque modéré", "Risque faible"]


def classer(lot):
    """Traitement complet d'un lot : groupe de chaque client (nettoyage, périmètre, règle, niveau de risque du modèle)."""
    nettoyes, geants, inactifs, plafonds = nettoyage_niveaux_1_a_4(lot)
    nettoyes = niveau_5(nettoyes)
    perimetre = colonnes_du_modele(nettoyes[(nettoyes["BILL_AMT1"] > 0) & (nettoyes["LIMIT_BAL"] <= 500000)])
    groupe = pd.Series(GROUPES[0], index=lot["ID"].to_numpy())
    groupe[nettoyes.loc[nettoyes["BILL_AMT1"] <= 0, "ID"]] = GROUPES[1]
    regle = au_contentieux(perimetre)
    groupe[perimetre.loc[regle, "ID"]] = GROUPES[2]
    hors_ctx = perimetre[~regle]
    if len(hors_ctx):
        proba = enregistre["modele"].predict_proba(hors_ctx[VARIABLES])[:, 1]
        groupe[hors_ctx["ID"]] = np.select([proba >= bornes["tres_haut_risque"], proba >= bornes["haut_risque"], proba >= bornes["risque_modere"]],
                                           GROUPES[3:6], GROUPES[6])
    return groupe, nettoyes


@st.cache_data
def taux_par_groupe(date_modification):
    """Groupe de chaque client de la réserve et taux de défaut constaté de chaque groupe (réserve entière)."""
    groupe, _ = classer(reserve)
    taux = reserve.set_index("ID")["dpnm"].groupby(groupe).mean().mul(100).to_dict()
    return groupe, taux


groupe_reserve, taux_groupe = taux_par_groupe(CHEMIN_BRUTS.stat().st_mtime)

def ecarts_base_fichier(lignes):
    """Nombre de clients dont la ligne lue dans la base diffère de celle du fichier d'origine (hors EDUCATION et MARRIAGE,
    dont les valeurs inconnues sont regroupées au chargement de la base, comme au nettoyage)."""
    colonnes = [c for c in reserve.columns if c not in ("EDUCATION", "MARRIAGE")]
    fichier = reserve.set_index("ID").loc[lignes["ID"], [c for c in colonnes if c != "ID"]]
    return int((lignes.set_index("ID")[fichier.columns].to_numpy() != fichier.to_numpy()).any(axis=1).sum())


entete_partie_7()
st.header("7.3 Démo 2 : test grandeur nature, de la base de données à la décision", anchor="demo-2")
st.markdown(f"""
Cette fois, rien n'est préparé : les clients sont lus **dans la base de données du projet, par l'API REST** (partie 2), avec les valeurs du fichier d'origine de l'UCI, et **tout est refait en direct** : le nettoyage, les corrections de codification, le périmètre, la règle du contentieux et le modèle. Si l'API ne répond pas, les mêmes clients sont lus dans le fichier d'origine, en secours. La base n'est jamais modifiée : les clients y sont seulement lus, et le nettoyage se fait en mémoire, dans l'application, juste avant la règle et le modèle.

La réserve compte **{nombre_fr(len(reserve))} clients**, tous inconnus du modèle : ceux de la démo 1, et 20 % des clients que le projet a retirés avant le machine learning. Un client pris au hasard dans le fichier d'origine aurait de fortes chances d'avoir servi à l'apprentissage : une fois traité, le modèle le reconnaîtrait, et son score serait trop beau.

**Le périmètre** : les clients qui ont un encours à rembourser fin septembre (`BILL_AMT1 > 0`) et un plafond de 500 000 NT$ au plus. C'est sur eux seuls que s'appliquent la règle du contentieux et le modèle (partie 5). Après le nettoyage, les clients de la réserve qui entrent dans le périmètre sont **exactement ceux de la démo 1**.
""")

with st.expander("Voir les premières lignes du fichier d'origine, dont la base reprend les valeurs"):
    st.code("\n".join(CHEMIN_BRUTS.read_text(encoding="utf-8-sig").splitlines()[:6]), language=None)

st.subheader("1. Injecter un lot de clients", anchor="lot")
col_lot, col_legende = st.columns([2, 1])
with col_lot:
    CHOIX = CHOIX_DEMO
    TAILLES = [200, 500, 1000, 2000, len(reserve)]
    c1, c2 = st.columns(2)
    taille = c1.select_slider("Nombre de clients injectés", TAILLES, value=TAILLES[0],
                              format_func=lambda t: f"{nombre_fr(t)} (toute la réserve)" if t == len(reserve) else nombre_fr(t))
    choix = c2.radio("Part des défauts que la banque veut détecter avec le modèle (seuils fixés sur le jeu d'entraînement ; 60 % : seuil retenu pour l'apprentissage)", list(CHOIX), index=3)
    SOURCES = ["Base de données (API)", "Fichier d'origine (CSV), en secours si l'API ne répond pas"]
    col_source, _ = st.columns([1, 2])
    source = col_source.selectbox("Où lire les clients", SOURCES, index=0,
                      help="Par l'API, tout le lot est lu dans la base en un seul appel (POST /clients/lot). "
                           "Le fichier d'origine contient les mêmes clients : il sert de secours si l'API ne répond pas.")

    if "historique_lots_2" not in st.session_state:
        st.session_state.historique_lots_2 = []

    if st.button("▶️ Injecter le lot", type="primary"):
        numero = len(st.session_state.historique_lots_2) + 1
        regle_seule = CHOIX[choix] == "regle_seule"
        seuil = None if regle_seule else bornes[CHOIX[choix]]
        with st.status(f"Traitement du lot n° {numero}…", expanded=True) as statut:
            lot = reserve.sample(n=taille, random_state=numero) if taille < len(reserve) else reserve
            duree_lecture, ecarts, erreurs = None, None, []
            if source == SOURCES[0]:
                # Lecture du lot dans la base, par l'API, en un seul appel : seuls les identifiants viennent de la réserve
                debut_lecture = time.perf_counter()
                try:
                    with st.spinner("Lecture du lot dans la base par l'API (le premier appel peut prendre jusqu'à une minute si le serveur est en veille)…"):
                        lignes, introuvables, erreurs = lire_lot_api(lot["ID"])
                except (requests.exceptions.RequestException, ValueError) as e:
                    statut.update(label=f"Lot n° {numero} : lecture impossible", state="error")
                    st.error(f"Lecture par l'API impossible : {e}. Choisissez le fichier d'origine (secours) et relancez le lot.")
                    st.stop()
                duree_lecture = time.perf_counter() - debut_lecture
                erreurs += [f"client {i} : introuvable dans la base" for i in introuvables]
                lot = pd.DataFrame(lignes, columns=reserve.columns)
                ecarts = ecarts_base_fichier(lot) if len(lot) else 0
                st.write(f"📡 **{nombre_fr(len(lot))} clients lus dans la base par l'API**, en un seul appel (`POST /clients/lot`, "
                         f"tirage n° {numero}), en {nombre_fr(duree_lecture, 1)} s"
                         + ((" ; 1 client non reçu ou illisible, écarté" if len(erreurs) == 1 else f" ; {nombre_fr(len(erreurs))} clients non reçus ou illisibles, écartés") if erreurs else "") + ".")
                if erreurs:
                    with st.expander("Voir les clients non reçus"):
                        st.markdown("\n".join(f"- {e}" for e in erreurs[:50]))
            else:
                st.write(f"📥 **{nombre_fr(len(lot))} clients lus dans le fichier d'origine**, tirés au hasard dans la réserve (tirage n° {numero}).")
            time.sleep(PAUSE)
            debut = time.perf_counter()
            nettoyes, geants, inactifs, plafonds = nettoyage_niveaux_1_a_4(lot)
            st.write(f"🧹 **Nettoyage** : {nombre_fr(len(geants))} paiements géants, {nombre_fr(len(inactifs))} comptes inactifs "
                     f"et {nombre_fr(len(plafonds))} plafonds atypiques retirés ; codifications sans facture due corrigées.")
            time.sleep(PAUSE)
            avant = nettoyes[PAY].copy()
            nettoyes = niveau_5(nettoyes)
            corriges = (nettoyes[PAY] != avant).any(axis=1).sum()
            st.write(f"🔧 **Corrections du contentieux** (niveau 5) : {nombre_fr(corriges)} clients aux codifications corrigées "
                     f"(faux retards, mois de transition), indicateurs du contentieux calculés.")
            time.sleep(PAUSE)
            sans_encours = nettoyes[nettoyes["BILL_AMT1"] <= 0]
            perimetre = colonnes_du_modele(nettoyes[(nettoyes["BILL_AMT1"] > 0) & (nettoyes["LIMIT_BAL"] <= 500000)])
            duree_traitement = (time.perf_counter() - debut) * 1000
            st.write(f"🎯 **Périmètre** : {nombre_fr(len(sans_encours))} clients sans encours en septembre (encours nul ou négatif) écartés ; "
                     f"colonnes du modèle calculées. Traitement complet en {nombre_fr(duree_traitement, 0)} millisecondes.")
            time.sleep(PAUSE)
            regle = au_contentieux(perimetre)
            st.write(f"⚖️ **Règle du contentieux** : {nombre_fr(regle.sum())} clients au contentieux, prédits en défaut et retirés.")
            time.sleep(PAUSE)
            hors_ctx = perimetre[~regle]
            if regle_seule:
                proba = np.full(len(hors_ctx), np.nan)
                signale = np.zeros(len(hors_ctx), dtype=bool)
                st.write(f"🤖 **Le modèle** : non utilisé ({choix}) ; les {nombre_fr(len(hors_ctx))} clients hors contentieux ne sont pas déclarés en défaut.")
            else:
                debut = time.perf_counter()
                proba = enregistre["modele"].predict_proba(hors_ctx[VARIABLES])[:, 1] if len(hors_ctx) else np.array([])
                st.write(f"🤖 **Le modèle** : {nombre_fr(len(hors_ctx))} scores de risque calculés en {nombre_fr((time.perf_counter() - debut) * 1000, 0)} millisecondes.")
                time.sleep(PAUSE)
                signale = proba >= seuil
                st.write(f"🚩 **Décision** (seuil {nombre_fr(seuil, 3)}, {choix}) : {nombre_fr(signale.sum())} clients déclarés en défaut, {nombre_fr((~signale).sum())} non déclarés.")
            time.sleep(PAUSE)
            st.write("🔍 **Vérification** : comparaison avec le défaut constaté en octobre 2005.")
            statut.update(label=f"Lot n° {numero} traité", state="complete", expanded=False)

        groupes = {"Retirés par le nettoyage": pd.concat([geants, inactifs, plafonds]), "Sans encours en septembre": sans_encours,
                   "Contentieux (règle)": perimetre[regle], "Déclarés en défaut par le modèle": hors_ctx[signale], "Non déclarés en défaut par le modèle": hors_ctx[~signale]}
        st.session_state.dernier_lot_2 = {"numero": numero, "choix": choix, "total": (len(lot), int(lot["dpnm"].sum())), "ecarts_base": ecarts,
                                          "groupes": {n: (len(g), int(g["dpnm"].sum())) for n, g in groupes.items()},
                                          "perimetre": perimetre[["ID"] + PAY + ["FLAG_CTX", "MOIS_SORTIE_CTX", "CUMUL_INCIDENT", "PAY_habituel"]],
                                          "proba": pd.Series(proba, index=hors_ctx["ID"].to_numpy())}
        st.session_state.historique_lots_2.append({
            "Lot": numero, "Clients": len(lot), "Part visée": choix, "Source": "API" if duree_lecture is not None else "Fichier",
            "Lecture par l'API (s)": round(duree_lecture, 1) if duree_lecture is not None else None,
            **{f"{n} : taux constaté (%)": (round(g["dpnm"].mean() * 100, 1) if len(g) else None) for n, g in groupes.items()},
            "Défauts manqués, parmi les non déclarés (%)": round(groupes["Non déclarés en défaut par le modèle"]["dpnm"].sum() / lot["dpnm"].sum() * 100, 1)})

    if "dernier_lot_2" in st.session_state:
        dernier = st.session_state.dernier_lot_2
        total_clients, total_defauts = dernier["total"]
        st.markdown(f"**Résultat du lot n° {dernier['numero']}** ({dernier['choix']}) : {nombre_fr(total_clients)} clients, "
                    f"taux de défaut constaté de tout le lot {nombre_fr(total_defauts / total_clients * 100, 1)} %")
        couleurs = [NIVEAUX_DEMO["Retiré par le nettoyage"][0], NIVEAUX_DEMO["Sans encours en septembre"][0], NIVEAUX_DEMO["Contentieux (règle)"][0],
                    couleur_signales(CHOIX[dernier["choix"]]), NIVEAUX_DEMO["Risque faible"][0]]
        for col, (nom, (clients, defauts)), couleur in zip(st.columns(5), dernier["groupes"].items(), couleurs):
            col.markdown(f"<div style='border-left: 6px solid {couleur}; padding-left: 10px; min-height: 3em;'><b>{nom}</b></div>", unsafe_allow_html=True)
            carte_chiffre(col, "Clients", nombre_fr(clients), couleur)
            carte_chiffre(col, "Taux de défaut constaté", f"{nombre_fr(defauts / clients * 100, 1)} %" if clients else "–", couleur,
                          aide="Part des clients du groupe en défaut constaté en octobre 2005.")
            carte_chiffre(col, "Part des défauts du lot", f"{nombre_fr(defauts)} sur {nombre_fr(total_defauts)}, soit {nombre_fr(defauts / total_defauts * 100, 0)} %", couleur,
                          aide="Défauts constatés dans ce groupe, sur tous les défauts constatés du lot.")

        clients_sans_encours, defauts_sans_encours = dernier["groupes"]["Sans encours en septembre"]
        if clients_sans_encours:
            st.warning(f"""
    **L'anomalie : des défauts sans dette.** {nombre_fr(clients_sans_encours)} clients n'avaient rien à rembourser fin septembre (encours nul ou négatif), et pourtant **{nombre_fr(defauts_sans_encours / clients_sans_encours * 100, 1)} %** d'entre eux sont comptés en défaut en octobre. Un client sans dette ne peut pas manquer un paiement : la cible ne mesure probablement pas seulement un défaut de paiement (page 6.5). Ces clients sont écartés avant le système (partie 5), et ce taux reste une limite des données.
    """)

        noms = list(dernier["groupes"])
        restants, defauts_restants = [total_clients], [total_defauts]
        for nom in noms[:3]:
            restants.append(restants[-1] - dernier["groupes"][nom][0])
            defauts_restants.append(defauts_restants[-1] - dernier["groupes"][nom][1])
        noms_etapes = ["Clients lus", "Après le nettoyage", "Avec un encours en septembre (périmètre)", "Hors contentieux, vers le modèle"]
        fig = figure_entonnoir([(nom, n, d, COULEURS["bleu_pale"]) for nom, n, d in zip(noms_etapes, restants, defauts_restants)]
                               + [("Non déclarés en défaut par le modèle", *dernier["groupes"]["Non déclarés en défaut par le modèle"], NIVEAUX_DEMO["Risque faible"][0])], 440)

        # Contrôle client par client : le traitement en direct redonne le jeu de données du projet (et donc la démo 1)
        reference = load_data().set_index("ID")
        calcule = dernier["perimetre"].set_index("ID")
        colonnes_controle = PAY + ["FLAG_CTX", "MOIS_SORTIE_CTX", "CUMUL_INCIDENT", "PAY_habituel"]
        ecarts = (calcule[colonnes_controle] != reference.loc[calcule.index, colonnes_controle]).any(axis=1).sum()
        st.caption(("✅" if ecarts == 0 else "⚠️") + f" Contrôle client par client : pour les {nombre_fr(len(calcule))} clients du périmètre, "
                   f"les codifications corrigées, les indicateurs du contentieux et les colonnes du modèle calculés en direct sont "
                   + ("identiques à ceux" if ecarts == 0 else f"**différents pour {nombre_fr(ecarts)} clients** de ceux") +
                   f" du jeu de données du projet ([nettoyage]({NETTOYAGE})). Fichiers de la démo : [préparation]({PREPARATION}).")
        if dernier.get("ecarts_base") is not None:
            st.caption(("✅" if dernier["ecarts_base"] == 0 else "⚠️") + " Contrôle de la lecture par l'API : les lignes lues dans la base sont "
                       + ("identiques à celles" if dernier["ecarts_base"] == 0 else f"**différentes pour {nombre_fr(dernier['ecarts_base'])} clients** de celles")
                       + " du fichier d'origine (hors catégories inconnues d'éducation et de statut marital, regroupées au chargement de la base).")

# Légende remplie après le choix du seuil (colonne de droite)
with col_legende:
    legende_niveaux(taux_groupe, CHOIX[choix])

# Entonnoir, récipient et performance du dernier lot : toute la largeur de la page
if "dernier_lot_2" in st.session_state:
    col_entonnoir, col_recipient = st.columns([3, 2])
    col_entonnoir.plotly_chart(fig, width='stretch')
    col_recipient.plotly_chart(figure_recipient(dernier["groupes"], couleur_signales(CHOIX[dernier["choix"]]), 440), width='stretch')
    tableau_performance(dernier["groupes"])

if st.session_state.historique_lots_2:
    st.subheader("Les lots déjà injectés", anchor="historique")
    st.markdown("""
Relancez plusieurs lots de **200 clients**, puis de **toute la réserve** : sur un petit lot, les taux de défaut constatés changent beaucoup d'un tirage à l'autre, car chaque groupe ne compte que quelques dizaines de clients, parfois moins. Sur toute la réserve, ceux du système (contentieux, signalés, écartés) retrouvent ceux de la démo 1 et de l'[évaluation finale]({}). **Un taux ne veut rien dire sans assez de clients derrière.**
""".format(EVALUATION))
    st.dataframe(pd.DataFrame(st.session_state.historique_lots_2), hide_index=True, width='stretch')
    if st.button("Effacer les lots"):
        st.session_state.historique_lots_2 = []
        st.session_state.pop("dernier_lot_2", None)
        st.rerun()

# ==============================================================================
# 2. UN CLIENT À LA FOIS
# ==============================================================================

st.subheader("2. Un client à la fois", anchor="client")
ORIGINES = {"Tous les clients de la réserve": GROUPES, "Parmi les clients retirés par le nettoyage": GROUPES[:1],
            "Parmi les clients hors périmètre (sans encours en septembre)": GROUPES[1:2],
            "Parmi les clients au contentieux": GROUPES[2:3], "Parmi les autres clients": GROUPES[3:]}
st.markdown("""
Le client est lu **dans la base de données du projet, par l'API REST** (partie 2), comme le ferait un outil branché sur le système d'information d'une banque. La base contient les 30 000 clients, dont ceux qui ont servi à l'apprentissage : seuls les identifiants de la réserve, **jamais vus par le modèle**, sont proposés.
""")
origine = st.radio("Clients proposés", list(ORIGINES), horizontal=True, key="origine_2")
vivier = groupe_reserve[groupe_reserve.isin(ORIGINES[origine])]
with st.expander(f"Voir la liste des {nombre_fr(len(groupe_reserve))} identifiants jamais vus par le modèle"):
    st.dataframe(groupe_reserve.rename("Où le système l'arrête").rename_axis("ID").reset_index(), hide_index=True, width='stretch')

def lire_dans_la_base(id_client):
    """Lecture de la fiche, avec message en cas d'erreur."""
    try:
        with st.spinner("Lecture dans la base par l'API (le premier appel peut prendre jusqu'à une minute si le serveur est en veille)…"):
            ligne, reponses = lire_client_api(id_client)
    except requests.exceptions.RequestException as e:
        st.error(f"API injoignable : {e}")
        return
    except ValueError as e:
        st.error(str(e))
        return
    st.session_state.lu_api_2 = {"ligne": pd.DataFrame([ligne])[reserve.columns], "reponses": reponses}
    st.session_state.revele_2 = False


# Un clic : un identifiant tiré au hasard, lu dans la base et traité aussitôt (la liste de choix est remplie avant son affichage)
tirage = st.button("🎲 Un client au hasard : lire dans la base et traiter", type="primary", key="tirage_2")
if tirage:
    st.session_state.numero_client_2 = st.session_state.get("numero_client_2", 0) + 1
    st.session_state.id_choisi_2 = int(vivier.sample(n=1, random_state=st.session_state.numero_client_2).index[0])
if st.session_state.get("id_choisi_2") not in vivier.index:
    st.session_state.id_choisi_2 = int(vivier.index[0])
c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
id_choisi = c1.selectbox("Ou choisir l'identifiant du client", sorted(vivier.index.astype(int)), key="id_choisi_2")
if c2.button("📡 Lire ce client dans la base et le traiter", key="lecture_api_2") or tirage:
    lire_dans_la_base(id_choisi)

if "lu_api_2" in st.session_state:
    brut = st.session_state.lu_api_2["ligne"]
    b = brut.iloc[0]
    groupe_client, nettoye = classer(brut)                       # traitement en direct de ce seul client
    groupe_client = groupe_client.iloc[0]
    st.markdown(f"#### Client n° {int(b['ID'])}, plafond de crédit : {nombre_fr(b['LIMIT_BAL'])} NT$")
    with st.expander("Voir les réponses de l'API (JSON)"):
        st.json({"GET /client": st.session_state.lu_api_2["reponses"][0], "GET /historique_mensuel": st.session_state.lu_api_2["reponses"][1]})
    st.markdown("**Sa ligne, reconstruite à partir de la base, au format du fichier d'origine**")
    st.code(";".join(str(v) for v in brut.drop(columns="dpnm").iloc[0].tolist()), language=None)
    # Contrôle : la base redonne la ligne du fichier d'origine (sauf EDUCATION et MARRIAGE, dont les valeurs inconnues sont
    # regroupées avant le chargement dans la base, comme au nettoyage)
    fichier = reserve[reserve["ID"] == b["ID"]].iloc[0]
    colonnes_identiques = [c for c in reserve.columns if c not in ("EDUCATION", "MARRIAGE")]
    if (brut.iloc[0][colonnes_identiques].to_numpy() == fichier[colonnes_identiques].to_numpy()).all():
        st.caption("✅ La ligne lue dans la base est identique à celle du fichier d'origine (hors catégories inconnues d'éducation et de statut marital, regroupées au chargement de la base).")
    else:
        st.caption("⚠️ La ligne lue dans la base **diffère** de celle du fichier d'origine : la base a été modifiée (espace administrateur). Le traitement porte sur la ligne de la base.")
    lignes = [["<b>Codification dans le fichier (PAY_n)</b>", *[cellule_codif(b[f"PAY_{n}"]) for n, _ in MOIS_CHRONO]]]
    if len(nettoye):
        c = nettoye.iloc[0]
        lignes.append(["<b>Codification après nettoyage</b>", *[cellule_codif(c[f"PAY_{n}"]) for n, _ in MOIS_CHRONO]])
    lignes += [["<b>Facture en fin de mois (NT$)</b>", *[nombre_fr(b[f"BILL_AMT{n}"]) for n, _ in MOIS_CHRONO]],
               ["<b>Paiement du mois (NT$)</b>", *[nombre_fr(b[f"PAY_AMT{n}"]) for n, _ in MOIS_CHRONO]]]
    tableau_html(["", *[m for _, m in MOIS_CHRONO]], lignes, largeurs=[28] + [12] * 6)
    if len(nettoye) and (nettoye.iloc[0][PAY].to_numpy() != b[PAY].to_numpy()).any():
        st.caption("Le nettoyage a corrigé au moins une codification de ce client (codification sans facture due, faux retard ou mois de transition).")

    st.markdown("**Le traitement, étape par étape**")
    if groupe_client == GROUPES[0]:
        inactif = (b[BILL] <= 0).all() and (b[PAY_AMT[:5]] == 0).all()
        raison = ("un paiement de plus d'un million de NT$" if (b[PAY_AMT] > 1000000).any() else
                  "un compte inactif sur les six mois" if inactif else "un plafond de plus de 500 000 NT$")
        encadre_niveau(groupe_client, f"🧹 **Retiré par le nettoyage** : {raison}. Le client n'entre pas dans le système.")
    elif groupe_client == GROUPES[1]:
        encadre_niveau(groupe_client, f"🎯 Nettoyage passé. **Écarté au périmètre** : encours de {nombre_fr(b['BILL_AMT1'])} NT$ fin septembre, rien à rembourser en octobre.")
    elif groupe_client == GROUPES[2]:
        encadre_niveau(groupe_client, f"⚖️ Nettoyage et périmètre passés. **Au contentieux** : retard de deux mois ou plus pendant au moins deux mois d'affilée, "
                       f"sans sortie constatée ({int(nettoye.iloc[0]['NB_MOIS_CTX'])} mois au contentieux). Prédit en défaut par la règle, sans passer par le modèle.")
    else:
        signale = groupe_client in SIGNALES_DEMO[CHOIX[choix]]
        encadre_niveau(groupe_client, f"🤖 Nettoyage, périmètre et règle du contentieux passés. Le modèle le classe en **{groupe_client}**. "
                                      f"Client **{'déclaré' if signale else 'non déclaré'} en défaut par le modèle** "
                                      + mention_seuil(choix))
    st.markdown(f"Dans la réserve, le taux de défaut constaté des clients de ce groupe est de **{nombre_fr(taux_groupe[groupe_client], 1)} %**.")
    st.caption("Le modèle ne donne pas une probabilité fiable pour un client seul (les défauts ont plus de poids pendant l'apprentissage) : "
               "on affiche le niveau de risque, et le taux de défaut constaté dans ce niveau.")

    if st.button("🔍 Révéler ce qui s'est passé en octobre 2005", key="revele_bouton_2"):
        st.session_state.revele_2 = True
    if st.session_state.get("revele_2"):
        if b["dpnm"] == 1:
            st.error("Le client a été **en défaut de paiement** en octobre 2005.")
        else:
            st.success("Le client **n'a pas été en défaut de paiement** en octobre 2005.")
