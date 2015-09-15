#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##
import platform
import os
# Local import
from . import debug
from . import tools
from . import multiprocess
from . import depend

enable_resize_image = True
try:
	if platform.system() == "Darwin":
		import CoreGraphics
	else:
		from PIL import Image
except:
	enable_resize_image = False
	debug.warning("Missing python tools : CoreGraphics (MacOs) or PIL") 

def get_pow_2_multiple(size):
	base = 2
	while size>base:
		base = base * 2
	return base

# TODO : 3 things to do :
#        check if force requested
#        check if time change
#        check if command line change
def resize(src_file, dest_file, x, y, cmd_file=None):
	if enable_resize_image == False:
		return
	if os.path.exists(src_file) == False:
		debug.error("Request a resize an image that does not existed : '" + src_file + "'")
	cmd_line = "resize Image : " + src_file + " ==> " + dest_file + " newSize=(" + str(x) + "x" + str(y) + ")"
	if False==depend.need_re_build(dest_file, src_file, file_cmd=cmd_file , cmd_line=cmd_line):
		return
	# add cmdLine ...
	x = get_pow_2_multiple(x)
	extension = dest_file[dest_file.rfind('.'):]
	if platform.system() == "Darwin":
		source_image = CoreGraphics.CGImageImport(CoreGraphics.CGDataProviderCreateWithFilename(src_file))
		source_width = source_image.getWidth()
		source_height = source_image.getHeight()
		if source_width <= x:
			# for small image just copy:
			tools.copy_file(src_file, dest_file)
		else:
			if y <= 0:
				# keep ratio :
				y = int(float(x) * float(source_height) / float(source_width))
			y = get_pow_2_multiple(y)
			debug.print_element("resize Image (" + str(x) + "x" + str(y) + ")", src_file, "==>", dest_file)
			debug.debug("Resize image: " + src_file + " size=(" + str(source_width) + "x" + str(source_height) + ") -> (" + str(x) + "x" + str(y) + ")")
			source_image_rect = CoreGraphics.CGRectMake(0, 0, source_width, source_height)
			new_image = source_image.createWithImageInRect(source_image_rect)
			colors_space = CoreGraphics.CGColorSpaceCreateDeviceRGB()
			colors = CoreGraphics.CGFloatArray(5)
			context = CoreGraphics.CGBitmapContextCreateWithColor(x, y, colors_space, colors)
			context.setInterpolationQuality(CoreGraphics.kCGInterpolationHigh)
			new_image_rect = CoreGraphics.CGRectMake(0, 0, x, y)
			context.drawImage(new_image_rect, new_image)
			tools.create_directory_of_file(dest_file)
			if extension == ".jpeg":
				context.writeToFile(dest_file, CoreGraphics.kCGImageFormatJPEG)
			elif extension == ".png":
				context.writeToFile(dest_file, CoreGraphics.kCGImageFormatPNG)
			else:
				debug.error(" can not manage extention ... : " + dest_file)
	else:
		# open an image file (.bmp,.jpg,.png,.gif) you have in the working path
		im1 = Image.open(src_file)
		if im1.size[0] <= x:
			# for small image just copy:
			tools.copy_file(src_file, dest_file)
		else:
			if y <= 0:
				# keep ratio :
				y = int(float(x) * float(im1.size[1]) / float(im1.size[0]))
			y = get_pow_2_multiple(y)
			debug.print_element("resize Image (" + str(x) + "x" + str(y) + ")", src_file, "==>", dest_file)
			# use one of these filter options to resize the image
			tmpImage = im1.resize((x, y), Image.ANTIALIAS)
			tools.create_directory_of_file(dest_file)
			tmpImage.save(dest_file)
	tools.store_command(cmd_line, cmd_file)
