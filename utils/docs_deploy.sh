
set -e

travis login --github-token

mkdocs gh-deploy
