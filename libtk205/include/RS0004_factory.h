#include "RS_instance_factory.h"

class RS0004_factory : public RS_instance_factory
{
   public:

      std::unique_ptr<RS_instance_base> Create() const override;

   private:
      static bool s_registered;
};
