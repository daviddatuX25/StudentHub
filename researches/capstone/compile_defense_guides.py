import os
import re
import html
import json
from pathlib import Path

# Paths
BASE_DIR = Path(r"d:\Projects\StudentHub\researches\capstone")
OUTPUT_DIR = BASE_DIR / "Group 13 Capstone Titles" / "capstone-titles"

# Capstone Metadata
METADATA = {
    1: {
        "name": "StudentHub",
        "tagline": "Campus Edge & Micro-Economy Hub",
        "desc": "PisoWiFi + Dokploy platform for campus services and local transactions.",
        "icon": "🏫",
        "accent": "167, 139, 250", # #a78bfa
        "glow": "rgba(139, 92, 246, 0.15)"
    },
    2: {
        "name": "SynapseRT",
        "tagline": "Multi-Agent Cognitive Orchestration System",
        "desc": "Coordinating specialized AI agents for complex task execution.",
        "icon": "🧠",
        "accent": "34, 211, 238", # #22d3ee
        "glow": "rgba(0, 229, 255, 0.15)"
    },
    3: {
        "name": "FlexiQueue",
        "tagline": "Institutional Service Queue Orchestrator",
        "desc": "Smart queue management for campus and government services.",
        "icon": "🏗️",
        "accent": "52, 211, 153", # #34d399
        "glow": "rgba(16, 185, 129, 0.15)"
    },
    4: {
        "name": "SecureCAT",
        "tagline": "Role-Based College Admission Testing System",
        "desc": "Secure, proctored computerized admission exams.",
        "icon": "🛡️",
        "accent": "251, 191, 36", # #fbbf24
        "glow": "rgba(251, 191, 36, 0.15)"
    },
    5: {
        "name": "CollabAcad",
        "tagline": "Institutional Forum & Real-Time Event Management",
        "desc": "Academic community interaction, collaborative spaces, and live updates.",
        "icon": "🎓",
        "accent": "129, 140, 248", # #818cf8
        "glow": "rgba(99, 102, 241, 0.15)"
    },
    6: {
        "name": "FlowPH",
        "tagline": "Government Funds Tracker & Citizen Watchdog Network",
        "desc": "Dimension-agnostic funds allocation tracking and crowdsourced auditing.",
        "icon": "🕵️‍♂️",
        "accent": "110, 231, 183", # #6ee7b7
        "glow": "rgba(20, 184, 166, 0.15)"
    }
}

def parse_inline(text):
    # Extract math blocks to protect them from markdown formatting
    math_blocks = []
    
    def replace_math(match):
        placeholder = f"__MATH_BLOCK_{len(math_blocks)}__"
        # Escape for HTML safety but preserve math formatting
        math_blocks.append(html.escape(match.group(0)))
        return placeholder
        
    # Replace display math $$...$$ first, then inline math $...$
    text = re.sub(r'\$\$([\s\S]+?)\$\$', replace_math, text)
    text = re.sub(r'\$(?!\s)([^\$]+?)(?<!\s)\$', replace_math, text)

    text = html.escape(text)
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italics
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
    # Code inline
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', text)
    
    # Restore standard entities
    text = text.replace('&amp;mdash;', '&mdash;').replace('&amp;ndash;', '&ndash;')
    text = text.replace('&amp;quot;', '&quot;').replace('&amp;amp;', '&amp;')
    text = text.replace('&amp;lt;', '&lt;').replace('&amp;gt;', '&gt;')
    
    # Restore math blocks
    for i, block in enumerate(math_blocks):
        placeholder = f"__MATH_BLOCK_{i}__"
        text = text.replace(placeholder, block)
        
    return text

def render_table(rows):
    if len(rows) < 2:
        return ""
    
    html_table = ["<div class='table-container'><table class='searchable'>"]
    
    # Header row
    header_cells = [cell.strip() for cell in rows[0].split('|')[1:-1]]
    html_table.append("<thead><tr>")
    for cell in header_cells:
        html_table.append(f"<th>{parse_inline(cell)}</th>")
    html_table.append("</tr></thead>")
    
    # Body rows
    start_body = 1
    if len(rows) > 1 and re.match(r'^[\s\:\-\|]+$', rows[1]):
        start_body = 2
        
    html_table.append("<tbody>")
    for row in rows[start_body:]:
        cells = [cell.strip() for cell in row.split('|')[1:-1]]
        html_table.append("<tr>")
        for cell in cells:
            html_table.append(f"<td>{parse_inline(cell)}</td>")
        html_table.append("</tr>")
    html_table.append("</tbody></table></div>")
    
    return '\n'.join(html_table)

