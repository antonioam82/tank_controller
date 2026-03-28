import random
import math

'''def crear_paisaje_complejo(filename="paisaje_complejo.obj", size=110, num_clusters=15):
    vertices = []
    faces = []
    v_count = 1

    def add_cube(x, y, z, sx, sy, sz):
        nonlocal v_count
        # 8 vértices para un bloque irregular
        v_local = [
            (x-sx, y, z-sz), (x+sx, y, z-sz), (x+sx, y+sy, z-sz), (x-sx, y+sy, z-sz),
            (x-sx, y, z+sz), (x+sx, y, z+sz), (x+sx, y+sy, z+sz), (x-sx, y+sy, z+sz)
        ]
        vertices.extend(v_local)
        
        # 6 caras (2 triángulos por cara)
        f_idx = [
            (0,1,2), (0,2,3), (4,5,6), (4,6,7), # front/back
            (0,4,7), (0,7,3), (1,5,6), (1,6,2), # sides
            (3,2,6), (3,6,7)                   # top
        ]
        for f in f_idx:
            faces.append(tuple(i + v_count for i in f))
        v_count += 8

    for _ in range(num_clusters):
        # Punto central del grupo de rocas
        cx = random.uniform(-size + 15, size - 15)
        cz = random.uniform(-size + 15, size - 15)
        
        # Cada formación es un conjunto de 5 a 8 bloques solapados
        num_bloques = random.randint(5, 8)
        for _ in range(num_bloques):
            # Desplazamiento respecto al centro del cluster
            off_x = random.uniform(-4, 4)
            off_z = random.uniform(-4, 4)
            
            # Dimensiones: base ancha, altura variable (montañas bajas)
            sx = random.uniform(2, 6)
            sz = random.uniform(2, 6)
            sy = random.uniform(2, 10) # Alturas variadas hasta 10
            
            add_cube(cx + off_x, 0.1, cz + off_z, sx, sy, sz)

    # Exportar archivo
    with open(filename, "w") as f:
        f.write("# Paisaje Rocoso Complejo\n")
        for v in vertices:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        for face in faces:
            f.write(f"f {face[0]} {face[1]} {face[2]}\n")

if __name__ == "__main__":
    crear_paisaje_complejo()
    print("Modelo 'paisaje_complejo.obj' generado.")'''

def crear_roca_compleja(filename="paisaje_rocoso.obj", size=110, num_rocas=18):
    vertices = []
    faces = []
    v_offset = 1

    def generar_formacion(cx, cz, radio_base, altura_max):
        nonlocal v_offset
        # Parámetros de la roca
        segmentos_h = 8  # Detalle vertical
        segmentos_v = 12 # Detalle circular
        
        # Crear vértices con deformación aleatoria (Fractal-like)
        v_locales = []
        for i in range(segmentos_h + 1):
            h_pct = i / segmentos_h
            y = h_pct * altura_max
            
            # El radio disminuye al subir, pero con irregularidad
            radio_capa = radio_base * (1.0 - h_pct**1.5) 
            
            for j in range(segmentos_v):
                angulo = (j / segmentos_v) * 2 * math.pi
                # DEFORMACIÓN: Aquí ocurre la magia de la "roca"
                deformacion = random.uniform(0.7, 1.3) 
                # Añadimos "salientes" aleatorios
                if random.random() > 0.8: deformacion *= 1.4 
                
                x = cx + math.cos(angulo) * radio_capa * deformacion
                z = cz + math.sin(angulo) * radio_capa * deformacion
                v_locales.append((x, y + 0.05, z)) # 0.05 sobre el grid

    # Vértice superior (pico) para cerrar la roca
        v_locales.append((cx, altura_max, cz))
        vertices.extend(v_locales)

        # Crear las caras (malla de triángulos)
        for i in range(segmentos_h):
            for j in range(segmentos_v):
                v1 = v_offset + i * segmentos_v + j
                v2 = v_offset + i * segmentos_v + (j + 1) % segmentos_v
                v3 = v_offset + (i + 1) * segmentos_v + j
                v4 = v_offset + (i + 1) * segmentos_v + (j + 1) % segmentos_v
                
                if i < segmentos_h - 1:
                    faces.append((v1, v2, v3))
                    faces.append((v2, v4, v3))
                else:
                    # Cerrar punta
                    pico_idx = v_offset + len(v_locales) - 1
                    faces.append((v1, v2, pico_idx))
        
        v_offset += len(v_locales)

    # Esparcir las formaciones por el mapa de 110x110
    for _ in range(num_rocas):
        pos_x = random.uniform(-size + 20, size - 20)
        pos_z = random.uniform(-size + 20, size - 20)
        r = random.uniform(6, 15)  # Tamaño base
        h = random.uniform(4, 12)  # Altura
        generar_formacion(pos_x, pos_z, r, h)

    # Guardar archivo
    with open(filename, "w") as f:
        f.write("# Paisaje de Rocas Irregulares\n")
        for v in vertices:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        for face in faces:
            f.write(f"f {face[0]} {face[1]} {face[2]}\n")

if __name__ == "__main__":
    crear_roca_compleja()
    print("Modelo 'paisaje_rocoso.obj' creado con geometría irregular.")
