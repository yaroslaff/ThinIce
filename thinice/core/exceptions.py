class ThinIceError(Exception):
    pass

class ArchiveNotRetrieved(ThinIceError):
    pass

class NoInventory(ThinIceError):
    pass

class InventoryJobActive(ThinIceError):
    """ do not initiated new job because already have it """
    pass

class InventoryIsOlder(ThinIceError):
    pass

class InventoryIsSame(ThinIceError):
    pass

