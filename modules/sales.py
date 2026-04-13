"""
Sales Module — scripts, objection handling, offer creation, unique mechanisms, price anchoring.
Pain x Confidence framework. Creator Monetize sales methodology.
"""
from __future__ import annotations
from .base import BaseModule


class SalesModule(BaseModule):
    name = "sales"
    description = "Sales scripts, objection handling, and offer creation"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are an expert sales strategist using the Creator Monetize sales methodology.

Your core framework: Pain x Confidence = Sale
- Pain: How badly do they need this solved? (scale their awareness)
- Confidence: How sure are they that YOU can solve it? (build through proof, rapport, frame)
- When both are high, the sale is inevitable. When either is low, the sale dies.

The 5 Core Tenets of Selling:
1. Never Judge — every prospect deserves respect regardless of their situation, objections, or attitude.
2. Never Give Up Easily — most sales happen after the 3rd-5th objection. Persistence with empathy.
3. Ask Hard Questions — go where it's uncomfortable. "What happens if you don't fix this?" "How long have you been stuck?"
4. Maintain Frame — you are the expert. You have the solution. Never break frame or get defensive.
5. Keep Conviction — you believe in your offer because it genuinely helps people. This isn't manipulation, it's matching.

Objection Handling: DECPC Formula
- D (Deflect): "That's a great point..." (acknowledge without agreeing)
- E (Empathize): "I totally understand..." (show you get it)
- C (Clarify): "Just so I understand..." (dig deeper — is this the real objection?)
- P (Problem): "So if [objection] wasn't a factor, would you be ready?" (isolate the objection)
- C (Close): Address and re-close with confidence

