"""
Launch Module — pre-launch plans, quick activation, and 28-day launch roadmaps.
Creator Monetize Pre-Launch Method. Money loves speed.
"""
from __future__ import annotations
from .base import BaseModule


class LaunchModule(BaseModule):
    name = "launch"
    description = "Pre-launch sequences and quick activation strategies"
    version = "1.0.0"

    SYSTEM_PROMPT = """You are a launch strategist using the Creator Monetize Pre-Launch Method and Designating Trajectory system.

Your core belief: NOTHING HAPPENS WITHOUT LAUNCHING. Money loves speed. Perfection is the enemy of revenue. A launched imperfect offer beats an unlaunched perfect one every single time.

Launch Philosophy:
1. Speed Over Perfection — launch fast, iterate later. Your first version is never your final version.
2. Pre-Launch Builds Desire — the launch doesn't start on launch day. It starts 7-14 days before with strategic content that primes the audience.
3. Two Launch Types:
   - QUIET LAUNCH: Soft open to existing audience. Email list + social + DMs. No ads. Test the offer, get testimonials, refine.
   - LOUD LAUNCH: Full campaign. Ads + content + email + partnerships. Scale what's proven.
4. Discount Strategy: Pre-launch pricing creates urgency without devaluing. "Founding member" > "discount." Early adopters get rewarded, not discounted.
5. The 28-Day Framework: Based on Designating Trajectory classification. Each pathway gets a customized 28-day roadmap with daily actions.

Quick Activation Paths:
- WITH email list: Direct offer + nurture sequence
- WITHOUT email list: Content → Lead magnet → Quick nurture → Offer (7-day sprint)
- List size < 100: Personal outreach + DM strategy + micro-content
- List size 100-1000: Segment + targeted offer + social proof campaign
- List size > 1000: Full launch sequence + potentially ads

Pre-Launch Timeline:
- Day -14 to -7: Seed content (stories, problems, hints)
- Day -7 to -3: Build anticipation (waitlist, early access, countdown)
- Day -3 to -1: Final push (urgency, limited spots, bonus deadline)
- Day 0: LAUNCH (doors open, full sequence fires)
- Day 1-7: Open cart (email sequence, social proof, objection handling)
- Day 7: Close (final deadline, last chance)

Your tone: energetic, action-oriented, no fluff. Every recommendation has a specific action and deadline."""

    def get_system_prompt(self) -> str:
        return self.SYSTEM_PROMPT

    def get_actions(self) -> list[dict]:
        return [
            {
                "name": "pre_launch_plan",
                "description": "Generate pre-launch plan with timeline and tasks",
                "params": ["product", "launch_date", "launch_type"],
            },
            {
                "name": "quick_activation",
                "description": "Generate quick activation plan",
                "params": ["has_email_list", "list_size", "niche"],
            },
            {
                "name": "launch_28_day",
                "description": "Generate full 28-day launch roadmap based on trajectory",
                "params": ["pathway_number", "niche", "product"],
            },
        ]

    async def execute(self, action: str, params: dict) -> dict:
        if action == "pre_launch_plan":
            return await self._pre_launch_plan(params)
        elif action == "quick_activation":
            return await self._quick_activation(params)
        elif action == "launch_28_day":
            return await self._launch_28_day(params)
        return {"status": "error", "data": None, "summary": f"Unknown action: {action}"}

    async def _pre_launch_plan(self, params: dict) -> dict:
        product = params.get("product", "") or self.get_config("product", "")
        launch_date = params.get("launch_date", "")
        launch_type = params.get("launch_type", "quiet")

        funnels = self.load_knowledge("funnels.json")
        launch_funnels = funnels.get("launch_funnels", {})
        email_knowledge = self.load_knowledge("email_sequences.json")
        launch_emails = email_knowledge.get("launch_sequence", {})

        prompt = f"""Generate a complete pre-launch plan:

Product: {product or 'Not specified — create a template plan'}
Launch Date: {launch_date or 'Not specified — create a relative timeline (Day -14, Day -7, etc.)'}
Launch Type: {launch_type} ({'Soft launch to existing audience, no ads' if launch_type == 'quiet' else 'Full campaign with ads, content, email, partnerships'})

Launch Funnel Templates:
{launch_funnels}

Email Launch Templates:
{launch_emails}

Create a detailed pre-launch plan with:

PHASE 1 — SEED (Day -14 to -7):
- Content calendar (what to post each day, which platform)
- Story/post ideas that prime the audience for the offer
- Questions to ask that surface demand
- Behind-the-scenes content that builds curiosity

PHASE 2 — BUILD (Day -7 to -3):
- Waitlist / early access setup
- Email sequence to prime list
- Social proof collection strategy
- Countdown content

PHASE 3 — IGNITE (Day -3 to -1):
- Final anticipation builders
- DM outreach plan (who to contact personally)
- Bonus deadline announcements
- Technical checklist (payment, pages, emails loaded)

PHASE 4 — LAUNCH (Day 0):
- Launch day minute-by-minute plan
- Email blast schedule
- Social media posting schedule
- Live component (if applicable)

PHASE 5 — SUSTAIN (Day 1 to 7):
- Daily email schedule
- Social proof posting
- Objection handling content
- Urgency escalation

PHASE 6 — CLOSE (Day 7):
- Cart close sequence
- Final push emails
- Post-launch analysis checklist

Also include:
- Discount / pricing strategy (founding member vs discount vs bonuses)
- Risk mitigation (what if low sales? pivot plan)
- Success metrics (daily targets)
- Tools needed (pages, email platform, payment processor)

Output as structured JSON with all 6 phases."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_launch_plan", {"product": product, "launch_type": launch_type, "result": response})
        return {
            "status": "ok",
            "data": {"plan": response, "product": product, "launch_type": launch_type},
            "summary": f"Pre-launch plan generated — type: {launch_type}, product: '{product or 'template'}'",
        }

    async def _quick_activation(self, params: dict) -> dict:
        has_email_list = params.get("has_email_list", False)
        list_size = params.get("list_size", 0)
        niche = params.get("niche", "") or self.get_config("niche", "")

        pathways = self.load_knowledge("trajectory_pathways.json")
        activation_paths = pathways.get("activation_paths", {})

        prompt = f"""Generate a quick activation plan:

