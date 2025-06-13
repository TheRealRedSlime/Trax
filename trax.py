from math import *
from kandinsky import *
deltas = [
{	"Δcoos":(1,0),
	"side_tuile":1,    # attention, les y sont positifs vers le bas
	"side_slot":3	},
{	"Δcoos":(0,1),
	"side_tuile":2,
	"side_slot":0	},
{	"Δcoos":(-1,0),
	"side_tuile":3,
	"side_slot":1	},
{	"Δcoos":(0,-1),
	"side_tuile":0,
	"side_slot":2	},
]


class tuile :
	def __init__(self, recto:bool, rotation:int, coordonnées=None) :
		if not 0<=rotation<=3 : raise TypeError; exit()
		if coordonnées : self.coos = coordonnées
		self.recto = recto
		self.rota = rotation

	# def display(self) -> None :
	# 	x,y = self.coos
	# 	for r,row in enumerate(self.UI) :
	# 		for p,pxl in enumerate(row) :
	# 			clr = "red" if pxl==0 else ["white" if pxl==1 else "black"][0]
	# 			set_pixel(x*10+p+160, y*10+r+111, clr)

	# def rotate(self, times) -> None :
	# 	for x in range(times) :
	# 		transposed_matrix = [[self.UI[j][i] for j in range(10)] for i in range(10)]
	# 		self.UI = [[row[i] for i in range(9, -1, -1)] for row in transposed_matrix]
	# 	self.rota = (self.rota + times)%4

def side_color(tile:tuile, side:int) -> int :
	side_clrs = [["b","n","n","b"] if tile.recto else ["n","b","n","b"]][0]
	for i in range(tile.rota) : 
		side_clrs = [side_clrs[-1]] +side_clrs[:-1]
	return side_clrs[side]

# class plateau :
# 	def __init__(self) :
# 		self.playable_slots = {} # { coos_slot:{side:color, ...} }
# 		self.tuiles = {
# 		(0,0):tuile(False,0,coordonnées=(0,0)), 
# 		(0,1):tuile(True,3,coordonnées=(0,1),),
# 		(2,1):tuile(False,0,coordonnées=(2,1),),
# 		(3,1):tuile(True,0,coordonnées=(3,1),),
# 		(1,1):tuile(True,1,coordonnées=(1,1),)
# 		}
# 		self.width = 0
# 		self.height = 0

# 	def display(self) :
# 		for coos_tuile in self.tuiles :
# 			self.tuiles[coos_tuile].display()

	# def play(self, tuile:tuile) :
	# 	self.tuiles[tuile.coos] = tuile
	# 	tuile.display()

	def detect_playable_slots_tile(self, coos_tuile) :
		playable = {}
		for delta in deltas :
			coos_slot = (coos_tuile[0]+delta["Δcoos"][0], coos_tuile[1]+delta["Δcoos"][1]) # coos du slot concerné (jouable)

			if coos_slot not in self.tuiles :
				color = self.tuiles[coos_tuile].side_color(delta["side_tuile"])
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
		for coos_tuile in self.tuiles :
			self.detect_playable_slots_tile(coos_tuile)

	def play_forced(self, coos_tuile=None, suivantes=[]) :
		if coos_tuile :
			playable = self.detect_playable_slots_tile(coos_tuile)
		else :
			playable = self.playable_slots

		for coos_slot in playable :
			contraintes = playable[coos_slot]
			clrs = [contraintes[side] for side in contraintes]
			if len(clrs) == 3 : pass 
			elif len(clrs) == 1 : pass
			elif clrs[0] == clrs[1] :
				tile = tuile(True,0,coordonnées=coos_slot)
				concerned_sides = list(contraintes)
				while not (tile.side_color(concerned_sides[0]) == tile.side_color(concerned_sides[1]) == clrs[0]) :
					tile.rotate(1)
				self.play(tile)
				if coos_slot not in suivantes :
					suivantes.append(coos_slot)
					print(suivantes)

		if suivantes :
			prochain = suivantes.pop(0)
			del self.playable_slots[prochain]
			self.play_forced(coos_tuile=prochain, suivantes=suivantes)




monplateau = plateau()
monplateau.display()
monplateau.detect_playable_slots_plateau()
monplateau.play_forced()
