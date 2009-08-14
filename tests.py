# Uses the vivi virtual test video device.  Run 'sudo modprobe vivi'
# before and 'sudo modprobe -r vivi' after.  As an example, you can
# run this test suite like this:

# sudo modprobe vivi && python tests.py && sudo modprobe -r vivi

"""
>>> import v4l2

>>> vd
<open file ..., mode 'rw' at ...>

"""

def run(fd):
    import doctest
    vd = open(fd, 'rw')
    doctest.testmod(optionflags=doctest.ELLIPSIS, extraglobs={'vd': vd})
    vd.close()


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        sys.stderr.write(
            '%s: ERROR: Specify the vivi (virtual test video) '
            'device as an argument.\n' % sys.argv[0])
        sys.exit(1)
    run(fd=sys.argv[1])
