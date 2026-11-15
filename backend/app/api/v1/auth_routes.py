"""Keycloak OIDC authentication routes - demo mode for localhost development."""

from urllib.parse import urlencode, parse_qsl
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel, Field

router = APIRouter(tags=["auth"], prefix="/auth")


# Keycloak configuration (demo mode - localhost only)
KEYCLOAK_DEMO_CONFIG = {
    "server_url": "http://localhost:8080",
    "realm": "demo-realm",
    "client_id": "lumen-lab",
    "client_secret": "lumen-lab-secret",
}


class UserInfo(BaseModel):
    """User information from Keycloak."""
    sub: str = Field(..., description="Keycloak user UUID")
    email: str = Field("", description="User email")
    name: str = Field("", description="User display name")
    preferred_username: str = Field("", description="Username")
    realm_access: dict = Field(default_factory=dict, description="Realm-level roles")
    resource_access: dict = Field(default_factory=dict, description="Client-level roles")

    @property
    def is_authenticated(self) -> bool:
        return self.sub is not None and self.sub != ""


class LoginRequest(BaseModel):
    """Login request - initiate Keycloak OIDC flow."""
    redirect_url: str = Field("/", description="Optional redirect after login")


class LogoutRequest(BaseModel):
    """Logout request - initiate Keycloak logout."""
    redirect_url: str = Field("/", description="Optional redirect after logout")


async def keycloak_login_url(request: Request, redirect_url: str = "/") -> str:
    """Generate Keycloak authorization URL for demo mode."""
    auth_params = {
        "response_type": "code",
        "client_id": KEYCLOAK_DEMO_CONFIG["client_id"],
        "redirect_uri": "http://localhost:8000/auth/callback",
        "scope": "openid profile email",
        "state": urlencode({"redirect": redirect_url}),
    }
    
    auth_url = f"{KEYCLOAK_DEMO_CONFIG['server_url']}/realms/{KEYCLOAK_DEMO_CONFIG['realm']}/protocol/openid/authorize?" + urlencode(auth_params)
    return auth_url


async def keycloak_callback(code: str, state: str) -> dict:
    """Handle Keycloak OAuth2 callback - demo mode."""
    import httpx
    
    token_url = f"{KEYCLOAK_DEMO_CONFIG['server_url']}/realms/{KEYCLOAK_DEMO_CONFIG['realm']}/protocol/openid/token"
    
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": KEYCLOAK_DEMO_CONFIG["client_id"],
        "redirect_uri": "http://localhost:8000/auth/callback",
        "client_secret": KEYCLOAK_DEMO_CONFIG["client_secret"],
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=token_data, timeout=10.0)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for tokens",
            )
        
        tokens = response.json()
        
        # Introspect to get user info
        introspect_url = f"{KEYCLOAK_DEMO_CONFIG['server_url']}/realms/{KEYCLOAK_DEMO_CONFIG['realm']}/protocol/openid/core/introspect"
        introspect_response = await client.post(
            introspect_url,
            data={"token": tokens["access_token"]},
            timeout=5.0,
        )
        
        user_info = {}
        if introspect_response.status_code == 200:
            user_info = introspect_response.json()
        
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token"),
            "user_info": user_info,
        }


async def keycloak_logout_url(redirect_uri: str = "http://localhost:8000/auth/logout-callback") -> str:
    """Generate Keycloak logout URL - demo mode."""
    logout_params = {
        "redirect_uri": redirect_uri,
        "post_logout_redirect_uri": redirect_uri,
        "client_id": KEYCLOAK_DEMO_CONFIG["client_id"],
    }
    
    logout_url = f"{KEYCLOAK_DEMO_CONFIG['server_url']}/realms/{KEYCLOAK_DEMO_CONFIG['realm']}/protocol/openid/logout?" + urlencode(logout_params)
    return logout_url


@router.get("/login", summary="Initiate Keycloak OIDC login", description="Redirect to Keycloak authorization page for OIDC authentication. Demo mode supports localhost development.")
async def login(
    request: Request,
    redirect_url: str = "/",
) -> RedirectResponse:
    """Initiate Keycloak OIDC login flow.
    
    Returns a redirect to the Keycloak authorization server.
    In demo mode, uses the development Keycloak instance.
    """
    auth_url = await keycloak_login_url(request, redirect_url)
    return RedirectResponse(url=auth_url)


