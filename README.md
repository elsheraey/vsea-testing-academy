# VSeA Testing Academy

A collection of exercises and solutions from the **VSeA Testing Academy**, the in-house automotive embedded-software training program of **Valeo Siemens eAutomotive** (a 2016–2022 joint venture between Valeo and Siemens, focused on electric powertrain: inverters, electric motors, on-board chargers). The exercises cover the full skill set of an automotive test engineer: CAN bus simulation in Vector CANoe, CAPL scripting, vTESTstudio test suites, bare-metal AVR firmware, and Python tooling for working with vehicle communication files.

This README is written for readers without an embedded / automotive background. The "What this is, for non-embedded people" section below explains the toolchain in plain terms.

---

## Structure

| Folder                                         | What it is                                                                                                                                                                                                                                       |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [01-signal-range-test/](01-signal-range-test/) | First CAPL exercise: write tests for a "system under test" that range-checks a signal and detects message timeout                                                                                                                                |
| [02-inverter-test/](02-inverter-test/)         | Main exercise: write tests for an encrypted electric-motor inverter (black-box test of a state machine)                                                                                                                                          |
| [03-gateway-dashboard/](03-gateway-dashboard/) | Gateway exercise: a CAPL gateway node that routes signals between buses, controlled via an interactive dashboard panel                                                                                                                           |
| [04-python-xml-gen/](04-python-xml-gen/)       | Python intro: use openpyxl + ElementTree to mass-generate CAN communication XML configs from an Excel spreadsheet                                                                                                                                |
| [05-avr-firmware/](05-avr-firmware/)           | Bare-metal C firmware on an AVR microcontroller (Atmel Studio project) using an AUTOSAR-style APP/HAL/MCAL layered architecture                                                                                                                  |
| [docs/](docs/)                                 | Training program materials: [academy schedule](docs/01-academy-schedule.pdf), [embedded-concepts slides](docs/02-embedded-concepts.pptx), [test-case template](docs/03-test-cases-template.xlsx), [interview prep](docs/04-valeo-interview.docx) |

Exercises that have both a starter pack and a worked solution use a `starter/` + `solution/` pair.

---

## What this is, for non-embedded people

Modern cars contain ~50–150 small computers called **ECUs** (Electronic Control Units): one for the engine, one for the brakes, one for the inverter that drives the electric motor, one for the dashboard, and so on. They talk to each other over a shared wire pair called the **CAN bus** by sending tiny messages (a few bytes) many times per second.

You can't easily test an ECU "in the wild". You'd need a whole car, and crashing into a wall to find a bug is expensive. So engineers do this instead:

1. Plug the real ECU (or a software copy of it) into a PC.
2. Use a simulator to pretend to be _every other ECU in the car_, feeding messages to the unit under test.
3. Run automated test scripts that send specific signals, then check that the ECU responds correctly.

That simulator is **Vector CANoe**. The test scripts are written in a C-like language called **CAPL**. The structured test suites are authored in **vTESTstudio**, which produces HTML reports. This whole stack is so dominant in the auto industry that knowing it is a hiring requirement at most OEMs and Tier-1 suppliers (Bosch, Continental, ZF, Valeo, etc.).

The exercises in this repo are the workflow in miniature.

---

## The toolchain (file-by-file)

