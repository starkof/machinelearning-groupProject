import numpy as np

a = np.random.randn(9, 6) + 1j*np.random.randn(9, 6)
b = np.random.randn(2, 7, 8, 3) + 1j*np.random.randn(2, 7, 8, 3)

print('a')
print(a.shape)
print(a)
print()

print('b')
print(a.shape)
print(a)
print()


u, s, vh = np.linalg.svd(a, full_matrices=False)

print('u;')
print(u.shape)
print(u)
print()
print()

print('s;')
print(s)
print(s.shape)
print()
print()

print('vh;')
print(vh.shape)
print(vh)
