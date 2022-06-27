# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0

from tests.fixtures.reflekt_event import REFLEKT_EVENT
from tests.fixtures.reflekt_groups import REFLEKT_GROUPS
from tests.fixtures.reflekt_plan import REFLEKT_PLAN
from tests.fixtures.reflekt_users import REFLEKT_USERS


def build_reflekt_plan_dir(
    tmp_dir,
    plan_fixture=REFLEKT_PLAN,
    event_fixture=REFLEKT_EVENT,
    users_fixture=REFLEKT_USERS,
    groups_fixture=REFLEKT_GROUPS,
):
    plan_dir = tmp_dir.mkdir("tracking-plans").mkdir("test-plan")
    create_reflekt_plan(plan_dir, plan_fixture)
    create_reflekt_users(plan_dir, users_fixture)
    create_reflekt_groups(plan_dir, groups_fixture)
    create_reflekt_event(plan_dir, event_fixture)

    return plan_dir


def create_reflekt_plan(tmp_dir, plan_fixture=REFLEKT_PLAN):
    r_prop = tmp_dir / "plan.yml"
    r_prop.write(plan_fixture)


def create_reflekt_event(tmp_dir, event_fixture=REFLEKT_EVENT):
    r_event = tmp_dir.mkdir("events") / "test-event.yml"
    r_event.write(event_fixture)


def create_reflekt_users(tmp_dir, users_fixture=REFLEKT_USERS):
    r_identify = tmp_dir / "user-traits.yml"
    r_identify.write(users_fixture)


def create_reflekt_groups(tmp_dir, groups_fixture=REFLEKT_GROUPS):
    r_group = tmp_dir / "group-traits.yml"
    r_group.write(groups_fixture)
