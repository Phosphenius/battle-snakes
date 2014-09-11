"""Contains useful functions"""

def add_vecs(vec1, vec2):
    """Add vectors."""
    return (vec1[0] + vec2[0], vec1[1] + vec2[1])

def mul_vec(vec, scalar):
    """Multiply vector with scalar."""
    return (vec[0] * scalar, vec[1] * scalar)

def str_to_vec(data):
    """Convert string rep. of a vector to tuple."""
    return tuple(int(i) for i in data.strip().split(':'))

# Converts a string representation of vectors to a list of tuples
def str_to_vec_lst(data):
    """Convert string rep. of vector list to tuple list."""
    veclst = []
    for entry in data.strip().split(';'):
        veclst.append(str_to_vec(entry))
    return veclst

class Timer(object):

    """
    Simple infinite timer.

    Note: Timer cannont be stopped.
    """

    def __init__(self, intervall, tick, delay=0, running=False):
        self.intervall = intervall
        self.tick = tick
        self.elapsed_t = 0.
        self.delay = delay
        self.running = running if self.delay == 0 else False

    def start(self, delay=0):
        """Start timer."""
        if delay != 0:
            self.delay = delay
            return
        self.running = True
        self.elapsed_t = 0.

    def update(self, delta_time):
        """Update timer."""
        if self.running:
            self.elapsed_t += delta_time
            if self.elapsed_t >= self.intervall:
                self.elapsed_t -= self.intervall
                # On tick
                if self.tick is not None:
                    self.tick()
                else:
                    raise Exception('No Tick-event handler!')
        elif self.delay > 0.:
            self.elapsed_t += delta_time
            if self.elapsed_t >= self.delay:
                self.running = True
                self.elapsed_t = 0.
