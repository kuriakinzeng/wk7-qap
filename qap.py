'''
Problem 3: Compute QAP by Hand
Convert the following R1CS into a QAP over real numbers, not a finite field

You can use a computer (Python, sage, etc) to check your work at each step and do the Lagrange interpolate, but you must show each step.

Check your work by seeing that the polynomial on both sides of the equation is the same.

Refer to the code here: https://www.rareskills.io/post/r1cs-to-qap
'''

import numpy as np
from scipy.interpolate import lagrange
import random

# Define the matrices
A = np.array([[0,0,3,0,0,0],
               [0,0,0,0,1,0],
               [0,0,1,0,0,0]])

B = np.array([[0,0,1,0,0,0],
               [0,0,0,1,0,0],
               [0,0,0,5,0,0]])

C = np.array([[0,0,0,0,1,0],
               [0,0,0,0,0,1],
               [-3,1,1,2,0,-1]])

# Convert each matrix into polynomial matrices U V W using Lagrange on xs = [1,2,3] and each column of the matrices
xs = np.array([1,2,3])
# ---- Matrix A ----
xs = np.array([1,2,3])
print(lagrange(xs, [3,0,1])) # 2x^2 - 9x + 10 
print(lagrange(xs, [0,1,0])) # -1x^2 + 4 x - 3
U = np.array([[0,0,2,0,-1,0],
              [0,0,-9,0,4,0],
              [0,0,10,0,-3,0]])
# ---- Matrix B ----
print(lagrange(xs, [1,0,0])) # 0.5 x^2 - 2.5 x + 3
print(lagrange(xs, [0,1,5])) # 1.5 x^2 - 3.5 x + 2
V = np.array([[0,0,0.5,1.5,0,0],
              [0,0,-2.5,-3.5,0,0],
              [0,0,3,2,0,0]])
# ---- Matrix C ----
# We can only do this when none of the elements in each column is zero. 
# There is probably a better way to make this work for A and B as well 
def interpolate_no_zero(col):
    return lagrange(xs, col) 
W = np.apply_along_axis(interpolate_no_zero, 0, C)
print (W)

# Compute Uw, Vw and Ww 
# Choose arbitrary x and y
x = 2
y = 3
out = 3 * x * x * y + 5 * x * y - x- 2*y + 3 # out = 3x^2y + 5xy - x - 2y + 3
v1 = 3*x*x
v2 = v1 * y
w = np.array([1, out, x, y, v1, v2])
print(w) # w =[1 61 2 3 12 36]

# By hand we get Uw = [-8 30 -16]
Uw = np.array([-8, 30, -16])
assert (U.dot(w) == Uw).all(), "Uw calculation is wrong"

# By hand we get Vw = [19 -47 30]
Vw = np.array([5.5, -15.5, 12])
assert (V.dot(w) == Vw).all(), "Vw calculation is wrong"

# By hand we get Ww = [-15  69 -42]
Ww = np.array([-15, 69, -42])
assert (W.dot(w) == Ww).all(), "Ww calculation is wrong"

# Balance the equation by adding h(x)t(x)
# First, we compute h with t = (x-1)(x-2)(x-3) which is an equation 
# where y = 0 at arbitrary x which we picked to be 1, 2, 3 for simplicity 
# Uw * Vw = Ww + h(x)t(x) where * is the polynomial multiplication 
# h = (Uw * Vw - Ww) / (x-1)(x-2)(x-3)

# Note: we cannot compute the above using the matrix form
# because the matrix is just a representation of the stacked polynomials. 
# We have a homomorphism from column vectors to polynomials
# where the multiplication (operation) in polynomials is different
# We need to do it in polynomial form
# => (-8x^2 + 30x - 16) * (5.5x^2 - 15.5x + 12) - (-15x^2 + 69x - 42) / (x-1)(x-2)(x-3)
# => -44x^4 + 289x^3 - 634x^2 + 539x - 150 / (x^3 - 6x^2 + 11x - 6)
# => -44x + 25

Uwp = np.poly1d(Uw)
Vwp = np.poly1d(Vw)
Wwp = np.poly1d(Ww)
tp = np.poly1d([1,-1]) * np.poly1d([1,-2]) * np.poly1d([1,-3])
(hp, r) = (Uwp * Vwp - Wwp) / tp
print(hp) # -44x + 25

# The equation is then Uwp Vwp = Wwp + hp tp
assert (Uwp * Vwp == Wwp + hp * tp, "Uw * Vw != Ww + h(x)t(x)")

# Plug in a number to try
tau = random.randint(1,1000)
A = Uwp(tau)
B = Vwp(tau)
C = Wwp(tau) + hp(tau) * tp(tau)
assert (A * B == C, "AB != C")

# Note: In reality we deal with w that's encrypted with 
# G1, G2 points, so it would have been pairing (A, B) = C
# It'd be interesting to do it here