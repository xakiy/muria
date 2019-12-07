from importlib import import_module


class EntityMixin(object):
    schema = None
    # NOTE: I think it is better to incorporate this functionality
    #       inside the entity itself when they do object instantiation.

    @classmethod
    def init(cls):
        cls.__module = import_module("muria.db.schema")
        sch = cls.__getattribute__(cls, '__name__')
        if hasattr(cls.__module, sch):
            cls.schematic = getattr(cls.__module, sch)
            if not isinstance(cls.schema, cls.schematic):
                cls.schema = cls.schematic()

    def unload(self):
        """Return serialized data or raise error."""

        self.init()
        return self.schema.dump(self)

    @classmethod
    def clean(cls, data, **kwargs):
        """Return deserialized data or throws error."""
        # NOTE: to prevent method naming collision from pony entity
        #       we name it 'clean' instead of 'load'.
        #       Since marshmallow 3.0.0b7 `load` will return deserialized data
        #       instead of tuple of (data, errors), so you need to catch
        #       the error.

        cls.init()
        return cls.schema.load(data, **kwargs)

    def validate(cls, data, **kwargs):
        """Return ValidationError dict."""
        cls.init()
        return cls.schema.validate(data, **kwargs)
