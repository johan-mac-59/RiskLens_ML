#!/usr/bin/env python3
"""
Exécute une série de notebooks Jupyter (.ipynb) les uns après les autres,
en ligne de commande (via `jupyter nbconvert --execute`), pour éviter les
soucis de VS Code : Run All qui ne démarre pas, ou plusieurs notebooks qui
se lancent en même temps quand on clique sur plusieurs onglets.

Comportement :
- Traite les notebooks en ordre alphabétique.
- Si un notebook plante, l'erreur est logguée et le script passe au suivant
  (il ne s'arrête jamais en cours de route).
- Écrase les fichiers originaux en place avec leurs nouveaux outputs
  (comportement standard d'un "Run All" classique).
- Écrit un log détaillé sur disque + un résumé final à l'écran.

Utilisation (le plus simple, depuis n'importe où) :
    python run_all_notebooks.py

Par défaut, il cherche tous les .ipynb dans le dossier où SE TROUVE CE SCRIPT,
et récursivement dans tous ses sous-dossiers. Placer ce fichier à la racine de
ton dossier ML (au même niveau que tes sous-dossiers correction_niveauX) suffit.

Options utiles :
    --dir "chemin"           cherche ailleurs qu'à côté du script
    --pattern "*.ipynb"      motif de sélection (défaut : "**/*.ipynb", récursif)
    --timeout 3600           timeout en secondes par cellule (défaut: 3600 = 1h)
    --kernel python3         force un kernel précis (par défaut : celui du notebook)
    --dry-run                liste juste les notebooks qui seraient exécutés, sans rien lancer

Prérequis (une seule fois) :
    pip install nbconvert ipykernel

IMPORTANT : ferme les onglets de ces notebooks dans VS Code avant de lancer
ce script (ou recharge-les après coup avec "Revert File"), sinon VS Code peut
afficher une version obsolète ou proposer d'écraser le fichier au moment où
tu cliques dessus.
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(description="Exécute des notebooks Jupyter séquentiellement.")
    parser.add_argument(
        "--dir", type=str, default=str(SCRIPT_DIR),
        help="Dossier racine où chercher les notebooks (défaut : dossier où se trouve ce script)",
    )
    parser.add_argument(
        "--pattern", type=str, default="**/*.ipynb",
        help="Motif de sélection des fichiers, récursif par défaut (défaut : **/*.ipynb)",
    )
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout en secondes par cellule (défaut : 3600)")
    parser.add_argument("--kernel", type=str, default=None, help="Nom du kernel à forcer (défaut : celui du notebook)")
    parser.add_argument("--dry-run", action="store_true", help="Affiche juste la liste des notebooks, sans exécuter")
    return parser.parse_args()


def run_all_notebooks():
    args = parse_args()
    base_dir = Path(args.dir).resolve()

    if not base_dir.is_dir():
        print(f"❌ Dossier introuvable : {base_dir}")
        sys.exit(1)

    # Sélection des notebooks, ordre alphabétique, on ignore les checkpoints Jupyter
    notebooks = sorted(
        p for p in base_dir.glob(args.pattern)
        if ".ipynb_checkpoints" not in p.parts
    )

    if not notebooks:
        print(f"❌ Aucun notebook trouvé dans {base_dir} avec le motif '{args.pattern}'")
        sys.exit(1)

    print(f"📒 {len(notebooks)} notebook(s) trouvé(s) dans {base_dir} (et sous-dossiers) :")
    for nb in notebooks:
        print(f"   - {nb.relative_to(base_dir)}")
    print()

    if args.dry_run:
        print("(--dry-run : rien n'a été exécuté)")
        return

    log_path = base_dir / f"run_all_notebooks_{datetime.now():%Y%m%d_%H%M%S}.log"
    results = []  # (nom, statut, durée_sec, extrait_erreur)

    with open(log_path, "w", encoding="utf-8") as log_file:

        def log(msg):
            print(msg)
            log_file.write(msg + "\n")
            log_file.flush()

        log(f"=== Démarrage : {datetime.now():%Y-%m-%d %H:%M:%S} ===")
        log(f"Dossier : {base_dir}")
        log(f"{len(notebooks)} notebook(s) à traiter, dans l'ordre alphabétique.\n")

        for i, nb_path in enumerate(notebooks, start=1):
            rel_path = nb_path.relative_to(base_dir)
            log(f"[{i}/{len(notebooks)}] ▶ Exécution de {rel_path} ...")
            start = time.time()

            cmd = [
                sys.executable, "-m", "jupyter", "nbconvert",
                "--to", "notebook",
                "--execute",
                "--inplace",
                f"--ExecutePreprocessor.timeout={args.timeout}",
                str(nb_path),
            ]
            if args.kernel:
                cmd.insert(-1, f"--ExecutePreprocessor.kernel_name={args.kernel}")

            proc = subprocess.run(cmd, capture_output=True, text=True)
            duration = time.time() - start

            if proc.returncode == 0:
                log(f"    ✅ OK en {duration:.0f}s")
                results.append((str(rel_path), "OK", duration, ""))
            else:
                # On garde les dernières lignes de stderr, souvent l'essentiel de l'erreur
                error_excerpt = "\n".join(proc.stderr.strip().splitlines()[-15:])
                log(f"    ❌ ÉCHEC en {duration:.0f}s")
                log(f"    --- Extrait de l'erreur ---\n{error_excerpt}\n    ---------------------------")
                results.append((str(rel_path), "ÉCHEC", duration, error_excerpt))

            log("")  # ligne vide entre deux notebooks

        # Rapport final
        n_ok = sum(1 for r in results if r[1] == "OK")
        n_fail = sum(1 for r in results if r[1] == "ÉCHEC")
        total_time = sum(r[2] for r in results)

        log("=" * 60)
        log(f"RÉSUMÉ : {n_ok}/{len(results)} réussis, {n_fail}/{len(results)} en échec")
        log(f"Temps total : {total_time / 60:.1f} min")
        log("=" * 60)

        if n_fail:
            log("\nNotebooks en échec :")
            for name, status, duration, err in results:
                if status == "ÉCHEC":
                    log(f"  - {name}")

        log(f"\nLog complet écrit dans : {log_path}")

    if n_fail:
        sys.exit(1)  # utile si tu enchaînes ce script dans un pipeline plus large


run_all_notebooks()
