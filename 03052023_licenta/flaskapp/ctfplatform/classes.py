class namespace_obj:
    def __init__(self):
        pass
    def __init__(self, name):
        self.name = name

class deployment_obj:
    def __init__(self):
        pass
    def __init__(self, name, imageName, port, replicas, ready):
        self.name = name
        self.imageName = imageName
        self.port = port
        self.replicas = replicas
        self.ready = ready

class ReleaseObj:
    def __init__(self):
        pass
    
    def __init__(self, name, version, imageName, description, apiVersion, appVersion, type, installed):
        self.name = name
        self.version = version
        self.imageName = imageName
        self.description = description
        self.apiVersion = apiVersion
        self.appVersion = appVersion
        self.type = type
        self.installed = installed
            
    def get_name(self):
        return self.name
    
    def get_version(self):
        return self.version
    
    def get_image_name(self):
        return self.imageName
    
    def get_description(self):
        return self.description
    
    def get_api_version(self):
        return self.apiVersion
    
    def get_app_version(self):
        return self.appVersion
    
    def get_type(self):
        return self.type
    
    def is_installed(self):
        return self.installed


class ImageObj:
    def __init__(self):
        pass
    def __init__(self, name, tag, fullUrl, inUse, digest):
        self.name = name
        self.tag = tag
        self.fullUrl = fullUrl
        self.inUse = inUse
        self.imageDigest = digest
        