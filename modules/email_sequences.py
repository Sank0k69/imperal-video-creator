"""
Email Sequences Module — promo, nurture, webinar, reactivation, and newsletter emails.
Three pillars: increase positive belief, increase pain, destroy limiting beliefs.
"""
from __future__ import annotations
from .base import BaseModule


class EmailSequencesModule(BaseModule):
    name = "email_sequences"
    description = "Generate email sequences, broadcasts, and newsletter content"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are an email marketing expert following the Creator Monetize methodology.

Your three pillars of email persuasion:
1. Increase Positive Belief — build trust, share wins, show proof that the method works
2. Increase Pain — remind them of the cost of inaction, the frustration of staying stuck
3. Destroy Limiting Beliefs — address the "but what about..." objections before they become blockers

Your email writing rules:
- Subject lines: curiosity-driven, under 50 chars, no spam triggers, personal tone
- Opening line: hook that earns the second sentence (never "I hope this finds you well")
- Body: one idea per email, conversational tone, short paragraphs (1-3 sentences max)
- CTA: soft in nurture (reply, read, watch), direct in promo (buy, book, join)
- P.S. section: this is PRIME selling real estate — always include it, always make it count
- Personalization: use [FIRST_NAME] and reference their specific situation
- Tone: write like a smart friend giving advice over coffee, not a corporation sending a memo

Email sequence types:
- Promo (6 emails): announcement → value → social proof → objection crusher → urgency → last chance
- Nurture (6 emails): welcome → quick win → story → deeper value → case study → soft pitch
- Webinar: multi-channel (email + telegram + sms) reminder sequences
- Reactivation: re-engage cold subscribers with personality and a fresh hook
- Newsletter: 5 primary types (value, story, curated, hybrid, personal)

Every email must pass the "would I open this?" test."""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {
                "name": "promo_sequence",
                "description": "Generate 6-email promo sequence",
                "params": ["product_name", "offer", "deadline"],
            },
            {
                "name": "nurture_sequence",
                "description": "Generate 6-email nurture sequence",
                "params": ["product", "dream_outcome"],
            },
            {
                "name": "webinar_sequence",
                "description": "Generate webinar reminder sequence",
                "params": ["webinar_title", "date", "link", "channels"],
            },
            {
                "name": "reactivation",
                "description": "Generate list reactivation email",
                "params": ["brand", "niche", "time_away"],
            },
            {
                "name": "newsletter",
                "description": "Generate newsletter email",
                "params": ["topic_type", "niche"],
            },
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "promo_sequence":
            return await self._promo_sequence(params)
        elif action == "nurture_sequence":
            return await self._nurture_sequence(params)
        elif action == "webinar_sequence":
            return await self._webinar_sequence(params)
        elif action == "reactivation":
            return await self._reactivation(params)
        elif action == "newsletter":
            return await self._newsletter(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _promo_sequence(self, params: dict) -> dict:
        product_name = params.get("product_name", "") or self.get_config("product", "")
        offer = params.get("offer", "") or self.get_config("offer", "")
        deadline = params.get("deadline", "")

        knowledge = self.load_knowledge("email_sequences.json")
        promo_template = knowledge.get("promo_sequence", {})

        prompt = f"""Write a complete 6-email promotional sequence:

Product: {product_name or 'Not specified — use [PRODUCT] placeholders'}
Offer: {offer or 'Not specified — use [OFFER] placeholders'}
Deadline: {deadline or '5 days from send'}

Promo Template:
{promo_template}

Write 6 emails following this arc:

Email 1 — ANNOUNCEMENT (Day 1):
The big reveal. Build excitement. Tease the offer. Don't sell yet — create anticipation.

Email 2 — VALUE (Day 2):
Lead with value. Teach something useful related to the product. Soft mention of the offer.

Email 3 — SOCIAL PROOF (Day 3):
Stack testimonials and case studies. Let others sell for you. "Don't take my word for it..."

Email 4 — OBJECTION CRUSHER (Day 4):
Address the top 3 objections head-on. Use the "I know what you're thinking..." framework.

