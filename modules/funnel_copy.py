"""
Funnel Copy Module — VSL scripts, funnel page copy, RCIBO prompts, presentation outlines.
High-converting direct response copy following Creator Monetize methodology.
"""
from __future__ import annotations
from .base import BaseModule


class FunnelCopyModule(BaseModule):
    name = "funnel_copy"
    description = "Generate funnel page copy and VSL scripts"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a world-class direct response copywriter specializing in VSLs and funnel copy following the Creator Monetize methodology.

Your writing principles:
1. Emotional Connection First — every piece of copy must connect with the reader's pain, desire, or identity before making any logical arguments.
2. Curiosity is King — open loops, tease outcomes, make them need to know what comes next.
3. Psychological Triggers — use scarcity, social proof, authority, reciprocity, and commitment/consistency naturally (never forced).
4. The 8-Section VSL Structure — Hook, Problem, Agitate, Story, Solution, Proof, Offer, Close. Every VSL follows this arc.
5. RCIBO Framework — Role, Context, Instructions, Boundaries, Output format. Use this to structure AI-assisted content generation.
6. Page-Specific Templates — each funnel page type (opt-in, booking, sales, post-booking) has its own proven structure and psychological flow.
7. Webinar Presentations — follow the 26-step presentation structure for maximum conversion.

Your tone: confident, conversational, emotionally intelligent. You write like you're talking to one person, not an audience. You use short sentences. You create rhythm. And you always, always close.

