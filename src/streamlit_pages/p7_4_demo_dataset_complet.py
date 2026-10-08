import time
import joblib
from streamlit_pages.commun import *

# ==============================================================================
# PAGE 7.4, DÉMO 3 : tout le dataset d'origine, un modèle sur les données brutes, face à la règle métier
# Les clients sont lus dans la base par l'API (POST /clients/lot). Le modèle : CatBoost de l'essai du comparatif global
# (jeu de base, variante complète), en 5 modèles de plis ; chaque client est noté par le modèle qui ne l'a pas vu.
# Classes de risque : bornes lues sur la courbe des 30 000 clients (lecture humaine), seuils de score et taux enregistrés.
# Tout est préparé par lab_ML/demo_ML/creation_demo_3.ipynb (étapes 1 à 9).
# ==============================================================================
DOSSIER_DEMO = BASE_DIR / "lab_ML" / "demo_ML"
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
PREPARATION = f"{GH_RACINE}/lab_ML/demo_ML/creation_demo_3.ipynb"
ESSAI = f"{GH_RACINE}/lab_ML/comparatif_global/essai_jeu_de_base.ipynb"
PAUSE = 0.6   # secondes entre deux étapes affichées, pour que le public suive (les temps de calcul affichés sont réels)
# Classes de risque, numérotées comme dans l'usage bancaire : le chiffre augmente avec le risque (9 = la plus risquée,
# 1 = non déclarés). Couleurs de la classe 9 (foncée) à la classe 2 (claire) ; classe 1 : bleu des autres démos
COULEURS_CLASSES = {9: "#67001F", 8: "#912235", 7: "#B2182B", 6: "#C83E3E", 5: "#D6604D", 4: "#E58368", 3: "#F4A582", 2: "#F8C3A4"}


@st.cache_resource
def charger_modeles():
    return joblib.load(DOSSIER_DEMO / "demo_3_modeles_plis.joblib")


enregistre = charger_modeles()
if not (DOSSIER_DEMO / "demo_3_classes.json").exists():
    st.error("Le fichier des classes de risque (`lab_ML/demo_ML/demo_3_classes.json`) est absent : lancer l'étape 9 du notebook "
             "`creation_demo_3`, qui le produit.")
    st.stop()
CLASSES = json.loads((DOSSIER_DEMO / "demo_3_classes.json").read_text(encoding="utf-8"))
BORNES = CLASSES["bornes_rappel"]                                   # 15, 25, 35, 40, 45, 50, 55, 60
SEUILS = [CLASSES["seuils_score"][str(r)] for r in BORNES]           # score à atteindre pour chaque borne
CLASSE_DE_BORNE = [CLASSES["classe_de_borne"][str(r)] for r in BORNES]   # 9 pour la borne de 15 %, ..., 2 pour celle de 60 %
PLI_DU_CLIENT = {i: numero for numero, ids in enumerate(enregistre["ids_non_vus"]) for i in ids}
TOUS_LES_IDS = sorted(PLI_DU_CLIENT)
NON_CLASSE = "Niveau risque 1/9"


def classer(score):
    """Classe de chaque score : 9 (la plus risquée) à 2, 1 sous le seuil de la classe 2 (non déclaré)."""
    classe = np.ones(len(score), dtype=int)
    for seuil, k in reversed(list(zip(SEUILS, CLASSE_DE_BORNE))):   # la classe la plus risquée atteinte l'emporte
        classe[np.asarray(score) >= seuil] = k
    return classe


def noter(lot):
    """Score du modèle brut pour chaque client du lot, par le modèle du pli qui ne l'a pas vu."""
    score = pd.Series(np.nan, index=lot.index)
    plis = lot["ID"].map(PLI_DU_CLIENT)
    for numero, modele in enumerate(enregistre["modeles"]):
        dans_pli = plis == numero
        if dans_pli.any():
            score[dans_pli] = modele.predict_proba(lot.loc[dans_pli, enregistre["variables"]])[:, 1]
    return score


