from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field

class MediaType(str, Enum):
    SCREEN = "screen"
    PRINT = "print"

class PageFormat(str, Enum):
    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    A5 = "A5"
    LETTER = "Letter"
    LEGAL = "Legal"
    TABLOID = "Tabloid"

class WaitUntil(str, Enum):
    LOAD = "load"
    DOMCONTENTLOADED = "domcontentloaded"
    NETWORKIDLE0 = "networkidle0"
    NETWORKIDLE2 = "networkidle2"

class ResourceType(str, Enum):
    DOCUMENT = "document"
    STYLESHEET = "stylesheet"
    IMAGE = "image"
    MEDIA = "media"
    FONT = "font"
    SCRIPT = "script"
    TEXTTRACK = "texttrack"
    XHR = "xhr"
    FETCH = "fetch"
    EVENTSOURCE = "eventsource"
    WEBSOCKET = "websocket"
    MANIFEST = "manifest"
    SIGNEDEXCHANGE = "signedexchange"
    PING = "ping"
    CSPVIOLATIONREPORT = "cspviolationreport"
    OTHER = "other"

class ScriptTag(BaseModel):
    url: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    id: Optional[str] = None

class StyleTag(BaseModel):
    url: Optional[str] = None
    path: Optional[str] = None
    content: Optional[str] = None

class Authentication(BaseModel):
    username: str
    password: str

class CookiePartitionKey(BaseModel):
    sourceOrigin: Optional[str] = None
    hasCrossSiteAncestor: Optional[bool] = None

class Cookie(BaseModel):
    name: str
    value: str
    url: Optional[str] = None
    domain: Optional[str] = None
    path: Optional[str] = None
    secure: Optional[bool] = None
    httpOnly: Optional[bool] = None
    sameSite: Optional[str] = None
    expires: Optional[int] = None
    priority: Optional[str] = None
    sameParty: Optional[bool] = None
    sourceScheme: Optional[str] = None
    partitionKey: Optional[CookiePartitionKey] = None

class Viewport(BaseModel):
    width: int
    height: int
    deviceScaleFactor: Optional[float] = 1.0
    isMobile: Optional[bool] = False
    isLandscape: Optional[bool] = False
    hasTouch: Optional[bool] = False

class Margin(BaseModel):
    top: Optional[str] = "0"
    bottom: Optional[str] = "0"
    left: Optional[str] = "0"
    right: Optional[str] = "0"

class PDFOptions(BaseModel):
    scale: Optional[float] = 1.0
    displayHeaderFooter: Optional[bool] = False
    headerTemplate: Optional[str] = None
    footerTemplate: Optional[str] = None
    printBackground: Optional[bool] = True
    landscape: Optional[bool] = False
    pageRanges: Optional[str] = None
    format: Optional[PageFormat] = PageFormat.A4
    width: Optional[str] = None
    height: Optional[str] = None
    preferCSSPageSize: Optional[bool] = False
    margin: Optional[Margin] = Field(default_factory=Margin)
    omitBackground: Optional[bool] = False
    tagged: Optional[bool] = False
    outline: Optional[bool] = False
    timeout: Optional[int] = 30000
    waitForFonts: Optional[bool] = True

class RequestInterceptor(BaseModel):
    pattern: str
    response: Dict[str, Any]

class PDFRequest(BaseModel):
    addScriptTag: Optional[List[ScriptTag]] = None
    addStyleTag: Optional[List[StyleTag]] = None
    authenticate: Optional[Authentication] = None
    bestAttempt: Optional[bool] = True
    cookies: Optional[List[Cookie]] = None
    emulateMediaType: Optional[MediaType] = None
    html: Optional[str] = None
    url: Optional[str] = None
    options: Optional[PDFOptions] = Field(default_factory=PDFOptions)
    rejectRequestPattern: Optional[List[str]] = None
    rejectResourceTypes: Optional[List[ResourceType]] = None
    requestInterceptors: Optional[List[RequestInterceptor]] = None
    setExtraHTTPHeaders: Optional[Dict[str, str]] = None
    setJavaScriptEnabled: Optional[bool] = True
    userAgent: Optional[str] = None
    viewport: Optional[Viewport] = None
    waitForTimeout: Optional[int] = None

    class Config:
        use_enum_values = True 

class CompressionLevel(int, Enum):
    NONE = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8
    MAXIMUM = 9

class PDFCompressionRequest(BaseModel):
    file_path: str
    compression_level: CompressionLevel = Field(
        default=CompressionLevel.LEVEL_5,
        description="Compression level from 0 (no compression) to 9 (maximum compression)"
    ) 