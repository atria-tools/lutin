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

enableResizeImage = True
try:
	if platform.system() == "Darwin":
		import CoreGraphics
	else:
		from PIL import Image
except:
	enableResizeImage = False
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
def resize(srcFile, destFile, x, y, cmd_file=None):
	if enableResizeImage == False:
		return
	if os.path.exists(srcFile) == False:
		debug.error("Request a resize an image that does not existed : '" + srcFile + "'")
	cmd_line = "resize Image : " + srcFile + " ==> " + destFile + " newSize=(" + str(x) + "x" + str(y) + ")"
	if False==depend.need_re_build(destFile, srcFile, file_cmd=cmd_file , cmdLine=cmd_line):
		return
	# add cmdLine ...
	x = get_pow_2_multiple(x)
	extension = destFile[destFile.rfind('.'):]
	if platform.system() == "Darwin":
		source_image = CoreGraphics.CGImageImport(CoreGraphics.CGDataProviderCreateWithFilename(srcFile))
		source_width = source_image.getWidth()
		source_height = source_image.getHeight()
		if source_width <= x:
			# for small image just copy:
			tools.copy_file(srcFile, destFile)
		else:
			if y <= 0:
				# keep ratio :
				y = int(float(x) * float(source_height) / float(source_width))
			y = get_pow_2_multiple(y)
			debug.print_element("resize Image (" + str(x) + "x" + str(y) + ")", srcFile, "==>", destFile)
			debug.debug("Resize image: " + srcFile + " size=(" + str(source_width) + "x" + str(source_height) + ") -> (" + str(x) + "x" + str(y) + ")")
			source_image_rect = CoreGraphics.CGRectMake(0, 0, source_width, source_height)
			new_image = source_image.createWithImageInRect(source_image_rect)
			colors_space = CoreGraphics.CGColorSpaceCreateDeviceRGB()
			colors = CoreGraphics.CGFloatArray(5)
			context = CoreGraphics.CGBitmapContextCreateWithColor(x, y, colors_space, colors)
			context.setInterpolationQuality(CoreGraphics.kCGInterpolationHigh)
			new_image_rect = CoreGraphics.CGRectMake(0, 0, x, y)
			context.drawImage(new_image_rect, new_image)
			tools.create_directory_of_file(destFile)
			if extension == ".jpeg":
				context.writeToFile(destFile, CoreGraphics.kCGImageFormatJPEG)
			elif extension == ".png":
				context.writeToFile(destFile, CoreGraphics.kCGImageFormatPNG)
			else:
				debug.error(" can not manage extention ... : " + destFile)
	else:
		# open an image file (.bmp,.jpg,.png,.gif) you have in the working folder
		im1 = Image.open(srcFile)
		if im1.size[0] <= x:
			# for small image just copy:
			tools.copy_file(srcFile, destFile)
		else:
			if y <= 0:
				# keep ratio :
				y = int(float(x) * float(im1.size[1]) / float(im1.size[0]))
			y = get_pow_2_multiple(y)
			debug.print_element("resize Image (" + str(x) + "x" + str(y) + ")", srcFile, "==>", destFile)
			# use one of these filter options to resize the image
			tmpImage = im1.resize((x, y), Image.ANTIALIAS)
			tools.create_directory_of_file(destFile)
			tmpImage.save(destFile)
	multiprocess.store_command(cmd_line, cmd_file)
