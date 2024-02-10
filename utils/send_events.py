import csv
import os
from datetime import datetime
from pathlib import Path

import rudderstack.analytics as rudderstack
import segment.analytics as segment
from amplitude import Amplitude

# By default, don't send events to any CDP
send_to_segment = False
send_to_rudderstack = False
send_to_amplitude = False

# Get CDP configs from environment variables
# Comment out CDP config if you don't want to send events to that CDP
cdps = [
    {
        "name": "segment",
        "write_key": os.getenv("JAFFLE_SEGMENT_WRITE_KEY"),
    },
    # {
    #     "name": "rudderstack",
    #     "write_key": os.getenv("JAFFLE_RUDDERSTACK_WRITE_KEY"),
    #     "dataPlaneUrl": os.getenv("JAFFLE_RUDDERSTACK_DATA_PLANE_URL"),
    # },
    # {
    #     "name": "amplitude",
    #     "api_key": os.getenv("JAFFLE_AMPLITUDE_API_KEY"),
    # },
]

# Initialize SDKs for each cdp in cdps list.
for cdp in cdps:
    if cdp["name"] == "segment":
        send_to_segment = True
        segment.write_key = cdp["write_key"]
    elif cdp["name"] == "rudderstack":
        send_to_rudderstack = True
        rudderstack.write_key = cdp["write_key"]
        rudderstack.dataPlaneUrl = cdp["dataPlaneUrl"]
    elif cdp["name"] == "amplitude":
        send_to_amplitude = True
        amplitude = Amplitude(cdp["api_key"])


def csv_to_cdp(cdp: str, row):
    """Write event from CSV row to Customer Data Platform (CDP).

    Args:
        cdp (_type_): _description_
        row (_type_): _description_
    """
    if cdp == "segment":
        if str.lower(row["event"]) == "identify":  # identify() calls
            segment.identify(
                user_id=row["user_id"],
                traits=row["properties"],
                context={
                    "page": {
                        "url": row["page"]["url"],
                        "path": row["page"]["path"],
                        "title": row["page"]["title"],
                        "search": row["page"]["search"],
                        "referrer": row["page"]["referrer"],
                    }
                },
                timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
            )
        elif str.lower(row["event"]) == "page viewed":  # page() calls
            segment.page(
                user_id=row["user_id"],
                name=row["page"]["name"],
                properties=row["properties"],
                context={
                    "page": {
                        "url": row["page"]["url"],
                        "path": row["page"]["path"],
                        "title": row["page"]["title"],
                        "search": row["page"]["search"],
                        "referrer": row["page"]["referrer"],
                    }
                },
                timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
            )
        elif str.lower(row["event"]) == "drop":  # Dummy event for debugging
            pass
        else:  # track() calls
            segment.track(
                user_id=row["user_id"],
                event=row["event"],
                properties=row["properties"],
                context={
                    "page": {
                        "url": row["page"]["url"],
                        "path": row["page"]["path"],
                        "title": row["page"]["title"],
                        "search": row["page"]["search"],
                        "referrer": row["page"]["referrer"],
                    }
                },
                timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S.%f"),
            )

    elif cdp == "rudderstack":
        pass  # TODO: Implement rudderstack event sending

    elif cdp == "amplitude":
        pass  # TODO: Implement amplitude event sending


if __name__ == "__main__":
    # Get CSV file with jaffle shop events
    events_file = Path.cwd() / "utils" / "jaffle_events.csv"

    # Read events from CSV and send to CDPs
    with events_file.open() as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            print(row)

            if send_to_segment:
                csv_to_cdp("segment", row)
            if send_to_rudderstack:
                csv_to_cdp("rudderstack", row)
            if send_to_amplitude:
                csv_to_cdp("amplitude", row)
