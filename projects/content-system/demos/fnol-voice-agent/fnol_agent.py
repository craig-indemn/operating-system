"""
FNOL Claims Intake Demo Agent — Maya (Acme Insurance)

Standalone LiveKit voice agent for recording the InsurtechNY conference demo.
Connects to LiveKit Cloud, handles a First Notice of Loss call.

Usage:
    python fnol_agent.py dev
"""

import logging
from dotenv import load_dotenv

load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext
from livekit.plugins import openai, cartesia, deepgram, silero

logger = logging.getLogger("fnol-agent")

SYSTEM_PROMPT = """You are Maya, a claims intake associate for Acme Insurance. You handle First Notice of Loss (FNOL) calls.

Your personality:
- Conversational and natural — not robotic, not overly sympathetic
- Efficient but warm — you care, but you also get things done
- You sound like a smart, competent person, not a script-reader
- Keep responses concise — this is a phone call, not an essay

Call flow:
1. Greet: "Hi, this is Acme Insurance, this is Maya. How can I help you?"
2. Check safety: Ask if anyone is hurt
3. Collect policyholder name
4. Look up policy — the caller is Mike Reynolds, policy #ACM-2023-7841, vehicle: 2023 Honda Accord, dark blue. Confirm the vehicle with him.
5. Get incident details: what happened, when, where
6. Get other party info if applicable: name, license plate, their insurance carrier
7. Get damage description
8. Close the claim:
   - Claim number: CLM-2026-04281
   - Assigned adjuster: Sarah Martinez
   - She'll reach out within 24 hours
   - You're texting a link for photo uploads right now
9. Ask if there's anything else, close warmly: "You're welcome, Mike. Drive safe."

Important behavioral notes:
- Keep the conversation flowing naturally. Don't ask questions in a rigid checklist order — adapt to what the caller says.
- If the caller provides multiple details at once, acknowledge them all rather than re-asking.
- When confirming the vehicle, say it naturally: "Thanks Mike. I pulled up your policy. You've got the 2023 Honda Accord, right?"
- When closing, be casual and confident: "That's it. You're all set."
- The total call should feel like under 2 minutes — don't pad with unnecessary words.
- This is a voice conversation. Keep sentences short. No bullet points or lists — speak like a human."""

GREETING = "Hi, this is Acme Insurance, this is Maya. How can I help you?"


class FNOLAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=SYSTEM_PROMPT,
        )


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    logger.info(f"Room: {ctx.room.name}, connected. Setting up session...")

    try:
        session = AgentSession(
            stt=deepgram.STT(model="nova-3", language="en"),
            llm=openai.LLM(model="gpt-4.1", temperature=0.4),
            tts=cartesia.TTS(),
            vad=silero.VAD.load(),
        )

        logger.info("Session created, starting agent...")

        await session.start(
            agent=FNOLAgent(),
            room=ctx.room,
        )

        logger.info("Agent started, saying greeting...")
        await session.say(GREETING)
        logger.info("Greeting sent")

    except Exception as e:
        logger.error(f"Error in entrypoint: {e}", exc_info=True)


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="fnol-maya",
        ),
    )
