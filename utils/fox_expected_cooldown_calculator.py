# import random as rand
import math
import matplotlib.pyplot as plt
import matplotlib

K = 0.05

def func(x, k):
    return 1 / (1 + pow(math.e, -k * (x - 2000 * k))) 

x_axis = []
y_axis = []
y_axis_total = []
y_axis_difference = []

last = 0
failing_odds = 1
for x in range(120):
    failing_odds *= (1 - func(x, K))
    print(x, func(x, K), 1 - failing_odds)
    x_axis.append(int(x))
    # y_axis.append((1 - failing_odds))
    y_axis_difference.append(1 - failing_odds - last)
    y_axis_total.append(1 - failing_odds)
    y_axis.append(func(x, K))
    last = (1 - failing_odds)

matplotlib.use('tkagg')

plt.plot(x_axis, y_axis)
plt.title("Probability values")
plt.xlabel("ticks")
plt.ylabel("change")
plt.show()
plt.plot(x_axis, y_axis_total)
plt.title("Probability values min")
plt.xlabel("ticks")
plt.ylabel("change")
plt.show()
plt.plot(x_axis, y_axis_difference)
plt.title("Probability values diff")
plt.xlabel("ticks")
plt.ylabel("change")
plt.show()