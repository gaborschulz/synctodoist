#!/bin/zsh

start=$(date +%s)
VERSION_BUMPED=0

load_env() {
    if [ -f .env ]; then
        echo "Loading .env file"
        export $(cat .env | xargs)
    fi

    echo "Project: $PROJECT_NAME"
}

run_test() {
    pytest
}

cleanup() {
    find . -type d -name "@eaDir" -print0 | xargs -0 rm -rf
}

bump_version() {
    echo "Argument: $1 / $#"
    if [[ "$#" -eq 0 ]]; then
        echo "No version bump"
        VERSION_BUMPED=0
        return 0
    fi

    echo "Bumping version from $(poetry version)"
    poetry version $1 &&
        poetry version &&
        git commit -am "Committing version $(poetry version --short)" &&
        git tag -a v$(poetry version --short) -m "Tagging version $(poetry version --short)"
    VERSION_BUMPED=1
}

push() {
    coverage-badge -o coverage.svg -f
    git push origin v$(poetry version --short)
}

release_to_pypi() {
    if [[ $VERSION_BUMPED == 0 ]]; then
        echo "No PyPI release without version bump"
    fi

    poetry publish --build
}

load_env &&
cleanup &&
run_test &&
bump_version $1 &&
push &&
release_to_pypi

end=$(date +%s)
runtime=$((end - start))

echo "Elapsed time: $runtime s"
