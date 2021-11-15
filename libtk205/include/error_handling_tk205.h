#ifndef ERROR_HANDLING_TK205_H_
#define ERROR_HANDLING_TK205_H_

#include <functional>
#include <string>
#include <nlohmann/json.hpp>
#include <iostream>

namespace tk205 {

    enum class msg_severity : unsigned int {
        DEBUG_205, 
        INFO_205, 
        WARN_205, 
        ERR_205
    };

    using msg_handler = std::function<void(msg_severity, const std::string &, void *)>;

    void Set_error_handler(msg_handler handler);
    void Show_message(msg_severity severity, const std::string& message);
}


#endif