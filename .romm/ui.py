import mmap
import os
from fcntl import ioctl

from PIL import Image, ImageDraw, ImageFont

fb: any
mm: any
screen_width = 640
screen_height = 480
bytes_per_pixel = 4
screen_size = screen_width * screen_height * bytes_per_pixel

fontFile = {}
fontFile[15] = ImageFont.truetype(
    "/usr/share/fonts/liberation/LiberationMono-Regular.ttf", 15
)
fontFile[13] = ImageFont.truetype(
    "/usr/share/fonts/liberation/LiberationMono-Regular.ttf", 13
)
fontFile[11] = ImageFont.truetype(
    "/usr/share/fonts/liberation/LiberationMono-Regular.ttf", 11
)
colorViolet = "#ad3c6b"
colorGreen = "#41aa3b"
colorRed = "#3c3cad"
colorBlue = "#bb7200"
colorYellow = "#3b80aa"
colorGrayL1 = "#383838"
colorGrayD2 = "#141414"

activeImage: Image.Image
activeDraw: ImageDraw.ImageDraw


def screen_reset():
    ioctl(
        fb,
        0x4601,
        b"\x80\x02\x00\x00\xe0\x01\x00\x00\x80\x02\x00\x00\xc0\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00^\x00\x00\x00\x96\x00\x00\x00\x00\x00\x00\x00\xc2\xa2\x00\x00\x1a\x00\x00\x00T\x00\x00\x00\x0c\x00\x00\x00\x1e\x00\x00\x00\x14\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    )
    ioctl(fb, 0x4611, 0)


def draw_start():
    global fb, mm
    fb = os.open("/dev/fb0", os.O_RDWR)
    mm = mmap.mmap(fb, screen_size)


def draw_end():
    global mm
    mm.close()
    os.close(fb)


def crate_image():
    image = Image.new("RGBA", (screen_width, screen_height), color="black")
    return image


def draw_active(image):
    global activeImage, activeDraw
    activeImage = image
    activeDraw = ImageDraw.Draw(activeImage)


def draw_update():
    mm.seek(0)
    mm.write(activeImage.tobytes())


def draw_clear():
    activeDraw.rectangle([0, 0, screen_width, screen_height], fill="black")


def draw_text(position, text, font=15, color="white", **kwargs):
    activeDraw.text(position, text, font=fontFile[font], fill=color, **kwargs)


def draw_rectangle(position, fill=None, outline=None, width=1):
    activeDraw.rectangle(position, fill=fill, outline=outline, width=width)


def draw_rectangle_r(position, radius, fill=None, outline=None):
    activeDraw.rounded_rectangle(position, radius, fill=fill, outline=outline)


def row_list(text, pos, width, height, selected, fill=colorViolet, outline=None):
    radius = 5
    draw_rectangle_r(
        [pos[0], pos[1], pos[0] + width, pos[1] + height],
        radius,
        fill=(fill if selected else colorGrayL1),
        outline=outline,
    )
    draw_text((pos[0] + 10, pos[1] + 10), text)


def draw_circle(position, radius, fill=None, outline="white"):
    activeDraw.ellipse(
        [
            position[0] - radius,
            position[1] - radius,
            position[0] + radius,
            position[1] + radius,
        ],
        fill=fill,
        outline=outline,
    )


def button_circle(pos, button, text, color=colorViolet):
    radius = 10
    btn_text_offset = 1
    label_margin_l = 20
    draw_circle(pos, radius, fill=color, outline=None)
    draw_text((pos[0] + btn_text_offset, pos[1] + btn_text_offset), button, anchor="mm")
    draw_text((pos[0] + label_margin_l, pos[1]), text, font=13, anchor="lm")


def draw_log(text, fill="Black", outline="black", text_color="white", lines=1):
    margin_bg = 5
    margin_bg_bottom = 40
    radius_bg = 5
    max_len_text = 65
    margin_text = 15
    margin_text_bottom = 30
    max_len_text_multiline = 79
    margin_text_multiline = 15
    margin_text_bottom_multiline = 38
    draw_rectangle_r(
        [
            margin_bg,
            screen_height - margin_bg_bottom,
            screen_width - margin_bg,
            screen_height - margin_bg,
        ],
        radius_bg,
        fill=fill,
        outline=outline,
    )
    if lines == 2:
        draw_text(
            (margin_text_multiline, screen_height - margin_text_bottom_multiline),
            (
                text
                if len(text) <= max_len_text_multiline
                else text[:max_len_text_multiline] + "..."
            ),
            color=text_color,
        )
    else:
        draw_text(
            (margin_text, screen_height - margin_text_bottom),
            text if len(text) <= max_len_text else text[:max_len_text] + "...",
            color=text_color,
        )
    draw_update()  # Update to show log before any api call that can block the render


def draw_header(host, username):
    pos = [screen_width / 2, 20]
    draw_text(
        (pos[0], pos[1]),
        f"RomM | Host: {host} | User: {username}",
        anchor="mm",
    )


def draw_platforms_list(
    platforms_selected_position, max_n_platforms, platforms, fill=colorViolet
):
    draw_rectangle_r([10, 35, 630, 437], 5, fill=colorGrayD2, outline=None)
    start_idx = int(platforms_selected_position / max_n_platforms) * max_n_platforms
    end_idx = start_idx + max_n_platforms
    for i, p in enumerate(platforms[start_idx:end_idx]):
        is_selected = i == (platforms_selected_position % max_n_platforms)
        row_list(
            (
                f"{p.display_name} ({p.rom_count})"
                if len(p.display_name) <= 55
                else p.display_name[:55] + f"... ({p.rom_count})"
            ),
            (20, 45 + (i * 35)),
            600,
            32,
            is_selected,
            fill=fill,
        )


def draw_collections_list(
    collections_selected_position, max_n_collections, collections, fill=colorViolet
):
    draw_rectangle_r([10, 35, 630, 437], 5, fill=colorGrayD2, outline=None)
    start_idx = int(collections_selected_position / max_n_collections) * max_n_collections
    end_idx = start_idx + max_n_collections
    for i, c in enumerate(collections[start_idx:end_idx]):
        is_selected = i == (collections_selected_position % max_n_collections)
        row_list(
            (
                f"{c.name} ({c.rom_count})"
                if len(c.name) <= 55
                else c.name[:55] + f"... ({c.rom_count})"
            ),
            (20, 45 + (i * 35)),
            600,
            32,
            is_selected,
            fill=fill,
        )


def draw_roms_list(
    roms_selected_position,
    max_n_roms,
    roms,
    header_text,
    header_color,
    multi_selected_roms,
    prepend_platform_slug=False,
):
    draw_rectangle_r([10, 37, 630, 100], 5, outline=colorGrayD2)
    draw_text(
        (screen_width / 2, 55),
        header_text,
        color=header_color,
        anchor="mm",
    )

    draw_rectangle_r([10, 70, 630, 437], 0, fill=colorGrayD2, outline=None)
    start_idx = int(roms_selected_position / max_n_roms) * max_n_roms
    end_idx = start_idx + max_n_roms
    max_len_text = 43
    for i, r in enumerate(roms[start_idx:end_idx]):
        is_selected = i == (roms_selected_position % max_n_roms)
        text_offset = 2 if r in multi_selected_roms else 0
        row_text = (
            f"{r.name} [{r.file_size}]"
            if len(r.name) <= max_len_text - text_offset
            else r.name[: max_len_text - text_offset] + f"... [{r.file_size}]"
        )
        if prepend_platform_slug:
            row_text = f"({r.platform_slug}) " + row_text
        if r in multi_selected_roms:
            row_text = f"* {row_text}"
        row_list(
            row_text,
            (20, 80 + (i * 35)),
            600,
            32,
            is_selected,
            fill=header_color,
            outline=header_color if r in multi_selected_roms else None,
        )


def draw_start_menu(option_selected_position, options, fill=colorViolet):
    pos = [screen_width / 3, screen_height / 3]
    padding = 5
    width = 200
    n_options = len(options)
    option_height = 32
    option_height_with_gap = 35
    magic_number = 3  # Can't explain why this is needed, but it is
    draw_rectangle_r(
        [
            pos[0],
            pos[1],
            pos[0] + width + padding * 2,
            n_options * option_height_with_gap + padding * 2 + pos[1] - magic_number,
        ],
        5,
        fill=colorGrayD2,
        outline=colorViolet,
    )
    start_idx = int(option_selected_position / n_options) * n_options
    end_idx = start_idx + n_options
    for i, option in enumerate(options[start_idx:end_idx]):
        is_selected = i == (option_selected_position % n_options)
        row_list(
            option[0],
            (pos[0] + padding, pos[1] + padding + (i * option_height_with_gap)),
            width,
            option_height,
            is_selected,
            fill=fill,
        )


draw_start()
screen_reset()

imgMain = crate_image()
draw_active(imgMain)
