# Annatel TV Player for Kodi  

Regardez vos chaînes TV préférées d’[Annatel.tv](https://www.annatel.tv/) directement sur Kodi grâce à cette extension simple et fluide.  

## Fonctionnalités  
- Accédez à toutes vos chaînes Annatel.tv via Kodi.  
- Diffusion en direct avec une interface intuitive.  
- Compatible avec les versions modernes de Kodi.  

## Installation

Dans Kodi, activez d'abord **Paramètres > Système > Extensions > Sources inconnues**.

1. **Paramètres > Gestionnaire de fichiers > Ajouter une source**, entrez l'adresse
   `https://mimoundaniel.github.io/Annatel-TV-Player/` et nommez la source `annatel`.
2. **Extensions > Installer depuis un fichier ZIP > annatel**, choisissez `repository.annatel`
   puis son zip.
3. **Extensions > Installer depuis un dépôt > Annatel TV Repository > Extensions de service >
   Annatel TV**. Les mises à jour arrivent ensuite automatiquement.
4. Entrez vos identifiants Annatel.tv dans les paramètres de l'extension. Les chaînes
   apparaissent dans **TV** après quelques secondes.

L'extension s'appuie sur **PVR IPTV Simple Client**, que Kodi installe automatiquement.

### Kodi sur une télé Samsung (Tizen)

Le dépôt officiel de Kodi ne fournit pas IPTV Simple pour Tizen. Avant l'étape 3, installez le
dépôt [kodi-tizen-addons](https://github.com/Ricrdsson1/kodi-tizen-addons) : ajoutez la source
`https://ricrdsson1.github.io/kodi-tizen-addons/` et installez `repository.kodi-tizen` depuis son zip.

## Développement

`python build.py` génère les zips et le dépôt Kodi dans `docs/`, publié par GitHub Pages.
Augmentez la version dans `addon.xml` avant chaque publication.

## Prérequis  
- Un compte actif sur [Annatel.tv](https://www.annatel.tv/).  
- Une version récente de Kodi installée.  

## Remerciements  
Un grand merci à **[Mreouven](https://github.com/mreouven)** pour son aide et ses contributions exceptionnelles ! 🙌  

---

Profitez du meilleur de la TV avec Annatel et Kodi !  
