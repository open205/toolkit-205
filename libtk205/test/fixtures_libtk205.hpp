/* Copyright (c) 2021 Big Ladder Software LLC. All rights reserved.
 * See the LICENSE file for additional terms and conditions. */

#ifndef FIXTURE_LIBTK205_HPP_
#define FIXTURE_LIBTK205_HPP_

#include "gtest/gtest.h"
// The following headers are necessary to create an RS instance
#include "rs0001.h"
#include "rs0002.h"
#include "rs0003.h"
#include "rs0004.h"
#include "rs0005.h"
#include "rs0006.h"
#include "rs0007.h"
// The following headers are required wherever we register necessary factories;
// it's not required that it be in the same place that RS instances are created.
#include "rs0001_factory.h"
#include "rs0002_factory.h"
#include "rs0003_factory.h"
#include "rs0004_factory.h"
#include "rs0005_factory.h"
#include "rs0006_factory.h"
#include "rs0007_factory.h"

using namespace tk205;

class RSFixture : public testing::Test
{
protected:
    RSFixture() {}
    std::unique_ptr<RSInstanceBase> rs_;
};

class RS0001Fixture : public RSFixture
{
protected:
    RS0001Fixture() : RSFixture()
    {
        RSInstanceFactory::register_factory("RS0001", std::make_shared<tk205::RS0001Factory>());
        rs_ = RSInstanceFactory::create("RS0001", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0001/Chiller-Constant-Efficiency.RS0001.a205.json");
    }
};

class RS0002Fixture : public RSFixture
{
protected:
    RS0002Fixture() : RSFixture()
    {
        RSInstanceFactory::register_factory("RS0002", std::make_shared<tk205::RS0002Factory>());
        rs_ = RSInstanceFactory::create("RS0002", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0002/Unitary-Constant-Efficiency.RS0002.a205.json");
    }
};

class RS0003Fixture : public RSFixture
{
protected:
    RS0003Fixture() : RSFixture()
    {
        RSInstanceFactory::register_factory("RS0003", std::make_shared<tk205::RS0003Factory>());
        rs_= RSInstanceFactory::create("RS0003", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0003/Fan-Continuous.RS0003.a205.json");
    }
};

class RS0004Fixture : public RSFixture
{
protected:
    RS0004Fixture() : RSFixture()
    {
        RSInstanceFactory::register_factory("RS0004", std::make_shared<tk205::RS0004Factory>());
        rs_= RSInstanceFactory::create("RS0004", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0004/DX-Constant-Efficiency.RS0004.a205.json");
    }
};

class RS0005Fixture : public RSFixture
{
protected:
    RS0005Fixture() : RSFixture()
    {
        RSInstanceFactory::register_factory("RS0005", std::make_shared<tk205::RS0005Factory>());
        rs_= RSInstanceFactory::create("RS0005", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0005/Motor-Constant-Efficiency.RS0005.a205.json");
    }
};

class RS0006Fixture : public RSFixture
{
protected:
    RS0006Fixture() : RSFixture()
    {
        RSInstanceFactory::register_factory("RS0006", std::make_shared<tk205::RS0006Factory>());
        rs_ = RSInstanceFactory::create("RS0006", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0006/Drive-Constant-Efficiency.RS0006.a205.json");
    }
};

class RS0007Fixture : public RSFixture
{
protected:
    RS0007Fixture() : RSFixture()
    {
        RSInstanceFactory::register_factory("RS0007", std::make_shared<tk205::RS0007Factory>());
        rs_ = RSInstanceFactory::create("RS0007", TEST205_INPUT_EXAMPLES_DIR "/examples/RS0007/Belt-Drive-Constant-Efficiency.RS0007.a205.json");
    }
};

#endif // FIXTURE_LIBTK205_HPP_
