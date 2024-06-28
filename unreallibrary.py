import unreal

class UnrealLibrary():
    def __init__(self):
        super().__init__()
        
        self.EAL = unreal.EditorAssetLibrary
        self.ELL = unreal.EditorLevelLibrary
         
    def spawnActor(self, shape = 'cube'):
        assetPath = "/Engine/BasicShapes/Cube.Cube"
        if shape == 'sphere':
            assetPath = "/Engine/BasicShapes/Sphere.Sphere"
        actorClass = self.EAL.load_asset(assetPath)
        
        actorLocation = unreal.Vector(0, 0, 0)
        actorRotation = unreal.Rotator(0, 0, 0)
        
        spawnedActor = self.ELL.spawn_actor_from_object(actorClass, actorLocation, actorRotation)
        
        return spawnedActor
        