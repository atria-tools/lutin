=?= [center]Basic concept[/center] =?=
___________________________________________

Lutin is a compleate builder system. It is designed to answers all the application problems.
The library and the distribution problem are partially manage (no real use-case)

==Technologie==

Lutin is designed in Python 2.X or 3.X to answers at the multiplatform problesm. On Linux or MacOs, it is really easy to compile with Makefile, cmake, but on Windows it is an other problem.
The first version of Lutin has been designed in Makefile, but we need to wait 20 minutes before the first build. In Pytho it is fast as Linux.

Lutin is not based over an other builder, but request compilation itself.

==Features==

Lutin is designed to:
:** support many hardware platform (X86/X64/ARM...);
:** support many operation system (windows, Ios, Android ...);
:** support complex worktree and depedency;
:** build only when needed;
:** create platform specific packages (application bundle);
:** 


==global overview==

Every build system is based on multiple concept depending of their own designed.

For lutin we can différentiate 4 basics concepts:
:** Mudule: Interface to create a part of an application, that contain binary, scipt, datas ...
:** Target: methode to creata an application or a library (may be internal: medium level)
:** Builder: Methode to transform element in other, for example: compile a cpp in object file, or object files in binary.
:** System: Many OS manage basic element contain in the OS, This part permit to find generic module availlable in the system.

===Module===

When you use lutin, you migth first create a module, This is the basis of the framework. It permit to describe your "module", all it contain, and the deendency.

We can separate a module in some part:
:** Binary:
:: A binary is an end point element.
:: It can be transform in a complete standalone bundle, or in an part instalable.
:** Library:
:: This represent an element that is used by other application
:** Package:
:: To Be Define.


===Target===



===Builder===


===System===



