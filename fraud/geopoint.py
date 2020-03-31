import numpy as np

def create_random_point(x0, y0, distance):
    r = distance/111300
    u = np.random.uniform(0, 1)
    v = np.random.uniform(0, 1)
    w = r * np.sqrt(u)
    t = 2 * np.pi * v
    x = w * np.cos(t)
    x1 = x / np.cos(y0)
    y = w * np.sin(t)
    return (x0+x1, y0 +y)

def create_geopoint(lat, lon):
    return create_random_point(lat, lon, 50000)
