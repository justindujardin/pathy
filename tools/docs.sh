#!/bin/bash
set -e
. .env/bin/activate
mathy_pydoc pathy.Pathy+ pathy.BlobStat+ pathy.use_fs pathy.get_fs_client pathy.use_fs_cache pathy.get_fs_cache > /tmp/pathy_api.md
typer pathy.cli utils docs > /tmp/pathy_cli.md

python tools/docs.py /tmp/pathy_api.md /tmp/pathy_cli.md README.md
npx prettier README.md --write