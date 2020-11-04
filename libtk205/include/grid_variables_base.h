#ifndef GRID_VARIABLES_BASE_H_
#define GRID_VARIABLES_BASE_H_

#include <memory>
#include <vector>
#include <iostream>

class performance_map_base;

// ------------------------------------------------------------------------------------------------
/// @class grid_variables_base grid_variables_base.h

class grid_variables_base {

public:
    grid_variables_base() = default;
    virtual ~grid_variables_base() = default;
    grid_variables_base(const grid_variables_base& other) = default;
    grid_variables_base& operator=(const grid_variables_base& other) = default;

    virtual void Populate_performance_map(const performance_map_base* performance_map) = 0;

    inline void Add_grid_axis(const performance_map_base* performance_map, std::vector<double>& axis)
    {
        std::cout << "Adding grid axis with size " << axis.size() << "\n";
    }
    inline void Add_grid_axis(const performance_map_base* performance_map, std::vector<int>& axis)
    {
        std::cout << "Adding (int) grid axis with size " << axis.size() << "\n";
    }
};

#endif