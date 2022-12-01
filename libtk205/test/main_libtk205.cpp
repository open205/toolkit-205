/* Copyright (c) 2021 Big Ladder Software LLC. All rights reserved.
 * See the LICENSE file for additional terms and conditions. */

#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include "fixtures_libtk205.hpp"
#include <stdexcept>

TEST_F(RS0001BadFixture, Verify_RS_object)
{
    auto rs = dynamic_cast<rs0001_ns::RS0001 *>(rs_.get());
    EXPECT_TRUE(rs == nullptr);
}

TEST_F(RS0001UnsupportedFixture, Verify_schema_version)
{
    auto rs = dynamic_cast<rs0001_ns::RS0001 *>(rs_.get());
    EXPECT_TRUE(rs == nullptr);
}

TEST_F(RS0001Fixture, Check_is_set)
{
    auto rs = dynamic_cast<rs0001_ns::RS0001 *>(rs_.get());
    EXPECT_TRUE(rs != nullptr);
    EXPECT_FALSE(rs->metadata.data_source_is_set);
    EXPECT_TRUE(rs->metadata.description_is_set);
}

TEST_F(RS0001Fixture, Calculate_performance_cooling)
{
    auto rs = dynamic_cast<rs0001_ns::RS0001 *>(rs_.get());
    EXPECT_TRUE(rs != nullptr);
    std::vector<double> target {0.0755, 280.0, 0.0957, 295.0, 0.5}; //NOLINT : Magic numbers necessary!
    auto result = rs->performance.performance_map_cooling.calculate_performance(target);
    EXPECT_EQ(result.size(), 9u);
}

TEST_F(RS0001Fixture, Calculate_performance_cooling_2)
{
    auto rs = dynamic_cast<rs0001_ns::RS0001 *>(rs_.get());
    EXPECT_TRUE(rs != nullptr);
    std::vector<double> target {0.0755, 280.0, 0.0957, 295.0, 0.5}; //NOLINT : Magic numbers necessary!
    auto result = rs->performance.performance_map_cooling.calculate_performance(target, rs->performance.performance_map_cooling.lookup_variables.condenser_liquid_leaving_temperature_index);
    // 59593.2,351600,411193,281.11,296.03,74400,23600,0,0
    EXPECT_NEAR(result, 296.03, 0.001);
}

TEST_F(RS0001Fixture, Calculate_performance_cooling_3)
{
    auto rs = dynamic_cast<rs0001_ns::RS0001 *>(rs_.get());
    EXPECT_TRUE(rs != nullptr);
    auto result = rs->performance.performance_map_cooling.calculate_performance(0.0755, 280.0, 0.0957, 295.0, 0.5, Btwxt::Method::LINEAR).condenser_liquid_leaving_temperature;
    EXPECT_NEAR(result, 296.03, 0.001);
}

TEST_F(ASHRAEChillerFixture, Calculate_performance_cubic)
{
    auto rs = dynamic_cast<rs0001_ns::RS0001 *>(rs_.get());
    EXPECT_TRUE(rs != nullptr);
    std::vector<double> target {0.00565, 280.0, 0.00845, 297.0, 1.5}; //NOLINT : Magic numbers necessary!
    auto result1 = rs->performance.performance_map_cooling.calculate_performance(target, Btwxt::Method::LINEAR);
    auto result2 = rs->performance.performance_map_cooling.calculate_performance(target, Btwxt::Method::CUBIC);
    EXPECT_NE(result1, result2);
}

TEST_F(RS0005Fixture, Calculate_embedded_RS_performance)
{
    auto rs = dynamic_cast<rs0005_ns::RS0005 *>(rs_.get());
    EXPECT_TRUE(rs != nullptr);
    std::vector<double> target {5550.0, 10.0}; //NOLINT
    auto result = rs->performance.drive_representation.performance.performance_map.calculate_performance(target);
    EXPECT_THAT(result, testing::ElementsAre(testing::DoubleEq(0.985)));
}

TEST_F(RS0003Fixture, Verify_grid_variable_index)
{
    auto rs = dynamic_cast<rs0003_ns::RS0003 *>(rs_.get());
    EXPECT_TRUE(rs != nullptr);
    auto pm = dynamic_cast<rs0003_ns::PerformanceMapContinuous *>(rs->performance.performance_map.get());
    auto result = pm->grid_variables.static_pressure_difference_index;
    EXPECT_EQ(result, 1u);
}

TEST_F(RS0006Fixture, Verify_enum_description)
{
    auto result = rs0006_ns::CoolingMethod_info.at(rs0006_ns::CoolingMethod::ACTIVE_AIR_COOLED).description;
    EXPECT_THAT(result, "Drive is cooled using forced air convection within the surrounding environment");
}

TEST_F(RS0001Fixture, Verify_element_metadata)
{
    auto result = rs0001_ns::RatingAHRI550590PartLoadPoint::evaporator_liquid_volumetric_flow_rate_name;
    EXPECT_THAT(result, "evaporator_liquid_volumetric_flow_rate");
    result = rs0001_ns::RatingAHRI550590PartLoadPoint::evaporator_liquid_volumetric_flow_rate_units;
    EXPECT_THAT(result, "gpm");
}

void Display_message(MsgSeverity severity, const std::string &message, void *)
{
    static std::map<MsgSeverity, std::string> severity_str {
        {MsgSeverity::DEBUG_205, "DEBUG"},
        {MsgSeverity::INFO_205, "INFO"},
        {MsgSeverity::WARN_205, "WARN"},
        {MsgSeverity::ERR_205, "ERR"}
    };
    std::cout << severity_str[severity] << ": " << message << std::endl;
}

void Btwxt_message(const Btwxt::MsgLevel messageType, const std::string message,
                   void *)
{
    static std::map<Btwxt::MsgLevel, MsgSeverity> severity {
        {Btwxt::MsgLevel::MSG_DEBUG, MsgSeverity::DEBUG_205},
        {Btwxt::MsgLevel::MSG_INFO, MsgSeverity::INFO_205},
        {Btwxt::MsgLevel::MSG_WARN, MsgSeverity::WARN_205},
        {Btwxt::MsgLevel::MSG_ERR, MsgSeverity::ERR_205}
    };
    Display_message(severity[messageType], message, nullptr);
}

int main(int argc, char **argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    tk205::set_error_handler(Display_message, nullptr);
    Btwxt::setMessageCallback(Btwxt_message, nullptr);
    return RUN_ALL_TESTS();
}
