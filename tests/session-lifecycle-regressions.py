"""Run actual Session lifecycle methods under ASAN/UBSAN, and the guest-map guard in debug mode."""
import argparse,pathlib,re,subprocess,tempfile
p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=pathlib.Path)
source=p.parse_args().source.resolve(strict=True)
folder=source/'hardware/xiaomi/aidl/fingerprint';text=(folder/'Session.cpp').read_text()
def method(name):
 m=re.search(r'^[^\n]*'+re.escape(name)+r'\([^)]*\)\s*\{',text,re.M)
 assert m,name
 pos=m.end();depth=1
 while depth:depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
 return text[m.start():pos]
methods='\n'.join(method(n) for n in ('~Session','unlinkDeathRecipient','close','linkToDeath','isClosed','clearLockout','startLockoutTimer','lockoutTimerExpired','enumerateEnrollments','onClientDeath','checkSensorLockout','authenticate'))
enum=text.split('case FINGERPRINT_TEMPLATE_ENUMERATING: {',1)[1].split('#ifndef IMPL_V2',1)[1].split('#else',1)[0]
code=r'''
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <memory>
#include <mutex>
#include <thread>
#include <utility>
#include <vector>
#define ALOGI(...) ((void)0)
#define ALOGD(...) ((void)0)
#define ALOGE(...) ((void)0)
namespace ndk {struct ScopedAStatus {static ScopedAStatus ok(){return {};}};}
using binder_status_t=int;constexpr int STATUS_DEAD_OBJECT=-32;
struct AIBinder {bool fail=false;};
using Death=void(*)(void*);
struct AIBinder_DeathRecipient {Death died,unlinked;};
struct Cookie {Death died,unlinked;void* cookie;};
std::vector<Cookie> cookies;std::atomic<int> deletes=0,destroyed=0;
AIBinder_DeathRecipient* AIBinder_DeathRecipient_new(Death cb){return new AIBinder_DeathRecipient{cb,nullptr};}
void AIBinder_DeathRecipient_setOnUnlinked(AIBinder_DeathRecipient* r,Death cb){r->unlinked=cb;}
void AIBinder_DeathRecipient_delete(AIBinder_DeathRecipient* r){++deletes;delete r;}
int AIBinder_linkToDeath(AIBinder* b,AIBinder_DeathRecipient* r,void* c){
 if(b->fail){r->unlinked(c);return -1;}cookies.push_back({r->died,r->unlinked,c});return 0;
}
enum class Error{UNABLE_TO_PROCESS};
struct Callback {std::atomic<int> closes=0,clears=0,timed=0;std::vector<int32_t> enumeration;
 void onLockoutTimed(int64_t){++timed;}void onLockoutPermanent(){}void onError(Error,int){}
 void onSessionClosed(){++closes;}void onLockoutCleared(){++clears;}
 void onEnrollmentsEnumerated(const std::vector<int32_t>& v){enumeration=v;}};
struct Tracker {enum class LockoutMode{kNone,kTimed,kPermanent};LockoutMode mode=LockoutMode::kNone;
 void reset(bool){mode=LockoutMode::kNone;}LockoutMode getMode(){return mode;}int64_t getLockoutTimeLeft(){return 20;}};
using LockoutTracker=Tracker;
struct Device {int auths=0;int enumerate(Device*){return 0;}int authenticate(Device*,int64_t,int){++auths;return 0;}};
struct Message {struct {struct {struct {int fid,gid;}finger;int remaining_templates;}enumerated;}data;};
void onClientDeath(void* cookie);
class Session;
struct ICancellationSignal {virtual ~ICancellationSignal()=default;};
struct CancellationSignal : ICancellationSignal {CancellationSignal(std::weak_ptr<Session>){} };
struct SharedRefBase {template<class T,class... A>static std::shared_ptr<T> make(A&&... a){return std::make_shared<T>(std::forward<A>(a)...);}};
struct Destruction {~Destruction(){++destroyed;}};
class Session : public std::enable_shared_from_this<Session> {
public:
 std::atomic<bool> mClosed{false};std::mutex mDeathMutex,mEnrollmentsMutex;std::recursive_mutex mLockoutMutex;
 std::vector<int32_t> mEnumeratedEnrollments;bool mIsLockoutTimerStarted=false;uint64_t mLockoutTimerGeneration=0;
 AIBinder_DeathRecipient* mDeathRecipient;std::shared_ptr<Callback> mCb=std::make_shared<Callback>();
 Tracker mLockoutTracker;Device device;Device* mDevice=&device;Destruction destruction;int mUserId=0;
 Session(){mDeathRecipient=AIBinder_DeathRecipient_new(onClientDeath);
 AIBinder_DeathRecipient_setOnUnlinked(mDeathRecipient,[](void* c){delete static_cast<std::weak_ptr<Session>*>(c);});}
 template<class T>std::shared_ptr<T> ref(){return std::static_pointer_cast<T>(shared_from_this());}
 ~Session();void unlinkDeathRecipient();ndk::ScopedAStatus close();binder_status_t linkToDeath(AIBinder*);
 bool isClosed();void clearLockout(bool);void startLockoutTimer(int64_t);void lockoutTimerExpired(uint64_t);
 ndk::ScopedAStatus enumerateEnrollments();
 bool checkSensorLockout();ndk::ScopedAStatus authenticate(int64_t,std::shared_ptr<ICancellationSignal>*);
 void enumeration(int fid,int remaining){Message message{};message.data.enumerated.finger.fid=fid;
 message.data.enumerated.remaining_templates=remaining;const Message* msg=&message;switch(0){case 0:{
'''+enum+r'''
 }break;}}
};
'''+methods+r'''
int main(){
 {auto s=std::make_shared<Session>();s->mLockoutTracker.mode=Tracker::LockoutMode::kTimed;
 std::shared_ptr<ICancellationSignal> signal;s->authenticate(1,&signal);assert(s->device.auths==0&&s->mCb->timed==1);
 s->clearLockout(true);s->authenticate(1,&signal);assert(s->device.auths==1);s->close();
 s->authenticate(1,&signal);assert(s->device.auths==1);std::this_thread::sleep_for(std::chrono::milliseconds(30));}
 {auto s=std::make_shared<Session>();auto cb=s->mCb;int before=deletes;
 std::vector<std::thread> closers;for(int i=0;i<32;i++)closers.emplace_back([s]{s->close();});for(auto& t:closers)t.join();
 assert(cb->closes==1&&deletes==before+1);s->close();assert(cb->closes==1);s.reset();assert(deletes==before+1);}
 {auto s=std::make_shared<Session>();auto cb=s->mCb;std::weak_ptr<Session> weak=s;
 s->startLockoutTimer(20);s->close();s.reset();assert(weak.expired());std::this_thread::sleep_for(std::chrono::milliseconds(60));assert(cb->clears==0);}
 {auto s=std::make_shared<Session>();auto cb=s->mCb;s->startLockoutTimer(100);uint64_t old=s->mLockoutTimerGeneration;
 s->clearLockout(true);s->startLockoutTimer(200);s->lockoutTimerExpired(old);
 assert(cb->clears==1&&s->mIsLockoutTimerStarted);std::this_thread::sleep_for(std::chrono::milliseconds(140));
 assert(cb->clears==1);std::this_thread::sleep_for(std::chrono::milliseconds(110));assert(cb->clears==2);s->close();}
 {auto s=std::make_shared<Session>();auto cb=s->mCb;AIBinder binder;assert(s->linkToDeath(&binder)==0);
 // onUnlinked can be delayed past recipient deletion; the cookie is independently alive.
 s->close();s.reset();cookies.back().died(cookies.back().cookie);cookies.back().unlinked(cookies.back().cookie);cookies.clear();assert(cb->closes==1);}
 {auto s=std::make_shared<Session>();AIBinder dead;dead.fail=true;assert(s->linkToDeath(&dead)!=0);s->close();}
 {auto a=std::make_shared<Session>(),b=std::make_shared<Session>();
 a->enumerateEnrollments();a->enumeration(17,1);b->enumerateEnrollments();b->enumeration(23,0);
 assert(b->mCb->enumeration==std::vector<int32_t>{23});a->enumerateEnrollments();a->enumeration(0,0);
 assert(a->mCb->enumeration.empty());a->enumeration(33,1);a->close();assert(a->mEnumeratedEnrollments.empty());b->close();}
}
'''
with tempfile.TemporaryDirectory(prefix='session-lifecycle-') as tmp:
 d=pathlib.Path(tmp);cpp=d/'probe.cpp';exe=d/'probe';cpp.write_text(code)
 subprocess.run(['g++','-std=c++20','-pthread','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(cpp),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
 # Compile the actual guest-map lookup/guard with checked container iterators.
 native=(source/'system/core/debuggerd/libdebuggerd/tombstone_proto_to_text.cpp').read_text()
 guard=native[native.index('  const auto& guest_threads = tombstone.guest_threads();'):].split('\n\n',1)[0]
 guest='''#include <unordered_map>\n#include <cassert>\nstruct Tombstone {std::unordered_map<int,int> guest;int tid(){return 5;}const auto& guest_threads(){return guest;}};
int calls=0;void print_guest_thread(int,int,Tombstone&,int,int,bool){calls++;}
void probe(Tombstone& tombstone){int callback=0,symbolize=0;std::unordered_map<int,int> threads;
'''+guard+'''\n}int main(){Tombstone t;probe(t);assert(calls==0);t.guest[5]=10;probe(t);assert(calls==1);}\n'''
 cpp.write_text(guest);subprocess.run(['g++','-std=c++20','-D_GLIBCXX_DEBUG',str(cpp),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
 cpp.write_text(guest.replace('main_guest_thread_it != guest_threads.end()','main_guest_thread_it != threads.end()'))
 subprocess.run(['g++','-std=c++20','-D_GLIBCXX_DEBUG',str(cpp),'-o',str(exe)],check=True)
 negative=subprocess.run([str(exe)],capture_output=True,text=True);assert negative.returncode!=0 and 'different sequences' in negative.stderr
print('PASS: actual Session methods ASAN/UBSAN; concurrent close, expired owner, stale timer, delayed death/unlink, failed link, per-session/empty enumeration; guest iterator guard and negative control')
