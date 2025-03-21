# Grid Simulation Project

Ce projet est une application graphique interactive développée avec Python et Tkinter. Il permet de simuler des circuits simples sur une grille, avec des éléments tels que des câbles, des boutons et des switches. L'application propose une propagation dynamique de l'activation, inspirée du fonctionnement de la redstone dans Minecraft, et offre des options de configuration avancées pour adapter la grille.

## Fonctionnalités

- **Interface interactive** : 
  - Placement, déplacement et suppression d'items sur une grille.
  - Utilisation d’événements souris pour interagir avec la grille.
- **Gestion d'items** :
  - **Câble** : Transmet l’activation.
  - **Bouton** : Source d’activation, activable/désactivable.
  - **Switch** : Se comporte comme une torche de redstone, avec une partie sensorielle à gauche et une transmission (droite, haut, bas).
- **Propagation dynamique** :
  - Mise à jour en continu des états des câbles et des switches via un mécanisme de "ticks".
  - Utilisation d’un algorithme de flood fill optimisé pour la propagation du signal.
- **Panneau de paramètres** :
  - Possibilité de modifier le nombre de lignes, de colonnes et la taille des cases de la grille.
  - Bouton "Reset Grid" pour effacer la grille et redessiner le quadrillage avec les nouveaux paramètres.
- **Sélection d’item** :
  - Possibilité de garder l’item en main pour le poser plusieurs fois.
  - Déselection via un clic molette pour interagir directement avec la grille.
- **Optimisations** :
  - Indexation spatiale pour un accès rapide aux items sur la grille.
  - Utilisation de `collections.deque` pour un flood fill performant.

## Prérequis

- Python 3.x
- Tkinter (généralement inclus avec Python)

## Installation

1. Clonez le dépôt ou téléchargez les fichiers du projet.
2. Assurez-vous que Python 3 est installé sur votre système.
3. Lancez l'application en exécutant la commande suivante dans le terminal :

```bash
python main.py 
```

## Utilisation

1. Sélection d'item : Utilisez le panneau "Items" pour sélectionner l’item souhaité (Câble, Bouton, Switch, etc.).
2. Placement : Cliquez sur la grille pour placer l’item. L’item reste en main, ce qui permet de le poser plusieurs fois.
3. Déplacement/Suppression : Déplacez un item en cliquant et glissant. Pour supprimer un item, effectuez un clic droit dessus.
4. Désélection : Cliquez avec la molette pour "lâcher" l’item en main et interagir directement avec la grille.
5. Paramètres de la grille :
    - Modifiez le nombre de lignes, le nombre de colonnes et la taille des cases dans le panneau "Paramètres".
    - Cliquez sur "Confirmer paramètres grille" pour appliquer les changements immédiatement.
    - Utilisez "Reset Grid" pour effacer la grille et redessiner le quadrillage.

## Structure du Code

1. main.py : Contient la classe GridApp qui implémente l'ensemble de la logique de l'interface graphique, la gestion des items, la propagation des signaux et les optimisations.
2. Interface Graphique :
    - Items Panel : Pour ajouter et sélectionner des items.
    - Grille : Zone de dessin où les items sont placés et où se produit la simulation.
    - Settings Panel : Pour configurer les paramètres de la grille et réinitialiser l'application.

## Améliorations Futures

1. Ajout de nouveaux types d’items et de comportements plus complexes.
2. Sauvegarde et chargement de configurations de grille.
3. Amélioration de l’optimisation et de la gestion des performances pour des grilles de grande taille.

## Licence

Ce projet est sous Licence MIT.