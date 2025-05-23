# Pre-built Archetypes (Phase 0, Deliverable 2)

## Reiterated Theme/Goal

The purpose of providing pre-built archetypes is to offer users a starting point for common documentation structures, accelerating adoption and promoting best practices. These archetypes leverage the DocModel Engine's schema capabilities to ensure consistency and quality, and can be customized by users for their specific needs.

## Proposed Archetypes & Definitions

We propose three initial archetypes:

1.  **Standard Project README (`archetype_StandardProjectREADME.yaml`)**
2.  **Basic Diátaxis Tutorial (`archetype_BasicDiataxisTutorial.yaml`)**
3.  **API Endpoint Documentation (`archetype_APIEndpointDoc.yaml`)**

---

### 1. Archetype: Standard Project README

*   **Purpose:** To provide a comprehensive, well-structured README for software projects. This archetype aims for a good balance of information for both new users and potential contributors. It can be seen as a more detailed and structured version of the `MyProjectReadmeStub.yaml` or an implementable version of one of the levels in `readme_maturity_levels.md`.
*   **Typical Structure:** Includes sections for project title, badges, overview, installation, usage, contributing guidelines, license, and acknowledgments.

*   **YAML Schema (`archetype_StandardProjectREADME.yaml`):**

```yaml
schema_name: StandardProjectREADME
version: "1.0"
description: "A standard, comprehensive README structure for software projects."

structure:
  ProjectTitle:
    name: ProjectTitle
    description: "The main title of the project, displayed as an H1."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 1
    validations:
      - type: pattern
        value: "\\S+" # Must contain non-whitespace
        message: "Project title cannot be empty."
    elements: {} # H1 text content is implicitly part of the heading

  Badges:
    name: Badges
    description: "A collection of badges (e.g., build status, version)."
    entry_marker_type: Paragraph # Typically a paragraph with multiple image links
    required: false
    elements: {} # Content is a series of images/links, specific validation could be complex

  Overview:
    name: Overview
    description: "A concise summary of the project's purpose and functionality."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^(Overview|Introduction|About)$"
    elements:
      SummaryParagraph:
        name: SummaryParagraph
        markdown_type: Paragraph
        required: true
        validations:
          - type: minLength
            value: 100
            message: "The overview summary should be at least 100 characters."
    ordered: true
    element_order: ["SummaryParagraph"]

  KeyFeatures:
    name: KeyFeatures
    description: "A bulleted list of key features or capabilities."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^(Key Features|Features)$"
    required: false
    elements:
      FeatureList:
        name: FeatureList
        entry_marker_type: List # This defines the list itself
        required: true # If KeyFeatures heading exists, list must be present
        elements: # Defines what each list item should be
          FeatureListItem:
            name: FeatureListItem
            entry_marker_type: ListItem
            required: true # List must not be empty if section is present
            elements:
              ItemContent:
                name: ItemContent
                markdown_type: Paragraph # Each list item is a paragraph
                required: true
                validations:
                  - type: minLength
                    value: 10
        validations: # Validations on the list itself
          - type: minCount # Minimum number of features
            value: 2
    ordered: true
    element_order: ["FeatureList"]


  Installation:
    name: Installation
    description: "Instructions on how to install and set up the project."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^Installation$"
    elements:
      Prerequisites:
        name: Prerequisites
        markdown_type: Paragraph
        required: false
      InstallationSteps:
        name: InstallationSteps
        entry_marker_type: List # A list of steps
        required: true
        elements:
          Step:
            name: Step
            entry_marker_type: ListItem
            elements:
              StepInstruction:
                name: StepInstruction
                markdown_type: Paragraph # Or CodeBlock
                required: true
    ordered: true
    element_order: ["Prerequisites", "InstallationSteps"]

  Usage:
    name: Usage
    description: "Examples and explanations on how to use the project."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^Usage$"
    elements:
      BasicExample:
        name: BasicExample
        markdown_type: CodeBlock # A code block showing basic usage
        required: true
      UsageExplanation:
        name: UsageExplanation
        markdown_type: Paragraph
        required: false
    ordered: true
    element_order: ["BasicExample", "UsageExplanation"]

  Contributing:
    name: Contributing
    description: "Guidelines for contributing to the project."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^(Contributing|How to Contribute)$"
    required: false
    elements:
      ContributionGuidance:
        name: ContributionGuidance
        markdown_type: Paragraph
        required: true
        validations:
          - type: minLength
            value: 50

  License:
    name: License
    description: "Information about the project's license."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^License$"
    elements:
      LicenseInfo:
        name: LicenseInfo
        markdown_type: Paragraph
        required: true
        validations:
          - type: pattern # e.g., "This project is licensed under the MIT License."
            value: "(licensed under|License)"
            message: "License information should mention the license type."

  Acknowledgments:
    name: Acknowledgments
    description: "Recognition for inspirations, libraries, or contributors."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^(Acknowledgments|Credits)$"
    required: false
    elements:
      AcknowledgmentText:
        name: AcknowledgmentText
        markdown_type: Paragraph
        required: true
```