def parse_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.split('\n')
    sections = []
    current_section = {"title": "Introduction", "id": "intro", "blocks": []}
    
    in_code_block = False
    code_block_lang = ''
    code_content = []
    in_list = False
    list_type = None
    in_quote = False
    quote_content = []
    in_table = False
    table_rows = []
    
    # Helper to flush current block accumulators
    def flush_list():
        nonlocal in_list, list_type
        if in_list:
            current_section["blocks"].append(f"</{list_type}>")
            in_list = False
            list_type = None
            
    def flush_quote():
        nonlocal in_quote, quote_content
        if in_quote:
            quote_text = '\n'.join(quote_content)
            # Parse quote content recursively
            quote_html = markdown_to_html_snippet(quote_text)
            current_section["blocks"].append(f"<blockquote>{quote_html}</blockquote>")
            in_quote = False
            quote_content = []
            
    def flush_table():
        nonlocal in_table, table_rows
        if in_table:
            if table_rows:
                current_section["blocks"].append(render_table(table_rows))
            in_table = False
            table_rows = []

    def flush_all():
        flush_list()
        flush_quote()
        flush_table()

    # Pre-scan lines to extract Q&As
    qa_list = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if line is a Q&A question header
        # Matches: #### Q1: or #### **Q1. or #### Q1. or #### **Q1: or #### **Q** or similar
        question_match = re.match(r'^#{4,5}\s+\*?\*?(Q\d+[\.\:\s][^\*]+|\*\*Q\*\*[\.\:\s][^\*]+|\*\*Question\*\*.*)\*?\*?$', line.strip())
        if question_match:
            question_text = re.sub(r'^\*?\*?Q\d+[\.\:\s]\s*', '', question_match.group(1)).strip()
            # Clean up quotes around question
            question_text = re.sub(r'^["\'](.*)["\']$', r'\1', question_text)
            # Strip markdown bold formatting if any
            question_text = question_text.replace('**', '')
            
            # Now extract the answer block (collect all lines until next heading or question or horizontal rule)
            answer_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if (next_line.strip().startswith('#### Q') or 
                    next_line.strip().startswith('#### **Q') or 
                    next_line.strip().startswith('##') or 
                    re.match(r'^(\-{3,}|\*{3,}|\_{3,})$', next_line.strip())):
                    i -= 1 # Step back so outer loop processes it
                    break
                answer_lines.append(next_line)
                i += 1
                
            answer_text = '\n'.join(answer_lines).strip()
            
            # Clean up the Answer prefix: e.g. * **Answer**: or * **Answer:**
            answer_text = re.sub(r'^[\*\-\+]\s+\*?\*?Answer\*?\*?[\:\s]*', '', answer_text)
            # Also clean up quotes if the entire answer is quoted
            answer_text = re.sub(r'^["\'](.*)["\']$', r'\1', answer_text)
            
            # Parse answer markdown to HTML
            answer_html = markdown_to_html_snippet(answer_text)
            
            # Determine category based on recent level 3 header
            recent_category = "General"
            if current_section["id"].startswith("cat-"):
                recent_category = current_section["title"]
            else:
                for prev_idx in range(len(sections) - 1, -1, -1):
                    if sections[prev_idx]["id"].startswith("cat-"):
                        recent_category = sections[prev_idx]["title"]
                        break
            
            qa_list.append({
                "id": f"qa-{len(qa_list)+1}",
                "category": recent_category,
                "section_id": current_section["id"],
                "question": question_text,
                "answer": answer_html
            })
            i += 1
            continue
            
        # Regular sections
        header_match = re.match(r'^(#{1,3})\s+(.*)$', line.strip())
        if header_match:
            flush_all()
            level = len(header_match.group(1))
            title_text = header_match.group(2).replace('**', '').replace('__', '').strip()
            
            # Create a slug ID
            slug_id = re.sub(r'[^a-z0-9_-]', '', title_text.lower().replace(' ', '-').replace('&', 'and'))
            if level == 3:
                slug_id = f"cat-{slug_id}"
                
            # If section already exists or has blocks, save it and create new
            if current_section["blocks"] or current_section["title"] != "Introduction":
                sections.append(current_section)
                
            current_section = {"title": title_text, "id": slug_id, "blocks": []}
            i += 1
            continue
            
        # Code Block
        if line.strip().startswith('```'):
            flush_list()
            flush_quote()
            flush_table()
            if in_code_block:
                code_text = html.escape('\n'.join(code_content))
                current_section["blocks"].append(f'<pre class="searchable"><code class="language-{code_block_lang}">{code_text}</code></pre>')
                in_code_block = False
                code_content = []
            else:
                in_code_block = True
                code_block_lang = line.strip()[3:].strip()
            i += 1
            continue
            
        if in_code_block:
            code_content.append(line)
            i += 1
            continue
            
        # Table Row
        if line.strip().startswith('|') and line.strip().endswith('|'):
            flush_list()
            flush_quote()
            in_table = True
            table_rows.append(line.strip())
            i += 1
            continue
        elif in_table:
            flush_table()
            
        # Blockquote
        if line.strip().startswith('>'):
            flush_list()
            flush_table()
            in_quote = True
            content = line.strip()
            if len(content) > 1 and content[1] == ' ':
                content = content[2:]
            else:
                content = content[1:]
            quote_content.append(content)
            i += 1
            continue
        elif in_quote:
            flush_quote()
            
        # List items
        ul_match = re.match(r'^[\*\-\+]\s+(.*)$', line.strip())
        ol_match = re.match(r'^([0-9]+)\.\s+(.*)$', line.strip())
        if ul_match:
            item_text = ul_match.group(1)
            if not in_list or list_type != 'ul':
                flush_list()
                current_section["blocks"].append("<ul class='searchable'>")
                in_list = True
                list_type = 'ul'
            current_section["blocks"].append(f"<li>{parse_inline(item_text)}</li>")
            i += 1
            continue
        elif ol_match:
            item_text = ol_match.group(2)
            if not in_list or list_type != 'ol':
                flush_list()
                current_section["blocks"].append("<ol class='searchable'>")
                in_list = True
                list_type = 'ol'
            current_section["blocks"].append(f"<li>{parse_inline(item_text)}</li>")
            i += 1
            continue
        else:
            if line.strip() == '':
                flush_list()
                
        # Horizontal Rule
        if re.match(r'^(\-{3,}|\*{3,}|\_{3,})$', line.strip()):
            flush_all()
            current_section["blocks"].append("<hr>")
            i += 1
            continue
            
        # Empty Line
        if line.strip() == '':
            i += 1
            continue
            
        # Standard line (paragraph or multi-line continuation)
        flush_list()
        flush_table()
        para_lines = [line.strip()]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if (next_line.startswith('```') or 
                next_line.startswith('>') or 
                next_line.startswith('|') or
                re.match(r'^#{1,6}\s', next_line) or 
                re.match(r'^[\*\-\+]\s', next_line) or 
                re.match(r'^[0-9]+\.\s', next_line) or
                re.match(r'^(\-{3,}|\*{3,}|\_{3,})$', next_line) or
                next_line == ''):
                break
            para_lines.append(next_line)
            i += 1
        
        para_text = ' '.join(para_lines)
        # Skip if it is an Answer placeholder (handled in Q&A pre-scan)
        if not re.match(r'^\*?\*?Answer\*?\*?[\:\s]*', para_text):
            current_section["blocks"].append(f"<p class='searchable'>{parse_inline(para_text)}</p>")
            
    # Flush remaining
    flush_all()
    if current_section["blocks"] or current_section["title"] != "Introduction":
        sections.append(current_section)
        
    return sections, qa_list

