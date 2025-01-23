import sys
import time

import graphic as gr
import input
from filesystem.filesystem import Filesystem
from api.romm import RomM

romm_provider = RomM()
selected_position = 0
roms_selected_position = 0
valid_host = True
valid_credentials = True
platforms = []
roms = []
current_window = "platforms"
max_n_platforms = 11
max_n_roms = 10
fs = Filesystem()
skip_input_check = False


def start():
    global current_window, romm_provider, platforms, valid_host, valid_credentials
    current_window = "platform"
    platforms, valid_host, valid_credentials = romm_provider.get_platforms()
    load_platforms_menu()


def update():
    global current_window, selected_position, skip_input_check, platforms, roms

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
    elif current_window == "roms":
        load_roms_menu()
    else:
        load_platforms_menu()


def load_platforms_menu():
    global romm_provider, selected_position, platforms, current_window, skip_input_check, roms, valid_host, valid_credentials

    if valid_host and valid_credentials:
        if input.key("DY"):
            if input.value == 1:
                if selected_position == len(platforms) - 1:
                    selected_position = 0
                elif selected_position < len(platforms) - 1:
                    selected_position += 1
            elif input.value == -1:
                if selected_position == 0:
                    selected_position = len(platforms) - 1
                elif selected_position > 0:
                    selected_position -= 1
        elif input.key("A"):
            current_window = "roms"
            gr.draw_log("Fetching ROMs...", fill=gr.colorViolet, outline=gr.colorViolet)
            gr.draw_paint()
            skip_input_check = True
            platform_id = platforms[selected_position][1]
            roms, valid_host, valid_credentials = romm_provider.get_roms(platform_id)
            return
        elif input.key("Y"):
            gr.draw_log("Refreshing...", fill=gr.colorViolet, outline=gr.colorViolet)
            gr.draw_paint()
            skip_input_check = True
            platforms, valid_host, valid_credentials = romm_provider.get_platforms()
            skip_input_check = False

    gr.draw_clear()

    # Header
    gr.draw_text(
        (gr.screen_width/2, 20), f"RomM | Host: {romm_provider.host} | User: {romm_provider.username}", anchor="mm"
    )
    if valid_host:
        if valid_credentials:
            # Platforms list
            gr.draw_rectangle_r([10, 35, 630, 437], 15, fill=gr.colorGrayD2, outline=None)
            start_idx = int(selected_position / max_n_platforms) * max_n_platforms
            end_idx = start_idx + max_n_platforms
            for i, p in enumerate(platforms[start_idx:end_idx]):
                row_list(
                    f"{p[0]} ({p[2]})" if len(p[0]) <= 55 else p[0][:55] + f"... ({p[2]})",
                    (20, 45 + (i * 35)),
                    600,
                    i == (selected_position % max_n_platforms),
                )
        else:
            gr.draw_text((25, 55), "Error: Invalid credentials")
    else:
        gr.draw_text((25, 55), "Error: Invalid host")

    if valid_host and valid_credentials:
        button_circle((30, 460), "A", "Select")
        button_circle((133, 460), "Y", "Refresh")
        button_circle((243, 460), "M", "Exit")
    else:
        button_circle((30, 460), "M", "Exit")

    gr.draw_paint()


def load_roms_menu():
    global romm_provider, selected_position, platforms, roms, current_window, roms_selected_position, skip_input_check, valid_host, valid_credentials

    if len(roms) < 1:
        current_window = "platforms"
        gr.draw_clear()
        return

    if valid_host and valid_credentials:
        if input.key("A"):
            skip_input_check = True
            gr.draw_log("Downloading...", fill=gr.colorViolet, outline=gr.colorViolet)
            gr.draw_paint()
            dest_path, valid_host, valid_credentials = romm_provider.download_rom(roms[roms_selected_position])
            gr.draw_log(
                f"Downloaded to\n{dest_path}", fill=gr.colorViolet, outline=gr.colorViolet, lines=2
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
            platform_id = platforms[selected_position][1]
            roms, valid_host, valid_credentials = romm_provider.get_roms(platform_id, refresh=True)
            skip_input_check = False
        elif input.key("X"):
            fs.switch_sd_storage()
        elif input.key("DY"):
            if input.value == 1:
                if roms_selected_position == len(roms) - 1:
                    roms_selected_position = 0
                elif roms_selected_position < len(roms) - 1:
                    roms_selected_position += 1
            elif input.value == -1:
                if roms_selected_position == 0:
                    roms_selected_position = len(roms) - 1
                elif roms_selected_position > 0:
                    roms_selected_position -= 1
        elif input.key("L1"):
            if roms_selected_position > 0:
                if roms_selected_position - max_n_roms >= 0:
                    roms_selected_position = roms_selected_position - max_n_roms
                else:
                    roms_selected_position = 0
        elif input.key("R1"):
            if roms_selected_position < len(roms) - 1:
                if roms_selected_position + max_n_roms <= len(roms) - 1:
                    roms_selected_position = roms_selected_position + max_n_roms
                else:
                    roms_selected_position = len(roms) - 1
        elif input.key("L2"):
            if roms_selected_position > 0:
                if roms_selected_position - 100 >= 0:
                    roms_selected_position = roms_selected_position - 100
                else:
                    roms_selected_position = 0
        elif input.key("R2"):
            if roms_selected_position < len(roms) - 1:
                if roms_selected_position + 100 <= len(roms) - 1:
                    roms_selected_position = roms_selected_position + 100
                else:
                    roms_selected_position = len(roms) - 1

    gr.draw_clear()

    # Header
    gr.draw_text(
        (gr.screen_width/2, 20), f"RomM | Host: {romm_provider.host} | User: {romm_provider.username}", anchor="mm"
    )
    gr.draw_rectangle_r([10, 37, 630, 100], 15, outline=gr.colorViolet)
    gr.draw_text((gr.screen_width/2, 55), platforms[selected_position][0], color=gr.colorViolet, anchor="mm")

    # ROMs list
    gr.draw_rectangle_r([10, 70, 630, 437], 15, fill=gr.colorGrayD2, outline=None)
    start_idx = int(roms_selected_position / max_n_roms) * max_n_roms
    end_idx = start_idx + max_n_roms
    for i, r in enumerate(roms[start_idx:end_idx]):
        row_list(
            f"{r[0]} [{r[5]}]" if len(r[0]) <= 55 else r[0][:55] + f"... {r[5]}",
            (20, 80 + (i * 35)),
            600,
            i == (roms_selected_position % max_n_roms),
        )

    if valid_host and valid_credentials:
        button_circle((30, 460), "A", "Download")
        button_circle((145, 460), "B", "Back")
        button_circle((225, 460), "Y", "Refresh")
        button_circle((330, 460), "X", f"SD: {fs.get_sd_storage()}")
        button_circle((420, 460), "M", "Exit")
    else:
        button_circle((30, 460), "M", "Exit")
    gr.draw_paint()

    return


def row_list(text, pos, width, selected, fill=None):
    gr.draw_rectangle_r(
        [pos[0], pos[1], pos[0] + width, pos[1] + 32],
        5,
        fill=(gr.colorViolet if selected else gr.colorGrayL1),
    )
    gr.draw_text((pos[0] + 5, pos[1] + 5), text)


def button_circle(pos, button, text):
    gr.draw_circle(pos, 15, fill=gr.colorViolet, outline=None)
    gr.draw_text(pos, button, anchor="mm")
    gr.draw_text((pos[0] + 20, pos[1]), text, font=13, anchor="lm")
