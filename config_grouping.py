# configurations for grouping

# expected number of batches in a day
GROUPS_IN_A_DAY = 48

# >4x highest processing time (in seconds) between two consecutive images
THRESHOLD = 41


def load_camera_names(file_name):
    """Returns a list with the references of the cameras.

    The source is a file with cameras preset names.
    """
    try:
        with open(file_name, 'r') as fp:
            camera_ref_names = fp.read().splitlines()
            return camera_ref_names
    except Exception as error:
        print('Error while reading file:', error)


def append_new_cameras(cameras):
    """Appends new cameras/presets to source list.

    The source is a Set data type from the grouping script.
    """
    try:
        with open('camera_ref.names', 'a') as fp:
            fp.writelines('\n'.join(cameras))
    except Exception as error:
        print('Error while reading file:', error)
