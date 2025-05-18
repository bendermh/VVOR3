import matplotlib.pyplot as plt
import numpy as np

# Crear figura y ejes sin bordes
fig, ax = plt.subplots(figsize=(2, 2), dpi=256)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Cabeza (círculo azul oscuro)
circle_head = plt.Circle((0.5, 0.5), 0.36, color='#183A5A', lw=2, fill=True)
ax.add_patch(circle_head)

# Ojo (círculo naranja)
circle_eye = plt.Circle((0.7, 0.5), 0.13, color='#FF8600', lw=2, fill=True)
ax.add_patch(circle_eye)

# Onda (seno) en blanco
t = np.linspace(0.18, 0.82, 120)
y = 0.5 + 0.12 * np.sin(8 * np.pi * (t - 0.18))
ax.plot(t, y, color="white", lw=3, solid_capstyle='round')

plt.savefig("vvor_icon.png", dpi=256, bbox_inches='tight', pad_inches=0, transparent=True)
plt.close()