def regle_metier(lot):
    """Règle du projet : nettoyage, périmètre, puis contentieux à M ; renvoie aussi où le projet place chaque client."""
    nettoyes, _, _, _ = nettoyage_niveaux_1_a_4(lot)
    nettoyes = niveau_5(nettoyes)
    dans_perimetre = (nettoyes["BILL_AMT1"] > 0) & (nettoyes["LIMIT_BAL"] <= 500000)
    ctx = set(nettoyes.loc[dans_perimetre & au_contentieux(nettoyes), "ID"])
    perimetre = set(nettoyes.loc[dans_perimetre, "ID"])
    place = lot["ID"].map(lambda i: "Au contentieux" if i in ctx else ("Hors contentieux, dans le périmètre" if i in perimetre
                                                                       else "Hors périmètre (nettoyage, sans encours)"))
    return lot["ID"].isin(ctx), place


def mesures(nom, declares, y):
    detectes, defauts, n = int((declares & y).sum()), int(y.sum()), int(declares.sum())
    rappel = detectes / defauts if defauts else 0
    precision = detectes / n if n else 0
    f2 = 5 * precision * rappel / (4 * precision + rappel) if precision + rappel else 0
    return [f"<b>{nom}</b>", f"{nombre_fr(detectes)} sur {nombre_fr(defauts)}", f"{nombre_fr(rappel * 100, 1)} %", f"{nombre_fr(precision * 100, 1)} %",
            f"{nombre_fr(n / len(y) * 100, 1)} %", nombre_fr(f2, 3)]


# Taux de défaut constaté de chaque classe, sur les 30 000 clients (« 1 » : non déclarés)
TAUX_CLASSE = {int(k): v * 100 for k, v in CLASSES["taux_defaut_classes"].items()}


def legende_classes(classe_min):
    """Tableau des classes de risque : bornes, décision selon le seuil choisi, taux de défaut constaté sur tout le dataset."""
    lignes = []
    for i, k in enumerate(CLASSE_DE_BORNE):                        # de la classe 9 à la classe 2
        declare = k >= classe_min
        lignes.append([(f"<b>Niveau risque {k}/9</b>", f"background: {COULEURS_CLASSES[k]}; color: {'white' if k >= 5 else '#262730'};"),
                       f"{BORNES[i - 1] if i > 0 else 0} à {BORNES[i]} %",
                       ("<b>déclarés en défaut</b>", "background: rgba(204, 102, 119, 0.25);") if declare else "non déclarés",
                       f"{nombre_fr(TAUX_CLASSE[k], 1)} %"])
    lignes.append([(f"<b>{NON_CLASSE}</b>", f"background: {BLEU_INFO}; color: white;"), "60 à 100 %", "non déclarés",
                   f"{nombre_fr(TAUX_CLASSE[1], 1)} %"])
    st.markdown("**Les niveaux de risque, avec le seuil choisi**")
    tableau_html(["Niveau de risque", "Taux de rappel", "Décision", "Défaut constaté"], lignes, largeurs=[30, 22, 28, 20])
    st.caption(f"Défaut constaté : part des clients du niveau en défaut de paiement en octobre 2005, sur les {nombre_fr(len(TOUS_LES_IDS))} clients "
               f"(au hasard : {nombre_fr(CLASSES['taux_defaut_dataset'] * 100, 1)} %). Risques 9/9 à 2/9 : un risque élevé et bien échelonné, sur lequel la banque "
               f"choisit jusqu'où intervenir ; risque 1/9 : les clients sains. Construction et lecture des niveaux : plus bas, section 4 de cette page.")


entete_partie_7()
st.header("7.4 Démo 3 : tout le dataset d'origine, un modèle sur les données brutes", anchor="demo-3")
st.markdown(f"""
Cette démonstration porte sur **les {nombre_fr(len(TOUS_LES_IDS))} clients** du dataset d'origine, lus dans la base par l'API, **sans rien retirer** : ni nettoyage, ni règle du contentieux, ni périmètre. Elle répond à la problématique sans le travail du projet : **peut-on prévoir le défaut à partir du seul comportement des six derniers mois ?** Le modèle est le CatBoost de l'[essai du comparatif global]({ESSAI}), entraîné sur les 23 variables d'origine.

**Chaque client est noté par un modèle qui ne l'a jamais vu.** Un modèle entraîné sur tout le dataset aurait vu tout le dataset : on utilise donc cinq modèles, chacun entraîné sur 80 % des clients ; chaque client est noté par celui qui ne l'a pas appris.
""")

