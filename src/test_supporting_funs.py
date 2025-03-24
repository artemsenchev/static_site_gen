from supporting_funcs import split_nodes_delimiter
from supporting_funcs import extract_markdown_images
from supporting_funcs import extract_markdown_links
from supporting_funcs import split_nodes_image
from supporting_funcs import split_nodes_links
from supporting_funcs import text_to_textnodes
from supporting_funcs import markdown_to_blocks
from supporting_funcs import block_to_block_type, BlockType
from supporting_funcs import markdown_to_html_node
from textnode import TextNode, TextType
from supporting_funcs import extract_title
import unittest
from htmlnode import text_node_to_html_node
from htmlnode import LeafNode
from htmlnode import ParentNode

class TestSplitNodes(unittest.TestCase):
    def test_split_nodes_delimiter(self):
        # Test splitting a single TextNode with a delimiter
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        
        # Check the length of the new nodes
        self.assertEqual(len(new_nodes), 3)
        
        # Check the text and type of each new node
        self.assertEqual(new_nodes[0].text, "This is text with a ")
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        
        self.assertEqual(new_nodes[1].text, "code block")
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        
        self.assertEqual(new_nodes[2].text, " word")
        self.assertEqual(new_nodes[2].text_type, TextType.TEXT)


    def test_extract_markdown_images(self):
        # Test extracting markdown images from text
        text = "This is an image ![alt text](image_url) and some text."
        images = extract_markdown_images(text)
        
        # Check the length of the extracted images
        self.assertEqual(len(images), 1)
        
        # Check the content of the extracted image
        self.assertEqual(images[0], ("alt text", "image_url"))

    def test_extract_markdown_links(self):
        # Test extracting markdown links from text
        text = "This is a link [link text](link_url) and some text."
        links = extract_markdown_links(text)
        
        # Check the length of the extracted links
        self.assertEqual(len(links), 1)
        
        # Check the content of the extracted link
        self.assertEqual(links[0], ("link text", "link_url"))


    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://example.com) and another [second link](https://example.com/2)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_links([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://example.com/2"),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        # Test with plain text
        text = "This is plain text."
        nodes = text_to_textnodes(text)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text, "This is plain text.")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        
        # Test with bold text
        text = "This is **bold** text."
        nodes = text_to_textnodes(text)
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].text, "This is ")
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[1].text, "bold")
        self.assertEqual(nodes[1].text_type, TextType.BOLD)
        self.assertEqual(nodes[2].text, " text.")
        self.assertEqual(nodes[2].text_type, TextType.TEXT)
        
        # Test with multiple markdown features
        text = "This is **bold** and _italic_ text with a [link](https://example.com)."
        nodes = text_to_textnodes(text)
        # Add assertions to check each node
    
    def test_markdown_to_blocks(self):
        md = """
    This is **bolded** paragraph

    This is another paragraph with _italic_ text and `code` here
    This is the same paragraph on a new line

    - This is a list
    - with items
    """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type(self):
        # Test with a paragraph
        block = "This is a paragraph."
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.PARAGRAPH)

        # Test with an unordered list
        block = "- Item 1\n- Item 2"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.UNORDERED_LIST)

        # Test with a heading
        block = "# This is a heading"
        block_type = block_to_block_type(block)
        self.assertEqual(block_type, BlockType.HEADING)

        # You can add more tests for other block types...

    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    # def test_codeblock(self):
    #         md = """
    #     ```
    #     This is text that _should_ remain
    #     the **same** even with inline stuff
    #     ```
    #     """

    #         node = markdown_to_html_node(md)
    #         html = node.to_html()
    #         self.assertEqual(
    #             html,
    #             "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
    #         )

    # def test_empty_input(self):
    #     md = ""
    #     node = markdown_to_html_node(md)
    #     html = node.to_html()
    #     assert html == "<div></div>", f"Unexpected result: {html}"

    # def test_single_line_para(self):
    #     md = "This is a single line."
    #     node = markdown_to_html_node(md)
    #     html = node.to_html()
    #     assert html == "<div><p>This is a single line.</p></div>", f"Unexpected result: {html}"

    # def test_handle_headings(self):
    #     md = """
    # # Heading 1
    # ## Heading 2
    # ### Heading 3
    # """
    #     node = markdown_to_html_node(md)
    #     html = node.to_html()
    #     assert html == "<div><h1>Heading 1</h1><h2>Heading 2</h2><h3>Heading 3</h3></div>", f"Unexpected result: {html}"

    # def test_handle_lists(self):
    #     # Unordered List
    #     md_ul = """
    # - Item 1
    # - Item 2
    # """
    #     node_ul = markdown_to_html_node(md_ul)
    #     html_ul = node_ul.to_html()
    #     assert html_ul == "<div><ul><li>Item 1</li><li>Item 2</li></ul></div>", f"Unexpected result: {html_ul}"

    #     # Ordered List
    #     md_ol = """
    # 1. First
    # 2. Second
    # """
    #     node_ol = markdown_to_html_node(md_ol)
    #     html_ol = node_ol.to_html()
    #     assert html_ol == "<div><ol><li>First</li><li>Second</li></ol></div>", f"Unexpected result: {html_ol}"

    # def test_nested_lists(self):
    #     md = """
    # - Item 1
    # - Subitem 1.1
    # - Subitem 1.2
    #     - Sub-subitem 1.2.1
    # - Item 2
    # """

    #     node = markdown_to_html_node(md)
    #     html = node.to_html()
    #     assert html == (
    #         "<div>"
    #         "<ul>"
    #         "<li>Item 1<ul>"
    #         "<li>Subitem 1.1</li>"
    #         "<li>Subitem 1.2<ul>"
    #         "<li>Sub-subitem 1.2.1</li>"
    #         "</ul></li>"
    #         "</ul></li>"
    #         "<li>Item 2</li>"
    #         "</ul>"
    #         "</div>"
    #    ), f"Unexpected result: {html}"

    def test_extract_title(self):
        # Test with a basic title
        md = "# This is a title"
        title = extract_title(md)
        self.assertEqual(title, "This is a title")

        # Test with leading/trailing spaces in the title
        md = "#    Spaced out title   "
        title = extract_title(md)
        self.assertEqual(title, "Spaced out title")
        
        # Test with a title that has special characters
        md = "# Title with *formatting* and [links](https://example.com)"
        title = extract_title(md)
        self.assertEqual(title, "Title with *formatting* and [links](https://example.com)")
        
        # Test with title not on the first line
        md = "Some text here\n\n# Title in the middle\n\nMore text"
        title = extract_title(md)
        self.assertEqual(title, "Title in the middle")
        
        # Test with multiple h1 headers (should grab the first one)
        md = "# First title\n\nSome text\n\n# Second title"
        title = extract_title(md)
        self.assertEqual(title, "First title")

        # Test with an h2 header but no h1 header
        md = "## This is an h2 header"
        with self.assertRaises(ValueError):
            extract_title(md)

        # Test with no title - should raise an exception
        md = "This is just text."
        with self.assertRaises(ValueError):
            extract_title(md)
            
        # Test with empty string
        md = ""
        with self.assertRaises(ValueError):
            extract_title(md)

if __name__ == "__main__":
    unittest.main()
