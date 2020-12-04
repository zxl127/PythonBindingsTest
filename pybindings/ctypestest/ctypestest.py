from invoke import task
from ctypes import *
import pathlib


ubox = CDLL(pathlib.Path().absolute()/'ctypestest'/'libubox.so')


class uloop_fd(Structure):
    pass


uloop_fd_handler = CFUNCTYPE(None, POINTER(uloop_fd), c_uint)
uloop_fd._fields_ = [
        ('cb', uloop_fd_handler),
        ('fd', c_int),
        ('eof', c_bool),
        ('error', c_bool),
        ('registered', c_bool),
        ('flags', c_uint8)
    ]


def client_fd_cb(u, events):
    print('new data to read')
    client_fd = u.contents
    array = c_char * 64
    buf = array()
    ubox.read.restype = c_int
    print(client_fd.fd)
    ret = ubox.read(client_fd.fd, pointer(buf), 64)
    if ret < 0:
        print('read error')
        ubox.uloop_fd_delete(u)
    for i in range(ret):
        print(buf[i], end=' ')


def server_fd_cb(u, events):
    print('new connect')
    server_fd = u.contents
    ubox.accept.restype = c_int
    sock = ubox.accept(server_fd.fd, None, None)
    print('client socket: ', sock)
    if sock < 0:
        return
    global client_fd
    client_fd = uloop_fd()
    client_fd.fd = sock
    client_fd.cb = uloop_fd_handler(client_fd_cb)
    ubox.uloop_fd_add.restype = c_int
    ret = ubox.uloop_fd_add(pointer(client_fd), 1 << 0)
    if ret < 0:
        print('uloop_fd_add error')

@task
def ctypetest(c):
    ubox.uloop_init.restype = c_int
    ret = ubox.uloop_init()
    if ret < 0:
        print('uloop_init error')
        return

    ubox.usock.restype = c_int
    host = c_char_p(b'127.0.0.1')
    service = c_char_p(b'7777')
    fd = ubox.usock(0x0 | 0x0100, host, service)
    print(f'sock: {fd}')
    if fd < 0:
        print('usock error')

    server_fd = uloop_fd()
    server_fd.fd = fd
    server_fd.cb = uloop_fd_handler(server_fd_cb)
    ubox.uloop_fd_add.restype = c_int
    ret = ubox.uloop_fd_add(pointer(server_fd), 1 << 0)
    if ret < 0:
        print('uloop_fd_add error')
    
    ubox.uloop_run_timeout.restype = c_int
    ret = ubox.uloop_run_timeout(-1)
    if ret < 0:
        print('uloop_run error')
        return
    ubox.uloop_end()
