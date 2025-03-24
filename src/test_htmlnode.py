import unittest
from htmlnode import HTMLNode
from htmlnode import LeafNode
from htmlnode import ParentNode
from textnode import TextNode
from htmlnode import text_node_to_html_node
from textnode import TextType

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_empty(self):
        # Test props_to_html with empty props
        node = HTMLNode("div", "Hello, world!")
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_single_prop(self):
        # Test props_to_html with a single prop
        node = HTMLNode("div", "Hello, world!", None, {"class": "container"})
        self.assertEqual(node.props_to_html(), ' class="container"')

    def test_props_to_html_multiple_props(self):
        # Test props_to_html with multiple props
        node = HTMLNode("a", "Click me!", None, {"href": "https://www.google.com", "target": "_blank"})
        # The order of props might be different, so we need to check each part separately
        result = node.props_to_html()
        self.assertIn(' href="https://www.google.com"', result)
        self.assertIn(' target="_blank"', result)
        self.assertEqual(len(result.strip().split()), 2)  # Should have exactly 2 props

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        node1 = LeafNode("p", "Hello, world!", {"class": "text"})
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
        self.assertEqual(node.props_to_html(), "")
        self.assertEqual(node1.to_html(), '<p class="text">Hello, world!</p>')
        self.assertEqual(node1.props_to_html(), ' class="text"')

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")



    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(
            parent_node.to_html(),
            '<div class="container"><span>child</span></div>',
        )

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

if __name__ == "__main__":
    unittest.main()