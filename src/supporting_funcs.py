from textnode import TextNode, TextType
import re
from htmlnode import LeafNode
from htmlnode import ParentNode
from htmlnode import HTMLNode
from enum import Enum
import os
from pathlib import Path

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Split text nodes by delimiter pairs like "**bold**" and return new nodes.
    """
    new_nodes = []
    
    for old_node in old_nodes:
        # Skip non-text nodes or nodes that aren't of TEXT type
        if not isinstance(old_node, TextNode) or old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        # Get the text from the node
        text = old_node.text
        remaining_text = ""
        
        # Keep track of our current position in the text
        cursor = 0
        
        # Continue until we've processed all text
        while cursor < len(text):
            # Find the opening delimiter
            start = text.find(delimiter, cursor)
            
            if start == -1:
                # No more delimiters, add the remaining text
                remaining_text += text[cursor:]
                break
            
            # Add any text before the delimiter
            remaining_text += text[cursor:start]
            
            # Find the closing delimiter
            end = text.find(delimiter, start + len(delimiter))
            
            if end == -1:
                # No closing delimiter, treat as regular text
                remaining_text += text[start:]
                break
            
            # If we have accumulated regular text, add it as a node
            if remaining_text:
                new_nodes.append(TextNode(remaining_text, TextType.TEXT))
                remaining_text = ""
            
            # Extract the content between delimiters
            delimited_content = text[start + len(delimiter):end]
            
            # Add the delimited content as a node with the appropriate type
            new_nodes.append(TextNode(delimited_content, text_type))
            
            # Move cursor past the closing delimiter
            cursor = end + len(delimiter)
        
        # Add any remaining text
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    return new_nodes

def extract_markdown_images(text):
    """
    Extract markdown images from the text.
    """
    images = []
    images = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text) 
    return images

def extract_markdown_links(text):
    """
    Extract markdown links from the text.
    """
    links = []
    links = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text) 
    return links

def split_nodes_image(old_nodes):
    """
    Split the old nodes by images and return a list of new nodes.
    """
    result = []
    
    for old_node in old_nodes:
        if not isinstance(old_node, TextNode) or old_node.text_type != TextType.TEXT:
            result.append(old_node)
            continue
            
        images = extract_markdown_images(old_node.text)
        if not images:
            result.append(old_node)
            continue
            
        # Start with the original text
        remaining_text = old_node.text
        
        for alt_text, url in images:
            image_markdown = f"![{alt_text}]({url})"
            
            # Split at the first occurrence of this image
            parts = remaining_text.split(image_markdown, 1)
            
            # Add the text before the image if it's not empty
            if parts[0]:
                result.append(TextNode(parts[0], TextType.TEXT))
                
            # Add the image node
            result.append(TextNode(alt_text, TextType.IMAGE, url))
            
            # Update remaining_text for next iteration (or final text)
            if len(parts) > 1:
                remaining_text = parts[1]
            else:
                remaining_text = ""
                
        # Add any remaining text after processing all images
        if remaining_text:
            result.append(TextNode(remaining_text, TextType.TEXT))
    
    return result

def split_nodes_links(old_nodes):

    result = []
    
    for old_node in old_nodes:
        if not isinstance(old_node, TextNode) or old_node.text_type != TextType.TEXT:
            result.append(old_node)
            continue
            
        links = extract_markdown_links(old_node.text)
        if not links:
            result.append(old_node)
            continue
        valid_links = [
            (link_text, url) for link_text, url in links 
            if link_text and url  # Ensure neither is empty
        ]
        if not valid_links:
            result.append(old_node)
            continue


        remaining_text = old_node.text
        
        for link_text, url in valid_links:
            link_markdown = f"[{link_text}]({url})"
            
            # Split at the first occurrence of this link
            parts = remaining_text.split(link_markdown, 1)
            
            if parts[0]:
                result.append(TextNode(parts[0], TextType.TEXT))
                
            # Add the link node
            result.append(TextNode(link_text, TextType.LINK, url))
            
            # Update remaining_text for next iteration (or final text)
            if len(parts) > 1:
                remaining_text = parts[1]
            else:
                remaining_text = ""
                
        # Add any remaining text after processing all links
        if remaining_text:
            result.append(TextNode(remaining_text, TextType.TEXT))
    
    return result

def split_nodes_bold(old_nodes):
    """
    Split the old nodes by bold text and return a list of new nodes.
    """
    return split_nodes_delimiter(old_nodes, "**", TextType.BOLD)

def split_nodes_italic(old_nodes):
    """
    Split the old nodes by italic text and return a list of new nodes.
    """
    return split_nodes_delimiter(old_nodes, "_", TextType.ITALIC)

def split_nodes_code(old_nodes):
    """
    Split the old nodes by code text and return a list of new nodes.
    """
    return split_nodes_delimiter(old_nodes, "`", TextType.CODE)

def text_to_textnodes(text):
    
    nodes =  [TextNode(text, TextType.TEXT)]

    nodes = split_nodes_image(nodes)
    nodes = split_nodes_links(nodes)
    nodes = split_nodes_bold(nodes)
    nodes = split_nodes_italic(nodes)
    nodes = split_nodes_code(nodes)
    
    return nodes


def markdown_to_blocks(markdown):
    markdown = markdown.strip()
    tmp_blocks = markdown.split("\n\n")  # Split blocks by blank lines
    blocks = []

    for block in tmp_blocks:
        if not block.strip():
            continue

        # Handle list blocks
        if block.strip().startswith("- ") or block.strip().startswith("* ") or block[0].isdigit():
            cleaned_lines = [line.lstrip() for line in block.splitlines()]
            blocks.append("\n".join(cleaned_lines))  # Preserving newlines between list items

        else:
            # Preserve explicit line breaks within paragraphs
            paragraph = "\n".join(line.strip() for line in block.splitlines())
            blocks.append(paragraph)  # Append the paragraph with line breaks maintained

    return blocks

class BlockType(Enum):
    """
    Enum to represent different block types.
    """
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
    """
    Convert a block of text to its corresponding block type.
    """
    def quote_check(block):
        
        result = True
        for line in block.split("\n"):
            if not line.startswith(">"):
                result = False
                break
        return result

    def unordered_list_check(block):

        result = True
        for line in block.split("\n"):
            if not line.startswith("- "):
                result = False
                break
        return result
    
    def ordered_list_check(block):
        lines = block.split("\n")
        for i, line in enumerate(lines, 1):  # Start counting from 1
            # Check if each line starts with the correct number followed by ". "
            if not line.startswith(f"{i}. "):
                return False
        return True
    
    def code_block_check(block):
        lines = block.split("\n")
        if len(lines) < 2:  # Need at least opening and closing backticks
            return False
        return lines[0].startswith("```") and lines[-1].startswith("```")

    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING
    elif code_block_check(block):
        return BlockType.CODE
    elif quote_check(block):
        return BlockType.QUOTE
    elif unordered_list_check(block):
        return BlockType.UNORDERED_LIST
    elif ordered_list_check(block):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH
    
import re

def convert_inline_formatting(text):
    """
    Apply inline formatting to the given markdown text.
    Handles bold, italics, and links.
    """
    
    # Handle links: [text](url)
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"  # Regex to capture [text](url)
    text = re.sub(link_pattern, r'<a href="\2">\1</a>', text)  # Replace with HTML <a> tag
    
    # Handle bold: **text**
    bold_pattern = r"\*\*(.*?)\*\*"
    text = re.sub(bold_pattern, r'<b>\1</b>', text)  # Replace with <b> tag

    # Handle italics: _text_
    italic_pattern = r"_(.*?)_"
    text = re.sub(italic_pattern, r'<i>\1</i>', text)  # Replace with <i> tag

    return text

def parse_nested_list(lines, is_ordered=False):
    # Decide the top-level list tag
    list_tag = "ol" if is_ordered else "ul"
    root_list = ParentNode(list_tag, children=[])  # Root level <ul> or <ol>
    stack = [(0, root_list)]  # Stack of tuples (indent_level, current_list)

    for line in lines:
        if not line.strip():
            continue  # Skip empty lines

        # Calculate indentation level
        indent = len(line) - len(line.lstrip())
        content = line.strip()

        # Detect ordered and unordered markers to strip them away
        if content[0].isdigit() and content[1:3] == '. ':
            content = content[3:].strip()  # Remove "1. " for ordered items
        else:
            content = content[1:].strip()  # Remove "-", "*" for unordered items

        # Apply inline formatting to the content before wrapping it
        formatted_content = convert_inline_formatting(content)

        # Step 1: Ascend to the appropriate list level if indentation decreases
        while stack and stack[-1][0] > indent:
            stack.pop()

        # Step 2: Handle deeper indentation (creating a new nested list)
        if stack[-1][0] < indent:
            # Add a new nested list under the last <li> in the current level
            current_li = stack[-1][1].children[-1]  # Last <li> in the current list
            new_nested_list = ParentNode(list_tag, children=[])  # Nested list inherits parent's tag
            current_li.children.append(new_nested_list)  # Attach as child of the last <li>
            stack.append((indent, new_nested_list))

        # Step 3: Add a new <li> to the current list
        current_list = stack[-1][1]  # Get the current list (from the stack)
        content_node = TextNode(formatted_content, text_type=TextType.NORMAL)  # Create content node
        new_li = ParentNode("li", children=[content_node])  # Wrap the content node in a <li>
        current_list.children.append(new_li)  # Append the <li> to the current list

    # At the end, return the root list node
    return root_list

def process_nested_quotes(lines):
    if not lines:
        return []

    # Create a list for the nodes at the current level
    current_level_nodes = []
    current_depth = lines[0].count(">")

    while lines:
        line_depth = lines[0].count(">")

        if line_depth > current_depth:
            # Process deeper nested blockquote
            nested_nodes = process_nested_quotes(lines)
            current_level_nodes.append(ParentNode("blockquote", nested_nodes))
        elif line_depth == current_depth:
            # Handle the current line
            stripped_line = lines.pop(0).lstrip("> ").strip()
            if stripped_line:
                # Check if we can merge this line with the previous blockquote
                if current_level_nodes and isinstance(current_level_nodes[-1], LeafNode) and current_level_nodes[-1].tag == "blockquote":
                    # Merge the current stripped line into the previous blockquote
                    current_level_nodes[-1].value += " " + stripped_line
                else:
                    # Otherwise treat as a new blockquote
                    current_level_nodes.append(LeafNode("blockquote", stripped_line))
        else:
            # If the current line's depth is less, we return to parent depth
            break

    # Wrap all current-level nodes in a "blockquote" ParentNode if necessary
    return [ParentNode("blockquote", current_level_nodes)]

def split_blocks(text):
    # Splitting text into lines
    lines = text.split('\n')
    blocks = []
    current_paragraph = []

    # Loop through lines and group paragraphs
    for line in lines:
        if line.strip() == '':
            # End the current paragraph
            if current_paragraph:
                # Join all lines with a single space
                blocks.append(' '.join(current_paragraph))
                current_paragraph = []
        else:
            # Add line to the current paragraph, stripping excess spaces
            current_paragraph.append(line.strip())

    # Add any leftover paragraph
    if current_paragraph:
        blocks.append(' '.join(current_paragraph))

    return blocks

def find_closest_delimiter(text):
    import re
    # Pattern matching for markdown delimiters
    patterns = {
        '**': re.compile(r'\*\*(.+?)\*\*'),  # Bold
        '_': re.compile(r'_(.+?)_'),        # Italic
        '`': re.compile(r'`(.+?)`')        # Code
    }

    closest_match = None
    closest_start = float('inf')  # Start with a very high index

    # Iterate over the patterns to find the closest match
    for delimiter, pattern in patterns.items():
        match = pattern.search(text)
        if match:
            start_idx, end_idx = match.start(1), match.end(1)  # Only capture the inner text
            if match.start() < closest_start:  # Still check the outer delimiter span for order
                closest_match = (delimiter, start_idx, end_idx)
                closest_start = match.start()

    return closest_match  # Closest delimiter (or None if no matches found)

# In parse_inline_formatting function
def parse_inline_formatting(text):
    nodes = []
    
    # Regular expressions for different markdown elements
    image_pattern = r'!\[([^\]]+)\]\(([^)]+)\)'
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    bold_pattern = r'\*\*([^*]+)\*\*|__([^_]+)__'
    italic_pattern = r'\*([^*]+)\*|_([^_]+)_'
    code_pattern = r'`([^`]+)`'
    
    # Process the text character by character
    i = 0
    start = 0

    while i < len(text):
        # Check for image: ![alt](url)
        image_match = re.match(image_pattern, text[i:])
        if image_match:
            # Add text before the image as a TEXT node
            if i > start:
                nodes.append(TextNode(text[start:i], TextType.TEXT))
            
            alt_text = image_match.group(1)
            url = image_match.group(2)
            nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            i += image_match.end()
            start = i
            continue
            
        # Check for link: [text](url)
        link_match = re.match(link_pattern, text[i:])
        if link_match:
            # Add text before the link as a TEXT node
            if i > start:
                nodes.append(TextNode(text[start:i], TextType.TEXT))
            
            link_text = link_match.group(1)
            url = link_match.group(2)
            nodes.append(TextNode(link_text, TextType.LINK, url))
            
            i += link_match.end()
            start = i
            continue
          # Check for bold: **text** or __text__
        bold_match = re.match(bold_pattern, text[i:])
        if bold_match:
            # Add text before the bold as a TEXT node
            if i > start:
                nodes.append(TextNode(text[start:i], TextType.TEXT))
            
            # Group 1 for **text**, group 2 for __text__
            bold_text = bold_match.group(1) if bold_match.group(1) else bold_match.group(2)
            nodes.append(TextNode(bold_text, TextType.BOLD))
            
            i += bold_match.end()
            start = i
            continue
            
        # Check for italic: *text* or _text_
        italic_match = re.match(italic_pattern, text[i:])
        if italic_match:
            # Add text before the italic as a TEXT node
            if i > start:
                nodes.append(TextNode(text[start:i], TextType.TEXT))
            
            # Group 1 for *text*, group 2 for _text_
            italic_text = italic_match.group(1) if italic_match.group(1) else italic_match.group(2)
            nodes.append(TextNode(italic_text, TextType.ITALIC))
            
            i += italic_match.end()
            start = i
            continue
            
        # Check for code: `text`
        code_match = re.match(code_pattern, text[i:])
        if code_match:
            # Add text before the code as a TEXT node
            if i > start:
                nodes.append(TextNode(text[start:i], TextType.TEXT))
            
            code_text = code_match.group(1)
            nodes.append(TextNode(code_text, TextType.CODE))
            
            i += code_match.end()
            start = i
            continue  

        i += 1
    
    # Add any remaining text as a TEXT node
    if start < len(text):
        nodes.append(TextNode(text[start:], TextType.TEXT))
    
    return nodes 



def markdown_to_html_node(markdown):
    """
    Convert markdown to HTMLNode.
    """
    # First convert markdown to blocks
    blocks = markdown_to_blocks(markdown)

    if not blocks:
        return ParentNode("div", [])
    
    # Initialize an empty list to hold the HTML nodes
    html_nodes = []
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
        match block_type:
            case BlockType.PARAGRAPH:
                sanitized_text = " ".join(block.splitlines())  # Join lines with spaces
                formatted_text = convert_inline_formatting(sanitized_text)  # Apply inline formatting
                html_nodes.append(LeafNode("p", formatted_text))  # Wrap the formatted text directly
            case BlockType.HEADING:
                match = re.match(r"^(#{1,6})\s+(.*)", block)
                if match:
                    level = len(match.group(1))
                    tag = f"h{level}"
                    text = match.group(2).strip()
                    html_nodes.append(LeafNode(tag, text))
                else:
                    print(f"Malformed heading treated as paragraph: {block}")
                    html_nodes.append(LeafNode("p", block.strip()))
            case BlockType.CODE:
                if block.startswith("```") and block.endswith("```"):
                    lines = block.split("\n")
                    if len(lines) > 2:
                        code_content = "\n".join(lines[1:-1]).strip()
                    else:
                        print(f"Warning: Empty code block found: {block}")
                        continue
                else:
                    print(f"Malformed code block skipped: {block}")
                    continue

                pre_node = ParentNode("pre", [LeafNode("code", code_content)])
                html_nodes.append(pre_node)
            case BlockType.QUOTE:
                # Split the block into lines and pass it to process_nested_quotes
                stripped_lines = [line for line in block.split("\n") if line.strip()]
                nested_quote_nodes = process_nested_quotes(stripped_lines)

                # Extend the main HTML nodes list with the blockquote nodes
                html_nodes.extend(nested_quote_nodes)
            case BlockType.UNORDERED_LIST:
                lines = [line for line in block.split("\n") if line.strip()]
                nested_ul = parse_nested_list(lines, is_ordered=False)  # Default is False, but explicit is good
                html_nodes.append(nested_ul)  # Add the resulting node
            case BlockType.ORDERED_LIST:
                lines = [line for line in block.split("\n") if line.strip()]  # Extract non-empty lines
                nested_ol = parse_nested_list(lines, is_ordered=True)  # Explicitly pass is_ordered=True
                html_nodes.append(nested_ol)
    
    parent_node = ParentNode("div", html_nodes)

    return parent_node


lines = [
    "* Item 1",
    "  * Subitem 1.1",
    "  * Subitem 1.2",
    "    * Sub-subitem 1.2.1",
    "* Item 2"
]

root = parse_nested_list(lines)

def extract_title(markdown):
    # Use regex to find the first valid h1 header (exactly one # followed by whitespace)
    match = re.search(r'^#\s+(.+)$', markdown, re.MULTILINE)
    
    if match:
        # Return the captured group, stripping any leading/trailing whitespace
        return match.group(1).strip()
    else:
        # Raise an exception if no valid h1 header is found
        raise ValueError("No h1 header found in the markdown content")
    

def generate_page(from_path, template_path, dest_path):
    # Print generation message
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read markdown content
    with open(from_path, 'r', encoding='utf-8') as md_file:
        markdown = md_file.read()
    
    # Read template file
    with open(template_path, 'r', encoding='utf-8') as template_file:
        template = template_file.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown)
    html_content = html_node.to_html()
    
    # Extract title from markdown
    title = extract_title(markdown)
    
    # Replace template placeholders
    final_html = template.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    
    # Create destination directory if needed
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Write generated HTML to destination
    with open(dest_path, 'w', encoding='utf-8') as html_file:
        html_file.write(final_html)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):

    
    for filename in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, filename)
        dest_path = os.path.join(dest_dir_path, filename)
        if os.path.isfile(from_path):
            dest_path = Path(dest_path).with_suffix(".html")
            generate_page(from_path, template_path, dest_path)
        else:
            generate_pages_recursive(from_path, template_path, dest_path)