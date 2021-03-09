#include "libtk205.h"
#include "nlohmann/json.hpp"
#include <fstream>

#include "RS0001_factory.h"
#include "RS0002_factory.h"
#include "RS0003_factory.h"
#include "RS0004_factory.h"
#include "RS0005_factory.h"
#include "RS0006_factory.h"

#include <type_traits>

namespace libtk205_NS {

    using json = nlohmann::json;
    using namespace ASHRAE205_NS;

    A205_SDK::A205_SDK()
    {
        rs_instance_factory::Register_factory("RS0001", std::make_unique<RS0001_factory>());  
        rs_instance_factory::Register_factory("RS0002", std::make_unique<RS0002_factory>());  
        rs_instance_factory::Register_factory("RS0003", std::make_unique<RS0003_factory>());  
        rs_instance_factory::Register_factory("RS0004", std::make_unique<RS0004_factory>());  
        rs_instance_factory::Register_factory("RS0005", std::make_unique<RS0005_factory>());  
        rs_instance_factory::Register_factory("RS0006", std::make_unique<RS0006_factory>());  
    }

    ASHRAE205 A205_SDK::Load_A205(const char* input_file)
    {
        std::string filename(input_file);
        std::string::size_type idx = filename.rfind('.');
        ASHRAE205 a205;

        if(idx != std::string::npos)
        {
            std::string extension = filename.substr(idx+1);
            json j;

            if (extension == "cbor")
            {
                std::vector<uint8_t> bytearray;
                Read_binary_file(input_file, bytearray);
                j = json::from_cbor(bytearray);
            }
            else if (extension == "json")
            {
                std::string schema(input_file);
                std::ifstream in(schema);
                in >> j;
            }

            a205.Initialize(j);
        }
        return a205;
    }

    RS0001_NS::RS0001* A205_SDK::Get_RS0001(const ASHRAE205& a205)
    {
      return dynamic_cast<RS0001_NS::RS0001 *>(a205.rs_instance.get());
    }

    RS0002_NS::RS0002* A205_SDK::Get_RS0002(const ASHRAE205& a205)
    {
        return dynamic_cast<RS0002_NS::RS0002 *>(a205.rs_instance.get());
    }

    RS0003_NS::RS0003* A205_SDK::Get_RS0003(const ASHRAE205& a205)
    {
        return dynamic_cast<RS0003_NS::RS0003 *>(a205.rs_instance.get());
    }

    RS0004_NS::RS0004* A205_SDK::Get_RS0004(const ASHRAE205& a205)
    {
        return dynamic_cast<RS0004_NS::RS0004 *>(a205.rs_instance.get());
    }

    RS0005_NS::RS0005* A205_SDK::Get_RS0005(const ASHRAE205& a205)
    {
        return dynamic_cast<RS0005_NS::RS0005 *>(a205.rs_instance.get());
    }

    RS0006_NS::RS0006* A205_SDK::Get_RS0006(const ASHRAE205& a205)
    {
        return dynamic_cast<RS0006_NS::RS0006 *>(a205.rs_instance.get());
    }

    void A205_SDK::Read_binary_file(const char* filename, std::vector<uint8_t> &bytes)
    {
        std::ifstream is (filename, std::ifstream::binary);
        if (is) 
        {
            // get length of file:
            is.seekg(0, is.end);
            size_t length = static_cast<size_t>(is.tellg());
            is.seekg(0, is.beg);

            bytes.resize(length);
            // read data as a block:
            is.read(reinterpret_cast<char *>(bytes.data()), length);

            is.close();
        }
    }
}