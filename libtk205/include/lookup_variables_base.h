#ifndef LOOKUP_VARIABLES_BASE_H_
#define LOOKUP_VARIABLES_BASE_H_

#include <memory>
#include <vector>
#include <iostream>

class performance_map_base;

// ------------------------------------------------------------------------------------------------
/// @class lookup_variables_base lookup_variables_base.h

class lookup_variables_base {

public:
    lookup_variables_base() = default;
    virtual ~lookup_variables_base() = default;
    lookup_variables_base(const lookup_variables_base& other) = default;
    lookup_variables_base& operator=(const lookup_variables_base& other) = default;

    virtual void Populate_performance_map(performance_map_base* performance_map) = 0;

    inline void Add_data_table(performance_map_base* performance_map, std::vector<double>& table)
    {
        performance_map->Add_data_table(table);
        std::cout << "Adding grid table with size " << table.size() << "\n";
    }
};

#endif