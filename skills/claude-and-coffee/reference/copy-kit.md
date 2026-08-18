# Copy kit

Two texts fill the room: the Luma description and the LinkedIn post. Both below
are the shipped 2026-08-11 versions with the bracketed parts swapped per event.
Write them once, at T-28, and publish them the same day.

## Rules

- **"Claude Community Ambassador for New York City."** The August version shipped
  with "Community Leader" in the host bio. It is wrong. Check it every time.
- No em dashes. Commas, colons, periods.
- Name what someone leaves with, not what the event is called. "You'll leave with
  ideas you can apply the same night" does more work than any adjective.
- **No speaker names before the event.** Program rule. Tease the topic instead.
- Always: free, drop-in window, and the one thing to bring.
- Flip the Luma event from private to public **before** posting anywhere, then
  attach the graphic. A LinkedIn post pointing at a private page wastes the post.

## Luma description

> Welcome to [EVENT] [CITY]: an after-work coworking session for founders,
> operators, marketers, developers, and anyone building with AI.
>
> Drop in any time from [DOORS] to [ENDS]. Grab a coffee, open your laptop, and get
> real work done next to people doing the same. Early in the evening we'll break for
> a short keynote on [TOPIC]: how to think about working with it, and how to use it
> to genuinely improve your workflow, whether you write code, run a company, or run
> campaigns. You'll leave with ideas you can apply the same night, with the whole
> room around you to try them with.
>
> **What to expect**
> - A keynote on Claude and rethinking your workflow with AI
> - Focused coworking with your own projects, alongside people worth interrupting
> - Founders, creators, operators, and builders from across the [CITY] AI scene
> - Live feedback on whatever you're building, from people who ship with Claude daily
> - The kind of connections that turn into collaborators, cofounders, and friends
>
> Working on something with Claude or Claude Code? Bring it. Showing your work to the
> room is encouraged, never required.
>
> **Your host**
> [HOST] is the Claude Community Ambassador for [CITY] and [ONE LINE]. Say hi when
> you arrive, he means it.
>
> **About [EVENT]**
> [EVENT] brings together people building with AI through curated coworking sessions
> and small gatherings designed for real conversation over big crowds. We are part of
> Claude Community [CITY], the official Claude community for [AREA]. Free, as all our
> events are. Find everything we host at [SITE].

## LinkedIn post

> [EVENT] is coming to [CITY] on [DATE]. Coffee, laptops, and a room full of people
> building with AI.
>
> Drop in anywhere from [DOORS] to [ENDS], work on your own projects, and interrupt
> someone worth interrupting. Early in the evening I'll give a short keynote on
> [TOPIC], and how to think about using it to genuinely improve your workflow.
> Whether you write code, run a company, or run campaigns, you'll leave with things
> you can try the same night.
>
> Who it's for: founders, operators, marketers, developers, and anyone curious about
> building with AI. Bring what you're working on. Showing it to the room is
> encouraged, never required.
>
> Free, like everything Claude Community [CITY] hosts.
>
> RSVP: [LUMA URL]
>
> See you there.
>
> #ClaudeCommunity #[CITY] #ClaudeCode #AI #Coworking

## The other three sends

| When | What | Where it comes from |
|---|---|---|
| On approval | One line per guest, why they specifically are in | `event-attendee-research`, the `message` column |
| T-1 | Personalized day-before email with their table number | `event-attendee-research`, `emails.csv` |
| T+7 | Recap post, speakers credited by name at last | Photos, feedback QR results |
