#pragma once
#include "authored.hpp"
namespace syspane::configuration {
// Equality for validated authored values, including exact mixed numeric values.
// Unlike JSON library equality, signed/unsigned and integer/real never wrap or round.
bool authored_equal(const Json& left,const Json& right);
}
