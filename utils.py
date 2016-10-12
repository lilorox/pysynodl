def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def human_sizeof(num):
    for x in ['B', 'KB', 'MB', 'GB']:
        if(num < 1024.0):
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')