def markdown_to_html_snippet(md_text):
    # Quick utility for snippets
    lines = md_text.split('\n')
    html_out = []
    in_list = False
    list_type = None
    
    def close_list():
        nonlocal in_list, list_type
        if in_list:
            html_out.append(f"</{list_type}>")
            in_list = False
            list_type = None
            
    for line in lines:
        if line.strip() == '':
            close_list()
            continue
            
        ul_match = re.match(r'^[\*\-\+]\s+(.*)$', line.strip())
        ol_match = re.match(r'^([0-9]+)\.\s+(.*)$', line.strip())
        
        if ul_match:
            item_text = ul_match.group(1)
            if not in_list or list_type != 'ul':
                close_list()
                html_out.append("<ul>")
                in_list = True
                list_type = 'ul'
            html_out.append(f"<li>{parse_inline(item_text)}</li>")
        elif ol_match:
            item_text = ol_match.group(2)
            if not in_list or list_type != 'ol':
                close_list()
                html_out.append("<ol>")
                in_list = True
                list_type = 'ol'
            html_out.append(f"<li>{parse_inline(item_text)}</li>")
        else:
            close_list()
            html_out.append(f"<p>{parse_inline(line.strip())}</p>")
            
    close_list()
    return '\n'.join(html_out)

def generate_html_page(capstone_num, metadata, sections, qa_list, supplementary_docs):
    title = metadata["name"]
    tagline = metadata["tagline"]
    badge = f"Capstone {capstone_num}"
    accent = metadata["accent"]
    glow = metadata["glow"]
    icon = metadata["icon"]
    
    # Build Table of Contents
    toc_html = []
    toc_html.append('<div class="toc-group">')
    toc_html.append('  <div class="toc-group-title">Core Defense Guide</div>')
    for sec in sections:
        toc_html.append(f'  <a href="#{sec["id"]}" class="toc-link" data-target="{sec["id"]}">{sec["title"]}</a>')
    toc_html.append('</div>')
    
    if supplementary_docs:
        toc_html.append('<div class="toc-group">')
        toc_html.append('  <div class="toc-group-title">Supplementary Knowledge</div>')
        for doc in supplementary_docs:
            toc_html.append(f'  <a href="#{doc["id"]}" class="toc-link" data-target="{doc["id"]}">{doc["title"]}</a>')
        toc_html.append('</div>')

    # Build Content HTML
    content_html = []
    
    # Primary Guide Sections
    for sec in sections:
        content_html.append(f'<section id="{sec["id"]}" class="content-section">')
        content_html.append(f'  <h2 class="section-title searchable">{sec["title"]}</h2>')
        for block in sec["blocks"]:
            content_html.append(f'  {block}')
            
        # If this is a category section, populate its Q&As directly here
        if sec["id"].startswith("cat-") and qa_list:
            cat_qas = [qa for qa in qa_list if qa.get("section_id") == sec["id"]]
            if cat_qas:
                content_html.append('  <div class="qa-list" style="margin-top: 1.5rem;">')
                for qa in cat_qas:
                    content_html.append(f'    <div class="qa-item searchable" data-qa-id="{qa["id"]}" data-category="{qa["category"]}">')
                    content_html.append('      <button class="qa-header">')
                    content_html.append('        <span class="qa-q-badge">Q</span>')
                    content_html.append(f'        <span class="qa-question-text">{parse_inline(qa["question"])}</span>')
                    content_html.append('        <span class="qa-toggle">+</span>')
                    content_html.append('      </button>')
                    content_html.append('      <div class="qa-body">')
                    content_html.append(f'        <div class="qa-answer">{qa["answer"]}</div>')
                    content_html.append('      </div>')
                    content_html.append('    </div>')
                content_html.append('  </div>')
                
        content_html.append('</section>')
        
    # Supplementary Sections
    for doc in supplementary_docs:
        content_html.append(f'<section id="{doc["id"]}" class="content-section">')
        content_html.append(f'  <h2 class="section-title searchable">{doc["title"]}</h2>')
        for block in doc["blocks"]:
            content_html.append(f'  {block}')
        content_html.append('</section>')

    # Using standard template literal replacement to avoid curly braces escaping bugs in f-strings!
    html_template = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__BADGE__ Guide & Details - __TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #06080d;
  --bg-card: rgba(14, 20, 36, 0.7);
  --bg-card-hover: rgba(20, 30, 52, 0.85);
  --border: rgba(255, 255, 255, 0.06);
  --border-hover: rgba(__ACCENT__, 0.25);
  --text: #e8ecf4;
  --text-muted: #7a889e;
  --text-faint: #4a5568;
  --sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  --heading: 'Space Grotesk', system-ui, sans-serif;
  --mono: 'Fira Code', monospace;
  
  --accent: rgb(__ACCENT__);
  --accent-light: rgba(__ACCENT__, 0.08);
  --accent-border: rgba(__ACCENT__, 0.2);
  --accent-glow: __GLOW__;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  min-height: 100vh;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

.bg-mesh {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 80% 50% at 20% 20%, rgba(__ACCENT__, 0.06) 0%, transparent 60%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(16, 185, 129, 0.04) 0%, transparent 55%);
}

.bg-grid {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(255,255,255,0.01) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.01) 1px, transparent 1px);
  background-size: 50px 50px;
}

/* Sticky Top Bar & Sticky Search Bar */
.sticky-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(6, 8, 13, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  padding: 1rem 2rem;
  transition: all 0.3s ease;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  text-decoration: none;
  font-family: var(--mono);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  transition: all 0.2s ease;
}

.back-btn:hover {
  color: var(--text);
  background: rgba(255,255,255,0.08);
  border-color: var(--text-muted);
}

.project-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon {
  font-size: 1.5rem;
}

.title-badge {
  font-family: var(--mono);
  font-size: 0.7rem;
  color: var(--accent);
  background: var(--accent-light);
  border: 1px solid var(--accent-border);
  padding: 0.2rem 0.6rem;
  border-radius: 100px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

h1 {
  font-family: var(--heading);
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
}

/* Sticky Search Bar Container */
.search-wrapper {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 0.8rem 1.2rem 0.8rem 2.8rem;
  background: rgba(14, 20, 36, 0.9);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text);
  font-family: var(--sans);
  font-size: 0.95rem;
  outline: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px -5px rgba(0,0,0,0.5);
}

