```mermaid
stateDiagram-v2
[*] --> START
START --> ORCHESTRATING: USER_MESSAGE

ORCHESTRATING --> FLOW_ISSUE_TICKET: intent=issue_ticket && conf>=0.6 / init_flow
ORCHESTRATING --> FLOW_DIRECTIONS: intent=directions && conf>=0.6 / init_flow
ORCHESTRATING --> FLOW_PROCEDURE: intent=procedure && conf>=0.6 / init_flow
ORCHESTRATING --> SMALLTALK: intent=smalltalk && conf>=0.5
ORCHESTRATING --> FLOW_TRIAGE: intent=triage && conf>=0.6 / init_flow

state "FLOW_ISSUE_TICKET" as FLOW_ISSUE_TICKET {
  state "GATHER" as ISSUE_GATHER
  state "CONFIRM" as ISSUE_CONFIRM
  state "DONE" as ISSUE_DONE
  [*] --> ISSUE_GATHER
  ISSUE_GATHER --> ISSUE_GATHER: USER_MESSAGE && !all_required_slots_ready() / ask_next_slot()
  ISSUE_GATHER --> ISSUE_CONFIRM: SLOT_FILLED && all_required_slots_ready() / confirm_slots()
  ISSUE_CONFIRM --> ISSUE_DONE: CONFIRM_YES
}

state "FLOW_DIRECTIONS" as FLOW_DIRECTIONS {
  state "GATHER" as DIR_GATHER
  state "SHOW_ROUTE" as DIR_SHOW_ROUTE
  state "DONE" as DIR_DONE
  [*] --> DIR_GATHER
  DIR_GATHER --> DIR_GATHER: USER_MESSAGE && !all_required_slots_ready() / ask_next_slot()
  DIR_GATHER --> DIR_SHOW_ROUTE: SLOT_FILLED && all_required_slots_ready()
  DIR_SHOW_ROUTE --> DIR_DONE: USER_MESSAGE
}

state "FLOW_PROCEDURE" as FLOW_PROCEDURE {
  state "GATHER" as PROC_GATHER
  state "SHOW_CHECKLIST" as PROC_SHOW_CHECKLIST
  state "DONE" as PROC_DONE
  [*] --> PROC_GATHER
  PROC_GATHER --> PROC_GATHER: USER_MESSAGE && !all_required_slots_ready() / ask_next_slot()
  PROC_GATHER --> PROC_SHOW_CHECKLIST: SLOT_FILLED && all_required_slots_ready()
  PROC_SHOW_CHECKLIST --> PROC_DONE: USER_MESSAGE
}

state "FLOW_TRIAGE" as FLOW_TRIAGE {
  state "GATHER" as TRIAGE_GATHER
  state "SHOW_SUGGESTIONS" as TRIAGE_SHOW_SUGGESTIONS
  state "DONE" as TRIAGE_DONE
  [*] --> TRIAGE_GATHER
  TRIAGE_GATHER --> TRIAGE_GATHER: USER_MESSAGE && !all_required_slots_ready() / ask_next_slot()
  TRIAGE_GATHER --> TRIAGE_SHOW_SUGGESTIONS: SLOT_FILLED && all_required_slots_ready()
  TRIAGE_SHOW_SUGGESTIONS --> TRIAGE_DONE: USER_MESSAGE
}

SMALLTALK --> ORCHESTRATING: USER_MESSAGE

ISSUE_CONFIRM --> ORCHESTRATING: CONFIRM_NO / reset_flow

note right of ORCHESTRATING
  Cancel anywhere: CANCEL_FLOW -> ORCHESTRATING / reset_flow
  Timeout anywhere: TIMEOUT -> END / on_timeout
  Intent switch from FLOW_ISSUE_TICKET to DIRECTIONS:
    USER_MESSAGE with intent=directions && allow_intent_switch
end note

ORCHESTRATING --> ORCHESTRATING: else

ORCHESTRATING --> END: TIMEOUT / on_timeout
FLOW_ISSUE_TICKET --> END: TIMEOUT / on_timeout
FLOW_DIRECTIONS --> END: TIMEOUT / on_timeout
FLOW_PROCEDURE --> END: TIMEOUT / on_timeout
FLOW_TRIAGE --> END: TIMEOUT / on_timeout
END --> [*]
```
