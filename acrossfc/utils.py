from enum import Enum


def to_enum(cls, val):
    """Convenience method to take in any value type and try to turn it into an Enum instance"""
    assert issubclass(cls, Enum)
    if val in cls:
        return cls(val)
    elif val in cls.__members__:
        return cls[val]
    elif type(val) is cls:
        return cls(val)
    elif (type(val) is str) and val.isdigit() and ((v := int(val)) in cls):
        return cls(v)
    else:
        raise ValueError(f"Unable to convert {val} into an instance of {cls}")


def setup_utils():
    Enum.to_enum = classmethod(to_enum)
