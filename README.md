# Minidump Upload Example

A tool that will download and re-upload minidump and event payloads to Sentry with
compression built with the Sentry Python SDK.

## Installation

It is recommended to install dependencies in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

To reprocess an event, export the `SENTRY_DSN`,`BEARER_TOKEN`,and `ORG_SLUG` environment variables and call the script
with the issue id for the event you'd like to reprocess as well as the project slug for this issue. This will download 
the latest event in the issue and if it has a minidump attached to it, its minidump. Then, the event and 
(where applicable) its minidump, will be compressed via the Sentry Python SDK and uploaded to the project chosen via the
`SENTRY_DSN` inputted. 

```bash
export SENTRY_DSN="..."
export BEARER_TOKEN="..."
export ORG_SLUG="..."
./upload.py <issue ID to reprocess> <project slug for event> [<event id to reprocess>]
```

The script prints out the event ID of a new error event that will be created
through the upload.

The script takes an optional event id as a third parameter. This is useful if there is a specific event that you would
like to be reprocessed, or a minidump specific to a certain event. 

```bash
export SENTRY_DSN="..."
export BEARER_TOKEN="..."
export ORG_SLUG="..."
./upload.py <issue ID to reprocess> <project slug for event> [<event id to reprocess>]
```
