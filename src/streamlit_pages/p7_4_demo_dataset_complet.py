import time
import joblib
from streamlit_pages.commun import *

# ==============================================================================
# PAGE 7.4, DÉMO 3 : tout le dataset d'origine, une règle métier face à un modèle
# Les clients sont lus dans la base par l'API (POST /clients/lot). Deux décisions en direct pour chaque client :
# - la règle métier du projet : nettoyage, périmètre, contentieux à M (fonctions de commun.py) ;
# - un modèle entraîné sur les données brutes, sans le travail du projet : CatBoost de l'essai du comparatif global
#   (jeu de base, variante complète), en 5 modèles de plis ; chaque client est noté par le modèle qui ne l'a pas vu
#   (lab_ML/demo_ML/creation_demo_3.ipynb).
# ==============================================================================
DOSSIER_DEMO = BASE_DIR / "lab_ML" / "demo_ML"
GH_RACINE = "https://github.com/johan-mac-59/RiskLens_ML/blob/main"
PREPARATION = f"{GH_RACINE}/lab_ML/demo_ML/creation_demo_3.ipynb"
ESSAI = f"{GH_RACINE}/lab_ML/comparatif_global/essai_jeu_de_base.ipynb"
PAUSE = 0.6   # secondes entre deux étapes affichées, pour que le public suive (les temps de calcul affichés sont réels)


@st.cache_resource
def charger_modeles():
    return joblib.load(DOSSIER_DEMO / "demo_3_modeles_plis.joblib")


enregistre = charger_modeles()
PLI_DU_CLIENT = {i: numero for numero, ids in enumerate(enregistre["ids_non_vus"]) for i in ids}
TOUS_LES_IDS = sorted(PLI_DU_CLIENT)


def noter(lot):
    """Probabilité et décision du modèle brut pour chaque client du lot, par le modèle du pli qui ne l'a pas vu."""
    proba, decision = pd.Series(np.nan, index=lot.index), pd.Series(0, index=lot.index)
    plis = lot["ID"].map(PLI_DU_CLIENT)
    for numero, (modele, seuil) in enumerate(zip(enregistre["modeles"], enregistre["seuils"])):
        dans_pli = plis == numero
        if dans_pli.any():
            proba[dans_pli] = modele.predict_proba(lot.loc[dans_pli, enregistre["variables"]])[:, 1]
            decision[dans_pli] = (proba[dans_pli] >= seuil).astype(int)
    return proba, decision.astype(bool)


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


entete_partie_7()
st.header("7.4 Démo 3 : tout le dataset d'origine, une règle métier face à un modèle", anchor="demo-3")
st.markdown(f"""
Cette démonstration porte sur **les {nombre_fr(len(TOUS_LES_IDS))} clients** du dataset d'origine, lus dans la base par l'API, **sans rien retirer**. Elle répond à la problématique sans le travail du projet : **peut-on prévoir le défaut à partir du seul comportement des six derniers mois ?** Deux décisions sont prises en direct pour chaque client, puis comparées au défaut constaté :
- **la règle métier** du projet : après le nettoyage, un client du périmètre au contentieux est déclaré en défaut ;
- **un modèle entraîné sur les données brutes**, sans nettoyage métier ni colonne construite : le CatBoost de l'[essai du comparatif global]({ESSAI}), sur les 23 variables d'origine.

**Chaque client est noté par un modèle qui ne l'a jamais vu.** Un modèle entraîné sur tout le dataset aurait vu tout le dataset : on utilise donc cinq modèles, chacun entraîné sur 80 % des clients ; chaque client est noté par celui qui ne l'a pas appris. Le modèle déclare un client en défaut selon la règle de seuil de l'essai : au plus un bon client signalé pour un défaut attrapé, à la marge.
""")

# ==============================================================================
# 1. TOUT LE DATASET, OU UN LOT
# ==============================================================================
st.subheader("1. Injecter les clients", anchor="lot")
TAILLES = [1000, 5000, 10000, len(TOUS_LES_IDS)]
col_taille, _ = st.columns([1, 2])
taille = col_taille.select_slider("Nombre de clients injectés", TAILLES, value=TAILLES[-1],
                                  format_func=lambda t: f"{nombre_fr(t)} (tout le dataset)" if t == len(TOUS_LES_IDS) else nombre_fr(t))
if "historique_lots_3" not in st.session_state:
    st.session_state.historique_lots_3 = []

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
        declare_regle, place = regle_metier(lot)
        st.write(f"⚖️ **Règle métier** (nettoyage, périmètre, contentieux) : {nombre_fr(declare_regle.sum())} clients déclarés en défaut, "
                 f"en {nombre_fr((time.perf_counter() - debut) * 1000, 0)} millisecondes.")
        time.sleep(PAUSE)
        debut = time.perf_counter()
        proba, declare_modele = noter(lot)
        st.write(f"🤖 **Modèle sur les données brutes** : {nombre_fr(len(lot))} scores calculés en {nombre_fr((time.perf_counter() - debut) * 1000, 0)} millisecondes ; "
                 f"{nombre_fr(declare_modele.sum())} clients déclarés en défaut.")
        time.sleep(PAUSE)
        st.write("🔍 **Vérification** : comparaison avec le défaut constaté en octobre 2005.")
        statut.update(label=f"Lot n° {numero} traité", state="complete", expanded=False)

    y = lot["dpnm"].astype(bool)
    # À nombre égal de clients déclarés : les clients les mieux notés par le modèle, autant que la règle en déclare
    n_regle = int(declare_regle.sum())
    tete_modele = pd.Series(False, index=lot.index)
    tete_modele[proba.sort_values(ascending=False).index[:n_regle]] = True
    st.session_state.dernier_lot_3 = {"numero": numero, "y": y, "regle": declare_regle, "modele": declare_modele,
                                      "tete": tete_modele, "place": place, "proba": proba}
    st.session_state.historique_lots_3.append({
        "Lot": numero, "Clients": len(lot), "Taux de défaut constaté (%)": round(y.mean() * 100, 1),
        "Règle : précision (%)": round((declare_regle & y).sum() / max(declare_regle.sum(), 1) * 100, 1),
        "Modèle, même nombre de déclarés : précision (%)": round((tete_modele & y).sum() / max(tete_modele.sum(), 1) * 100, 1),
        "Déclarés par le modèle et au contentieux (%)": round((declare_modele & declare_regle).sum() / max(declare_modele.sum(), 1) * 100, 1)})

