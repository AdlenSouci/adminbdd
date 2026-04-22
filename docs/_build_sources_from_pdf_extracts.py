"""
Genere docs/pdf-source-*.html = UNIQUEMENT le texte lu depuis :
  - _pdf_extracts/*.txt (extraction des PDF)
  - explain.txt et gestion_droit.txt a la racine du projet

Usage (racine du projet) :  python docs/_build_sources_from_pdf_extracts.py
"""
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = Path(__file__).resolve().parent
EXTRACTS = ROOT / "_pdf_extracts"

MAPPING = [
    (EXTRACTS / "Modèle_Conceptuel_de_Données_MCD.txt", "pdf-source-01-mcd.html", "PDF — Modèle conceptuel de données (MCD)", "Modèle_Conceptuel_de_Données_(MCD).pdf"),
    (EXTRACTS / "Du_MCD_au_MLD.txt", "pdf-source-02-mcd-mld.html", "PDF — Du MCD au MLD", "Du_MCD_au_MLD.pdf"),
    (EXTRACTS / "Normalisation_des_bases_de_données.txt", "pdf-source-03-normalisation.html", "PDF — Normalisation des bases de données", "Normalisation_des_bases_de_données_.pdf"),
    (EXTRACTS / "DDL_-_Data_Definition_Language.txt", "pdf-source-04-ddl.html", "PDF — DDL (Data Definition Language)", "DDL_-_Data_Definition_Language.pdf"),
    (EXTRACTS / "DDL_Avancé_et_Optimisation_des_Schémas.txt", "pdf-source-05-ddl-avance.html", "PDF — DDL avancé et optimisation des schémas", "DDL_Avancé_et_Optimisation_des_Schémas.pdf"),
    (EXTRACTS / "Sauvegarde_Restauration_et_Résilience.txt", "pdf-source-06-sauvegarde.html", "PDF — Sauvegarde, restauration et résilience", "Sauvegarde,_Restauration_et_Résilience.pdf"),
    (ROOT / "explain.txt", "pdf-source-07-explain.html", "Fichier cours — EXPLAIN", "explain.txt"),
    (ROOT / "gestion_droit.txt", "pdf-source-08-droits.html", "Fichier cours — Gestion des droits", "gestion_droit.txt"),
]


def text_to_paragraphs(raw: str) -> list[str]:
    raw = raw.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not raw:
        return []
    parts = raw.split("\n\n")
    out: list[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) > 8000:
            for chunk in p.split("\n"):
                chunk = chunk.strip()
                if chunk:
                    out.append(chunk)
        else:
            out.append(p)
    return out


def build_page(title: str, source_filename: str, paragraphs: list[str]) -> str:
    body = "".join(
        f"<p class=\"src\">{html.escape(p).replace(chr(10), '<br>')}</p>" for p in paragraphs
    )
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="styles.css">
  <style>
    .src {{ font-size: 0.92rem; line-height: 1.5; margin: 0.6rem 0; word-break: break-word; }}
    .banner {{ background: var(--card); border: 1px solid var(--border); padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.88rem; color: var(--muted); }}
  </style>
</head>
<body>
  <a class="back" href="index.html">Accueil</a>
  <header>
    <h1>{html.escape(title)}</h1>
    <p class="sub">Fichier source : <code>{html.escape(source_filename)}</code> — contenu copié depuis l’extraction automatique (pas de réécriture).</p>
  </header>
  <div class="banner">Si un mot ou une mise en page manque, c’est une limite de l’extraction PDF → texte, pas un autre cours.</div>
  <article>
{body}
  </article>
  <footer><a href="index.html">Retour accueil</a></footer>
</body>
</html>
"""


def main() -> None:
    for src_path, out_name, title, source_label in MAPPING:
        if not src_path.is_file():
            print("SKIP (manquant):", src_path)
            continue
        raw = src_path.read_text(encoding="utf-8", errors="replace")
        paras = text_to_paragraphs(raw)
        page = build_page(title, source_label, paras)
        (DOCS / out_name).write_text(page, encoding="utf-8")
        print("OK", out_name, "paras", len(paras), "chars", len(raw))


if __name__ == "__main__":
    main()