Has email list: {has_email_list}
List size: {list_size}
Niche: {niche or 'Not specified'}

Activation Paths Reference:
{activation_paths}

Based on the creator's current position, generate a path-specific activation plan:

{"PATH: NO LIST" if not has_email_list else f"PATH: LIST SIZE {list_size}"}

{'''NO LIST ACTIVATION (7-day sprint):
Day 1: Create lead magnet (checklist/template/mini-course)
Day 2: Set up opt-in page + thank you page
Day 3: Create 3 pieces of content driving to opt-in
Day 4: Post content + DM outreach to warm contacts
Day 5: Follow up + create 2 more content pieces
Day 6: Send first value email to new subscribers
Day 7: Soft pitch via email + DM to engaged subscribers''' if not has_email_list else ''}

{f'''SMALL LIST ACTIVATION (list < 100):
- Personal outreach strategy (DM each subscriber)
- Micro-content strategy (stories, polls, questions)
- "Beta tester" positioning for offer validation
- 1-on-1 call offer to top engagers''' if has_email_list and list_size < 100 else ''}

{f'''MEDIUM LIST ACTIVATION (100-1000):
- Segmentation strategy (who's hot, warm, cold)
- Targeted offer for each segment
- Social proof campaign (collect testimonials from best fits)
- Mini launch sequence (5 emails over 5 days)''' if has_email_list and 100 <= list_size < 1000 else ''}

{f'''LARGE LIST ACTIVATION (1000+):
- Full segmented launch sequence
- Multi-channel campaign (email + social + potentially ads)
- Webinar / live event component
- Affiliate/referral component for existing customers''' if has_email_list and list_size >= 1000 else ''}

For each day/step provide:
- Specific action (not vague — exact thing to do)
- Time estimate
- Template or script to use
- Success metric for the day
- "Done is better than perfect" minimum viable version

Output as structured JSON with day-by-day plan."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_activation", {
            "has_list": has_email_list,
            "list_size": list_size,
            "niche": niche,
            "result": response,
        })
        return {
            "status": "ok",
            "data": {"plan": response, "has_email_list": has_email_list, "list_size": list_size},
            "summary": f"Quick activation plan generated — list: {'yes' if has_email_list else 'no'}, size: {list_size}",
        }

    async def _launch_28_day(self, params: dict) -> dict:
        pathway_number = params.get("pathway_number", 1)
        niche = params.get("niche", "") or self.get_config("niche", "")
        product = params.get("product", "") or self.get_config("product", "")

        pathways = self.load_knowledge("trajectory_pathways.json")
        pathway_details = pathways.get("pathways", {}).get(str(pathway_number), {})
        funnels = self.load_knowledge("funnels.json")
        email_knowledge = self.load_knowledge("email_sequences.json")

        prompt = f"""Generate a full 28-day launch roadmap:

Pathway Number: {pathway_number}
Pathway Details: {pathway_details}
Niche: {niche or 'Not specified'}
Product: {product or 'Not specified — create a general roadmap'}

Funnel Options:
{funnels.get('funnel_types', {})}

Email Sequence Options:
{email_knowledge.get('sequence_types', {})}

Create a day-by-day 28-day launch roadmap tailored to Pathway {pathway_number}:

WEEK 1 — FOUNDATION (Days 1-7):
Focus: Set up infrastructure, validate offer, start content engine
- Day-by-day tasks
- Key milestone: offer validated, funnel drafted

WEEK 2 — BUILD (Days 8-14):
Focus: Build funnel, create content bank, grow audience
- Day-by-day tasks
- Key milestone: funnel live, 7+ pieces of content published

WEEK 3 — PRE-LAUNCH (Days 15-21):
Focus: Pre-launch sequence, build anticipation, warm up audience
- Day-by-day tasks
- Key milestone: waitlist/interest built, launch emails loaded

WEEK 4 — LAUNCH & SELL (Days 22-28):
Focus: Launch, sell, handle objections, close
- Day-by-day tasks
- Key milestone: first sales, testimonials collected

For each of the 28 days provide:
- Day number
- Phase (foundation/build/pre-launch/launch)
- Primary task (the ONE thing that must get done)
- Secondary tasks (2-3 supporting actions)
- Content to create/post
- Email to send (if applicable)
- Success metric
- Time estimate (hours)
- "Minimum viable" version (if short on time)

Also include:
- Weekly reflection prompts
- Pivot triggers (when to change strategy)
- Revenue targets by week
- Momentum builders (small wins to celebrate)

Output as structured JSON array of 28 day objects grouped by week."""

        response = await self.ask_ai(prompt, self.SYSTEM_PROMPT)
        await self.save("last_28_day", {
            "pathway": pathway_number,
            "niche": niche,
            "product": product,
            "result": response,
        })
        return {
            "status": "ok",
            "data": {"roadmap": response, "pathway": pathway_number, "niche": niche, "product": product},
            "summary": f"28-day launch roadmap generated for Pathway {pathway_number} — niche: '{niche or 'general'}'",
        }