| Extension               | What it is                                                                                                                                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.dbc`                  | **CAN database.** Plain-text spec of every message on the bus: ID, length, which signals (named fields) live at which bit positions, who sends it, who receives it. The "schema for the wire format." |
| `.can`                  | **CAPL source code.** C-like scripting language used to simulate ECUs and write tests. Reacts to events: "on message X arriving", "on timer expiring", "on test start".                               |
| `.canencr`              | **Encrypted CAPL.** Same as `.can` but the source is hidden; you test it as a black box.                                                                                                              |
| `.cbf`                  | **Compiled CAPL binary.** Built from `.can` / `.canencr`.                                                                                                                                             |
| `.cfg`                  | **CANoe configuration.** The "project file" that wires together the bus, the nodes, the CAPL programs, the database.                                                                                  |
| `.stcfg`                | **vTESTstudio configuration.**                                                                                                                                                                        |
| `.xvp`                  | **CANoe Panel.** A drag-and-drop GUI panel (buttons, gauges, text boxes) that displays or injects signals while a simulation runs.                                                                    |
| `.vtestreport`          | Binary vTESTstudio report (open in vTESTstudio).                                                                                                                                                      |
| `_report.html` / `.xml` | Test reports generated after running a test suite, viewable in any browser.                                                                                                                           |
| `.atsln` / `.cproj`     | Atmel Studio (now Microchip Studio) solution / project files for AVR firmware.                                                                                                                        |

---

## 01: Signal range test

A 3-node CAN setup:

```
┌──────┐     ┌──────┐     ┌──────┐
│ CCU  │ ──> │ GTW  │ ──> │ SUT  │
└──────┘     └──────┘     └──────┘
```

- **CCU** (Central Control Unit): sends `Signal_8`, an int8 sensor reading, every 10 ms.
- **GTW** (Gateway): relays messages.
- **SUT** (System Under Test): receives `Signal_8` and publishes a "system" copy `@SYS_Signal_8` plus a validity flag `@SYS_Signal_8_VALID`.

### The SUT's contract (already implemented in [starter/SUT.can](01-signal-range-test/starter/SUT.can))

1. **Range check.** If `Signal_8 ∈ [-50, 50]`, publish it and set `VALID=1`.
2. **Out-of-range.** If outside, publish `0` and set `VALID=0`.
3. **Timeout.** If no `CCU_125` message arrives for ~200 ms, publish `0` and set `VALID=0`.

The trainee's job is to write the tests, not the SUT. The starter folder gives you the empty test file plus the SUT already wired up.

### Solution

[solution/Test_1.can](01-signal-range-test/solution/Test_1.can) covers:

| Test case          | Inputs                                         | Expectation                            |
| ------------------ | ---------------------------------------------- | -------------------------------------- |
| `TestCase1(input)` | `-50, -49, -1, 0, 1, 49, 50` (boundary values) | `@SYS_Signal_8 == input`, `VALID == 1` |
| `TestCase2(input)` | `51, -51` (just out of range)                  | `@SYS_Signal_8 == 0`, `VALID == 0`     |
| `TestCase3()`      | Disable the message entirely, wait 200 ms      | `@SYS_Signal_8 == 0`, `VALID == 0`     |

Classic black-box testing: equivalence partitioning (in-range vs. out-of-range), boundary-value analysis (at and just past the limits), plus a temporal test for the timeout.

[solution/Test_1_report.html](01-signal-range-test/solution/Test_1_report.html): **all 31 test steps pass**.

---

## 02: Inverter test

A simulated **electric-vehicle drivetrain** on a CAN bus, with a more elaborate state machine:

```
       CAN bus
┌──────┐       ┌──────┐
│ GTW  │ <───> │ INV  │
└──────┘       └──────┘
 Gateway       Inverter (SUT)
 (you / the    (encrypted,
  test bench)  test as black box)
