#!/bin/bash -e
# shellcheck source=/dev/null

root_dir="$(realpath "$(dirname "$0")")"

if ! conan --version > /dev/null 2>&1
then
    if ! source "${root_dir}/.venv-conan/bin/activate"
    then
        python3 -m venv "${root_dir}/.venv-conan"
        source "${root_dir}/.venv-conan/bin/activate"
        python -m pip install "conan<4.0"
    fi
fi

user="frontify"
channel="stable"

conan export "${root_dir}/recipes/cargo" --version 1.0 --user "${user}" --channel "${channel}"
conan export "${root_dir}/recipes/librsvg/all" --version 2.58.5 --user "${user}" --channel "${channel}"
conan export "${root_dir}/recipes/libvips/all" --version 8.15.2 --user "${user}" --channel "${channel}"
conan export "${root_dir}/recipes/ffmpeg/all" --version 8.1.0 --user "${user}" --channel "${channel}"
