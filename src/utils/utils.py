def intersection(a: list, b: list, equal: callable) -> list:
    """
    求两个数组的交集
    :param a: 数组a
    :param b: 数组b
    :param equal: 判断两个元素是否相等的函数
    :return: 交集
    """
    return list(filter(lambda x: any(map(lambda y: equal(x, y), b)), a))


def difference(a: list, b: list, equal: callable) -> list:
    """
    求两个数组的差集
    :param a: 数组a
    :param b: 数组b
    :param equal: 判断两个元素是否相等的函数
    :return: 差集
    """
    return list(filter(lambda x: not any(map(lambda y: equal(x, y), b)), a))


def union(a: list, b: list, equal: callable) -> list:
    """
    求两个数组的并集
    :param a: 数组a
    :param b: 数组b
    :param equal: 判断两个元素是否相等的函数
    :return: 并集
    """
    return a + difference(b, a, equal)