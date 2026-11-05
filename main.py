#!/usr/bin/env python3

# main.py
#
# Copyright 2022-2024 kramo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gettext
import locale
import re
import signal
import sys
from pathlib import Path
from platform import system

ROOT_DIR = Path(__file__).resolve().parent


def get_version() -> str:
    meson_file = ROOT_DIR / "meson.build"
    if meson_file.is_file():
        try:
            match = re.search(r"version:\s*'([^']+)'", meson_file.read_text("utf-8"))
            if match:
                return match.group(1)
        except OSError:
            pass
    return "2.13.1"


VERSION = get_version()

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

signal.signal(signal.SIGINT, signal.SIG_DFL)

if system() == "Linux":
    try:
        locale.bindtextdomain("cartridges", "/usr/share/locale")
        locale.textdomain("cartridges")
        gettext.install("cartridges", "/usr/share/locale", names=["ngettext"])
    except (AttributeError, OSError):
        gettext.install("cartridges", names=["ngettext"])
else:
    gettext.install("cartridges", names=["ngettext"])


def main() -> int:
    try:
        from gi.repository import Gio, GLib  # pylint: disable=import-outside-toplevel

        resource_candidates = [
            ROOT_DIR / "Resources" / "cartridges.gresource",
            ROOT_DIR / "data" / "cartridges.gresource",
            ROOT_DIR / "_build" / "data" / "cartridges.gresource",
            Path("/usr/share/cartridges/cartridges.gresource"),
        ]
        for res_path in resource_candidates:
            if res_path.is_file():
                try:
                    resource = Gio.Resource.load(str(res_path))
                    resource._register()  # pylint: disable=protected-access
                    break
                except GLib.GError:
                    pass
    except ImportError:
        pass

    from cartridges import main as app_main  # pylint: disable=import-outside-toplevel

    return int(app_main.main(VERSION))


if __name__ == "__main__":
    sys.exit(main())
