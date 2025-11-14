from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import JSONResponse, Response
from typing import List, Optional
from datetime import datetime

import json

router = APIRouter()
