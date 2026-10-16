// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 N1-k0-la1
#include "diting_ota_aliases.h"
#include <cassert>
#include <iostream>
#include <vector>
int main() {
    struct Case { const char* device; const char* package; const char* aliases; bool allowed; };
    const std::vector<Case> cases = {
        {"diting", "ditingp", "diting,ditingp", true},
        {"ditingp", "diting", "diting,ditingp", true},
        {"ditingp", "diting|ditingp", "diting,ditingp", true},
        {"diting", "diting", "ditingp,diting", true},
        {"raphael", "diting", "diting,ditingp", false},
        {"diting", "raphael", "diting,ditingp", false},
        {"diting", "", "diting,ditingp", false},
        {"ditingp", "diting", "diting", false},
        {"diting", "ditingp", "", false},
        {"diting", "ditingpro", "diting,ditingp", false},
        {"diting", "notditing|raphael", "diting,ditingp", false},
        {"", "diting", "diting,ditingp", false},
        {"diting", "ditingp", "diting, ditingp", true},
        {"ditingp", " diting \r\n", " diting ,\tditingp\r\n", true},
        {"diting", "other |\tditingp \r", "diting,\tditingp", true},
        {"diting", "diting_other", "diting, ditingp", false},
        {"diting", "ditingp_other", "diting, ditingp", false},
        {"diting", "other|notditingp", "diting, ditingp", false},
        {"diting", "ditingp", "diting, ditingp_other", false},
        {" diting", "ditingp", "diting,ditingp", false},
        {"diting", "  \t\r\n", "diting,ditingp", false},
        {"ditingp", "diting", ",diting,,\tditingp,", true},
    };
    for (const auto& c : cases) {
        assert(diting_recovery::PackageUsesDitingAlias(c.device, c.package, c.aliases) == c.allowed);
    }
    assert(!diting_recovery::HasToken("", '|', ""));
    assert(!diting_recovery::HasToken("diting_other", '|', "diting"));
    std::cout << cases.size() << " device alias acceptance/rejection cases passed\n";
}
