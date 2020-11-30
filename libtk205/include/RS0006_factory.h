#ifndef RS0006_FACTORY_H_
#define RS0006_FACTORY_H_

#include "RS_instance_factory.h"

namespace ASHRAE205_NS {

   class RS0006_factory : public RS_instance_factory
   {
      public:

         std::unique_ptr<RS_instance_base> Create_instance() const override;

      private:
         static bool s_registered;
   };
}

#endif