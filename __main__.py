"""A GitHub Python Pulumi program"""

import pulumi
import pulumi_github as github
from pyhocon import ConfigFactory

conf = ConfigFactory.parse_file("hocon.config")

# Create a GitHub repository
repo = github.Repository(conf.repo.name, description=conf.repo.description, name=conf.repo.name, auto_init=True)


# Create the required branches
branch_names = conf.branches
branches = {}
for branch_name in branch_names:
    branch = github.Branch(branch_name,
                    repository=repo.name,
                    branch=branch_name,
                    source_branch="main")
    branches[branch_name] = branch

default_branch = github.BranchDefault("default_branch", repository=repo.name, branch=conf.default_branch, opts=pulumi.ResourceOptions(depends_on=[branches[conf.default_branch]]))

# Apply branch protection and rules for dev, stage, and prod branches
protected_branches = ["dev", "stage", "prod"]

for protected_branch in protected_branches:
    github.BranchProtection(f"{protected_branch}-protection",
                       repository_id=repo.name,
                       pattern=protected_branch,
                       enforce_admins=True,
                       allows_force_pushes=False,
                       required_pull_request_reviews=[
                           {
                           "required_approving_review_count": 0,
                           "dismiss_stale_reviews": True,
                           "require_code_owner_reviews": False,
                           }
                       ])

# Export the Name of the repository
pulumi.export('name', repo.name)
