# Homework 6: QAP

## Problem 1: Encrypted R1CS

Given an R1CS of the form

$$
L\mathbf{\vec{[s]_1}}\odot R\mathbf{\vec{[s]_2}} = O\mathbf{\vec{[s]}_{12}}
$$

Where L, R, and O are n x m matrices of field elements and **s** is a vector of G1, G2, or G12 points

Write solidity code that verifies the formula.

You can check the equality of G12 points in Python this way:

```python
a = pairing(multiply(G2, 5), multiply(G1, 8))
b = pairing(multiply(G2, 10), multiply(G1, 4))
eq(a, b)
```

**********************Hint:********************** Each row of the matrices is a separate pairing.

**********Hint:********** When you get **s** encrypted with both G1 and G2 generators, you don’t know whether or not they have the same discrete logarithm. However, it is straightforward to check using another equation.

The solution can be found under
`tests/` and
`contracts/`

## Problem 2

Why does an R1CS require exactly one multiplication per row?

How does this relate to bilinear pairings?

The solution can be found in q2.md

## Problem 3: QAP by hand

Convert the following R1CS into a QAP **************************************************************************over real numbers, not a finite field**************************************************************************

```python
import numpy as np
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

# pick random values for x and y
x = random.randint(1,1000)
y = random.randint(1,1000)

# this is our orignal formula
out = 3 * x * x * y + 5 * x * y - x- 2*y + 3# the witness vector with the intermediate variables inside
v1 = 3*x*x
v2 = v1 * y
w = np.array([1, out, x, y, v1, v2])

result = C.dot(w) == np.multiply(A.dot(w),B.dot(w))
assert result.all(), "result contains an inequality"
```

You can use a computer (Python, sage, etc) to check your work at each step and do the Lagrange interpolate, but you must show each step.

Check your work by seeing that the polynomial on both sides of the equation is the same.

Refer to the code here: https://www.rareskills.io/post/r1cs-to-qap

The solution can be found in `q3.py`


# Virtualenv
If you have a project in a directory called my-project you can set up virtualenv for that project by running:

```
cd my-project/
virtualenv venv
```

If you want your virtualenv to also inherit globally installed packages run:

```
virtualenv venv --system-site-packages
```

These commands create a venv/ directory in your project where all dependencies are installed. You need to activate it first though (in every terminal instance where you are working on your project):

```
source venv/bin/activate
```

You should see a (venv) appear at the beginning of your terminal prompt indicating that you are working inside the virtualenv. Now when you install something like this:

```
pip install <package>
```
It will get installed in the venv/ folder, and not conflict with other projects.

To leave the virtual environment run:

```
deactivate
```

Important: Remember to add venv to your project's .gitignore file so you don't include all of that in your source code.

It is preferable to install big packages (like Numpy), or packages you always use (like IPython) globally. All the rest can be installed in a virtualenv.
