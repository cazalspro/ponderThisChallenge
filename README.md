
# ponderThisChallenge
__Problem formulation :__

A game is played on an $n\cdot n$ grid of lightbulbs. We are given an initial state where some of the bulbs are off and some are on. Then, at every step a bulb in the off state is chosen.

The bulb is turned on, and every other bulb in the row and in the column of the bulb is toggled: If it was on, it turns off, and vice versa.

The goal of the game is to reach a grid where all the light bulbs are on. We use a coordinate system where the grid cell at column $x$ and row $y$ , with $1 \leqslant x,y \leqslant$ n is denoted by $(x,y)$ , where $(1,1)$ is the bottom-left grid cell. A solution is denoted by a list of coordinates of the corresponding bulbs.

More informations and instances on : https://research.ibm.com/haifa/ponderthis/challenges/April2023.html

__Current state :__

The model is correct but generates many constraints ($O(n⁶)$), I will improve it in the next commit, as well as the code readability.

I also think that I will have to use another solver than GLPK to succeed in solving the requested instances.