---

### 2. Archetype: Basic Diátaxis Tutorial

*   **Purpose:** To structure a tutorial document following the principles of the Diátaxis framework (specifically, a "Tutorial" type). This archetype helps create hands-on, learning-oriented guides.
*   **Typical Structure:** Introduction (goal of the tutorial), Prerequisites, Step-by-step instructions, Conclusion/Next Steps.

*   **YAML Schema (`archetype_BasicDiataxisTutorial.yaml`):**

```yaml
schema_name: BasicDiataxisTutorial
version: "1.0"
description: "A basic tutorial structure following Diátaxis principles."

structure:
  TutorialTitle:
    name: TutorialTitle
    description: "The main title of the tutorial."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 1
    validations:
      - type: pattern
        value: "\\S+"
    elements: {}

  Goal:
    name: Goal
    description: "What the user will learn or achieve by completing the tutorial."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^(Goal|What You'll Learn|Objective)$"
    elements:
      GoalDescription:
        name: GoalDescription
        markdown_type: Paragraph
        required: true
        validations:
          - type: minLength
            value: 50

  Prerequisites:
    name: Prerequisites
    description: "What the user needs to know or have before starting."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^Prerequisites$"
    required: false
    elements:
      PrerequisiteList:
        name: PrerequisiteList
        entry_marker_type: List
        required: true # If Prerequisites section exists, list must be present
        elements:
          Item:
            name: Item
            entry_marker_type: ListItem
            elements:
              ItemDescription:
                name: ItemDescription
                markdown_type: Paragraph
                required: true
        validations:
          - type: minCount
            value: 1

  Steps: # The core tutorial content, a series of steps
    name: Steps
    description: "The main step-by-step instructions."
    entry_marker_type: Heading # Optional heading for the overall steps section
    entry_marker_properties:
      level: 2
      text_pattern: "^(Steps|Tutorial)$"
    required: true # The steps themselves are required for a tutorial
    elements: # This will contain multiple 'Step' StructureRules
      # The keys "Step1", "Step2" are logical names for schema, not literal heading text.
      # The validator would look for a sequence of these Step structures.
      # To enforce a sequence of generic "Step" elements, a different modeling approach might be needed,
      # e.g., a single "StepList" element of type List, where each ListItem is a structured "Step".
      # For now, let's define one named step to show structure.
      # A more robust way is to have 'elements' define a 'Step' StructureRule and use minCount/maxCount.
      # For simplicity here, we'll assume steps are identified by H3s.
      # This part highlights a modeling challenge for repeating, identifiable structures.
      # A better model:
      # StepSequence:
      #   name: StepSequence
      #   entry_marker_type: List # or a sequence of Heading defined elements
      #   required: true
      #   elements:
      #     ConcreteStep: # This rule applies to each item in the list if it's a List
      #       name: ConcreteStep
      #       entry_marker_type: ListItem # or Heading for H3 style steps
      #       # ... (see below)
      # This example uses H3 for each step directly under the main "Steps" H2.
      # So, the "elements" of "Steps" will be a series of StructureRules, each for an H3.
      # This requires the user to name their step elements in the schema (e.g. Step1_Install, Step2_Configure)
      # For a generic list of steps, the 'entry_marker_type: List' approach for 'Steps' is better.
      # Let's pivot to that for better generalizability:
      StepList: # The parent element is a List containing all steps
        name: StepList
        entry_marker_type: List # The steps are items in a single list
        required: true
        elements:
          StepItem: # Defines the structure of each ListItem within StepList
            name: StepItem
            entry_marker_type: ListItem # Each step is a list item
            required: true # The list should not be empty
            elements:
              StepTitle: # Optional: each list item could start with emphasized text or similar
                name: StepTitle
                markdown_type: Paragraph # Could be Strong within a Paragraph
                required: false
                # Example: **Step 1: Do this**
              StepInstruction:
                name: StepInstruction
                markdown_type: Paragraph
                required: true
              StepCode:
                name: StepCode
                markdown_type: CodeBlock
                required: false
              StepExplanation:
                name: StepExplanation
                markdown_type: Paragraph
                required: false
        validations:
          - type: minCount
            value: 2 # A tutorial should have at least two steps.

  Conclusion:
    name: Conclusion
    description: "Summary of what was learned and next steps."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2
      text_pattern: "^(Conclusion|Summary|Next Steps)$"
    elements:
      SummaryText:
        name: SummaryText
        markdown_type: Paragraph
        required: true
      NextStepsLink:
        name: NextStepsLink
        markdown_type: Paragraph # Could contain a Link FieldDefinition
        required: false

```

