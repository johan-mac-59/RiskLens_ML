from streamlit_pages.commun import *

# ==============================================================================
# ANNEXE : LES SOURCES DU PROJET
# La page affiche docs/sources.md tel quel : une seule liste à tenir à jour, le document et la page ne peuvent pas diverger.
# Les liens relatifs du document (PDF, autres documents de docs/) sont convertis en liens GitHub.
# ==============================================================================
GH_DOCS = "https://github.com/johan-mac-59/RiskLens_ML/blob/main/docs/"

texte = (BASE_DIR / "docs" / "sources.md").read_text(encoding="utf-8")
texte = texte.split("\n", 1)[1]                                          # titre du document remplacé par celui de la page
texte = re.sub(r"\]\((?!https?://)([^)]+)\)", lambda m: f"]({GH_DOCS}{m.group(1)})", texte)
texte = texte.replace("$", "\\$")                                        # NT$ : pas de formule mathématique

st.title("📚 Annexe : les sources du projet")
# Tous les tableaux du document à la même largeur, avec les mêmes colonnes (source, ce qu'elle appuie, utilisée dans) :
# sans cela, chaque tableau Markdown se dimensionne selon son contenu
st.markdown("""<style>
.st-key-sources table { width: 100%; table-layout: fixed; }
.st-key-sources th:nth-child(1), .st-key-sources td:nth-child(1) { width: 42%; }
.st-key-sources th:nth-child(2), .st-key-sources td:nth-child(2) { width: 38%; }
.st-key-sources th:nth-child(3), .st-key-sources td:nth-child(3) { width: 20%; }
</style>""", unsafe_allow_html=True)
st.container(key="sources").markdown(texte)
