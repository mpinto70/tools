#include <debug/debug.hpp>
#include <gtest/gtest.h>

namespace DEBUG::test {

namespace {
TEST(Debug, basic) {
    DEBUG_TRACE_FUNC();
    DEBUG_LOG("Hello, world!");
    DEBUG_LOG(PROJECT_DIR);
}

TEST(Debug, with_name) {
    DEBUG_TRACE_FUNC("Some name");
    DEBUG_LOG("Hello, world!");
}

static void func() {
    DEBUG_TRACE_FUNC("Inner func");
    DEBUG_LOG("Multiple values = ", 1234, " and ", 56.78);
}

TEST(Debug, multi_level) {
    DEBUG_TRACE_FUNC("Some name");
    DEBUG_LOG("Hello, world!");
    func();
}

} // namespace

} // namespace DEBUG::test
