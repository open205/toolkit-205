#include "RS_instance_factory.h"
#include <map>

namespace
{
    using RS_factory_map = std::map<std::string, std::shared_ptr<RS_instance_factory> >;

    RS_factory_map& Get_RS_factory_map()
    {
    static RS_factory_map factory_map;
    return factory_map;
    }
}

//static
bool RS_instance_factory::Register_factory(std::string const& RS_ID,
                                           std::shared_ptr<RS_instance_factory> factory)
{
   Get_RS_factory_map()[RS_ID] = factory;
   return true;
}

//static
std::unique_ptr<RS_instance_base> RS_instance_factory::Create(std::string const& RS_ID)
{
   const auto factory = Get_RS_factory_map()[RS_ID];
   return (factory == nullptr) ? nullptr : factory->Create_instance();
}