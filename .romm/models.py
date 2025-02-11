from collections import namedtuple

Rom = namedtuple(
    "Rom",
    [
        "id",
        "name",
        "file_name",
        "platform_slug",
        "file_extension",
        "file_size",
        "file_size_bytes",
    ],
)
Collection = namedtuple("Collection", ["id", "name", "rom_count"])
Platform = namedtuple("Platform", ["id", "display_name", "slug", "rom_count"])
