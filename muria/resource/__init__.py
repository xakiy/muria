from muria.init import config


class Resource(object):
    """Resource Base Class."""

    def __init__(self, config=config, **params):
        self.config = config
