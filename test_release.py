import os
import time
import github
import tqdm

fname = "linux-64/cf-autotick-bot-test-package-0.9-py36h9f0ad1d_172.tar.bz2"

subdir, pkg = os.path.split(fname)

gh = github.Github(os.environ["GITHUB_TOKEN"])

repo = gh.get_repo("regro/releases")

for _ in tqdm.trange(10000):
    repo.create_repository_dispatch(
        "release",
        {
            "subdir": subdir,
            "package": pkg,
            "repodata-shard": {"repodata": {"sha256": "blah"}},
        }
    )
    time.sleep(1)
