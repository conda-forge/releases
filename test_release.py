import os
import github

fname = "linux-64/cf-autotick-bot-test-package-0.9-py36h9f0ad1d_172.tar.bz2"

subdir, pkg = os.path.split(fname)

gh = github.Github(os.environ["GITHUB_TOKEN"])

repo = gh.get_repo("regro/releases")

repo.create_repository_dispatch(
    "release",
    {
        "subdir": subdir,
        "package": pkg,
        "url": f"https://conda.anaconda.org/conda-forge/{subdir}/{pkg}",
    }
)
