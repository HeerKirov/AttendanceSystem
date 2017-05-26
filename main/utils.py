def check_crossing(a_min, a_max, b_min, b_max):
    """
    检测两个标量区间是否相交。
    :param a_min: 
    :param a_max: 
    :param b_min: 
    :param b_max: 
    :return: 
    """
    return a_min <= a_max and a_min <= b_max and b_min <= a_max and b_min <= b_max


def check_in(a, b_min, b_max):
    """
    检测目标标量是否在标量区间之内。
    :param a: 
    :param b_min: 
    :param b_max: 
    :return: 
    """
    return b_min <= a <= b_max


def date_to_str(year, month, day):
    return '%04d-%02d-%02d' % (year, month, day,)


def time_to_str(hour, minute, second):
    return "%02d:%02d:%02d" % (hour, minute, second)


def datetime_to_str(year, month, day, hour, minute, second):
    return '%04d-%02d-%02d %02d:%02d:%02d' % (year, month, day, hour, minute, second)
