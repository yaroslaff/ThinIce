class ThinIceError(Exception):
    pass

class ArchiveNotRetrieved(ThinIceError):
    pass

class NoInventory(ThinIceError):
    pass

class InventoryJobActive(ThinIceError):
    pass