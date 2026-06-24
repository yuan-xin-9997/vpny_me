from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup


ROOT = Path(__file__).resolve().parent
API_DIR = ROOT / "vnpy_ctp" / "api"
VNCTP_DIR = API_DIR / "vnctp"


def ctp_extension(name: str, source_dir: str, libs: list[str]) -> Pybind11Extension:
    source_path = VNCTP_DIR / source_dir
    return Pybind11Extension(
        name,
        sources=[str(source_path / f"{source_dir}.cpp")],
        include_dirs=[
            str(VNCTP_DIR),
            str(API_DIR / "include"),
            str(API_DIR / "include" / "ctp"),
        ],
        library_dirs=[str(API_DIR / "libs")],
        libraries=libs,
        language="c++",
        cxx_std=17,
    )


setup(
    name="vnpy-me-ctp-extensions",
    ext_modules=[
        ctp_extension(
            "vnpy_ctp.api.vnctp.vnctpmd",
            "vnctpmd",
            ["thostmduserapi_se"],
        ),
        ctp_extension(
            "vnpy_ctp.api.vnctp.vnctptd",
            "vnctptd",
            ["thosttraderapi_se"],
        ),
    ],
    cmdclass={"build_ext": build_ext},
)
