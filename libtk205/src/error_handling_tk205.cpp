#include "error_handling_tk205.h"
#include <map>
#include <iostream>

namespace ASHRAE205_NS {

    msg_handler _error_handler;

    void Set_error_handler(msg_handler handler)
    {
        _error_handler = std::move(handler);
    }

    void Show_message(msg_severity severity, const std::string &message)
    {
        static std::map<msg_severity, std::string> severity_str {
            {msg_severity::DEBUG, "DEBUG"},
            {msg_severity::INFO, "INFO"},
            {msg_severity::WARN, "WARN"},
            {msg_severity::ERR, "ERR"}
        };
        if (!_error_handler)
        {
            std::cout << severity_str[severity] << ": " << message << std::endl;
        }
        else
        {
            _error_handler(severity, message, nullptr);
        }
    }
}

