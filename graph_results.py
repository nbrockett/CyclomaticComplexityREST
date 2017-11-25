import matplotlib.pyplot as plt

# (number of nodes, time required to compute cc)
# result = [(1, 119493), (2, 1231), (3,3124), (4,1231)]
result = [(1,2,3,4,5), (10,9,5,2,2)]

fig = plt.figure()
ax = fig.add_subplot(111)
xs = range(5)
# ys = range(26)

ax.plot(result[0], result[1])
ax.set_title('Code Complexity Performance')
ax.set_xlabel('nodes')
ax.set_ylabel('time')
plt.show()