Email 5 — URGENCY (Day 5):
Deadline approaching. Scarcity is real. Pain of missing out > pain of paying.

Email 6 — LAST CHANCE (Day 6):
Final email. Cart closing. No more chances. Direct, emotional, urgent.

For each email provide:
- Subject line (primary + 2 alternatives)
- Preview text
- Body copy (formatted with paragraphs)
- CTA (button text + link placeholder)
- P.S. section
- Send timing (day + time recommendation)
- Pillar focus (positive belief / pain / limiting belief)

Output as structured JSON array of 6 email objects."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_promo_sequence", {"product": product_name, "result": response})
        return {
            "status": "ok",
            "data": {"sequence": response, "product": product_name, "emails_count": 6},
            "summary": f"6-email promo sequence generated for '{product_name or 'template'}'",
        }

    async def _nurture_sequence(self, params: dict) -> dict:
        product = params.get("product", "") or self.get_config("product", "")
        dream_outcome = params.get("dream_outcome", "")

        knowledge = self.load_knowledge("email_sequences.json")
        nurture_template = knowledge.get("nurture_sequence", {})

        prompt = f"""Write a complete 6-email nurture sequence for a value video funnel:

Product: {product or 'Not specified — use [PRODUCT] placeholders'}
Dream Outcome: {dream_outcome or 'Not specified — use transformation language'}

Nurture Template:
{nurture_template}

Write 6 emails following this arc:

Email 1 — WELCOME (Immediate):
Welcome to the community. Set expectations. Deliver the promised value (link to video/resource). Personal tone.

Email 2 — QUICK WIN (Day 2):
Give them one actionable tip they can implement in 10 minutes. Build trust through results.

Email 3 — STORY (Day 4):
Share your/client's transformation story. Relatable struggle → discovery → results. Emotional connection.

Email 4 — DEEPER VALUE (Day 6):
Teach a framework or methodology. Position yourself as the expert. Reference the dream outcome.

Email 5 — CASE STUDY (Day 8):
Detailed case study of a client/student success. Specific numbers. Before → after.

Email 6 — SOFT PITCH (Day 10):
Natural transition to the offer. "If you've been getting value from these emails, here's how to go deeper..."

For each email provide:
- Subject line (primary + 2 alternatives)
- Preview text
- Body copy (formatted with paragraphs)
- CTA (soft — reply, read, watch for 1-5; direct for 6)
- P.S. section
- Send timing (day + time recommendation)
- Pillar focus (positive belief / pain / limiting belief)

Output as structured JSON array of 6 email objects."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_nurture_sequence", {"product": product, "result": response})
        return {
            "status": "ok",
            "data": {"sequence": response, "product": product, "emails_count": 6},
            "summary": f"6-email nurture sequence generated for '{product or 'template'}'",
        }

    async def _webinar_sequence(self, params: dict) -> dict:
        webinar_title = params.get("webinar_title", "")
        date = params.get("date", "")
        link = params.get("link", "[WEBINAR_LINK]")
        channels = params.get("channels", ["email"])

        knowledge = self.load_knowledge("email_sequences.json")
        webinar_template = knowledge.get("webinar_sequence", {})

        prompt = f"""Write a complete webinar reminder sequence across multiple channels:

Webinar Title: {webinar_title or 'Not specified — use [WEBINAR_TITLE] placeholder'}
Date: {date or 'Not specified — use [DATE] placeholder'}
Registration Link: {link}
Channels: {', '.join(channels) if isinstance(channels, list) else channels}

Webinar Template:
{webinar_template}

Generate messages for each channel requested:

{"EMAIL SEQUENCE:" if "email" in channels else ""}
{"- Confirmation email (immediate after registration)" if "email" in channels else ""}
{"- Reminder 1 (24 hours before)" if "email" in channels else ""}
{"- Reminder 2 (1 hour before)" if "email" in channels else ""}
{"- 'We're live!' (at start time)" if "email" in channels else ""}
{"- Replay email (next day, for no-shows)" if "email" in channels else ""}

