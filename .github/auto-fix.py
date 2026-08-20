#!/usr/bin/env python3
"""Auto-correcteur : corrige les erreurs sûres uniquement.
- JAMAIS de nouveau fichier
- JAMAIS de CSS ajoute dans le HTML
- Si une correction necessite le CSS : on le signale et on demande a l'utilisateur
"""

import re
import os
import sys

def lister_erreurs(rapport_texte):
    """Analyse la sortie du validateur et extrait (fichier, ligne, message, regle)."""
    erreurs = []
    fichier = ""
    for ligne in rapport_texte.splitlines():
        if re.match(r'^[/.]', ligne):
            fichier = ligne
        m = re.match(r'^\s+(\d+):(\d+)\s+error\s+(.*?)\s*$', ligne)
        if m and fichier:
            num = int(m.group(1))
            message = m.group(3).strip()
            regle = message.split()[-1] if message.split() else ""
            erreurs.append((fichier, num, message, regle))
    return erreurs

def appliquer_corrections(erreurs):
    """Applique uniquement les corrections sûres.
    Retourne (rapport_corrections, questions_pour_utilisateur)."""
    rapport = []
    questions = []
    fichiers_modifies = {}
    css_regles = []  # collecte des styles trouves (pour les signaler)

    for fichier, num, message, regle in erreurs:
        if not os.path.exists(fichier):
            continue
        if fichier not in fichiers_modifies:
            with open(fichier, encoding='utf-8') as f:
                fichiers_modifies[fichier] = f.readlines()

        lignes = fichiers_modifies[fichier]
        if num > len(lignes):
            continue
        ligne_avant = lignes[num - 1].rstrip('\n')
        corrige = False

        # 1. Espaces en fin de ligne (sûr a 100%)
        if regle == 'no-trailing-whitespace':
            nouvelle = ligne_avant.rstrip()
            if nouvelle != ligne_avant:
                lignes[num - 1] = nouvelle + '\n'
                rapport.append((fichier, num, "no-trailing-whitespace",
                                ligne_avant, nouvelle, "Espaces en fin de ligne supprimes"))
                corrige = True

        # 2. Bouton sans type (sûr)
        elif regle == 'no-implicit-button-type':
            m = re.search(r'<button\b([^>]*)>', ligne_avant)
            if m and 'type=' not in m.group(1):
                nouvelle = re.sub(r'<button\b', '<button type="button"', ligne_avant, count=1)
                lignes[num - 1] = nouvelle + '\n'
                rapport.append((fichier, num, "no-implicit-button-type",
                                ligne_avant, nouvelle, 'Ajout de type="button"'))
                corrige = True

        # 3. Image sans alt (sûr : alt vide pour image decorative)
        elif regle == 'wcag/h37':
            if '<img' in ligne_avant and 'alt=' not in ligne_avant:
                nouvelle = re.sub(r'(<img[^>]*?)(/?>)', r'\1 alt=""\2', ligne_avant, count=1)
                lignes[num - 1] = nouvelle + '\n'
                rapport.append((fichier, num, "wcag/h37",
                                ligne_avant, nouvelle, 'Ajout de alt=""'))
                corrige = True

        # 4. Style inline -> NE PAS CORRIGER, DEMANDER
        elif regle == 'no-inline-style':
            m = re.search(r'style="([^"]*)"', ligne_avant)
            if m:
                questions.append((fichier, num, m.group(1), ligne_avant))
                corrige = False

        # 5. Lien sans texte -> aria-label si icone connue (sûr)
        elif regle == 'wcag/h30':
            icons = re.findall(r'fa-([a-z0-9-]+)', ligne_avant)
            if icons and 'aria-label' not in ligne_avant:
                icon = icons[-1].replace('-', ' ').title()
                nouvelle = re.sub(r'(<a[^>]*?)(>)', rf'\1 aria-label="{icon}"\2', ligne_avant, count=1)
                lignes[num - 1] = nouvelle + '\n'
                rapport.append((fichier, num, "wcag/h30",
                                ligne_avant, nouvelle, f'Ajout de aria-label="{icon}"'))
                corrige = True

        # 6. Balise fermante orpheline (sûr)
        elif regle == 'close-order':
            m = re.match(r'^\s*</([a-z0-9]+)>\s*$', ligne_avant)
            if m:
                del lignes[num - 1]
                rapport.append((fichier, num, "close-order",
                                ligne_avant, "(ligne supprimee)", "Balise fermante orpheline supprimee"))
                corrige = True

    # Ecrire UNIQUEMENT les fichiers existants modifies
    fichiers_touches = set()
    for fichier, num, regle, avant, apres, explication in rapport:
        fichiers_touches.add(fichier)
    for fichier, lignes in fichiers_modifies.items():
        if fichier in fichiers_touches:
            with open(fichier, 'w', encoding='utf-8') as f:
                f.writelines(lignes)

    return rapport, questions

if __name__ == '__main__':
    rapport_path = sys.argv[1] if len(sys.argv) > 1 else 'rapport.txt'
    try:
        with open(rapport_path, encoding='utf-8') as f:
            rapport_texte = f.read()
    except FileNotFoundError:
        print("Rapport introuvable")
        sys.exit(0)

    erreurs = lister_erreurs(rapport_texte)
    if not erreurs:
        print("Aucune erreur a corriger")
        sys.exit(0)

    print(f"=== {len(erreurs)} erreur(s) detectee(s) ===")
    for f, n, msg, regle in erreurs:
        print(f"  {os.path.basename(f)}:{n} - {regle}")

    corrections, questions = appliquer_corrections(erreurs)

    print("\n=== CORRECTIONS APPLIQUEES ===")
    for fichier, num, regle, avant, apres, explication in corrections:
        print(f"\n[{regle}] {os.path.basename(fichier)} ligne {num}")
        print(f"  AVANT  : {avant}")
        print(f"  APRES  : {apres}")
        print(f"  ({explication})")

    if questions:
        print("\n=== QUESTIONS POUR L'UTILISATEUR ===")
        for fichier, num, style, ligne in questions:
            print(f"\n[style inline] {os.path.basename(fichier)} ligne {num}")
            print(f"  Code : {ligne}")
            print(f"  Style trouve : {style}")
            print("  -> Non corrige automatiquement car cela necessiterait du CSS.")
            print("  -> Dis-moi : 'corrige en mettant le style dans style.css' ou 'supprime le style'")

    print(f"\n{len(corrections)} correction(s) appliquee(s), {len(questions)} question(s) pour toi")
