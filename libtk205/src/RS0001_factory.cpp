#include "RS0001_factory.h"
#include "RS0001.h"
#include <memory>

// A little trickery here: https://www.learncpp.com/cpp-tutorial/811-static-member-variables/
// "static members exist even if no objects of the class have been instantiated"

bool RS0001_factory::s_registered = RS_instance_factory::Register_factory("RS0001", std::make_shared<RS0001_factory>());

std::unique_ptr<RS_instance_base> RS0001_factory::Create() const
{
    return std::make_unique<ASHRAE205_NS::RS0001_NS::RS0001>();
}
