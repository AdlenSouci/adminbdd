# -*- coding: utf-8 -*-
"""
Fiches de révision HTML : tout le texte des extractions PDF / .txt,
 découpé en sections (titres + paragraphes lisibles).

Usage (racine du projet) :  python docs/build_revision_fiches.py
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = Path(__file__).resolve().parent
EX = ROOT / "_pdf_extracts"

COURSES = [
    (EX / "Modèle_Conceptuel_de_Données_MCD.txt", "revision-01-mcd.html", "Fiche — MCD (MERISE)", "Modèle Conceptuel de Données (MCD).pdf"),
    (EX / "Du_MCD_au_MLD.txt", "revision-02-mcd-mld.html", "Fiche — Du MCD au MLD", "Du MCD au MLD.pdf"),
    (EX / "Normalisation_des_bases_de_données.txt", "revision-03-normalisation.html", "Fiche — Normalisation", "Normalisation des bases de données.pdf"),
    (EX / "DDL_-_Data_Definition_Language.txt", "revision-04-ddl.html", "Fiche — DDL", "DDL - Data Definition Language.pdf"),
    (EX / "DDL_Avancé_et_Optimisation_des_Schémas.txt", "revision-05-ddl-avance.html", "Fiche — DDL avancé", "DDL Avancé et Optimisation des Schémas.pdf"),
    (EX / "Sauvegarde_Restauration_et_Résilience.txt", "revision-06-sauvegarde.html", "Fiche — Sauvegarde & résilience", "Sauvegarde, Restauration et Résilience.pdf"),
    (ROOT / "explain.txt", "revision-07-explain.html", "Fiche — EXPLAIN", "explain.txt"),
    (ROOT / "gestion_droit.txt", "revision-08-droits.html", "Fiche — Droits & utilisateurs", "gestion_droit.txt"),
]


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def is_h3_title(line: str) -> bool:
    s = line.strip()
    if len(s) < 4 or len(s) > 110:
        return False
    if s.endswith(".") and len(s) > 45:
        return False
    if re.match(
        r"^(?:\d+[\.\)]\s+)?(?:"
        r"Les |La |Le |L'|Un |Une |Des |Exemple|Définitions?|Objectifs|Introduction|Conclusion|"
        r"Première|Deuxième|Troisième|Qu'est|Qu’|Règle|Règles|Étape |Outils |Rappel|Vue |"
        r"Identification|Création|Transform|Cardinalités|Associat|Identifian|Clé |Clés |Forme |Pourquoi |"
        r"Typ|MERISE|MCD|MLD|MPD|Normalisation|Syntaxe|Commandes|Types |Contrainte|Contraintes|"
        r"Modifier|Exemples|FAQ|Bonnes |Checklist|Points |Exercice|Correction|Ressources|Résumé|"
        r"Comparaison|Stratég|Partition|Index |OLTP|Atelier|Questions|DDL|DML|Sauvegarde|PITR|"
        r"RPO|RTO|Automatisation|Scénarios|Conséquences|Types de|Complète|Incrément|Différent|"
        r"Point-in|ExPLAIN|MySQL|PostgreSQL|Nœud|Plan |Analyse |Problème|Suggestions|Gestion|"
        r"Concepts|Transmission|Révocation|Les rôles|Création d'|Les droits|Pour |"
        r"Exemple de|Décomposition|Suite\b|Merci|Objectifs du cours"
        r")",
        s,
        re.I,
    ):
        return True
    if re.match(r"^[A-ZÀÉÈÊÏÔÙ][A-Za-zÀ-ÿ0-9 ,'\-–]{2,85}$", s):
        if s.isupper() and len(s) > 12:
            return True
        if not re.search(r"[a-zàéèêëïôùûç]{4,}", s):
            return True
    return False


def chunk_to_html(chunk: str) -> str:
    chunk = chunk.strip()
    if not chunk:
        return ""
    lines = chunk.split("\n")
    first = lines[0].strip()
    rest_lines = [ln.rstrip() for ln in lines[1:]]

    if is_h3_title(first) and rest_lines:
        parts = [f"<h3>{esc(first)}</h3>"]
        body = "\n".join(rest_lines).strip()
        if "\t" in body or (body.count("\n") >= 2 and re.search(r"\t|  {2,}", body)):
            parts.append(f'<div class="table-lines">{esc(body)}</div>')
        else:
            for para in re.split(r"\n{2,}", body):
                para = para.strip()
                if not para:
                    continue
                sub = [x for x in para.split("\n") if x.strip()]
                if len(sub) >= 2 and all(
                    re.match(r"^[-•●]\s|^\d+[\.\)]\s", x.strip()) or x.strip().startswith("-") for x in sub
                ):
                    lis = "".join(f"<li>{esc(re.sub(r'^[-•●\d\.\)\s]+', '', x.strip()))}</li>" for x in sub)
                    parts.append(f"<ul>{lis}</ul>")
                else:
                    parts.append("<p>" + "<br>\n".join(esc(x) for x in sub) + "</p>")
        return "\n".join(parts)

    # Bloc sans titre : paragraphes
    parts: list[str] = []
    for para in re.split(r"\n{2,}", chunk):
        para = para.strip()
        if not para:
            continue
        sub = [x for x in para.split("\n") if x.strip()]
        if not sub:
            continue
        if "\t" in para:
            parts.append(f'<div class="table-lines">{esc(para)}</div>')
        elif len(sub) >= 2 and sum(1 for x in sub if re.match(r"^[-•●]\s|^\d+[\.\)]\s", x.strip())) >= max(2, len(sub) // 2):
            lis = "".join(f"<li>{esc(re.sub(r'^[-•●\d\.\)\s]+', '', x.strip()))}</li>" for x in sub)
            parts.append(f"<ul>{lis}</ul>")
        else:
            parts.append("<p>" + "<br>\n".join(esc(x) for x in sub) + "</p>")
    return "\n".join(parts)


def text_to_article(raw: str) -> str:
    raw = raw.replace("\r\n", "\n").replace("\r", "\n").strip()
    # Grosses parties : triple saut de ligne ou titre tout en ligne seule majuscule
    big_parts = re.split(r"\n{3,}", raw)
    out: list[str] = []
    for part in big_parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n")
        fl = lines[0].strip()
        if len(fl) <= 85 and fl.isupper() and len(fl) >= 10 and len(lines) > 1:
            out.append(f"<h2>{esc(fl)}</h2>")
            part = "\n".join(lines[1:]).strip()
        chunks = re.split(r"\n\s*\n", part)
        for ch in chunks:
            ch = ch.strip()
            if not ch:
                continue
            inner = chunk_to_html(ch)
            if inner:
                out.append(f"<section>\n{inner}\n</section>")
    return "\n".join(out)


PDF_SOURCE = {
    "revision-01-mcd.html": "pdf-source-01-mcd.html",
    "revision-02-mcd-mld.html": "pdf-source-02-mcd-mld.html",
    "revision-03-normalisation.html": "pdf-source-03-normalisation.html",
    "revision-04-ddl.html": "pdf-source-04-ddl.html",
    "revision-05-ddl-avance.html": "pdf-source-05-ddl-avance.html",
    "revision-06-sauvegarde.html": "pdf-source-06-sauvegarde.html",
    "revision-07-explain.html": "pdf-source-07-explain.html",
    "revision-08-droits.html": "pdf-source-08-droits.html",
}


def main() -> None:
    for src, out_name, title, label in COURSES:
        if not src.is_file():
            print("SKIP", src)
            continue
        raw = src.read_text(encoding="utf-8", errors="replace")
        article = text_to_article(raw)
        fn = PDF_SOURCE[out_name]
        page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="revision.css?v=2">
</head>
<body>
  <a class="back" href="index.html">← Accueil</a>
  <header>
    <h1>{esc(title)}</h1>
    <p class="sub">Basé sur <strong>{esc(label)}</strong> — tout le texte extrait, mis en forme pour réviser.</p>
  </header>
  <article>
{article}
  </article>
  <footer><a href="index.html">Accueil</a> · <a href="{fn}">Version texte brut</a></footer>
</body>
</html>
"""
        (DOCS / out_name).write_text(page, encoding="utf-8")
        print("OK", out_name)


if __name__ == "__main__":
    main()