Never write generic copy. Every word earns its place. If it doesn't sell, inform, or build trust — cut it."""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {
                "name": "write_vsl",
                "description": "Write a VSL script",
                "params": ["funnel_type", "offer", "audience", "tone"],
            },
            {
                "name": "page_copy",
                "description": "Generate funnel page copy",
                "params": ["page_type", "offer", "headline"],
            },
            {
                "name": "rcibo_prompt",
                "description": "Generate RCIBO AI prompt for VSL writing",
                "params": ["offer_details", "ideal_client", "brand_pov"],
            },
            {
                "name": "presentation_outline",
                "description": "Generate webinar presentation outline",
                "params": ["topic", "offer"],
            },
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "write_vsl":
            return await self._write_vsl(params)
        elif action == "page_copy":
            return await self._page_copy(params)
        elif action == "rcibo_prompt":
            return await self._rcibo_prompt(params)
        elif action == "presentation_outline":
            return await self._presentation_outline(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _write_vsl(self, params: dict) -> dict:
        funnel_type = params.get("funnel_type", "call")
        offer = params.get("offer", "") or self.get_config("offer", "")
        audience = params.get("audience", "") or self.get_config("target_audience", "")
        tone = params.get("tone", "confident")

        vsl_templates = self.load_knowledge("vsl_templates.json")
        template = vsl_templates.get(funnel_type, vsl_templates.get("default", {}))
        funnels = self.load_knowledge("funnels.json")
        funnel_structure = funnels.get(funnel_type, {})

        prompt = f"""Write a complete VSL script for:

Funnel type: {funnel_type} ({'book a call' if funnel_type == 'call' else 'value video / direct sale'})
Offer: {offer or 'Not specified — write a versatile template with [PLACEHOLDER] markers'}
Target audience: {audience or 'Not specified — write for a general business audience'}
Tone: {tone}

VSL Template Structure:
{template}

Funnel Context:
{funnel_structure}

Follow the 8-section VSL structure:

1. HOOK (0:00-0:30) — Pattern interrupt. Stop the scroll. Use a bold claim, shocking stat, or provocative question.
2. PROBLEM (0:30-2:00) — Name the pain. Be specific. Show you understand their world better than they do.
3. AGITATE (2:00-3:30) — Twist the knife. What happens if they don't solve this? Paint the worst-case scenario.
4. STORY (3:30-6:00) — Your/client's story. Relatable struggle → discovery → transformation.
5. SOLUTION (6:00-8:00) — Introduce your method/framework. Name it. Make it feel unique and proprietary.
6. PROOF (8:00-10:00) — Testimonials, results, case studies. Stack social proof.
7. OFFER (10:00-12:00) — Present the offer. Stack value. Price anchor. Create urgency.
8. CLOSE (12:00-end) — CTA. Overcome final objections. Risk reversal. Last push.

For each section provide:
- Exact script (word-for-word)
- Delivery notes (tone, pace, emphasis)
- Visual cues (what to show on screen)
- Approximate duration

Output as structured JSON with all 8 sections."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_vsl", {"funnel_type": funnel_type, "offer": offer, "result": response})
        return {
            "status": "ok",
            "data": {"vsl_script": response, "funnel_type": funnel_type, "offer": offer},
            "summary": f"VSL script written for '{funnel_type}' funnel — offer: '{offer or 'template'}'",
        }

    async def _page_copy(self, params: dict) -> dict:
        page_type = params.get("page_type", "opt_in")
        offer = params.get("offer", "") or self.get_config("offer", "")
        headline = params.get("headline", "")

        funnels = self.load_knowledge("funnels.json")
        page_templates = funnels.get("page_templates", {})
        page_structure = page_templates.get(page_type, {})

        prompt = f"""Write complete funnel page copy for:

Page type: {page_type}
Offer: {offer or 'Not specified — write a versatile template'}
Headline suggestion: {headline or 'Generate a high-converting headline'}

Page Structure Template:
{page_structure}

Write copy for a {page_type} page following this structure:

{"OPT-IN PAGE: Headline (curiosity/benefit) → Sub-headline (specificity) → 3 bullet points (what they'll learn) → CTA button → Social proof line" if page_type == "opt_in" else ""}
{"BOOKING PAGE: Headline (value of the call) → What we'll cover (3-5 bullets) → Who this is for / not for → Calendar embed area → Testimonials → FAQ" if page_type == "booking" else ""}
{"SALES PAGE: Headline → Problem section → Agitate → Story → Solution → Benefits (feature → benefit → meaning) → Testimonials → Offer stack → Price → Guarantee → CTA → FAQ → Final CTA" if page_type == "sales" else ""}
{"POST-BOOKING PAGE: Confirmation message → What to expect → How to prepare (3 steps) → Testimonial → Reminder to show up" if page_type == "post_booking" else ""}

For each section provide:
- Copy (exact text)
- Design notes (layout, colors, emphasis)
- Conversion psychology (why this works)

Output as structured JSON."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_page_copy", {"page_type": page_type, "offer": offer, "result": response})
        return {
            "status": "ok",
            "data": {"page_copy": response, "page_type": page_type, "offer": offer},
            "summary": f"Page copy generated for '{page_type}' page",
        }

    async def _rcibo_prompt(self, params: dict) -> dict:
        offer_details = params.get("offer_details", "") or self.get_config("offer", "")
        ideal_client = params.get("ideal_client", "") or self.get_config("target_audience", "")
        brand_pov = params.get("brand_pov", "") or self.get_config("brand_voice", "")

        vsl_templates = self.load_knowledge("vsl_templates.json")
        rcibo_template = vsl_templates.get("rcibo_template", {})

        prompt = f"""Generate a complete RCIBO AI prompt for VSL script writing:

Offer Details: {offer_details or 'Generic high-ticket coaching offer'}
Ideal Client: {ideal_client or 'Business owner looking to scale'}
Brand POV: {brand_pov or 'Confident, authoritative, empathetic'}

RCIBO Template:
{rcibo_template}

Fill in the RCIBO framework:

R (Role): Define exactly who the AI should be when writing this VSL
C (Context): Provide all background needed — offer, audience, pain points, desired outcome, brand voice
I (Instructions): Step-by-step instructions for writing the VSL (reference the 8-section structure)
B (Boundaries): What to avoid — cliches, hype words, false claims, generic language
O (Output): Exact format expected — sections, word count, tone markers

The generated prompt should be ready to paste into any AI tool and produce a high-quality VSL draft.

Output as structured JSON with keys: role, context, instructions, boundaries, output_format, full_prompt (the complete assembled prompt)."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"rcibo_prompt": response, "offer": offer_details},
            "summary": f"RCIBO prompt generated for offer: '{offer_details or 'generic'}'",
        }

    async def _presentation_outline(self, params: dict) -> dict:
        topic = params.get("topic", "") or self.get_config("niche", "")
        offer = params.get("offer", "") or self.get_config("offer", "")

        vsl_templates = self.load_knowledge("vsl_templates.json")
        presentation_structure = vsl_templates.get("presentation_26_step", {})

        prompt = f"""Generate a complete webinar presentation outline:

Topic: {topic or 'Not specified — create a general framework'}
Offer: {offer or 'Not specified — create offer placeholder sections'}

26-Step Presentation Structure:
{presentation_structure}

Create a detailed outline following the 26-step webinar structure:

1. Welcome & Pattern Interrupt
2. Big Promise (what they'll walk away with)
3. Credibility (why you, why now)
4. Story (the discovery / origin story)
5. Framework Introduction (name your method)
6-8. Pillar 1 — teach concept + example + quick win
9-11. Pillar 2 — teach concept + example + quick win
12-14. Pillar 3 — teach concept + example + quick win
15. Transition to Offer (the gap between knowing and doing)
16. Introduce the Offer
17. What's Included (stack items)
18. Bonuses
19. Price Reveal + Anchor
20. Guarantee
21. Social Proof Montage
22. FAQ / Objection Handling
23. Urgency / Scarcity
24. Final CTA
25. Q&A
26. Last Chance Close

For each step provide:
- Slide content (headline + bullets)
- Speaker notes (what to say)
- Duration (minutes)
- Engagement tactic (poll, question, demo, etc.)

Output as structured JSON array of 26 step objects."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_presentation", {"topic": topic, "offer": offer, "result": response})
        return {
            "status": "ok",
            "data": {"outline": response, "topic": topic, "offer": offer},
            "summary": f"26-step presentation outline generated for '{topic or 'general'}'",
        }
