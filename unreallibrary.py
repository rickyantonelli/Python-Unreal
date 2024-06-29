import unreal

class UnrealLibrary():
    """A class that gives access to the necessary libraries from the Unreal Engine Python API"""
    def __init__(self):
        """ Init's UnrealLibrary"""
        super().__init__()
        
        self.EAL = unreal.EditorAssetLibrary
        self.ELL = unreal.EditorLevelLibrary
         
    def spawnActor(self, shape='square', x=0, y=0):
        """Spawns an actor in Unreal Engine that is tied to an item in the 2D grid
        
        Args:
            shape (str): The shape to be given
            x (float): The starting x position
            y (float): The starting y position
            
        Returns:
            The Unreal Engine asset
        """
        assetPath = "/Engine/BasicShapes/Cube.Cube"
        if shape == 'circle':
            assetPath = "/Engine/BasicShapes/Sphere.Sphere"
        actorClass = self.EAL.load_asset(assetPath)
        
        # set the position to the same of the item
        actorLocation = unreal.Vector(x, y, 0)
        
        # we wont be setting rotation
        actorRotation = unreal.Rotator(0, 0, 0)
        
        spawnedActor = self.ELL.spawn_actor_from_object(actorClass, actorLocation, actorRotation)
        
        return spawnedActor
        