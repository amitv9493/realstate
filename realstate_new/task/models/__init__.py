from .basetask import BaseTask
from .lockbox_task import LockBoxTaskBS
from .lockbox_task import LockBoxTaskIR
from .open_for_vendor_task import OpenForVendorTask
from .openhouse import OpenHouseTask
from .professional_task import ProfessionalServiceTask
from .runner_task import RunnerTask
from .showing_task import ShowingTask
from .sign_task import SignTask
from .third_party_call import ThirdPartyCall
from .verification_image import VerificationDocument

__all__ = [
    "BaseTask",
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
    "get_job",
]


JOB_TYPE_MAPPINGS = {
    "LockBoxBS": LockBoxTaskBS,
    "LockBoxIR": LockBoxTaskIR,
    "Showing": ShowingTask,
    "OpenHouse": OpenHouseTask,
    "Runner": RunnerTask,
    "Sign": SignTask,
    "Professional": ProfessionalServiceTask,
    "OpenForVendor": OpenForVendorTask,
}


def get_job(job_model: str, task_id: int):
    return JOB_TYPE_MAPPINGS[job_model].objects.get(id=task_id)
