#ifndef APPROVALTESTS_CPP_TESTREPORTER_H
#define APPROVALTESTS_CPP_TESTREPORTER_H

#include "ApprovalTests/reporters/GenericDiffReporter.h"
#include "DoNothingLauncher.h"

class TestReporter : public ApprovalTests::CommandReporter
{
public:
    DoNothingLauncher launcher;

    TestReporter(bool working = true) : CommandReporter("fake", &launcher)
    {
        launcher.working = working;
    };
};
#endif //APPROVALTESTS_CPP_TESTREPORTER_H
