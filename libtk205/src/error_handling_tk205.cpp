#include "error_handling_tk205.h"
#include <map>
#include <iostream>
#include <string_view>

namespace tk205 {

    msg_handler _error_handler;

    void Set_error_handler(msg_handler handler)
    {
        _error_handler = std::move(handler);
    }

    void Show_message(msg_severity severity, const std::string &message)
    {
        static std::map<msg_severity, std::string_view> severity_str {
            {msg_severity::DEBUG_205, "DEBUG"},
            {msg_severity::INFO_205, "INFO"},
            {msg_severity::WARN_205, "WARN"},
            {msg_severity::ERR_205, "ERR"}
        };
        if (!_error_handler)
        {
            //std::cout << severity_str[severity] << ": " << message << std::endl;
        }
        else
        {
            _error_handler(severity, message, nullptr);
        }
    }
}

