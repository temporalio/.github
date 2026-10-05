# Temporal organization GitHub configuration

Temporal's default community health files and shared GitHub Actions workflows.
See GitHub's documentation on
[default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
and [reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).


## What is this

This is the default file for all Temporal OSS repos. Primarily we offer:

- 2 basic issue templates, covering Bug Report and Feature Requests
- 1 PR template, reminding the contributor to file an issue first
- Shared workflows for checks used across multiple Temporal repositories
- in future, we may add [CONTRIBUTING.md](https://github.com/OctoPrint/OctoPrint/blob/master/CONTRIBUTING.md?WT.mc_id=-blog-scottha) and SECURITY.md

## Shared workflows

`changelog.yml` verifies that a pull request adds to a `CHANGELOG.md` only
within its Unreleased section. Repositories retain a small caller workflow so
label changes can rerun the check and the `skip-changelog` override remains
available. Callers grant `contents: read` for checkout and `pull-requests: read`
so the shared workflow can read the pull request's current labels.

`changelog-fragments.yml` is the alternative for SDKs migrating to per-PR
Markdown fragments. It uses the caller's pinned sdk-rust `changelog-tool`, requires
a new fragment in a category folder, and validates pending fragments. The existing
`changelog.yml` remains available for repositories that have not migrated.

Pass `sdk-rust-path` (the submodule path, or `.` in sdk-rust itself) and optionally
`fragments-directory` (default `changelog`). Callers retain the pull request event
types `opened`, `synchronize`, `reopened`, `labeled`, and `unlabeled`, the same read
permissions, and the `skip-changelog` override. Pin the workflow to a reviewed
commit, and update the caller's sdk-rust pin to a revision containing the tool
before switching workflows.


## Why do this

The goal of this is to make a small nudge to improve our OSS community submissions, and set public expectations on PRs.

## Internal instructions

To Temporal employees: You can override this behavior on a per-repo basis, simply by making another file with the same names in side of your repo. [More details in GitHub's docs](https://docs.github.com/en/github/building-a-strong-community/creating-a-default-community-health-file).

You can also improve your issue triage by [using saved replies](https://docs.github.com/en/github/writing-on-github/creating-a-saved-reply) to [close issues with a polite and reasonable tone](https://blog.jessfraz.com/post/the-art-of-closing/).


## Acknowledgements

Thanks to https://github.com/stevemao/github-issue-templates for our base templates.
