# Multi-Agent Financial Analysis System

AAI-520 Final Team Project — Team 9

Team members: Russell Miller and Rogelio Aguilar

## Project Overview

We are developing an agentic financial research system that accepts a
stock symbol, gathers financial and news information, and produces a
source-supported research summary.

The system is being developed to combine research planning, dynamic
tool use, specialist routing, a news-processing prompt chain,
self-reflection, cross-run memory, and evaluator–optimizer refinement.

## Planned Agent Functions

- Plan research steps for a given stock symbol.
- Select and use financial and news tools dynamically.
- Assess the quality and evidence support of generated analysis.
- Save and use lessons across runs to improve later analyses.

## Planned Workflow Patterns

### News Prompt Chain

Ingest news → preprocess → classify → extract → summarize.

The completed chain will prepare news articles, classify their topics
and reported business impact, extract relevant facts, and produce
summaries grounded in the supplied information.

### Specialist Routing

Direct tasks or content to the appropriate financial, news, or market
analysis component.

### Evaluator–Optimizer

Generate an analysis draft, evaluate its quality, and revise it using
the evaluator’s feedback.

## Assigned Team Contributions

### Rogelio Aguilar

- Financial and news data integrations.
- Dynamic tool selection and use.
- Routing to specialist functions or agents.
- Memory saved in one run and used in a later run.
- Shared platform setup and integration support.

### Russell Miller

- Research planning.
- News ingestion and preprocessing.
- News classification, extraction, and summarization.
- Self-reflection and evaluator–optimizer refinement.
- Final notebook assembly, documentation, requirements review, and export.

### Shared Work

- Coordinate component inputs and outputs.
- Review each other’s work.
- Integrate the components and test the complete research workflow.

These responsibilities describe the team’s division of work, not the
completion status of each component.

## Verified News-Component Progress

The current work-in-progress notebook,
`notebooks/aai_520_Final_Project_WIP.ipynb`, includes:

- Required-column validation and basic news-data cleanup.
- Ticker and text-field cleanup.
- Publication-date conversion to UTC.
- Removal of missing required values and duplicate incoming URLs.
- DuckDB article metadata storage and retrieval.
- Prevention of duplicate article insertion.
- Ingestion counts for received, valid, and inserted rows.
- Passing tests for insertion, duplicate prevention, and retrieval
  after reopening the database.
- Two fictional development articles.
- A classification prompt template with passing checks for inclusion
  of the headline and article text.
- Setup instructions and integration notes.

The classification template is not yet connected to an LLM.
Extraction, summarization, research planning, self-reflection, and
evaluator–optimizer refinement remain to be implemented in this notebook.

This progress summary describes the reviewed news component, not the
completion status of every team component.

## Current Limitations

- Classification currently constructs a prompt; it does not execute
  an LLM or validate a model response.
- The database stores article metadata, not full article text.
- Article storage does not implement the agent’s learning memory.
- Fictional examples are development data, not real market news.
- Current tests verify individual components, not the complete system.

## Final Deliverable

The completed system will be documented in an executed code notebook
demonstrating all four agent functions and all three workflow patterns.

The final notebook will explain:

- Agent design and workflows.
- Agent functions and capabilities.
- Evaluation and iteration.

GitHub will be used for version control and collaboration, and Python
code will follow PEP 8.