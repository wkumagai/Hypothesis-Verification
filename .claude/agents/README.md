# Claude Code Subagents for Hypothesis Verification

This directory contains specialized subagents for the Hypothesis Verification System. These subagents are designed to work with Claude Code to provide expert assistance in specific domains.

## Available Subagents

### 🔍 data-validator
**Purpose**: Validates data quality before analysis
**Key Skills**: 
- Missing data detection
- Consistency checking
- Statistical validity assessment
- Quality scoring

**When to use**: Before running any analysis to ensure data quality

### 📊 market-context
**Purpose**: Research market conditions and confounding events
**Key Skills**:
- Event timeline construction
- Earnings/news impact assessment
- Sector trend analysis
- Confounding factor identification

**When to use**: When analyzing stock price movements to separate correlation from causation

### 📈 statistical-analyzer
**Purpose**: Perform rigorous statistical validation
**Key Skills**:
- Hypothesis testing
- Correlation analysis
- Regression modeling
- Multiple comparison correction

**When to use**: To ensure findings are statistically significant

### 📄 report-generator
**Purpose**: Create professional, standardized reports
**Key Skills**:
- Multi-format output (MD, PDF, HTML)
- Visualization standards
- Executive summaries
- Academic writing

**When to use**: When presenting results to stakeholders

### 🔧 spec-researcher
**Purpose**: Keep technical stack up-to-date
**Key Skills**:
- API version monitoring
- Security vulnerability tracking
- Best practices research
- Dependency management

**When to use**: Quarterly reviews or when encountering compatibility issues

## How to Use Subagents

### In Claude Code

1. **Direct invocation**:
   ```
   /use data-validator
   ```

2. **With specific task**:
   ```
   /use statistical-analyzer to validate the correlation findings
   ```

3. **Multiple subagents**:
   ```
   /use data-validator, market-context for comprehensive pre-analysis
   ```

### Subagent Capabilities

Each subagent has access to specific tools:
- **data-validator**: Read, Write, Bash, TodoWrite, Grep, Glob
- **market-context**: WebSearch, WebFetch, Read, Write, Bash
- **statistical-analyzer**: Read, Write, Bash, TodoWrite
- **report-generator**: Read, Write, Bash, TodoWrite
- **spec-researcher**: WebSearch, WebFetch, Read, Write, Bash

## Example Workflows

### Pre-Analysis Validation
```
1. /use data-validator to check data quality
2. /use market-context to research the analysis period
3. Proceed with main analysis if validation passes
```

### Post-Analysis Validation
```
1. Complete initial analysis
2. /use statistical-analyzer to validate findings
3. /use report-generator to create publication
```

### Maintenance Workflow
```
1. /use spec-researcher for quarterly review
2. Update dependencies based on recommendations
3. Run tests to verify compatibility
```

## Subagent Philosophy

These subagents follow the principle of **specialized expertise**:
- Each focuses on a specific domain
- They provide deep, expert-level assistance
- They follow best practices in their field
- They produce standardized, high-quality outputs

## Creating Custom Subagents

To create a new subagent:

1. Create a markdown file with YAML frontmatter:
   ```markdown
   ---
   name: your-subagent-name
   description: When to use this subagent
   tools: tool1, tool2, tool3
   ---
   
   System prompt defining the subagent's expertise...
   ```

2. Place in `.claude/agents/` (project-level) or `~/.claude/agents/` (user-level)

3. The subagent will be automatically available in Claude Code

## Integration with Hypothesis Verification

These subagents are specifically designed for the hypothesis verification workflow:

1. **Data Collection** → data-validator ensures quality
2. **Context Research** → market-context identifies confounds  
3. **Analysis** → statistical-analyzer validates findings
4. **Reporting** → report-generator creates outputs
5. **Maintenance** → spec-researcher keeps system current

Together, they provide comprehensive support for rigorous, reproducible research.