from geometry import calc

PRICE_PER_M2 = 12.5


def floor_price(width, length):
    return round(calc("rect", width, length) * PRICE_PER_M2, 2)
