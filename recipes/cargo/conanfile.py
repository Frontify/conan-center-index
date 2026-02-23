from conan import ConanFile


class CargoConan(ConanFile):
    name = "cargo"
    version = "1.0"
    implements = ["auto_header_only"]

    def package_info(self):
        self.buildenv_info.prepend_path("PATH", "$HOME/.cargo/bin")