{"TELEGRAM MESSAGES:" if "telegram" in channels else ""}
{"- Confirmation message (immediate)" if "telegram" in channels else ""}
{"- Reminder (2 hours before)" if "telegram" in channels else ""}
{"- 'Starting now!' (at start time)" if "telegram" in channels else ""}

{"SMS MESSAGES:" if "sms" in channels else ""}
{"- Confirmation (immediate, under 160 chars)" if "sms" in channels else ""}
{"- Reminder (1 hour before, under 160 chars)" if "sms" in channels else ""}
{"- 'Live now!' (at start time, under 160 chars)" if "sms" in channels else ""}

For email messages include: subject line, preview text, body, CTA.
For telegram messages include: message text (with emoji, casual tone).
For SMS include: message text (under 160 chars, with link).

Output as structured JSON grouped by channel."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_webinar_sequence", {"title": webinar_title, "channels": channels, "result": response})
        return {
            "status": "ok",
            "data": {"sequence": response, "webinar_title": webinar_title, "channels": channels},
            "summary": f"Webinar reminder sequence generated for '{webinar_title or 'template'}' — channels: {channels}",
        }

    async def _reactivation(self, params: dict) -> dict:
        brand = params.get("brand", "") or self.get_config("brand", "")
        niche = params.get("niche", "") or self.get_config("niche", "")
        time_away = params.get("time_away", "a while")

        knowledge = self.load_knowledge("email_sequences.json")
        reactivation_template = knowledge.get("reactivation_template", {})

        prompt = f"""Write a single reactivation email for a cold subscriber:

Brand: {brand or 'Not specified — use [BRAND] placeholder'}
Niche: {niche or 'Not specified — keep it general'}
Time away: {time_away}

Reactivation Template:
{reactivation_template}

Write an email that:
1. Acknowledges the silence with humor/honesty ("It's been {time_away}...")
2. Doesn't guilt-trip — makes them curious about what they've missed
3. Leads with a fresh, valuable insight or resource
4. Gives them a clear reason to stay (what's coming next)
5. Offers an easy unsubscribe as a power move ("If this isn't for you anymore, no hard feelings")
6. P.S. with a teaser for upcoming content/offer

Tone: human, slightly self-deprecating, genuinely helpful.

Provide:
- Subject line (primary + 2 alternatives)
- Preview text
- Body copy
- CTA
- P.S. section

Output as structured JSON."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"email": response, "brand": brand, "time_away": time_away},
            "summary": f"Reactivation email generated — time away: {time_away}",
        }

    async def _newsletter(self, params: dict) -> dict:
        topic_type = params.get("topic_type", "value")
        niche = params.get("niche", "") or self.get_config("niche", "")

        knowledge = self.load_knowledge("email_sequences.json")
        newsletter_types = knowledge.get("newsletter_types", {})
        type_template = newsletter_types.get(topic_type, {})

        prompt = f"""Write a single newsletter email:

Type: {topic_type}
Niche: {niche or 'Not specified — keep it general'}

Newsletter Type Template:
{type_template}

The 5 primary newsletter types:
1. VALUE — Teach something actionable. Framework or tip they can use today.
2. STORY — Personal narrative with a lesson. Vulnerability + insight.
3. CURATED — Best resources, links, tools you found this week. Your commentary on each.
4. HYBRID — Mix of value + story + curated. The "weekly digest" format.
5. PERSONAL — Raw, honest update. Behind the scenes. What's working, what's not.

Write a {topic_type} newsletter that:
- Opens with a hook (not "Hey [NAME], hope you're well")
- Delivers genuine value in under 500 words
- Has a clear takeaway or action item
- Feels like it came from a real person
- Ends with a CTA (reply, share, or click)
- P.S. with something personal or teaser

Provide:
- Subject line (primary + 2 alternatives)
- Preview text
- Body copy (formatted)
- CTA
- P.S. section
- Best send day/time for this type

Output as structured JSON."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"newsletter": response, "type": topic_type, "niche": niche},
            "summary": f"Newsletter ({topic_type}) generated for niche: '{niche or 'general'}'",
        }
