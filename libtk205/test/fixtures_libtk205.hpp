/* Copyright (c) 2021 Big Ladder Software LLC. All rights reserved.
 * See the LICENSE file for additional terms and conditions. */

#ifndef FIXTURE_LIBTK205_HPP_
#define FIXTURE_LIBTK205_HPP_

#include "gtest/gtest.h"
// The following headers are necessary to Create an RS instance
#include "RS0001.h"
#include "RS0002.h"
#include "RS0003.h"
#include "RS0004.h"
#include "RS0005.h"
#include "RS0006.h"
#include "RS0007.h"
// The following headers are required wherever we register necessary factories;
// it's not required that it be in the same place that RS instances are Created.
#include "RS0001_factory.h"
#include "RS0002_factory.h"
#include "RS0003_factory.h"
#include "RS0004_factory.h"
#include "RS0005_factory.h"
#include "RS0006_factory.h"
#include "RS0007_factory.h"

using namespace tk205;

class RS_fixture : public testing::Test
{
protected:
    RS_fixture() {}
    std::unique_ptr<rs_instance_base> _rs;
};

class RS0001_fixture : public RS_fixture
{
protected:
    RS0001_fixture() : RS_fixture()
    {
        rs_instance_factory::Register_factory("RS0001", std::make_shared<tk205::RS0001_factory>());
        _rs = rs_instance_factory::Create("RS0001", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0001/Chiller-Constant-Efficiency.RS0001.a205.json");
    }
};

class RS0002_fixture : public RS_fixture
{
protected:
    RS0002_fixture() : RS_fixture()
    {
        rs_instance_factory::Register_factory("RS0002", std::make_shared<tk205::RS0002_factory>());
        _rs = rs_instance_factory::Create("RS0002", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0002/Unitary-Constant-Efficiency.RS0002.a205.json");
    }
};

class RS0003_fixture : public RS_fixture
{
protected:
    RS0003_fixture() : RS_fixture()
    {
        rs_instance_factory::Register_factory("RS0003", std::make_shared<tk205::RS0003_factory>());
        _rs= rs_instance_factory::Create("RS0003", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0003/Fan-Continuous.RS0003.a205.json");
    }
};

class RS0004_fixture : public RS_fixture
{
protected:
    RS0004_fixture() : RS_fixture()
    {
        rs_instance_factory::Register_factory("RS0004", std::make_shared<tk205::RS0004_factory>());
        _rs= rs_instance_factory::Create("RS0004", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0004/DX-Constant-Efficiency.RS0004.a205.json");
    }
};

class RS0005_fixture : public RS_fixture
{
protected:
    RS0005_fixture() : RS_fixture()
    {
        rs_instance_factory::Register_factory("RS0005", std::make_shared<tk205::RS0005_factory>());
        _rs= rs_instance_factory::Create("RS0005", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0005/Motor-Constant-Efficiency.RS0005.a205.json");
    }
};

class RS0006_fixture : public RS_fixture
{
protected:
    RS0006_fixture() : RS_fixture()
    {
        rs_instance_factory::Register_factory("RS0006", std::make_shared<tk205::RS0006_factory>());
        _rs = rs_instance_factory::Create("RS0006", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0006/Drive-Constant-Efficiency.RS0006.a205.json");
    }
};

class RS0007_fixture : public RS_fixture
{
protected:
    RS0007_fixture() : RS_fixture()
    {
        rs_instance_factory::Register_factory("RS0007", std::make_shared<tk205::RS0007_factory>());
        _rs = rs_instance_factory::Create("RS0007", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0007/Belt-Drive-Constant-Efficiency.RS0007.a205.json");
    }
};

#endif // FIXTURE_LIBTK205_HPP_
