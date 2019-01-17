import numpy as np

np.set_printoptions(precision=2)
Mat = np.arange(12)  # random matrix 2D
print(Mat)
mat2 = Mat.reshape(3,4)
print(mat2)
print(mat2.shape)
"""
[ 0  1  2  3  4  5  6  7  8  9 10 11]
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]

"""