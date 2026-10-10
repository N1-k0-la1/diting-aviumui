// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 N1-k0-la1
#include "diting_ota_aliases.h"
#include <cassert>
#include <iostream>
int main() {
    using diting_recovery::PackageUsesDitingAlias;
    const std::string aliases="diting,ditingp";
    assert(PackageUsesDitingAlias("diting", "ditingp", aliases));
    assert(PackageUsesDitingAlias("ditingp", "diting", aliases));
    assert(PackageUsesDitingAlias("ditingp", "diting|ditingp", aliases));
    assert(PackageUsesDitingAlias("diting", "diting", "ditingp,diting"));
    assert(!PackageUsesDitingAlias("raphael", "diting", aliases));
    assert(!PackageUsesDitingAlias("diting", "raphael", aliases));
    assert(!PackageUsesDitingAlias("diting", "", aliases));
    assert(!PackageUsesDitingAlias("ditingp", "diting", "diting"));
    assert(!PackageUsesDitingAlias("diting", "ditingp", ""));
    assert(!PackageUsesDitingAlias("diting", "ditingpro", aliases));
    assert(!PackageUsesDitingAlias("diting", "notditing|raphael", aliases));
    assert(!PackageUsesDitingAlias("", "diting", aliases));
    std::cout << "12 device alias acceptance/rejection cases passed\n";
}
