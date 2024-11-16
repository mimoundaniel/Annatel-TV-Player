import os

def lister_fichiers_dossiers(chemin, base='./'):
    for dossier, sous_dossiers, fichiers in os.walk(chemin):
        # Remplace le chemin de base par `./`
        dossier_relative = dossier.replace(chemin, base)
        print(f"Dossier : {dossier_relative}")
        
        # Affiche chaque fichier dans le dossier actuel
        for fichier in fichiers:
            fichier_relative = os.path.join(dossier_relative, fichier)
            print(f"  Fichier : {fichier_relative}")

# Remplace 'chemin_du_dossier' par le chemin réel du dossier que tu veux explorer
chemin_du_dossier = "c:/Users/Daniel Mimoun/Desktop/plugin.video.annatel.tv"
lister_fichiers_dossiers(chemin_du_dossier)
