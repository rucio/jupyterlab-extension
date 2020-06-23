def find(pred, iterable):
    for element in iterable:
        if pred(element):
            return element
    return None


def map(iterable, mapper):
    result = []
    i = 0
    for element in iterable:
        result.append(mapper(element, i))
        i += 1
    return result


def filter(iterable, filter):
    result = []
    i = 0
    for element in iterable:
        if filter(element, i):
            result.append(element)
        i += 1
    return result