# ==============================================================================
# 1. INJECTER LES CLIENTS
# ==============================================================================
st.subheader("1. Injecter les clients", anchor="lot")
CHOIX = {f"{r} % des défauts": k for r, k in zip(BORNES, CLASSE_DE_BORNE)}   # part visée -> classe la moins risquée déclarée
TAILLES = [1000, 5000, 10000, len(TOUS_LES_IDS)]
if "historique_lots_3" not in st.session_state:
    st.session_state.historique_lots_3 = []

col_lot, col_legende = st.columns([2, 1])
with col_lot:
    c1, c2 = st.columns(2)
    taille = c1.select_slider("Nombre de clients injectés", TAILLES, value=TAILLES[-1],
                              format_func=lambda t: f"{nombre_fr(t)} (tout le dataset)" if t == len(TOUS_LES_IDS) else nombre_fr(t))
    choix = c2.radio("Part des défauts que la banque veut détecter (niveaux de risque construits plus bas, section 4 de cette page)",
                     list(CHOIX), index=len(CHOIX) - 1)
    classe_min = CHOIX[choix]

    if st.button("▶️ Injecter les clients", type="primary"):
        numero = len(st.session_state.historique_lots_3) + 1
        with st.status(f"Traitement du lot n° {numero}…", expanded=True) as statut:
            ids = TOUS_LES_IDS if taille == len(TOUS_LES_IDS) else pd.Series(TOUS_LES_IDS).sample(n=taille, random_state=numero).tolist()
            debut = time.perf_counter()
            try:
                with st.spinner("Lecture dans la base par l'API (le premier appel peut prendre jusqu'à une minute si le serveur est en veille)…"):
                    lignes, introuvables, illisibles = lire_lot_api(ids)
            except (requests.exceptions.RequestException, ValueError) as e:
                statut.update(label=f"Lot n° {numero} : lecture impossible", state="error")
                st.error(f"Lecture par l'API impossible : {e}")
                st.stop()
            lot = pd.DataFrame(lignes)
            non_recus = len(introuvables) + len(illisibles)
            st.write(f"📡 **{nombre_fr(len(lot))} clients lus dans la base par l'API**, en un seul appel (`POST /clients/lot`), "
                     f"en {nombre_fr(time.perf_counter() - debut, 1)} s" + (f" ; {nombre_fr(non_recus)} non reçus ou incomplets, écartés" if non_recus else "") + ".")
            time.sleep(PAUSE)
            debut = time.perf_counter()
            score = noter(lot)
            classe = classer(score)
            st.write(f"🤖 **Le modèle, sur les données brutes** : {nombre_fr(len(lot))} scores calculés en {nombre_fr((time.perf_counter() - debut) * 1000, 0)} "
                     f"millisecondes, chaque client rangé dans son niveau de risque.")
            time.sleep(PAUSE)
            declare = classe >= classe_min
            st.write(f"🚩 **Décision** ({choix}) : {nombre_fr(declare.sum())} clients déclarés en défaut, {nombre_fr((~declare).sum())} non déclarés.")
            time.sleep(PAUSE)
            debut = time.perf_counter()
            declare_regle, place = regle_metier(lot)
            st.write(f"⚖️ **Pour comparer, la règle métier du projet** (nettoyage, périmètre, contentieux) : {nombre_fr(declare_regle.sum())} clients "
                     f"au contentieux, en {nombre_fr((time.perf_counter() - debut) * 1000, 0)} millisecondes.")
            time.sleep(PAUSE)
            st.write("🔍 **Vérification** : comparaison avec le défaut constaté en octobre 2005.")
            statut.update(label=f"Lot n° {numero} traité", state="complete", expanded=False)

        y = lot["dpnm"].astype(bool).to_numpy()
        st.session_state.dernier_lot_3 = {"numero": numero, "choix": choix, "classe_min": classe_min, "y": y, "score": score.to_numpy(),
                                          "classe": classe, "regle": declare_regle.to_numpy(), "place": place.to_numpy()}
        st.session_state.historique_lots_3.append({
            "Lot": numero, "Clients": len(lot), "Part visée": choix, "Taux de défaut constaté (%)": round(y.mean() * 100, 1),
            "Déclarés en défaut : taux constaté (%)": round(y[declare].mean() * 100, 1) if declare.any() else None,
            "Non déclarés : taux constaté (%)": round(y[~declare].mean() * 100, 1) if (~declare).any() else None,
            "Défauts manqués (%)": round((y & ~declare).sum() / max(y.sum(), 1) * 100, 1)})

    if "dernier_lot_3" in st.session_state:
        d = st.session_state.dernier_lot_3
        y, classe = d["y"], d["classe"]
        declare = classe >= d["classe_min"]
        st.markdown(f"**Résultat du lot n° {d['numero']}** ({d['choix']}) : {nombre_fr(len(y))} clients, taux de défaut constaté {nombre_fr(y.mean() * 100, 1)} %")
        couleur_declares = COULEURS_CLASSES[d["classe_min"]]
        for col, (nom, groupe, couleur) in zip(st.columns(2), (("Déclarés en défaut par le modèle", declare, couleur_declares),
                                                               ("Non déclarés en défaut par le modèle", ~declare, BLEU_INFO))):
            col.markdown(f"<div style='border-left: 6px solid {couleur}; padding-left: 10px;'><b>{nom}</b></div>", unsafe_allow_html=True)
            carte_chiffre(col, "Clients", nombre_fr(groupe.sum()), couleur)
            carte_chiffre(col, "Taux de défaut constaté", f"{nombre_fr(y[groupe].mean() * 100, 1)} %" if groupe.any() else "–", couleur,
                          aide="Part des clients du groupe en défaut constaté en octobre 2005.")
            carte_chiffre(col, "Part des défauts du lot", f"{nombre_fr((groupe & y).sum())} sur {nombre_fr(y.sum())}, soit {nombre_fr((groupe & y).sum() / max(y.sum(), 1) * 100, 0)} %",
                          couleur, aide="Défauts constatés dans ce groupe, sur tous les défauts constatés du lot.")

