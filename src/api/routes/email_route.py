from fastapi import APIRouter

from ..controllers.email_controller import add_email_credential, get_email_credential, update_email_credential, delete_email_credential


router = APIRouter()

router.add_api_route("/add-credential", add_email_credential, methods=["POST"])
router.add_api_route("/get-credential", get_email_credential, methods=["GET"])
router.add_api_route("/update-credential", update_email_credential, methods=["PATCH"])
router.add_api_route("/delete-credential", delete_email_credential, methods=["DELETE"])





