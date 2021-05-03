/* Copyright (c) 2021 Big Ladder Software LLC. All rights reserved.
 * See the LICENSE file for additional terms and conditions. */

#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include "fixtures_libtk205.hpp"
#include "libtk205.h"
#include <stdexcept>

using namespace libtk205_NS;

TEST(RS_fixture, Validate_RSes)
{
   EXPECT_TRUE(A205_SDK::Validate_A205(TEST205_INPUT_EXAMPLES_DIR"/schema-205/build/schema/RS0001.schema.json", 
                                       TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0001/Chiller-Constant-Efficiency.RS0001.a205.json"));
   EXPECT_TRUE(A205_SDK::Validate_A205(TEST205_INPUT_EXAMPLES_DIR"/schema-205/build/schema/RS0002.schema.json", 
                                       TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0002/Unitary-Constant-Efficiency.RS0002.a205.json"));
   EXPECT_TRUE(A205_SDK::Validate_A205(TEST205_INPUT_EXAMPLES_DIR"/schema-205/build/schema/RS0003.schema.json", 
                                       TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0003/Fan-Continuous.RS0003.a205.json"));
}

TEST_F(RS0001_fixture, Calculate_performance_cooling)
{
   std::vector<double> target {0.0755, 280.0, 0.0957, 295.0, 0.5}; //NOLINT : Of course you need magic numbers; it's a numerical test
   auto result = _rs.performance.performance_map_cooling.Calculate_performance(target);
   EXPECT_EQ(result.size(), 9u);
   //EXPECT_THAT(result, testing::ElementsAre(testing::DoubleEq(3.189), testing::DoubleEq(6.378), ...));
   }

TEST_F(RS0005_fixture, Calculate_embedded_RS_performance)
{
    std::vector<double> target {5550.0, 10.0}; //NOLINT
    auto result = _rs.performance.drive_representation.performance.performance_map.Calculate_performance(target);
    EXPECT_THAT(result, testing::ElementsAre(testing::DoubleEq(0.985)));
}

void Display_message(ASHRAE205_NS::msg_severity severity, const std::string &message, void *)
{
   using namespace ASHRAE205_NS;
   static std::map<msg_severity, std::string> severity_str {
      {msg_severity::DEBUG, "DEBUG"},
      {msg_severity::INFO, "INFO"},
      {msg_severity::WARN, "WARN"},
      {msg_severity::ERR, "ERR"}
   };
   if (severity <= msg_severity::WARN)
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
   static std::map<Btwxt::MsgLevel, ASHRAE205_NS::msg_severity> severity {
      {Btwxt::MsgLevel::MSG_DEBUG, ASHRAE205_NS::msg_severity::DEBUG},
      {Btwxt::MsgLevel::MSG_INFO, ASHRAE205_NS::msg_severity::INFO},
      {Btwxt::MsgLevel::MSG_WARN, ASHRAE205_NS::msg_severity::WARN},
      {Btwxt::MsgLevel::MSG_ERR, ASHRAE205_NS::msg_severity::ERR}
   };
   Display_message(severity[messageType], message, nullptr);
}

int main(int argc, char **argv)
{
   ::testing::InitGoogleTest(&argc, argv);
   ASHRAE205_NS::Set_error_handler(Display_message);
   Btwxt::setMessageCallback(Btwxt_message, nullptr);
   return RUN_ALL_TESTS();
}