with col_legende:
    legende_classes(classe_min)

# Entonnoir, récipient et performance du dernier lot : toute la largeur
if "dernier_lot_3" in st.session_state:
    d = st.session_state.dernier_lot_3
    y, classe = d["y"], d["classe"]
    declare = classe >= d["classe_min"]
    col_entonnoir, col_recipient = st.columns([3, 2])
    col_entonnoir.plotly_chart(figure_entonnoir([("Clients lus", len(y), int(y.sum()), COULEURS["bleu_pale"]),
                                                 ("Non déclarés en défaut par le modèle", int((~declare).sum()), int((y & ~declare).sum()), BLEU_INFO)], 380),
                               width='stretch')
    vrais = [(f"Vrais défauts, niveau risque {k}/9", int((y & (classe == k)).sum()), COULEURS_CLASSES[k])
             for k in CLASSE_DE_BORNE if k >= d["classe_min"]]
    col_recipient.plotly_chart(figure_recipient_parts(vrais, int(declare.sum()), 380), width='stretch')
    st.markdown("**Performance sur ce lot**")
    tableau_html(["", "Défauts détectés", "Taux de rappel", "Précision des défauts prédits", "Clients déclarés en défaut", "Score décisionnel F2"],
                 [mesures(f"Modèle sur les données brutes ({d['choix']})", declare, y)], largeurs=[28, 15, 12, 15, 15, 15])

if st.session_state.historique_lots_3:
    st.subheader("Les lots déjà injectés", anchor="historique")
    st.dataframe(pd.DataFrame(st.session_state.historique_lots_3), hide_index=True, width='stretch')
    if st.button("Effacer les lots"):
        st.session_state.historique_lots_3 = []
        st.session_state.pop("dernier_lot_3", None)
        st.rerun()

