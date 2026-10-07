from pathlib import Path
import hashlib,json,zipfile
r=Path.cwd();d=r/'out/campaign/scene-images-original'
cases=[{'bytes':n,'sha256':hashlib.sha256(b'a'*n).hexdigest()} for n in (55,56,63,64,65,1048577,8388608,16777216)]
p=r/'tests/configuration/content-digests.json';p.write_text(json.dumps(cases,indent=2)+'\n',encoding='utf-8',newline='\n')
with zipfile.ZipFile(d/'digest-original.zip','x',zipfile.ZIP_DEFLATED) as z:z.write(p,p.relative_to(r).as_posix())
(d/'digest-original.json').write_text(json.dumps({p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8',newline='\n')
p=r/'source/configuration/digest.cpp';t=p.read_text().replace('#include <vector>','')
t=t.replace('std::string sha256(std::string_view bytes){\n    if(bytes.size()>1048576)throw protocol::Error("digest.size");','namespace {\nstd::string digest(std::string_view bytes){')
a=t.index('    std::vector<unsigned char> data');b=t.index('    const auto rotate=',a)
t=t[:a]+'''    const auto bits=static_cast<std::uint64_t>(bytes.size())*8;
    const auto length=((bytes.size()+9+63)/64)*64;
    const auto byte=[&](std::size_t at)->unsigned char {
        if(at<bytes.size())return static_cast<unsigned char>(bytes[at]);
        if(at==bytes.size())return 0x80;
        if(at>=length-8)return static_cast<unsigned char>(bits>>(8*(length-1-at)));
        return 0;
    };
'''+t[b:]
t=t.replace('pos<data.size()', 'pos<length').replace('data[pos+4*i+n]','byte(pos+4*i+n)')
t=t.rstrip();assert t.endswith('}\n}');t=t[:-1]+'''}
std::string sha256(std::string_view bytes){if(bytes.size()>1048576)throw protocol::Error("digest.size");return digest(bytes);}
std::string content_sha256(std::string_view bytes){if(bytes.size()>16777216)throw protocol::Error("digest.size");return digest(bytes);}
}
'''
p.write_text(t,encoding='utf-8',newline='\n')
p=r/'source/configuration/digest.hpp';t=p.read_text().replace('std::string sha256(std::string_view bytes);','std::string sha256(std::string_view bytes);\n// Same algorithm, bounded to the declared 16 MiB content-asset ceiling.\nstd::string content_sha256(std::string_view bytes);');p.write_text(t,encoding='utf-8',newline='\n')
for name,replacements in {
 'source/configuration/content.cpp':[('&&sha256(raw)==asset','&&content_sha256(raw)==asset')],
 'source/rendering/image_job_linux.cpp':[('configuration::sha256(encoded)','configuration::content_sha256(encoded)')],
 'source/platform/generation_store_linux.cpp':[('c::sha256(payload)','c::content_sha256(payload)'),('c::sha256(asset.second)','c::content_sha256(asset.second)')],
 'tests/scene/image_fixture.hpp':[('c::sha256(bytes)','c::content_sha256(bytes)')],
 'tests/scene/image_surface_tests.cpp':[('c::sha256(bytes)','c::content_sha256(bytes)')],
}.items():
 p=r/name;t=p.read_text()
 for a,b in replacements:assert a in t;t=t.replace(a,b)
 p.write_text(t,encoding='utf-8',newline='\n')
p=r/'tests/configuration/authored_tests.cpp';t=p.read_text();mark='void digest(){';assert mark in t
t=t.replace(mark,'''void content_digest(){
    std::ifstream stream(fixtures+"/../../../tests/configuration/content-digests.json");Json cases;stream>>cases;
    for(const auto& c:cases)CHECK(c::content_sha256(std::string(c["bytes"].get<std::size_t>(),'a'))==c["sha256"]);
    rejected([]{c::sha256(std::string(1048577,'a'));});rejected([]{c::content_sha256(std::string(16777217,'a'));});
}
'''+mark).replace('else if(name=="DIGEST")digest();','else if(name=="DIGEST")digest();else if(name=="DIGEST-CONTENT")content_digest();')
p.write_text(t,encoding='utf-8',newline='\n')
p=r/'CMakeLists.txt';t=p.read_text().replace('TX-CAPACITY DIGEST CONTENT','TX-CAPACITY DIGEST DIGEST-CONTENT CONTENT');p.write_text(t,encoding='utf-8',newline='\n')
p=r/'tests/configuration/native_content_commands.py';t=p.read_text().replace("{'images/pixel.png':b'opaque media bytes\\x00unchanged'}", "{'images/pixel.png':b'a'*1048577 if name=='LARGE-RESOURCE' else b'opaque media bytes\\x00unchanged'}")
t=t.replace("('NORMAL-RETAINED','POLICY-DENY','RETAINED-ONLY')", "('NORMAL-RETAINED','POLICY-DENY','RETAINED-ONLY','LARGE-RESOURCE')").replace("if name=='NORMAL-RETAINED':", "if name in ('NORMAL-RETAINED','LARGE-RESOURCE'):")
t=t.replace("'CATALOG-REJECTION'):run(name)","'CATALOG-REJECTION','LARGE-RESOURCE'):run(name)")
p.write_text(t,encoding='utf-8',newline='\n')
with zipfile.ZipFile(d/'resource-native-original.zip','x',zipfile.ZIP_DEFLATED) as z:z.write(p,p.relative_to(r).as_posix())
(d/'resource-native-original.json').write_text(json.dumps({p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8',newline='\n')
