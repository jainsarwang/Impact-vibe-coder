from fastapi import APIRouter

from ..controllers.email_controller import add_email_credential, get_email_credential, update_email_credential, delete_email_credential
from ..types.api import EmailCredentialResponse

router = APIRouter()

router.add_api_route("/add-credential", add_email_credential, methods=["POST"], response_model=EmailCredentialResponse)
router.add_api_route("/get-credential", get_email_credential, methods=["GET"], response_model=EmailCredentialResponse)
router.add_api_route("/update-credential", update_email_credential, methods=["PATCH"], response_model=EmailCredentialResponse)
router.add_api_route("/delete-credential", delete_email_credential, methods=["DELETE"], response_model=None)