# ==============================================================================
# 2. UN CLIENT À LA FOIS
# ==============================================================================
st.subheader("2. Un client à la fois", anchor="client")
st.markdown("""
Le client est lu **dans la base de données par l'API**, puis noté **en direct** par le modèle de son pli, celui qui ne l'a jamais vu. Tous les clients du dataset peuvent être consultés : chacun a un modèle qui ne l'a pas appris.
""")


def lire_et_noter(id_client):
    try:
        with st.spinner("Lecture dans la base par l'API (le premier appel peut prendre jusqu'à une minute si le serveur est en veille)…"):
            ligne, reponses = lire_client_api(id_client)
    except requests.exceptions.RequestException as e:
        st.error(f"API injoignable : {e}")
        return
    except ValueError as e:
        st.error(str(e))
        return
    # Prédiction enregistrée dans la base (route GET /prediction) : lue à part, la fiche reste utilisable si elle manque
    try:
        res = requests.get(f"{API_URL}/prediction/{id_client}", timeout=API_TIMEOUT)
        prediction = res.json() if res.status_code == 200 else {"erreur": message_erreur_api(res)}
    except requests.exceptions.RequestException as e:
        prediction = {"erreur": str(e)}
    st.session_state.client_3 = {"ligne": pd.DataFrame([ligne]), "reponses": reponses, "prediction": prediction}
    st.session_state.revele_3 = False


tirage = st.button("🎲 Un client au hasard : lire dans la base et noter", type="primary", key="tirage_3")
if tirage:
    st.session_state.numero_client_3 = st.session_state.get("numero_client_3", 0) + 1
    st.session_state.id_choisi_3 = int(pd.Series(TOUS_LES_IDS).sample(n=1, random_state=st.session_state.numero_client_3).iloc[0])
c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
id_choisi = c1.selectbox("Ou choisir l'identifiant du client", TOUS_LES_IDS, key="id_choisi_3")
if c2.button("📡 Lire ce client dans la base et le noter", key="lecture_api_3") or tirage:
    lire_et_noter(id_choisi)

