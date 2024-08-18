#!/bin/zsh

start=$(date +%s)
VERSION_BUMPED=0

RED="\033[1;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;34m"
PURPLE="\033[1;35m"
CYAN="\033[1;36m"
WHITE="\033[1;37m"
RESET="\033[0m"

QUESTION_FLAG="${GREEN}?"
WARNING_FLAG="${YELLOW}!"
NOTICE_FLAG="${CYAN}❯"

load_env() {
    if [ -f .env ]; then
        echo "Loading .env file"
        export $(cat .env | xargs)
    fi

    echo "Project: $PROJECT_NAME"
}

run_test() {
    pytest --cov=. --cov-report xml -s && \
    coverage-badge -o coverage.svg -f
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
    poetry version $1 && \
    poetry version && \

    COMMIT_MESSAGE="Committing version $(poetry version --short)" && \
    echo -ne "${QUESTION_FLAG} ${CYAN}Enter a custom commit/release message [${WHITE}$COMMIT_MESSAGE${CYAN}]: "
    read INPUT_STRING
    if [ "$INPUT_STRING" = "" ]; then
        INPUT_STRING=$COMMIT_MESSAGE
    fi

    git commit -am "$INPUT_STRING" && \
    git tag -a v$(poetry version --short) -m "$INPUT_STRING" && \

    git push && \
    git push origin v$(poetry version --short) && \
    VERSION_BUMPED=1
}

push() {
    git push && \
    git push origin v$(poetry version --short)
}

release_to_pypi() {
    if [[ $VERSION_BUMPED == 0 ]]; then
        echo "No PyPI release without version bump"
    fi

    poetry publish --build
    gh release create v$(poetry version --short) --generate-notes
}

load_env &&
cleanup &&
# run_test &&
bump_version $1 &&
push &&
release_to_pypi

end=$(date +%s)
runtime=$((end - start))

echo "Elapsed time: $runtime s"
