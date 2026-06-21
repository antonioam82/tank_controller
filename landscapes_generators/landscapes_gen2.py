import random

def crear_paisaje_obj(filename="paisaje.obj", size=110, num_formaciones=40):
    vertices = []
    faces = []
    v_count = 1

    for _ in range(num_formaciones):
        # Posición aleatoria dentro del grid
        x_base = random.uniform(-size, size)
        z_base = random.uniform(-size, size)
        
        # Dimensiones de la formación (montañas bajas y rocas)
        width = random.uniform(5, 15)
        height = random.uniform(3, 8) # Altura baja
        depth = random.uniform(5, 15)
        
        # Crear un "pirámide" irregular para cada formación
        # Vértice superior (pico)
        vertices.append((x_base, height, z_base))
        pico_idx = v_count
        v_count += 1
        
        # Vértices de la base (4 puntos)
        base_pts = [
            (x_base - width/2, 0.1, z_base - depth/2),
            (x_base + width/2, 0.1, z_base - depth/2),
            (x_base + width/2, 0.1, z_base + depth/2),
            (x_base - width/2, 0.1, z_base + depth/2)
        ]
        
        base_indices = []
        for pt in base_pts:
            vertices.append(pt)
            base_indices.append(v_count)
            v_count += 1
        
        # Crear caras laterales
        for i in range(4):
            v1 = base_indices[i]
            v2 = base_indices[(i + 1) % 4]
            faces.append((pico_idx, v1, v2))

    # Guardar en formato OBJ
    with open(filename, "w") as f:
        f.write("# Paisaje para Grid OpenGL\n")
        for v in vertices:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        for face in faces:
            f.write(f"f {face[0]} {face[1]} {face[2]}\n")

if __name__ == "__main__":
    crear_paisaje_obj()
    print("Archivo 'paisaje.obj' generado con éxito.")
