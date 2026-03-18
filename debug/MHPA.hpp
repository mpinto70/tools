#pragma once

#include <iostream>
#include <source_location>
#include <sstream>
#include <thread>

inline std::size_t MHPA_get_spacing(int increment = 0) {
  thread_local std::size_t spacing = 0;
  spacing += increment;
  return spacing;
}

template <typename... Args>
std::string MHPA_to_string(Args &&...args) {
  std::stringstream ss;
  (ss << ... << std::forward<Args>(args));
  return ss.str();
}

template <typename... Args>
void MHPA_print(std::thread::id threadId, std::source_location local,
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

class MHPA_debug final {
 public:
  template <typename... Args>
  MHPA_debug(Args &&...args,
             std::source_location local = std::source_location::current())
      : threadId_(std::this_thread::get_id()),
        local_(local),
        name_(MHPA_to_string(std::forward<Args>(args)...)),
        spaces_(MHPA_get_spacing() * 2, ' '),
        spaces2_(MHPA_get_spacing(1) * 2, ' ') {
    MHPA_print(threadId_, local_, spaces_, ">>| ", name_);
  }
  ~MHPA_debug() {
    MHPA_print(threadId_, local_, spaces_, "<<| ", name_);
    MHPA_get_spacing(-1);
  }

  template <typename... Args>
  void dbg(Args &&...args,
           std::source_location local = std::source_location::current()) {
    MHPA_print(threadId_, local, spaces2_, "| ", std::forward<Args>(args)...);
  }

 private:
  std::thread::id threadId_;
  std::source_location local_;
  std::string name_;
  std::string spaces_;
  std::string spaces2_;
};
