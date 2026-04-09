"""FastAPI application entrypoint."""

import os
import warnings
from pathlib import Path
import absl.logging

# Suppress C++ level warnings from Mediapipe/TensorFlow
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
absl.logging.set_verbosity(absl.logging.ERROR)

# Suppress protobuf deprecation warning caused by internal dependencies (e.g. mediapipe)
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=".*SymbolDatabase.GetPrototype().*",
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes.analyze import router as analyze_router
from api.routes.chat import router as chat_router
from api.routes.health import router as health_router
from app.config import get_settings
from src.storage.supabase_storage import SupabaseStorageClient, SupabaseStorageError

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix, tags=["health"])
app.include_router(analyze_router, prefix=settings.api_prefix, tags=["analysis"])
app.include_router(chat_router, prefix=settings.api_prefix, tags=["chat"])

debug_dir = Path("debug")
debug_dir.mkdir(parents=True, exist_ok=True)
app.mount("/debug-assets", StaticFiles(directory=str(debug_dir.resolve())), name="debug-assets")


@app.on_event("startup")
def ensure_storage_buckets() -> None:
    """Create the public buckets used by the chat flow when possible."""
    storage_client = SupabaseStorageClient()
    if not storage_client.is_configured:
        return

    for bucket in (
        settings.supabase_chat_bucket,
        settings.supabase_posture_bucket,
        settings.supabase_posture_analysis_bucket,
    ):
        try:
            storage_client.ensure_public_bucket(bucket)
        except SupabaseStorageError:
            # The API can still serve local debug assets even if Supabase Storage is unavailable.
            continue
