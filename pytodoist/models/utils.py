from uuid import uuid4


def str_uuid4_factory():
    """Factory method for generating UUID's as string"""
    return str(uuid4())
