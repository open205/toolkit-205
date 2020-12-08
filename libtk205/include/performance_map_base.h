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

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	j
  // ----------------------------------------------------------------------------------------------
    virtual void Initialize(const nlohmann::json& j) = 0;

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	axis TBD
  // ----------------------------------------------------------------------------------------------
    inline void Add_grid_axis(std::vector<double>& axis) {
        _grid_axes.emplace_back(Btwxt::GridAxis(axis));
    }

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	axis TBD
  // ----------------------------------------------------------------------------------------------
    inline void Add_grid_axis(std::vector<int>& axis) {
        _grid_axes.emplace_back(Btwxt::GridAxis(std::vector<double>(axis.begin(), axis.end())));
    }

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	table TBD
  // ----------------------------------------------------------------------------------------------
    inline void Add_data_table(std::vector<double>& table) {
        _btwxt.add_value_table(table);
    }
    
  // ----------------------------------------------------------------------------------------------
  /// @brief	
  // ----------------------------------------------------------------------------------------------
    inline void Finalize_grid() {
        auto gd = Btwxt::GriddedData(_grid_axes);
        _btwxt = Btwxt::RegularGridInterpolator(gd);
    }

  // ----------------------------------------------------------------------------------------------
  /// @brief	
  /// @param	table_index TBD
  // ----------------------------------------------------------------------------------------------
    inline double Calculate_performance(std::size_t table_index) {
        return _btwxt.get_value_at_target(table_index);
    }

  // ----------------------------------------------------------------------------------------------
  /// @brief	Using pre-populated grid axes and lookup tables, calculate a set of performance
  ///         results.
  /// @param	target 
  // ----------------------------------------------------------------------------------------------
    inline std::vector<double> Calculate_performance(const std::vector<double> &target) {
        return _btwxt.get_values_at_target(target);
    }

private:
    Btwxt::RegularGridInterpolator _btwxt;
    std::vector<Btwxt::GridAxis>   _grid_axes;

};

#endif