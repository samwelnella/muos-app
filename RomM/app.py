from romm.romm import RomM
import graphic as gr
import input
import sys
import time
from filesystem.filesystem import Filesystem

romm_provider = RomM()
selected_position = 0
roms_selected_position = 0
platforms = []
roms = []
current_window = "platforms"
max_n_platforms = 11
max_n_roms = 10
fs = Filesystem()
skip_input_check = False


def start():
	global current_window, romm_provider, platforms
	current_window == "console"
	platforms = romm_provider.get_platforms()
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
	global romm_provider, selected_position, platforms, current_window, skip_input_check, roms

	if input.key("DY"):
		if input.value == 1:
			if selected_position == len(platforms) - 1:
				selected_position = 0
			elif selected_position < len(platforms) - 1:
				selected_position += 1
		elif input.value == -1:
			if selected_position == 0:
				selected_position = len(platforms) -1
			elif selected_position > 0:
				selected_position -= 1
	elif input.key("A"):
		current_window = "roms"
		gr.draw_log("Fetching ROMs...", fill=gr.colorViolet, outline=gr.colorViolet)
		gr.draw_paint()
		skip_input_check = True
		platform_id = platforms[selected_position][1]
		roms = romm_provider.get_roms(platform_id)
		return
	elif input.key("Y"):
		gr.draw_log("Refreshing...", fill=gr.colorViolet, outline=gr.colorViolet)
		gr.draw_paint()
		skip_input_check = True
		platforms = romm_provider.get_platforms()
		skip_input_check = False

	gr.draw_clear()

	# Header
	gr.draw_text((15, 10), f"RomM | Host: {romm_provider.host} | User: {romm_provider.username}")

	# Platforms list
	gr.draw_rectangle_r([10, 40, 630, 440], 15, fill=gr.colorGrayD2, outline=None)
	start_idx = int(selected_position / max_n_platforms) * max_n_platforms
	end_idx = start_idx + max_n_platforms
	for i, p in enumerate(platforms[start_idx:end_idx]):
		row_list(f"{p[0]} ({p[2]})" if len(p[0]) <= 55 else p[0][:55] + f"... ({p[2]})", (20, 50 + (i * 35)), 600, i == (selected_position % max_n_platforms))

	button_circle((30, 460), "A", "Select")
	button_circle((133, 460), "Y", "Refresh")
	button_circle((243, 460), "M", "Exit")

	gr.draw_paint()


def load_roms_menu():
	global romm_provider, selected_position, platforms, roms, current_window, roms_selected_position, skip_input_check

	if len(roms) < 1:
		current_window = "platforms"
		gr.draw_clear()
		return

	if input.key("A"):
		skip_input_check = True
		gr.draw_log(f"Downloading...", fill=gr.colorViolet, outline=gr.colorViolet)
		gr.draw_paint()
		dest_path = romm_provider.download_rom(roms[roms_selected_position])
		gr.draw_log(f"Downloaded to {dest_path}", fill=gr.colorViolet, outline=gr.colorViolet)
		gr.draw_paint()
		time.sleep(3)
		skip_input_check = False
	elif input.key("B"):
		current_window = "platforms"
		gr.draw_clear()
		romm_provider.reset_roms_list()
		roms_selected_position = 0
		skip_input_check = True
		platforms = romm_provider.get_platforms()
		skip_input_check = False
		return
	elif input.key("Y"):
		gr.draw_log("Refreshing...", fill=gr.colorViolet, outline=gr.colorViolet)
		gr.draw_paint()
		skip_input_check = True
		platform_id = platforms[selected_position][1]
		roms = romm_provider.get_roms(platform_id, refresh=True)
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
				roms_selected_position = len(roms) -1
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
	platform_name = platforms[selected_position][0]
	gr.draw_text((15, 10), f"RomM | Host: {romm_provider.host} | User: {romm_provider.username}")
	gr.draw_text((15, 35), f" - {platform_name} - ", color=gr.colorViolet)

	# ROMs list
	gr.draw_rectangle_r([10, 60, 630, 430], 15, fill=gr.colorGrayD2, outline=None)
	start_idx = int(roms_selected_position / max_n_roms) * max_n_roms
	end_idx = start_idx + max_n_roms
	for i, r in enumerate(roms[start_idx:end_idx]):
		row_list(r[0] if len(r[0]) <= 55 else r[0][:55] + f"... {r[5]}", (20, 70 + (i * 35)), 600, i == (roms_selected_position % max_n_roms))
	
	button_circle((30, 460), "A", "Download")
	button_circle((145, 460), "B", "Back")
	button_circle((225, 460), "Y", "Refresh")
	button_circle((330, 460), "X", f"SD: {fs.get_sd_storage()}")
	button_circle((420, 460), "M", "Exit")
	gr.draw_paint()

	return


def row_list(text, pos, width, selected, fill=None):
	gr.draw_rectangle_r([pos[0], pos[1], pos[0]+width, pos[1]+32], 5, fill=(gr.colorViolet if selected else gr.colorGrayL1))
	gr.draw_text((pos[0]+5, pos[1] + 5), text)


def button_circle(pos, button, text):
	gr.draw_circle(pos, 15, fill=gr.colorViolet, outline=None)
	gr.draw_text(pos, button, anchor="mm")
	gr.draw_text((pos[0] + 20, pos[1]), text, font=13, anchor="lm")
