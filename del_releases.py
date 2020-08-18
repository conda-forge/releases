import os
import github

gh = github.Github(os.environ["GITHUB_TOKEN"])

repo = gh.get_repo("regro/releases")

for ref in repo.get_git_refs():
    if "tag" in ref.ref:
        ref.delete()

for rel in repo.get_releases():
    rel.delete_release()
