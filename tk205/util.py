import itertools

def create_grid_set(grid_variables, order):
    lists = []
    if len(grid_variables) != len(order):
        raise Exception(f"order: {order} must contain the keys of 'grid_variables'")

    for var in order:
        if var not in grid_variables:
            raise Exception(f"{var} not found in {order}")

        if len(grid_variables[var]) == 0:
            #TODO: Probably should be an exception
            return None
        lists.append(grid_variables[var])

    grid = list(zip(*itertools.product(*lists)))
    grid_set = {}
    for i, var in enumerate(order):
        grid_set[var] = grid[i]

    return grid_set

def process_grid_set(grid_set):
    grid_vars = {}
    for var in grid_set:
        grid_vars[var] = list(set(grid_set[var]))
        grid_vars[var].sort()
    return grid_vars

def unique_name_with_index(name, list_of_names):
    if name not in list_of_names:
        return name
    else:
        i = 0
        searching = True
        while searching:
            if f"{name}{i}" not in list_of_names:
                searching = False
                return f"{name}{i}"



