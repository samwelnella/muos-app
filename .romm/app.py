import sys
import time
import os

import graphic as gr
import input
from filesystem.filesystem import Filesystem
from api.api import API

romm_provider = API()
platforms_selected_position = 0
collections_selected_position = 0
roms_selected_position = 0
valid_host = True
valid_credentials = True
platforms = []
collections = []
roms = []
current_window = "platforms"
max_n_platforms = 11
max_n_collections = 11
max_n_roms = 10
fs = Filesystem()
skip_input_check = False


def start():
    global current_window, romm_provider, platforms, collections, valid_host, valid_credentials
    current_window = "platforms"
    load_platforms_menu()
    gr.draw_log("Fetching platforms...", fill=gr.colorViolet, outline=gr.colorViolet)
    gr.draw_paint()
    platforms, valid_host, valid_credentials = romm_provider.get_platforms()
    collections, valid_host, valid_credentials = romm_provider.get_collections()
    load_platforms_menu()
    return


def update():
    global current_window, platforms_selected_position, skip_input_check, platforms, roms

    if skip_input_check:
        input.reset_input()
        skip_input_check = False
    else:
        input.check()

    if input.key("MENUF"):
        gr.draw_end()
        sys.exit()

    if current_window == "platforms":
        load_platforms_menu()
    elif current_window == "collections":
        load_collections_menu()
    elif current_window == "roms":
        load_roms_menu()
    else:
        load_platforms_menu()

    return


def load_platforms_menu():
    global romm_provider, platforms_selected_position, platforms, current_window, skip_input_check, roms, valid_host, valid_credentials, max_n_platforms

    if valid_host and valid_credentials:
        platforms_selected_position = input.handle_navigation(
            platforms_selected_position, max_n_platforms, len(platforms)
        )
        platforms_selected_position = input.handle_large_navigation(
            platforms_selected_position, max_n_platforms, len(platforms)
        )

        if input.key("A"):
            current_window = "roms"
            gr.draw_log("Fetching roms...", fill=gr.colorViolet, outline=gr.colorViolet)
            gr.draw_paint()
            skip_input_check = True
            platform_id = platforms[platforms_selected_position][1]
            roms, valid_host, valid_credentials = romm_provider.get_roms(platform_id)
            return
        elif input.key("Y"):
            gr.draw_log("Refreshing...", fill=gr.colorViolet, outline=gr.colorViolet)
            gr.draw_paint()
            skip_input_check = True
            platforms, valid_host, valid_credentials = romm_provider.get_platforms()
            skip_input_check = False
        elif input.key("X"):
            current_window = "collections"
            skip_input_check = True
            return

    gr.draw_clear()

    gr.draw_header(romm_provider.host, romm_provider.username)

    if valid_host:
        if valid_credentials:
            gr.draw_platforms_list(
                platforms_selected_position, max_n_platforms, platforms
            )
        else:
            gr.draw_text((25, 55), "Error: Permission denied")
    else:
        gr.draw_text((25, 55), "Error: Invalid host")

    if valid_host and valid_credentials:
        gr.button_circle((30, 460), "A", "Select")
        gr.button_circle((133, 460), "Y", "Refresh")
        gr.button_circle((243, 460), "X", "collections" if current_window == "platforms" else "platforms")
        gr.button_circle((380, 460), "M", "Exit")
    else:
        gr.button_circle((30, 460), "M", "Exit")

    gr.draw_paint()

    return


def load_collections_menu():
    global romm_provider, collections_selected_position, collections, current_window, skip_input_check, roms, valid_host, valid_credentials, max_n_collections

    if valid_host and valid_credentials:
        collections_selected_position = input.handle_navigation(
            collections_selected_position, max_n_collections, len(collections)
        )
        collections_selected_position = input.handle_large_navigation(
            collections_selected_position, max_n_collections, len(collections)
        )

        if input.key("A"):
            # current_window = "roms"
            # gr.draw_log("Fetching roms...", fill=gr.colorViolet, outline=gr.colorViolet)
            # gr.draw_paint()
            # skip_input_check = True
            # platform_id = platforms[platforms_selected_position][1]
            # roms, valid_host, valid_credentials = romm_provider.get_roms(platform_id)
            return
        elif input.key("Y"):
            gr.draw_log("Refreshing...", fill=gr.colorViolet, outline=gr.colorViolet)
            gr.draw_paint()
            skip_input_check = True
            collections, valid_host, valid_credentials = romm_provider.get_collections()
            skip_input_check = False
        elif input.key("X"):
            current_window = "platforms"
            skip_input_check = True
            return

    gr.draw_clear()

    gr.draw_header(romm_provider.host, romm_provider.username)

    if valid_host:
        if valid_credentials:
            gr.draw_platforms_list(
                collections_selected_position, max_n_collections, collections
            )
        else:
            gr.draw_text((25, 55), "Error: Permission denied")
    else:
        gr.draw_text((25, 55), "Error: Invalid host")

    if valid_host and valid_credentials:
        gr.button_circle((30, 460), "A", "Select")
        gr.button_circle((133, 460), "Y", "Refresh")
        gr.button_circle((243, 460), "X", "collections" if current_window == "platforms" else "platforms")
        gr.button_circle((380, 460), "M", "Exit")
    else:
        gr.button_circle((30, 460), "M", "Exit")

    gr.draw_paint()

    return


