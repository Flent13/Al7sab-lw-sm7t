import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["tkinter", "docxtpl", "sqlalchemy"],
    "include_files": ["invoice_template.docx"],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="al7sab_lw_sm7t",
    version="1.0",
    description="Invoice & Inventory Manager",
    options={"build_exe": build_exe_options},
    executables=[Executable("invoice_generator.py", base=base)]
)
