"""
Array Backed Grid Shown By Sprites

Show how to use a two-dimensional list/array to back the display of a
grid on-screen.

This version makes a grid of sprites instead of numbers. Instead of
iterating all the cells when the grid changes we simply just
swap the color of the selected sprite. This means this version
can handle very large grids and still have the same performance.
"""
import arcade
from arcade.types import Color

GRAY = Color.from_gray(140)
WHITE = Color.from_gray(255)

# Set how many rows and columns we will have
ROW_COUNT = 16
COLUMN_COUNT = 16

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 47
HEIGHT = 47

# Do the math to figure out our screen dimensions
WINDOW_WIDTH = WIDTH * COLUMN_COUNT
WINDOW_HEIGHT = HEIGHT * ROW_COUNT
WINDOW_TITLE = "Trax game"

RECTO = arcade.load_texture("2222.png")
VERSO = arcade.load_texture("1111.png")

CLIC = {
    1 : {"recto" : False,
         "texture" : VERSO},
    4 : {"recto" : True,
         "texture" : RECTO}
}
DELTAS = [
{   "Δcoos":(1,0), # (x,y)
    "side_tuile":1,    
    "side_slot":3   },
{   "Δcoos":(0,1),
    "side_tuile":0,
    "side_slot":2   },
{   "Δcoos":(-1,0),
    "side_tuile":3,
    "side_slot":1   },
{   "Δcoos":(0,-1),
    "side_tuile":2,
    "side_slot":0   },
]


NEUTRAL = arcade.Sprite(path_or_texture = "1111.png", angle = 0.0, alpha=0)
NEUTRAL.recto = False
NEUTRAL.alpha = 0

