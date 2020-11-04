#include <string>
#include <memory>
#include "RS_instance_base.h" // definition req'd for unique_ptr

/// @class RS_instance_factory RS_instance_factory.h
/// @brief This class is an abstract interface to support RS factory sub-classes

class RS_instance_factory
{
public: // Interface

   RS_instance_factory() = default;
   virtual ~RS_instance_factory() = default;

   static bool Register_factory(std::string const &RS_ID,
                                std::shared_ptr<RS_instance_factory> factory);

   static std::unique_ptr<RS_instance_base> Create(std::string const &RS_ID);

   virtual std::unique_ptr<RS_instance_base> Create() const = 0;

   // Rule of five
   RS_instance_factory(const RS_instance_factory& other) = delete;
   RS_instance_factory& operator=(const RS_instance_factory& other) = delete;
   RS_instance_factory(RS_instance_factory&&) = delete;
   RS_instance_factory& operator=(RS_instance_factory&&) = delete;
};