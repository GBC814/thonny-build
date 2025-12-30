import tkinter as tk
from tkinter import font
import os
import tempfile
from thonny import get_workbench
from thonny.languages import tr

# Constants
INDENT_GUIDE_TAG = "indent_guide"

class IndentGuidesPlugin:
    def __init__(self):
        self.workbench = get_workbench()
        self.workbench.set_default("view.show_indent_guides", True)
        self.workbench.set_default("view.indent_guide_color", "lightgray")
        
        self._stipple_files = []
        self._font_width = 0
        # Keep reference to temp dir to prevent cleanup
        self._temp_dir = tempfile.TemporaryDirectory(prefix="thonny_indent_guides_")
        
        # Add menu item
        self.workbench.add_command(
            command_id="show_indent_guides",
            menu_name="edit",
            command_label=tr("Show indentation guides"),
            flag_name="view.show_indent_guides",
            handler=self._toggle_indent_guides,
            group=49
        )
        
        # Listen for editor creation
        self.workbench.bind("EditorTextCreated", self._on_editor_created, True)
        self.workbench.bind("SyntaxThemeChanged", self._on_theme_changed, True)
        
        # Initial setup if editors exist
        self.workbench.bind("WorkbenchInitialized", self._on_workbench_initialized, True)

    def _toggle_indent_guides(self):
        var = get_workbench().get_variable("view.show_indent_guides")
        var.set(not var.get())
        self._update_all_editors()

    def _on_workbench_initialized(self, event=None):
        self._update_stipples()
        self._update_all_editors()

    def _on_editor_created(self, event):
        text = event.text_widget
        
        # Bind events
        text.bind("<<TextChange>>", self._on_text_change, True)
        text.bind("<Configure>", self._on_configure, True)
        
        # Hook into scrolling
        text.bind("<<CursorMove>>", self._check_scroll_alignment, True)
        
        # Apply initial tags
        self._update_text_tags(text)
        self._update_tag_config(text)

    def _on_theme_changed(self, event=None):
        self._update_stipples()
        self._update_all_editors()

    def _update_all_editors(self, event=None):
        try:
            notebook = self.workbench.get_editor_notebook()
        except AssertionError:
            # Editor notebook might not be initialized yet (e.g. during startup theme reload)
            return

        if not notebook:
            return
            
        for editor in notebook.get_all_editors():
            text = editor.get_text_widget()
            self._update_tag_config(text)
            self._update_text_tags(text)

    def _update_stipples(self):
        # Measure font width
        f = font.nametofont("EditorFont")
        width = f.measure(" ")
        if width <= 0: width = 8 
        
        if width == self._font_width and self._stipple_files:
            return

        self._font_width = width
        self._stipple_files = []
        
        # Generate XBM files
        for i in range(width):
            # We want a vertical line at the 0th pixel (left edge)
            # But we are placing it on a character that might be shifted by x pixels
            # The stipple aligns to screen origin.
            # So if character starts at x, we need bit (x % width) set?
            # Wait, if we want the line at the LEFT of the character space:
            # The line should be at x.
            # Stipple at x should be 1.
            # So bit (x % width) should be 1.
            # Yes.
            
            num_bytes = (width + 7) // 8
            row_bytes = [0] * num_bytes
            
            # Use 2-pixel wide line as requested by user
            for offset in range(2):
                curr_bit = (i + offset) % width
                byte_idx = curr_bit // 8
                bit_idx = curr_bit % 8
                row_bytes[byte_idx] |= (1 << bit_idx)
            
            hex_bytes = ", ".join([f"0x{b:02x}" for b in row_bytes])
            
            content = f"""
#define stipple_width {width}
#define stipple_height 1
static char stipple_bits[] = {{ {hex_bytes} }};
"""
            filename = os.path.join(self._temp_dir.name, f"guide_{i}.xbm")
            with open(filename, "w") as f:
                f.write(content)
            self._stipple_files.append(filename)

    def _check_scroll_alignment(self, event):
        text = event.widget
        self._update_tag_config(text)

    def _on_configure(self, event):
        text = event.widget
        self._update_tag_config(text)

    def _on_text_change(self, event):
        text = event.widget
        self._update_text_tags(text)
        self._update_tag_config(text)

    def _update_tag_config(self, text):
        if not get_workbench().get_option("view.show_indent_guides"):
            text.tag_configure(INDENT_GUIDE_TAG, background="", bgstipple="")
            return

        try:
            dline = text.dlineinfo("1.0")
            if dline is None:
                return
            
            x = dline[0]
            stipple_idx = x % self._font_width
            if 0 <= stipple_idx < len(self._stipple_files):
                stipple_file = self._stipple_files[stipple_idx]
                
                # Determine color
                color = get_workbench().get_option("view.indent_guide_color")
                try:
                    if color == "lightgray":
                        # Try to get from theme settings
                        syntax_options = getattr(text, "_syntax_options", {})
                        if (
                            "indent_guide" in syntax_options
                            and "foreground" in syntax_options["indent_guide"]
                        ):
                            color = syntax_options["indent_guide"]["foreground"]
                        elif "GUTTER" in syntax_options and "foreground" in syntax_options["GUTTER"]:
                            # Gutter foreground is usually a good proxy for indent guides
                            color = syntax_options["GUTTER"]["foreground"]
                        else:
                            # Fallback calculation
                             bg_rgb = text.winfo_rgb(text.cget("background"))
                             fg_rgb = text.winfo_rgb(text.cget("foreground"))

                             # Blend BG and FG (40% FG, 60% BG) for high contrast visibility
                             # ensuring guides are clearly visible in any custom theme
                             ratio = 0.4
                             r = int(bg_rgb[0] * (1 - ratio) + fg_rgb[0] * ratio)
                             g = int(bg_rgb[1] * (1 - ratio) + fg_rgb[1] * ratio)
                             b = int(bg_rgb[2] * (1 - ratio) + fg_rgb[2] * ratio)
                             color = "#%02x%02x%02x" % (r >> 8, g >> 8, b >> 8)
                except:
                    pass

                text.tag_configure(INDENT_GUIDE_TAG, 
                                   background=color, 
                                   bgstipple=f"@{stipple_file}",
                                   foreground="") 
        except Exception:
            pass

    def _update_text_tags(self, text):
        if not get_workbench().get_option("view.show_indent_guides"):
            text.tag_remove(INDENT_GUIDE_TAG, "1.0", "end")
            return

        content = text.get("1.0", "end")
        lines = content.splitlines()
        
        indent_width = get_workbench().get_option("edit.indent_width")
        if not indent_width: indent_width = 4
        
        text.tag_remove(INDENT_GUIDE_TAG, "1.0", "end")
        
        for i, line in enumerate(lines):
            lineno = i + 1
            leading_spaces = 0
            for char in line:
                if char == ' ':
                    leading_spaces += 1
                elif char == '\t':
                    # Stop at tab for now
                    break
                else:
                    break
            
            if leading_spaces > 0:
                # Draw guides at indent levels
                for col in range(0, leading_spaces, indent_width):
                    # We skip the 0th column if we don't want a line at the very left edge
                    # PyCharm usually shows lines for nested blocks.
                    # The line at column 0 corresponds to top-level. 
                    # Usually we want lines at 4, 8, etc.
                    # But the user picture shows lines.
                    # Let's include 0 for now as it helps visually.
                    index = f"{lineno}.{col}"
                    text.tag_add(INDENT_GUIDE_TAG, index)

_plugin_instance = None

def load_plugin():
    global _plugin_instance
    _plugin_instance = IndentGuidesPlugin()
