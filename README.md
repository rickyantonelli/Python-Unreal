## "QuickBlock" - A Python Widget in Unreal
This repository explores Python usage in Unreal Engine through the use of PySide/Qt widgets. The app in this repository is for blocking out levels extremely quickly in a 3D space from a 2D grid. It includes:
- The ability to add cubes, spheres, or selected assets into a `QGraphicsView` - updates to the assets in the grid will reflect into your Unreal Engine level
- The widget is parented into Unreal, and both the widget and Unreal Engine can run simultaneously without the need for threading
- Using Python 3, and tested for Unreal Engine 5 (although it likely works for Unreal Engine 4)
- There are many quality-of-life options in this tool, some to highlight are: Quick blocking with hotkeys, multi-select with copy and paste, z-scaling updates by item, deleting items through a context menu, zooming, etc.

Below is a quick visualization of what the tool can do:


<img width="1268" alt="Screenshot 2024-07-26 125151" src="https://github.com/user-attachments/assets/80a485a7-138b-473e-86af-2c02c71a542e">

## Hooking up Python to Unreal:
- First, these two must be enabled

![Screenshot 2024-06-14 170746](https://github.com/user-attachments/assets/b48b12e9-457c-4856-9981-484dd1d80b55)
- Then, in Project Settings->Python, add a path to the folder that will contain the python scripts
	- For the tutorial, this folder is just in the content browser but it can be anywhere
- Additionally, you can also add a second path to where your modules are stored
	- If you dont know where, just open python and do something like this
```Python
import module_name
print(module_name.__file__)
```
### How to run a Python script in Unreal
- A Python script must always `import unreal`
- In Unreal's Output Log, change cmd to Python
- Import the script, which will also run the script
	- Ex: `import tutorial_script as TS`
- One can enable hot reloading by running `from importlib import reload`
- Once reload is available, you can then just `reload()` with the script name
	- Ex: `reload(TS)`
