# SPDX-FileCopyrightText: 2022 Gregory Clunies <greg@reflekt-ci.com>
#
# SPDX-License-Identifier: Apache-2.0


class AmplitudeApi:
    # fmt: off
    """API class to pass tracking plan docs and metadata to Amplitude's
    Taxonomy API. In particular, the ability to update Event properties in
    Amplitude to ensure they are consistent with the tracking plan.

    Amplitude docs:
    https://developers.amplitude.com/docs/taxonomy-api#update-an-event-property
    """
    # fmt: on
