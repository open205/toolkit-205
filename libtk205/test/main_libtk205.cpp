/* Copyright (c) 2021 Big Ladder Software LLC. All rights reserved.
 * See the LICENSE file for additional terms and conditions. */

#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include "fixtures_libtk205.hpp"
#include <stdexcept>

//using namespace tk205;

#if 0
TEST(RS_fixture, Validate_RSes)
{
   EXPECT_TRUE(A205_SDK::Validate_A205(TEST205_INPUT_EXAMPLES_DIR"/schema-205/build/schema/RS0001.schema.json", 
                                       TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0001/Chiller-Constant-Efficiency.RS0001.a205.json"));
   EXPECT_TRUE(A205_SDK::Validate_A205(TEST205_INPUT_EXAMPLES_DIR"/schema-205/build/schema/RS0002.schema.json", 
                                       TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0002/Unitary-Constant-Efficiency.RS0002.a205.json"));
   EXPECT_TRUE(A205_SDK::Validate_A205(TEST205_INPUT_EXAMPLES_DIR"/schema-205/build/schema/RS0003.schema.json", 
                                       TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0003/Fan-Continuous.RS0003.a205.json"));
}
#endif

TEST_F(RS0001_fixture, Check_is_set)
{
    auto rs = dynamic_cast<RS0001_NS::RS0001 *>(_rs.get());
    EXPECT_FALSE(rs->metadata.data_source_is_set);
    EXPECT_TRUE(rs->metadata.description_is_set);
}

TEST_F(RS0001_fixture, Calculate_performance_cooling)
{
   auto rs = dynamic_cast<RS0001_NS::RS0001 *>(_rs.get());
   std::vector<double> target {0.0755, 280.0, 0.0957, 295.0, 0.5}; //NOLINT : Magic numbers necessary!
   auto result = rs->performance.performance_map_cooling.Calculate_performance(target);
   EXPECT_EQ(result.size(), 9u);
}

TEST_F(RS0001_fixture, Calculate_performance_cooling_2)
{
   auto rs = dynamic_cast<RS0001_NS::RS0001 *>(_rs.get());
   std::vector<double> target {0.0755, 280.0, 0.0957, 295.0, 0.5}; //NOLINT : Magic numbers necessary!
   auto result = rs->performance.performance_map_cooling.Calculate_performance(target, rs->performance.performance_map_cooling.lookup_variables.condenser_liquid_leaving_temperature_index);
   // 59593.2,351600,411193,281.11,296.03,74400,23600,0,0
   EXPECT_NEAR(result, 296.03, 0.001);
}

TEST_F(RS0001_fixture, Calculate_performance_cooling_3)
{
   auto rs = dynamic_cast<RS0001_NS::RS0001 *>(_rs.get());
   auto result = rs->performance.performance_map_cooling.Calculate_performance(0.0755, 280.0, 0.0957, 295.0, 0.5).condenser_liquid_leaving_temperature;
   EXPECT_NEAR(result, 296.03, 0.001);
}

TEST_F(RS0005_fixture, Calculate_embedded_RS_performance)
{
    auto rs = dynamic_cast<RS0005_NS::RS0005 *>(_rs.get());
    std::vector<double> target {5550.0, 10.0}; //NOLINT
    auto result = rs->performance.drive_representation.performance.performance_map.Calculate_performance(target);
    EXPECT_THAT(result, testing::ElementsAre(testing::DoubleEq(0.985)));
}

TEST_F(RS0003_fixture, Verify_grid_variable_index)
{
    auto rs = dynamic_cast<RS0003_NS::RS0003 *>(_rs.get());
    auto pm = dynamic_cast<RS0003_NS::PerformanceMapContinuous *>(rs->performance.performance_map.get());
    auto result = pm->grid_variables.static_pressure_difference_index;
    EXPECT_EQ(result, 1u);
}

TEST_F(RS0006_fixture, Verify_enum_description)
{
    auto result = RS0006_NS::CoolingMethod_info.at(RS0006_NS::CoolingMethod::ACTIVE_AIR_COOLED).description;
    EXPECT_THAT(result, "Drive is cooled using forced air convection within the surrounding environment");
}

TEST_F(RS0001_fixture, Verify_element_metadata)
{
    auto result = RS0001_NS::RatingAHRI550590PartLoadPoint::evaporator_liquid_volumetric_flow_rate_name;
    EXPECT_THAT(result, "evaporator_liquid_volumetric_flow_rate");
    result = RS0001_NS::RatingAHRI550590PartLoadPoint::evaporator_liquid_volumetric_flow_rate_units;
    EXPECT_THAT(result, "gpm");
}

void Display_message(msg_severity severity, const std::string &message, void *)
{
   static std::map<msg_severity, std::string> severity_str {
      {msg_severity::DEBUG_205, "DEBUG"},
      {msg_severity::INFO_205, "INFO"},
      {msg_severity::WARN_205, "WARN"},
      {msg_severity::ERR_205, "ERR"}
   };
   if (severity <= msg_severity::WARN_205)
   {
      std::cout << severity_str[severity] << ": " << message << std::endl;
   }
   else
   {
      throw std::invalid_argument(message);
   }   
}

void Btwxt_message(const Btwxt::MsgLevel messageType, const std::string message,
                   void *)
{
   static std::map<Btwxt::MsgLevel, msg_severity> severity {
      {Btwxt::MsgLevel::MSG_DEBUG, msg_severity::DEBUG_205},
      {Btwxt::MsgLevel::MSG_INFO, msg_severity::INFO_205},
      {Btwxt::MsgLevel::MSG_WARN, msg_severity::WARN_205},
      {Btwxt::MsgLevel::MSG_ERR, msg_severity::ERR_205}
   };
   Display_message(severity[messageType], message, nullptr);
}

int main(int argc, char **argv)
{
   ::testing::InitGoogleTest(&argc, argv);
   tk205::Set_error_handler(Display_message);
   Btwxt::setMessageCallback(Btwxt_message, nullptr);
   return RUN_ALL_TESTS();
}
