from http.client import HTTPException
from clerk_backend_api import Clerk
import os
from dotenv import load_dotenv


load_dotenv()

clerk_sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRETE_KEY"))

def authentication_and_get_user_details(request):
    try:
        request_state = clerk_sdk.authenticate_request(
            request,
            AAuthenticateRequestOption(
                authorized_parties=["http://localhost:5173", "https://localhost:5173"]
            )
        )
        if not request_state.signed_in:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = request_state.payload.get("sub")

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))