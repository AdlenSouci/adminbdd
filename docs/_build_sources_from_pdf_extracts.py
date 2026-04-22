"""
Genere dans docs/ les pages pdf-source-*.html a partir du texte EXTRAIT des PDF
(dossier _pdf_extracts/) + explain.txt et gestion_droit.txt a la racine du projet.

A lancer depuis la racine du depot :  python docs/_build_sources_from_pdf_extracts.py
"""
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = Path(__file__).resolve().parent
EXTRACTS = ROOT / "_pdf_extracts"

# (fichier source relatif a ROOT ou EXTRACTS, page html dans docs/, titre affiche)
MAPPING = [
    (EXTRACTS / "Modèle_Conceptuel_de_Données_MCD.txt", "pdf-source-01-mcd.html", "Source PDF — MCD (texte extrait)"),
    (EXTRACTS / "Du_MCD_au_MLD.txt", "pdf-source-02-mcd-mld.html", "Source PDF — Du MCD au MLD (texte extrait)"),
    (EXTRACTS / "Normalisation_des_bases_de_données.txt", "pdf-source-03-normalisation.html", "Source PDF — Normalisation (texte extrait)"),
    (EXTRACTS / "DDL_-_Data_Definition_Language.txt", "pdf-source-04-ddl.html", "Source PDF — DDL (texte extrait)"),
    (EXTRACTS / "DDL_Avancé_et_Optimisation_des_Schémas.txt", "pdf-source-05-ddl-avance.html", "Source PDF — DDL avancé (texte extrait)"),
    (EXTRACTS / "Sauvegarde_Restauration_et_Résilience.txt", "pdf-source-06-sauvegarde.html", "Source PDF — Sauvegarde & résilience (texte extrait)"),
    (ROOT / "explain.txt", "pdf-source-07-explain.html", "Source — EXPLAIN (fichier cours .txt)"),
    (ROOT / "gestion_droit.txt", "pdf-source-08-droits.html", "Source — Gestion des droits (fichier cours .txt)"),
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
        # evite paragraphes geants : coupe sur lignes vides internes faibles
        if len(p) > 8000:
            for chunk in p.split("\n"):
                chunk = chunk.strip()
                if chunk:
                    out.append(chunk)
        else:
            out.append(p)
    return out


def build_page(title: str, paragraphs: list[str], back_href: str, back_label: str) -> str:
    body = "".join(f"<p class=\"src\">{html.escape(p).replace(chr(10), '<br>')}</p>" for p in paragraphs)
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="styles.css">
  <style>
    .src {{ font-size: 0.92rem; line-height: 1.5; margin: 0.6rem 0; white-space: normal; word-break: break-word; }}
    .banner {{ background: var(--card); border: 1px solid var(--border); padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.88rem; color: var(--muted); }}
  </style>
</head>
<body>
  <a class="back" href="index.html">Accueil</a>
  <a class="back" href="{html.escape(back_href, quote=True)}">{html.escape(back_label)}</a>
  <header>
    <h1>{html.escape(title)}</h1>
    <p class="sub">Contenu genere automatiquement depuis l'extraction texte du support (sans mise en page d'origine).</p>
  </header>
  <div class="banner">Ce texte provient exclusivement du fichier source indique dans le script de generation — pas une reecriture par l'IA.</div>
  <article>
{body}
  </article>
  <footer><a href="{html.escape(back_href, quote=True)}">Retour fiche</a></footer>
</body>
</html>
"""


def main() -> None:
    for src_path, out_name, title in MAPPING:
        if not src_path.is_file():
            print("SKIP (manquant):", src_path)
            continue
        raw = src_path.read_text(encoding="utf-8", errors="replace")
        paras = text_to_paragraphs(raw)
        # Lien retour vers la fiche courte correspondante
        parts = out_name.replace(".html", "").split("-")
        num = parts[2] if len(parts) > 2 else "01"
        fiche = {
            "01": ("01-mcd.html", "Fiche 01"),
            "02": ("02-mcd-mld.html", "Fiche 02"),
            "03": ("03-normalisation.html", "Fiche 03"),
            "04": ("04-ddl.html", "Fiche 04"),
            "05": ("05-ddl-avance.html", "Fiche 05"),
            "06": ("06-sauvegarde.html", "Fiche 06"),
            "07": ("07-explain.html", "Fiche 07"),
            "08": ("08-droits.html", "Fiche 08"),
        }.get(num, ("index.html", "Accueil"))
        page = build_page(title, paras, fiche[0], fiche[1])
        out_path = DOCS / out_name
        out_path.write_text(page, encoding="utf-8")
        print("OK", out_name, "paras", len(paras), "chars", len(raw))


if __name__ == "__main__":
    main()
