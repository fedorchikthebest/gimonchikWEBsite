import uuid

def update_ip(ip):
    with open('loggined_ip.txt', 'w') as f:
        f.write(ip)


def load_ip():
    with open('loggined_ip.txt') as f:
        return f.read()


def check_key(key):
    with open('key.txt') as f:
        return f.read() == key


def gen_filename(request, name):
    return f'{uuid.uuid1()}.{request.files.get(name).filename.split(".")[-1]}'