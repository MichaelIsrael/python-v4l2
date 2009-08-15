"""
Tests for Python bindings for the v4l2 userspace api

Can be run with or without py.test.
"""

import sys
import glob
import v4l2


#
# tests
#

def test_VIDEO_QUERYCAP(fd):
    capability = v4l2.v4l2_capability()
    assert 0 == v4l2.ioctl(fd, v4l2.VIDIOC_QUERYCAP, capability)
    

def test_VIDEO_ENUMINPUT(fd):
    index = 0
    while True:
        input_ = v4l2.v4l2_input(index)
        try:
            assert 0 == v4l2.ioctl(fd, v4l2.VIDIOC_ENUMINPUT, input_)
        except IOError, e:
            assert e.errno == 22
            break
        index += 1


def test_VIDEO_ENUMOUTPUT(fd):
    index = 0
    while True:
        output = v4l2.v4l2_output(index)
        try:
            assert 0 == v4l2.ioctl(fd, v4l2.VIDIOC_ENUMOUTPUT, output)
        except IOError, e:
            assert e.errno == 22
            break
        index += 1


def test_VIDIOC_G_INPUT(fd):
    index = v4l2.ctypes.c_int(0)
    try:
        assert 0 == v4l2.ioctl(fd, v4l2.VIDIOC_G_INPUT, index)
    except IOError, e:
        assert e.errno == 22


def test_VIDIOC_G_OUTPUT(fd):
    index = v4l2.ctypes.c_int(0)
    try:
        assert 0 == v4l2.ioctl(fd, v4l2.VIDIOC_G_OUTPUT, index)
    except IOError, e:
        assert e.errno == 22


def test_VIDIOC_S_INPUT(fd):
    index = 0
    while True:
        try:
            assert 0 == v4l2.ioctl(
                fd, v4l2.VIDIOC_S_INPUT, v4l2.ctypes.c_int(index))
        except IOError, e:
            assert e.errno == 22
            break
        index += 1


def test_VIDIOC_S_OUTPUT(fd):
    index = 0
    while True:
        try:
            assert 0 == v4l2.ioctl(
                fd, v4l2.VIDIOC_S_OUTPUT, v4l2.ctypes.c_int(index))
        except IOError, e:
            assert e.errno == 22
            break
        index += 1


#
# bootstrap
#

devices = None


def open_devices():
    global devices
    if devices is None:
        devices = [
            open(device, 'rw')
            for device in glob.glob('/dev/video*')]


def pytest_generate_tests(metafunc):
    open_devices()
    for fd in devices:
        metafunc.addcall(funcargs=dict(fd=fd))


if __name__ == '__main__':
    def run():
        open_devices()
        for fd in devices:
            for member in globals():
                if member.startswith('test_'):
                    try:
                        globals()[member](fd)
                    except:
                        sys.stderr.write('fd = %r\n' % fd)
                        raise
    run()
