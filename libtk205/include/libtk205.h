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
#include "RS0007.h"
#include "nlohmann/json.hpp"

namespace libtk205_NS {

    class A205_SDK 
    {
    public:
        A205_SDK();
        
        static bool Validate_A205(const char* schema, const char* input_file);
#if 0
        ASHRAE205_NS::ASHRAE205 Load_A205(const char* input_file);
        ASHRAE205_NS::RS0001_NS::RS0001* Get_RS0001(const ASHRAE205_NS::ASHRAE205& a205);
        ASHRAE205_NS::RS0002_NS::RS0002* Get_RS0002(const ASHRAE205_NS::ASHRAE205& a205);
        ASHRAE205_NS::RS0003_NS::RS0003* Get_RS0003(const ASHRAE205_NS::ASHRAE205& a205);
        ASHRAE205_NS::RS0004_NS::RS0004* Get_RS0004(const ASHRAE205_NS::ASHRAE205& a205);
        ASHRAE205_NS::RS0005_NS::RS0005* Get_RS0005(const ASHRAE205_NS::ASHRAE205& a205);
        ASHRAE205_NS::RS0006_NS::RS0006* Get_RS0006(const ASHRAE205_NS::ASHRAE205& a205);
#endif
        nlohmann::json Load_json(const char* input_file);

        ASHRAE205_NS::RS0001_NS::RS0001 Load_RS0001(const char* input_file);
        ASHRAE205_NS::RS0002_NS::RS0002 Load_RS0002(const char* input_file);
        ASHRAE205_NS::RS0003_NS::RS0003 Load_RS0003(const char* input_file);
        ASHRAE205_NS::RS0004_NS::RS0004 Load_RS0004(const char* input_file);
        ASHRAE205_NS::RS0005_NS::RS0005 Load_RS0005(const char* input_file);
        ASHRAE205_NS::RS0006_NS::RS0006 Load_RS0006(const char* input_file);
        ASHRAE205_NS::RS0007_NS::RS0007 Load_RS0007(const char* input_file);

    private:
        void Read_binary_file(const char* filename, std::vector<uint8_t> &bytes);
    };
}

#endif