---

### 3. Archetype: API Endpoint Documentation

*   **Purpose:** To provide a standardized structure for documenting a single API endpoint, including its request, response, and authentication details.
*   **Typical Structure:** Endpoint URL and Method, Description, Request Parameters, Request Body, Response Codes, Response Body Example, Authentication.

*   **YAML Schema (`archetype_APIEndpointDoc.yaml`):**

```yaml
schema_name: APIEndpointDocumentation
version: "1.0"
description: "Structure for documenting a single API endpoint."

structure:
  EndpointTitle: # e.g., "GET /users/{id}"
    name: EndpointTitle
    description: "The API endpoint URL and HTTP method (e.g., GET /users)."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 2 # Or H3 if part of a larger API docs page
    validations:
      - type: pattern
        # Basic check for HTTP method and path
        value: "^(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\\s+/"
        message: "Endpoint title should start with HTTP method and path (e.g., GET /users)."
    elements: {}

  Description:
    name: Description
    description: "Detailed explanation of the endpoint's purpose and behavior."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 3
      text_pattern: "^Description$"
    elements:
      DescriptionParagraph:
        name: DescriptionParagraph
        markdown_type: Paragraph
        required: true
        validations:
          - type: minLength
            value: 30

  Authentication:
    name: Authentication
    description: "Details on authentication/authorization requirements."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 3
      text_pattern: "^(Authentication|Authorization)$"
    required: false # Some endpoints might be public
    elements:
      AuthDetails:
        name: AuthDetails
        markdown_type: Paragraph # Could be a list if multiple methods
        required: true

  RequestParameters: # URL Query Parameters or Path Parameters
    name: RequestParameters
    description: "Description of URL query or path parameters."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 3
      text_pattern: "^(Request Parameters|Parameters)$"
    required: false # Not all endpoints have parameters
    elements:
      ParameterList: # Typically a table, but Markdown tables are hard to schema-validate deeply.
                     # Using a list of parameter descriptions for now.
        name: ParameterList
        entry_marker_type: List
        required: true
        elements:
          Parameter:
            name: Parameter
            entry_marker_type: ListItem
            elements:
              ParamDetail: # e.g., "`name` (string, required): Description of the parameter."
                name: ParamDetail
                markdown_type: Paragraph
                required: true
                validations:
                  - type: pattern # Check for common param format like `name` (type): description
                    value: "^`\\w+`\\s*\\(\\w+(,\\s*(required|optional))?\\):"
                    message: "Parameter description should be like: `name` (type, required/optional): description"
        validations:
          - type: minCount
            value: 1

  RequestBody:
    name: RequestBody
    description: "Details about the request body (e.g., JSON payload)."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 3
      text_pattern: "^(Request Body|Payload)$"
    required: false # GET requests usually don't have a body
    elements:
      BodyDescription:
        name: BodyDescription
        markdown_type: Paragraph # Description of the body structure
        required: true
      BodyExample:
        name: BodyExample
        markdown_type: CodeBlock # JSON or XML example
        required: true
        # Could add validation for CodeBlock language if parser provides it
    ordered: true
    element_order: ["BodyDescription", "BodyExample"]


  Responses:
    name: Responses
    description: "Details about possible HTTP responses."
    entry_marker_type: Heading
    entry_marker_properties:
      level: 3
      text_pattern: "^(Responses|Response Codes)$"
    elements:
      # Multiple response codes can be documented.
      # This is another case for repeating structures.
      # Using one example, but ideally, this would allow multiple 'ResponseCodeDetail' elements.
      ResponseCodeDetail_200: # Example for a 200 OK
        name: ResponseCodeDetail_200 # User would name this e.g. SuccessResponse, ErrorResponse404
        entry_marker_type: Paragraph # e.g., "**200 OK** - Successful response."
        required: true
        validations:
          - type: pattern
            value: "^(\\*{0,2}\\d{3}\\s\\w+\\*{0,2})" # e.g. "**200 OK**" or "404 Not Found"
            message: "Response detail should start with status code and reason phrase."
        elements: # A 'Paragraph' type doesn't typically have 'elements' in this model,
                  # but if we want to structure content *within* this response para,
                  # it should be a StructureRule with entry_marker_type Paragraph.
                  # For now, assume the paragraph contains description and refers to an example.
          ResponseBodyExample: # Example response body for this status code
            name: ResponseBodyExample
            markdown_type: CodeBlock # JSON/XML example
            required: false # Not all responses have bodies (e.g. 204)
            # This element should logically follow the paragraph describing the response code.
            # This ordering is tricky if ResponseCodeDetail is just a Paragraph.
            # A better model: Response (StructureRule, H4) -> Description (Para), Example (Code)

  # A more robust Responses section:
  # Responses:
  #   name: Responses
  #   entry_marker_type: Heading
  #   elements:
  #     SuccessResponse: # User defines one or more response types
  #       name: SuccessResponse
  #       entry_marker_type: Heading # e.g. H4 "200 OK"
  #       elements:
  #         ResponseDescription: { markdown_type: Paragraph, required: true }
  #         ResponseBodyExample: { markdown_type: CodeBlock, required: false }
  #     ErrorResponse:
  #       name: ErrorResponse
  #       entry_marker_type: Heading # e.g. H4 "404 Not Found"
  #       elements:
  #         ResponseDescription: { markdown_type: Paragraph, required: true }
  #         ResponseBodyExample: { markdown_type: CodeBlock, required: false }

```

