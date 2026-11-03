import math


def calc(shape, a, b=None):
    if shape == "circle":
        return math.pi * a * a
    if shape == "rect":
        return a * b
    if shape == "triangle":
        return 0.5 * a * b
    raise ValueError(f"unknown shape: {shape}")
