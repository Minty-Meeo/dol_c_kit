import dol_c_kit
import setuptools

setuptools.setup(
    name="dol_c_kit",
    version=dol_c_kit.__version__,
    author=dol_c_kit.__author__,
    description="A toolkit for compiling C/C++ code using DevkitPPC and injecting it into a Gamecube Executable (DOL)",
    url="https://github.com/Minty-Meeo/dol_c_kit",
    author_email="MintyMeeo@airmail.cc",
    license="MIT License",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=("dolreader", "pyelftools", "geckolibs"),
    python_requires=">=3.8",
)
