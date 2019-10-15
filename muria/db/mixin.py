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
        """Return serialized data or raise error."""

        self.init()
        return self.schema.dump(self)

    def clean(self, data):
        """Return deserialized data or raise error."""
        # NOTE: to prevent method naming collision from pony entity
        #       we name it 'clean' instead of 'load'.

        self.init()
        return self.schema.load(data)
