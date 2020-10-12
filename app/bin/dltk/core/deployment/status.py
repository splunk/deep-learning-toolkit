
STATUS_DEPLOYING = "deploying"
STATUS_DEPLOYED = "deployed"
STATUS_UNDEPLOYING = "undeploying"
STATUS_DISABLING = "disabling"
STATUS_DISABLED = "disabled"
STATUS_ERROR = "error"


class DeploymentStatus(Exception):
    status = None
    message = None

    def __init__(self, status, message=""):
        self.status = status
        self.message = message


class StillDeploying(DeploymentStatus):
    def __init__(self, message):
        super().__init__(STATUS_DEPLOYING, message)


class Deployed(DeploymentStatus):
    def __init__(self):
        super().__init__(STATUS_DEPLOYED)


class StillUndeploying(DeploymentStatus):
    def __init__(self, message):
        super().__init__(STATUS_UNDEPLOYING, message)


class StillStopping(DeploymentStatus):
    def __init__(self, message):
        super().__init__(STATUS_DISABLING, message)


class Disabled(DeploymentStatus):
    def __init__(self):
        super().__init__(STATUS_DISABLED)


class DeploymentError(DeploymentStatus):
    def __init__(self, message):
        super().__init__(STATUS_ERROR, message)
