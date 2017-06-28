Build and deploy for IOS                               {#lutin_ios}
========================

@tableofcontents

Deploy on IOs is a little complicated, due to the fact Apple demand a developper licence.

To deploy you need to buy a [developper licence](https://developer.apple.com/account) nearly 99€ / year

Step 1: deploy your application with Xcode             {#lutin_ios_xcode}
==========================================

it can be conplicated to do the first deploy (register tablette:watch ... or user ...) 
Then the best way is now to create your first game sample application with XCode and deploy it on your device ...


when all your problem are solved, I can help you...

**Note:**

```
	To add a device, in xcode select your top project, and in the section "signing" select "automatic manage signing", select your team and activate your device ...
```


step 2: Build for IOs                                  {#lutin_ios_build}
=====================

This step is simpliest... All is integrated:

Select the target IOs

```{.sh}
	lutin -C -D -tIOs yourApplication?build
```

This is done .... now deploy ...



step 3: Deploy                                  {#lutin_ios_deploy}
==============

Do it ... it does not work ...

```{.sh}
	lutin -C -D -tIOs yourApplication?install
```

Application ID
--------------

It miss some things to do:

create a reference of you application in [apple interface](https://developer.apple.com/account/ios/identifier/bundle/create)


your application id is: 

```{.py}
	get_compagny_type() + "." + get_compagny_name() + "." + module.get_name()
```

For example if you module is named: ```lutin_application.py```

And you set description:

```{.py}
def get_compagny_type():
	return "com"

def get_compagny_name():
	return "compagny NAME"

```

your id is: ```com.compagnyname.application```


When you have create the application, it will generate for you a unique ID, you can see it on the webpage, it is like: ```DFGDSFGSDFGS.com.compagnyname.application```

In your module definition you need to add:
```{.py}
my_module.set_pkg("APPLE_APPLICATION_IOS_ID", "DFGDSFGSDFGS");
```

Team signing ID
---------------

the second point to do is creating the file: ```.iosKey.txt``` in you root path of your workspace (where you execute lutin)

it will contain sothing like: 
```
'iPhone Developer: Francis DUGENOUX (YRRQE5KGTH)'

```

you can optain it with executing:
```{.sh}
certtool y | grep "Developer"
```



Install:
--------

Now it works ...

```{.sh}
	lutin -C -D -tIOs yourApplication?build
```
