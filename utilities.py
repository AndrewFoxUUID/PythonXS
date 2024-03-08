uuid_iterator = -1

def uuid():
    global uuid_iterator
    uuid_iterator += 1
    return str(uuid_iterator)