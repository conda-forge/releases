import os
import json
import tempfile
import subprocess
import uuid
import copy

import github


def make_repodata_shard(subdir, pkg, label, feedstock, url, tmpdir):
    os.makedirs(f"{tmpdir}/noarch", exist_ok=True)
    os.makedirs(f"{tmpdir}/{subdir}", exist_ok=True)
    subprocess.run(
        f"curl -L {url} > {tmpdir}/{subdir}/{pkg}",
        shell=True
    )
    subprocess.run(
        f"conda index --no-progress {tmpdir}",
        shell=True
    )

    with open(f"{tmpdir}/channeldata.json", "r") as fp:
        cd = json.load(fp)

    with open(f"{tmpdir}/{subdir}/repodata.json", "r") as fp:
        rd = json.load(fp)

    shard = {}
    shard["labels"] = [label]
    shard["repodata_version"] = rd["repodata_version"]
    shard["repodata"] = rd["packages"][pkg]
    shard["subdir"] = subdir
    shard["package"] = pkg
    shard["url"] = url
    shard["feedstock"] = feedstock

    # we are hacking at this
    shard["channeldata_version"] = cd["channeldata_version"]
    shard["channeldata"] = copy.deepcopy(
        cd["packages"][rd["packages"][pkg]["name"]]
    )
    shard["channeldata"]["subdirs"] = [subdir]
    shard["channeldata"]["version"] = rd["packages"][pkg]["version"]

    return shard


if __name__ == "__main__":
    with open(os.environ["GITHUB_EVENT_PATH"], 'r') as fp:
        event_data = json.load(fp)

    event_name = os.environ['GITHUB_EVENT_NAME'].lower()

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

    url = f"https://conda.anaconda.org/conda-forge/{subdir}/{pkg}"

    uid = uuid.uuid4().hex

    with tempfile.TemporaryDirectory() as tmpdir:
        shard = make_repodata_shard(subdir, pkg, "main", "blah", url, tmpdir)

        rel = repo.create_git_tag_and_release(
            f"{uid}/{subdir}/{pkg}",
            "",
            f"{subdir}/{pkg}",
            "",
            sha,
            "commit",
        )

        rel.upload_asset(
            f"{tmpdir}/{subdir}/{pkg}",
            content_type="application/x-bzip2",
        )

        with open(f"{tmpdir}/repodata_shard.json", "w") as fp:
            json.dump(shard)

        rel.upload_asset(
            f"{tmpdir}/repodata_shard.json",
            content_type="application/json",
        )
