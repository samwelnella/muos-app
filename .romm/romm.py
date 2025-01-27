import sys
import time
import threading
import os

import ui
from filesystem.filesystem import Filesystem
from api.api import API
from input import Input
from __version__ import version


class View:
    PLATFORMS = "platform"
    COLLECTIONS = "collection"
    ROMS = "roms"


class StartMenuOptions:
    EXIT = (f"{ui.glyphs.exit} Exit", 0)


class RomM:
    def __init__(self):
        self.romm_provider = API()
        self.fs = Filesystem()
        self.input = Input()
        self.valid_host = True
        self.valid_credentials = True
        self.current_view = View.PLATFORMS
        self.previows_view = View.PLATFORMS
        self.start_menu = False
        self.start_menu_options = [
            value
            for name, value in StartMenuOptions.__dict__.items()
            if not name.startswith("__")
        ]
        self.platforms_selected_position = 0
        self.collections_selected_position = 0
        self.roms_selected_position = 0
        self.start_menu_selected_position = 0
        self.multi_selected_roms = []
        self.platforms = []
        self.platforms_ready = threading.Event()
        self.collections = []
        self.collections_ready = threading.Event()
        self.roms = []
        self.roms_ready = threading.Event()
        self.download_queue = []
        self.downloading_rom = None
        self.downloaded_rom_bytes_progress = 0
        self.downloaded_percent = 0
        self.downloading_rom_position = 0
        self.download_rom_ready = threading.Event()
        self.max_n_platforms = 11
        self.max_n_collections = 11
        self.max_n_roms = 10

    def _fetch_platforms(self):
        self.platforms, self.valid_host, self.valid_credentials = (
            self.romm_provider.get_platforms()
        )
        self.platforms_ready.set()

    def _fetch_collections(self):
        self.collections, self.valid_host, self.valid_credentials = (
            self.romm_provider.get_collections()
        )
        self.collections_ready.set()

    def _fetch_roms(self):
        if self.current_view != View.ROMS:
            self.roms, self.valid_host, self.valid_credentials = (
                self.romm_provider.get_roms(
                    (
                        self.current_view
                        if self.current_view != View.ROMS
                        else self.previows_view
                    ),
                    (
                        self.platforms[self.platforms_selected_position].id
                        if self.current_view == View.PLATFORMS
                        else self.collections[self.collections_selected_position].id
                    ),
                )
            )
        else:
            self.roms, self.valid_host, self.valid_credentials = (
                self.romm_provider.get_roms(
                    self.previows_view,
                    (
                        self.platforms[self.platforms_selected_position].id
                        if self.previows_view == View.PLATFORMS
                        else self.collections[self.collections_selected_position].id
                    ),
                )
            )
        self.roms_ready.set()

    def _download_roms(self):
        self.download_queue.sort(key=lambda rom: rom.name)
        for i, rom in enumerate(self.download_queue):
            self.downloading_rom = rom
            self.downloading_rom_position = i + 1
            dest_path = os.path.join(
                self.fs.get_sd_storage_platform_path(rom.platform_slug),
                rom.file_name,
            )
            for (
                current_downloaded_bytes,
                valid_host,
                valid_credentials,
            ) in self.romm_provider.download_rom(self.downloading_rom, dest_path):
                if not valid_host or not valid_credentials:
                    self.valid_host = valid_host
                    self.valid_credentials = valid_credentials
                    break
                self.downloaded_rom_bytes_progress = current_downloaded_bytes
                self.downloaded_percent = (
                    self.downloaded_rom_bytes_progress
                    / self.downloading_rom.file_size_bytes
                ) * 100
            self.downloaded_percent = 0
            self.downloaded_rom_bytes_progress = 0
        self.downloading_rom = None
        self.multi_selected_roms = []
        self.download_queue = []
        self.download_rom_ready.set()

    def _render_platforms_view(self):
        ui.draw_platforms_list(
            self.platforms_selected_position,
            self.max_n_platforms,
            self.platforms,
        )
        if not self.platforms_ready.is_set():
            ui.draw_log(text_line_1=f"{next(ui.glyphs.spinner)} Fetching platforms")
            time.sleep(0.1)
        elif not self.download_rom_ready.is_set() and self.downloading_rom:
            ui.draw_loader(self.downloaded_percent)
            ui.draw_log(
                text_line_1=f"{self.downloading_rom_position}/{len(self.download_queue)} | {self.downloaded_percent:.2f}% | {ui.glyphs.download} {self.downloading_rom.name}",
                text_line_2=f"({self.downloading_rom.file_name})",
                background=False,
            )
            time.sleep(0.1)
        elif not self.valid_host:
            ui.draw_log(
                text_line_1="Error: Invalid host",
                text_color=ui.colorRed,
            )
            time.sleep(2)
            self.valid_host = True
        elif not self.valid_credentials:
            ui.draw_log(
                text_line_1="Error: Permission denied",
                text_color=ui.colorRed,
            )
            time.sleep(2)
            self.valid_credentials = True
        else:
            ui.button_circle((30, 460), "A", "Select", color=ui.colorRed)
            ui.button_circle((133, 460), "Y", "Refresh", color=ui.colorGreen)
            ui.button_circle(
                (243, 460),
                "X",
                ("Collections" if self.current_view == View.PLATFORMS else "Platforms"),
                color=ui.colorBlue,
            )

    def _update_platforms_view(self):
        if self.input.key("A"):
            if self.roms_ready.is_set():
                self.roms_ready.clear()
                self.roms = []
                self.previows_view = View.PLATFORMS
                self.current_view = View.ROMS
                threading.Thread(target=self._fetch_roms).start()
            self.input.reset_input()
        elif self.input.key("Y"):
            if self.platforms_ready.is_set():
                self.platforms_ready.clear()
                threading.Thread(target=self._fetch_platforms).start()
            self.input.reset_input()
        elif self.input.key("X"):
            self.current_view = View.COLLECTIONS
            self.input.reset_input()
        else:
            self.platforms_selected_position = self.input.handle_navigation(
                self.platforms_selected_position,
                self.max_n_platforms,
                len(self.platforms),
            )

    def _render_collections_view(self):
        ui.draw_collections_list(
            self.collections_selected_position,
            self.max_n_collections,
            self.collections,
            fill=ui.colorYellow,
        )
        if not self.collections_ready.is_set():
            ui.draw_log(text_line_1=f"{next(ui.glyphs.spinner)} Fetching collections")
            time.sleep(0.1)
        elif not self.download_rom_ready.is_set() and self.downloading_rom:
            ui.draw_loader(self.downloaded_percent)
            ui.draw_log(
                text_line_1=f"{self.downloading_rom_position}/{len(self.download_queue)} | {self.downloaded_percent:.2f}% | {ui.glyphs.download} {self.downloading_rom.name}",
                text_line_2=f"({self.downloading_rom.file_name})",
                background=False,
            )
            time.sleep(0.1)
        elif not self.valid_host:
            ui.draw_log(
                text_line_1="Error: Invalid host",
                text_color=ui.colorRed,
            )
            time.sleep(2)
            self.valid_host = True
        elif not self.valid_credentials:
            ui.draw_log(
                text_line_1="Error: Permission denied",
                text_color=ui.colorRed,
            )
            time.sleep(2)
            self.valid_credentials = True
        else:
            ui.button_circle((30, 460), "A", "Select", color=ui.colorRed)
            ui.button_circle((133, 460), "Y", "Refresh", color=ui.colorGreen)
            ui.button_circle(
                (243, 460),
                "X",
                ("Collections" if self.current_view == View.PLATFORMS else "Platforms"),
                color=ui.colorBlue,
            )

    def _update_collections_view(self):
        if self.input.key("A"):
            if self.roms_ready.is_set():
                self.roms_ready.clear()
                self.roms = []
                self.previows_view = View.COLLECTIONS
                self.current_view = View.ROMS
                threading.Thread(target=self._fetch_roms).start()
            self.input.reset_input()
        elif self.input.key("Y"):
            if self.collections_ready.is_set():
                self.collections_ready.clear()
                threading.Thread(target=self._fetch_collections).start()
            self.input.reset_input()
        elif self.input.key("X"):
            self.current_view = View.PLATFORMS
            self.input.reset_input()
        else:
            self.collections_selected_position = self.input.handle_navigation(
                self.collections_selected_position,
                self.max_n_collections,
                len(self.collections),
            )

    def _render_roms_view(self):
        header_text = (
            self.platforms[self.platforms_selected_position].display_name
            if self.previows_view == View.PLATFORMS
            else self.collections[self.collections_selected_position].name
        )
        header_color = (
            ui.colorViolet if self.previows_view == View.PLATFORMS else ui.colorYellow
        )
        ui.draw_roms_list(
            self.roms_selected_position,
            self.max_n_roms,
            self.roms,
            header_text,
            header_color,
            self.multi_selected_roms,
            prepend_platform_slug=self.previows_view == View.COLLECTIONS,
        )
        if not self.roms_ready.is_set():
            ui.draw_log(text_line_1=f"{next(ui.glyphs.spinner)} Fetching roms")
            time.sleep(0.1)
        elif not self.download_rom_ready.is_set() and self.downloading_rom:
            ui.draw_loader(self.downloaded_percent)
            ui.draw_log(
                text_line_1=f"{self.downloading_rom_position}/{len(self.download_queue)} | {self.downloaded_percent:.2f}% | {ui.glyphs.download} {self.downloading_rom.name}",
                text_line_2=f"({self.downloading_rom.file_name})",
                background=False,
            )
            time.sleep(0.1)
        elif not self.valid_host:
            ui.draw_log(
                text_line_1="Error: Invalid host",
                text_color=ui.colorRed,
            )
            time.sleep(2)
            self.valid_host = True
        elif not self.valid_credentials:
            ui.draw_log(
                text_line_1="Error: Permission denied",
                text_color=ui.colorRed,
            )
            time.sleep(2)
            self.valid_credentials = True
        else:
            ui.button_circle((30, 460), "A", "Download", color=ui.colorRed)
            ui.button_circle((145, 460), "B", "Back", color=ui.colorYellow)
            ui.button_circle((225, 460), "Y", "Refresh", color=ui.colorGreen)
            ui.button_circle(
                (330, 460), "X", f"SD: {self.fs.get_sd_storage()}", color=ui.colorBlue
            )

    def _update_roms_view(self):
        if self.input.key("A"):
            if self.roms_ready.is_set() and self.download_rom_ready.is_set():
                self.download_rom_ready.clear()
                # If no game is "multi-selected" the current game is added to the download list
                if len(self.multi_selected_roms) == 0:
                    self.multi_selected_roms.append(
                        self.roms[self.roms_selected_position]
                    )
                self.download_queue = self.multi_selected_roms
                threading.Thread(target=self._download_roms).start()
                self.input.reset_input()
        elif self.input.key("B"):
            self.current_view = self.previows_view
            self.romm_provider.reset_roms_list()
            self.roms_selected_position = 0
            self.multi_selected_roms = []
            self.input.reset_input()
        elif self.input.key("Y"):
            if self.roms_ready.is_set():
                self.roms_ready.clear()
                threading.Thread(target=self._fetch_roms).start()
                self.multi_selected_roms = []
            self.input.reset_input()
        elif self.input.key("X"):
            current = self.fs.get_sd_storage()
            self.fs.switch_sd_storage()
            new = self.fs.get_sd_storage()
            if new == current:
                ui.draw_log(
                    text_line_1=f"Error: Couldn't find path {self.fs.get_sd2_storage_path()}",
                    text_color=ui.colorRed,
                )
            else:
                ui.draw_log(
                    text_line_1=f"Set download path to SD {self.fs.get_sd_storage()}: {self.fs.get_sd_storage_platform_path(self.roms[self.roms_selected_position].platform_slug)}",
                    text_color=ui.colorGreen,
                )
            time.sleep(2)
            self.input.reset_input()
        elif self.input.key("SELECT"):
            if self.download_rom_ready.is_set():
                if (
                    self.roms[self.roms_selected_position]
                    not in self.multi_selected_roms
                ):
                    self.multi_selected_roms.append(
                        self.roms[self.roms_selected_position]
                    )
                else:
                    self.multi_selected_roms.remove(
                        self.roms[self.roms_selected_position]
                    )
            self.input.reset_input()
        else:
            self.roms_selected_position = self.input.handle_navigation(
                self.roms_selected_position, self.max_n_roms, len(self.roms)
            )

    def _render_start_menu(self):
        pos = [ui.screen_width / 3, ui.screen_height / 3]
        padding = 5
        width = 200
        n_options = len(self.start_menu_options)
        option_height = 32
        option_height_with_gap = 35
        version_x_adjustement = 50
        version_height = 24
        ui.draw_rectangle_r(
            [
                pos[0],
                pos[1],
                pos[0] + width + padding * 2,
                n_options * option_height_with_gap
                + padding * 2
                + pos[1]
                + version_height,
            ],
            5,
            fill=ui.colorGrayD2,
            outline=ui.colorViolet,
        )
        start_idx = int(self.start_menu_selected_position / n_options) * n_options
        end_idx = start_idx + n_options
        for i, option in enumerate(self.start_menu_options[start_idx:end_idx]):
            is_selected = i == (self.start_menu_selected_position % n_options)
            ui.row_list(
                option[0],
                (pos[0] + padding, pos[1] + padding + (i * option_height_with_gap)),
                width,
                option_height,
                is_selected,
            )
        ui.draw_text(
            (
                pos[0] + width - version_x_adjustement,
                pos[1]
                + padding
                + padding
                + len(self.start_menu_options) * option_height_with_gap,
            ),
            f"v{version}",
        )

    def _update_start_menu(self):
        if self.input.key("A"):
            if self.start_menu_selected_position == StartMenuOptions.EXIT[1]:
                ui.draw_end()
                sys.exit()
            elif self.start_menu_selected_position == StartMenuOptions.ABOUT[1]:
                self.input.reset_input()
        elif self.input.key("B"):
            self.start_menu = not self.start_menu
            self.input.reset_input()
        else:
            self.start_menu_selected_position = self.input.handle_navigation(
                self.start_menu_selected_position,
                len(self.start_menu_options),
                len(self.start_menu_options),
            )

    def _update_common(self):
        if self.input.key("START"):
            self.start_menu = not self.start_menu
            self.input.reset_input()

    def start(self):
        threading.Thread(target=self.input.check, daemon=True).start()
        ui.draw_header(self.romm_provider.host, self.romm_provider.username)
        self._render_platforms_view()
        threading.Thread(target=self._fetch_platforms).start()
        threading.Thread(target=self._fetch_collections).start()
        self.roms_ready.set()
        self.download_rom_ready.set()

    def update(self):
        ui.draw_clear()

        ui.draw_header(self.romm_provider.host, self.romm_provider.username)

        # Render view
        if self.valid_host:
            if self.valid_credentials:
                if self.current_view == View.PLATFORMS:
                    self._render_platforms_view()
                    if not self.start_menu:
                        self._update_platforms_view()
                elif self.current_view == View.COLLECTIONS:
                    self._render_collections_view()
                    if not self.start_menu:
                        self._update_collections_view()
                elif self.current_view == View.ROMS:
                    self._render_roms_view()
                    if not self.start_menu:
                        self._update_roms_view()
                else:
                    self._render_platforms_view()
                    if not self.start_menu:
                        self._update_platforms_view()
            else:
                ui.draw_text(
                    (ui.screen_width / 2, ui.screen_height / 2),
                    "Error: Permission denied",
                    color=ui.colorRed,
                    anchor="mm",
                )
        else:
            ui.draw_text(
                (ui.screen_width / 2, ui.screen_height / 2),
                "Error: Invalid host",
                color=ui.colorRed,
                anchor="mm",
            )
        # Render start menu
        if self.start_menu:
            self._render_start_menu()
            self._update_start_menu()

        self._update_common()

        ui.draw_update()
