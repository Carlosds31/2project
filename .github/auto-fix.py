#!/usr/bin/env python3
"""Auto-correcteur : corrige les erreurs detectees par les validateurs.
Sans modification de design, corrige uniquement les erreurs sûres."""

import re
import sys
import os

def lister_erreurs(rapport_texte):
    """Analyse la sortie html-validate et extrait (fichier, ligne, message, regle)."""
    erreurs = []
    fichier = ""
    for ligne in rapport_texte.splitlines():
        if re.match(r'^[/.]', ligne):
            fichier = ligne
        m = re.match(r'^\s+(\d+):(\d+)\s+error\s+(.*?)\s*$', ligne)
        if m and fichier:
            num = int(m.group(1))
            message = m.group(3).strip()
            # Extraire la regle (dernier mot)
            regle = message.split()[-1] if message.split() else ""
            erreurs.append((fichier, num, message, regle))
    return erreurs

def appliquer_corrections(erreurs):
    """Applique les corrections sûres. Retourne le rapport avant/apres."""
    rapport = []
    fichiers_modifies = {}

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

        # 1. Espaces en fin de ligne
        if regle == 'no-trailing-whitespace':
            nouvelle = ligne_avant.rstrip()
            if nouvelle != ligne_avant:
                lignes[num - 1] = nouvelle + '\n'
                rapport.append(("no-trailing-whitespace", fichier, num,
                                ligne_avant, nouvelle, "Espaces supprimes en fin de ligne"))
                corrige = True

        # 2. Bouton sans attribut type
        elif regle == 'no-implicit-button-type':
            m = re.search(r'<button\b([^>]*)>', ligne_avant)
            if m and 'type=' not in m.group(1):
                nouvelle = re.sub(r'<button\b', '<button type="button"', ligne_avant, count=1)
                lignes[num - 1] = nouvelle + '\n'
                rapport.append(("no-implicit-button-type", fichier, num,
                                ligne_avant, nouvelle, "Ajout de type=\"button\""))
                corrige = True

        # 3. Image sans alt
        elif regle == 'wcag/h37':
            if '<img' in ligne_avant and 'alt=' not in ligne_avant:
                nouvelle = re.sub(r'(<img[^>]*?)(/?>)', r'\1 alt=""\2', ligne_avant, count=1)
                lignes[num - 1] = nouvelle + '\n'
                rapport.append(("wcag/h37", fichier, num,
                                ligne_avant, nouvelle, "Ajout de alt=\"\" (image decorative)"))
                corrige = True

        # 4. Style inline -> deplace dans le CSS
        elif regle == 'no-inline-style':
            m = re.search(r'style="([^"]*)"', ligne_avant)
            if m:
                style = m.group(1)
                # Generer une classe unique
                cls = f"auto-fix-{num}"
                # Remplacer style par class
                nouvelle = ligne_avant.replace(f'style="{style}"', f'class="{cls}"')
                lignes[num - 1] = nouvelle + '\n'
                rapport.append(("no-inline-style", fichier, num,
                                ligne_avant, nouvelle,
                                f"Style deplace vers CSS (classe .{cls})"))
                # Enregistrer la regle CSS a ajouter
                css_regles.append(f".{cls} {{ {style} }}")
                corrige = True

        # 5. Lien sans texte -> aria-label si icone connue
        elif regle == 'wcag/h30':
            icons = re.findall(r'fa-([a-z0-9-]+)', ligne_avant)
            if icons and 'aria-label' not in ligne_avant:
                icon = icons[-1].replace('-', ' ').title()
                nouvelle = re.sub(r'(<a[^>]*?)(>)', rf'\1 aria-label="{icon}"\2', ligne_avant, count=1)
                lignes[num - 1] = nouvelle + '\n'
                rapport.append(("wcag/h30", fichier, num,
                                ligne_avant, nouvelle, f"Ajout de aria-label=\"{icon}\""))
                corrige = True

        # 6. Balise fermante orpheline
        elif regle == 'close-order':
            m = re.match(r'^\s*</([a-z0-9]+)>\s*$', ligne_avant)
            if m:
                del lignes[num - 1]
                rapport.append(("close-order", fichier, num,
                                ligne_avant, "(ligne supprimee)", "Balise fermante orpheline supprimee"))
                corrige = True

    # Ecrire les fichiers modifies (jamais de nouveaux fichiers)
    fichiers_touches = set()
    for regle, fichier, num, avant, apres, explication in rapport:
        if num != 0:
            fichiers_touches.add(fichier)

    # Regles CSS : dans un fichier CSS existant OU un bloc <style> dans le HTML
    if css_regles:
        css_file = None
        for f in os.listdir('.'):
            if f.endswith('.css'):
                css_file = f
                break
        if css_file:
            with open(css_file, 'a', encoding='utf-8') as f:
                f.write('\n/* Corrections automatiques */\n')
                for r in css_regles:
                    f.write(r + '\n')
            rapport.append(("CSS", css_file, 0, "", "\n".join(css_regles),
                            "Regles CSS ajoutees dans le fichier CSS existant"))
        else:
            for fichier_html in fichiers_modifies:
                if fichier_html.endswith('.html'):
                    lignes = fichiers_modifies[fichier_html]
                    idx_close_head = None
                    for i, l in enumerate(lignes):
                        if '</head>' in l:
                            idx_close_head = i
                            break
                    if idx_close_head is not None:
                        style_block = '<style>\n/* Corrections automatiques */\n'
                        for r in css_regles:
                            style_block += r + '\n'
                        style_block += '</style>\n'
                        lignes.insert(idx_close_head, style_block)
                        fichiers_touches.add(fichier_html)
                        rapport.append(("CSS", fichier_html, 0, "",
                                        "\n".join(css_regles),
                                        "Bloc <style> ajoute dans le <head> du HTML existant"))
                    break

    # Ecrire tous les fichiers modifies
    for fichier, lignes in fichiers_modifies.items():
        if fichier in fichiers_touches:
            with open(fichier, 'w', encoding='utf-8') as f:
                f.writelines(lignes)

    return rapport

css_regles = []  # global pour collecter les regles

if __name__ == '__main__':
    import sys
    # Lire le rapport du validateur
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
    import os
    for f, n, msg, regle in erreurs:
        print(f"  {os.path.basename(f)}:{n} - {regle}")

    corrections = appliquer_corrections(erreurs)

    print("\n=== RAPPORT AVANT / APRES ===")
    for regle, fichier, num, avant, apres, explication in corrections:
        print(f"\n[{regle}] {os.path.basename(fichier)} ligne {num}")
        print(f"  Explication : {explication}")
        if num != 0:
            print(f"  AVANT  : {avant}")
            print(f"  APRES  : {apres}")

    print(f"\n{len(corrections)} correction(s) appliquee(s)")
