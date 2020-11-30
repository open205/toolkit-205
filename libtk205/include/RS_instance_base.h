#ifndef RS_INSTANCE_BASE_H_
#define RS_INSTANCE_BASE_H_

#include <nlohmann/json.hpp>
#include <iostream>

/// @class RS_instance_base RS_instance_base.h
/// @brief This class isolates derived RS classes from their owner (ASHRAE205). It handles
///        no resources.

namespace ASHRAE205_NS {

	inline void A205_json_catch(nlohmann::json::out_of_range & ex)
	{
    	std::cout << ex.what() << std::endl;
	}
}

class RS_instance_base
{
public:

    RS_instance_base() = default;
    virtual ~RS_instance_base() = default;
    RS_instance_base(const RS_instance_base& other) = default;
    RS_instance_base& operator=(const RS_instance_base& other) = default;
    RS_instance_base(RS_instance_base&&) = default;
    RS_instance_base& operator=(RS_instance_base&&) = default;

    virtual void Initialize(const nlohmann::json& j) = 0;
};

#endif