def controller_node(state):
    """
    Thin controller:
    - Does NOT retry
    - Does NOT route sequentially
    - Only validates / logs (optional)
    """
    return {}


def controller_router(state):
    """
    Controller is no longer used for sequencing.
    Keep only safety checks if needed.
    """

    # Optional: if symbol resolution failed → stop early
    if not state.get("stock_symbol"):
        return "__end__"

    # Otherwise, do nothing (flow handled by graph)
    return "__end__"