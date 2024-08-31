import tkinter as tk
from math import sqrt, cos, sin, pi
from map import Map, Terrain, Position
from battle import Battle, Fighter as BattleFighter

class RoguelikeGUI:
    def __init__(self, root, map_width, map_height, hex_orientation=None):
        self.root = root
        self.root.title("Roguelike Game (Map)")

        # Map dimensions
        self.map_width = map_width
        self.map_height = map_height

        # Create frames
        self.map_frame = tk.Frame(root)
        self.map_frame.grid(row=0, column=0, sticky="nsew")

        self.info_frame = tk.Frame(root)
        self.info_frame.grid(row=0, column=1, sticky="ns")

        self.status_frame = tk.Frame(root)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=0)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=0)

        # Map type and orientation
        self.hex_orientation = hex_orientation
        self.map_type = 'hex' if hex_orientation else 'square'

        # Initialize hex and square parameters
        if self.map_type == 'hex':
            self._initialize_hex_parameters()
        else:
            self._initialize_square_parameters()

        # Adjust canvas size to fit the grid without gaps
        if self.map_type == 'hex':
            canvas_width = (self.map_width + 1) * self.hex_horiz
            canvas_height = (self.map_height + 1) * self.hex_vert
        elif self.map_type == 'square':
            canvas_width = (self.map_width + 1) * self.square_size
            canvas_height = (self.map_height + 1) * self.square_size

        self.map_canvas = tk.Canvas(self.map_frame, bg="white", width=canvas_width, height=canvas_height)
        self.map_canvas.pack(expand=True, fill=tk.BOTH)

        # Calculate centering offsets
        self.calculate_centering_offsets(canvas_width, canvas_height)

        # Info frame content
        self.info_text = tk.Text(self.info_frame, height=20, width=30, state="disabled")
        self.info_text.pack(expand=True, fill=tk.BOTH)

        # Status frame content
        self.health_label = tk.Label(self.status_frame, text="Health: 100")
        self.health_label.pack(side="left", anchor="w")

        self.strength_label = tk.Label(self.status_frame, text="Strength: 10")
        self.strength_label.pack(side="left", anchor="w")

        # Initialize the map and battle
        self.battle = Battle(
            title="Test Battle",
            roles=[{
                'class': BattleFighter,
                'name': 'Player',
                'level': 1,
                'ai': None,
                'faction': 'Player',
                'weapon': None,
                'armor': None,
                'shield': None
            }],
            map_width=map_width,
            map_height=map_height
        )

        self.draw_map()

        # Bind keys
        self.root.bind("<Key>", self.handle_keypress)

    def calculate_centering_offsets(self, canvas_width, canvas_height):
        """Calculate the X and Y offsets to center the map on the canvas."""
        if self.map_type == 'hex':
            if self.hex_orientation == "pointy-top":
                map_pixel_width = self.map_width * self.hex_horiz + self.hex_horiz / 2
                map_pixel_height = (self.map_height - 1) * self.hex_vert + self.hex_height
            elif self.hex_orientation == "flat-top":
                map_pixel_width = (self.map_width - 1) * self.hex_horiz + self.hex_width
                map_pixel_height = self.map_height * self.hex_vert + self.hex_vert / 2
            self.offset_x = (canvas_width - map_pixel_width) / 2 + self.hex_horiz / 2
            self.offset_y = (canvas_height - map_pixel_height) / 2 + self.hex_vert / 2
        elif self.map_type == 'square':
            map_pixel_width = self.map_width * self.square_size
            map_pixel_height = self.map_height * self.square_size
            self.offset_x = (canvas_width - map_pixel_width) / 2
            self.offset_y = (canvas_height - map_pixel_height) / 2

    def _initialize_hex_parameters(self):
        """Initialize parameters for hex maps."""
        self.hex_radius = 20  # Adjust the radius to fit a single ASCII character
        if self.hex_orientation == "pointy-top":
            self.hex_width = sqrt(3) * self.hex_radius
            self.hex_height = 2 * self.hex_radius
            self.hex_horiz = self.hex_width
            self.hex_vert = self.hex_height * 3 / 4
        elif self.hex_orientation == "flat-top":
            self.hex_width = 2 * self.hex_radius
            self.hex_height = sqrt(3) * self.hex_radius
            self.hex_horiz = self.hex_width * 3 / 4
            self.hex_vert = self.hex_height

    def _initialize_square_parameters(self):
        """Initialize parameters for square grids."""
        self.square_size = 40  # Size of each square (adjust as needed)
        self.hex_horiz = self.square_size
        self.hex_vert = self.square_size

    def hex_to_pixel(self, q, r):
        """Convert grid coordinates to pixel coordinates."""
        if self.map_type == 'hex':
            if self.hex_orientation == "pointy-top":
                x = self.hex_horiz * (q + 0.5 * (r % 2))  # Offset every other column
                y = self.hex_vert * r
            elif self.hex_orientation == "flat-top":
                x = self.hex_horiz * q
                y = self.hex_vert * (r + 0.5 * (q % 2))  # Offset every other row
        elif self.map_type == 'square':
            x = self.square_size * q
            y = self.square_size * r
        return x + self.offset_x, y + self.offset_y  # Apply offsets to center the map

    def draw_hex(self, x, y, color, draw_outline=True):
        """Draw a single hexagon or square on the canvas."""
        if self.map_type == 'hex':
            points = []
            for i in range(6):
                if self.hex_orientation == "pointy-top":
                    angle = pi / 3 * i + pi / 6
                elif self.hex_orientation == "flat-top":
                    angle = pi / 3 * i
                point_x = x + self.hex_radius * cos(angle)
                point_y = y + self.hex_radius * sin(angle)
                points.append(point_x)
                points.append(point_y)
            if draw_outline:
                self.map_canvas.create_polygon(points, outline="black", fill=color)
            else:
                self.map_canvas.create_polygon(points, outline="", fill=color)
        elif self.map_type == 'square':
            self.map_canvas.create_rectangle(x, y, x + self.square_size, y + self.square_size, outline="black", fill=color)

    def draw_map(self):
        """Draw the map on the canvas."""
        self.map_canvas.delete("all")

        # Draw the tiles
        for x in range(self.map_width):
            for y in range(self.map_height):
                pixel_x, pixel_y = self.hex_to_pixel(x, y)
                pos = self.battle.map.get_position(x, y)
                color = self.get_color_by_terrain(pos.terrain)
                self.draw_hex(pixel_x, pixel_y, color)
                if pos.fighter:
                    self.map_canvas.create_text(
                        pixel_x + self.square_size / 2 if self.map_type == 'square' else pixel_x,
                        pixel_y + self.square_size / 2 if self.map_type == 'square' else pixel_y,
                        text=pos.fighter.name[0], fill="white"
                    )

    def get_color_by_terrain(self, terrain):
        """Return the color associated with a terrain type."""
        terrain_colors = {
            Terrain.PLAIN: "lightgreen",
            Terrain.FOREST: "darkgreen",
            Terrain.MOUNTAIN: "gray",
            Terrain.WATER: "blue",
        }
        return terrain_colors.get(terrain, "white")

    def handle_keypress(self, event):
        """Handle keypress events to move the player."""
        direction = None
        if event.keysym == "Up":
            direction = (0, -1)
        elif event.keysym == "Down":
            direction = (0, 1)
        elif event.keysym == "Left":
            direction = (-1, 0)
        elif event.keysym == "Right":
            direction = (1, 0)

        if direction:
            self.move_player(direction)

    def move_player(self, direction):
        """Move the player in the specified direction."""
        new_x = self.battle.fighters[0].position.x + direction[0]
        new_y = self.battle.fighters[0].position.y + direction[1]
        new_pos = self.battle.map.get_position(new_x, new_y)

        if new_pos and not self.battle.map.is_position_occupied(new_pos) and new_pos.terrain != Terrain.WATER:
            self.battle.map.move_fighter(self.battle.fighters[0], new_pos)
            self.battle.fighters[0].position.x = new_x
            self.battle.fighters[0].position.y = new_y
            self.draw_map()  # Redraw the entire map
            self.log_message(f"Player moved to ({new_x}, {new_y})")

    def log_message(self, message):
        """Log a message in the log text area."""
        self.info_text.config(state="normal")
        self.info_text.insert(tk.END, message + "\n")
        self.info_text.config(state="disabled")
        self.info_text.see(tk.END)  # Scroll to the end

        # Limit the number of lines in the log to the last 10
        self._limit_log_lines(10)  # Change this number to the desired number of visible lines

    def _limit_log_lines(self, max_lines):
        """Remove old lines to keep only the most recent ones."""
        self.info_text.update_idletasks()  # Ensure the text widget has been updated
        num_lines = int(self.info_text.index('end-1c').split('.')[0])
        if num_lines > max_lines:
            self.info_text.delete('1.0', f'{num_lines - max_lines}.0')

if __name__ == "__main__":
    root = tk.Tk()
    gui = RoguelikeGUI(root, map_width=10, map_height=10, hex_orientation="flat-top") # "flat-top", "pointy-top", or None
    root.mainloop()
