import os
import json
import tempfile
import subprocess

import github

with open(os.environ["GITHUB_EVENT_PATH"], 'r') as fp:
    event_data = json.load(fp)

event_name = os.environ['GITHUB_EVENT_NAME'].lower()

print("event_name:", event_name, flush=True)

gh = github.Github(os.environ["GITHUB_TOKEN"])
repo = gh.get_repo("regro/releases")

sha = subprocess.run(
    "git rev-parse --verify HEAD",
    shell=True,
    capture_output=True,
).stdout.decode("utf-8").strip()

subdir = event_data['client_payload']["subdir"]
pkg = event_data['client_payload']["package"]
sha256 = event_data["client_payload"]["repodata-shard"]["repodata"]["sha256"]
print("subdir/package: %s/%s" % (subdir, pkg), flush=True)
print("sha256:", sha256, flush=True)

url = f"https://conda.anaconda.org/conda-forge/{subdir}/{pkg}"

with tempfile.TemporaryDirectory() as tmpdir:
    subprocess.run(
        f"curl -L {url} > {tmpdir}/{pkg}",
        shell=True,
    )

    rel = repo.create_git_tag_and_release(
        sha256,
        "",
        f"{subdir}/{pkg}",
        "",
        sha,
        "commit",
    )

    rel.upload_asset(
        f"{tmpdir}/{pkg}",
        content_type="application/x-bzip2",
    )
