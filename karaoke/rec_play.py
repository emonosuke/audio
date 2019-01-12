from player import Player
from recorder import Recorder

p = Player('./piano10.wav')

r = Recorder()
r.start()

p.run()
