#include "nlohmann/json.hpp"
#include <iostream>
int main(){using J=nlohmann::json;const auto integer=J::parse("18446744073709551615");const auto real=J::parse("18446744073709551616.0");const auto low=J::parse("9007199254740993");const auto rounded=J::parse("9007199254740992.0");std::cout<<J{{"integer",integer},{"real",real},{"library_equal",integer==real},{"nested_library_equal",J{{"value",integer}}==J{{"value",real}}},{"2pow53_library_equal",low==rounded},{"signed_unsigned_equal",J(-1)==integer}}.dump(2)<<'\n';}
