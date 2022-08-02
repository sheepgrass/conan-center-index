from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get
from conan.tools.scm import Version
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class CppProjectFrameworkConan(ConanFile):
    name = "cpp_project_framework"
    license = "AGPL-3.0"
    homepage = "https://github.com/sheepgrass/cpp_project_framework"
    url = "https://github.com/conan-io/conan-center-index"  # Package recipe repository url here, for issues about the package
    description = "C++ Project Framework is a framework for creating C++ project."
    topics = ("c++", "project", "framework")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "%s/*" % name, "test_package/*.*"
    build_requires = "gtest/1.10.0", "doxygen/1.8.20", "benchmark/1.5.1"

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.os != "Linux" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"{self.name} is just supported for Linux and Windows")

        compiler = self.settings.compiler

        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        if compiler == "gcc" or compiler == "clang":
            if compiler.get_safe("libcxx") != "libstdc++":
                raise ConanInvalidConfiguration(f"only supported {compiler} with libstdc++")

        min_version = self._minimum_compilers_version.get(str(compiler))
        if not min_version:
            self.output.warn(f"{self.name} recipe lacks information about the {compiler} compiler support.")
        else:
            if Version(compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"{self.name} requires C++{self._minimum_cpp_standard} support. The current compiler {compiler} {compiler.version} does not support it.")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include/%s" % self.name, src=os.path.join(self._source_subfolder, self.name))

    def package_id(self):
        self.info.header_only()
