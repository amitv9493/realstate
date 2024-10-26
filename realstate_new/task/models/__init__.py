from .lockbox_task import LockBoxTaskBS
from .lockbox_task import LockBoxTaskIR
from .openhouse import OpenHouseTask
from .professional_task import ProfessionalServiceTask
from .runner_task import RunnerTask
from .showing_task import ShowingTask
from .sign_task import SignTask
from .third_party_call import ThirdPartyCall
from .verification_image import VerificationDocument

__all__ = [
    "JOB_TYPE_MAPPINGS",
    "LockBoxTaskBS",
    "LockBoxTaskIR",
    "OpenHouseTask",
    "ProfessionalServiceTask",
    "RunnerTask",
    "ShowingTask",
    "SignTask",
    "ThirdPartyCall",
    "VerificationDocument",
]


JOB_TYPE_MAPPINGS = {
    "LockBoxBS": LockBoxTaskBS,
    "LockBoxIR": LockBoxTaskIR,
    "Showing": ShowingTask,
    "OpenHouse": OpenHouseTask,
    "Runner": RunnerTask,
    "Sign": SignTask,
    "Professional": ProfessionalServiceTask,
}
