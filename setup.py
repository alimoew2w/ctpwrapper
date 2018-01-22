# encoding:utf-8
import codecs
import os
import re
import shutil
import sys
from distutils.core import setup
from distutils.dir_util import copy_tree

from Cython.Build import cythonize
from Cython.Distutils import build_ext, Extension


def find_version(*file_paths):
    """
    Don't pull version by importing package as it will be broken due to as-yet uninstalled
    dependencies, following recommendations at  https://packaging.python.org/single_source_version,
    extract directly from the init file
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *file_paths), 'r', encoding="utf-8") as f:
        version_file = f.read()

    # The version line must have the form
    # __version__ = 'ver'
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


base_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(base_dir, "ctpwrapper")
ctp_dir = os.path.join(base_dir, "ctp")
cython_headers = os.path.join(project_dir, "headers")
header_dir =[os.path.join(ctp_dir, "header")]
header_dir.append(os.path.join(project_dir,"ctpwrapper/include"))
header_dir.append(os.path.join(project_dir,"ctpwrapper"))
lib_dir = None
package_data = ["*.xml", "*.dtd"]
extra_link_args = None
extra_compile_args = None

if sys.platform == "linux":
    lib_dir = os.path.join(ctp_dir, "linux")
    package_data.append("*.so")
    extra_compile_args = ["-Wall"]
    extra_link_args = ['-Wl,-rpath,$ORIGIN']

elif sys.platform == "win32":
    lib_dir = os.path.join(ctp_dir, "win")
    extra_compile_args = ["/GR", "/EHsc"]
    # extra_link_args = []
    package_data.append("*.dll")

package_data.append("error.dtd")
package_data.append("error.xml")
shutil.copy2(header_dir + "/error.dtd", project_dir + "/error.dtd")
shutil.copy2(header_dir + "/error.xml", project_dir + "/error.xml")
copy_tree(lib_dir, project_dir)

common_args = {
    "cython_include_dirs": [cython_headers],
    "include_dirs": header_dir,
    "library_dirs": [lib_dir],
    "language": "c++",
    "extra_compile_args": extra_compile_args,
    "extra_link_args": extra_link_args,
}

ext_modules = [
    Extension(name="ctpwrapper.MdApi",
              sources=["ctpwrapper/MdApi.pyx","MdSpi.cpp"],
              libraries=["thostmduserapi"],
              **common_args),
    Extension(name="ctpwrapper.TraderApi",
              sources=["ctpwrapper/TraderApi.pyx"],
              libraries=["thosttraderapi"],
              **common_args)
]

setup(
    name="ctpwrapper",
    version=find_version("ctpwrapper", "__init__.py"),
    packages=["ctpwrapper"],
    include_dirs=header_dir,
    platforms=["win32", "linux"],
    package_dir={"ctpwrapper": "ctpwrapper"},
    package_data={"": package_data},
    ext_modules=cythonize(ext_modules),
    cmdclass={'build_ext': build_ext},
)