.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 15px -3px var(--accent-glow), 0 4px 20px -5px rgba(0,0,0,0.5);
  background: rgba(20, 30, 52, 0.95);
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
  font-size: 1rem;
}

.search-clear {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 1rem;
  display: none;
  padding: 0.2rem;
}

.search-clear:hover {
  color: var(--text);
}

.search-stats {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: var(--mono);
  text-align: right;
  margin-top: 0.25rem;
  display: none;
}

/* Layout */
.main-layout {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2.5rem;
  padding: 2.5rem 2rem;
}

/* Sidebar navigation */
.sidebar {
  position: sticky;
  top: 170px;
  height: calc(100vh - 200px);
  overflow-y: auto;
  padding-right: 1rem;
}

.sidebar::-webkit-scrollbar {
  width: 4px;
}

.sidebar::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 4px;
}

.toc-group {
  margin-bottom: 1.5rem;
}

.toc-group-title {
  font-family: var(--mono);
  font-size: 0.65rem;
  color: var(--text-faint);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
  margin-bottom: 0.5rem;
  padding-left: 0.75rem;
}

.toc-link {
  display: block;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.85rem;
  padding: 0.5rem 0.75rem;
  border-left: 2px solid transparent;
  transition: all 0.2s ease;
  line-height: 1.4;
  border-radius: 0 6px 6px 0;
}

.toc-link:hover {
  color: var(--text);
  background: rgba(255,255,255,0.02);
  border-left-color: var(--text-faint);
}

.toc-link.active {
  color: var(--accent);
  font-weight: 500;
  border-left-color: var(--accent);
  background: var(--accent-light);
}

/* Main Content Area */
.content-pane {
  max-width: 900px;
}

.content-section {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 2.5rem;
  margin-bottom: 2rem;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition: all 0.3s ease;
}

.content-section:hover {
  border-color: rgba(__ACCENT__, 0.15);
}

.section-title {
  font-family: var(--heading);
  font-size: 1.8rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
  color: var(--text);
  background: linear-gradient(135deg, #fff 0%, rgba(__ACCENT__, 0.85) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Typography inside Content Sections */
p {
  font-size: 0.95rem;
  line-height: 1.65;
  color: var(--text-muted);
  margin-bottom: 1.25rem;
}

strong {
  color: var(--text);
  font-weight: 600;
}

h3 {
  font-family: var(--heading);
  font-size: 1.3rem;
  color: var(--text);
  margin: 2rem 0 1rem 0;
  font-weight: 500;
}

h4 {
  font-family: var(--heading);
  font-size: 1.1rem;
  color: var(--text);
  margin: 1.5rem 0 0.75rem 0;
  font-weight: 500;
}

ul, ol {
  margin-bottom: 1.25rem;
  padding-left: 1.5rem;
}

li {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

blockquote {
  border-left: 3px solid var(--accent);
  background: var(--accent-light);
  padding: 1rem 1.25rem;
  margin: 1.5rem 0;
  border-radius: 0 8px 8px 0;
  font-style: italic;
}

blockquote p {
  margin-bottom: 0;
  color: var(--text);
}

hr {
  border: 0;
  height: 1px;
  background: var(--border);
  margin: 2.5rem 0;
}

/* Code Blocks */
pre {
  background: #020306;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem;
  margin: 1.5rem 0;
  overflow-x: auto;
}

code {
  font-family: var(--mono);
  font-size: 0.85rem;
  color: rgba(__ACCENT__, 0.95);
  background: rgba(__ACCENT__, 0.05);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}

pre code {
  color: #cfd8e3;
  background: none;
  padding: 0;
  border-radius: 0;
}

/* Table Styling */
.table-container {
  width: 100%;
  overflow-x: auto;
  margin: 1.5rem 0;
  border: 1px solid var(--border);
  border-radius: 10px;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.9rem;
}

th {
  background: rgba(255,255,255,0.02);
  color: var(--text);
  font-weight: 600;
  padding: 1rem;
  border-bottom: 1px solid var(--border);
  font-family: var(--heading);
}

td {
  padding: 1rem;
  border-bottom: 1px solid var(--border);
  color: var(--text-muted);
  line-height: 1.5;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background: rgba(255,255,255,0.01);
  color: var(--text);
}

/* Mock Q&A Accordion */
.qa-filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.filter-btn {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 0.75rem;
  font-family: var(--mono);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-btn:hover, .filter-btn.active {
  background: var(--accent-light);
  border-color: var(--accent-border);
  color: var(--accent);
}

.qa-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.qa-item {
  border: 1px solid var(--border);
  border-radius: 10px;
  background: rgba(255,255,255,0.01);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.qa-item:hover {
  border-color: var(--accent-border);
  background: rgba(255,255,255,0.02);
}

.qa-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: none;
  border: none;
  color: var(--text);
  font-family: var(--heading);
  font-size: 0.95rem;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  outline: none;
  justify-content: space-between;
}

.qa-q-badge {
  width: 24px;
  height: 24px;
  background: var(--accent-light);
  border: 1px solid var(--accent-border);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-family: var(--mono);
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}

.qa-question-text {
  flex: 1;
  line-height: 1.4;
}

.qa-toggle {
  font-size: 1.2rem;
  color: var(--text-faint);
  transition: transform 0.3s ease;
  padding-left: 0.5rem;
}

.qa-body {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.qa-answer {
  padding: 0 1.25rem 1.25rem 3.25rem;
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-muted);
}

.qa-answer p {
  margin-bottom: 0.75rem;
}

.qa-answer p:last-child {
  margin-bottom: 0;
}

.qa-item.open {
  border-color: var(--accent-border);
  background: rgba(__ACCENT__, 0.02);
  box-shadow: 0 4px 20px -10px var(--accent-glow);
}

.qa-item.open .qa-body {
  max-height: 1200px; /* Large enough for detailed answers */
}

.qa-item.open .qa-toggle {
  transform: rotate(45deg);
  color: var(--accent);
}

/* Highlighted search text */
mark.highlight {
  background: rgba(var(--accent), 0.25);
  color: var(--text);
  border-radius: 4px;
  padding: 0.1rem 0.2rem;
  border-bottom: 2px solid var(--accent);
}

/* Search Flex Layout with AI Button */
.search-flex-container {
  display: flex;
  gap: 0.75rem;
  width: 100%;
  align-items: center;
}

.ai-explore-btn {
  background: linear-gradient(135deg, rgba(var(--accent), 0.2) 0%, rgba(var(--accent), 0.05) 100%);
  color: var(--text);
  border: 1px solid rgba(var(--accent), 0.35);
  border-radius: 10px;
  padding: 0.8rem 1.25rem;
  font-weight: 600;
  font-family: var(--sans);
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  box-shadow: 0 0 15px -3px rgba(var(--accent), 0.1), 0 4px 20px -5px rgba(0,0,0,0.5);
}

.ai-explore-btn:hover {
  border-color: rgba(var(--accent), 0.7);
  background: linear-gradient(135deg, rgba(var(--accent), 0.3) 0%, rgba(var(--accent), 0.15) 100%);
  box-shadow: 0 0 20px -2px rgba(var(--accent), 0.35), 0 4px 20px -5px rgba(0,0,0,0.5);
  transform: translateY(-1px);
}

.ai-explore-btn:active {
  transform: translateY(1px);
  box-shadow: 0 0 10px -2px rgba(var(--accent), 0.2);
}

.ai-icon {
  font-size: 1.1rem;
  animation: pulse-glow 2s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { transform: scale(1); filter: drop-shadow(0 0 2px rgba(var(--accent), 0.5)); }
  50% { transform: scale(1.1); filter: drop-shadow(0 0 6px rgba(var(--accent), 0.8)); }
}

/* Toast Notification Styles */
.ai-toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: rgba(10, 15, 30, 0.95);
  border: 1px solid rgba(var(--accent), 0.3);
  border-radius: 12px;
  padding: 1rem 1.5rem;
  color: var(--text);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.6), 0 0 30px -5px rgba(var(--accent), 0.3);
  transform: translateY(150%) scale(0.9);
  opacity: 0;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
  max-width: 350px;
}

.ai-toast.show {
  transform: translateY(0) scale(1);
  opacity: 1;
  pointer-events: auto;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.toast-icon {
  font-size: 1.5rem;
}

.toast-text-wrapper {
  display: flex;
  flex-direction: column;
}

.toast-title {
  font-family: var(--heading);
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text);
}

.toast-desc {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.toast-progress {
  height: 3px;
  background: var(--accent);
  width: 100%;
  border-radius: 2px;
  transform-origin: left;
  transform: scaleX(0);
}

.toast-progress.animate {
  animation: progress-bar linear forwards;
}

@keyframes progress-bar {
  from { transform: scaleX(1); }
  to { transform: scaleX(0); }
}

/* Search overlay for empty search results */
.no-results {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-muted);
  display: none;
}

.no-results-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Floating Mobile Menu Button & Drawer */
.mobile-menu-toggle {
  display: none;
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 110;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--accent);
  color: #000;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 30px -5px var(--accent-glow);
  transition: all 0.3s ease;
}

.mobile-menu-toggle:hover {
  transform: scale(1.05);
}

/* Responsive Breakpoints */
@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem 1.25rem;
    position: static;
    z-index: auto;
  }
  
  .content-pane {
    min-width: 0;
    width: 100%;
  }
  
  .sidebar {
    position: fixed;
    top: 0;
    left: -300px;
    width: 280px;
    height: 100vh;
    z-index: 1000;
    background: #090d16;
    border-right: 1px solid var(--border);
    padding: 2rem 1.5rem;
    transition: left 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }
  
  .sidebar.open {
    left: 0;
    box-shadow: 20px 0 60px rgba(0,0,0,0.8);
  }
  
  .mobile-menu-toggle {
    display: flex;
  }
  
  .content-section {
    padding: 1.75rem;
  }
}

