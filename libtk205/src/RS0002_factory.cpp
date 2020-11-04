#include "RS0002_factory.h"
#include "RS0002.h"
#include <memory>
//#include <iostream>

bool RS0002_factory::s_registered = RS_instance_factory::Register_factory("RS0002", std::make_shared<RS0002_factory>());

std::unique_ptr<RS_instance_base> RS0002_factory::Create() const
{
    return std::make_unique<ASHRAE205_NS::RS0002_NS::RS0002>();
}