```

- **`INV` (Inverter):** the **SUT**. CAPL source is encrypted ([starter/INV.canencr](02-inverter-test/starter/INV.canencr)) so you observe it only via CAN traffic.
- **`GTW` (Gateway):** represents the rest of the vehicle; sends commands.
- **`NM_eMOT`:** a Network Management message that wakes the inverter up.

### Signals (from [VseaExersise.dbc](02-inverter-test/starter/VseaExersise.dbc))

GTW → INV commands: `Ign_Stat`, `eMOT_Rq` (Standby / In Active), `Md_Rq` (Torque / Speed), `Ctrl_Trq_Rq`, `Curr_Sens_Cnt` (2 or 3 sensors), `eMOT_Type` (IM / PMSM), `MOT_Spd_Mech` (Resolver / Encoder / PLL).

INV → GTW status: `eMOT_Stat` (Init / Passive / Standby / Trq / Spd / Fault), `eMOT_flt_stat`, `Config_error`, `Pos_error`, `Three_Phase_Error`, `Trq_cons_err`, `Ctrl_Trq_est`, `eMOT_Ctrl_Phase_Curr`, `eMOT_Ctrl_Rotor`.

### Solution

[solution/Test.can](02-inverter-test/solution/Test.can) covers two state-machine scenarios:

- **TestCase02**: Power Off → Inactive → Power Off
- **TestCase03**: Power Off → Inactive → Fault → Inactive → Power Off, including negative testing for motor requests

Each scenario sets configuration signals (sensor count, motor type, speed mechanism), waits for state transitions, and asserts on `eMOT_Stat`. Historical test runs are preserved in [solution/runs-history/](02-inverter-test/solution/runs-history/).

You can't open the inverter; you infer its state machine from the DBC and observed behavior, then design tests that pin it down. That's the whole skill.

---

## 03: Gateway dashboard

A CAPL **gateway node** ([GTW.can](03-gateway-dashboard/GTW.can)) that:

- Reads `Signal_5`, `Signal_6`, `Signal_7` from system variables (driven by the interactive panel)
- Packs them into `GTW_124` and transmits cyclically
- Has a `Switch_GTW` system variable that enables / disables transmission

The dashboard [Dashboard.xvp](03-gateway-dashboard/Dashboard.xvp) is a CANoe Panel: interactive buttons and inputs that drive the simulation in real time. Useful for demonstrating runtime behavior to non-test-engineers.

This exercise teaches: gateways, system-variable-driven simulation, and panel-based interactive testing.

---

## 04: Python XML generation

[Mourad.py](04-python-xml-gen/Mourad.py) is a code-gen utility: it reads replacement key-value pairs from an Excel spreadsheet ([Generationfile.xlsx](04-python-xml-gen/Generationfile.xlsx)) and applies them recursively to a CAN-communication XML config ([input/CanComm*RX*\*.xml](04-python-xml-gen/input/)), producing multiple parameterised output variants in [outputs/](04-python-xml-gen/outputs/).

Real-world use: you have a base CAN-bus configuration and need to generate dozens of variants (one per ECU, one per car model, etc.) without hand-editing XML each time. Same idea as templating tools (Jinja, Handlebars) but driven by Excel because the engineering team works in Excel.

The script also includes warm-up exercises (string length, list sum, character count) from the Python intro section of the academy.

---

## 05: AVR firmware

The other side of automotive software: writing the firmware that runs **inside** an ECU. This is a bare-metal C project for an AVR microcontroller (Atmel Studio / Microchip Studio).

Architecture follows AUTOSAR-inspired layering:

- **MCAL** ([C_Example/MCAL/](05-avr-firmware/C_Example/MCAL/)): Microcontroller Abstraction Layer. Direct register access for `Dio` (digital I/O) and `Timer0`.
- **HAL** ([C_Example/HAL/](05-avr-firmware/C_Example/HAL/)): Hardware Abstraction Layer. Drivers for `Led`, `Switch`, `Seg7` (7-segment display), `LCD`, `PWD` (PWM).
- **APP** ([C_Example/APP/](05-avr-firmware/C_Example/APP/)): Application logic. `Motor`, `POS` (position tracking), `MOD` (mode), `WinBtn` (window button) — strongly suggests this is the classic **automotive power-window** exercise (one-touch up / down with position tracking).
- **Scheduler** ([main.c](05-avr-firmware/C_Example/main.c)): cooperative task scheduler driven by a 500 µs timer ISR. Dispatches `Task_1ms`, `Task_2ms`, …, `Task_2000ms` based on counter math.

This is the "trainee version" — task bodies are stubs to be filled in. Build output (the `Debug/` folder) is gitignored.

---

## How to run

You need **Vector CANoe** + **vTESTstudio** for exercises 01–03 (commercial, Windows-only; demo licence is fine for these projects). For 04 you need Python 3 with `openpyxl`. For 05 you need **Atmel Studio** (now Microchip Studio) and an AVR target. Without the tools, the source files are still readable and reviewable.

---

## Why this matters outside automotive

Strip the automotive jargon and what's left is:

- A network protocol with a schema (the DBC): same idea as Protobuf or OpenAPI.
- A black-box service with a hidden state machine (the encrypted inverter): same as testing a closed-source binary.
- Event-driven scripting (CAPL's `on message`, `on timer`): same model as Node.js handlers or AWS Lambda.
- Boundary / equivalence / timeout testing: vocabulary that applies to any backend service.
- Code generation from spreadsheets: same idea as schema-driven codegen.
- Layered firmware architecture: same separation of concerns as any well-structured backend service.

The novelty is just that the wire is a 500 kbit/s CAN bus instead of HTTPS, and the consumer is a motor controller instead of a microservice.
