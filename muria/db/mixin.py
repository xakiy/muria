from importlib import import_module


class EntityMixin(object):
    schema = None

    def init(self):
        self.__module = import_module("muria.db.schema")
        sch = "_%s" % self.__class__.__name__
        # print(self.__module, sch, hasattr(self.__module, sch))
        if hasattr(self.__module, sch):
            self.schematic = getattr(self.__module, sch)
            if not isinstance(self.schema, self.schematic):
                self.schema = self.schematic()

    def unload(self):
        """Return tuple of data and error if any."""

        self.init()
        data, error = self.schema.dump(self)
        return data

    def clean(self, data):
        """Validate dict data and return tuple of data and error."""

        self.init()
        return self.schema.load(data)
