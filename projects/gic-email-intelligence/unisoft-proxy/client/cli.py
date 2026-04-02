"""Unisoft AMS CLI — adapter for GIC's agency management system.

Domain-oriented commands that map to insurance operations:
  quote, submission, activity, agents, lobs, carriers

Designed as an adapter: wraps Unisoft SOAP operations via REST proxy.
When the Indemn OS entity layer exists, this becomes the Unisoft sync adapter.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Optional

import typer

from unisoft_client import UnisoftClient, UnisoftError

app = typer.Typer(name="unisoft", help="Unisoft AMS operations", no_args_is_help=True)
quote_app = typer.Typer(help="Quote operations", no_args_is_help=True)
submission_app = typer.Typer(help="Submission operations", no_args_is_help=True)
activity_app = typer.Typer(help="Activity operations", no_args_is_help=True)
agents_app = typer.Typer(help="Agent lookup", no_args_is_help=True)
lobs_app = typer.Typer(help="Lines of business", no_args_is_help=True)
carriers_app = typer.Typer(help="Carrier lookup", no_args_is_help=True)

app.add_typer(quote_app, name="quote")
app.add_typer(submission_app, name="submission")
app.add_typer(activity_app, name="activity")
app.add_typer(agents_app, name="agents")
app.add_typer(lobs_app, name="lobs")
app.add_typer(carriers_app, name="carriers")


def get_client() -> UnisoftClient:
    """Build client, pulling API key from 1Password."""
    base_url = os.environ.get("UNISOFT_PROXY_URL", "http://54.83.28.79:5000")
    api_key = os.environ.get("UNISOFT_API_KEY")
    if not api_key:
        try:
            api_key = subprocess.check_output(
                ["op", "read", "op://cli-secrets/Unisoft Proxy API Key/credential"],
                text=True,
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            typer.echo("Error: No UNISOFT_API_KEY and 1Password lookup failed.", err=True)
            raise typer.Exit(1)
    return UnisoftClient(base_url, api_key)


def out(data, compact: bool = False):
    """Print JSON output."""
    if compact:
        typer.echo(json.dumps(data, default=str))
    else:
        typer.echo(json.dumps(data, indent=2, default=str))


# --- Health ---

@app.command()
def health():
    """Check proxy health."""
    client = get_client()
    out(client.health())


# --- Quote ---

@quote_app.command("create")
def quote_create(
    lob: str = typer.Option(..., help="LOB code (e.g., CG)"),
    sublob: str = typer.Option(..., help="SubLOB code (e.g., AC)"),
    agent: int = typer.Option(..., help="Agent number"),
    name: str = typer.Option(..., help="Applicant/insured name"),
    address: str = typer.Option("", help="Street address"),
    city: str = typer.Option("", help="City"),
    state: str = typer.Option("FL", help="State code"),
    zip: str = typer.Option("", help="Zip code"),
    policy_state: str = typer.Option("FL", help="Policy state"),
    form_of_business: str = typer.Option("L", help="Form of business (C=Corp, L=LLC, I=Individual, P=Partnership)"),
    term: int = typer.Option(12, help="Term in months"),
    effective_date: Optional[str] = typer.Option(None, help="Effective date (ISO format). Defaults to today."),
    expiration_date: Optional[str] = typer.Option(None, help="Expiration date (ISO format). Defaults to effective + term."),
    business_description: str = typer.Option("", help="Description of operations"),
    email: str = typer.Option("", help="Applicant email"),
    memo: str = typer.Option("", help="Memo/notes"),
    compact: bool = typer.Option(False, "--compact", "-c", help="Compact JSON output"),
):
    """Create a new quote in Unisoft. Returns the Quote ID."""
    if not effective_date:
        eff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        eff = datetime.fromisoformat(effective_date)

    if not expiration_date:
        exp = eff + timedelta(days=term * 30)  # approximate
        # For annual (12 months), use exact year
        if term == 12:
            exp = eff.replace(year=eff.year + 1)
    else:
        exp = datetime.fromisoformat(expiration_date)

    quote_data = {
        "LOB": lob,
        "SubLOB": sublob,
        "AgentNumber": agent,
        "Name": name,
        "Address": address,
        "City": city,
        "State": state,
        "Zip": zip,
        "PolicyState": policy_state,
        "FormOfBusiness": form_of_business,
        "Term": term,
        "EffectiveDate": eff.isoformat(),
        "ExpirationDate": exp.isoformat(),
        "QuoteType": "N",
        "Status": "1",
        "OriginatingSystem": "UIMS",
    }
    if business_description:
        quote_data["BusinessDescription"] = business_description
    if email:
        quote_data["Email"] = email
    if memo:
        quote_data["Memo"] = memo

    client = get_client()
    try:
        result = client.create_quote(quote_data)
        quote_id = result.get("Quote", {}).get("QuoteID")
        if not compact:
            typer.echo(f"Quote created: {quote_id}")
        out(result, compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)


@quote_app.command("get")
def quote_get(
    id: int = typer.Option(..., help="Quote ID"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """Get a quote by ID."""
    client = get_client()
    try:
        out(client.get_quote(id), compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)


# --- Submission ---

@submission_app.command("create")
def submission_create(
    quote_id: int = typer.Option(..., help="Quote ID to add submission to"),
    carrier: int = typer.Option(..., help="Carrier number (e.g., 2=USLI)"),
    broker: int = typer.Option(1, help="Broker ID (default: 1=GIC Underwriters)"),
    description: str = typer.Option("", help="Submission description"),
    effective_date: Optional[str] = typer.Option(None, help="Effective date (ISO). Defaults to today."),
    expiration_date: Optional[str] = typer.Option(None, help="Expiration date (ISO). Defaults to effective + 1 year."),
    entered_by: str = typer.Option("ccerto", help="Username who entered"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """Create a submission on an existing quote."""
    if not effective_date:
        eff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        eff = datetime.fromisoformat(effective_date)

    if not expiration_date:
        exp = eff.replace(year=eff.year + 1)
    else:
        exp = datetime.fromisoformat(expiration_date)

    submission_data = {
        "QuoteId": quote_id,
        "BrokerId": broker,
        "CarrierNo": carrier,
        "Description": description,
        "EffectiveDate": eff.isoformat(),
        "ExpirationDate": exp.isoformat(),
        "EnteredByUser": entered_by,
        "MgaNo": 1,
        "SubmissionId": 0,
        "SubmissionNo": 0,
    }

    client = get_client()
    try:
        result = client.create_submission(submission_data)
        sub = result.get("Submission", {})
        sub_id = sub.get("SubmissionId")
        sub_no = sub.get("SubmissionNo")
        if not compact:
            typer.echo(f"Submission created: ID={sub_id}, No={sub_no}")
        out(result, compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)


@submission_app.command("list")
def submission_list(
    quote_id: int = typer.Option(..., help="Quote ID"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """List submissions for a quote."""
    client = get_client()
    try:
        out(client.get_submissions(quote_id), compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)


# --- Activity ---

@activity_app.command("create")
def activity_create(
    quote_id: int = typer.Option(..., help="Quote ID"),
    submission_id: int = typer.Option(..., help="Submission ID"),
    action_id: int = typer.Option(..., help="Action ID (e.g., 2=Offer received from carrier)"),
    section_id: int = typer.Option(3, help="Section ID (3=Submissions, 5=Quotes)"),
    agent: int = typer.Option(0, help="Agent number"),
    logged_by: str = typer.Option("ccerto", help="Username"),
    notes: str = typer.Option("", help="Activity notes"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """Log an activity on a submission."""
    activity_data = {
        "ActionId": action_id,
        "ActivityId": 0,
        "AgentNo": agent,
        "LoggedByUser": logged_by,
        "LoggedDate": datetime.now().isoformat(),
        "QuoteId": quote_id,
        "SectionId": section_id,
        "SubmissionId": submission_id,
    }
    if notes:
        activity_data["Notes"] = notes

    client = get_client()
    try:
        result = client.create_activity(activity_data)
        act_id = result.get("Activity", {}).get("ActivityId")
        if not compact:
            typer.echo(f"Activity created: {act_id}")
        out(result, compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)


@activity_app.command("list")
def activity_list(
    quote_id: int = typer.Option(0, help="List by quote ID"),
    submission_id: int = typer.Option(0, help="List by submission ID"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """List activities for a quote or submission."""
    client = get_client()
    try:
        if submission_id:
            result = client.call("GetActivitiesBySubmissionId", {"SubmissionId": submission_id})
        elif quote_id:
            result = client.call("GetActivitiesByQuoteId", {"QuoteId": quote_id})
        else:
            typer.echo("Provide --quote-id or --submission-id", err=True)
            raise typer.Exit(1)
        out(result, compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)


@activity_app.command("actions")
def activity_actions(
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """List all available activity action types."""
    client = get_client()
    try:
        result = client.call("GetQuoteActions")
        actions = result.get("Actions", [])
        if not compact:
            for a in sorted(actions, key=lambda x: x.get("ActionId", 0)):
                section = a.get("SectionId", "")
                typer.echo(f"  {a['ActionId']:4d}  s{section}  {a.get('Description', '')}")
        else:
            out(actions, compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)


# --- Agents ---

@agents_app.command("list")
def agents_list(
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """List all agents."""
    client = get_client()
    agents = client.get_agents()
    if not compact:
        typer.echo(f"{len(agents)} agents")
        for a in agents[:20]:
            typer.echo(f"  {a['AgentNumber']:6d}  {a.get('Name1', '')}")
        if len(agents) > 20:
            typer.echo(f"  ... and {len(agents) - 20} more (use --compact for full list)")
    else:
        out(agents, compact)


@agents_app.command("search")
def agents_search(
    name: str = typer.Option(..., help="Search string (matches against agency name)"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """Search agents by name."""
    client = get_client()
    agents = client.get_agents()
    query = name.lower()
    matches = [a for a in agents if query in (a.get("Name1", "") or "").lower()]
    if not compact:
        typer.echo(f"{len(matches)} matches for '{name}'")
        for a in matches:
            typer.echo(f"  {a['AgentNumber']:6d}  {a.get('Name1', '')}  ({a.get('State', '')})")
    else:
        out(matches, compact)


@agents_app.command("get")
def agents_get(
    number: int = typer.Option(..., help="Agent number"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """Get full agent details."""
    client = get_client()
    try:
        result = client.call("GetAgent", {"AgentNumber": number})
        out(result, compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)


# --- LOBs ---

@lobs_app.command("list")
def lobs_list(
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """List all lines of business."""
    client = get_client()
    lobs = client.get_lobs()
    if not compact:
        for l in lobs:
            typer.echo(f"  {l.get('LOB', ''):4s}  {l.get('Description', '')}")
    else:
        out(lobs, compact)


@lobs_app.command("sublobs")
def lobs_sublobs(
    lob: str = typer.Option(..., help="LOB code (e.g., CG)"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """List sub-LOBs for a line of business."""
    client = get_client()
    subs = client.get_sub_lobs(lob)
    if not compact:
        typer.echo(f"{lob} sub-LOBs:")
        for s in subs:
            typer.echo(f"  {s.get('SubLOB', ''):4s}  {s.get('Description', '')}")
    else:
        out(subs, compact)


# --- Carriers ---

@carriers_app.command("list")
def carriers_list(
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """List all carriers."""
    client = get_client()
    carriers = client.get_carriers()
    if not compact:
        for c in carriers:
            typer.echo(f"  {c.get('CarrierNumber', 0):4d}  {c.get('Name', '')}")
    else:
        out(carriers, compact)


# --- Raw call ---

@app.command("call")
def raw_call(
    operation: str = typer.Argument(help="SOAP operation name (e.g., GetCompanyRules)"),
    params: str = typer.Argument("{}", help="JSON parameters"),
    compact: bool = typer.Option(False, "--compact", "-c"),
):
    """Call any Unisoft SOAP operation directly."""
    client = get_client()
    try:
        p = json.loads(params)
    except json.JSONDecodeError as e:
        typer.echo(f"Invalid JSON: {e}", err=True)
        raise typer.Exit(1)
    try:
        result = client.call(operation, p)
        out(result, compact)
    except UnisoftError as e:
        typer.echo(f"Error: {e.data}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
