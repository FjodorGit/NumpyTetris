import numpy as np 
import random
import os
from collections import deque

def clear():
	os.system("clear")

# First four tuples are coordinates of the tile and the last one is the centre of it; used for rotation
z_tile = np.array([[0,3],[0,4],[1,4],[1,5],[0,4]])
line_tile = np.array([[1,3],[1,4],[1,5],[1,6],[1.5, 4.5]])
l_tile = np.array([[0,5],[1,3],[1,4],[1,5],[1,4]])
square_tile = np.array([[0,4],[0,5],[1,4],[1,5],[0.5, 4.5]])
j_tile = np.array([[0,3],[1,3],[1,4],[1,5],[1,4]])
t_tile = np.array([[0,4],[1,3],[1,4],[1,5],[1,4]])
s_tile = np.array([[0,4],[0,5],[1,3],[1,4],[0,4]])

all_tiles = [t_tile, line_tile, square_tile, l_tile, j_tile, s_tile, z_tile]

'''
Tetris has three visible elements: The screen, the preview of the next tiles and a place to hold a tile
later use
'''

class Tetris():

	def __init__(self):
        
        #boundaries to prevent a tile from going off screen
		self.left_bounds = [[elem, -1] for elem in np.arange(0,23)]
		self.right_bounds = [[elem, 10] for elem in np.arange(0,23)]
		self.lower_bounds = [[22, elem] for elem in np.arange(-1,11)]
		top_bounds = [[-1, elem] for elem in np.arange(-1,11)]
		self.boundaries = self.left_bounds + self.right_bounds + self.lower_bounds + top_bounds

		self.holding = [] #the place to hold a tile
		self.ones_locations = [] #coordinates of already unmoveable tiles 
		
		self.preview_que = deque(maxlen=5) 
		self.fill_que() 
		self.spawn_tile()

	def fill_que(self):
        
		for i in range(5):
			rand_tile = np.copy(random.sample(all_tiles, k = 1)[0])
			rand_tile = rand_tile + np.array([i*3, -3])
			self.preview_que.append(rand_tile)
            
		#print(self.preview_que)


	def spawn_tile(self):
		
		new_tile = np.copy(random.sample(all_tiles, k = 1)[0]) #creates a new tile
		new_tile =  new_tile + np.array([12,-3]) #puts it in buttom of the que
		self.tile = np.copy(self.preview_que[0]) + np.array([0,3]) #takes the top tile from the que
        
        #moves the remaining tiles in the que one position up
		for i in range(len(self.preview_que)):
			self.preview_que[i] += np.array([-3,0])
		self.preview_que.append(new_tile)
        
        #the line tile performs some movements diffrenttly than the other tiles
		for i in range(len(self.tile)):
			if list(self.tile[i]) == list(line_tile[i]):
				self.move_magnitude = 2
			else:
				self.move_magnitude = 1
                
		self.hold_blocked = False # hold blocked prevents the player from perfroming the hold action
                                  # twice in a row
                                        

	def get_state(self): #creates a the visible screen from an array of positions
        
		self.screen = np.zeros((22,10))
		self.holding_screen = np.zeros((2,4))
		self.preview_screen = np.zeros((14,4))

		all_ones = [self.tile[0:-1], self.ones_locations]
		for pos_array in all_ones:
			for elem in pos_array:
				[height, width] = elem
				self.screen[int(height), int(width)] = 1

		for elem in self.holding[0:-1]:
			[height, width] = list(elem)
			self.holding_screen[int(height), int(width)] = 1

		for tile in self.preview_que:
			for block in tile[0:-1]:
				[height, width] = list(block)
				self.preview_screen[int(height), int(width)] = 1



	def act_on_tile(self, tile, move_matrix = np.array([1,0])):
		tile = np.array(tile, dtype = np.float32)
        
        # the behavior for turning a tile
		if len(move_matrix.shape) == 2:
			on_origin = (tile[0:-1] - tile[-1]).T
			turned_on_origin = np.matmul(move_matrix, on_origin).T
			tile[0:-1] = turned_on_origin + tile[-1]
        #all other behavior

		else:
			tile += move_matrix

		return tile

	def check_for_collison(self, tile):

		has_to_move = False

		for position in tile[0:-1]:
			if list(position) in self.ones_locations or list(position) in self.boundaries:
					has_to_move = True
					break

		return has_to_move

	def turn(self, direction):
        
        #if a turn causes a colision with boundaries
		correction_vektors = [np.array([-1,0]),np.array([0,-1]), np.array([0,1]),np.array([1,0])]

        #special behavior for the line tile
		if self.move_magnitude == 2:
			for i in range(len(correction_vektors)):
				correction_vektors.append(correction_vektors[i]*self.move_magnitude)

		if direction == "left":
			rotation_matrix = np.array([[0,1],[-1,0]])
		if direction == "right":
			rotation_matrix = np.array([[0,-1],[1,0]])
		if direction == "180":
			rotation_matrix = np.array([[-1,0],[0,-1]])
            
        #checks for collisions and moves the tile accordingly
		turned_tile = self.act_on_tile(np.copy(self.tile), move_matrix = rotation_matrix)
		has_to_move = self.check_for_collison(turned_tile)
        
		if has_to_move:
			for i in range(len(correction_vektors)):
				turned_tile = self.act_on_tile(np.copy(self.tile), move_matrix = rotation_matrix)
				turned_tile = self.act_on_tile(turned_tile, move_matrix = correction_vektors[i])
				has_to_move = self.check_for_collison(turned_tile)
				if not has_to_move:
					self.tile = np.copy(turned_tile)
					break
		else:
			self.tile = np.copy(turned_tile)

	def fall_or_stop(self): 
        #if no action is registered it is possible for the tile to become unmovable
		self.tile = self.act_on_tile(self.tile, move_matrix = np.array([1,0]))
		self.spawned = False
		for position in self.tile[0:-1]:
			if list(position) in self.ones_locations or list(position) in self.lower_bounds:
				self.tile = self.act_on_tile(self.tile, move_matrix = np.array([-1, 0]))
				for elem in self.tile[0:-1]:
					self.ones_locations.append(list(elem))
				self.spawn_tile()
				self.spawned = True
				break

	def slide_to_the(self, direction):
		if direction == "left":
			direction_vektor = np.array([0,-1])
		if direction == "right":
			direction_vektor = np.array([0,1])

		moved_tile = self.act_on_tile(np.copy(self.tile), move_matrix = direction_vektor)
		has_to_move = self.check_for_collison(moved_tile)

		if not has_to_move:
			self.tile = np.copy(moved_tile)

	def hard_drop(self):
        
        #searches for the least amount free space under the tile and moves it down that much, gives
        # twice the distance dropped as reward
        
		tile_in_cols = []
		for col in self.tile[0:-1,1]:
			if col not in tile_in_cols:
				tile_in_cols.append(col)


		highest_points = []
		for column in tile_in_cols:
			highest_col = 22
			for location in (self.ones_locations+self.lower_bounds):
				#print("location: ",location[1] ," and ", col)
				if location[1] == column and location[0] <= highest_col:
					highest_col = location[0]
					col_location = column
			highest_points.append([highest_col,col_location])


		drop_height = 21 - np.max(self.tile[0:-1,0])
		for location in highest_points:
			for block in list(self.tile[0:-1]):
				if block[1] == location[1] and (location[0] - block[0] - 1) < drop_height:
						drop_height = (location[0] - block[0] - 1)

		self.tile = self.act_on_tile(self.tile, move_matrix=(np.array([1,0])*(drop_height)))

		for elem in self.tile[0:-1]:
			self.ones_locations.append(list(elem))
		self.spawn_tile()

		score = drop_height*2

		return score

	def soft_drop(self):
        
        # drops a random disatance between 2 and 4 and gives it a reward  
        
		times_list = [2,3,4]
		times = random.sample(times_list, k=1)[0]
		for i in range(times):
			self.fall_or_stop()
			if self.spawned:
				break

		return times

	def hold(self):
        
        #a tile could already have been turned on the gamescreen. So it has to be rotated back to fit into
        #the hold field
        
		if not self.hold_blocked:
			tile_height_min = np.min(self.tile[0:-1,0])
			tile_height_max = np.max(self.tile[0:-1,0])
			tile_width_min = np.min(self.tile[0:-1,1])

			if (tile_height_max - tile_height_min) > 1:
				tile_to_hold = self.act_on_tile(np.copy(self.tile), move_matrix = np.array([[0,1],[-1,0]]))
				tile_height_min = np.min(tile_to_hold[0:-1,0])
				tile_width_min = np.min(tile_to_hold[0:-1,1])

				tile_to_hold = tile_to_hold - np.array([tile_height_min, tile_width_min])
			else:
				tile_to_hold = np.copy(self.tile) - np.array([tile_height_min, tile_width_min])

			if len(self.holding) > 0:
				self.tile = np.copy(self.holding) + np.array([0,3])
				self.holding = tile_to_hold
			else:
				self.holding = tile_to_hold
				self.spawn_tile()
			self.hold_blocked = True


	def take_action(self, action):
		reward = 0
		if action == "up" or action == "turn_right":
			self.turn("right")
		if action == "z" or action == "turn_left":
			self.turn("left")
		if action == "space" or action == "hard_drop":
			reward = self.hard_drop()
		if action == "left":
			self.slide_to_the("left")
		if action == "right":
			self.slide_to_the("right")
		if action == "c" or action == "hold":
			self.hold()
		if action == "down" or action == "soft_drop":
			#print("take action softdrop")
			reward = self.soft_drop()
		if action == "a" or action == "180":
			self.turn("180")
		if action == "nothing":
			self.fall_or_stop()

		return reward

	def clear_lines(self):
        
        #ckeck if a line needs to be cleared:
        #clears the line and moves the remaining chuck above the cleared line one step down
        
		lines_cleared = 0
		for height in list(np.arange(0,22)):
			line_tile_to_clear = []
			for width in list(np.arange(0,10)):
				if [height, width] in self.ones_locations:
					line_tile_to_clear.append([height, width])
                    
			if len(line_tile_to_clear) == 10:
				for elem in line_tile_to_clear:
					self.ones_locations.remove(elem)
				for i in range(len(self.ones_locations)):
					if self.ones_locations[i][0] < height:
						print("line cleared at: ", height)
						self.ones_locations[i] = list(self.act_on_tile(np.array(self.ones_locations[i]), move_matrix = np.array([1,0])))

				lines_cleared += 1

		if lines_cleared > 0:
			score = 200*lines_cleared - 100
			if lines_cleared == 4:
				score += 100
		else:
			score = int(0)

		return score

	def check_for_restart(self): 
        #checks if there is an unmovable element in the top row and restarts the game if this is the case
    
		score = 0
		restart_reqired = False
		top_row = [[0,elem] for elem in np.arange(0,10)]
		for elem in top_row:
			if elem in self.ones_locations:
				self.ones_locations = []
				self.fill_que()
				self.spawn_tile()
				restart_reqired = True

				score = -1

		return score, restart_reqired