def load_roms_menu():
    global romm_provider, platforms_selected_position, platforms, roms, current_window, roms_selected_position, skip_input_check, valid_host, valid_credentials

    if len(roms) < 1:
        current_window = "platforms"
        gr.draw_clear()
        return

    if valid_host and valid_credentials:
        roms_selected_position = input.handle_navigation(
            roms_selected_position, max_n_roms, len(roms)
        )
        roms_selected_position = input.handle_large_navigation(
            roms_selected_position, max_n_roms, len(roms)
        )

        if input.key("A"):
            skip_input_check = True
            gr.draw_log("Downloading...", fill=gr.colorViolet, outline=gr.colorViolet)
            gr.draw_paint()
            dest_path = os.path.join(
                fs.get_sd_storage_platform_path(roms[roms_selected_position][2]),
                roms[roms_selected_position][1],
            )
            valid_host, valid_credentials = romm_provider.download_rom(
                roms[roms_selected_position], dest_path
            )
            if valid_host and valid_credentials:
                gr.draw_log(
                    f"Downloaded to\n{dest_path}",
                    fill=gr.colorGreen,
                    outline=gr.colorGreen,
                    lines=2,
                )
            elif not valid_host:
                gr.draw_log(
                    "Error: Invalid host", fill=gr.colorRed, outline=gr.colorRed
                )
                valid_host = True
            elif not valid_credentials:
                gr.draw_log(
                    "Error: Permission denied", fill=gr.colorRed, outline=gr.colorRed
                )
                valid_credentials = True
            else:
                gr.draw_log(
                    "Error: Invalid host or permission denied",
                    fill=gr.colorRed,
                    outline=gr.colorRed,
                )
            gr.draw_paint()
            time.sleep(2)
            skip_input_check = False
        elif input.key("B"):
            current_window = "platforms"
            gr.draw_clear()
            romm_provider.reset_roms_list()
            roms_selected_position = 0
            skip_input_check = True
            return
        elif input.key("Y"):
            gr.draw_log("Refreshing...", fill=gr.colorViolet, outline=gr.colorViolet)
            gr.draw_paint()
            skip_input_check = True
            platform_id = platforms[platforms_selected_position][1]
            roms, valid_host, valid_credentials = romm_provider.get_roms(
                platform_id, refresh=True
            )
            skip_input_check = False
        elif input.key("X"):
            current = fs.get_sd_storage()
            fs.switch_sd_storage()
            new = fs.get_sd_storage()
            if new == current:
                gr.draw_log(
                    f"Couldn't set SD {fs.get_sd_storage()}",
                    fill=gr.colorRed,
                    outline=gr.colorRed,
                )
            else:
                gr.draw_log(
                    f"Set download path to SD {fs.get_sd_storage()}: {fs.get_sd_storage_platform_path(roms[roms_selected_position][2])}",
                    fill=gr.colorGreen,
                    outline=gr.colorGreen,
                )
            gr.draw_paint()
            time.sleep(1)

    gr.draw_clear()

    gr.draw_header(romm_provider.host, romm_provider.username)

    gr.draw_roms_list(
        roms_selected_position, max_n_roms, roms, platforms, platforms_selected_position
    )

    if valid_host and valid_credentials:
        gr.button_circle((30, 460), "A", "Download")
        gr.button_circle((145, 460), "B", "Back")
        gr.button_circle((225, 460), "Y", "Refresh")
        gr.button_circle((330, 460), "X", f"SD: {fs.get_sd_storage()}")
        gr.button_circle((420, 460), "M", "Exit")
    else:
        gr.button_circle((30, 460), "M", "Exit")

    gr.draw_paint()

    return
