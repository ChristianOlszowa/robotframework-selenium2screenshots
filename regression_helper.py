""" A Library for doing regression tests.
"""

from robot.libraries.BuiltIn import BuiltIn
from PIL import Image
import os


class RegressionHelper:
    """Library for doing regression tests.

    A Library of Keywords for handling input tasks like selecting and similar.
    """
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LIBRARY_VERSION = 1.0

    @property
    def _current_browser(self):
        """Get browser instance

        :return: Current Browser
        """
        seleniumlib = BuiltIn().get_library_instance('Selenium2Library')
        return seleniumlib._current_browser()

    @staticmethod
    def add_diff_to_log(name):
        return "<img style=\"border-width: 5px; border-style: solid;\" src=\"diff_%s_.png\">" % name

    @staticmethod
    def add_test_to_log(name):
        return "<img style=\"border-width: 5px; border-style: solid;\" src=\"test_%s_.png\">" % name

    @staticmethod
    def generate_test_image_filename(name):
        """Builds the filename with the easy supplied name from the test

        :return: String
        """

        return "test_{}_.png".format(name)

    @staticmethod
    def generate_reference_image_filename(name):
        """Builds the filename with the easy supplied name from the test

        :return: String
        """

        return "ref_{}_.png".format(name)

    @staticmethod
    def generate_diff_image_filename(current_path, name):
        """Gets the path of the test image and builds the filename

        :return: String
        """
        diff_path = os.path.abspath(os.path.dirname(current_path))
        if not diff_path:
            diff_path = "."
        diff_path = diff_path + ("/diff_{}_.png".format(name))
        return diff_path

    @staticmethod
    def get_test_shot_path(path, file_name):
        """Builds the path from the supplied arguments to the current test image
        
        :param path: Testfile output directory from ${OUTPUT_DIR}
        :param file_name: created filename from 'generate_test_image_filename(name)'
        :return: combined path as string
        """
        full_path = path + "/" + file_name
        return full_path

    @staticmethod
    def set_ref_shot_path(file_name, ref_path):
        path = os.path.abspath(os.path.dirname(ref_path))
        full_path = path + "/regression_references/" + file_name
        return full_path

    @staticmethod
    def get_ref_shot_path(name, ref_path):
        """Builds the path to the reference directory from the current location
        
        :param name: Supplied name from the test case
        :param ref_path: Supplied path from robot framework variable to keyword and test directory
        :return: Absolute path with the filename at the end
        """

        # get the actual dir, add the path to ref image and creates the ref image dir if necessary
        path = os.path.abspath(os.path.dirname(ref_path))
        BuiltIn().log(path)

        full_path = path + "/regression_references/"
        BuiltIn().log(full_path)
        check_dir = path + "/regression_references/"
        BuiltIn().log(check_dir)
        if not os.path.exists(full_path):
            os.makedirs(check_dir)
        # returns the ref image file with the supplied name

        ref = "ref_{}_.png".format(name)

        if ref in os.listdir(full_path):
            return os.path.join(full_path, ref)

        message = "No initial \"{}\" in directory \"{}\", please call test in robot-server with -v update:True as option to create it.".format(ref, full_path)
        raise AssertionError(message)

    @staticmethod
    def alter_image(image, greyscale):
        """Alternates the image in color and force it to RGB

        :param image: Path to an image
        :param greyscale: If set to True, both given images will be greyscaled before comparing
        :return: Image 
        """
        image = image.convert("RGB")  # Important
        if greyscale:
            image = image.convert("L")  # Convert it to greyscale.
        return image

    @staticmethod
    def create_diff(img1, img2, diff_path):
        """Compares to given images and stores a difference image under the diff_path 

        :param img1: Path to an image
        :param img2: Path to an image
        :param diff_path: Path where the diff image will be stored
        :return: None
        """

        pink = (255, 0, 128)
        error_count = 0.0
        i1width, i1height = img1.size
        i2width, i2height = img2.size
        pix1 = img1.load()
        pix2 = img2.load()

        max_h = max(i1height, i2height)
        max_w = max(i1width, i2width)
        diff = Image.new('RGB', (max_w, max_h), pink)

        for y in range(0, max_h):
            if y == min(i1height, i2height):
                break
            for x in range(0, max_w):
                if x == min(i1width, i2width):
                    break
                if pix1[x, y] == pix2[x, y]:
                    diff.putpixel((x, y), pix1[x, y])
                    error_count += 1
        error = error_count/(max_h*max_w)
        diff.save(diff_path, 'PNG')
        return error

    @classmethod
    def should_look_like_reference(cls, ref_path, current_path, name, greyscale=False):
        """Keyword `Should Look Like Reference`

        Compares the two given pictures and returns a Boolean

        :param ref_path: Path to an image
        :param current_path: Path to an image
        :param name: Internal name for test_/ref_/diff_NAME_.png images
        :param greyscale: If set to True, both given images will be greyscale before comparing
        :return: True
        """

        # adds the current test image to the logfile
        log_test = RegressionHelper.add_test_to_log(name)
        BuiltIn().log(log_test, html=True)

        # get the images from the filepath
        img1 = Image.open(ref_path.encode("UTF-8"))
        img2 = Image.open(current_path.encode("UTF-8"))

        # force RGB mode
        img1 = cls.alter_image(img1, greyscale)
        img2 = cls.alter_image(img2, greyscale)
        # # draw outlines for better views in report

        message = ''
        diff = RegressionHelper.generate_diff_image_filename(current_path, name)
        relative_error = cls.create_diff(img1, img2, diff)
        error = 100 - (relative_error * 100.0)
        BuiltIn().log("%s%% difference" % error)
        # ToDo: Fix me, fontrendering in FF 45.9.0esr is crappy. Update to FF 53 esr with geckodriver if out and stable.
        if relative_error != 1.0:
        # lazy workaround for trouble caused by fontrender in FF 45.9.0esr
        # if error > 3.8:
            log = RegressionHelper.add_diff_to_log(name)
            BuiltIn().log(log, html=True)
            if not message:
                message = "The element '%s' should look like its reference, " \
                          "but it does not. \nLook at '%s'." % (current_path, os.path.abspath(diff))
            raise AssertionError(message)
        else:
            return True
