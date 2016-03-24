# Hacky script to plot the distribution of briefs per case (data source: pivot table)
__author__ = 'lars'

import numpy as np
from matplotlib import pyplot as plt

briefs = [1, 5, 7, 1, 3, 2, 6, 21, 5, 3, 2, 4, 2, 3, 4, 8, 1, 13, 6, 16, 7, 1, 1, 8, 2, 4, 3, 6, 2, 8, 3, 4, 3, 13, 28, 11, 2, 8, 41, 7, 9, 22, 70, 2, 3, 6, 1, 10, 6, 10, 8, 1, 12, 12, 3, 9, 8, 30, 9, 6, 2, 1, 5, 9, 3, 6, 5, 3, 12, 6, 8, 3, 1, 17, 5, 27, 3, 9, 5, 6, 12, 3, 7, 8, 7, 2, 13, 7, 18, 18, 7, 6, 3, 1, 5, 22, 12, 1, 9, 1, 4, 3, 11, 4, 4, 1, 11, 6, 7, 2, 4, 17, 2, 16, 3, 11, 7, 23, 18, 9, 15, 5, 4, 1, 10, 3, 3, 3, 5, 3, 2, 5, 8, 2, 3, 9, 21, 5, 19, 14, 12, 3, 16, 3, 10, 40, 6, 7, 3, 4, 9, 51, 6, 5, 15, 3, 2, 7, 7, 30, 3, 6, 16, 3, 7, 10, 7, 14, 6, 5, 4, 1, 2, 1, 21, 21, 21, 8, 17, 4, 15, 4, 4, 67, 3, 15, 6, 2, 3, 3, 4, 3, 1, 2, 4, 8, 3, 1, 1, 14, 19, 11, 32, 7, 14, 8, 4, 8, 4, 11, 6, 14, 13, 3, 3, 4, 11, 3, 10, 9, 4, 4, 9, 15, 29, 8, 29, 1, 4, 14, 11, 1, 6, 3, 9, 3, 10, 13, 7, 8, 10, 7, 5, 2, 4, 1, 15, 3, 5, 10, 5, 1, 27, 4, 3, 21, 14, 5, 10, 4, 32, 7, 6, 5, 23, 28, 27, 48, 8, 8, 2, 1, 6, 15, 4, 5, 27, 6, 1, 13, 16, 6, 6, 8, 2, 5, 18, 4, 4, 30, 3, 4, 5, 2, 2, 1, 11, 8, 1, 3, 7, 15, 8, 12, 7, 24, 34, 3, 13, 2, 3, 5, 8, 2, 27, 2, 4, 10, 4, 2, 13, 2, 5, 23, 5, 10, 2, 17, 5, 3, 8, 6, 38, 2, 13, 15, 5, 2, 5, 21, 4, 69, 35, 3, 5, 5, 11, 11, 11, 6, 3]
for i in range(409-351): briefs.append(0)

briefs.sort(reverse=True)
cumSum = np.cumsum(briefs)
cumSum = [0] + cumSum

straightLine = np.linspace(0, cumSum[-1], len(cumSum))

fig = plt.figure()
fig.patch.set_facecolor('white')
plt.gca().set_axis_bgcolor('white')

axes = plt.gca()
axes.set_xlim([0,409])
axes.set_ylim([0,3500])

plt.plot(cumSum, label='actual distribution')
plt.plot(straightLine, 'k--', label='uniform distribution')
plt.title('Cummulative distribution of #amicus briefs per docket')
plt.xlabel('dockets in decreasing order of #amicus briefs')
plt.ylabel('#amicus briefs')
plt.legend(loc=4)
plt.show()
