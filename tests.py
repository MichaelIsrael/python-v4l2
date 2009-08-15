"""
Tests for Python bindings for the v4l2 userspace api
"""

import os
import v4l2


#
# validators
#


def valid_string(string):
    for char in string:
        if (ord(char) < 32 or 126 < ord(char)):
            return False
    return True


def valid_v4l2_std_id(std_id):
    return std_id & ~ (
        v4l2.V4L2_STD_PAL_B |
        v4l2.V4L2_STD_PAL_B1 |
        v4l2.V4L2_STD_PAL_G |
        v4l2.V4L2_STD_PAL_H |
        v4l2.V4L2_STD_PAL_I |
        v4l2.V4L2_STD_PAL_D |
        v4l2.V4L2_STD_PAL_D1 |
        v4l2.V4L2_STD_PAL_K |
        v4l2.V4L2_STD_PAL_M |
        v4l2.V4L2_STD_PAL_N |
        v4l2.V4L2_STD_PAL_Nc |
        v4l2.V4L2_STD_PAL_60 |
        v4l2.V4L2_STD_NTSC_M |
        v4l2.V4L2_STD_NTSC_M_JP |
        v4l2.V4L2_STD_NTSC_443 |
        v4l2.V4L2_STD_NTSC_M_KR |
        v4l2.V4L2_STD_SECAM_B |
        v4l2.V4L2_STD_SECAM_D |
        v4l2.V4L2_STD_SECAM_G |
        v4l2.V4L2_STD_SECAM_H |
        v4l2.V4L2_STD_SECAM_K |
        v4l2.V4L2_STD_SECAM_K1 |
        v4l2.V4L2_STD_SECAM_L |
        v4l2.V4L2_STD_SECAM_LC |
        v4l2.V4L2_STD_ATSC_8_VSB |
        v4l2.V4L2_STD_ATSC_16_VSB) == 0


def valid_capabilities(capabilities):
    return capabilities & ~ (
        v4l2.V4L2_CAP_VIDEO_CAPTURE |
        v4l2.V4L2_CAP_VIDEO_OUTPUT |
        v4l2.V4L2_CAP_VIDEO_OVERLAY |
        v4l2.V4L2_CAP_VBI_CAPTURE |
        v4l2.V4L2_CAP_VBI_OUTPUT |
        v4l2.V4L2_CAP_SLICED_VBI_CAPTURE |
        v4l2.V4L2_CAP_SLICED_VBI_OUTPUT |
        v4l2.V4L2_CAP_RDS_CAPTURE |
        v4l2.V4L2_CAP_VIDEO_OUTPUT_OVERLAY |
        v4l2.V4L2_CAP_TUNER |
        v4l2.V4L2_CAP_AUDIO |
        v4l2.V4L2_CAP_RADIO |
        v4l2.V4L2_CAP_READWRITE |
        v4l2.V4L2_CAP_ASYNCIO |
        v4l2.V4L2_CAP_STREAMING) == 0


def valid_input_status(status):
    return status & (
        v4l2.V4L2_IN_ST_NO_POWER |
        v4l2.V4L2_IN_ST_NO_SIGNAL |
        v4l2.V4L2_IN_ST_NO_COLOR |
        v4l2.V4L2_IN_ST_NO_H_LOCK |
        v4l2.V4L2_IN_ST_COLOR_KILL |
        v4l2.V4L2_IN_ST_NO_SYNC |
        v4l2.V4L2_IN_ST_NO_EQU |
        v4l2.V4L2_IN_ST_NO_CARRIER |
        v4l2.V4L2_IN_ST_MACROVISION |
        v4l2.V4L2_IN_ST_NO_ACCESS |
        v4l2.V4L2_IN_ST_VTR)


#
# tests
#

def test_VIDIOC_QUERYCAP(fd):
    cap = v4l2.v4l2_capability()

    v4l2.ioctl(fd, v4l2.VIDIOC_QUERYCAP, cap)

    assert 0 < len(cap.driver)
    assert valid_string(cap.card)
    # bus_info is allowed to be an empty string
    assert valid_string(cap.bus_info)
    assert valid_capabilities(cap.capabilities)
    assert cap.reserved[0] == 0
    assert cap.reserved[1] == 0
    assert cap.reserved[2] == 0
    assert cap.reserved[3] == 0


def test_VIDIOC_QUERYCAP_NULL(fd):
    try:
        v4l2.ioctl(fd, v4l2.VIDIOC_QUERYCAP, None)
    except TypeError, e:
        pass


def test_VIDIOC_ENUMINPUT(fd):
    cap = v4l2.v4l2_capability()
    v4l2.ioctl(fd, v4l2.VIDIOC_QUERYCAP, cap)

    if not cap.capabilities & v4l2.V4L2_CAP_VIDEO_CAPTURE:
        return
    
    original_index = v4l2.ctypes.c_int()
    v4l2.ioctl(fd, v4l2.VIDIOC_G_INPUT, original_index)

    index = 0
    while True:
        input_ = v4l2.v4l2_input(index)
        try:
            v4l2.ioctl(fd, v4l2.VIDIOC_ENUMINPUT, input_)
        except IOError, e:
            assert e.errno == os.errno.EINVAL
            break

        v4l2.ioctl(fd, v4l2.VIDIOC_S_INPUT, v4l2.ctypes.c_int(input_.index))

        assert input_.index == index
        assert valid_string(input_.name)
        assert input_.type & (
            v4l2.V4L2_INPUT_TYPE_CAMERA | v4l2.V4L2_INPUT_TYPE_TUNER)
        assert input_.audioset < 32
        assert valid_v4l2_std_id(input_.std)
        if input_.status:
            assert valid_input_status(status)
        assert input_.reserved[0] == 0
        assert input_.reserved[1] == 0
        assert input_.reserved[2] == 0
        assert input_.reserved[3] == 0

        index += 1

    v4l2.ioctl(fd, v4l2.VIDIOC_S_INPUT, original_index)


#
# bootstrap
#

devices = None


def open_devices():
    import glob
    global devices
    if devices is None:
        devices = [
            open(device, 'rw')
            for device in glob.glob('/dev/video*')]
        assert devices, 'No video devices found.'


def pytest_generate_tests(metafunc):
    open_devices()
    for fd in devices:
        metafunc.addcall(funcargs=dict(fd=fd))


if __name__ == '__main__':
    def run():
        import sys
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
