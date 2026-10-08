#pragma once
#include "transaction.hpp"
#include <functional>
#include <memory>
#include <optional>
#include <string>

namespace syspane::platform {
struct ProfileLocation {
    std::string profile,home,config_home,data_home,state_home;
    std::optional<std::string> portable_root;
};
struct ProfilePaths {
    std::string profile,mode,configuration,content,state;
    std::string generations,packages,recovery;
};
// Pure selection; returned strings are not filesystem or policy authority.
ProfilePaths profile_paths(const ProfileLocation&);
ProfileLocation profile_environment(std::string profile,std::optional<std::string> portable_root={});

// Serialized worker only. Hold for the controller lifetime; never inherit across fork.
// Installed composition must supply current native policy and supervise filesystem work.
class LinuxProfileOwner {
public:
    using Guard=std::function<bool()>;
    using Transition=std::function<void(const std::string&)>;
    using InitialProfile=std::function<configuration::Committed()>;
    LinuxProfileOwner(const ProfileLocation&,bool create,const Guard&,Transition={},InitialProfile={});
    ~LinuxProfileOwner();
    LinuxProfileOwner(const LinuxProfileOwner&)=delete;
    LinuxProfileOwner& operator=(const LinuxProfileOwner&)=delete;
    ProfilePaths verified_paths(const Guard&)const;
private:
    struct Impl;std::unique_ptr<Impl> impl_;
};
}
