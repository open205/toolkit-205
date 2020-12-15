#ifndef LIBTK205_H_
#define LIBTK205_H_

#include <vector>
#include <memory>
#include "ASHRAE205.h"
#include "RS0001.h"
#include "RS0002.h"
#include "RS0003.h"
#include "RS0004.h"
#include "RS0005.h"
#include "RS0006.h"

namespace libtk205_NS {

    enum class msg_severity { DEBUG, INFO, WARN, ERR };
    void Set_error_handler(std::function<void(msg_severity, const std::string, void *)> handler);

    class A205_SDK 
    {
    public:
        A205_SDK();
        
        ASHRAE205_NS::ASHRAE205 Load_A205(const char* input_file);
        const ASHRAE205_NS::RS0001_NS::RS0001* Get_RS0001(const ASHRAE205_NS::ASHRAE205& a205);
        const ASHRAE205_NS::RS0002_NS::RS0002* Get_RS0002(const ASHRAE205_NS::ASHRAE205& a205);
        const ASHRAE205_NS::RS0003_NS::RS0003* Get_RS0003(const ASHRAE205_NS::ASHRAE205& a205);
        const ASHRAE205_NS::RS0004_NS::RS0004* Get_RS0004(const ASHRAE205_NS::ASHRAE205& a205);
        const ASHRAE205_NS::RS0005_NS::RS0005* Get_RS0005(const ASHRAE205_NS::ASHRAE205& a205);
        const ASHRAE205_NS::RS0006_NS::RS0006* Get_RS0006(const ASHRAE205_NS::ASHRAE205& a205);

    private:
        void Read_binary_file(const char* filename, std::vector<uint8_t> &bytes);

        std::vector<ASHRAE205_NS::ASHRAE205> _a205_instances;
    };
}

#endif