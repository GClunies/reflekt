# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from reflekt.property import ReflektProperty


# Traits behave the same way as properties, but traits capture attributes of a
# user, not an event.
class ReflektTrait(ReflektProperty):
    pass
