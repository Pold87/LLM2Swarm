# argos-python

## How to use
copy all files in the plugin folder of argos simulator
then build.

### Building instructions
You need at least boost, boost-libs, cmake, gcc, python3.
Compliling tested on archlinux only.
```bash
cd argos-python
cmake .
make
```
### Controller
Now you use the python_controller in your .argos configuration like so :
```xml
<python_controller id="whatever" library="/path/to/compiled/libpy_controller_interface.so">
```

don't forget to also add :
```xml
<params script="/path/to/script.py" />
```
at the end of controller section

### python script
