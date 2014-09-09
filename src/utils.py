# Adds to vectors
def add_vecs(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

# Multiplies a vector with a scalar
def mul_vec(v1, scalar):
    return (v1[0] * scalar, v1[1] * scalar)

# Converts the string representation of a vector to a tuple
def str_to_vec(data):
	return tuple(int(i) for i in data.strip().split(':'))

# Converts a string representation of vectors to a list of tuples
def str_to_vec_lst(data):
		veclst = []
		for entry in data.strip().split(';'):
			veclst.append(str_to_vec(entry))
		return veclst

# Simple infinite timer
# Note: Timer can't be stopped or paused
class Timer:
	def __init__(self, intervall, tick, delay=0, running=False):
		self.intervall = intervall
		self.Tick = tick
		self.elapsed_t = 0.
		self.delay = delay
		self.running = running if self.delay == 0 else False
		
	def start(self, delay=0):
		if delay != 0:
			self.delay = delay
			return
		self.running = True
		self.elapsed_t = 0.
		
	def update(self, dt):
		if self.running:
			self.elapsed_t += dt
			if self.elapsed_t >= self.intervall:
				self.elapsed_t -= self.intervall
                # On tick
				if self.Tick is not None:
					self.Tick()
				else:
					raise Exception('No Tick-event handler!')
		elif self.delay > 0.:
			self.elapsed_t += dt
			if self.elapsed_t >= self.delay:
				self.running = True
				self.elapsed_t = 0.