---

## Relationship to DocModel Engine

These YAML archetype schemas are designed to be parsed and understood by the **DocModel Engine**.
When one of these archetypes is used:

1.  The **SchemaLoader** component of the DocModel Engine will read the YAML file (e.g., `archetype_StandardProjectREADME.yaml`).
2.  It will parse the YAML and instantiate the corresponding Pydantic models defined in the engine's core: `DocModelSchema`, `StructureRule`, `FieldDefinition`, and `ValidationRule`. For example, each entry under `structure:` in the YAML (like `ProjectTitle` or `Installation`) will become a `StructureRule` instance within the `DocModelSchema.structure` dictionary. Similarly, items under `elements:` will become instances of `FieldDefinition` or nested `StructureRule`s.
3.  The populated `DocModelSchema` Pydantic object then serves as the blueprint for the **ValidatorEngine** to validate a user's Markdown document against that archetype.

The power of the DocModel Engine (type checking, required fields, pattern matching, min/max lengths, ordering) is directly utilized in defining these archetypes.

---

## Application to Dynamic README Scenario

The proposed archetypes, especially the "Standard Project README," have direct relevance to the Dynamic README scenario:

1.  **`StandardProjectREADME.yaml` as a Foundation:**
    *   The `archetype_StandardProjectREADME.yaml` can serve as a more detailed and robust version of the initial `MyProjectReadmeStub.yaml`. Users wanting a comprehensive README from the start could use this archetype.
    *   It provides a concrete implementation of what a "good" or "mature" README (as envisioned by `readme_maturity_levels.md`) might look like. Different levels within `readme_maturity_levels.md` could even correspond to variations or subsets of this standard archetype. For instance, a "Bronze Level README" might only require `ProjectTitle`, `Overview`, and `License` sections from the standard archetype.