if "dernier_lot_3" in st.session_state:
    d = st.session_state.dernier_lot_3
    y, regle, modele, tete, place = d["y"], d["regle"], d["modele"], d["tete"], d["place"]
    st.markdown(f"**Résultat du lot n° {d['numero']}** : {nombre_fr(len(y))} clients, taux de défaut constaté {nombre_fr(y.mean() * 100, 1)} %")

    st.markdown("**La règle métier face au modèle, sur tous les clients du lot**")
    tableau_html(["", "Défauts détectés", "Taux de rappel", "Précision des défauts prédits", "Clients déclarés en défaut", "Score décisionnel F2"], [
        mesures("Règle métier seule (contentieux)", regle, y),
        mesures("Modèle seul, à son seuil", modele, y),
        mesures("Modèle seul, autant de déclarés que la règle", tete, y),
        mesures("Règle + modèle", regle | modele, y),
    ], largeurs=[28, 15, 12, 15, 15, 15])
    st.caption("« Autant de déclarés que la règle » : les clients les mieux notés par le modèle, en même nombre que les clients au contentieux. "
               "C'est la comparaison la plus juste : à nombre égal d'alertes, lequel a le plus souvent raison ?")

    st.markdown("**Qui le modèle déclare-t-il en défaut ?**")
    lignes = []
    for nom in ["Au contentieux", "Hors contentieux, dans le périmètre", "Hors périmètre (nettoyage, sans encours)"]:
        groupe = modele & (place == nom)
        lignes.append([f"<b>{nom}</b>", nombre_fr(groupe.sum()), f"{nombre_fr(groupe.sum() / max(modele.sum(), 1) * 100, 1)} %",
                       f"{nombre_fr(y[groupe].mean() * 100, 1)} %" if groupe.any() else "–"])
    tableau_html(["Où le projet place ces clients", "Clients déclarés par le modèle", "Part des déclarés", "Taux de défaut constaté"], lignes,
                 largeurs=[40, 20, 20, 20])

    st.markdown("**Les deux décisions se recouvrent-elles ?**")
    lignes = []
    for nom, groupe in (("Déclarés par les deux", regle & modele), ("Par le modèle seulement", modele & ~regle),
                        ("Par la règle seulement", regle & ~modele), ("Par aucun des deux", ~regle & ~modele)):
        lignes.append([f"<b>{nom}</b>", nombre_fr(groupe.sum()), f"{nombre_fr(y[groupe].mean() * 100, 1)} %" if groupe.any() else "–",
                       f"{nombre_fr((groupe & y).sum() / max(y.sum(), 1) * 100, 1)} %"])
    tableau_html(["", "Clients", "Taux de défaut constaté", "Part de tous les défauts"], lignes, largeurs=[40, 20, 20, 20])

    # Réponse à la problématique, chiffres calculés en direct
    part_ctx = (modele & regle).sum() / max(modele.sum(), 1) * 100
    prec_regle = (regle & y).sum() / max(regle.sum(), 1) * 100
    prec_tete = (tete & y).sum() / max(tete.sum(), 1) * 100
    rappel_union = ((regle | modele) & y).sum() / max(y.sum(), 1) * 100
    st.info(f"""
**Ce que répond cette démonstration à la problématique.** Sur les données brutes, le comportement des six derniers mois permet de prévoir une partie des défauts : règle et modèle ensemble en détectent {nombre_fr(rappel_union, 0)} %. Mais **{nombre_fr(part_ctx, 0)} % des clients que le modèle déclare en défaut sont des clients au contentieux**, que la règle métier repère déjà, sans machine learning et de façon explicable. À nombre égal d'alertes, la règle a raison dans {nombre_fr(prec_regle, 0)} % des cas, le modèle dans {nombre_fr(prec_tete, 0)} %. Le gros de ce qui est prévisible tient donc dans les retards de paiement que la banque a déjà codifiés : c'est ce qui a conduit le projet à confier ces clients à la règle, et le reste au modèle (parties 5 et 6).
""")

if st.session_state.historique_lots_3:
    st.subheader("Les lots déjà injectés", anchor="historique")
    st.dataframe(pd.DataFrame(st.session_state.historique_lots_3), hide_index=True, width='stretch')
    if st.button("Effacer les lots"):
        st.session_state.historique_lots_3 = []
        st.session_state.pop("dernier_lot_3", None)
        st.rerun()

st.caption(f"Modèles : CatBoost de l'essai du comparatif global, variante complète (23 variables d'origine), 5 modèles de plis, "
           f"identiques à ceux de l'essai (contrôle dans le [notebook de préparation]({PREPARATION})).")
