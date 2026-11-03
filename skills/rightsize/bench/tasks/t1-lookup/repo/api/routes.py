from payments.client import charge


def checkout(request, gateway):
    order = request.order
    receipt = charge(gateway, order)
    return {"status": "paid", "receipt": receipt}
