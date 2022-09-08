#!/usr/bin/env python3

import os
import sys
import uuid
import requests
import sentry_sdk
from sentry_sdk.envelope import Envelope, Item


SAFE_FIELDS = (
    "breadcrumbs",
    "contexts",
    "dist",
    "environment",
    "extra",
    "logentry",
    "message",
    "release",
    "request",
    "sdk",
    "tags",
    "user",
)

def main():

    ORG_SLUG = os.getenv("ORG_SLUG") or "adobe-inc"
    if len(sys.argv) < 2:
        print("Usage: upload.py <issue ID to reprocess> <project slug for event> [<event_id to reprocess>]")
        return 1
    BEARER_TOKEN = os.getenv("BEARER_TOKEN")
    if not BEARER_TOKEN:
        BEARER_TOKEN = input("Error: Please Enter Bearer Token\n")
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    if not SENTRY_DSN:
        SENTRY_DSN = input("Error: Please Enter Sentry DSN\n")
    issue_id = sys.argv[1] if len(sys.argv) > 1 else input("Enter the issue ID you would like to reprocess:")
    project_input = sys.argv[2] if len(sys.argv) > 2 else input("Ente r the project slug for the event:")
    event_id = sys.argv[3] if len(sys.argv) > 3 else requests.get('https://sentry.io/api/0/issues/{}/events/?limit=50&query='.format(issue_id), headers={"Authorization":"Bearer {}".format(BEARER_TOKEN)}).json()[0]['id']

    event = requests.get('https://sentry.io/api/0/projects/{}/{}/events/{}/json/'.format(ORG_SLUG,project_input,event_id), headers={"Authorization":"Bearer {}".format(BEARER_TOKEN)}).json()
    attachments = requests.get('https://sentry.io/api/0/issues/{}/attachments/'.format(issue_id), headers={"Authorization":"Bearer {}".format(BEARER_TOKEN)}).json()
    dump_name = ""
    attachment_for_event = False
    for attachment in attachments:
        if attachment['type'] == 'event.minidump' and attachment['event_id'] == event_id:
            dump_name = attachment['name']
            minidump = requests.get('https://sentry.io/api/0/projects/{}/{}/events/{}/attachments/{}/?download=1'.format(ORG_SLUG,project_input,event_id,attachment['id']), headers={"Authorization":"Bearer {}".format(BEARER_TOKEN)}).content
            attachment_for_event = True
            break
        continue

    event_id = uuid.uuid4().hex
    envelope = Envelope(headers={"event_id": event_id})
    if attachment_for_event:
        envelope.add_item(Item(
            payload=minidump,
            type="attachment",
            filename=dump_name,
            headers={"attachment_type": "event.minidump"}
        ))
    if event:
        if not isinstance(event, dict):
            print("Error: Event data is not a dictionary")
            return 1

        event_data = {k: v for k, v in event.items() if k in SAFE_FIELDS}
        envelope.add_event(event_data)

    sentry_sdk.init(dsn=SENTRY_DSN, default_integrations=False, shutdown_timeout=15)
    sentry_sdk.Hub.current.client.transport.capture_envelope(envelope)
    sentry_sdk.flush()

    print(event_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
