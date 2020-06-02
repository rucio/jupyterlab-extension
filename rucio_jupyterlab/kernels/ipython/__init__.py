def load_ipython_extension(ipython):
    ipython.push({'did': resolve_did})


def unload_ipython_extension(ipython):
    pass


def resolve_did(did):
    return '/eos/rucio/' + did
