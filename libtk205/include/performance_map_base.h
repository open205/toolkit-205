#ifndef PERFORMANCE_MAP_BASE_H_
#define PERFORMANCE_MAP_BASE_H_

#include <memory>
#include <vector>
#include <iostream>
#include <nlohmann/json.hpp>
#include <btwxt.h>

// ------------------------------------------------------------------------------------------------
/// @class performance_map_base performance_map_base.h

class performance_map_base {

public:
    performance_map_base() = default;
    virtual ~performance_map_base() = default;
    performance_map_base(const performance_map_base& other) = default;
    performance_map_base& operator=(const performance_map_base& other) = default;

    virtual void Initialize(const nlohmann::json& j) = 0;

    inline void Add_grid_axis(std::vector<double>& axis) {
        _grid_axes.emplace_back(Btwxt::GridAxis(axis));
    }

    inline void Add_grid_axis(std::vector<int>& axis) {
        _grid_axes.emplace_back(Btwxt::GridAxis(std::vector<double>(axis.begin(), axis.end())));
    }

    inline void Add_data_table(std::vector<double>& table) {
        _btwxt.add_value_table(table);
    }
    
    inline void Finalize_grid() {
        auto gd = Btwxt::GriddedData(_grid_axes);
        _btwxt = Btwxt::RegularGridInterpolator(gd);
    }

    inline void Calculate_performance(std::vector<double>& target);

private:
    Btwxt::RegularGridInterpolator _btwxt;
    std::vector<Btwxt::GridAxis>   _grid_axes;

};

#endif