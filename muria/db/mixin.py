from importlib import import_module


class EntityMixin(object):
    schema = None

    def init(self):
        self.__module = import_module("schema")
        sch = "_%s" % self.__class__.__name__
        # print(self.__module, sch, hasattr(self.__module, sch))
        if hasattr(self.__module, sch):
            self.schematic = getattr(self.__module, sch)
            if not isinstance(self.schema, self.schematic):
                self.schema = self.schematic()

    @property
    def as_dict(self):
        """Return tuple of data and error if any."""

        self.init()
        return self.schema.dump(self)

    def validate(self, data):
        """Validate given dict argument."""

        self.init()
        return self.schema.validate(data)
