import unreal

class UnrealLibrary():
    """Class that reflects changes into Unreal Engine and gives access to the necessary libraries from the Unreal Engine Python API"""
    def __init__(self):
        """ Init's UnrealLibrary and initializes the necessary libraries"""
        super().__init__()
        
        self.EAL = unreal.EditorAssetLibrary
        self.ELL = unreal.EditorLevelLibrary
        self.EAS = unreal.EditorActorSubsystem
        self.EUL = unreal.EditorUtilityLibrary
         
    def spawnActor(self, shape='square', x=0, y=0, label=None, assetPath=None):
        """Spawns an actor in Unreal Engine that is tied to an item in the 2D grid
        
        Args:
            shape (str): The shape to be given
            x (float): The starting x position
            y (float): The starting y position
            label (str): The label to set for the actor in Unreal
            
        Returns:
            The Unreal Engine asset
        """
        actorClass = None
        
        if not assetPath:
            if shape == 'circle':
                assetPath = "/Engine/BasicShapes/Sphere.Sphere"
            else:
                assetPath = "/Engine/BasicShapes/Cube.Cube"
            actorClass = self.EAL.load_asset(assetPath)
        else:
            # we have an asset path, but need to convert it to a relevant path
            # newAssetPath = assetPath.replace(r"C:\Program Files\Epic Games\UE_5.2\Engine\Content", "/Engine")
            print(assetPath)
            actorName = assetPath.split("/")[-1].split(".")[0]
            newAssetPath = "/Engine{}".format(assetPath)
            newAssetPath = newAssetPath.replace("uasset", actorName)
            print(newAssetPath)
            
            actorClass = self.EAL.load_asset(newAssetPath)
        
        # set the position to the same of the item
        actorLocation = unreal.Vector(x, y, 0)
        
        # we wont be setting rotation
        actorRotation = unreal.Rotator(0, 0, 0)
        
        spawnedActor = self.ELL.spawn_actor_from_object(actorClass, actorLocation, actorRotation)
        spawnedActor.set_actor_scale3d(unreal.Vector(0.25, 0.25, 0.25))
        if label:
            spawnedActor.set_actor_label(label)
        
        return spawnedActor
    
    def copyActor(self, unrealActor=None, label=None):
        """Copies an Unreal actor and returns the duplicated actor
        
        Args:
            unrealActor (Actor): The unreal actor being duplicated
            label (str): The label to set for the actor in Unreal
            
        Returns:
            The duplicated Unreal actor
        """
        if not unrealActor:
            return
        
        duplicatedActor = self.EAS.duplicate_actor(unreal.EditorActorSubsystem(), unrealActor)
        if label:
            duplicatedActor.set_actor_label(label)
        
        return duplicatedActor
    
    def selectActors(self, unrealActors):
        """Selects the actors in the Unreal Engine editor
        
        Args:
            unrealActors (list): The actors to select
        """
        
        # this does not need to be a method if it's just one line
        # but might want to do more here so we'll leave it
        self.ELL.set_selected_level_actors(unrealActors)
         