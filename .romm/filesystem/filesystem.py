import os


class Filesystem:

    def __init__(self):
        self.__sd1_rom_storage_path = "/mnt/mmc/roms"
        self.__sd2_rom_storage_path = "/mnt/sdcard/roms"
        self.__current_sd = 2 if os.path.exists(self.__sd2_rom_storage_path) else 1

    def get_sd1_storage_path(self):
        return self.__sd1_rom_storage_path

    def get_sd2_storage_path(self):
        return self.__sd1_rom_storage_path

    def get_sd1_storage_platform_path(self, platform):
        return os.path.join(self.__sd1_rom_storage_path, platform)

    def get_sd2_storage_platform_path(self, platform):
        return os.path.join(self.__sd2_rom_storage_path, platform)

    def set_sd_storage(self, sd):
        if sd == 1:
            self.__current_sd = sd
        elif sd == 2 and os.path.exists(self.__sd2_rom_storage_path):
            self.__current_sd = sd

    def get_sd_storage(self):
        return self.__current_sd

    def switch_sd_storage(self):
        if self.__current_sd == 1 and os.path.exists(self.__sd2_rom_storage_path):
            self.__current_sd = 2
        else:
            self.__current_sd = 1

    def get_sd_storage_path(self):
        if self.__current_sd == 1:
            return self.get_sd1_storage_path()
        else:
            return self.get_sd2_storage_path()

    def get_sd_storage_platform_path(self, platform):
        if self.__current_sd == 1:
            return self.get_sd1_storage_platform_path(platform)
        else:
            return self.get_sd2_storage_platform_path(platform)
