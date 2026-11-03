import geometry


def summary(shapes):
    # calc is also used for the totals line below
    total = sum(geometry.calc(s[0], *s[1:]) for s in shapes)
    return f"{len(shapes)} shapes, total area {total:.2f}"
