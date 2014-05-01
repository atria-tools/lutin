#!/usr/bin/python
import lutinDebug as debug
import platform

if platform.system() == "Darwin":
	import CoreGraphics
else:
	import image

def resize(srcFile, destFile, x, y):
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
		new_image_rect = CoreGraphics.CGRectMake(0, 0, x, y)
		context.drawImage(new_image_rect, new_image)
		context.writeToFile(destFile, CoreGraphics.kCGImageFormatPNG)
	else:
		# open an image file (.bmp,.jpg,.png,.gif) you have in the working folder
		im1 = image.open(srcFile)
		# use one of these filter options to resize the image
		tmpImage = im1.resize((x, y), Image.ANTIALIAS)
		tmpImage.save(destFile)
