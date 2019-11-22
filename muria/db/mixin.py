from importlib import import_module


class EntityMixin(object):
    schema = None

    def init(self):
        self.__module = import_module("muria.db.schema")
        sch = "_%s" % self.__class__.__name__
        if hasattr(self.__module, sch):
            self.schematic = getattr(self.__module, sch)
            if not isinstance(self.schema, self.schematic):
                self.schema = self.schematic()

    def unload(self):
        """Return serialized data or raise error."""

        self.init()
        return self.schema.dump(self)

    def clean(self, data, partial=None):
        """Return deserialized data or throws error."""
        # NOTE: to prevent method naming collision from pony entity
        #       we name it 'clean' instead of 'load'.
        #       Since marshmallow 3.0.0b7 `load` will return deserialized data
        #       instead of tuple of (data, errors), so you need to catch
        #       the error.

        self.init()
        return self.schema.load(data, partial=partial)