if "client_3" in st.session_state:
    brut = st.session_state.client_3["ligne"]
    b = brut.iloc[0]
    score = noter(brut)
    k = int(classer(score)[0])
    st.markdown(f"#### Client n° {int(b['ID'])}, plafond de crédit : {nombre_fr(b['LIMIT_BAL'])} NT$")
    with st.expander("Voir les réponses de l'API (JSON)"):
        st.json({"GET /client": st.session_state.client_3["reponses"][0], "GET /historique_mensuel": st.session_state.client_3["reponses"][1]})
    tableau_html(["", *[m for _, m in MOIS_CHRONO]], [
        ["<b>Codification du mois (PAY_n)</b>", *[cellule_codif(b[f"PAY_{n}"]) for n, _ in MOIS_CHRONO]],
        ["<b>Facture en fin de mois (NT$)</b>", *[nombre_fr(b[f"BILL_AMT{n}"]) for n, _ in MOIS_CHRONO]],
        ["<b>Paiement du mois (NT$)</b>", *[nombre_fr(b[f"PAY_AMT{n}"]) for n, _ in MOIS_CHRONO]],
    ], largeurs=[28] + [12] * 6)
    st.caption("Les données brutes, telles qu'elles sont dans la base : le modèle de cette démonstration ne reçoit aucune correction.")
    # Décision selon le seuil choisi plus haut : elle ne dépend que du niveau de risque
    declare = k >= classe_min
    encadre_couleur(COULEURS_CLASSES.get(k, BLEU_INFO), f"🤖 Le modèle place ce client en **niveau risque {k}/9**. Client **{'déclaré' if declare else 'non déclaré'} "
                                                          f"en défaut par le modèle** au seuil de {choix} (seuil choisi plus haut).")
    st.markdown(f"Sur tout le dataset, le taux de défaut constaté des clients de ce niveau est de **{nombre_fr(TAUX_CLASSE[k], 1)} %**.")
    # La prédiction enregistrée dans la base, face au calcul en direct
    prediction = st.session_state.client_3.get("prediction", {})
    if prediction.get("predictions"):
        p = prediction["predictions"][0]
        identique = p["classe_risque"] == k and abs(p["score"] - float(score.iloc[0])) < 1e-9
        st.markdown(f"📦 **Prédiction enregistrée dans la base** (calcul de {p['periode']['mois_num']:02d}/{p['periode']['annee']}, route `GET /prediction`) : "
                    f"**{p['description_classe']}**, taux de défaut constaté de ce niveau {nombre_fr(p['taux_defaut_constate_classe'], 1)} %. "
                    + ("✅ Identique au calcul en direct." if identique else "⚠️ **Différente du calcul en direct** : la base n'est plus à jour."))
        with st.expander("Voir la réponse de l'API (JSON)"):
            st.json(prediction)
    else:
        st.caption("📦 Prédiction enregistrée dans la base : indisponible pour ce client"
                   + (f" ({prediction['erreur']})." if prediction.get("erreur") else "."))
    regle, place = regle_metier(brut)
    st.markdown(f"Pour comparer, **la règle métier du projet** : {place.iloc[0].lower()}"
                + (", donc déclaré en défaut par la règle." if regle.iloc[0] else "."))
    st.caption("Le modèle ne donne pas une probabilité fiable pour un client seul (les défauts ont plus de poids pendant l'apprentissage) : "
               "on affiche son niveau de risque, et le taux de défaut constaté dans ce niveau.")
    if st.button("🔍 Révéler ce qui s'est passé en octobre 2005", key="revele_bouton_3"):
        st.session_state.revele_3 = True
    if st.session_state.get("revele_3"):
        if b["dpnm"] == 1:
            st.error("Le client a été **en défaut de paiement** en octobre 2005.")
        else:
            st.success("Le client **n'a pas été en défaut de paiement** en octobre 2005.")

# ==============================================================================
# 3. FACE À LA RÈGLE MÉTIER DU PROJET
# ==============================================================================
if "dernier_lot_3" in st.session_state:
    st.subheader("3. Le modèle face à la règle métier du projet", anchor="regle")
    d = st.session_state.dernier_lot_3
    y, classe, regle, place = d["y"], d["classe"], d["regle"], d["place"]
    modele = classe >= d["classe_min"]
    # À nombre égal de clients déclarés : les clients les mieux notés par le modèle, autant que la règle en déclare
    tete = np.zeros(len(y), dtype=bool)
    tete[np.argsort(-d["score"])[:int(regle.sum())]] = True
    st.markdown("""
Le projet a pris un autre chemin : une **règle métier**, le contentieux, pour les clients figés en retard, puis un modèle pour les autres (parties 5 et 6). La règle est calculée ici sur les mêmes clients, pour comparaison : nettoyage du projet, périmètre, puis contentieux à M.
""")
    tableau_html(["", "Défauts détectés", "Taux de rappel", "Précision des défauts prédits", "Clients déclarés en défaut", "Score décisionnel F2"], [
        mesures("Règle métier seule (contentieux)", regle, y),
        mesures(f"Modèle seul ({d['choix']})", modele, y),
        mesures("Modèle seul, autant de déclarés que la règle", tete, y),
    ], largeurs=[28, 15, 12, 15, 15, 15])
    st.caption("« Autant de déclarés que la règle » : les clients les mieux notés par le modèle, en même nombre que les clients au contentieux. "
               "À nombre égal d'alertes, lequel a le plus souvent raison ?")
    lignes = []
    for nom in ["Au contentieux", "Hors contentieux, dans le périmètre", "Hors périmètre (nettoyage, sans encours)"]:
        groupe = modele & (place == nom)
        lignes.append([f"<b>{nom}</b>", nombre_fr(groupe.sum()), f"{nombre_fr(groupe.sum() / max(modele.sum(), 1) * 100, 1)} %",
                       f"{nombre_fr(y[groupe].mean() * 100, 1)} %" if groupe.any() else "–"])
    st.markdown("**Qui le modèle déclare-t-il en défaut ? Là où le projet place ces clients**")
    tableau_html(["", "Clients déclarés par le modèle", "Part des déclarés", "Taux de défaut constaté"], lignes, largeurs=[40, 20, 20, 20])
    part_ctx = (modele & regle).sum() / max(modele.sum(), 1) * 100
    prec_regle = (regle & y).sum() / max(regle.sum(), 1) * 100
    prec_tete = (tete & y).sum() / max(tete.sum(), 1) * 100
    st.info(f"""
**Ce que répond cette démonstration à la problématique.** Sur les données brutes, le comportement des six derniers mois permet de prévoir une partie des défauts. Mais **{nombre_fr(part_ctx, 0)} % des clients que le modèle déclare en défaut sont des clients au contentieux**, que la règle métier repère déjà, sans machine learning et de façon explicable. À nombre égal d'alertes, la règle a raison dans {nombre_fr(prec_regle, 0)} % des cas, le modèle dans {nombre_fr(prec_tete, 0)} %. Le gros de ce qui est prévisible tient dans les retards de paiement que la banque a déjà codifiés : c'est ce qui a conduit le projet à confier ces clients à la règle, et le reste au modèle (parties 5 et 6).
""")

