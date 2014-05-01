#!/usr/bin/python
import lutinDebug as debug
import lutinTools as tools
import platform

if platform.system() == "Darwin":
	import CoreGraphics
else:
	from PIL import Image

def resize(srcFile, destFile, x, y):
	extension = destFile[destFile.rfind('.'):]
	if platform.system() == "Darwin":
		source_image = CoreGraphics.CGImageImport(CoreGraphics.CGDataProviderCreateWithFilename(srcFile))
		source_width = source_image.getWidth()
		source_height = source_image.getHeight()
		source_image_rect = CoreGraphics.CGRectMake(0, 0, source_width, source_height)
		new_image = source_image.createWithImageInRect(source_image_rect)
		colors_space = CoreGraphics.CGColorSpaceCreateDeviceRGB()
		colors = CoreGraphics.CGFloatArray(5)
		context = CoreGraphics.CGBitmapContextCreateWithColor(x, y, colors_space, colors)
		context.setInterpolationQuality(CoreGraphics.kCGInterpolationHigh)
		if im1.size[0] <= x:
			# for small image just copy:
			tools.copy_file(srcFile, destFile)
		else:
			if y <= 0:
				# keep ratio :
				y = int(float(x) * float(source_height) / float(source_width))
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
			# use one of these filter options to resize the image
			tmpImage = im1.resize((x, y), Image.ANTIALIAS)
			tools.create_directory_of_file(destFile)
			tmpImage.save(destFile)