@media (max-width: 640px) {
  .sticky-header {
    padding: 0.5rem 0.75rem;
  }
  
  .header-container {
    gap: 0.5rem;
  }
  
  h1 {
    font-size: 1.1rem;
  }
  
  .project-title {
    flex-wrap: nowrap;
    gap: 0.4rem;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .search-flex-container {
    flex-direction: row;
    gap: 0.5rem;
    align-items: center;
  }
  
  .search-wrapper {
    flex: 1;
  }
  
  .ai-explore-btn {
    width: auto;
    padding: 0.6rem 0.8rem;
    font-size: 0.85rem;
    white-space: nowrap;
  }
  
  .ai-btn-text-extra {
    display: none;
  }
  
  .content-section {
    padding: 1.25rem;
    border-radius: 12px;
  }
  
  .section-title {
    font-size: 1.4rem;
  }
  
  .qa-answer {
    padding-left: 1.25rem;
  }
  
  /* Prevent tables from causing horizontal page scrolling */
  table {
    font-size: 0.8rem;
  }
  
  th, td {
    padding: 0.75rem 0.5rem;
  }
}

/* Overlay for mobile drawer */
.sidebar-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 999;
  backdrop-filter: blur(4px);
}

.sidebar-overlay.open {
  display: block;
}
</style>
  <!-- MathJax for rendering LaTeX formulas -->
  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']],
        processEscapes: true
      },
      options: {
        ignoreHtmlClass: 'tex2jax_ignore',
        processHtmlClass: 'tex2jax_process'
      }
    };
  </script>
  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
  <div class="bg-mesh"></div>
  <div class="bg-grid"></div>

  <!-- Sticky Header containing search and title -->
  <header class="sticky-header">
    <div class="header-container">
      <div class="top-nav">
        <a class="back-btn" href="../../index.html">&larr; Dashboard</a>
        <div class="project-title">
          <span class="title-icon">__ICON__</span>
          <h1>__TITLE__</h1>
          <span class="title-badge">__BADGE__</span>
        </div>
      </div>
      
      <!-- Sticky Search Bar -->
      <div class="search-flex-container">
        <div class="search-wrapper">
          <span class="search-icon">&#x1F50D;</span>
          <input type="text" class="search-input" id="search-input" placeholder="Search guide or type AI question, then click 'Explore with AI'...">
          <button class="search-clear" id="search-clear">&times;</button>
        </div>
        <button class="ai-explore-btn" id="ai-explore-btn" onclick="exploreWithAI()">
          <span class="ai-icon">✨</span> Explore <span class="ai-btn-text-extra">with AI</span>
        </button>
      </div>
      <div class="search-stats" id="search-stats">Showing all sections</div>
    </div>
  </header>

  <!-- Sidebar Overlay -->
  <div class="sidebar-overlay" id="sidebar-overlay"></div>

  <!-- Floating Mobile Menu Button -->
  <button class="mobile-menu-toggle" id="mobile-menu-toggle">&#x2630;</button>

  <!-- Main Layout -->
  <div class="main-layout">
    <!-- Sidebar navigation -->
    <aside class="sidebar" id="sidebar">
      __TOC_HTML__
    </aside>

    <!-- Main Content Pane -->
    <main class="content-pane" id="content-pane">
      __CONTENT_HTML__
      
      <div class="no-results" id="no-results">
        <div class="no-results-icon">🕵️‍♂️</div>
        <h3>No matching concepts found</h3>
        <p style="margin-bottom: 1.5rem;">Try searching for other terms like "architecture", "security", or specific components.</p>
        <button class="ai-explore-btn" onclick="exploreWithAI()" style="margin: 0 auto; display: inline-flex;">
          <span class="ai-icon">✨</span> Explore <span class="ai-btn-text-extra">with AI</span>
        </button>
      </div>
    </main>
  </div>

  <script>
    // Q&A Accordion Toggle
    document.querySelectorAll('.qa-header').forEach(header => {
      header.addEventListener('click', () => {
        const item = header.parentElement;
        item.classList.toggle('open');
      });
    });

    // Category Filter for Q&A
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const cat = btn.getAttribute('data-cat');
        document.querySelectorAll('.qa-item').forEach(item => {
          if (cat === 'all' || item.getAttribute('data-category') === cat) {
            item.style.display = 'block';
          } else {
            item.style.display = 'none';
          }
        });
      });
    });

    // Mobile Navigation Drawer Toggle
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const menuToggle = document.getElementById('mobile-menu-toggle');

    function toggleMobileMenu() {
      sidebar.classList.toggle('open');
      overlay.classList.toggle('open');
      if (sidebar.classList.contains('open')) {
        menuToggle.innerHTML = '&times;';
        menuToggle.style.background = '#f87171'; // soft red for close
      } else {
        menuToggle.innerHTML = '&#x2630;';
        menuToggle.style.background = 'var(--accent)';
      }
    }

    menuToggle.addEventListener('click', toggleMobileMenu);
    overlay.addEventListener('click', toggleMobileMenu);
    
    // Close mobile menu when link clicked
    document.querySelectorAll('.toc-link').forEach(link => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 1024) {
          toggleMobileMenu();
        }
      });
    });

    // Table of Contents Active Link Highlight on Scroll
    const observerOptions = {
      root: null,
      rootMargin: '-10% 0px -70% 0px',
      threshold: 0
    };

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          document.querySelectorAll('.toc-link').forEach(link => {
            if (link.getAttribute('data-target') === id) {
              link.classList.add('active');
            } else {
              link.classList.remove('active');
            }
          });
        }
      });
    }, observerOptions);

    document.querySelectorAll('section.content-section').forEach(section => {
      observer.observe(section);
    });

    // Client-side Search Engine
    const searchInput = document.getElementById('search-input');
    const searchClear = document.getElementById('search-clear');
    const searchStats = document.getElementById('search-stats');
    const noResults = document.getElementById('no-results');

    // Create search index mapping from searchable items
    const searchIndex = [];
    document.querySelectorAll('.content-section').forEach(section => {
      const sectionId = section.getAttribute('id');
      const sectionTitle = section.querySelector('.section-title').textContent;
      
      // Store standard searchable elements (paragraphs, list items, headers)
      section.querySelectorAll('.searchable').forEach(el => {
        // Skip elements inside qa-item answers to avoid double-processing, Q&As handled separately below
        if (el.closest('.qa-item')) return;
        
        searchIndex.push({
          element: el,
          sectionId: sectionId,
          type: 'text',
          originalHTML: el.innerHTML,
          text: el.textContent.toLowerCase()
        });
      });
      
      // Store Q&A cards
      section.querySelectorAll('.qa-item').forEach(qaItem => {
        const qText = qaItem.querySelector('.qa-question-text');
        const aContent = qaItem.querySelector('.qa-answer');
        
        searchIndex.push({
          element: qaItem,
          sectionId: sectionId,
          type: 'qa',
          qaItem: qaItem,
          qTextEl: qText,
          aContentEl: aContent,
          originalQHTML: qText.innerHTML,
          originalAHTML: aContent.innerHTML,
          qText: qText.textContent.toLowerCase(),
          aText: aContent.textContent.toLowerCase()
        });
      });
    });

    searchInput.addEventListener('input', runSearch);
    searchClear.addEventListener('click', () => {
      searchInput.value = '';
      runSearch();
      searchInput.focus();
    });

    function runSearch() {
      const query = searchInput.value.trim().toLowerCase();
      
      if (query === '') {
        searchClear.style.display = 'none';
        searchStats.style.display = 'none';
        noResults.style.display = 'none';
        
        // Reset all elements
        searchIndex.forEach(item => {
          if (item.type === 'text') {
            item.element.innerHTML = item.originalHTML;
            item.element.style.display = '';
          } else if (item.type === 'qa') {
            item.qTextEl.innerHTML = item.originalQHTML;
            item.aContentEl.innerHTML = item.originalAHTML;
            item.qaItem.style.display = '';
            item.qaItem.classList.remove('open');
          }
        });
        
        // Show all sections & reset links
        document.querySelectorAll('section.content-section').forEach(sec => {
          sec.style.display = '';
        });
        document.querySelectorAll('.toc-link').forEach(link => {
          link.style.opacity = '';
          link.style.pointerEvents = '';
        });
        return;
      }
      
      searchClear.style.display = 'block';
      
      // Multi-term support: split query by whitespace
      const terms = query.split(/\s+/).filter(t => t.length > 0);
      
      let matchCount = 0;
      const visibleSections = new Set();
      
      // Perform search filtering
      searchIndex.forEach(item => {
        if (item.type === 'text') {
          // Check if every search term is found in the text
          const matches = terms.every(term => item.text.includes(term));
          if (matches) {
            matchCount++;
            visibleSections.add(item.sectionId);
            item.element.style.display = '';
            item.element.innerHTML = highlightText(item.originalHTML, query);
          } else {
            item.element.style.display = 'none';
          }
        } else if (item.type === 'qa') {
          // Check for each search term in Q or A
          const matches = terms.every(term => item.qText.includes(term) || item.aText.includes(term));
          
          if (matches) {
            matchCount++;
            visibleSections.add(item.sectionId);
            item.qaItem.style.display = '';
            
            // Highlight matching parts
            const qMatchesAny = terms.some(term => item.qText.includes(term));
            const aMatchesAny = terms.some(term => item.aText.includes(term));
            
            if (qMatchesAny) {
              item.qTextEl.innerHTML = highlightText(item.originalQHTML, query);
            } else {
              item.qTextEl.innerHTML = item.originalQHTML;
            }
            
            if (aMatchesAny) {
              item.aContentEl.innerHTML = highlightText(item.originalAHTML, query);
            } else {
              item.aContentEl.innerHTML = item.originalAHTML;
            }
            
            // Auto expand matching Q&A items!
            item.qaItem.classList.add('open');
          } else {
            item.qaItem.style.display = 'none';
            item.qaItem.classList.remove('open');
          }
        }
      });
      
      // Filter main content sections based on whether they contain any matches
      document.querySelectorAll('section.content-section').forEach(sec => {
        const id = sec.getAttribute('id');
        if (visibleSections.has(id)) {
          sec.style.display = '';
        } else {
          sec.style.display = 'none';
        }
      });
      
      // Update sidebar TOC link styling (dim sections with no results)
      document.querySelectorAll('.toc-link').forEach(link => {
        const targetId = link.getAttribute('data-target');
        if (visibleSections.has(targetId)) {
          link.style.opacity = '1';
          link.style.pointerEvents = 'auto';
        } else {
          link.style.opacity = '0.3';
          link.style.pointerEvents = 'none';
        }
      });
      
      // Update status info
      searchStats.style.display = 'block';
      searchStats.textContent = 'Found ' + matchCount + ' matching concept(s) across ' + visibleSections.size + ' section(s)';
      
      if (matchCount === 0) {
        noResults.style.display = 'block';
      } else {
        noResults.style.display = 'none';
      }
    }

    function highlightText(htmlText, query) {
      const terms = query.split(/\s+/).filter(t => t.length > 0);
      if (terms.length === 0) return htmlText;
      
      // Sort terms by length descending to prevent shorter sub-terms from mangling HTML markup of longer terms
      terms.sort((a, b) => b.length - a.length);
      
      let highlighted = htmlText;
      terms.forEach(term => {
        const escQuery = term.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        // Regex matches query outside of HTML tags (<...>) and prevents recursive marking
        const regex = new RegExp('(' + escQuery + ')(?=[^>]*<|[^>]*$)', 'gi');
        highlighted = highlighted.replace(regex, '<mark class="highlight">$1</mark>');
      });
      return highlighted;
    }

    // --- Toast Notification ---
    function showToast(title, desc, duration = 3000) {
      const toast = document.getElementById('ai-toast');
      if (!toast) return;
      const toastTitle = toast.querySelector('.toast-title');
      const toastDesc = toast.querySelector('.toast-desc');
      const progress = toast.querySelector('.toast-progress');
      
      if (toastTitle) toastTitle.textContent = title;
      if (toastDesc) toastDesc.textContent = desc;
      
      toast.classList.add('show');
      progress.classList.remove('animate');
      void progress.offsetWidth; // Trigger DOM reflow
      progress.style.animationDuration = `${duration}ms`;
      progress.classList.add('animate');
      
      setTimeout(() => {
        toast.classList.remove('show');
      }, duration);
    }

    // --- DOM Knowledge Base Text Extraction ---
    function getKnowledgeBaseText() {
      let textParts = [];
      
      document.querySelectorAll('section.content-section').forEach(section => {
        const titleEl = section.querySelector('.section-title');
        if (titleEl) {
          textParts.push(`\n# ${titleEl.textContent.trim()}\n`);
        }
        
        section.querySelectorAll('.searchable').forEach(el => {
          if (el.classList.contains('qa-item')) {
            const qText = el.querySelector('.qa-question-text')?.textContent.trim() || '';
            const aText = el.querySelector('.qa-answer')?.textContent.trim() || '';
            textParts.push(`Q: ${qText}\nA: ${aText}\n`);
          } else if (el.closest('.qa-item')) {
            // Avoid duplicate processing of elements nested inside Q&As
            return;
          } else {
            const tag = el.tagName.toLowerCase();
            const text = el.textContent.trim();
            if (!text) return;
            
            if (tag.startsWith('h')) {
              textParts.push(`## ${text}\n`);
            } else {
              textParts.push(`${text}\n`);
            }
          }
        });
      });
      
      return textParts.join('\n').trim();
    }

    // --- Explore with AI (Redirect to Gemini) ---
    function exploreWithAI() {
      const query = document.getElementById('search-input').value.trim();
      const title = document.querySelector('.project-title h1')?.textContent || 'this capstone project';
      const tagline = document.querySelector('.project-title h1')?.nextElementSibling?.textContent || '';
      
      const knowledgeBase = getKnowledgeBaseText();
      
      let promptText = `You are an AI assistant helping me analyze the capstone project "${title}" (${tagline}).\n\n`;
      if (query) {
        promptText += `My question/focus is: "${query}"\n\n`;
      } else {
        promptText += `Please help me explore this capstone project.\n\n`;
      }
      
      promptText += `Here is the comprehensive project documentation and knowledge base for context:\n`;
      promptText += `=========================================\n`;
      promptText += knowledgeBase;
      promptText += `\n=========================================\n\n`;
      
      if (query) {
        promptText += `Please answer my question ("${query}") based on the documentation provided above. If the information isn't directly in the docs, use your general knowledge but clearly indicate what is from the docs and what is external extrapolation.`;
      } else {
        promptText += `Please provide a strategic overview of this project, list its core architecture elements, point out key panel defense risks/questions, and suggest how the presenters can best pitch this to a jury.`;
      }
      
      const maxUrlLength = 6000;
      
      // Prepare short prompt for Gemini URL query parameter
      let shortPrompt = `I want to explore the capstone project "${title}". `;
      if (query) {
        shortPrompt += `My question is: "${query}". `;
      }
      shortPrompt += `I have copied the entire project knowledge base/documentation to my clipboard. I will paste it in my next message. Please prepare to receive it.`;
      
      const encodedShort = encodeURIComponent(shortPrompt);
      const geminiUrl = `https://gemini.google.com/app?q=${encodedShort}`;
      
      // Copy prompt to clipboard
      navigator.clipboard.writeText(promptText).then(() => {
        showToast(
          "📋 Context Copied!",
          "Use Ctrl+V (or Cmd+V) to paste the full documentation in Gemini. Redirecting in 4 seconds...",
          4000
        );
        setTimeout(() => {
          window.open(geminiUrl, '_blank');
        }, 3800);
      }).catch(err => {
        console.error("Clipboard copy failed, falling back to direct URL redirect: ", err);
        
        let fallbackPrompt = promptText;
        if (fallbackPrompt.length > maxUrlLength) {
          fallbackPrompt = fallbackPrompt.substring(0, maxUrlLength - 100) + "... [truncated due to URL limits]";
        }
        const encodedFallback = encodeURIComponent(fallbackPrompt);
        const fallbackUrl = `https://gemini.google.com/app?q=${encodedFallback}`;
        
        showToast(
          "✨ Redirecting...",
          "Opening Gemini with direct URL prompt...",
          2000
        );
        setTimeout(() => {
          window.open(fallbackUrl, '_blank');
        }, 1500);
      });
    }
  </script>
  
  <!-- Toast HTML -->
  <div id="ai-toast" class="ai-toast">
    <div class="toast-content">
      <span class="toast-icon">✨</span>
      <div class="toast-text-wrapper">
        <div class="toast-title">Copying Knowledge Base...</div>
        <div class="toast-desc">Copying context to clipboard and opening Gemini</div>
      </div>
    </div>
    <div class="toast-progress"></div>
  </div>
