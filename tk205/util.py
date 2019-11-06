import itertools

def create_grid_set(grid_variables, order):
    lists = []
    if len(grid_variables) != len(order):
        raise Exception(f"order: {order} must contain the keys of 'grid_variables'")
    for var in order:
        if var not in grid_variables:
            raise Exception(f"{var} not found in {order}")
        lists.append(grid_variables[var])

    grid = list(zip(*itertools.product(*lists)))
    grid_set = {}
    for i, var in enumerate(order):
        grid_set[var] = grid[i]

    return grid_set

