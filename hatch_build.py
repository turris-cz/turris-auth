import pathlib
from typing import Any, Dict, List

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CompileMessages(BuildHookInterface):
    ROOT_DIR = pathlib.Path(__file__).parent

    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:

        if self.target_name in ['sdist']:
            # don't compile messages for sdist
            return super().initialize(version, build_data)

        mo_files = []
        for po_file in CompileMessages.ROOT_DIR.glob("**/*.po"):
            mo_file = po_file.parent / (po_file.stem + ".mo")
            locale = po_file.parent.parent.name
            with po_file.open() as f:
                catalog = read_po(f, locale)
            with mo_file.open("wb") as f:
                write_mo(f, catalog)
                mo_files.append(mo_file)

        force_include = build_data.get("force_include", {})
        force_include.update(
            {p: p.relative_to(CompileMessages.ROOT_DIR) for p in mo_files}
        )
        build_data["force_include"] = force_include

        return super().initialize(version, build_data)

    def clean(self, versions: List[str]) -> None:
        for mo_file in CompileMessages.ROOT_DIR.glob("**/*.mo"):
            mo_file.unlink()
