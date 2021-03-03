/* Copyright (c) 2021 Big Ladder Software LLC. All rights reserved.
 * See the LICENSE file for additional terms and conditions. */

#ifndef FIXTURE_LIBTK205_HPP_
#define FIXTURE_LIBTK205_HPP_

#include "gtest/gtest.h"
#include "libtk205.h"

using namespace libtk205_NS;

class RS_fixture : public testing::Test {
protected:
   RS_fixture(const char * filename) : _sdk() 
   {
      _a205 = _sdk.Load_A205(filename);
   }
   A205_SDK _sdk;
   ASHRAE205_NS::ASHRAE205 _a205;
};

class RS0001_fixture : public RS_fixture {
protected:
   RS0001_fixture() : RS_fixture(TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0001/Chiller-Constant-Efficiency.RS0001.a205.json") 
   {
   }
};

class RS0002_fixture : public RS_fixture {
protected:
   RS0002_fixture() : RS_fixture(TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0002/Unitary-Constant-Efficiency.RS0002.a205.json") 
   {
   }
};

class RS0003_fixture : public RS_fixture {
protected:
   RS0003_fixture() : RS_fixture(TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0003/Fan-Continuous.RS0003.a205.json") 
   {
   }
};

class RS0004_fixture : public RS_fixture {
protected:
   RS0004_fixture() : RS_fixture(TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0004/DX-Constant-Efficiency.RS0004.a205.json") 
   {
   }
};

class RS0005_fixture : public RS_fixture {
protected:
   RS0005_fixture() : RS_fixture(TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0005/Motor-Constant-Efficiency.RS0005.a205.json") 
   {
   }
};

class RS0006_fixture : public RS_fixture {
protected:
   RS0006_fixture() : RS_fixture(TEST205_INPUT_EXAMPLES_DIR"/schema-205/examples/RS0006/Drive-Constant-Efficiency.RS0006.a205.json") 
   {
   }
};

#endif // FIXTURE_LIBTK205_HPP_
