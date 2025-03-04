import tkinter as tk
from tkinter import ttk
from collections import deque

class GridApp:
    def __init__(self, root, rows=8, cols=8):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.grid_size = 50  # Taille d'une case
        self.items = {}
        self.placed_items = {}
        self.position_index = {}  # (x, y) -> id de l'item placé
        self.selected_item = None
        self.item_id_counter = 0
        self.textures = {}
        self.tick_interval = 100  # Intervalle en ms pour la boucle de mise à jour
        self.ticker_id = None

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')
        
        # Création des onglets
        self.frame_items = tk.Frame(self.notebook)
        self.frame_grid = tk.Frame(self.notebook)
        self.frame_settings = tk.Frame(self.notebook)
        self.frame_presets = tk.Frame(self.notebook)  # Nouvel onglet pour les presets
        
        self.notebook.add(self.frame_items, text='Items')
        self.notebook.add(self.frame_grid, text='Grille')
        self.notebook.add(self.frame_settings, text='Paramètres')
        self.notebook.add(self.frame_presets, text='Presets')
        
        # Canvas de la grille
        self.canvas = tk.Canvas(self.frame_grid, width=self.cols * self.grid_size, 
                                height=self.rows * self.grid_size, bg='white')
        self.canvas.pack()
        
        # Panneau Items
        self.selected_item_label = tk.Label(self.frame_items, text="Aucun item sélectionné", fg="red")
        self.selected_item_label.pack()
        self.items_container = tk.Frame(self.frame_items)
        self.items_container.pack()
        tk.Button(self.frame_items, text="Ajouter un item", command=self.add_item).pack()
        
        self.create_settings_panel()
        self.create_presets_panel()  # Création du panneau presets
        self.draw_grid()
        # Création des items par défaut (incluant LED)
        for i in range(6):
            self.add_item()
        
        # Bindings pour le canvas
        self.canvas.bind("<Button-1>", self.place_item)
        self.canvas.bind("<B1-Motion>", self.move_item)
        self.canvas.bind("<Button-3>", self.delete_item)
        self.canvas.bind("<Button-2>", self.release_item)  # Clique molette pour déselectionner
        
        # Barre de statut
        self.status_bar = tk.Label(root, text="Item en main : Aucun", anchor='w')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.start_update_loop()

    # ---------------------- Boucle de mise à jour centralisée ----------------------
    def start_update_loop(self):
        self.ticker_id = self.root.after(self.tick_interval, self.update_loop)

    def update_loop(self):
        self.update_switches()
        self.update_cables()
        self.update_leds()
        self.update_comparators()
        self.update_repeaters()
        self.ticker_id = self.root.after(self.tick_interval, self.update_loop)

    # ---------------------- Mise à jour des éléments ----------------------
    def update_status_bar(self):
        if self.selected_item is not None:
            item_name = self.items[self.selected_item]['name']
            self.status_bar.config(text=f"Item en main : {item_name}")
        else:
            self.status_bar.config(text="Item en main : Aucun")

    def release_item(self, event):
        self.selected_item = None
        self.selected_item_label.config(text="Aucun item sélectionné", fg="red")
        self.update_status_bar()

    def draw_grid(self):
        self.canvas.delete("grid_line")
        for i in range(self.cols + 1):
            self.canvas.create_line(i * self.grid_size, 0, i * self.grid_size, self.rows * self.grid_size,
                                    tags="grid_line")
        for i in range(self.rows + 1):
            self.canvas.create_line(0, i * self.grid_size, self.cols * self.grid_size, i * self.grid_size,
                                    tags="grid_line")

    # ---------------------- Panneaux Items, Paramètres et Presets ----------------------
    def create_settings_panel(self):
        # Paramètres des items
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
        
        tk.Button(self.frame_settings, text='Appliquer', command=self.apply_settings).pack(pady=5)
        
        # Paramètres de la grille
        tk.Label(self.frame_settings, text="Paramètres de la grille", font=('Helvetica', 12, 'bold')).pack(pady=10)
        tk.Label(self.frame_settings, text="Nombre de lignes:").pack()
        self.rows_entry = tk.Entry(self.frame_settings)
        self.rows_entry.pack()
        self.rows_entry.insert(0, str(self.rows))
        tk.Label(self.frame_settings, text="Nombre de colonnes:").pack()
        self.cols_entry = tk.Entry(self.frame_settings)
        self.cols_entry.pack()
        self.cols_entry.insert(0, str(self.cols))
        tk.Label(self.frame_settings, text="Taille de case:").pack()
        self.grid_size_entry = tk.Entry(self.frame_settings)
        self.grid_size_entry.pack()
        self.grid_size_entry.insert(0, str(self.grid_size))
        tk.Button(self.frame_settings, text="Confirmer paramètres grille", command=self.confirm_grid_settings).pack(pady=5)
        tk.Button(self.frame_settings, text="Reset Grid", command=self.reset_grid).pack(pady=5)

    def create_presets_panel(self):
        """Crée l'interface pour importer des schémas préconfigurés."""
        tk.Label(self.frame_presets, text="Sélectionnez un preset:", font=('Helvetica', 12, 'bold')).pack(pady=5)
        self.preset_selector = ttk.Combobox(self.frame_presets, state="readonly")
        self.preset_selector['values'] = ["Porte AND","Porte OR","Porte NAND","Porte NOR","Porte NOT"]
        self.preset_selector.current(0)
        self.preset_selector.pack(pady=5)
        
        offset_frame = tk.Frame(self.frame_presets)
        offset_frame.pack(pady=5)
        tk.Label(offset_frame, text="Offset X:").grid(row=0, column=0, padx=2)
        self.offset_x_entry = tk.Entry(offset_frame, width=5)
        self.offset_x_entry.insert(0, "0")
        self.offset_x_entry.grid(row=0, column=1, padx=2)
        tk.Label(offset_frame, text="Offset Y:").grid(row=0, column=2, padx=2)
        self.offset_y_entry = tk.Entry(offset_frame, width=5)
        self.offset_y_entry.insert(0, "0")
        self.offset_y_entry.grid(row=0, column=3, padx=2)
        
        tk.Button(self.frame_presets, text="Importer le preset", command=self.import_selected_preset).pack(pady=5)

    def load_item_settings(self, event):
        selected_text = self.item_selector.get()
        if selected_text:
            self.selected_item = int(selected_text.split(':')[0])
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.items[self.selected_item]['name'])
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, self.items[self.selected_item]['color'])
            self.selected_item_label.config(text=f"Item sélectionné: {self.items[self.selected_item]['name']}", fg="green")
            self.update_status_bar()

    def apply_settings(self):
        if self.selected_item is not None:
            name = self.name_entry.get() or f'Item {self.selected_item}'
            color = self.color_entry.get() or 'blue'
            self.items[self.selected_item]['name'] = name
            self.items[self.selected_item]['color'] = color
            self.items[self.selected_item]['canvas'].itemconfig(self.items[self.selected_item]['shape'], fill=color)
            self.update_item_selector()
            self.selected_item_label.config(text=f"Item sélectionné: {name}", fg="green")
            self.update_status_bar()

    def update_item_selector(self):
        self.item_selector['values'] = [f"{item_id}: {data['name']}" for item_id, data in self.items.items()]

    def select_item(self, item_id):
        self.selected_item = item_id
        self.selected_item_label.config(text=f"Item sélectionné: {self.items[item_id]['name']}", fg="green")
        self.update_item_selector()
        self.update_status_bar()

    def confirm_grid_settings(self):
        try:
            new_rows = int(self.rows_entry.get())
            new_cols = int(self.cols_entry.get())
            new_grid_size = int(self.grid_size_entry.get())
        except ValueError:
            return
        self.rows = new_rows
        self.cols = new_cols
        self.grid_size = new_grid_size
        self.canvas.config(width=self.cols * self.grid_size, height=self.rows * self.grid_size)
        self.reset_grid()

    def reset_grid(self):
        for item_id in list(self.placed_items.keys()):
            self.canvas.delete(item_id)
        self.placed_items.clear()
        self.position_index.clear()
        self.canvas.delete("all")
        self.draw_grid()

    # ---------------------- Fonctions d'import de schémas ----------------------
    def import_schema_item(self, item_id, grid_x, grid_y):
        """
        Place un item sur la grille à la position (grid_x, grid_y) selon son type (item_id).
        Pour les câbles, on commence avec la couleur "gray".
        Pour les boutons (id 1), on lie l'événement de clic pour permettre l'activation/désactivation.
        """
        fill = self.items[item_id]['color'] if item_id != 0 else "gray"
        item = self.canvas.create_oval(
            grid_x * self.grid_size + 5, grid_y * self.grid_size + 5,
            (grid_x + 1) * self.grid_size - 5, (grid_y + 1) * self.grid_size - 5,
            fill=fill, tags='movable'
        )
        self.placed_items[item] = {
            'id': item_id,
            'active': (item_id == 1),  # Les boutons (id 1) sont activés par défaut
            'position': (grid_x, grid_y),
            'previous_state': False,
            'initialized': False
        }
        self.position_index[(grid_x, grid_y)] = item
        # Pour les boutons, lier le clic pour toggler leur état
        if item_id == 1:
            self.canvas.tag_bind(item, "<Button-1>", self.toggle_item_state)
        if item_id == 2:
            self.root.after(200, lambda: self.set_switch_initialized(item))

    def import_schema(self, schema, offset_x=0, offset_y=0):
        for item_type, rel_x, rel_y in schema:
            self.import_schema_item(item_type, offset_x + rel_x, offset_y + rel_y)

    def import_and_gate(self, offset_x=0, offset_y=0):
        schema = [
            (1, 0, 0),   # Bouton (entrée supérieure)
            (2, 1, 0),   # Switch à droite du bouton supérieur
            (1, 0, 2),   # Bouton (entrée inférieure)
            (2, 1, 2),   # Switch à droite du bouton inférieur
            (0, 1, 1),   # Cable reliant les deux entrées
            (2, 2, 1),   # Switch de traitement
            (3, 3, 1)    # LED en sortie
        ]
        self.import_schema(schema, offset_x, offset_y)

    def import_or_gate(self, offset_x=0, offset_y=0):
        schema = [
            (1, 0, 0),
            (1, 0, 1),
            (0, 1, 0),
            (0, 1, 1),
            (3, 2, 0) 
        ]
        self.import_schema(schema, offset_x, offset_y)
    
    def import_nand_gate(self, offset_x=0, offset_y=0):
        schema = [
            (1, 0, 0),
            (2, 1, 0),
            (1, 0, 2),
            (2, 1, 2),
            (0, 1, 1),
            (3, 2, 1)
        ]
        self.import_schema(schema, offset_x, offset_y)
    
    def import_nor_gate(self, offset_x=0, offset_y=0):
        schema = [
            (1, 0, 0),
            (0, 1, 0),
            (1, 0, 1),
            (0, 1, 1),
            (2, 2, 0),
            (3, 3, 0)
        ]
        self.import_schema(schema, offset_x, offset_y)
    
    def import_not_gate(self, offset_x=0, offset_y=0):
        schema = [
            (1, 0, 0),
            (2, 1, 0),
            (3, 2, 0),
        ]
        self.import_schema(schema, offset_x, offset_y)
    
    def import_selected_preset(self):
        try:
            offset_x = int(self.offset_x_entry.get())
            offset_y = int(self.offset_y_entry.get())
        except ValueError:
            offset_x, offset_y = 0, 0
        preset = self.preset_selector.get()
        if preset == "Porte AND":
            self.import_and_gate(offset_x, offset_y)
        if preset == "Porte OR":
            self.import_or_gate(offset_x,offset_y)
        if preset == "Porte NAND":
            self.import_nand_gate(offset_x,offset_y)
        if preset == "Porte NOR":
            self.import_nor_gate(offset_x,offset_y)
        if preset == "Porte NOT":
            self.import_not_gate(offset_x,offset_y)
        # D'autres presets peuvent être ajoutés ici.

    # ---------------------- Gestion des items placés ----------------------
    def set_switch_initialized(self, item):
        if item in self.placed_items:
            self.placed_items[item]['initialized'] = True

    def place_item(self, event):
        if self.selected_item is not None:
            x, y = event.x // self.grid_size, event.y // self.grid_size
            color = self.items[self.selected_item]['color']
            item = self.canvas.create_oval(
                x * self.grid_size + 5, y * self.grid_size + 5,
                (x + 1) * self.grid_size - 5, (y + 1) * self.grid_size - 5,
                fill=color if self.selected_item != 0 else "gray",
                tags='movable'
            )
            self.placed_items[item] = {
                'id': self.selected_item,
                'active': (self.selected_item == 1),
                'position': (x, y),
                'previous_state': False,
                'initialized': False
            }
            self.position_index[(x, y)] = item
            self.canvas.tag_bind(item, "<B1-Motion>", self.move_item)
            if self.selected_item == 1:
                self.canvas.tag_bind(item, "<Button-1>", self.toggle_item_state)
            if self.selected_item == 2:
                self.root.after(200, lambda: self.set_switch_initialized(item))
            self.update_status_bar()

    def move_item(self, event):
        item = self.canvas.find_withtag(tk.CURRENT)
        if item:
            item_id = item[0]
            if item_id not in self.placed_items:
                print(f"Erreur : l'élément {item_id} n'existe pas")
                return
            old_pos = self.placed_items[item_id]['position']
            x, y = event.x // self.grid_size, event.y // self.grid_size
            new_pos = (x, y)
            if self.position_index.get(old_pos) == item_id:
                del self.position_index[old_pos]
            self.position_index[new_pos] = item_id
            self.placed_items[item_id]['position'] = new_pos
            self.canvas.coords(
                item_id,
                x * self.grid_size + 5, y * self.grid_size + 5,
                (x + 1) * self.grid_size - 5, (y + 1) * self.grid_size - 5
            )

    def delete_item(self, event):
        item = self.canvas.find_withtag(tk.CURRENT)
        if item:
            if item[0] in self.placed_items:
                pos = self.placed_items[item[0]]['position']
                if self.position_index.get(pos) == item[0]:
                    del self.position_index[pos]
                self.canvas.delete(item)
                del self.placed_items[item[0]]

    def toggle_item_state(self, event):
        item = self.canvas.find_withtag(tk.CURRENT)
        if item and item[0] in self.placed_items:
            item_data = self.placed_items[item[0]]
            item_id = item_data['id']
            if item_id == 1:
                item_data['active'] = not item_data['active']
                new_color = self.items[item_id]['color'] if item_data['active'] else 'brown'
                self.canvas.itemconfig(item[0], fill=new_color)

    def update_switches(self):
        switches = {item: data for item, data in self.placed_items.items() if data['id'] == 2}
        for item, data in switches.items():
            if item not in self.placed_items or not data.get('initialized', False):
                continue
            x, y = data['position']
            left_pos = (x - 1, y)
            left_item = None
            if left_pos in self.position_index:
                left_canvas_item = self.position_index[left_pos]
                left_item = self.placed_items.get(left_canvas_item)
            new_state = False if (left_item is not None and left_item.get('active', False)) else True
            if data['active'] != new_state:
                data['active'] = new_state
                new_color = "orange" if new_state else "moccasin"
                self.canvas.itemconfig(item, fill=new_color)

    def update_cables(self):
        cables = {item: data for item, data in self.placed_items.items() if data['id'] == 0}
        cable_positions = {data['position'] for data in cables.values()}
        active_sources = []
        for item, data in self.placed_items.items():
            if data.get('active', False) and data['id'] in (1, 2):
                if data['id'] == 1:
                    allowed_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                elif data['id'] == 2:
                    allowed_dirs = [(1, 0), (0, -1), (0, 1)]
                active_sources.append((data['position'], allowed_dirs))
        reachable = set()
        frontier = deque()
        for pos, allowed_dirs in active_sources:
            x, y = pos
            for dx, dy in allowed_dirs:
                neighbor = (x + dx, y + dy)
                if neighbor in cable_positions and neighbor not in reachable:
                    reachable.add(neighbor)
                    frontier.append(neighbor)
        while frontier:
            current = frontier.popleft()
            cx, cy = current
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (cx + dx, cy + dy)
                if neighbor in cable_positions and neighbor not in reachable:
                    reachable.add(neighbor)
                    frontier.append(neighbor)
        for cable_item, cable_data in cables.items():
            if cable_data['position'] in reachable:
                if not cable_data['active']:
                    cable_data['active'] = True
                    self.canvas.itemconfig(cable_item, fill="lime")
            else:
                if cable_data['active']:
                    cable_data['active'] = False
                    self.canvas.itemconfig(cable_item, fill="forestgreen")

    def update_leds(self):
        for item, data in self.placed_items.items():
            if data['id'] == 3:  # LED
                x, y = data['position']
                neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                active = any((nx, ny) in self.position_index and 
                             self.placed_items[self.position_index[(nx, ny)]].get('active', False)
                             for nx, ny in neighbors)
                if active and not data.get('active', False):
                    data['active'] = True
                    on_color = self.items[3].get('on_color', "yellow")
                    self.canvas.itemconfig(item, fill=on_color)
                elif not active and data.get('active', False):
                    data['active'] = False
                    self.canvas.itemconfig(item, fill="olive")
                    
    def update_comparators(self):
        """Met à jour les comparateurs et applique les règles Redstone de Minecraft."""
        for item, data in self.placed_items.items():
            if data['id'] == 4:  # Comparateur
                x, y = data['position']

                # Définition des positions
                back_pos = (x - 1, y)   # Arrière (Gauche en 2D)
                front_pos = (x + 1, y)  # Avant (Droite en 2D)
                left_pos = (x, y - 1)   # Gauche (Haut en 2D)
                right_pos = (x, y + 1)  # Droite (Bas en 2D)

                # Vérification des entrées
                back_active = back_pos in self.position_index and self.placed_items[self.position_index[back_pos]].get('active', False)
                left_active = left_pos in self.position_index and self.placed_items[self.position_index[left_pos]].get('active', False)
                right_active = right_pos in self.position_index and self.placed_items[self.position_index[right_pos]].get('active', False)

                # **Application des règles du comparateur**
                if back_active and not (left_active or right_active):
                    data['active'] = True  # Transmission du signal arrière
                else:
                    data['active'] = False  # Comparateur désactivé si une entrée latérale est active

                # Propagation du signal vers l'avant (Droite)
                if data['active'] and front_pos in self.position_index:
                    forward_item = self.placed_items[self.position_index[front_pos]]
                    if forward_item['id'] == 0:  # Si un câble est en sortie
                        forward_item['active'] = True


    def update_repeaters(self):
        """Met à jour les répéteurs pour qu'ils prolongent un signal uniquement vers l'avant (droite)."""
        for item, data in self.placed_items.items():
            if data['id'] == 5:  # Répéteur
                x, y = data['position']

                # Position d'entrée (arrière) et de sortie (avant)
                back_pos = (x - 1, y)  # Entrée arrière (gauche)
                front_pos = (x + 1, y)  # Sortie avant (droite)

                back_active = back_pos in self.position_index and self.placed_items[self.position_index[back_pos]].get('active', False)

                # Si l'entrée arrière est active, le répéteur s'allume et envoie un signal vers l'avant
                if back_active:
                    data['active'] = True
                    self.canvas.itemconfig(item, fill="blue")  # Répéteur activé

                    # Propage le signal vers l'avant après un léger délai (100ms)
                    self.root.after(100, lambda: self.propagate_repeater_signal(front_pos))
                else:
                    data['active'] = False
                    self.canvas.itemconfig(item, fill="darkblue")  # Répéteur éteint
        
    def propagate_repeater_signal(self, front_pos):
        """Propage le signal du répéteur à l'élément de sortie après un délai."""
        if front_pos in self.position_index:
            front_item = self.placed_items[self.position_index[front_pos]]

            # Si c'est un câble, il devient actif
            if front_item['id'] == 0:
                front_item['active'] = True
                self.canvas.itemconfig(self.position_index[front_pos], fill="green")

            # Si c'est un autre répéteur, il est activé aussi
            elif front_item['id'] == 5:
                front_item['active'] = True
                self.canvas.itemconfig(self.position_index[front_pos], fill="blue")

            # Si c'est un switch ou une LED, ils s'activent aussi
            elif front_item['id'] in [2, 3]:  
                front_item['active'] = True
                color = "orange" if front_item['id'] == 2 else "yellow"  # Switch ou LED
                self.canvas.itemconfig(self.position_index[front_pos], fill=color)

    # ---------------------- Ajout d'items ----------------------
    def add_item(self):
        item_id = self.item_id_counter
        self.item_id_counter += 1
        if item_id == 0:
            name = "Câble"
            color = "forestgreen"
        elif item_id == 1:
            name = "Bouton"
            color = "red"
        elif item_id == 2:
            name = "Switch"
            color = "moccasin"
        elif item_id == 3:
            name = "LED"
            color = "olive"
        elif item_id == 4:
            name = "Comparateur"
            color = "purple"
        elif item_id == 5:
            name = "Amplificateur"
            color = "darkblue"
        else:
            name = f"Item {item_id}"
            color = "blue"
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
        if item_id == 3:
            self.items[item_id]['on_color'] = "yellow"
        if hasattr(self, 'item_selector'):
            self.update_item_selector()

if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    root.mainloop()
