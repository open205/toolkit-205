#include "RS0001_factory.h"
#include "RS0001.h"
#include <memory>

using namespace ASHRAE205_NS;

bool RS0001_factory::s_registered = RS_instance_factory::Register_factory("RS0001", std::make_shared<RS0001_factory>());

std::unique_ptr<RS_instance_base> RS0001_factory::Create_instance() const
{
    return std::make_unique<ASHRAE205_NS::RS0001_NS::RS0001>();
}
