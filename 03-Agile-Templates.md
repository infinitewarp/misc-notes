# Brad's agile ceremony templates

Herein lies a summary of otherwise unwritten templates that live in my brain! I've been performing the role of scrum master or team lead or process guru long enough that these are mostly ingrained into my subconscious, and I basically run on autopilot without actively thinking when I conduct many of our meetings.

This is just a brain-dump of how I think I operate. They're certainly not the only and probably not the best way to manage the conversations, but they work well enough for me!

This may be like learning how a simple sleight-of-hand magic trick works. Once you see it, you cannot un-see it, and you'll realize there's not much "clever" about how I conduct our discussions.

### Common strategies

* Always introduce the meeting with a brief agenda reminder.

  * Why are people here? What are they expected to do? Set their expectations!
  * This is very helpful for new people or visitors who may be unfamiliar with the way we work.
  * It's also helpful for long-standing team members because it's easy to forget why you joined this call if you just active with something else (maybe another call, maybe some intense work thinking).
  * It gives people a moment to breathe and mentally context switch.

* To present a topic for maximum audience retention: explain the topic three times.

  1. "I am telling you what I'm going to tell you."
  2. "I am telling you the thing."
  3. "I am telling you what I just told you."

  I don't know where I learned this "explain it three times" expression, but the idea is that you introduce the topic with a very brief summary so the audience knows what to expect, and you end the topic with a similar summary for anyone who got distracted and tuned out (it happens more often than we like to admit!). Many presenters remember to do the former but forget or don't think about doing the latter.

* Try to reserve a few minutes at the end of the meeting to ask if there are any ideas or concerns that we didn't have time to raise. Encourage people to continue the conversation outside the meeting in Slack.
* If two or more core contributors are absent from a ceremony, ask if the team would like to skip or reschedule. Everyone's feedback is valuable, and we might miss an important idea or question with too many people being absent.

### Standup

* Wait about 1 minute, no more, for people to arrive late. (Standup waits for no one!)
  * It's **not your fault** if tardy/absent team members miss important information.
* Restate the purpose of the meeting.
  * Something like: "It's time for standup. Let's look at our in-progress items."
* For each item from the top, read the title and then wait or prompt the current owner to speak provide updates or blockers.
* Pay attention for distraction and digressions, and politely interrupt to suggest moving the discussion elsewhere to stay on topic.
  * Remember that *the primary purpose of standup is to raise and address blockers*. Brief progress status updates are fine, but we do not want to waste time on mundain progress details that are not relevant or important for other team members.
* After reading all items, ask the team:
  * "Does anyone have any additional comments, questions, blockers, or other general updates?"
  * Opening these questions at the end invites discussion for topics that may not be on the board but are important and timely to share.

### Backlog refinement

* Wait about 1 minute for people to arrive late.
  * It's **not your fault** if tardy/absent team members miss important information.
* Restate the purpose of the meeting.
  * Something like: "It's time for backlog refinement. We want to look at the items in the backlog, make sure they're in priority order, and define issues so that we're ready and confident to start working on them."
* After reading all items, ask the team:
  * "Does anyone have any issues that you think are urgent to discuss that we may have missed?"

### User story

* General template for user stories:

    ```
    As a [persona], I want [behavior] so that [rationale].

    Maybe a more detailed technical explanation of the preceding line.

    Acceptance Criteria

    * Verify that A happens
    * Verify that B is present
    * Verify that C does not happen

    Assumptions and Questions

    * What happens when X?
    * Don't forget Y.
    * See also related thing Z.
    ```

* Make sure the title is succinct and meaningful, that most people will understand the intent at a quick glance.
* Read and discuss each part of the user story.
* Try to look at the issue from every angle. Pretend you are QE and you need to automate tests. Pretend you are a technical writer and you need to write user-facing docs. Pretend you are a UI dev and you need to add fields and buttons.
* When it looks done, ask the team if anyone has any more questions or uncertainty about the definition. Could we start working on the issue *right now*? If not, maybe we're not done defining it.
* Actually pause to give people time to reflect on that question. Maybe re-read the issue one last time before calling it "ready"/"to do" and moving on.

### Retrospectives

* Wait about 1 minute for people to arrive late.
  * It's **not your fault** if tardy/absent team members miss important information.
* Restate the purpose of the meeting.
  * Something like: "Let's take the next X minutes to think of and write down things that went well or poorly since we last met."
* Before reading new notes as a group, jump to last session's notes to confirm or follow up on requested actions.
* Before reading new notes as a group, skim and try to estimate how long we can spend in each section. 45 minutes may not be enough time for everyone to talk.
* Call out individuals to read their notes as we get to them.
  * Letting individuals read their notes helps everyone feel that their feedback is important.
  * It also gives them an opportunity to verbally expand on thoughts they may not have typed.
* Keep an eye on the clock, and cut off distractions or even volunteer to read others' comments for them to keep up the pace.
* As we identify problems or challenges we want to address, jump to the end and add **and assign** followup action items for people to do.
* After reading all items, ask the team:
  * "Does anyone have any other comments or thoughs we may have missed?"

