#ifndef ERROR_HANDLING_TK205_H_
#define ERROR_HANDLING_TK205_H_

#include <functional>

namespace ASHRAE205_NS {
    enum class msg_severity { DEBUG, INFO, WARN, ERR };

    using msg_handler = std::function<void(msg_severity, const std::string &, void *)>;

    void Set_error_handler(msg_handler handler);
    void Show_message(msg_severity severity, const std::string& message);
}


#endif