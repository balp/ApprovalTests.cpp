#include "Catch.hpp"
#include <ApprovalTests/Approvals.h>

#include <ostream>

using namespace std;

struct Rectangle3{

    int x,y, width, height;

    friend std::ostream &operator<<(std::ostream &os, const Rectangle3 &rectangle) {
        os << "[x: " << rectangle.x << " y: " << rectangle.y << " width: " << rectangle.width << " height: "
           << rectangle.height << "]";
        return os;
    }
};

std::vector<Rectangle3> getRectangles()
{
    return
    {
        {4, 50, 100, 61},
        {50, 5200, 400, 62},
        {60, 3, 7, 63},
    };
}

TEST_CASE("MultipleLinesCanBeHardToRead") {
    Approvals::verifyAll(
        "rectangles",
        getRectangles(),
        [](auto r, auto& os){os << r;}
    );
}

// startcode to_string_wrapper_example
struct FormatRectangleForMultipleLines{

    explicit FormatRectangleForMultipleLines(Rectangle3 rectangle) : rectangle(rectangle)
    {
    }

    Rectangle3 rectangle;

    friend std::ostream &operator<<(std::ostream &os, const FormatRectangleForMultipleLines &wrapper) {
        os << "(x,y,width,height) = (" <<
           wrapper.rectangle.x << "," <<
           wrapper.rectangle.y << "," <<
           wrapper.rectangle.width << "," <<
           wrapper.rectangle.height << ")";
        return os;
    }
};
// endcode

TEST_CASE("AlternativeFormattingCanBeEasyToRead") {
    Approvals::verifyAll(
        "rectangles",
        getRectangles(),
        [](auto r, auto& os){os << FormatRectangleForMultipleLines(r);}
    );
}

std::ostream& toStringForMultipleLines(std::ostream &os, const Rectangle3 &rectangle) {
    os << "(x,y,width,height) = (" <<
       rectangle.x << "," <<
       rectangle.y << "," <<
       rectangle.width << "," <<
       rectangle.height << ")";
    return os;
}

TEST_CASE("AlternativeFormattingCanBeEasyToRead2") {
    Approvals::verifyAll(
        "rectangles",
        getRectangles(),
        [](auto r, auto& os){ toStringForMultipleLines(os, r);}
    );
}