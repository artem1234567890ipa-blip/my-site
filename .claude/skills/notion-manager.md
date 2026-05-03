---
name: notion-manager
description: When user wants to save notes, create pages, search content, or manage anything in Notion. Triggers on: "save to Notion", "create Notion page", "find in Notion", "add to Notion", "update Notion", "запиши в Notion", "создай страницу в Notion", "найди в Notion".
---

Use the Notion MCP to manage pages and content in Notion.

## Available Operations

### Create a page
Create a new page in the user's Notion workspace. Ask for:
- Title of the page
- Parent page/database (if not specified, use the default workspace)
- Content to add

### Search content
Search across all Notion pages and databases for relevant content.

### Save notes
Quickly save a note or text snippet to Notion. Create a new page with:
- Title: current date + short description
- Content: the provided text

### Update a page
Find and update existing Notion content.

## Rules
- Always confirm with the user before creating or modifying pages
- For search results, show page title + brief excerpt + link
- If Notion MCP is not authenticated, tell the user to connect it at claude.ai settings
- Keep page titles concise and descriptive
- When saving research results, format them with headers and bullet points for readability
