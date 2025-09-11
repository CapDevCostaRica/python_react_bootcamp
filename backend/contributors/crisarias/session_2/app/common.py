def getFilterDictionary(request):
    filter_dict = {}
    for key in request.args:
        if key.startswith('filters[') and key.endswith(']'):
            field = key[8:-1]
            filter_dict[field] = request.args.get(key)
    return filter_dict
