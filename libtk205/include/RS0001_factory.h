#ifndef RS0001_FACTORY_H_
#define RS0001_FACTORY_H_

#include "RS_instance_factory.h"

namespace ASHRAE205_NS {

   class RS0001_factory : public RS_instance_factory
   {
      public:

         std::unique_ptr<RS_instance_base> Create_instance() const override;

      private:
         // Implementation of self-registering class
         // a la https://www.bfilipek.com/2018/02/factory-selfregister.html
         static bool s_registered;
   };
}

#endif