def side_tocolor(tile:arcade.Sprite, side:int=None) :
    side_clrs = [["b","n","n","b"] if tile.recto else ["b","n","b", "n"]][0]
    for i in range(int(tile.angle)//90) : 
        side_clrs = [side_clrs[-1]] +side_clrs[:-1]
    if side is not None :
        return side_clrs[side]
    else : return side_clrs

def color_tosides(tile:arcade.Sprite, color:str) :
    side_clrs = [["b","n","n","b"] if tile.recto else ["b","n","b", "n"]][0]
    for i in range(int(tile.angle)//90) : 
        side_clrs = [side_clrs[-1]] +side_clrs[:-1]
    return [i for i, x in enumerate(side_clrs) if x == color]


def reverse_contraintes(contraintes) :
    rev_contraintes = {}
    for key, value in contraintes.items():
        if value in rev_contraintes :
            rev_contraintes[value].append(key)
        else :
            rev_contraintes[value] = [key]
    return rev_contraintes

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.WHITE
        self.grid_tiles_list = arcade.SpriteList()
        self.grid_tiles = []
        self.curr_mouse_tile = [0,0]
        self.curr_args ={
            "recto" : False,
            "texture" : VERSO,
            "angle" : 0.0
        }
        self.dimensions = [0,0] # à voir comment remplir ce truc

        for row in range(ROW_COUNT):
            self.grid_tiles.append([])
            for column in range(COLUMN_COUNT):
                x = column * WIDTH + WIDTH / 2
                y = row * HEIGHT + HEIGHT / 2
                sprite = arcade.Sprite(path_or_texture = "1111.png", angle = 0.0)
                sprite.center_x = x
                sprite.center_y = y
                sprite.alpha = 0
                sprite.recto = False
                self.grid_tiles_list.append(sprite)
                self.grid_tiles[row].append(sprite)

        self.playable_slots = {(8,8):{}, (7,7):{}, (7,8):{}, (8,7):{}} # { coos_slot:{side:color, ...} }

    def on_update(self, delta_time) :
        # put logic here
        for tile in self.grid_tiles_list :
            tile.update()
        # Call update() on the sprite lists that need it

    def get_adjacents(self, row, column) :
        return {delta["side_tuile"] : self.grid_tiles[row+delta["Δcoos"][1]][column+delta["Δcoos"][0]] for delta in DELTAS if self.grid_tiles[row+delta["Δcoos"][1]][column+delta["Δcoos"][0]].alpha == 255}
        # off_grid = s_row >= ROW_COUNT or s_column >= COLUMN_COUNT or s_row < 0 or s_column < 0

    def walk(self, current_tile, color, current_side, origin_tile) -> bool :
        if current_tile.alpha != 255 : return None
        next_sides = color_tosides(current_tile, color)
        next_sides.remove(current_side)
        next_side = next_sides[0]

        curr_row, curr_column = int(current_tile.center_y // HEIGHT), int(current_tile.center_x // WIDTH)
        delta = [delta for delta in DELTAS if delta["side_tuile"]==next_side][0]
        next_row, next_column = curr_row+delta["Δcoos"][1], curr_column+delta["Δcoos"][0]
        next_tile = self.grid_tiles[next_row][next_column]
        if next_tile != origin_tile :
            return self.walk(next_tile, color, (next_side+2)%4, origin_tile)
        else :
            return color

    def check_winner(self, row, column) :
        origin_tile = self.grid_tiles[row][column]
        adjacents = self.get_adjacents(row, column)
        # { side_tuile:Sprite, side_tuile:Sprite}
        if len(adjacents) >= 2 :
            colors = {
                "b" : [],
                "n" : []
            }
            for side_origin,concerned_tile in adjacents.items() :
                colors[side_tocolor(origin_tile, side=side_origin)].append([side_origin,concerned_tile])
            # colors = {"b":[[origin_side, tile], [origin_side]], "n":[]}
            # donc tile_side = (origin_side+2)%4

            for color, tiles in colors.items() :
                if len(tiles)<=1 : pass
                else :
                    winner = self.walk(tiles[0][1], color, (tiles[0][0]+2)%4, origin_tile)
                    print(winner)
                    return winner

    def detect_playable_slots_tile(self, coos_tuile) :
        playable = {}
        column, row = coos_tuile
        for delta in DELTAS :
            s_column, s_row = column+delta["Δcoos"][0], row+delta["Δcoos"][1]
            coos_slot = (s_column, s_row)
            off_grid = s_row >= ROW_COUNT or s_column >= COLUMN_COUNT or s_row < 0 or s_column < 0
            if not off_grid :
                current_tile = self.grid_tiles[s_row][s_column]
            
                if current_tile.alpha != 255 :
                    color = side_tocolor(self.grid_tiles[row][column], side = delta["side_tuile"])
                    
                    if coos_slot in self.playable_slots : # s'il y a déjà une contrainte sur le slot
                        self.playable_slots[coos_slot][delta["side_slot"]] = color # {side1:color1, side2:color2}
                        if coos_slot not in playable :
                            playable[coos_slot] = self.playable_slots[coos_slot]
                    else : 
                        self.playable_slots[coos_slot] = {delta["side_slot"]:color} # {side:color}  

                    if coos_slot in playable : # s'il y a déjà une contrainte sur le slot
                        playable[coos_slot][delta["side_slot"]] = color # {side1:color1, side2:color2}
                    else : 
                        playable[coos_slot] = {delta["side_slot"]:color} # {side:color} 

        return playable 

    def detect_playable_slots_plateau(self) :
        self.playable_slots = {}
        for row, rowlist in enumerate(self.grid_tiles) :
            for column, tile in enumerate(rowlist) :
                if tile.alpha == 255 :
                    self.detect_playable_slots_tile([column, row])

    def play_forced(self, coos_tuile=None, suivantes=[]) :
        if coos_tuile :
            playable = self.detect_playable_slots_tile(coos_tuile)
        else :
            self.detect_playable_slots_plateau()
            playable = self.playable_slots

        for coos_slot in playable :
            contraintes = reverse_contraintes(playable[coos_slot])
            for color, sides in contraintes.items() :
                if len(sides) == 2 :
                    if (abs(sides[0] - sides[1] + 4)%2) == 1 :
                        tile = self.grid_tiles[coos_slot[1]][coos_slot[0]]
                        tile.recto, tile.texture = True, RECTO
                    else :
                        tile = self.grid_tiles[coos_slot[1]][coos_slot[0]]
                        tile.recto, tile.texture = False, VERSO


                    x=0
                    while not (side_tocolor(tile, side=sides[0]) == side_tocolor(tile, side=sides[1]) == color) :
                        tile.angle = (tile.angle + 90.0) % 360.0
                        x+=1
                        if x>= 5 : 
                            print("error boucle infinie")
                            return
                        
                    if coos_slot not in suivantes :
                        suivantes.append(coos_slot)
                    tile.alpha = 255

        if suivantes :
            prochain = suivantes.pop(0)
            del self.playable_slots[prochain]
            self.play_forced(coos_tuile=prochain, suivantes=suivantes)

    def on_draw(self):
        # We always start by clearing the window pixels
        self.clear()
        # Batch draw the grid sprites
        self.grid_tiles_list.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        row, column = int(y // HEIGHT), int(x // WIDTH)

        if row >= ROW_COUNT or column >= COLUMN_COUNT: # Nothing needs updating
            return
        tile = self.grid_tiles[row][column]
        if button not in [1,4] : return

        adjacents = self.get_adjacents(row, column)
        contraintes = {side:side_tocolor(adj_tile, side=(side+2)%4) for side,adj_tile in adjacents.items()}
        respected = [side_tocolor(tile, side=side)==color for side,color in contraintes.items()]

        if tile.recto == CLIC[button]["recto"] and (all(respected) or adjacents=={}) :
            match tile.alpha :
                case 0 : return
                case 90 : tile.alpha = 255
                case 255 : tile.alpha = 90
            self.play_forced(coos_tuile=[column, row])
            self.detect_playable_slots_plateau()
            self.check_winner(row, column)
        else :
            tile.recto = CLIC[button]["recto"]
            tile.texture = CLIC[button]["texture"]
            if tile.alpha == 90 :
                self.curr_args["recto"] = CLIC[button]["recto"]
                self.curr_args["texture"] = CLIC[button]["texture"]

    def on_mouse_motion(self, x, y, dx, dy):
        row, column = int(y // HEIGHT), int(x // WIDTH)
        if row >= ROW_COUNT or column >= COLUMN_COUNT: # Nothing needs updating
            return
        if [row, column] == self.curr_mouse_tile : return

        tile = self.grid_tiles[row][column]
        prev_row, prev_column = self.curr_mouse_tile
        prev_tile = self.grid_tiles[prev_row][prev_column]

        if tile.alpha == 0 and (column, row) in self.playable_slots :
            tile.color = GRAY
            tile.alpha = 90
            tile.angle = self.curr_args['angle']
            tile.texture = self.curr_args["texture"]
            tile.recto = self.curr_args["recto"]
        elif tile.alpha == 90 : pass
        elif tile.alpha == 255 : tile.color = GRAY

        if prev_tile.alpha == 90 :
            prev_tile.color = WHITE
            prev_tile.alpha = 0
            prev_tile.angle = 0
            prev_tile.texture = VERSO
            prev_tile.recto = False
        elif prev_tile.alpha != 0 : 
            prev_tile.color = WHITE

        self.curr_mouse_tile = [row, column]

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y) :
        # Convert the clicked mouse position into grid coordinates
        row, column = int(y // HEIGHT), int(x // WIDTH)
        if row >= ROW_COUNT or column >= COLUMN_COUNT: # Nothing needs updating
            return

        tile = self.grid_tiles[row][column]
        tile.angle = (tile.angle + scroll_y * 90.0) % 360.0
        if tile.alpha == 90 :
            self.curr_args["angle"] = tile.angle

    def on_key_press(self, symbol, modifiers):
        pass


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    window.set_location(0,0)
    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()


""" IDEAS :

        Click on X-Tile but W-Tile alrdy clicked
        -> call func check_selected_tiles(coos_tile_clicked)
        -> If exists Tile with coos != coos_tile_clicked
            -> Then Tile.reset() ------> angle=0.0 & Alpha=0


        Call it every time a tile is placed
        it detects the adjacent ones
        it stores them in a style {"b":[tile, tile], "n":[]}
        if a color has 2 elements :
            takes the sides with color


        faire une fonction relation(tile1, tile2)

"""

