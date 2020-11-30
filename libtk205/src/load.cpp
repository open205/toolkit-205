#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include "libtk205.h"

#include "RS_instance_factory.h"
#include "RS0003_factory.h"

using json = nlohmann::json;

void iterj(json& j, std::vector<std::string>& lineage, std::string &out) 
{
    for (json::iterator it = j.begin(); it != j.end(); ++it) 
    {
        auto item_lineage = lineage;
        std::ostringstream oss;
        item_lineage.push_back(it.key());
        if (!it->is_object())
        {
            for (const auto &i : item_lineage)
            {
                oss << i << ", ";
            }
            oss << " : " << it.value() << "\n";
            out += oss.str();
        }
        else
        {
            iterj(*it, item_lineage, out);
        }
    }
}

void Read_binary_file(const char* filename, std::vector<uint8_t> &bytes)
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

#if 0
void Load_A205(const json& j)
{
    ASHRAE205_NS::ASHRAE205 a205;
    a205.Initialize(j);

    std::cout << a205.disclaimer << "\n";
    auto rs01 = std::dynamic_pointer_cast<ASHRAE205_NS::RS0001_NS::RS0001>(a205.RS_instance);
    if (rs01)
    {
        for (const auto& element : rs01->performance.performance_map_cooling.grid_variables.condenser_liquid_entering_temperature)
        {
            std::cout << element << "\n";
        }
    }
    auto rs03 = std::dynamic_pointer_cast<ASHRAE205_NS::RS0003_NS::RS0003>(a205.RS_instance);
    if (rs03)
    {
        //std::cout << rs03->description.assembly_components.at(1).component_description << "\n";
        std::cout << rs03->description.product_information.number_of_impellers << "\n";
        auto gridvars1 = std::dynamic_pointer_cast<ASHRAE205_NS::RS0003_NS::PerformanceMapContinuous>(rs03->performance.performance_map)->grid_variables.volumetric_air_flow_rate;
        for (const auto& element : gridvars1)
        {
            std::cout << element << "\n";
        }
    }
    auto rs05 = std::dynamic_pointer_cast<ASHRAE205_NS::RS0005_NS::RS0005>(a205.RS_instance);
    if (rs05)
    {
        auto rs06 = std::dynamic_pointer_cast<ASHRAE205_NS::RS0006_NS::RS0006>(rs05->performance.drive_representation.RS_instance);
        if (rs06)
        {
            std::cout << rs06->description.product_information.model_number << "\n";
        }
    }
    auto rs06 = std::dynamic_pointer_cast<ASHRAE205_NS::RS0006_NS::RS0006>(a205.RS_instance);
    if (rs06)
    {
        std::cout << rs06->description.product_information.model_number << "\n";
    }
}
#endif

int main(int argc, char* argv[])
{
    RS_instance_factory::Register_factory("RS0003", std::make_shared<RS0003_factory>());  

    if (argc > 1)
    {
#if 0
        using json = nlohmann::json;
        std::string schema(argv[1]);
        std::ifstream in(schema);
        json j;
        in >> j;
        Load_A205(j);
#else
        using namespace libtk205_NS;
        A205_SDK sdk;
        auto a205 = sdk.Load_A205(argv[1]);
        auto rs01 = sdk.Get_RS0001(a205);
        if (rs01)
        {
            for (const auto& element : rs01->performance.performance_map_cooling.grid_variables.condenser_liquid_entering_temperature)
            {
                std::cout << element << "\n";
            }
        }
        auto rs03 = std::dynamic_pointer_cast<ASHRAE205_NS::RS0003_NS::RS0003>(a205.RS_instance);
        if (rs03)
        {
        //     //std::cout << rs03->description.assembly_components.at(1).component_description << "\n";
            std::cout << "number_of_impellers " << rs03->description.product_information.number_of_impellers << "\n";
            auto gridvars1 = std::dynamic_pointer_cast<ASHRAE205_NS::RS0003_NS::PerformanceMapContinuous>(rs03->performance.performance_map)->grid_variables.volumetric_air_flow_rate;
            for (const auto& element : gridvars1)
            {
                std::cout << element << "\n";
            }
        }
        auto rs05 = sdk.Get_RS0005(a205);
        if (rs05)
        {
            auto rs06 = sdk.Get_RS0006(rs05->performance.drive_representation);
            if (rs06)
            {
                std::cout << rs06->description.product_information.model_number << "\n";
            }
        }
#endif
    }
}