</body>
</html>
"""
    
    # Do manual replacements to avoid any f-string curly-bracket collisions!
    html_page = html_template
    html_page = html_page.replace('__TITLE__', title)
    html_page = html_page.replace('__TAGLINE__', tagline)
    html_page = html_page.replace('__BADGE__', badge)
    html_page = html_page.replace('__ACCENT__', accent)
    html_page = html_page.replace('__GLOW__', glow)
    html_page = html_page.replace('__ICON__', icon)
    html_page = html_page.replace('__TOC_HTML__', '\n'.join(toc_html))
    html_page = html_page.replace('__CONTENT_HTML__', '\n'.join(content_html))
    
    return html_page

def process_all_capstones():
    for num in range(1, 7):
        meta = METADATA[num]
        cap_dir = BASE_DIR / f"capstone{num}"
        print(f"Processing Capstone {num} in {cap_dir}...")
        
        # Discover all markdown files
        md_files = list(cap_dir.glob("*.md"))
        if not md_files:
            print(f"  No markdown files found in {cap_dir}!")
            continue
            
        # Determine the primary defense guide file
        primary_guide_file = None
        for file in md_files:
            name_lower = file.name.lower()
            if "defense_guide" in name_lower or "defense-guide" in name_lower:
                primary_guide_file = file
                break
                
        if not primary_guide_file:
            for file in md_files:
                name_lower = file.name.lower()
                if "defense-documentation" in name_lower or "defense_documentation" in name_lower:
                    primary_guide_file = file
                    break
                
        if not primary_guide_file:
            # Fallback to the largest markdown file or README.md
            readme_files = [f for f in md_files if "readme" in f.name.lower()]
            if readme_files:
                primary_guide_file = readme_files[0]
            else:
                primary_guide_file = sorted(md_files, key=lambda x: x.stat().st_size, reverse=True)[0]
                
        print(f"  Primary guide selected: {primary_guide_file.name}")
        
        # Parse the primary guide
        sections, qa_list = parse_markdown_file(primary_guide_file)
        
        # Parse all other markdown files as supplementary documents
        supplementary_docs = []
        for file in md_files:
            if file == primary_guide_file:
                continue
            name_lower = file.name.lower()
            # Skip development/internal/process files that aren't useful as defense guide readouts
            skip_files = [
                "agents.md", "claude.md", "install.md", "readme.md", "review.md",
                "demo.md", "demo-template.md", "system-planning-prompt.md", "system_planning_prompt.md"
            ]
            if name_lower in skip_files:
                continue
            
            print(f"  Parsing supplementary: {file.name}")
            doc_sections, _ = parse_markdown_file(file)
            
            # Combine all blocks of the supplementary document into a single tab section
            doc_title = file.stem.replace('_', ' ').replace('-', ' ').title()
            doc_id = f"supp-{file.stem.lower().replace('_', '-').replace('.', '')}"
            
            # Convert all sections in the supplementary document to HTML blocks
            doc_blocks = []
            for d_sec in doc_sections:
                if d_sec["title"] != "Introduction":
                    doc_blocks.append(f'<h3 class="searchable">{d_sec["title"]}</h3>')
                for block in d_sec["blocks"]:
                    doc_blocks.append(block)
                    
            supplementary_docs.append({
                "id": doc_id,
                "title": doc_title,
                "blocks": doc_blocks
            })
            
        # Generate HTML content
        html_page = generate_html_page(num, meta, sections, qa_list, supplementary_docs)
        
        # Ensure output folder exists
        out_folder = OUTPUT_DIR / f"capstone{num}"
        out_folder.mkdir(parents=True, exist_ok=True)
        
        output_file = out_folder / "defense-and-details.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_page)
            
        print(f"  Generated: {output_file}")
        
if __name__ == "__main__":
    process_all_capstones()
