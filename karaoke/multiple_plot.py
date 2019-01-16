import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

fig1, (ax1, ax2) = plt.subplots(1, 2)

fig2, (ax3, ax4) = plt.subplots(1, 2)

ax1.set_title('Title of ax1')
ax2.set_title('Title of ax2')
ax3.set_title("hoge")
ax4.set_title("fuga")

ax1.imshow([[1, 2], [2, 1]])
ax2.imshow([[2, 1], [1, 2]])

plt.show()