@router.get("/callback", summary="Keycloak OAuth2 callback", description="Handle the OAuth2 callback from Keycloak after user authorization. Exchanges authorization code for tokens and validates the user session.")
async def callback(
    request: Request,
    code: str,
    state: str,
) -> JSONResponse:
    """Handle Keycloak OAuth2 callback.
    
    Exchanges the authorization code for access tokens and user info,
    then stores user session and redirects to the intended page.
    """
    result = await keycloak_callback(code, state)
    
    # Build user info
    user_info_data = result.get("user_info", {})
    user_info = UserInfo(
        sub=user_info_data.get("sub", ""),
        email=user_info_data.get("email", ""),
        name=user_info_data.get("name", ""),
        preferred_username=user_info_data.get("preferred_username", ""),
        realm_access=user_info_data.get("realm_access", {}),
        resource_access=user_info_data.get("resource_access", {}),
    )
    
    # Set session cookie
    response = JSONResponse({"status": "authenticated", "user": user_info.model_dump()})
    response.set_cookie(
        key="lumen_lab_auth",
        value=user_info.sub,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    
    # Parse state for redirect target
    redirect_target = "/"
    if state:
        try:
            state_params = dict(parse_qsl(state))
            redirect_target = state_params.get("redirect", "/")
        except Exception:
            pass
    
    response.headers["HX-Redirect"] = redirect_target
    return response


@router.post("/logout", summary="Initiate Keycloak OIDC logout", description="Logout from Keycloak and clear the user session. Redirects to the specified redirect URI.")
async def logout(
    request: Request,
    logout_request: LogoutRequest,
) -> JSONResponse:
    """Initiate Keycloak logout.
    
    Clears the user session and redirects to Keycloak's logout endpoint.
    """
    # Generate Keycloak logout URL
    logout_url = await keycloak_logout_url(logout_request.redirect_url)
    
    # Clear auth cookie
    response = JSONResponse({"status": "logged_out"})
    response.delete_cookie(
        key="lumen_lab_auth",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    
    # Redirect to Keycloak logout
    response.headers["HX-Redirect"] = logout_url
    return response


@router.get("/logout-callback", summary="Keycloak logout callback", description="Handle Keycloak logout callback. Clears local session and redirects to frontend.")
async def logout_callback(request: Request) -> JSONResponse:
    """Handle Keycloak logout callback.
    
    Clears any local session data and redirects to the frontend landing page.
    """
    # Clear auth cookie
    response = JSONResponse({"status": "session_cleared"})
    response.delete_cookie(
        key="lumen_lab_auth",
        httponly=True,
        secure=False,
        samesite="lax",
    )
    
    response.headers["HX-Redirect"] = "/"
    return response


@router.get("/me", summary="Get current user info", description="Return the currently authenticated user's information from the Keycloak session. Demo mode returns user info if session exists.")
async def me(
    request: Request,
) -> UserInfo:
    """Get current authenticated user info.
    
    In demo mode, reads the auth cookie and returns user information.
    Returns 401 if no authenticated user found (no cookie set).
    """
    # Read auth cookie
    auth_cookie = request.cookies.get("lumen_lab_auth")
    if not auth_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # In demo mode, we accept any non-empty sub as authenticated
    # In production, this would validate the JWT token
    user_info = UserInfo(
        sub=auth_cookie,
        email="",
        name="Demo User",
        preferred_username="demo-user",
        realm_access={},
        resource_access={},
    )
    
    return user_info


@router.get("/health", summary="Auth service health check", description="Check Keycloak OIDC service availability in demo mode.")
async def health() -> dict:
    """Check Keycloak OIDC service health."""
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{KEYCLOAK_DEMO_CONFIG['server_url']}/realms/{KEYCLOAK_DEMO_CONFIG['realm']}/.well-known/openid-configuration",
                timeout=3.0,
            )
            if response.status_code == 200:
                return {
                    "status": "ok",
                    "service": "keycloak",
                    "demo_mode": True,
                    "message": "Keycloak OIDC demo mode is configured",
                }
        return {
            "status": "warning",
            "service": "keycloak",
            "demo_mode": True,
            "message": "Keycloak not reachable (expected in dev without container)",
        }
    except Exception:
        return {
            "status": "warning",
            "service": "keycloak",
            "demo_mode": True,
            "message": "Keycloak not reachable (expected in dev without container)",
        }