# ==============================================================================
# 4. LA CONSTRUCTION DES CLASSES DE RISQUE (TOUT LE DATASET)
# ==============================================================================
st.subheader("4. La construction des niveaux de risque", anchor="courbe")
hasard = CLASSES["taux_defaut_dataset"] * 100
st.markdown(f"""
Le modèle donne un score à chaque client. En prenant les clients du score le plus haut au plus bas, on détecte de plus en plus de défauts (le **taux de rappel**), avec une précision qui baisse. Les niveaux de risque ont été fixés **par une lecture humaine** de la courbe de précision selon le taux de rappel, tracée sur les **{nombre_fr(len(TOUS_LES_IDS))} clients**, chacun noté par le modèle qui ne l'avait pas vu :
- **les paliers d'abord** : la précision forme trois plateaux, jusqu'à 15 %, de 15 à 25 % et de 25 à 35 % de rappel (risques 9/9, 8/9 et 7/9, les plus élevés) ;
- **puis des tranches égales de 5 %** de 35 à 60 %, là où la précision descend en ligne droite (risques 6/9 à 2/9) : c'est là que la banque choisit jusqu'où elle signale ;
- **un arrêt à 60 %** : au-delà, la précision de chaque tranche passe **sous le hasard** ({nombre_fr(hasard, 1)} %, le taux de défaut du dataset). Déclarer ces clients en défaut serait moins juste qu'un tirage au sort : ils sont en risque 1/9, non déclarés.

**Numérotation** : comme dans l'usage bancaire, le chiffre augmente avec le risque (risque 9/9 le plus élevé, risque 1/9 pour les non déclarés).

**Comment lire les niveaux de risque** :
- **du risque 9/9 au risque 2/9, le risque est élevé tout le long, et bien échelonné.** Chaque niveau fait défaut plus souvent que le suivant, sans plateau de risque, et tous restent au-dessus du hasard. Les risques 9/9, 8/9 et 7/9 sont les plus élevés : la majorité de leurs clients font défaut ;
- **c'est sur cette échelle que la banque choisit jusqu'où elle intervient.** Chaque niveau ajouté détecte plus de défauts, mais fait aussi signaler plus de clients qui, en réalité, paieront : c'est le coût des faux positifs, à mettre en regard des défauts en plus ;
- **risque 1/9 : très peu de risque, les clients sains** aux yeux du modèle. Leur taux de défaut est bien sous la moyenne, mais le modèle ne sait plus y repérer les rares défauts.

Les courbes des 5 modèles, chacun sur ses clients non vus, ont confirmé que ces paliers sont réels et non dus au hasard. Courbes, lecture et vérification des niveaux pli par pli : [notebook de préparation]({PREPARATION}), étapes 8 et 9.
""")
