#include "rs_instance_factory.h"
#include <map>

namespace
{
    using rs_factory_map = std::map<std::string, std::unique_ptr<ASHRAE205_NS::rs_instance_factory> >;

    rs_factory_map& Get_rs_factory_map()
    {
    static rs_factory_map factory_map;
    return factory_map;
    }
}

namespace ASHRAE205_NS  {
   //static
   bool rs_instance_factory::Register_factory(std::string const& RS_ID,
                                              std::unique_ptr<rs_instance_factory> factory)
   {
      Get_rs_factory_map()[RS_ID] = std::move(factory);
      return true;
   }

   //static
   std::unique_ptr<rs_instance_base> rs_instance_factory::Create(std::string const& RS_ID)
   {
      const auto &factory = Get_rs_factory_map()[RS_ID];
      std::unique_ptr<rs_instance_base> inst = (factory == nullptr) ? nullptr : factory->Create_instance();
      // Return smart pointers by value to take advantage of RVO or move semantics:
      return inst;
   }
}