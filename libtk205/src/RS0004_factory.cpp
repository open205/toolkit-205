#include "RS0004_factory.h"
#include "RS0004.h"
#include <memory>

using namespace ASHRAE205_NS;

bool RS0004_factory::s_registered = RS_instance_factory::Register_factory("RS0004", std::make_shared<RS0004_factory>());

std::unique_ptr<RS_instance_base> RS0004_factory::Create_instance() const
{
    return std::make_unique<ASHRAE205_NS::RS0004_NS::RS0004>();
}
