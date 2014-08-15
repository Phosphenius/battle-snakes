from settings import *
from utils import add_vecs

# -- Directions --
RIGHT = (+1, 0)
LEFT = (-1, 0)
UP = (0, -1)
DOWN = (0, +1)

class SnakeNormalState:
	def __init__(self, snake):
		self.snake = snake
		
	def get_name(self):
		return 'Normal'
		
	def update(self, dt):
		self.snake.move()
	
class SnakeInvincibleState:
	def __init__(self, snake, lifetime):
		self.snake = snake
		self.snake.isinvincible = True
		self.lifetime = lifetime
		self.elapsed_lifetime = 0.
		self.elapsed_blink = 0.

	def get_name(self):
		return 'Invincible'

	def update(self, dt):
		self.elapsed_lifetime += dt
		self.elapsed_blink += dt
			
		if self.elapsed_blink >= INVINCIBILITY_BLINK_RATE:
			self.elapsed_blink -= INVINCIBILITY_BLINK_RATE
			self.snake.isvisible = not self.snake.isvisible
			
		if self.elapsed_lifetime >= self.lifetime:
			self.snake.change_state(SnakeNormalState(self.snake))
			
		self.snake.move()

	def leave(self):
		self.snake.isinvincible = False
		self.snake.isvisible = True
		
class Snake(object):
	def __init__(self, game, pos, tex, _id, killed_handler):
		self.game = game
		self.body_tag = '#p{0}-body'.format(_id)
		self.head_tag = '#p{0}-head'.format(_id)
		self.tex = tex
		self.body = [pos, (pos[0] + 1, pos[1])]
		self.heading = None
		self._hitpoints = MAX_HITPOINTS
		self._speed = INIT_SPEED
		self._speed_bonus = 0
		self.elapsed_t = 0.
		self.grow = 0
		self.isalive = True
		self.isvisible = True
		self.isinvincible = False
		self.ismoving = False
		self.curr_state = SnakeInvincibleState(self, 5)
		self.killed_event = killed_handler
		self.prev = self.body[:]
		self.prev_heading = self.heading
		
	@property
	def hitpoints(self):
		return self._hitpoints
		
	@hitpoints.setter
	def hitpoints(self, value):
		if value > MAX_HITPOINTS:
			self._hitpoints = MAX_HITPOINTS
		elif value < 0:
			self._hitpoints = 0
		else:
			self._hitpoints = value
		
	@property
	def speed(self):
		return self._speed
		
	@speed.setter
	def speed(self, value):
		if value > MAX_SPEED:
			self._speed = MAX_SPEED
		elif value < MIN_SPEED:
			self._speed = MIN_SPEED
		else:
			self._speed = value
		
	@property
	def speed_bonus(self):
		return self._speed_bonus
		
	@speed_bonus.setter
	def speed_bonus(self, value):
		self._speed_bonus = value
		
	def gain_speed(self, speed):
		self.speed += speed
			
	def gain_hitpoints(self, hp):
		self.hitpoints += hp
		if self.hitpoints > MAX_HITPOINTS:
			self.hitpoints = MAX_HITPOINTS
		
	def set_heading(self, new_heading):
		self.prev_heading = self.heading
		self.heading = new_heading
		
	def change_state(self, new_state):
		if hasattr(self.curr_state, 'leave'):
			self.curr_state.leave()
		self.curr_state = new_state

	def take_damage(self, dmg, by, setback=False,
	invincible=False, invinc_lifetime=0, shrink=0, slowdown=0):
		if not self.isinvincible:
			self.hitpoints -= dmg
			for i in range(shrink):
				if len(self.body) == 2:
					break
				if setback:
					self.prev.pop()
				else:
					self.body.pop()
			self.gain_speed(-slowdown)
				
		if setback:
			# Set the snake back to its previous position
			self.body = self.prev[:]
			x = 0
			y = 0
			if self.body[0][0] > self.body[1][0]:
				x = 1
			elif self.body[0][0] < self.body[1][0]:
				x = -1
			if self.body[0][1] > self.body[1][1]:
				y = 1
			elif self.body[0][1] < self.body[1][1]:
				y = -1
			self.set_heading((x, y))
			self.prev_heading = (x, y)
		
		if invincible and not self.isinvincible:
			self.change_state(SnakeInvincibleState(self, invinc_lifetime))
				
		if self.hitpoints <= 0:
			self.isalive = False
			self.killed_event(by)

	def respawn(self, pos):
		self.body = [pos, (pos[0] + 1, pos[1])]
		self._speed = INIT_SPEED
		self.heading = None
		self.prev_heading = None
		self.ismoving = False
		self.isalive = True
		self.hitpoints = MAX_HITPOINTS
		self.change_state(SnakeInvincibleState(self, 3.5))
		self.elapsed_t = 0
		
	def update(self, dt):
		if not self.isalive:
			return
			
		if self.ismoving:
			self.elapsed_t += dt
			
		self.curr_state.update(dt)
			
	def move(self):
		if not self.ismoving:
			return
			
		self.body[0] = self.game.toroidal(self.body[0])
		# Move Snake
		if self.elapsed_t >= 1. / (self._speed + self._speed_bonus):
			self.prev = self.body[:]
			self.elapsed_t -= 1. / (self._speed + self._speed_bonus)
			self.body.insert(0, add_vecs(self.body[0], self.heading))
			if self.grow == 0:
				self.body.pop()
			elif self.grow > 0:
				self.grow -= 1
			elif self.grow < 0:
				for i in range(-self.grow+1):
					if len(self.body) == 2:
						break
					self.body.pop()
				self.grow = 0
			
	def draw(self):
		if not self.isalive:
			return
		if self.isvisible:
			for i, b in enumerate(self.body):
				tex = self.tex if i != 0 else 'snake_head'
				self.game.graphics.draw(tex, b)
	
	def __setitem__(self, i, item):
		self.body[i] = item
	
	def __getitem__(self, i):
		return self.body[i]
