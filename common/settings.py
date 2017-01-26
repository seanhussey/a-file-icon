import json
import os
import re
import sublime

from .vendor import jsonutils
from .vendor import webcolors
from .utils.logging import log, dump

PACKAGE_NAME = "A File Icon"
PACKAGE_MAIN = PACKAGE_NAME
PACKAGE_BASE = os.path.basename(os.path.dirname(os.path.dirname(__file__)))

PACKAGE_SETTINGS_FILE = PACKAGE_NAME + ".sublime-settings"
SUBLIME_SETTINGS_FILE = "Preferences.sublime-settings"
PKGCTRL_SETTINGS_FILE = "Package Control.sublime-settigns"

OVERLAY_ROOT = "{0} {1} {0}".format("zzz", PACKAGE_NAME)

_current_settings = {}
_default_settings = {}
_pattern = re.compile(r"#([0-9a-fA-F]{3}){1,2}")
_uuid = "9ebcce78-4cac-4089-8bd7-d551c634b052"


def _get_default():
    s = json.loads(jsonutils.sanitize_json(sublime.load_resource(
        "Packages/{0}/.sublime/{0}.sublime-settings"
        .format(PACKAGE_NAME)
    )))

    del s["dev_mode"]
    del s["dev_trace"]

    return s


def _get_colors():
    colors = {}
    package_settings = package()
    color_options = [
        o for o in _default_settings if o.startswith("color")
    ]

    if package_settings.get("color"):
        for opt in color_options:
            color = package_settings.get(opt)

            if re.match(_pattern, color):
                rgb_color = webcolors.hex_to_rgb(color)

                color = ", ".join(str(e) for e in rgb_color)
                colors[opt] = "[" + color + "]"
            else:
                colors[opt] = ""

    return colors


def _on_aliases_change():
    log("Aliases settings changed")
    sublime.run_command("afi_check_aliases")


def _on_icons_change():
    log("Icons settings changed")
    sublime.run_command("afi_patch_themes", {"overwrite": True})


def _on_force_mode_change():
    log("Force mode settings changed")
    sublime.run_command("afi_patch_themes")


def _on_change():
    is_aliases_changed = False
    is_icons_changed = False
    is_force_mode_changed = False

    global _current_settings
    real_settings = {}

    for s in _default_settings:
        real_settings[s] = package().get(s)

        if real_settings[s] != _current_settings[s]:
            if s.startswith("aliases"):
                is_aliases_changed = True
            elif s.startswith("force_mode"):
                is_force_mode_changed = True
            else:
                is_icons_changed = True

    if is_aliases_changed:
        _on_aliases_change()

    if is_icons_changed:
        _on_icons_change()
    elif is_force_mode_changed:
        _on_force_mode_change()

    if is_aliases_changed or is_force_mode_changed or is_icons_changed:
        _current_settings = real_settings


def _add_listener():
    package().add_on_change(_uuid, _on_change)


def _update():
    global _current_settings

    for s in _default_settings:
        _current_settings[s] = package().get(s)


def clear_listener():
    package().clear_on_change(_uuid)


def is_package_archive():
    if os.path.splitext(PACKAGE_BASE)[1] == ".sublime-package":
        return True
    return False


def subltxt():
    return sublime.load_settings(SUBLIME_SETTINGS_FILE)


def pkgctrl():
    return sublime.load_settings(PKGCTRL_SETTINGS_FILE)


def package():
    return sublime.load_settings(PACKAGE_SETTINGS_FILE)


def icons():
    log("Getting settings of the icons")

    s = _get_colors()
    s["opacity"] = package().get("opacity")
    s["opacity_on_hover"] = package().get("opacity_on_hover")
    s["opacity_on_select"] = package().get("opacity_on_select")
    s["size"] = package().get("size")
    dump(s)

    return s


def init():
    log("Initializing settings")

    _add_listener()

    global _default_settings
    _default_settings = _get_default()

    _update()