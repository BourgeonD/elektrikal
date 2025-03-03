import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

class GridApp:
    def __init__(self, root, rows=8, cols=8):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.grid_size = 50  # Taille d'une case
        self.items = {}
        self.placed_items = {}
        self.selected_item = None
        self.item_id_counter = 0
        self.textures = {}
        self.tick_interval = 500  # Intervalle de tick en millisecondes (500ms = 2 ticks/s)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')
        
        self.frame_items = tk.Frame(self.notebook)
        self.frame_grid = tk.Frame(self.notebook)
        self.frame_settings = tk.Frame(self.notebook)
        
        self.notebook.add(self.frame_items, text='Items')
        self.notebook.add(self.frame_grid, text='Grille')
        self.notebook.add(self.frame_settings, text='Paramètres')
        
        self.canvas = tk.Canvas(self.frame_grid, width=self.cols * self.grid_size, height=self.rows * self.grid_size, bg='white')
        self.canvas.pack()
        
        self.selected_item_label = tk.Label(self.frame_items, text="Aucun item sélectionné", fg="red")
        self.selected_item_label.pack()
        
        self.items_container = tk.Frame(self.frame_items)
        self.items_container.pack()
        
        tk.Button(self.frame_items, text="Ajouter un item", command=self.add_item).pack()
        
        self.create_settings_panel()
        self.draw_grid()
        self.create_items_panel()
        
        self.canvas.bind("<Button-1>", self.place_item)
        self.canvas.bind("<B1-Motion>", self.move_item)
        self.canvas.bind("<Button-3>", self.delete_item)

        # Lancer la clock pour les ticks
        self.start_clock()

    def start_clock(self):
        """Démarre l'horloge pour générer des ticks en boucle."""
        self.tick()  # Exécuter un tick immédiatement
        self.root.after(self.tick_interval, self.start_clock)  # Planifier le prochain tick

    def tick(self):
        """Méthode appelée à chaque tick pour mettre à jour les états."""
        self.update_cable_state()  # Mise à jour des câbles

    
    def draw_grid(self):
        for i in range(self.cols + 1):
            self.canvas.create_line(i * self.grid_size, 0, i * self.grid_size, self.rows * self.grid_size)
        for i in range(self.rows + 1):
            self.canvas.create_line(0, i * self.grid_size, self.cols * self.grid_size, i * self.grid_size)
    
    def create_items_panel(self):
        for i in range(3):
            self.add_item()
    
    def add_item(self):
        item_id = self.item_id_counter
        self.item_id_counter += 1

        # Définir les noms et couleurs spécifiques
        if item_id == 0:
            name = "Câble"
            color = "green"  # Câble désactivé (gris ensuite)
        elif item_id == 1:
            name = "Bouton"
            color = "red"  # Bouton activable
        else:
            name = f"Item {item_id}"
            color = "blue"  # Autres items lambda

        item = tk.Canvas(self.items_container, width=self.grid_size, height=self.grid_size, bg='white')
        item.pack(side=tk.LEFT, padx=5, pady=5)
        shape = item.create_oval(5, 5, self.grid_size - 5, self.grid_size - 5, fill=color)

        item.bind("<Button-1>", lambda event, id=item_id: self.select_item(id))

        self.items[item_id] = {
            'canvas': item,
            'shape': shape,
            'color': color,
            'name': name,
            'texture': None
        }

        if hasattr(self, 'item_selector'):
            self.update_item_selector()

    def create_settings_panel(self):
        tk.Label(self.frame_settings, text="Sélectionner un item:").pack()
        self.item_selector = ttk.Combobox(self.frame_settings, state="readonly")
        self.item_selector.pack()
        self.item_selector.bind("<<ComboboxSelected>>", self.load_item_settings)
        
        tk.Label(self.frame_settings, text="Nom de l'item:").pack()
        self.name_entry = tk.Entry(self.frame_settings)
        self.name_entry.pack()
        
        tk.Label(self.frame_settings, text="Couleur de l'item:").pack()
        self.color_entry = tk.Entry(self.frame_settings)
        self.color_entry.pack()
        
        tk.Button(self.frame_settings, text='Changer Texture', command=self.load_texture).pack()
        
        tk.Button(self.frame_settings, text='Appliquer', command=self.apply_settings).pack()
    
    def load_texture(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path and self.selected_item is not None:
            img = Image.open(file_path)
            img = img.resize((self.grid_size, self.grid_size), Image.Resampling.LANCZOS)
            self.textures[self.selected_item] = ImageTk.PhotoImage(img)
            self.items[self.selected_item]['texture'] = self.textures[self.selected_item]
            self.items[self.selected_item]['canvas'].create_image(0, 0, anchor=tk.NW, image=self.textures[self.selected_item])
    
    def update_item_selector(self):
        self.item_selector['values'] = [f"{item_id}: {data['name']}" for item_id, data in self.items.items()]
    
    def load_item_settings(self, event):
        selected_text = self.item_selector.get()
        if selected_text:
            self.selected_item = int(selected_text.split(':')[0])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.items[self.selected_item]['name'])
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, self.items[self.selected_item]['color'])
            self.selected_item_label.config(text=f"Item sélectionné: {self.items[self.selected_item]['name']}", fg="green")
    
    def apply_settings(self):
        if self.selected_item is not None:
            name = self.name_entry.get() or f'Item {self.selected_item}'
            color = self.color_entry.get() or 'blue'
            
            self.items[self.selected_item]['name'] = name
            self.items[self.selected_item]['color'] = color
            self.items[self.selected_item]['canvas'].itemconfig(self.items[self.selected_item]['shape'], fill=color)
            self.update_item_selector()
            self.selected_item_label.config(text=f"Item sélectionné: {name}", fg="green")
    
    def select_item(self, item_id):
        self.selected_item = item_id
        self.selected_item_label.config(text=f"Item sélectionné: {self.items[item_id]['name']}", fg="green")
        self.update_item_selector()
    
    def place_item(self, event):
        if self.selected_item is not None:
            x, y = event.x // self.grid_size, event.y // self.grid_size
            color = self.items[self.selected_item]['color']
        
            item = self.canvas.create_oval(
                x * self.grid_size + 5, y * self.grid_size + 5,
                (x + 1) * self.grid_size - 5, (y + 1) * self.grid_size - 5,
                fill=color if self.selected_item != 0 else "gray",  # Câble désactivé de base
                tags='movable'
            )

            # Stocker l'item placé
            self.placed_items[item] = {
                'id': self.selected_item,
                'active': (self.selected_item == 1),  # Bouton activable, câble inactif au départ
                'position': (x, y)
            }

            # Si c'est un bouton, ajouter le comportement d'activation
            if self.selected_item == 1:
                self.canvas.tag_bind(item, "<Button-1>", self.toggle_item_state)

            # Mettre à jour les câbles après chaque placement
            self.update_cable_state()

            self.selected_item = None
            self.selected_item_label.config(text="Aucun item sélectionné", fg="red")
    
    def move_item(self, event):
        x, y = event.x // self.grid_size, event.y // self.grid_size
        item = self.canvas.find_withtag(tk.CURRENT)
        if item:
            self.canvas.coords(item,
                               x * self.grid_size + 5, y * self.grid_size + 5,
                               (x + 1) * self.grid_size - 5, (y + 1) * self.grid_size - 5)
    
    def delete_item(self, event):
        item = self.canvas.find_withtag(tk.CURRENT)
        if item:
            # Vérifier que l'élément fait partie des objets placés et non de la grille
            if item[0] in self.placed_items:
                self.canvas.delete(item)
                del self.placed_items[item[0]]

    def toggle_item_state(self, event):
        item = self.canvas.find_withtag(tk.CURRENT)
        if item and item[0] in self.placed_items:
            item_data = self.placed_items[item[0]]
            item_id = item_data['id']
        
            # Ne permettre l'activation/désactivation que pour le bouton
            if item_id == 1:
                item_data['active'] = not item_data['active']
            
                # Changer la couleur selon l'état
                new_color = self.items[item_id]['color'] if item_data['active'] else 'gray'
                self.canvas.itemconfig(item[0], fill=new_color)

                # Mettre à jour les câbles après activation/désactivation du bouton
                self.update_cable_state()




    def update_item_0_state(self):
        # Trouver les positions des items activés
        active_positions = {data['position'] for item, data in self.placed_items.items() if data['id'] == 1 and data['active']}

        # Vérifier chaque item 0 et s'il doit être activé/désactivé
        for item, data in self.placed_items.items():
            if data['id'] == 0:  # On cible uniquement les items 0
                x, y = data['position']

                # Vérifier les voisins (haut, bas, gauche, droite)
                adjacent_positions = [
                    (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)
                ]

                has_active_neighbor = any(pos in active_positions for pos in adjacent_positions)

                # Vérifier s'il y a un voisin désactivé
                has_neighbor = any(
                    pos in [data['position'] for _, data in self.placed_items.items() if data['id'] == 1]
                    for pos in adjacent_positions
                )

                # Appliquer les règles de l'activation/désactivation
                if has_active_neighbor:
                    data['active'] = True
                    self.canvas.itemconfig(item, fill="green")  # Activation
                elif has_neighbor:  # S'il y a des voisins désactivés, l'item 0 est désactivé
                    data['active'] = False
                    self.canvas.itemconfig(item, fill="gray")  # Désactivation
                else:
                    data['active'] = False
                    self.canvas.itemconfig(item, fill="gray")  # Reste désactivé

    def update_cable_state(self):
        """Met à jour l'état des câbles en fonction des sources activables actives."""
        # Trouver toutes les positions des items activés qui sont activables (ex: boutons)
        active_sources = {data['position'] for item, data in self.placed_items.items() if data['id'] == 1 and data['active']}

        # Liste des câbles placés
        cables = [item for item, data in self.placed_items.items() if data['id'] == 0]

        # Désactiver tous les câbles temporairement
        for cable in cables:
            self.placed_items[cable]['active'] = False
            self.canvas.itemconfig(cable, fill="gray")

        # Réactiver uniquement ceux connectés à une source activée
        updated = True
        while updated:  # Continue tant qu'il y a des changements
            updated = False
            for cable in cables:
                x, y = self.placed_items[cable]['position']

                # Vérifier si un câble a un voisin qui est activable et activé
                adjacent_positions = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
                if any(pos in active_sources for pos in adjacent_positions):
                    if not self.placed_items[cable]['active']:  # Si le câble était inactif
                        self.placed_items[cable]['active'] = True
                        self.canvas.itemconfig(cable, fill="green")  # Activer le câble
                        active_sources.add((x, y))  # Ce câble devient une nouvelle source activée
                        updated = True  # Indiquer qu'on a mis à jour un câble




if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    root.mainloop()