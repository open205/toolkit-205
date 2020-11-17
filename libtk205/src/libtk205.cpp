#include "libtk205.h"
#include "nlohmann/json.hpp"
#include <fstream>

namespace libtk205_NS {

    using json = nlohmann::json;
    using namespace ASHRAE205_NS;

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

    std::shared_ptr<RS0001_NS::RS0001> A205_SDK::Get_RS0001(const ASHRAE205& a205)
    {
        return std::dynamic_pointer_cast<RS0001_NS::RS0001>(a205.RS_instance);
    }

    std::shared_ptr<RS0002_NS::RS0002> A205_SDK::Get_RS0002(const ASHRAE205& a205)
    {
        return std::dynamic_pointer_cast<RS0002_NS::RS0002>(a205.RS_instance);
    }

    std::shared_ptr<RS0003_NS::RS0003> A205_SDK::Get_RS0003(const ASHRAE205& a205)
    {
        return std::dynamic_pointer_cast<RS0003_NS::RS0003>(a205.RS_instance);
    }

    std::shared_ptr<RS0004_NS::RS0004> A205_SDK::Get_RS0004(const ASHRAE205& a205)
    {
        return std::dynamic_pointer_cast<RS0004_NS::RS0004>(a205.RS_instance);
    }

    std::shared_ptr<RS0005_NS::RS0005> A205_SDK::Get_RS0005(const ASHRAE205& a205)
    {
        return std::dynamic_pointer_cast<RS0005_NS::RS0005>(a205.RS_instance);
    }

    std::shared_ptr<RS0006_NS::RS0006> A205_SDK::Get_RS0006(const ASHRAE205& a205)
    {
        return std::dynamic_pointer_cast<RS0006_NS::RS0006>(a205.RS_instance);
    }

    void A205_SDK::Read_binary_file(const char* filename, std::vector<uint8_t> &bytes)
    {
        std::ifstream is (filename, std::ifstream::binary);
        if (is) 
        {
            // get length of file:
            is.seekg(0, is.end);
            int length = is.tellg();
            is.seekg(0, is.beg);

            bytes.resize(length);
            // read data as a block:
            is.read(reinterpret_cast<char *>(bytes.data()), length);

            is.close();
        }
    }
}