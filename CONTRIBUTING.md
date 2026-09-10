# Contributing to RapidPro

Contributions to the RapidPro projects are highly appreciated! 

We accept contributions in the form of:
 * Bug reports 
 * Pull requests for code changes
 * Documentation updates

All non-trivial pull requests, especially those with functional changes should first open a ticket to discuss approach 
and likelihood of inclusion in the project.

Note that all pull requests must:

 * Pass all unit tests
 * Maintain 100% unit test coverage (without new no-covers)
 * Pass the code quality checks (ruff etc)

Install the git hooks with `pre-commit install` so the checks run automatically on commit. You can also run
`pre-commit run --all-files` to check the whole repository, or `code_check.py` to additionally check for missing
migrations.

RapidPro is licensed under the AGPL-3.0 and your contributions will be licensed in the same way. Note that contributing 
does not change your rights to use your own Contributions for any other purpose.
