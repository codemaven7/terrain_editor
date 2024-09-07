



class RomFileSizeError(Exception):
    """Rom file size exception"""

    def __init__(self, file_size, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "A rom file size error occurred. File size was: %d" % file_size
        super(RomFileSizeError, self).__init__(msg)
        self.file_size = file_size






def smc_header(rom_path):

    import os

    file_size = os.stat(rom_path).st_size  # file size

    SMC_header = file_size % 1024  # file_size & 0x03FF == 0x200

    # if file_size % 1024 not in (0, 512):
    if SMC_header not in (0, 512):
        raise RomFileSizeError(file_size, "Improper rom header size.")

    return SMC_header


