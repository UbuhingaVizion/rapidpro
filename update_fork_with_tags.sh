# Repo: someuser/myframework
# Fork: superteam/myframework

# Track:
git clone git@github.com:UbuhingaVizion/rapidpro.git
cd rapidpro
git remote add upstream https://github.com/rapidpro/rapidpro.git

# Update:
git fetch upstream
git rebase upstream/master
git push
git push --tags