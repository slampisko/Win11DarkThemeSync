"""
Utility for Windows 11 Night Light and Dark Theme synchronization.
When run, it checks whether or not the Night Light is on, and whether the Dark Theme is activated. If these aren't
synchronized, it turns the Dark Theme on or off depending on the Night Light state, and then exits.
The current version also restarts explorer.exe -- I might decide to scrap that feature if it turns out to be intrusive.
I am using it with the Windows Task Scheduler to run the check periodically.
Author: slampisko
Original implementation date: 2024-08-03
"""
import os
import sys
import winreg
import subprocess

NIGHT_LIGHT_SUBKEY = ("Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current"
                      "\\default$windows.data.bluelightreduction.bluelightreductionstate"
                      "\\windows.data.bluelightreduction.bluelightreductionstate")
DARK_THEME_SUBKEY = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
SYSTEM_USES_LIGHT_THEME = 'SystemUsesLightTheme'
APPS_USE_LIGHT_THEME = 'AppsUseLightTheme'
DATA_VALUE_NAME = 'Data'


def _restart_explorer():
    # For some reason using subprocess.call did not work for this command, but os.system did.
    # I can't be bothered to investigate.
    os.system('cmd /c "taskkill /f /im explorer.exe"')
    subprocess.Popen(['cmd', '/c', ''"start explorer.exe"''])


def _get_value_data(key: winreg.HKEYType, value_name: str):
    index = 0
    while True:
        cur_name, cur_data, _ = winreg.EnumValue(key, index)
        if cur_name == value_name:
            return cur_data
        index += 1


def _set_dword_value(key: winreg.HKEYType, value_name: str, new_value: int):
    winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, new_value)


def is_night_light_on():
    """
    Returns whether the Night Light feature is on
    """
    with (winreg.CreateKey(winreg.HKEY_CURRENT_USER, NIGHT_LIGHT_SUBKEY)) as key:
        value_name = None
        while value_name != DATA_VALUE_NAME:
            value_name, value_data, _ = winreg.EnumValue(key, 0)
        # This is a bit of a shortcut -- the correct way would be to check certain indexes for certain bits.
        # But it works well enough for my purposes.
        # The sacred knowledge related to the format of the registry key can be found here:
        # https://superuser.com/q/1200222
        return len(value_data) == 43


def is_light_theme_on():
    """
    Returns whether the Light Theme is on for either apps or the system
    """
    with (winreg.CreateKey(winreg.HKEY_CURRENT_USER, DARK_THEME_SUBKEY)) as key:
        light_theme_apps = bool(_get_value_data(key, APPS_USE_LIGHT_THEME))
        light_theme_system = bool(_get_value_data(key, SYSTEM_USES_LIGHT_THEME))
        return light_theme_apps or light_theme_system


def set_light_theme(enabled: bool):
    """
    Enables or disables the Light Theme for apps and the system
    """
    with (winreg.CreateKey(winreg.HKEY_CURRENT_USER, DARK_THEME_SUBKEY)) as key:
        _set_dword_value(key, APPS_USE_LIGHT_THEME, 1 * enabled)
        _set_dword_value(key, SYSTEM_USES_LIGHT_THEME, 1 * enabled)
        _restart_explorer()


def main() -> int:
    """
    Synchronize the Windows 11 Dark Theme to the Night Light state.
    """
    try:
        night_light_on = is_night_light_on()
        light_theme_on = is_light_theme_on()
        if night_light_on == light_theme_on:
            set_light_theme(not night_light_on)
    except OSError:
        print("There was an error reading from the registry, or the key did not contain the required value.")
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
