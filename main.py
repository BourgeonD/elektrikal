import tkinter as tk
from tkinter import ttk, filedialog
from collections import deque

class GridApp:
    def __init__(self, root, rows=8, cols=8):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.grid_size = 50  # Taille d'une case
        self.items = {}
        self.placed_items = {}
        self.position_index = {}  # Indexation spatiale : (x, y) -> id de l'item placé
        self.selected_item = None
        self.item_id_counter = 0
        self.textures = {}
        # Boucle de mise à jour centralisée
        self.tick_interval = 100  # en ms
        self.ticker_id = None

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
        # Création des items par défaut (ici on ajoute 4 items pour inclure la LED)
        for i in range(4):
            self.add_item()
        
        self.canvas.bind("<Button-1>", self.place_item)
        self.canvas.bind("<B1-Motion>", self.move_item)
        self.canvas.bind("<Button-3>", self.delete_item)
        # Clique molette pour déselectionner l'item en main
        self.canvas.bind("<Button-2>", self.release_item)

        # Barre de statut en bas indiquant l'item en main
        self.status_bar = tk.Label(root, text="Item en main : Aucun", anchor='w')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.start_update_loop()

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

    def start_update_loop(self):
        self.ticker_id = self.root.after(self.tick_interval, self.update_loop)

    def update_loop(self):
        self.update_switches()
        self.update_cables()
        self.update_leds()  # Mise à jour des LED
        self.ticker_id = self.root.after(self.tick_interval, self.update_loop)

    def draw_grid(self):
        self.canvas.delete("grid_line")
        for i in range(self.cols + 1):
            self.canvas.create_line(i * self.grid_size, 0, i * self.grid_size, self.rows * self.grid_size, tags="grid_line")
        for i in range(self.rows + 1):
            self.canvas.create_line(0, i * self.grid_size, self.cols * self.grid_size, i * self.grid_size, tags="grid_line")
    
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
                'active': (self.selected_item == 1),  # Bouton activé par défaut
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
                print(f"Erreur : l'élément {item_id} n'existe pas dans placed_items")
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
                new_color = self.items[item_id]['color'] if item_data['active'] else 'gray'
                self.canvas.itemconfig(item[0], fill=new_color)

    def update_switches(self):
        switches = {item: data for item, data in self.placed_items.items() if data['id'] == 2}
        for item, data in switches.items():
            if item not in self.placed_items:
                continue
            if not data.get('initialized', False):
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
                new_color = "orange" if new_state else "gray"
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
                    self.canvas.itemconfig(cable_item, fill="green")
            else:
                if cable_data['active']:
                    cable_data['active'] = False
                    self.canvas.itemconfig(cable_item, fill="gray")

    def update_leds(self):
        """Met à jour l'état des LED.
        Une LED (id == 3) devient 'allumée' (par exemple, couleur jaune) si l'une de ses cases adjacentes est activée, sinon elle reste grise."""
        for item, data in self.placed_items.items():
            if data['id'] == 3:  # LED
                x, y = data['position']
                # Considérer les voisins immédiats
                neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                active = False
                for nx, ny in neighbors:
                    if (nx, ny) in self.position_index:
                        neighbor_id = self.position_index[(nx, ny)]
                        if self.placed_items[neighbor_id].get('active', False):
                            active = True
                            break
                # Met à jour l'état et la couleur
                if active and not data.get('active', False):
                    data['active'] = True
                    # Couleur LED allumée (on_color)
                    on_color = data.get('on_color', "yellow")
                    self.canvas.itemconfig(item, fill=on_color)
                elif not active and data.get('active', False):
                    data['active'] = False
                    # Couleur LED éteinte
                    self.canvas.itemconfig(item, fill="grey")

    def add_item(self):
        item_id = self.item_id_counter
        self.item_id_counter += 1

        # Définition des items en fonction de l'ID
        if item_id == 0:
            name = "Câble"
            color = "green"  # Couleur par défaut pour le câble activé
        elif item_id == 1:
            name = "Bouton"
            color = "red"
        elif item_id == 2:
            name = "Switch"
            color = "orange"
        elif item_id == 3:
            name = "LED"
            color = "grey"  # Couleur par défaut pour la LED éteinte
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
        # Pour la LED, on ajoute la couleur d'allumage
        if item_id == 3:
            self.items[item_id]['on_color'] = "yellow"
        if hasattr(self, 'item_selector'):
            self.update_item_selector()

if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root)
    root.mainloop()
