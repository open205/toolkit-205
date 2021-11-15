/* Copyright (c) 2021 Big Ladder Software LLC. All rights reserved.
 * See the LICENSE file for additional terms and conditions. */

#ifndef FIXTURE_LIBTK205_HPP_
#define FIXTURE_LIBTK205_HPP_

#include "gtest/gtest.h"
#include "libtk205.h"

using namespace tk205;

class RS_fixture : public testing::Test
{
protected:
    RS_fixture() {}
};

class RS0001_fixture : public RS_fixture
{
protected:
    RS0001_fixture() : RS_fixture()
    {
        _rs = Load_RS0001(TEST205_INPUT_EXAMPLES_DIR "/schema-205/examples/RS0001/Chiller-Constant-Efficiency.RS0001.a205.json");
    }
    RS0001_NS::RS0001 _rs;
};

class RS0002_fixture : public RS_fixture
{
protected:
    RS0002_fixture() : RS_fixture()
    {
        _rs = Load_RS0002(TEST205_INPUT_EXAMPLES_DIR "/schema-205/examples/RS0002/Unitary-Constant-Efficiency.RS0002.a205.json");
    }
    RS0002_NS::RS0002 _rs;
};

class RS0003_fixture : public RS_fixture
{
protected:
    RS0003_fixture() : RS_fixture()
    {
        _rs= Load_RS0003(TEST205_INPUT_EXAMPLES_DIR "/schema-205/examples/RS0003/Fan-Continuous.RS0003.a205.json");
    }
    RS0003_NS::RS0003 _rs;
};

class RS0004_fixture : public RS_fixture
{
protected:
    RS0004_fixture() : RS_fixture()
    {
        _rs= Load_RS0004(TEST205_INPUT_EXAMPLES_DIR "/schema-205/examples/RS0004/DX-Constant-Efficiency.RS0004.a205.json");
    }
    RS0004_NS::RS0004 _rs;
};

class RS0005_fixture : public RS_fixture
{
protected:
    RS0005_fixture() : RS_fixture()
    {
        _rs= Load_RS0005(TEST205_INPUT_EXAMPLES_DIR "/schema-205/examples/RS0005/Motor-Constant-Efficiency.RS0005.a205.json");
    }
    RS0005_NS::RS0005 _rs;
};

class RS0006_fixture : public RS_fixture
{
protected:
    RS0006_fixture() : RS_fixture()
    {
        _rs = Load_RS0006(TEST205_INPUT_EXAMPLES_DIR "/schema-205/examples/RS0006/Drive-Constant-Efficiency.RS0006.a205.json");
    }
    RS0006_NS::RS0006 _rs;
};

class RS0007_fixture : public RS_fixture
{
protected:
    RS0007_fixture() : RS_fixture()
    {
        _rs = Load_RS0007(TEST205_INPUT_EXAMPLES_DIR "/schema-205/examples/RS0007/Belt-Drive-Constant-Efficiency.RS0007.a205.json");
    }
    RS0007_NS::RS0007 _rs;
};

#endif // FIXTURE_LIBTK205_HPP_
