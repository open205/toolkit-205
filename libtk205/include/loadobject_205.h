#ifndef LOADOBJECT_205_H_
#define LOADOBJECT_205_H_

#include <nlohmann/json.hpp>
#include <error_handling_tk205.h>

namespace tk205 {

    template<class T>
    void A205_json_get(nlohmann::json j, const char *subnode, T& a205_object, bool& object_is_set, bool required = false)
    {
		try 
        {
            a205_object = j.at(subnode).get<T>();
            object_is_set = true;
        }
		catch (nlohmann::json::out_of_range & ex)
        {
            object_is_set = false;
            if (required)
            {
                Show_message(msg_severity::WARN_205, ex.what());
            }
        }
    }
}


#endif