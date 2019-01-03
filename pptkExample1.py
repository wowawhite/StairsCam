import pptk
xyz = pptk.rand(100, 3)

v = pptk.viewer(xyz, xyz[:, 2])
v.set(point_size=0.005)