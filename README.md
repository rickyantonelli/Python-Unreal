## "QuickBlock" - A Python Widget in Unreal
This repository explores Python usage in Unreal Engine through the use of PySide/Qt widgets. The app in this repository is for blocking out levels extremely quickly in a 3D space from a 2D grid. It includes:
- The ability to add cubes and spheres into a `QGraphicsView` - updates to the assets in the grid will reflect into your Unreal Engine level
- The widget is parented into Unreal, and both the widget and Unreal Engine can run simultaneously without the need for parenting
- Using Python 3, and tested for Unreal Engine 5 (although it likely works for Unreal Engine 4)
- There are many quality-of-life options in this tool, some to highlight are: Quick blocking with hotkeys, multi-select with copy and paste, z-scaling updates by item, deleting items through a context menu
- Many more will are planned to be added to the future, such as: Rotating items, zooming out, expanding to user-selected assets in addition to basic shapes, action history, etc.

Below is a quick visualization of what the tool can do:

<img width="1706" alt="QuickBlockTest" src="https://github.com/rickyantonelli/Python-Unreal/assets/90994929/1a115672-5ca8-4258-8934-0026b958e783">
