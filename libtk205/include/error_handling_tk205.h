#ifndef ERROR_HANDLING_TK205_H_
#define ERROR_HANDLING_TK205_H_

#include <functional>
#include <string>
#include <nlohmann/json.hpp>
#include <iostream>

namespace ASHRAE205_NS {

    struct enum_info
    { 
        std::string_view enumerant_name; 
        std::string_view display_text; 
        std::string_view description;
    };

    enum class msg_severity : unsigned int {
        DEBUG_205, 
        INFO_205, 
        WARN_205, 
        ERR_205
    };

    using msg_handler = std::function<void(msg_severity, const std::string &, void *)>;

    void Set_error_handler(msg_handler handler);
    void Show_message(msg_severity severity, const std::string& message);

    template<class T>
    void A205_json_get(nlohmann::json j, const char *subnode, T& a205_object, bool required = false)
    {
		try 
        {
            a205_object = j.at(subnode).get<T>();
        }
		catch (nlohmann::json::out_of_range & ex)
        {
            if (required)
            {
                Show_message(msg_severity::WARN_205, ex.what());
            }
        }
    }

	inline void A205_json_catch(nlohmann::json::out_of_range & ex)
	{
    	Show_message(msg_severity::WARN_205, ex.what());
	}

}


#endif