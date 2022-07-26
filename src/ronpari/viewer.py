import cv2
import imutils
import screeninfo
from PIL import Image
from PIL import ImageOps


def view_image(path_to_image):
    screen_id = 0
    screen = screeninfo.get_monitors()[screen_id]
    width, height = screen.width, screen.height

    image = Image.open(path_to_image)
    # TODO: method=Image.LANCOZ?
    image = ImageOps.contain(image, (width, height))
    image.show()
    # image.close()
    return

    # screen_id = 0
    # is_color = True
    #
    # # get the size of the screen
    # screen = screeninfo.get_monitors()[screen_id]
    # width, height = screen.width, screen.height
    #
    # image = cv2.imread(path_to_image, cv2.IMREAD_UNCHANGED)
    # image = imutils.resize(image, height=height)
    #
    # window_name = "projector"
    # cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    # cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
    # cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    # cv2.imshow(window_name, image)
    # # while True:
    # cv2.waitKey()
    # cv2.destroyAllWindows()


def view_folder(path_to_folder):
    # TODO: bind keys to next/previous images
    ...
