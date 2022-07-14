from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake
import os

required_conan_version = ">=1.33.0"


class CppProjectFrameworkConan(ConanFile):
    name = "cpp_project_framework"
    license = "GNU Affero General Public License v3.0"
    homepage = "https://github.com/sheepgrass/cpp_project_framework"
    url = "https://github.com/conan-io/conan-center-index"  # Package recipe repository url here, for issues about the package
    description = "C++ Project Framework is a framework for creating C++ project."
    topics = ("c++", "project", "framework")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"
    short_paths = True
    exports_sources = "%s/*" % name, "test_package/*.*"
    build_requires = "gtest/1.10.0", "doxygen/1.8.20", "benchmark/1.5.1"
    exports_resources = ".gitignore", "LICENSE", "conanfile.txt", "CMakeLists.txt", "make.bat", "Makefile", "cpp_project_framework_callables.cmake", "cpp_project_framework.cmake"

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "17",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.os != "Linux" and self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"{self.name} is just supported for Linux and Windows")

        compiler = self.settings.compiler

        if compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)

        if compiler == "gcc" or compiler == "clang":
            if compiler.get_safe("libcxx") == "libstdc++11":
                raise ConanInvalidConfiguration(f"{compiler} with libstdc++11 not supported")

        min_version = self._minimum_compilers_version.get(str(compiler))
        if not min_version:
            self.output.warn(f"{self.name} recipe lacks information about the {compiler} compiler support.")
        else:
            if tools.Version(compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"{self.name} requires C++{self._minimum_cpp_standard} support. The current compiler {compiler} {compiler.version} does not support it.")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        self.run("conan install conanfile.txt -b missing -s build_type=%s -if ." % cmake.build_type, cwd=self._source_subfolder)
        cmake.configure(source_folder=self._source_subfolder, build_folder=os.path.join(self._source_subfolder, cmake.build_type))
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/cpp_project_framework %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include/%s" % self.name, src=os.path.join(self._source_subfolder, self.name))
        self.copy("*.hpp", dst="include/%s" % self.name, src=os.path.join(self._source_subfolder, self.name))
        self.copy("*.hxx", dst="include/%s" % self.name, src=os.path.join(self._source_subfolder, self.name))
        for resource in self.exports_resources:
            self.copy(resource, dst="res", src=self._source_subfolder)

    def package_info(self):
        postfix = "_d" if self.settings.build_type == "Debug" else ""
        name_with_postfix = self.name + postfix
        self.cpp_info.libs = []
