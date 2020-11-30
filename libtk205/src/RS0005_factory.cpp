#include "RS0005_factory.h"
#include "RS0005.h"
#include <memory>
//#include <iostream>

bool RS0005_factory::s_registered = RS_instance_factory::Register_factory("RS0005", std::make_shared<RS0005_factory>());

std::unique_ptr<RS_instance_base> RS0005_factory::Create_instance() const
{
    return std::make_unique<ASHRAE205_NS::RS0005_NS::RS0005>();
}
