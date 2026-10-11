#include "scene_inspector_admission.hpp"

namespace syspane::interfaces {
namespace d=recovery;
InspectorAdmission::InspectorAdmission(rendering::SceneSurface& surface):surface_(surface){}
void InspectorAdmission::owner()const{
    if(owner_!=std::this_thread::get_id()||calling_)throw std::logic_error("inspector.delivery_owner");
}
void InspectorAdmission::forget(){binding_.reset();frame_.reset();heartbeat_.reset();token_=until_=0;}
void InspectorAdmission::reset(){owner();forget();}
bool InspectorAdmission::compatible(d::DeliveryScope current)const{
    owner();return current.profile&&(!scope_.profile||scope_.profile==current.profile);
}
std::map<std::string,model::Tick> InspectorAdmission::admit(const d::TelemetryDelivery& value,d::DeliveryScope current,std::uint64_t now){
    owner();
    const bool matches=compatible(current);
    struct Call {bool& active;explicit Call(bool& a):active(a){active=true;}~Call(){active=false;}} call(calling_);
    if(!matches){forget();surface_.close();return {};}
    std::map<std::string,model::Tick> ticks;
    const auto detach=[&]{
        if(token_&&binding_)(void)surface_.disconnect(binding_->producer,token_,binding_->policy_revision,now);
        forget();ticks.clear();
    };
    if(!value.deliverable(current,now)){detach();scope_=current;return ticks;}
    const auto& binding=*value.binding;
    if(scope_.generation!=current.generation||binding_!=value.binding||now>=until_)detach();
    scope_=current;
    if(!token_){
        const auto attached=surface_.attach(binding.producer,binding,now);
        if(attached.code!=d::DataCode::accepted)return ticks;
        token_=attached.token;binding_=value.binding;until_=now+3000;
    }
    ticks[binding.producer]=*value.clock;
    if(frame_!=value.frame){
        if(frame_){
            const auto before=frame_->ordinal,after=value.frame->ordinal;
            if(after<=before){detach();return ticks;}
            if(after-before>1&&surface_.gap(binding.producer,token_,binding.policy_revision,now)!=d::DataCode::accepted){detach();return ticks;}
        }
        const auto accepted=surface_.receive(binding.producer,token_,binding.policy_revision,value.frame->bytes,now,*value.clock);
        if(accepted.code!=d::DataCode::accepted&&accepted.code!=d::DataCode::duplicate){detach();return ticks;}
        frame_=value.frame;
    }
    if(value.heartbeat&&value.heartbeat!=heartbeat_){
        const auto accepted=surface_.heartbeat(binding.producer,token_,binding.policy_revision,*value.heartbeat,now);
        if(accepted!=d::DataCode::accepted&&accepted!=d::DataCode::duplicate){detach();return ticks;}
        if(accepted==d::DataCode::accepted)until_=now+3000;
        heartbeat_=value.heartbeat;
    }
    return ticks;
}
}
