import sys
import time
import os
import threading

import ui
from filesystem.filesystem import Filesystem
from api.api import API
from input import Input


class RomM:
    def __init__(self):
        self.romm_provider = API()
        self.fs = Filesystem()
        self.input = Input()
        self.valid_host = True
        self.valid_credentials = True
        self.current_window = "platform"
        self.selected_bucket = "platform"
        self.platforms_selected_position = 0
        self.collections_selected_position = 0
        self.roms_selected_position = 0
        self.multi_selected_roms = []
        self.platforms = []
        self.collections = []
        self.roms = []
        self.max_n_platforms = 11
        self.max_n_collections = 11
        self.max_n_roms = 10
        self.skip_input_check = False

    def start(self):
        input_thread = threading.Thread(target=self.input.check, daemon=True)
        input_thread.start()
        self._render_platforms_view()
        ui.draw_log("Fetching platforms...")
        self.platforms, self.valid_host, self.valid_credentials = (
            self.romm_provider.get_platforms()
        )
        self.collections, self.valid_host, self.valid_credentials = (
            self.romm_provider.get_collections()
        )
        return

    def _render_platforms_view(self):
        ui.draw_header(self.romm_provider.host, self.romm_provider.username)
        if self.valid_host:
            if self.valid_credentials:
                ui.draw_platforms_list(
                    self.platforms_selected_position,
                    self.max_n_platforms,
                    self.platforms,
                )
                ui.button_circle((30, 460), "A", "Select", color=ui.colorRed)
                ui.button_circle((133, 460), "Y", "Refresh", color=ui.colorGreen)
                ui.button_circle(
                    (243, 460),
                    "X",
                    "Collections" if self.current_window == "platform" else "Platforms",
                    color=ui.colorBlue,
                )
                ui.button_circle((380, 460), "M", "Exit")
            else:
                ui.draw_text((25, 55), "Error: Permission denied")
                ui.button_circle((30, 460), "M", "Exit")
        else:
            ui.draw_text((25, 55), "Error: Invalid host")
            ui.button_circle((30, 460), "M", "Exit")

    def _update_platforms_view(self):
        if self.valid_host and self.valid_credentials:
            if self.input.key("A"):
                ui.draw_log("Fetching roms...")
                platform_id = self.platforms[self.platforms_selected_position][1]
                self.roms, self.valid_host, self.valid_credentials = (
                    self.romm_provider.get_roms(self.current_window, platform_id)
                )
                self.selected_bucket = "platform"
                self.current_window = "roms"
                self.input.reset_input()
            elif self.input.key("Y"):
                ui.draw_log("Fetching platforms...")
                self.platforms, self.valid_host, self.valid_credentials = (
                    self.romm_provider.get_platforms()
                )
                self.input.reset_input()
            elif self.input.key("X"):
                self.current_window = "collection"
                self.input.reset_input()
            elif self.input.key("MENUF"):
                self.input.reset_input()
                ui.draw_end()
                sys.exit()
            else:
                self.platforms_selected_position = self.input.handle_navigation(
                    self.platforms_selected_position,
                    self.max_n_platforms,
                    len(self.platforms),
                )

    def _render_collections_view(self):
        ui.draw_header(self.romm_provider.host, self.romm_provider.username)
        if self.valid_host:
            if self.valid_credentials:
                ui.draw_platforms_list(
                    self.collections_selected_position,
                    self.max_n_collections,
                    self.collections,
                    fill=ui.colorYellow,
                )
                ui.button_circle((30, 460), "A", "Select", color=ui.colorRed)
                ui.button_circle((133, 460), "Y", "Refresh", color=ui.colorGreen)
                ui.button_circle(
                    (243, 460),
                    "X",
                    "Collections" if self.current_window == "platform" else "Platforms",
                    color=ui.colorBlue,
                )
                ui.button_circle((380, 460), "M", "Exit")
            else:
                ui.draw_text((25, 55), "Error: Permission denied")
                ui.button_circle((30, 460), "M", "Exit")
        else:
            ui.draw_text((25, 55), "Error: Invalid host")
            ui.button_circle((30, 460), "M", "Exit")

    def _update_collections_view(self):
        if self.valid_host and self.valid_credentials:
            if self.input.key("A"):
                ui.draw_log("Fetching roms...")
                collections_id = self.collections[self.collections_selected_position][1]
                self.roms, self.valid_host, self.valid_credentials = (
                    self.romm_provider.get_roms(self.current_window, collections_id)
                )
                self.selected_bucket = "collection"
                self.current_window = "roms"
                self.input.reset_input()
            elif self.input.key("Y"):
                ui.draw_log("Fetching collections...")
                self.collections, self.valid_host, self.valid_credentials = (
                    self.romm_provider.get_collections()
                )
                self.input.reset_input()
            elif self.input.key("X"):
                self.current_window = "platform"
                self.input.reset_input()
            elif self.input.key("MENUF"):
                self.input.reset_input()
                ui.draw_end()
                sys.exit()
            else:
                self.collections_selected_position = self.input.handle_navigation(
                    self.collections_selected_position,
                    self.max_n_collections,
                    len(self.collections),
                )

    def _render_roms_view(self):
        ui.draw_header(self.romm_provider.host, self.romm_provider.username)
        header_text = (
            self.platforms[self.platforms_selected_position][0]
            if self.selected_bucket == "platform"
            else self.collections[self.collections_selected_position][0]
        )
        header_color = (
            ui.colorViolet if self.selected_bucket == "platform" else ui.colorYellow
        )
        ui.draw_roms_list(
            self.roms_selected_position,
            self.max_n_roms,
            self.roms,
            header_text,
            header_color,
            self.multi_selected_roms,
            prepend_platform_slug=self.selected_bucket == "collection",
        )
        ui.button_circle((30, 460), "A", "Download", color=ui.colorRed)
        ui.button_circle((145, 460), "B", "Back", color=ui.colorYellow)
        ui.button_circle((225, 460), "Y", "Refresh", color=ui.colorGreen)
        ui.button_circle(
            (330, 460), "X", f"SD: {self.fs.get_sd_storage()}", color=ui.colorBlue
        )
        ui.button_circle((420, 460), "M", "Exit")

    def _update_roms_view(self):
        if self.valid_host and self.valid_credentials:
            if self.input.key("A"):
                if len(self.multi_selected_roms) == 0:
                    self.multi_selected_roms.append(
                        self.roms[self.roms_selected_position]
                    )

                for rom in self.multi_selected_roms:
                    ui.draw_log(f"Downloading {rom[0]} ({rom[1]})")
                    dest_path = os.path.join(
                        self.fs.get_sd_storage_platform_path(rom[2]),
                        rom[1],
                    )

                    self.valid_host, self.valid_credentials = (
                        self.romm_provider.download_rom(rom, dest_path)
                    )
                    if self.valid_host and self.valid_credentials:
                        ui.draw_log(
                            f"Downloaded to\n{dest_path}",
                            lines=2,
                        )
                    elif not self.valid_host:
                        ui.draw_log("Error: Invalid host")
                        self.valid_host = True
                    elif not self.valid_credentials:
                        ui.draw_log("Error: Permission denied")
                        self.valid_credentials = True
                    else:
                        ui.draw_log(
                            "Error: Invalid host or permission denied",
                        )
                    time.sleep(2)
                self.multi_selected_roms = []
                self.input.reset_input()
            elif self.input.key("B"):
                self.current_window = self.selected_bucket
                self.romm_provider.reset_roms_list()
                self.roms_selected_position = 0
                self.multi_selected_roms = []
                self.input.reset_input()
            elif self.input.key("Y"):
                ui.draw_log("Fetching roms...")
                bucket_id = (
                    self.platforms[self.platforms_selected_position][1]
                    if self.selected_bucket == "platform"
                    else self.collections[self.collections_selected_position][1]
                )
                self.roms, self.valid_host, self.valid_credentials = (
                    self.romm_provider.get_roms(
                        self.selected_bucket, bucket_id, refresh=True
                    )
                )
                self.multi_selected_roms = []
                self.input.reset_input()
            elif self.input.key("X"):
                current = self.fs.get_sd_storage()
                self.fs.switch_sd_storage()
                new = self.fs.get_sd_storage()
                if new == current:
                    ui.draw_log(
                        f"Error: Couldn't find path {self.fs.get_sd2_storage_path()}",
                    )
                else:
                    ui.draw_log(
                        f"Set download path to SD {self.fs.get_sd_storage()}: {self.fs.get_sd_storage_platform_path(self.roms[self.roms_selected_position][2])}",
                    )
                time.sleep(2)
                self.input.reset_input()
            elif self.input.key("SELECT"):
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
            elif self.input.key("MENUF"):
                self.input.reset_input()
                ui.draw_end()
                sys.exit()
            else:
                self.roms_selected_position = self.input.handle_navigation(
                    self.roms_selected_position, self.max_n_roms, len(self.roms)
                )

    def update(self):
        ui.draw_clear()
        if self.current_window == "platform":
            self._render_platforms_view()
            self._update_platforms_view()
        elif self.current_window == "collection":
            self._render_collections_view()
            self._update_collections_view()
        elif self.current_window == "roms":
            self._render_roms_view()
            self._update_roms_view()
        else:
            self._render_platforms_view()
            self._update_platforms_view()
        ui.draw_update()
