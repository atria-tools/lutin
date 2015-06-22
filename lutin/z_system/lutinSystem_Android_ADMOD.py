#!/usr/bin/python
##
## @author Edouard DUPIN
##
## @copyright 2012, Edouard DUPIN, all right reserved
##
## @license APACHE v2.0 (see license file)
##

from lutin import debug
from lutin import system
from lutin import tools
import os

class System(system.System):
	def __init__(self, target):
		system.System.__init__(self)
		# create some HELP:
		self.help="ADMOD: Android SDK ad-mod interface (auto-create interface for admod)\n"
		# todo : Check if present ...
		self.valid = True
		# todo : create a searcher of the presence of the library:
		self.add_export_SRC(target.folder_sdk + "/extras/google/google_play_services/libproject/google-play-services_lib/libs/google-play-services.jar")
		self.add_action("PACKAGE", 10, "admod-auto-wrapper", tool_generate_main_java_class)



##################################################################
##
## Android specific section
##
##################################################################
def tool_generate_main_java_class(target, module, package_name):
	if "ADMOD_ID" not in module.package_prop:
		debug.warning("Missing parameter ADMOD_ID wen you resuested dependency of ADMOD")
		return
	
	module.package_prop["RIGHT"].append("INTERNET")
	module.package_prop["RIGHT"].append("ACCESS_NETWORK_STATE")
	
	module.pkg_add("GENERATE_SECTION__IMPORT", [
		"import com.google.android.gms.ads.AdRequest;",
		"import com.google.android.gms.ads.AdSize;",
		"import com.google.android.gms.ads.AdView;",
		"import android.widget.LinearLayout;",
		"import android.widget.Button;"
		])
	module.pkg_add("GENERATE_SECTION__DECLARE", [
		"/** The view to show the ad. */",
		"private AdView adView;",
		"private LinearLayout mLayout = null;"
		])
	list_create = [
		"mLayout = new LinearLayout(this);"
		"mLayout.setOrientation(android.widget.LinearLayout.VERTICAL);",
		"LinearLayout.LayoutParams paramsWindows = new LinearLayout.LayoutParams(",
		"	LinearLayout.LayoutParams.FILL_PARENT,",
		"	LinearLayout.LayoutParams.FILL_PARENT);",
		"",
		"setContentView(mLayout, paramsWindows);",
		"",
		"LinearLayout.LayoutParams paramsAdds = new LinearLayout.LayoutParams(",
		"	LinearLayout.LayoutParams.FILL_PARENT,",
		"	LinearLayout.LayoutParams.WRAP_CONTENT);",
		"paramsAdds.weight = 0;",
		"",
		"LinearLayout.LayoutParams paramsGLView = new LinearLayout.LayoutParams(",
		"	LinearLayout.LayoutParams.FILL_PARENT,",
		"	LinearLayout.LayoutParams.FILL_PARENT);",
		"paramsGLView.weight = 1;",
		"paramsGLView.height = 0;",
		"",
		"mLayout.setGravity(android.view.Gravity.TOP);",
		"",
		"// Create an adds.",
		"adView = new AdView(this);",
		"adView.setAdSize(AdSize.SMART_BANNER);",
		"adView.setAdUnitId(\"" + module.package_prop["ADMOD_ID"] + "\");",
		"",
		"// Create an ad request. Check logcat output for the hashed device ID to get test ads on a physical device.",
		"AdRequest adRequest = new AdRequest.Builder()",
		"	.addTestDevice(AdRequest.DEVICE_ID_EMULATOR)",
		"	.build();",
		"",
		"// Add the AdView to the view hierarchy. The view will have no size until the ad is loaded."]
		if     "ADMOD_POSITION" in module.package_prop \
		   and module.package_prop["ADMOD_POSITION"] == "top":
			list_create.append("mLayout.addView(adView, paramsAdds);")
			list_create.append("mLayout.addView(mGLView, paramsGLView);")
		else:
			list_create.append("mLayout.addView(mGLView, paramsGLView);")
			list_create.append("mLayout.addView(adView, paramsAdds);")
		list_create.append("")
		list_create.append("// Start loading the ad in the background.")
		list_create.append("adView.loadAd(adRequest);")
	module.pkg_add("GENERATE_SECTION__ON_CREATE", list_create)
	module.pkg_add("GENERATE_SECTION__ON_RESUME", [
		"if (adView != null) {",
		"	adView.resume();",
		"}"
		])
	module.pkg_add("GENERATE_SECTION__ON_PAUSE", [
		"if (adView != null) {",
		"	adView.pause();",
		"}"
		])
	module.pkg_add("GENERATE_SECTION__ON_DESTROY", [
		"// Destroy the AdView.",
		"if (adView != null) {",
		"	adView.destroy();",
		"}"
		])
	