The 6 True Objections (everything else is a smokescreen):
1. No money (budget)
2. No time (priority)
3. No trust (in you or the method)
4. No need (don't believe they have the problem)
5. No authority (need someone else's approval)
6. No urgency (can wait, no deadline pressure)

Elixir Genesis — 8-step offer creation for irresistible offers.

Your tone: confident but never pushy. Consultative, not salesy. You help people make decisions, not force them."""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {
                "name": "sales_script",
                "description": "Generate customized sales call script",
                "params": ["product", "price", "niche"],
            },
            {
                "name": "handle_objection",
                "description": "Handle a specific objection using DECPC formula",
                "params": ["objection", "context"],
            },
            {
                "name": "create_offer",
                "description": "Build offer using 8-step Elixir Genesis",
                "params": ["dream_outcome", "target_audience", "product_type"],
            },
            {
                "name": "unique_mechanism",
                "description": "Generate unique mechanism statement",
                "params": ["niche", "method"],
            },
            {
                "name": "price_anchor",
                "description": "Generate price anchoring script",
                "params": ["price", "value_points"],
            },
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "sales_script":
            return await self._sales_script(params)
        elif action == "handle_objection":
            return await self._handle_objection(params)
        elif action == "create_offer":
            return await self._create_offer(params)
        elif action == "unique_mechanism":
            return await self._unique_mechanism(params)
        elif action == "price_anchor":
            return await self._price_anchor(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _sales_script(self, params: dict) -> dict:
        product = params.get("product", "") or self.get_config("product", "")
        price = params.get("price", "") or self.get_config("price", "")
        niche = params.get("niche", "") or self.get_config("niche", "")

        sales_system = self.load_knowledge("sales_system.json")
        script_template = sales_system.get("script_template", {})
        psychology = self.load_knowledge("sales_psychology.json")

        prompt = f"""Generate a complete sales call script:

Product: {product or 'Not specified — use [PRODUCT] placeholders'}
Price: {price or 'Not specified — use [PRICE] placeholders'}
Niche: {niche or 'Not specified — keep it general'}

Script Template:
{script_template}

Sales Psychology Context:
{psychology.get('call_framework', {})}

Write a 12-stage sales call script:

Stage 1 — RAPPORT (2 min): Small talk with purpose. Find common ground. Set the tone.
Stage 2 — FRAME SET (1 min): "Here's how this call works..." Set expectations. You're in control.
Stage 3 — CURRENT SITUATION (3 min): "Where are you at right now?" Deep discovery questions.
Stage 4 — PAIN IDENTIFICATION (5 min): "What's the biggest challenge?" Dig 3 levels deep. "Why is that a problem?" x3.
Stage 5 — DREAM OUTCOME (3 min): "If we could wave a magic wand..." Paint the vision.
Stage 6 — GAP ANALYSIS (2 min): "So you're at [current] and want to get to [dream]... what's in the way?"
Stage 7 — PAST ATTEMPTS (3 min): "What have you tried before?" Understand failed solutions.
Stage 8 — COMMITMENT CHECK (1 min): "On a scale of 1-10, how committed are you to solving this?"
Stage 9 — SOLUTION PRESENT (5 min): Present your offer as the bridge from current to dream.
Stage 10 — VALUE STACK (3 min): Stack all components with individual values.
Stage 11 — PRICE REVEAL (2 min): Anchor high, reveal actual price, payment options.
Stage 12 — CLOSE (5 min): Ask for the sale. Handle objections. Get the yes.

For each stage provide:
- Exact script with fill-in prompts [like this]
- Key questions to ask
- What to listen for (buying signals / red flags)
- Transition phrase to next stage
- Psychology principle at play

Output as structured JSON array of 12 stage objects."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_sales_script", {"product": product, "price": price, "result": response})
        return {
            "status": "ok",
            "data": {"script": response, "product": product, "price": price, "stages": 12},
            "summary": f"12-stage sales script generated for '{product or 'template'}' at {price or '[PRICE]'}",
        }

    async def _handle_objection(self, params: dict) -> dict:
        objection = params.get("objection", "")
        context = params.get("context", "")

        sales_system = self.load_knowledge("sales_system.json")
        objection_framework = sales_system.get("objection_framework", {})
        psychology = self.load_knowledge("sales_psychology.json")
        true_objections = psychology.get("true_objections", {})

        prompt = f"""Handle this sales objection:

Objection: "{objection}"
Context: {context or 'General sales call context'}

Objection Framework:
{objection_framework}

The 6 True Objections:
{true_objections}

Steps:
1. Classify: Which of the 6 true objections is this really? (it may be a smokescreen for a deeper one)
2. Apply DECPC Formula:
   - D (Deflect): Acknowledge without agreeing
   - E (Empathize): Show genuine understanding
   - C (Clarify): Ask a question to get to the real objection
   - P (Problem): Isolate — "If [objection] wasn't a factor, would you be ready?"
   - C (Close): Address and re-close

3. Provide 3 different response options:
   - Soft (empathetic, question-based)
   - Direct (confident, challenge-based)
   - Story-based (use an analogy or client example)

4. Include follow-up questions for each response
5. Warning signs this objection might be real vs. smokescreen

Output as structured JSON with keys: classification, decpc_response, soft_response, direct_response, story_response, follow_ups, is_smokescreen_probability."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"handling": response, "objection": objection},
            "summary": f"Objection handled: '{objection[:60]}...'",
        }

    async def _create_offer(self, params: dict) -> dict:
        dream_outcome = params.get("dream_outcome", "")
        target_audience = params.get("target_audience", "") or self.get_config("target_audience", "")
        product_type = params.get("product_type", "coaching")

        offer_creation = self.load_knowledge("offer_creation.json")
        elixir_genesis = offer_creation.get("elixir_genesis", {})

        prompt = f"""Build a complete offer using the 8-step Elixir Genesis framework:

Dream Outcome: {dream_outcome or 'Not specified — build a template'}
Target Audience: {target_audience or 'Not specified — general business audience'}
Product Type: {product_type}

Elixir Genesis Framework:
{elixir_genesis}

Complete all 8 steps:

Step 1 — DREAM OUTCOME: What's the vivid, specific transformation? (before → after)
Step 2 — IDEAL CLIENT: Who is this PERFECT for? (demographics + psychographics)
Step 3 — CORE MECHANISM: What's your unique method/process? Name it. Make it proprietary.
Step 4 — COMPONENTS: Break the offer into deliverables (modules, calls, resources, tools)
Step 5 — VALUE STACK: Assign a value to each component. Total perceived value should be 5-10x the price.
Step 6 — BONUSES: 3 bonuses that address specific objections. Each bonus removes a barrier.
Step 7 — GUARANTEE: Risk reversal. What promise can you make? (results-based, time-based, or hybrid)
Step 8 — URGENCY: Why now? (deadline, limited spots, price increase, bonus expiration)

Additionally provide:
- One-liner offer statement (under 15 words)
- Elevator pitch (30 seconds)
- Offer name suggestions (3 options)
- Pricing recommendation with rationale

Output as structured JSON with all 8 steps + additional items."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_offer", {"dream_outcome": dream_outcome, "product_type": product_type, "result": response})
        return {
            "status": "ok",
            "data": {"offer": response, "dream_outcome": dream_outcome, "product_type": product_type},
            "summary": f"Offer created via Elixir Genesis — type: {product_type}",
        }

    async def _unique_mechanism(self, params: dict) -> dict:
        niche = params.get("niche", "") or self.get_config("niche", "")
        method = params.get("method", "")

        offer_creation = self.load_knowledge("offer_creation.json")
        mechanism_framework = offer_creation.get("unique_mechanism", {})

        prompt = f"""Generate a unique mechanism statement:

Niche: {niche or 'Not specified'}
Method/Process: {method or 'Not specified — create a general framework'}

Unique Mechanism Framework:
{mechanism_framework}

A unique mechanism is the "why this is different" — it's the proprietary process, framework, or method that makes your offer stand apart from everything else in the market.

Create:
1. Mechanism Name — catchy, proprietary-sounding (2-4 words). 3 options.
2. Mechanism Statement — "The [Name] is a [what it is] that helps [who] achieve [outcome] without [common pain point]"
3. Mechanism Story — brief origin story (how you discovered/created this method)
4. Mechanism Breakdown — 3-5 steps/pillars that make up the mechanism
5. Why It Works — the logic/science/principle behind it (makes it believable)
6. Why Nothing Else Works — positioning against alternatives without naming competitors

Output as structured JSON."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"mechanism": response, "niche": niche, "method": method},
            "summary": f"Unique mechanism generated for niche: '{niche or 'general'}'",
        }

    async def _price_anchor(self, params: dict) -> dict:
        price = params.get("price", "")
        value_points = params.get("value_points", [])

        psychology = self.load_knowledge("sales_psychology.json")
        anchoring_framework = psychology.get("price_anchoring", {})

        prompt = f"""Generate a price anchoring script:

