from .base import BaseModule
from .ideation import IdeationModule
from .framing import FramingModule
from .packaging import PackagingModule
from .hooks import HooksModule
from .scripting import ScriptingModule
from .pcm import PCMModule
from .captions import CaptionsModule
from .cta import CTAModule
from .publishing import PublishingModule
from .iteration import IterationModule
from .market_research import MarketResearchModule
from .funnel_copy import FunnelCopyModule
from .email_sequences import EmailSequencesModule
from .sales import SalesModule
from .launch import LaunchModule

ALL_MODULES = {
    "ideation": IdeationModule,
    "framing": FramingModule,
    "packaging": PackagingModule,
    "hooks": HooksModule,
    "scripting": ScriptingModule,
    "pcm": PCMModule,
    "captions": CaptionsModule,
    "cta": CTAModule,
    "publishing": PublishingModule,
    "iteration": IterationModule,
    "market_research": MarketResearchModule,
    "funnel_copy": FunnelCopyModule,
    "email_sequences": EmailSequencesModule,
    "sales": SalesModule,
    "launch": LaunchModule,
}

__all__ = ["BaseModule", "ALL_MODULES"]
