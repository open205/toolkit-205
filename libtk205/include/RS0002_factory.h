#ifndef RS0002_FACTORY_H_
#define RS0002_FACTORY_H_

#include "RS_instance_factory.h"

class RS0002_factory : public RS_instance_factory
{
   public:

      std::unique_ptr<RS_instance_base> Create_instance() const override;

   private:
      static bool s_registered;
};

#endif