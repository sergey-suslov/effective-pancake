class PublicWrapper():
    def __init__(self, fn, instance) -> None:
        self.fn = fn
        self.instance = instance
        self.public = True

    def __call__(self, *args, **kwargs):
        return self.fn(self.instance, *args, **kwargs)


class PublicMethod(object):
    def __init__(self, func):
        self.calls = 0
        self.func = func

    def __get__(self, instance, owner):
        return PublicWrapper(self.func, instance)