2.  **Informing `README.stub` Generation:**
    *   When `markitect` generates a `README.stub` (FR2.2), it could offer a choice of archetypes. Selecting "Standard Project README" would generate a stub that includes all the defined H2 sections as prompts for the user.
    *   Alternatively, `markitect` could use a simpler internal stub but validate against a chosen archetype like `StandardProjectREADME.yaml`.

3.  **`readme_maturity_levels.md` as an Instance of a "Framework Definition Document" Archetype:**
    *   The `readme_maturity_levels.md` document itself, which defines a framework, has a discernible structure (e.g., Introduction, Level Definitions, Criteria per Level).
    *   One could envision a "FrameworkDefinitionDocument" archetype that formalizes the structure of documents that *describe* frameworks or sets of standards.
    *   **Example (Conceptual Snippet for a `FrameworkDefinitionDocument` archetype):**
        ```yaml
        schema_name: FrameworkDefinitionDocument
        version: "1.0"
        structure:
          FrameworkTitle:
            entry_marker_type: Heading
            entry_marker_properties: { level: 1 }
            # ...
          Introduction:
            entry_marker_type: Heading
            entry_marker_properties: { level: 2 }
            elements:
              Purpose: { markdown_type: Paragraph, required: true }
          LevelDefinitions: # A section describing multiple levels
            entry_marker_type: Heading
            entry_marker_properties: { level: 2, text_pattern: "Levels" }
            elements: # Contains multiple 'Level' structure rules
              Level: # This would be a repeatable StructureRule definition
                name: Level # Generic name, user would create e.g. BronzeLevel, SilverLevel
                entry_marker_type: Heading # e.g., H3 for each level
                elements:
                  Description: { markdown_type: Paragraph, required: true }
                  CriteriaList:
                    entry_marker_type: List
                    required: true
                    elements:
                      Criterion: { entry_marker_type: ListItem, required: true }
        ```
    *   Validating `readme_maturity_levels.md` against such an archetype could ensure that all defined maturity levels consistently include essential information (e.g., description, criteria).

---

## Storage/Packaging

These pre-built archetype YAML files (e.g., `archetype_StandardProjectREADME.yaml`, `archetype_BasicDiataxisTutorial.yaml`, `archetype_APIEndpointDoc.yaml`) should be packaged with the Markitect tool itself.

A suitable location within the project structure would be:

```
markitect/
├── src/
│   └── markitect/
│       └── archetypes/ # New directory
│           ├── archetype_StandardProjectREADME.yaml
│           ├── archetype_BasicDiataxisTutorial.yaml
│           ├── archetype_APIEndpointDoc.yaml
│           └── __init__.py
│       └── docmodel_engine/
│           └── ...
│       └── ...
└── ...
```

This makes them easily discoverable and loadable by the Markitect CLI and core engine. The `__init__.py` in the `archetypes` directory would allow them to be treated as package resources. Users could then specify an archetype by a short name (e.g., `standard_readme`) which the tool would resolve to the appropriate packaged YAML file.
