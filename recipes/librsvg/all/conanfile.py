from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.60.0 <2.0 || >=2.0.6"


class LibrsvgConan(ConanFile):
    name = "librsvg"
    description = "A library to render SVG images to Cairo surfaces."
    license = "LGPL-2.1-or-later"
    topics = ("svg", "render", "cairo")
    homepage = "https://wiki.gnome.org/Projects/LibRsvg"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "avif": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "avif": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # librsvg is a C library (Rust internals are statically linked)
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires(
            "cairo/[>=1.18.0 <2]", transitive_headers=True, transitive_libs=True
        )
        self.requires(
            "glib/[>=2.78.3 <3]", transitive_headers=True, transitive_libs=True
        )
        self.requires("freetype/[>=2.13.0 <3]")
        self.requires("harfbuzz/[>=2.0.0 <13]")
        self.requires("libxml2/[>=2.9.0 <3]")
        self.requires("pango/[>=1.50.0 <2]")
        self.requires("fontconfig/[>=2.15.0 <3]")
        self.requires("gdk-pixbuf/[>=2.44.4 <3]")
        if self.options.avif:
            self.requires("dav1d/[>=1.3.0 <2]")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        self.tool_requires("cargo/[~1]@frontify/stable")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            f"--enable-avif={yes_no(self.options.avif)}",
            "--disable-gtk-doc",
            f"--enable-debug={yes_no(self.settings.build_type == 'Debug')}",
            "--disable-introspection",
            "--disable-pixbuf",
            "--disable-pixbuf-loader",
            "--disable-vala",
        ]
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(
            self,
            "COPYING",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "librsvg-2.0")
        self.cpp_info.libs = ["rsvg-2"]
        self.cpp_info.includedirs = [os.path.join("include", "librsvg-2.0")]
        self.cpp_info.requires = [
            "cairo::cairo_",
            "cairo::cairo-png",
            "cairo::cairo-gobject",
            "fontconfig::fontconfig",
            "freetype::freetype",
            "glib::gio-2.0",
            "glib::glib-2.0",
            "glib::gobject-2.0",
            "harfbuzz::harfbuzz",
            "libxml2::libxml2",
            "pango::pangocairo",
            "pango::pangoft2",
            "gdk-pixbuf::gdk-pixbuf",
        ]
        if self.options.avif:
            self.cpp_info.requires.append("dav1d::dav1d")
