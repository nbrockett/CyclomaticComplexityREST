import matplotlib.pyplot as plt

# (number of nodes, time required to compute cc)
result = [(1,2,3,4,5,6,7), (90.01,42.60,31.76,26.23,22.28,21.97,21.07)]  # results taken from real run



fig = plt.figure()
ax = fig.add_subplot(111)
xs = range(5)
ys = range(26)

ax.plot(result[0], result[1])
ax.set_title('Code Complexity - Worker Stealing Scheme')
ax.set_xlabel('nodes')
ax.set_ylabel('time [s]')
ax.set_ylim([0,100])
plt.show()