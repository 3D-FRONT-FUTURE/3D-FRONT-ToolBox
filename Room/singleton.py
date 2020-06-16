# # -*- coding: utf-8 -*


def Singleton(class_):
    """
    :param class_:
    :return:
    """
    instance = {}

    def get_instance(*args, **kwargs):
        if class_ not in instance:
            instance[class_] = class_(*args, ** kwargs)
        return instance[class_]
    return get_instance