Actual Price: {price or 'Not specified — use [PRICE] placeholder'}
Value Points: {value_points or 'Not specified — generate sample value points'}

Price Anchoring Framework:
{anchoring_framework}

Write a complete price anchoring sequence:

1. VALUE STACK — List each component with its individual value:
   "Component 1 — [description] — normally $X"
   "Component 2 — [description] — normally $X"
   Stack until total perceived value is 5-10x the actual price.

2. TOTAL VALUE REVEAL — "If you were to get all of this separately, you'd invest $[TOTAL]"

3. ANCHOR DROP — "But you're not going to pay $[TOTAL]..."

4. SECOND ANCHOR — "You're not even going to pay $[HALF]..."

5. PRICE REVEAL — "Your investment today is just $[PRICE]"

6. PAYMENT OPTIONS — Present payment plans if applicable

7. PER-DAY BREAKDOWN — "That's less than $[daily amount] per day — less than a cup of coffee"

8. RISK REVERSAL — Guarantee statement immediately after price

9. URGENCY LAYER — Why this price won't last

For each step provide:
- Exact script (word for word)
- Pause/delivery notes
- Emotional state to invoke (excitement, relief, FOMO, etc.)

Output as structured JSON array of 9 step objects."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        return {
            "status": "ok",
            "data": {"anchor_script": response, "price": price},
            "summary": f"Price anchoring script generated for {price or '[PRICE]'}",
        }
