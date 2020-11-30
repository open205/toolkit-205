#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include "libtk205.h"

#include "RS_instance_factory.h"
#include "RS0003_factory.h"

using json = nlohmann::json;

int main(int argc, char* argv[])
{
    using namespace ASHRAE205_NS;

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