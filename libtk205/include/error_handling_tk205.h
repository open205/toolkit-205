#ifndef ERROR_HANDLING_TK205_H_
#define ERROR_HANDLING_TK205_H_

#include <functional>
#include <string>
#include <nlohmann/json.hpp>

namespace ASHRAE205_NS {
   enum class msg_severity : unsigned int {
       DEBUG, 
       INFO, 
       WARN, 
       ERR
   };

    using msg_handler = std::function<void(msg_severity, const std::string &, void *)>;

    void Set_error_handler(msg_handler handler);
    void Show_message(msg_severity severity, const std::string& message);

	inline void A205_json_catch(nlohmann::json::out_of_range & ex)
	{
    	Show_message(msg_severity::WARN, ex.what());
	}

}


#endif