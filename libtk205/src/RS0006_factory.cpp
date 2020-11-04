#include "RS0006_factory.h"
#include "RS0006.h"
#include <memory>
//#include <iostream>

bool RS0006_factory::s_registered = RS_instance_factory::Register_factory("RS0006", std::make_shared<RS0006_factory>());

std::unique_ptr<RS_instance_base> RS0006_factory::Create() const
{
    return std::make_unique<ASHRAE205_NS::RS0006_NS::RS0006>();
}
