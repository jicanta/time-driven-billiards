#pragma once

#include "arguments.hpp"
#include "billiard.hpp"

int runOscillator(const Arguments& arguments);
int runSimulate(const Arguments& arguments);
int runBench(const Arguments& arguments);
int runExplore(const Arguments& arguments);

BilliardParameters billiardFromArguments(const Arguments& arguments);
