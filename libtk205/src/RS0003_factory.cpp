#include "RS0003_factory.h"
#include "RS0003.h"
#include <memory>
//#include <iostream>

bool RS0003_factory::s_registered = RS_instance_factory::Register_factory("RS0003", std::make_shared<RS0003_factory>());

std::unique_ptr<RS_instance_base> RS0003_factory::Create() const
{
    return std::make_unique<ASHRAE205_NS::RS0003_NS::RS0003>();
}
