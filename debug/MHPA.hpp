#pragma once

#include <iostream>
#include <source_location>
#include <sstream>
#include <thread>

#define MHPA_TRACE_FUNC() MHPA::debug MHPA_dbg(__func__, "()")
#define MHPA_TRACE() MHPA_dbg(std::source_location::current())
#define MHPA_LOG(...) MHPA_dbg(std::source_location::current(), __VA_ARGS__)

namespace MHPA {
inline std::size_t _get_spacing(int increment = 0) {
  thread_local std::size_t spacing = 0;
  spacing += increment;
  return spacing;
}

template <typename... Args>
std::string _to_string(Args &&...args) {
  std::stringstream ss;
  (ss << ... << std::forward<Args>(args));
  return ss.str();
}

std::string _to_string() { return ""; }

template <typename... Args>
void _print(std::thread::id threadId, std::source_location local,
            Args &&...args) {
  std::stringstream ss;
  ss << "MHPA " << threadId << " ";
  (ss << ... << std::forward<Args>(args));
  constexpr std::size_t MIN_SPACING = 70;
  const std::string spaces =
      ss.str().size() >= MIN_SPACING
          ? " "
          : std::string(MIN_SPACING - ss.str().size(), ' ');
  ss << spaces << local.file_name() << " (" << local.line() << ")\n";
  std::cerr << ss.str();
}

template <typename... Ts>
class debug final {
 public:
  debug(Ts &&...ts,
        std::source_location local = std::source_location::current())
      : threadId_(std::this_thread::get_id()),
        local_(std::move(local)),
        name_(_to_string(std::forward<Ts>(ts)...)),
        spaces_(_get_spacing() * 2, ' '),
        spaces2_(_get_spacing(1) * 2, ' ') {
    _print(threadId_, local_, spaces_, ">>| ", name_);
  }
  ~debug() {
    _print(threadId_, local_, spaces_, "<<| ", name_);
    _get_spacing(-1);
  }

  template <typename... Args>
  void operator()(std::source_location local, Args &&...args) {
    _print(threadId_, local, spaces2_, "| ", std::forward<Args>(args)...);
  }

 private:
  std::thread::id threadId_;
  std::source_location local_;
  std::string name_;
  std::string spaces_;
  std::string spaces2_;
};

template <typename... Args>
debug(Args &&...) -> debug<Args...>;

}  // namespace MHPA
