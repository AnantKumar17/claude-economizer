The user wants to change the Prompt Economizer operating mode.
Valid modes: auto, manual, off.
Read ~/.claude/prompt-economizer/config.json (create if missing).
Set the "mode" key to the mode specified by the user.
If no mode specified, ask the user: "Which mode? auto (always runs), manual (#opt tag required), or off (disabled)?"
Write the config and confirm the change.
