/* Copyright (c) 2021 Big Ladder Software LLC. All rights reserved.
 * See the LICENSE file for additional terms and conditions. */

#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include "fixtures_libtk205.hpp"
#include "libtk205.h"

using namespace libtk205_NS;

TEST_F(RS0001_fixture, Create_RS01)
{
   auto rs = _sdk.Get_RS0001(_a205);
   EXPECT_TRUE(rs != nullptr);
}

TEST_F(RS0001_fixture, Calculate_performance_cooling)
{
   auto rs = _sdk.Get_RS0001(_a205);
   std::vector<double> target {0.0755, 280.0, 0.0957, 295.0, 0.5};
   auto result = rs->performance.performance_map_cooling.Calculate_performance(target);
   EXPECT_EQ(result.size(), 9u);
   //EXPECT_THAT(result, testing::ElementsAre(testing::DoubleEq(3.189), testing::DoubleEq(6.378), ...));
   }

TEST_F(RS0005_fixture, Calculate_embedded_RS_performance)
{
   auto rs05 = _sdk.Get_RS0005(_a205);
   EXPECT_TRUE(rs05 != nullptr);

   if (rs05)
   {
      auto rs06 = _sdk.Get_RS0006(rs05->performance.drive_representation);
      EXPECT_TRUE(rs06 != nullptr);
      if (rs06)
      {
         std::vector<double> target {5550.0};
         auto result = rs06->performance.performance_map.Calculate_performance(target);
         EXPECT_THAT(result, testing::ElementsAre(testing::DoubleEq(0.985)));
      }
   }
}

TEST_F(RS0002_fixture, Create_RS02)
{
   auto rs = _sdk.Get_RS0002(_a205);
   EXPECT_TRUE(rs != nullptr);
}

TEST_F(RS0003_fixture, Create_RS03)
{
   auto rs = _sdk.Get_RS0003(_a205);
   EXPECT_TRUE(rs != nullptr);
}

TEST_F(RS0004_fixture, Create_RS04)
{
   auto rs = _sdk.Get_RS0004(_a205);
   EXPECT_TRUE(rs != nullptr);
}

TEST_F(RS0005_fixture, Create_RS05)
{
   auto rs = _sdk.Get_RS0005(_a205);
   EXPECT_TRUE(rs != nullptr);
}

TEST_F(RS0006_fixture, Create_RS06)
{
   auto rs = _sdk.Get_RS0006(_a205);
   EXPECT_TRUE(rs != nullptr);
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
   if (severity >= msg_severity::WARN)
   {
      std::cout << severity_str[severity] << ": " << message << std::endl;
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
