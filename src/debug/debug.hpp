#pragma once

#ifdef NODEBUG

#define DEBUG_TRACE_FUNC(...)
#define DEBUG_LOG(...)

#else

#include <cstring>
#include <iostream>
#include <source_location>
#include <sstream>
#include <thread>

#ifndef PROJECT_DIR
#define PROJECT_DIR ""
#endif

#ifndef DEBUG_MIN_SPACING
#define DEBUG_MIN_SPACING 80
#endif

#define DEBUG_TRACE_FUNC(...) ::DEBUG::debug DEBUG_dbg(__func__, ::DEBUG::_to_string(__VA_ARGS__))
#define DEBUG_LOG(...)        DEBUG_dbg(std::source_location::current(), ::DEBUG::_to_string(__VA_ARGS__))

namespace DEBUG {

constexpr const char _project_dir[] = PROJECT_DIR;
constexpr std::size_t _project_dir_len = sizeof(_project_dir) - 1;

inline std::size_t _get_spacing(int increment = 0) {
    thread_local std::size_t spacing = 0;
    spacing += increment;
    return spacing;
}

template <typename... Args>
inline std::string _to_string(Args&&... args) {
    std::stringstream ss;
    (ss << ... << std::forward<Args>(args));
    return ss.str();
}

inline std::string _to_string() {
    return "";
}

template <typename... Args>
inline void _print(const std::string& preamble, std::size_t line, Args&&... args) {
    constexpr std::size_t MIN_SPACING = DEBUG_MIN_SPACING;
    auto pre = _to_string(preamble, line, ") ");
    if (pre.size() < MIN_SPACING) {
        pre += std::string(MIN_SPACING - pre.size(), ' ');
    }
    const auto msg = _to_string(std::forward<Args>(args)...);
    std::stringstream ss;
    ss << pre << msg << "\n";
    std::cerr << ss.str();
}

inline std::string _create_preamble(std::source_location local) {
    std::size_t name_ini = 0;
    if (std::strncmp(local.file_name(), _project_dir, _project_dir_len) == 0) {
        name_ini = _project_dir_len;
    }

    return _to_string(
          "DEBUG ",
          std::this_thread::get_id(),
          " ",
          local.file_name() + name_ini,
          " (");
}

class debug final {
public:
    debug(std::string func,
          std::string name,
          std::source_location local = std::source_location::current())
          : func_(std::move(func)),
            name_(std::move(name)),
            preamble_(_create_preamble(local)),
            local_(std::move(local)),
            spaces_(_get_spacing() * 2, ' '),
            spaces2_(_get_spacing(1) * 2, ' ') {
        if (!name_.empty()) {
            name_ += " ";
        }
        if (!func_.empty()) {
            func_ += "()";
        }
        _print(preamble_, local_.line(), spaces_, ">>| ", name_, func_);
    }
    ~debug() {
        _print(preamble_, local_.line(), spaces_, "<<| ", name_, func_);
        _get_spacing(-1);
    }

    debug(const debug&) = delete;
    debug(debug&&) = delete;
    debug& operator=(const debug&) = delete;
    debug& operator=(debug&&) = delete;

    template <typename... Args>
    void operator()(std::source_location local, Args&&... args) {
        _print(preamble_, local.line(), spaces2_, "| ", name_, std::forward<Args>(args)...);
    }

private:
    std::string func_;
    std::string name_;
    std::string preamble_;
    std::source_location local_;
    std::string spaces_;
    std::string spaces2_;
};

} // namespace DEBUG

#endif
