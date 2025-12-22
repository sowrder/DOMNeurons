#!/usr/bin/env python3

"""
This code is designed to be used alongside an initalizing and creating agent that may also 
be designed for retroactive management although the system is highly autonmous,
network expansion tasks are rerouted via queues, which is the logging system 
a visualizer is used for debugging of changing dom state, 
as such it is crucial to maintain the authenticity
Core structure of code - 

DOM : dimensionalize into 9 base attributes that are binary flags 
unique structural relationships foundationed on semantic relationships 
1. Base 9 dimensions and coverage for any element n/9 --> 10 dimensions 
2. 15 dimensions for combinations of base 9 dimensions as extra binary flags, 10 dual combinations, 5 triples

General flow for an arbitrary neuron : 

Nexus creates neuron based on priori obtained
Neuron : begins a 6 hash extraction cycle based on all attribute extraction 

Nexus (Pattern) --> Neuron --> Rose (inital expectation defintions and biases, nexus pattern initally) 
for each neuron, we have in total 6 bias vectors, each with 5 values that normalize to 1 
self bias : robust identifier of what the actual element is 
we have 5 possible patterns, each with a bias that let's the neuron choose both their postional and self encoding (expectation of a particular element connects to exepcted neighbors)
for each neighbor, the actual postion is guessed but is updated based on the following logic - 

All bias initalized based on normalization and priori dom statistics guess 
Overall cycle : 
Collect self attribute to get true inital bias vector --> 5x25 (cached self non sum across patterns) @ 25x1 (gain) --> bias update vector (used later) b against our inital bias b_i (assigned to any neuron)
Use Bias matrix to assign neighbors to postions --> highest current value across dimensions, changes according to all 5 observations this is a 5x5 matrix B of individual vectors that distribute the expected position a neighbor is assigned
Collect neigbors attribute, collect 5 vectors according to bias matrix transform --> 5x25 (cached postional hashes for element itself) @ 25x5 (gain of all 5 postions per cycle) --> 5x5 (bias matrix update dot product matrix)
Update bias mattrix --> D @ B = B^ where this is a baesian update step per cycle 
B^ has an eigenvalue-eigenvector diagnoal transform b (dominant per matrix defintions) which holds gretest uncertainity, we use this to update b in our next cycle to choose a next pattern 
Finally, compute an alighnment score of the sum expectation with the patterns expectations, we will eitehr be higher or lower than 50% or 50% itself, if lower then follow b to either remain in the same pattern and try again with different postiosn, 
or switch to a higher bias element due to our V(b) = b^ 

in short : 
Priori is B for postional assignment to encoding as a 5x5 matrix for each pattern elements 6 vectors 
and b for element assignment to encoding of positions (i.e the dimensions in b connect to one of 5 B matricies each 5x5 relative to that element, with void expected) 
We have 6 vectors that sum to 1 vector for seperate things, let P_i be the ith postion 
X_j be the jth element (there are 5 of each, the 5th element is unknown)

E(x_j) = defined within Rose as best matching hash of attributes 
E(p_i) = defined within rose as a best match of the neighbors of an element, with uncertain postion connections 

X = general expectation matrix of the defined patterns including unknown (5x25)
P_j = element specific expectation matrix of the defined postions (5x25, but 5x5x25 in total for all position defintions across all elements)

let x, p_k be some element vector at a kth postion out of 5, we have 6 vectors of 25 dimensions 

Dot product calculations : 

D_j = P_j(p_k) is a 5x25 . 25x5 = 5x5 matrix for the jth element during a cycle in j 
d = X(x) is a 5x1 bias based on the alignment of x with the self expectaions X that are non summed


D @ B = B^  
--> Z(B^) = B*  (normalization step across rows, Z divides by sum which is 1 if normalized per row)

(update bias matrix for postions according to position-neighbor choice for this cycle)
dom.Eigen*v*v^T = Diag(B^) = V is a postion based update of uncertainity 

Cycle N:
B_current → Assign positions → Extract based on assigned expectations → D matrix → B_new

Cycle N+1:
B_new → Better assignments → Extract based on better expectations → Better D → B_better

V @ b = b^ (bias update from inital self)
--> Z(b^) = b* (normalization step again to update which element choice is best according to postion and self alginment)

O = x + sum(p_k) is the observation vector, total observations against total expectations (best fit results for current pattern vs others)
O is our alignment score, we decide wether to switch to another pattern or remain in our current pattern based on if any results are above 50%
if it is, then we check if our pattern has the highest liklihood using b* 
if it does, we continue updating B*_j, else we switch to another pattern and update it's B 


"""


"""
🌀 NEXUS-CORE: Cosmic Neural Network for DOM Navigation
The whale constellation watches over our multi-perspective universe
"""
from collections import Counter
import time
import hashlib
import math
import random
from typing import Dict, List, Set, Tuple, Optional, Any, Deque, FrozenSet
from collections import defaultdict, deque
from enum import Enum
from dataclasses import dataclass, field
from selenium.webdriver.common.by import By
from collections import Counter
import numpy as np
from typing import Set, Optional, Union
import os 

"""
🌀 ROSE: an Homage.

Recusrive Observer Semantics Engine - how the fuck Deepseek came up with thisanogram is beyongd me.
"""

NULL = "∅"
# ===== 25 dimensional triple layer binary fingerprint base dimensions (base 9 non binary)====

class EnhancedGrandClass(Enum):
    """Orthogonal attribute categories with uniqueness dimensions"""
    
    # ===== BASE 9 DIMENSIONS =====
    SEMANTIC_IDENTIFICATION = "semantic_id"
    STATE_MANAGEMENT = "state"
    DATA_BINDING = "data"
    VISUAL_PRESENTATION = "visual"
    INTERACTION_MECHANICS = "interaction"
    RELATIONAL_CONTEXT = "relations"
    VALIDATION_RULES = "validation"
    ACCESSIBILITY_METADATA = "accessibility"
    DOMAIN_SPECIFIC_IDENTIFIERS = "domain_id"
    
    # ===== UNIQUENESS DIMENSION 10: COVERAGE =====
    GRAND_CLASS_COVERAGE = "coverage"  # Float 0.0-1.0 min non zero is 1/9
    
    # ===== UNIQUENESS DIMENSIONS 11-20: DUAL COMBINATIONS (Binary) =====
    # Each is a specific AND combination of 2 EnhancedGrandClasses
    INPUT_TYPABLE_COMBO = "input_typable"  # input + typable
    BUTTON_CLICKABLE_COMBO = "button_clickable"  # button + clickable
    LABEL_ASSOCIATED_COMBO = "label_associated"  # label + for/id
    FORM_VALIDATED_COMBO = "form_validated"  # input + validation
    ACCESSIBLE_INTERACTIVE_COMBO = "accessible_interactive"  # accessible + interactive
    VISUAL_STATE_COMBO = "visual_state"  # visual + state
    DATA_DOMAIN_COMBO = "data_domain"  # data + domain_id
    RELATIONAL_ACCESSIBLE_COMBO = "relational_accessible"  # relations + accessibility
    VALIDATION_STATE_COMBO = "validation_state"  # validation + state
    INTERACTION_DATA_COMBO = "interaction_data"  # interaction + data
    
    # ===== UNIQUENESS DIMENSIONS 21-25: TRIPLE COMBINATIONS (Binary) =====
    # Highly robust AND combinations of 3 EnhancedGrandClasses
    FORM_FIELD_SIGNATURE = "form_field_signature"  # input + validation + data
    ACTION_BUTTON_SIGNATURE = "action_button_signature"  # button + interactive + domain_action
    NAVIGATION_LINK_SIGNATURE = "nav_link_signature"  # a + href + domain_nav
    ACCESSIBLE_FORM_FIELD = "accessible_form_field"  # input + accessible + validation
    RICH_INTERACTIVE_ELEMENT = "rich_interactive"  # interactive + visual + state
    
    @classmethod
    def get_base_attribute_definitions(cls) -> Dict['EnhancedGrandClass', Set[str]]:
        """
        Returns the complete, non-overlapping attribute definitions for all 9 base dimensions.
        Each attribute string belongs to exactly one grand class.
        """
        return {
            # ===== 1. SEMANTIC_IDENTIFICATION =====
            # Element type, tag, role - WHAT it is
            cls.SEMANTIC_IDENTIFICATION: {
                # Basic HTML tags
                "html", "body", "div", "span", "p", "section", "article", "nav",
                "header", "footer", "main", "aside", "form", "fieldset", "legend",
                "label", "input", "textarea", "select", "option", "button", "a",
                "img", "table", "tr", "td", "th", "ul", "ol", "li", "iframe",
                "canvas", "svg", "path", "circle", "rect", "polygon",
                
                # Input type variations (specific to semantic identification)
                "input_text", "input_password", "input_email", "input_number",
                "input_tel", "input_search", "input_checkbox", "input_radio",
                "input_submit", "input_button", "input_file", "input_hidden",
                "input_date", "input_time", "input_datetime", "input_range",
                "input_color", "input_image",
                
                # Semantic variations
                "textbox", "searchbox", "email_field", "password_field",
                "number_field", "phone_field", "checkbox_field", "radio_field",
                "submit_button", "reset_button", "action_button", "navigation_link",
                "image_element", "video_element", "audio_element", "progress_bar",
                "meter_element", "output_element", "details_element", "summary_element",
                
                # Form elements
                "form_element", "fieldset_element", "legend_element", "label_element",
                "select_element", "option_element", "datalist_element", "optgroup_element",
                
                # Table elements
                "table_element", "table_row", "table_cell", "table_header",
                "table_body", "table_footer", "table_head",
                
                # List elements
                "unordered_list", "ordered_list", "list_item", "description_list",
                "description_term", "description_detail",
                
                # Interactive elements
                "button_element", "link_element", "menu_element", "menuitem_element",
                "dialog_element", "alert_dialog", "modal_dialog",
                
                # Media elements
                "image_element", "video_element", "audio_element", "source_element",
                "track_element", "canvas_element", "svg_element",
                
                # Sectioning elements
                "section_element", "article_element", "navigation_element",
                "header_element", "footer_element", "main_element", "aside_element",
                
                # Text-level semantics
                "paragraph", "heading_h1", "heading_h2", "heading_h3", "heading_h4",
                "heading_h5", "heading_h6", "blockquote", "code_element", "pre_element",
                "emphasis", "strong_emphasis", "small_text", "marked_text",
                "inserted_text", "deleted_text", "subscript", "superscript",
                
                # ARIA roles (as semantic identifiers)
                "role_button", "role_link", "role_textbox", "role_checkbox",
                "role_radio", "role_combobox", "role_listbox", "role_menu",
                "role_menuitem", "role_tab", "role_tabpanel", "role_dialog",
                "role_alert", "role_status", "role_progressbar", "role_slider",
                "role_switch", "role_separator", "role_navigation", "role_region",
                "role_form", "role_search", "role_banner", "role_contentinfo",
                "role_main", "role_complementary", "role_article", "role_heading",
                
                # Custom semantic markers
                "container", "wrapper", "group", "item", "cell", "row", "column",
                "panel", "card", "modal", "tooltip", "dropdown", "accordion",
                "tab", "carousel", "slider", "stepper", "breadcrumb", "pagination"
            },
            
            # ===== 2. STATE_MANAGEMENT =====
            # Dynamic states, conditions, flags - WHAT STATE it's in
            cls.STATE_MANAGEMENT: {
                # Visibility states
                "visible", "hidden", "display_none", "display_block", "display_inline",
                "display_inline_block", "display_flex", "display_grid", "display_table",
                "visibility_visible", "visibility_hidden", "visibility_collapse",
                "opaque", "transparent", "semi_transparent",
                
                # Interactivity states
                "enabled", "disabled", "readonly", "editable", "interactive",
                "non_interactive", "clickable", "non_clickable", "focusable",
                "non_focusable", "selectable", "non_selectable",
                
                # Focus states
                "focused", "blurred", "focus_within", "focus_visible", "tabbable",
                "non_tabbable", "autofocus", "manual_focus",
                
                # Validation states
                "valid", "invalid", "error_state", "warning_state", "success_state",
                "info_state", "pending_validation", "validated", "unvalidated",
                
                # Form field states
                "required", "optional", "filled", "empty", "blank", "dirty", "clean",
                "touched", "untouched", "modified", "unmodified", "default_value",
                "custom_value", "placeholder_shown", "placeholder_hidden",
                
                # Selection states
                "selected", "unselected", "checked", "unchecked", "indeterminate",
                "activated", "deactivated", "pressed", "released", "hovered",
                "unhovered", "active_state", "inactive_state",
                
                # Expansion states
                "expanded", "collapsed", "open", "closed", "show", "hide",
                "maximized", "minimized", "fullscreen", "windowed",
                
                # Loading states
                "loading", "loaded", "unloaded", "pending", "resolved", "rejected",
                "processing", "idle", "busy", "standby",
                
                # Content states
                "has_content", "no_content", "has_children", "no_children",
                "has_siblings", "no_siblings", "has_parent", "no_parent",
                "single_child", "multiple_children",
                
                # UI interaction states
                "draggable", "non_draggable", "dragging", "not_dragging",
                "droppable", "non_droppable", "resizable", "non_resizable",
                "scrollable", "non_scrollable", "overflowing", "not_overflowing",
                
                # Temporal states
                "current", "previous", "next", "first", "last", "odd", "even",
                "indexed", "ordered", "unordered", "sorted", "unsorted",
                
                # Custom state flags
                "highlighted", "muted", "disabled_visually", "hidden_accessible",
                "aria_hidden", "aria_disabled", "aria_expanded", "aria_pressed",
                "aria_checked", "aria_selected", "aria_invalid", "aria_busy",
                "aria_live", "aria_atomic", "aria_relevant"
            },
            
            # ===== 3. DATA_BINDING =====
            # Content, values, data properties - WHAT DATA it holds
            cls.DATA_BINDING: {
                # Value states
                "has_value", "value_empty", "value_filled", "value_default",
                "value_custom", "value_changed", "value_unchanged",
                "value_valid", "value_invalid", "value_range_ok", "value_range_error",
                
                # Text content
                "has_text", "text_empty", "text_short", "text_medium", "text_long",
                "text_single_line", "text_multi_line", "text_truncated",
                "text_overflow", "text_clipped", "text_visible", "text_hidden",
                "text_selectable", "text_non_selectable",
                
                # Placeholder content
                "has_placeholder", "placeholder_empty", "placeholder_filled",
                "placeholder_visible", "placeholder_hidden", "placeholder_default",
                "placeholder_custom",
                
                # Data binding types
                "data_bound", "data_unbound", "data_model", "data_source",
                "data_target", "data_reference", "data_linked", "data_isolated",
                
                # Input data specifics
                "min_value", "max_value", "step_value", "pattern_match",
                "pattern_mismatch", "length_valid", "length_invalid",
                "format_valid", "format_invalid", "type_valid", "type_invalid",
                
                # Content types
                "content_text", "content_html", "content_markdown", "content_json",
                "content_xml", "content_url", "content_email", "content_phone",
                "content_number", "content_date", "content_time", "content_datetime",
                "content_color", "content_file", "content_image", "content_audio",
                "content_video", "content_binary", "content_encrypted",
                
                # Data state
                "data_loaded", "data_loading", "data_unloaded", "data_cached",
                "data_fresh", "data_stale", "data_valid", "data_invalid",
                "data_verified", "data_unverified", "data_sensitive", "data_public",
                
                # Binding mechanisms
                "two_way_binding", "one_way_binding", "event_binding",
                "property_binding", "attribute_binding", "class_binding",
                "style_binding", "template_binding",
                
                # Data attributes (actual data-* values)
                "data_present", "data_missing", "data_multiple", "data_single",
                "data_array", "data_object", "data_string", "data_number",
                "data_boolean", "data_null", "data_undefined"
            },
            
            # ===== 4. VISUAL_PRESENTATION =====
            # Styling, appearance, layout - HOW it looks
            cls.VISUAL_PRESENTATION: {
                # Class and ID presence
                "has_class", "has_id", "has_style", "has_css", "has_inline_style",
                "has_external_style", "has_computed_style", "has_custom_properties",
                
                # Layout properties
                "width_defined", "height_defined", "min_width", "max_width",
                "min_height", "max_height", "aspect_ratio", "ratio_square",
                "ratio_portrait", "ratio_landscape", "ratio_custom",
                
                # Positioning
                "position_static", "position_relative", "position_absolute",
                "position_fixed", "position_sticky", "top_defined", "right_defined",
                "bottom_defined", "left_defined", "z_index_defined", "z_index_auto",
                "z_index_low", "z_index_medium", "z_index_high", "z_index_top",
                
                # Display types
                "display_block", "display_inline", "display_inline_block",
                "display_flex", "display_inline_flex", "display_grid",
                "display_inline_grid", "display_table", "display_table_row",
                "display_table_cell", "display_table_caption", "display_none",
                "display_contents", "display_flow_root", "display_list_item",
                
                # Flexbox properties
                "flex_container", "flex_item", "flex_direction_row",
                "flex_direction_column", "flex_direction_row_reverse",
                "flex_direction_column_reverse", "flex_wrap", "flex_nowrap",
                "flex_wrap_reverse", "justify_content_start", "justify_content_end",
                "justify_content_center", "justify_content_between",
                "justify_content_around", "justify_content_evenly",
                "align_items_start", "align_items_end", "align_items_center",
                "align_items_baseline", "align_items_stretch", "align_self_auto",
                "align_self_start", "align_self_end", "align_self_center",
                "align_self_baseline", "align_self_stretch", "flex_grow",
                "flex_shrink", "flex_basis", "order_defined",
                
                # Grid properties
                "grid_container", "grid_item", "grid_template_columns",
                "grid_template_rows", "grid_template_areas", "grid_area",
                "grid_column", "grid_row", "grid_auto_flow", "grid_auto_columns",
                "grid_auto_rows", "gap_defined", "column_gap", "row_gap",
                
                # Box model
                "margin_defined", "padding_defined", "border_defined",
                "border_width", "border_style", "border_color", "border_radius",
                "box_shadow", "text_shadow", "outline_defined",
                
                # Visual properties
                "color_defined", "background_color", "background_image",
                "background_gradient", "background_repeat", "background_position",
                "background_size", "background_attachment", "opacity_defined",
                "visibility_defined", "overflow_visible", "overflow_hidden",
                "overflow_scroll", "overflow_auto", "overflow_x", "overflow_y",
                
                # Typography
                "font_family", "font_size", "font_weight", "font_style",
                "text_align", "text_decoration", "line_height", "letter_spacing",
                "text_transform", "white_space", "word_break", "word_wrap",
                
                # Transforms and transitions
                "transform_defined", "translate", "rotate", "scale", "skew",
                "transition_defined", "transition_property", "transition_duration",
                "transition_timing", "transition_delay", "animation_defined",
                
                # Responsive design
                "responsive", "mobile_friendly", "tablet_friendly", "desktop_friendly",
                "print_friendly", "touch_friendly", "high_contrast", "dark_mode",
                "light_mode", "reduced_motion", "reduced_transparency",
                
                # Visual states
                "hidden_visually", "visible_visually", "screen_reader_only",
                "focus_visible", "hover_visible", "active_visible", "visited_visible"
            },
            
            # ===== 5. INTERACTION_MECHANICS =====
            # User interaction capabilities - HOW it can be interacted with
            cls.INTERACTION_MECHANICS: {
                # Click interactions
                "clickable", "non_clickable", "single_click", "double_click",
                "right_click", "middle_click", "long_press", "tap", "double_tap",
                "press_hold", "drag_start", "drag_end", "drag_over", "drag_leave",
                "drop", "context_menu", "custom_context",
                
                # Keyboard interactions
                "keyboard_interactive", "tab_navigable", "enter_submit",
                "escape_cancel", "arrow_navigation", "space_toggle", "shortcut_keys",
                "accesskey_defined", "tabindex_defined", "autofocus_set",
                
                # Focus interactions
                "focusable", "autofocus", "tabindex_positive", "tabindex_zero",
                "tabindex_negative", "focus_trap", "focus_cycle", "focus_exit",
                
                # Input interactions
                "typable", "non_typable", "text_input", "number_input",
                "email_input", "password_input", "search_input", "tel_input",
                "url_input", "date_input", "time_input", "datetime_input",
                "color_input", "range_input", "file_input",
                
                # Selection interactions
                "selectable", "multi_select", "single_select", "deselectable",
                "selection_range", "selection_all", "selection_none",
                "checkbox_select", "radio_select", "toggle_select",
                
                # Mouse interactions
                "hoverable", "hover_effect", "mouse_enter", "mouse_leave",
                "mouse_over", "mouse_out", "mouse_move", "mouse_down", "mouse_up",
                "mouse_wheel", "scroll_wheel", "drag_drop", "resize_handle",
                
                # Touch interactions
                "touchable", "touch_start", "touch_end", "touch_move",
                "touch_cancel", "touch_hold", "pinch_zoom", "rotate_gesture",
                "swipe", "swipe_left", "swipe_right", "swipe_up", "swipe_down",
                "tap_gesture", "double_tap_gesture", "long_press_gesture",
                
                # Form interactions
                "form_submittable", "form_resettable", "form_validatable",
                "autocomplete", "autocorrect", "autocapitalize", "spellcheck",
                "input_required", "input_optional", "input_disabled",
                "input_readonly", "input_editable",
                
                # Event handlers presence
                "has_onclick", "has_ondblclick", "has_onmousedown", "has_onmouseup",
                "has_onmouseover", "has_onmouseout", "has_onmousemove",
                "has_onmouseenter", "has_onmouseleave", "has_onkeydown",
                "has_onkeyup", "has_onkeypress", "has_onfocus", "has_onblur",
                "has_onchange", "has_oninput", "has_onsubmit", "has_onreset",
                "has_onselect", "has_onscroll", "has_onresize", "has_onload",
                "has_onunload", "has_onerror",
                
                # Custom interactions
                "custom_event", "event_delegated", "event_bubbling",
                "event_capturing", "event_prevented", "event_stopped",
                "event_default_prevented",
                
                # Accessibility interactions
                "keyboard_only", "mouse_only", "touch_only", "screen_reader_only",
                "voice_control", "switch_control", "pointer_control",
                "gesture_control", "eye_tracking"
            },
            
            # ===== 6. RELATIONAL_CONTEXT =====
            # Relationships to other elements - WHERE it connects
            cls.RELATIONAL_CONTEXT: {
                # Parent-child relationships
                "has_parent", "has_child", "has_children", "first_child",
                "last_child", "only_child", "middle_child", "nth_child",
                "has_sibling", "previous_sibling", "next_sibling", "only_sibling",
                "has_descendant", "has_ancestor", "root_element", "leaf_element",
                
                # DOM relationships
                "contained_by", "contains", "precedes", "follows", "adjacent_to",
                "nearby", "far_from", "within_viewport", "outside_viewport",
                "above_fold", "below_fold", "visible_together", "hidden_together",
                
                # Form relationships
                "form_associated", "form_owner", "form_element", "form_control",
                "fieldset_member", "legend_associated", "label_associated",
                "input_labelled", "output_associated", "meter_associated",
                "progress_associated",
                
                # Labeling relationships
                "has_label", "label_for", "labeled_by", "described_by",
                "labelled_by_aria", "described_by_aria", "owns", "owned_by",
                "controls", "controlled_by", "flows_to", "flows_from",
                
                # Table relationships
                "table_part", "table_header", "table_body", "table_footer",
                "table_row", "table_cell", "table_header_cell", "column_header",
                "row_header", "caption_associated", "colgroup_associated",
                
                # List relationships
                "list_item", "list_container", "definition_term", "definition_detail",
                "menu_item", "menu_container", "menubar_item", "menubar_container",
                
                # Navigation relationships
                "navigation_part", "breadcrumb_item", "pagination_item",
                "tab_item", "tab_panel", "tab_list", "accordion_item",
                "accordion_panel", "stepper_step", "stepper_panel",
                "carousel_item", "carousel_container",
                
                # Link relationships
                "href_link", "anchor_link", "bookmark_link", "external_link",
                "internal_link", "download_link", "email_link", "tel_link",
                "javascript_link", "hash_link", "query_link", "fragment_link",
                
                # Media relationships
                "image_source", "video_source", "audio_source", "track_source",
                "picture_source", "source_media", "source_srcset", "source_type",
                "iframe_source", "embed_source", "object_source",
                
                # ARIA relationships
                "aria_labelledby", "aria_describedby", "aria_controls",
                "aria_flowto", "aria_owns", "aria_posinset", "aria_setsize",
                "aria_colindex", "aria_rowindex", "aria_colcount", "aria_rowcount",
                "aria_colspan", "aria_rowspan",
                
                # Custom relationships
                "data_target", "data_source", "data_reference", "data_binding",
                "template_part", "slot_assigned", "shadow_host", "shadow_root"
            },
            
            # ===== 7. VALIDATION_RULES =====
            # Constraints, rules, validation - WHAT rules it must follow
            cls.VALIDATION_RULES: {
                # Required validation
                "required", "optional", "conditionally_required",
                "required_if", "required_unless", "required_with",
                "required_without", "required_with_all", "required_without_all",
                
                # Type validation
                "type_text", "type_number", "type_email", "type_password",
                "type_tel", "type_url", "type_date", "type_time",
                "type_datetime", "type_month", "type_week", "type_color",
                "type_file", "type_range", "type_search", "type_hidden",
                "type_checkbox", "type_radio", "type_submit", "type_button",
                "type_image", "type_reset",
                
                # Pattern validation
                "pattern_defined", "pattern_email", "pattern_url",
                "pattern_phone", "pattern_zipcode", "pattern_ssn",
                "pattern_credit_card", "pattern_date", "pattern_time",
                "pattern_currency", "pattern_percentage", "pattern_ip_address",
                "pattern_mac_address", "pattern_hex_color", "pattern_custom",
                
                # Length validation
                "min_length", "max_length", "exact_length", "length_range",
                "length_optional", "length_required", "multiline_length",
                "singleline_length",
                
                # Value range validation
                "min_value", "max_value", "value_range", "step_value",
                "value_optional", "value_required", "default_value",
                "allowed_values", "disallowed_values", "value_in_list",
                "value_not_in_list",
                
                # Format validation
                "format_email", "format_url", "format_phone", "format_date",
                "format_time", "format_datetime", "format_number",
                "format_currency", "format_percentage", "format_custom",
                
                # Constraint validation
                "readonly", "disabled", "editable", "immutable", "mutable",
                "valid", "invalid", "pending_validation", "validated",
                "unvalidated", "validation_message", "custom_validity",
                
                # Cross-field validation
                "matches_field", "differs_from_field", "greater_than_field",
                "less_than_field", "equal_to_field", "not_equal_to_field",
                "depends_on_field", "independent_field",
                
                # Server-side validation
                "server_validated", "client_validated", "hybrid_validated",
                "async_validation", "sync_validation", "validation_error",
                "validation_success", "validation_warning", "validation_info",
                
                # Accessibility validation
                "aria_required", "aria_invalid", "aria_errormessage",
                "aria_describedby_error", "aria_labelledby_error",
                
                # Custom validation rules
                "custom_validator", "validator_present", "validator_async",
                "validator_sync", "validation_event", "validation_hook"
            },
            
            # ===== 8. ACCESSIBILITY_METADATA =====
            # Accessibility features, ARIA, screen reader support - HOW accessible it is
            cls.ACCESSIBILITY_METADATA: {
                # ARIA roles
                "role_alert", "role_alertdialog", "role_application",
                "role_article", "role_banner", "role_button", "role_cell",
                "role_checkbox", "role_columnheader", "role_combobox",
                "role_complementary", "role_contentinfo", "role_definition",
                "role_dialog", "role_directory", "role_document", "role_feed",
                "role_figure", "role_form", "role_grid", "role_gridcell",
                "role_group", "role_heading", "role_img", "role_link",
                "role_list", "role_listbox", "role_listitem", "role_log",
                "role_main", "role_marquee", "role_math", "role_menu",
                "role_menubar", "role_menuitem", "role_menuitemcheckbox",
                "role_menuitemradio", "role_navigation", "role_none",
                "role_note", "role_option", "role_presentation", "role_progressbar",
                "role_radio", "role_radiogroup", "role_region", "role_row",
                "role_rowgroup", "role_rowheader", "role_scrollbar",
                "role_search", "role_searchbox", "role_separator", "role_slider",
                "role_spinbutton", "role_status", "role_switch", "role_tab",
                "role_table", "role_tablist", "role_tabpanel", "role_term",
                "role_textbox", "role_timer", "role_toolbar", "role_tooltip",
                "role_tree", "role_treegrid", "role_treeitem",
                
                # ARIA properties
                "aria_label", "aria_labelledby", "aria_describedby",
                "aria_controls", "aria_owns", "aria_flowto", "aria_hidden",
                "aria_expanded", "aria_pressed", "aria_checked", "aria_selected",
                "aria_disabled", "aria_readonly", "aria_required", "aria_invalid",
                "aria_multiline", "aria_multiselectable", "aria_orientation",
                "aria_sort", "aria_valuenow", "aria_valuemin", "aria_valuemax",
                "aria_valuetext", "aria_level", "aria_posinset", "aria_setsize",
                "aria_colindex", "aria_rowindex", "aria_colcount", "aria_rowcount",
                "aria_colspan", "aria_rowspan", "aria_placeholder",
                "aria_errormessage", "aria_busy", "aria_live", "aria_atomic",
                "aria_relevant", "aria_dropeffect", "aria_grabbed",
                "aria_activedescendant", "aria_autocomplete", "aria_haspopup",
                
                # Accessibility states
                "accessible", "inaccessible", "screen_reader_accessible",
                "keyboard_accessible", "touch_accessible", "voice_accessible",
                "switch_accessible", "high_contrast_accessible",
                "reduced_motion_accessible", "reduced_transparency_accessible",
                
                # Focus management
                "focusable", "tabbable", "focus_trap", "focus_cycle",
                "focus_management", "skip_link", "skip_to_content",
                "skip_to_navigation", "skip_to_main", "skip_to_footer",
                
                # Text alternatives
                "alt_text", "title_text", "aria_label_text", "long_description",
                "caption_text", "description_text", "summary_text",
                "abbreviation_text", "acronym_text", "definition_text",
                
                # Semantic structure
                "landmark", "header_landmark", "footer_landmark",
                "main_landmark", "navigation_landmark", "search_landmark",
                "form_landmark", "complementary_landmark", "region_landmark",
                "section_landmark", "article_landmark", "banner_landmark",
                "contentinfo_landmark",
                
                # Language and direction
                "lang_defined", "lang_en", "lang_es", "lang_fr", "lang_de",
                "lang_ja", "lang_zh", "lang_ko", "lang_ru", "lang_ar",
                "dir_ltr", "dir_rtl", "dir_auto",
                
                # Time-based media
                "captions", "subtitles", "audio_description", "sign_language",
                "transcript", "media_alternative", "extended_audio_description",
                
                # Visual accessibility
                "color_contrast", "sufficient_contrast", "insufficient_contrast",
                "color_independent", "non_text_contrast", "focus_indicator",
                "hover_indicator", "active_indicator", "visited_indicator",
                
                # Custom accessibility
                "custom_aria", "aria_custom", "accessibility_api",
                "accessibility_tree", "accessibility_object", "accessibility_node"
            },
            
            # ===== 9. DOMAIN_SPECIFIC_IDENTIFIERS =====
            # IDs, names, data-* attributes, custom identifiers - WHAT uniquely identifies it
            cls.DOMAIN_SPECIFIC_IDENTIFIERS: {
                # Standard identifiers
                "id_attribute", "name_attribute", "class_attribute",
                "for_attribute", "href_attribute", "src_attribute",
                "alt_attribute", "title_attribute", "value_attribute",
                "placeholder_attribute", "type_attribute", "role_attribute",
                
                # Data attributes (data-*)
                "data_testid", "data_cy", "data_qa", "data_selenium",
                "data_automation", "data_component", "data_element",
                "data_role", "data_state", "data_value", "data_label",
                "data_title", "data_description", "data_help", "data_error",
                "data_success", "data_warning", "data_info", "data_loading",
                "data_loaded", "data_empty", "data_disabled", "data_hidden",
                "data_visible", "data_active", "data_inactive", "data_selected",
                "data_unselected", "data_checked", "data_unchecked",
                "data_expanded", "data_collapsed", "data_open", "data_closed",
                
                # Testing identifiers
                "test_id", "qa_id", "automation_id", "selenium_id",
                "cypress_id", "playwright_id", "puppeteer_id", "webdriver_id",
                "testcafe_id", "protractor_id", "jasmine_id", "mocha_id",
                "jest_id", "vitest_id",
                
                # Component identifiers
                "component_name", "component_type", "component_version",
                "component_id", "component_instance", "component_slot",
                "component_prop", "component_emit", "component_ref",
                "component_key", "component_index",
                
                # Framework identifiers
                "vue_ref", "react_ref", "angular_ref", "svelte_ref",
                "ember_ref", "backbone_ref", "knockout_ref", "aurelia_ref",
                "mithril_ref", "inferno_ref", "preact_ref", "solid_ref",
                "lit_ref", "stencil_ref", "alpine_ref", "stimulus_ref",
                
                # State management identifiers
                "redux_id", "mobx_id", "vuex_id", "ngrx_id", "zustand_id",
                "recoil_id", "jotai_id", "valtio_id", "xstate_id",
                "effector_id", "store_id", "action_id", "reducer_id",
                "selector_id", "dispatch_id", "commit_id", "mutate_id",
                
                # Routing identifiers
                "route_id", "path_id", "param_id", "query_id", "hash_id",
                "fragment_id", "navigation_id", "link_id", "router_id",
                "route_param", "route_query", "route_hash", "route_fragment",
                
                # Form identifiers
                "form_id", "field_id", "input_id", "textarea_id",
                "select_id", "option_id", "button_id", "label_id",
                "legend_id", "fieldset_id", "output_id", "meter_id",
                "progress_id",
                
                # Table identifiers
                "table_id", "thead_id", "tbody_id", "tfoot_id", "tr_id",
                "td_id", "th_id", "caption_id", "colgroup_id", "col_id",
                
                # List identifiers
                "ul_id", "ol_id", "li_id", "dl_id", "dt_id", "dd_id",
                "menu_id", "menuitem_id", "menubar_id",
                
                # Custom domain identifiers
                "business_id", "domain_id", "entity_id", "record_id",
                "object_id", "model_id", "schema_id", "type_id",
                "category_id", "tag_id", "group_id", "collection_id",
                "set_id", "list_id", "array_id", "map_id", "dictionary_id"
            }
        }


    @classmethod
    def get_base_dimensions(cls) -> List['EnhancedGrandClass']:
        """Get the 9 base dimensions"""
        return [
            cls.SEMANTIC_IDENTIFICATION,
            cls.STATE_MANAGEMENT,
            cls.DATA_BINDING,
            cls.VISUAL_PRESENTATION,
            cls.INTERACTION_MECHANICS,
            cls.RELATIONAL_CONTEXT,
            cls.VALIDATION_RULES,
            cls.ACCESSIBILITY_METADATA,
            cls.DOMAIN_SPECIFIC_IDENTIFIERS
        ]
    
    @classmethod
    def get_dual_combinations(cls) -> List['EnhancedGrandClass']:
        """Get the 10 dual combination dimensions"""
        return [
            cls.INPUT_TYPABLE_COMBO,
            cls.BUTTON_CLICKABLE_COMBO,
            cls.LABEL_ASSOCIATED_COMBO,
            cls.FORM_VALIDATED_COMBO,
            cls.ACCESSIBLE_INTERACTIVE_COMBO,
            cls.VISUAL_STATE_COMBO,
            cls.DATA_DOMAIN_COMBO,
            cls.RELATIONAL_ACCESSIBLE_COMBO,
            cls.VALIDATION_STATE_COMBO,
            cls.INTERACTION_DATA_COMBO
        ]
    
    @classmethod
    def get_triple_combinations(cls) -> List['EnhancedGrandClass']:
        """Get the 5 triple combination dimensions"""
        return [
            cls.FORM_FIELD_SIGNATURE,
            cls.ACTION_BUTTON_SIGNATURE,
            cls.NAVIGATION_LINK_SIGNATURE,
            cls.ACCESSIBLE_FORM_FIELD,
            cls.RICH_INTERACTIVE_ELEMENT
        ]
    
    @classmethod
    def get_all_dimensions(cls) -> List['EnhancedGrandClass']:
        """Get all 25 dimensions"""
        return (cls.get_base_dimensions() + 
                [cls.GRAND_CLASS_COVERAGE] +
                cls.get_dual_combinations() +
                cls.get_triple_combinations())
    
    @classmethod
    def calculate_coverage_score(cls, element_vectors: Dict['EnhancedGrandClass', Set[str]]) -> float:
        """
        Calculate how many of the 9 base EnhancedGrandClasses are present.
        Returns: 0.0-1.0
        """
        if not element_vectors:
            return 0.0
        
        present_count = 0
        for base_gc in cls.get_base_dimensions():
            if base_gc in element_vectors and element_vectors[base_gc]:
                # Has at least one attribute from this EnhancedGrandClass
                present_count += 1
        
        return present_count / 9.0
    
    @classmethod
    def check_dual_combination(cls, combination: 'EnhancedGrandClass',
                             element_vectors: Dict['EnhancedGrandClass', Set[str]]) -> bool:
        """
        Check if element matches a dual combination requirement.
        Returns: True/False
        """
        requirements = {
            # input + typable
            cls.INPUT_TYPABLE_COMBO: {
                cls.SEMANTIC_IDENTIFICATION: {"input"},
                cls.INTERACTION_MECHANICS: {"typable", "oninput", "onchange"}
            },
            # button + clickable
            cls.BUTTON_CLICKABLE_COMBO: {
                cls.SEMANTIC_IDENTIFICATION: {"button", "input[type='button']", "input[type='submit']"},
                cls.INTERACTION_MECHANICS: {"clickable", "onclick"}
            },
            # label + for/id
            cls.LABEL_ASSOCIATED_COMBO: {
                cls.SEMANTIC_IDENTIFICATION: {"label"},
                cls.RELATIONAL_CONTEXT: {"for", "aria-labelledby"}
            },
            # input + validation
            cls.FORM_VALIDATED_COMBO: {
                cls.SEMANTIC_IDENTIFICATION: {"input", "textarea", "select"},
                cls.VALIDATION_RULES: {"required", "pattern", "min", "max", "minlength", "maxlength"}
            },
            # accessible + interactive
            cls.ACCESSIBLE_INTERACTIVE_COMBO: {
                cls.ACCESSIBILITY_METADATA: {"aria-label", "aria-labelledby", "role"},
                cls.INTERACTION_MECHANICS: {"clickable", "typable", "selectable", "focusable"}
            },
            # visual + state
            cls.VISUAL_STATE_COMBO: {
                cls.VISUAL_PRESENTATION: {"class", "style", "hidden", "display"},
                cls.STATE_MANAGEMENT: {"visible", "hidden", "enabled", "disabled"}
            },
            # data + domain_id
            cls.DATA_DOMAIN_COMBO: {
                cls.DATA_BINDING: {"value", "placeholder", "text"},
                cls.DOMAIN_SPECIFIC_IDENTIFIERS: {"data-", "name", "id"}
            },
            # relations + accessibility
            cls.RELATIONAL_ACCESSIBLE_COMBO: {
                cls.RELATIONAL_CONTEXT: {"for", "href", "action", "form"},
                cls.ACCESSIBILITY_METADATA: {"aria-controls", "aria-describedby", "aria-labelledby"}
            },
            # validation + state
            cls.VALIDATION_STATE_COMBO: {
                cls.VALIDATION_RULES: {"required", "pattern", "aria-invalid"},
                cls.STATE_MANAGEMENT: {"valid", "invalid", "error"}
            },
            # interaction + data
            cls.INTERACTION_DATA_COMBO: {
                cls.INTERACTION_MECHANICS: {"oninput", "onchange", "onclick"},
                cls.DATA_BINDING: {"value", "text", "placeholder"}
            }
        }
        
        req = requirements.get(combination, {})
        for gc, required_values in req.items():
            if gc not in element_vectors:
                return False
            if not (element_vectors[gc] & required_values):
                return False
        return True
    
    @classmethod
    def check_triple_combination(cls, combination: 'EnhancedGrandClass',
                               element_vectors: Dict['EnhancedGrandClass', Set[str]]) -> bool:
        """
        Check if element matches a triple combination requirement.
        These are highly robust signatures.
        Returns: True/False
        """
        requirements = {
            # FORM_FIELD_SIGNATURE: input + validation + data
            cls.FORM_FIELD_SIGNATURE: {
                cls.SEMANTIC_IDENTIFICATION: {"input", "textarea", "select"},
                cls.VALIDATION_RULES: {"required", "pattern", "min", "max", "minlength", "maxlength"},
                cls.DATA_BINDING: {"value", "placeholder", "text"}
            },
            # ACTION_BUTTON_SIGNATURE: button + interactive + domain_action
            cls.ACTION_BUTTON_SIGNATURE: {
                cls.SEMANTIC_IDENTIFICATION: {"button", "input[type='submit']", "input[type='button']"},
                cls.INTERACTION_MECHANICS: {"clickable", "onclick", "tabindex"},
                cls.DOMAIN_SPECIFIC_IDENTIFIERS: {"submit", "save", "cancel", "next", "back", "action"}
            },
            # NAVIGATION_LINK_SIGNATURE: a + href + domain_nav
            cls.NAVIGATION_LINK_SIGNATURE: {
                cls.SEMANTIC_IDENTIFICATION: {"a", "link"},
                cls.RELATIONAL_CONTEXT: {"href", "target"},
                cls.DOMAIN_SPECIFIC_IDENTIFIERS: {"nav", "menu", "home", "about", "contact", "navigation"}
            },
            # ACCESSIBLE_FORM_FIELD: input + accessible + validation
            cls.ACCESSIBLE_FORM_FIELD: {
                cls.SEMANTIC_IDENTIFICATION: {"input", "textarea", "select"},
                cls.ACCESSIBILITY_METADATA: {"aria-label", "aria-labelledby", "aria-describedby", "aria-required"},
                cls.VALIDATION_RULES: {"required", "pattern", "aria-invalid"}
            },
            # RICH_INTERACTIVE_ELEMENT: interactive + visual + state
            cls.RICH_INTERACTIVE_ELEMENT: {
                cls.INTERACTION_MECHANICS: {"clickable", "typable", "selectable", "draggable", "hoverable"},
                cls.VISUAL_PRESENTATION: {"class", "style", "id", "data-style"},
                cls.STATE_MANAGEMENT: {"enabled", "disabled", "focus", "hover", "active"}
            }
        }
        
        req = requirements.get(combination, {})
        for gc, required_values in req.items():
            if gc not in element_vectors:
                return False
            if not (element_vectors[gc] & required_values):
                return False
        return True
    
    @classmethod
    def calculate_all_uniqueness_dims(cls, 
                                    element_vectors: Dict['EnhancedGrandClass', Set[str]]
                                    ) -> Dict['EnhancedGrandClass', Any]:
        """
        Calculate all uniqueness dimensions for an element.
        Returns: {dimension: value}
        """
        result = {}
        
        # 1. Base dimensions (already in element_vectors)
        result.update(element_vectors)
        
        # 2. Dimension 10: Coverage score
        result[cls.GRAND_CLASS_COVERAGE] = cls.calculate_coverage_score(element_vectors)
        
        # 3. Dimensions 11-20: Dual combinations
        for dual in cls.get_dual_combinations():
            result[dual] = cls.check_dual_combination(dual, element_vectors)
        
        # 4. Dimensions 21-25: Triple combinations
        for triple in cls.get_triple_combinations():
            result[triple] = cls.check_triple_combination(triple, element_vectors)
        
        return result


# ===== NULL VALUE FOR DEFINITIVE ABSENCE =====

class LogicType(Enum):
    OR = "or"          # Any of these
    AND = "and"        # All of these  
    NOT = "not"        # None of these
    ANY = "any"        # Any attribute possible

@dataclass(frozen=True)
class AttributeExpression:
    """Represents a logical expression over attribute set"""
    logic: LogicType
    attributes: Optional[FrozenSet[str]] = None  # None for ANY
    
    @classmethod
    def from_simple(cls, attrs: Set[str]) -> 'AttributeExpression':
        """Convert simple set to OR expression (backward compatibility)"""
        return cls(LogicType.OR, frozenset(attrs))
    
    @classmethod  
    def any(cls) -> 'AttributeExpression':
        """Anything possible (universal)"""
        return cls(LogicType.ANY, None)
    
    @classmethod
    def absent(cls) -> 'AttributeExpression':
        """Definitely absent (empty NOT)"""
        return cls(LogicType.NOT, frozenset())
    
    @classmethod
    def not_these(cls, attrs: Set[str]) -> 'AttributeExpression':
        """None of these attributes"""
        return cls(LogicType.NOT, frozenset(attrs))
    
    @classmethod
    def all_of(cls, attrs: Set[str]) -> 'AttributeExpression':
        """All of these attributes"""
        return cls(LogicType.AND, frozenset(attrs))
  

    def to_dict(self) -> Dict:
        """Convert to serializable dictionary"""
        return {
            'logic': self.logic.value,
            'attributes': list(self.attributes) if self.attributes else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AttributeExpression':
        """Create from serialized dictionary"""
        logic = LogicType(data['logic'])
        attrs = frozenset(data['attributes']) if data['attributes'] else None
        return cls(logic, attrs)
        
    def evaluate(self, observed_attributes: Set[str]) -> float:
        """
        Binary evaluation: 1.0 if matches, 0.0 if not.
        observed_attributes: Set of actual attribute strings present
        """
        if self.logic == LogicType.ANY:
            return 1.0  # ANY matches everything
        
        if self.logic == LogicType.NOT:
            if not self.attributes:  # ABSENT
                return 0.0  # ABSENT expects nothing = always 0 (strict)
            # NOT these attributes: 1.0 if NONE are present, 0.0 if ANY present
            return 0.0 if observed_attributes & self.attributes else 1.0
        
        if self.logic == LogicType.OR:
            if not self.attributes:  # Empty OR
                return 0.0  # Expecting nothing
            # OR: 1.0 if ANY expected attribute is present
            return 1.0 if observed_attributes & self.attributes else 0.0
        
        if self.logic == LogicType.AND:
            if not self.attributes:  # Empty AND
                return 0.0  # Impossible expectation
            # AND: 1.0 if ALL expected attributes are present
            return 1.0 if self.attributes.issubset(observed_attributes) else 0.0
        
        return 0.0  # Default

# ===== HASH REPRESENTATION =====

@dataclass(frozen=True)
class Hash:
    """A hash is (grand_class, attribute_expression)"""
    grand_class: EnhancedGrandClass
    expression: AttributeExpression  # Changed from value: str
    
    @property
    def is_anything(self) -> bool:
        """Check if this hash represents ANYTHING"""
        return self.expression.logic == LogicType.ANY
    
    @property
    def is_absent(self) -> bool:
        """Check if this hash represents ABSENT/NOT"""
        return self.expression.logic == LogicType.NOT and (
            self.expression.attributes is None or len(self.expression.attributes) == 0
        )

# ===== PATTERN DEFINITION =====

"""
🌀 PATTERN: Complete pattern system with logical expressions and bias matrices
"""


@dataclass
class Pattern:
    """
    Complete pattern system with:
    1. 6 expectation vectors using logical expressions (self + 5 neighbors)
    2. Position bias matrix (5×5) for neighbor assignments
    3. Pattern bias scalar for this pattern
    4. All methods needed by ROSE for calculations
    """
    
    # ===== PATTERN IDENTITY =====
    name: str
    
    # ===== 6 EXPECTATION VECTORS (logical expressions) =====
    self_vector: Dict[EnhancedGrandClass, AttributeExpression]
    parent_vector: Dict[EnhancedGrandClass, AttributeExpression]
    up_vector: Dict[EnhancedGrandClass, AttributeExpression]
    down_vector: Dict[EnhancedGrandClass, AttributeExpression]
    left_vector: Dict[EnhancedGrandClass, AttributeExpression]
    right_vector: Dict[EnhancedGrandClass, AttributeExpression]
    
    # ===== BIAS SYSTEM =====
    # Position bias matrix (5×5) - each row sums to 1
    position_bias_matrix: np.ndarray = field(
        default_factory=lambda: np.ones((5, 5)) / 5
    )  # Uniform: 0.2 in every cell
    
    # Pattern bias scalar (0.0-1.0)
    pattern_bias: float = 0.5
    
    # ===== CACHES FOR EFFICIENCY =====
    _position_expectation_matrix: Optional[np.ndarray] = None  # 5×25
    _sum_expectation_vector: Optional[np.ndarray] = None  # 1×25
    _self_expectation_vector: Optional[np.ndarray] = None  # 1×25
    
    # ===== HISTORY TRACKING =====
    bias_history: deque = field(default_factory=lambda: deque(maxlen=50))
    dot_product_history: deque = field(default_factory=lambda: deque(maxlen=50))
    
    # ===== INITIALIZATION VALIDATION =====
    def __post_init__(self):
        """Validate all vectors use AttributeExpression"""
        self._validate_vectors()
        self._normalize_biases()
    
    def _validate_vectors(self):
        """Ensure all vectors use AttributeExpression"""
        positions = ["self", "parent", "up", "down", "left", "right"]
        vectors = {
            "self": self.self_vector,
            "parent": self.parent_vector,
            "up": self.up_vector,
            "down": self.down_vector,
            "left": self.left_vector,
            "right": self.right_vector
        }
        
        for pos_name, vector in vectors.items():
            for gc, expr in vector.items():
                if not isinstance(expr, AttributeExpression):
                    raise TypeError(
                        f"Pattern {self.name} position {pos_name} dimension {gc} "
                        f"must be AttributeExpression, got {type(expr)}"
                    )
    
    def _normalize_biases(self):
        """Ensure position bias matrix rows sum to 1"""
        row_sums = self.position_bias_matrix.sum(axis=1, keepdims=True)
        self.position_bias_matrix = np.divide(
            self.position_bias_matrix, 
            row_sums,
            out=self.position_bias_matrix,
            where=row_sums != 0
        )
    
    # ===== VECTOR ACCESS METHODS =====
    
    def get_vector(self, position: str) -> Dict[EnhancedGrandClass, AttributeExpression]:
        """Get expectation vector for specific position"""
        vectors = {
            "self": self.self_vector,
            "parent": self.parent_vector,
            "up": self.up_vector,
            "down": self.down_vector,
            "left": self.left_vector,
            "right": self.right_vector
        }
        return vectors.get(position, {})
    
    def get_all_vectors(self) -> Dict[str, Dict[EnhancedGrandClass, AttributeExpression]]:
        """Get all 6 expectation vectors"""
        return {
            "self": self.self_vector,
            "parent": self.parent_vector,
            "up": self.up_vector,
            "down": self.down_vector,
            "left": self.left_vector,
            "right": self.right_vector
        }
    
    # ===== NUMERIC CONVERSION METHODS =====
    def _expression_vector_to_numeric(self, 
        vector: Dict[EnhancedGrandClass, AttributeExpression]
    ) -> np.ndarray:
        """Convert logical expression vector to 25D numeric array"""
        numeric_vector = np.zeros(25)
        all_dimensions = EnhancedGrandClass.get_all_dimensions()
        
        for i, dimension in enumerate(all_dimensions):
            if dimension in vector:
                expr = vector[dimension]
                
                # For expectation matrix: ANY = 0.5, everything else with attributes = 1.0
                if expr.logic == LogicType.ANY:
                    numeric_vector[i] = 0.5
                elif expr.logic == LogicType.NOT and not expr.attributes:
                    numeric_vector[i] = 0.0  # ABSENT
                elif expr.attributes:  # OR, AND, or NOT with attributes
                    numeric_vector[i] = 1.0
                else:
                    numeric_vector[i] = 0.0
        
        return numeric_vector
        
    def to_dict(self) -> Dict:
        """Convert pattern to serializable dictionary"""
        vectors = self.get_all_vectors()
        serialized_vectors = {}
        
        for position, vector in vectors.items():
            serialized_vectors[position] = {
                gc.name: expr.to_dict() 
                for gc, expr in vector.items()
            }
        
        return {
            "name": self.name,
            "vectors": serialized_vectors,
            "position_bias_matrix": self.position_bias_matrix.tolist(),
            "pattern_bias": self.pattern_bias,
            "bias_history_length": len(self.bias_history),
            "dot_history_length": len(self.dot_product_history)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Pattern':
        """Create pattern from serialized dictionary"""
        # Convert serialized vectors back to AttributeExpression
        vectors_data = data["vectors"]
        
        def parse_vector(position_data: Dict) -> Dict[EnhancedGrandClass, AttributeExpression]:
            vector = {}
            for gc_name, expr_data in position_data.items():
                gc = EnhancedGrandClass[gc_name]
                expr = AttributeExpression.from_dict(expr_data)
                vector[gc] = expr
            return vector
        
        pattern = cls(
            name=data["name"],
            self_vector=parse_vector(vectors_data["self"]),
            parent_vector=parse_vector(vectors_data["parent"]),
            up_vector=parse_vector(vectors_data["up"]),
            down_vector=parse_vector(vectors_data["down"]),
            left_vector=parse_vector(vectors_data["left"]),
            right_vector=parse_vector(vectors_data["right"])
        )
        
        pattern.position_bias_matrix = np.array(data["position_bias_matrix"])
        pattern.pattern_bias = data["pattern_bias"]
        
        return pattern
    
    # ===== STRING REPRESENTATION =====
    
    def __str__(self) -> str:
        position_biases = self.get_position_bias_vector()
        bias_sum = position_biases.sum()
        
        return (f"Pattern(name={self.name}, "
                f"pattern_bias={self.pattern_bias:.3f}, "
                f"position_bias_sum={bias_sum:.3f}, "
                f"vector_count=6)")
    
    def get_position_bias_vector(self) -> np.ndarray:
        """Get the diagonal of the position bias matrix (5×1)"""
        return np.diag(self.position_bias_matrix)
        
    def summary(self) -> Dict:
        """Get summary statistics"""
        position_biases = self.get_position_bias_vector()
        
        return {
            "name": self.name,
            "pattern_bias": float(self.pattern_bias),
            "position_biases": {
                "parent": float(position_biases[0]),
                "up": float(position_biases[1]),
                "down": float(position_biases[2]),
                "left": float(position_biases[3]),
                "right": float(position_biases[4])
            },
            "position_bias_matrix_shape": self.position_bias_matrix.shape,
            "bias_history_length": len(self.bias_history),
            "dot_history_length": len(self.dot_product_history)
        }


# ===== ROSE CORE ENGINE =====

class ROSE:
    """
    Pattern library with action plan templates.
    Pure storage - no execution logic.
    """
    
    def __init__(self, initial_pattern: str, coordinate: Tuple[int, ...]):
        """
        Initialize ROSE instance for a specific neuron.
        """
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_priority: Dict[str, float] = {}
        self.coordinate = coordinate
        
        # 1. Initialize ALL patterns (UNKNOWN + 4 base patterns)
        self._initialize_patterns()  # This creates all 5 patterns
        
        # 2. NOW set pattern_names AFTER patterns are created
        self.pattern_names = list(self.patterns.keys())  # ← Use self.patterns, not self.rose
        self.position_names = ["self", "parent", "up", "down", "left", "right"]
        
        # 3. Initialize pattern transition tracking for this neuron
        self._pattern_transitions = []
        
        print(f"🌀 ROSE created for coordinate {coordinate} with initial bias: {initial_pattern}")
        print(f"  Patterns: {self.pattern_names}")
          
    def _initialize_patterns(self):
        """Initialize all patterns with strategic relational definitions for T() transformation."""
        
        # Define constants
        ABSENT = AttributeExpression.absent()      # Definitely nothing in this dimension
        ANY = AttributeExpression.any()            # Could be anything in this dimension
        
        # Helper functions
        def OR(attrs):
            return AttributeExpression(LogicType.OR, attrs) if attrs else ABSENT
        
        def AND(attrs):
            return AttributeExpression(LogicType.AND, attrs) if attrs else ABSENT
        
        def NOT(attrs):
            return AttributeExpression(LogicType.NOT, attrs) if attrs else ANY
        
        # Strategic attribute sets for each dimension
        # We're defining these NOT as real DOM attributes but as relational markers
        
        # Dimension 0: SEMANTIC_IDENTIFICATION - Common attributes for poor patterns
        SEMANTIC_RICH = set()  # Rich patterns ignore
        SEMANTIC_POOR = {"div", "span", "label", "p", "section", "container"}  # Poor patterns claim
        
        # Dimension 1: STATE_MANAGEMENT - Certain for poor, uncertain for rich
        STATE_CERTAIN = {"visible", "exists"}  # Poor patterns are certain
        STATE_ANY = set()  # Rich patterns are uncertain
        
        # Dimension 2: DATA_BINDING - Core for DATA_INPUT, absent for others
        DATA_CORE = {"value", "placeholder", "has_value"}
        DATA_ABSENT = set()
        
        # Dimension 3: VISUAL_PRESENTATION - Poor patterns claim, rich ignore
        VISUAL_POOR = {"has_class", "has_style"}
        VISUAL_RICH = set()
        
        # Dimension 4: INTERACTION_MECHANICS - Core for interactive patterns
        INTERACTIVE_CORE = {"typable", "clickable", "focusable"}
        NON_INTERACTIVE = set()
        
        # Dimension 5: RELATIONAL_CONTEXT - Rich uncertain, poor certain
        RELATIONS_POOR = {"for", "contains", "parent_of"}
        RELATIONS_RICH = set()
        
        # Dimension 6: VALIDATION_RULES - Core for DATA_INPUT
        VALIDATION_CORE = {"required", "pattern", "minlength"}
        VALIDATION_ABSENT = set()
        
        # Dimension 7: ACCESSIBILITY_METADATA - ACTION_ELEMENT core, others uncertain
        ACCESS_CORE = {"aria-label", "role_button", "role_link"}
        ACCESS_UNCERTAIN = set()
        
        # Dimension 8: DOMAIN_SPECIFIC_IDENTIFIERS - Poor patterns claim
        DOMAIN_POOR = {"id_attribute", "data_container", "data_section"}
        DOMAIN_RICH = set()
        
        # Helper to create position vector with strategic allocations
        def create_strategic_vector(semantic_set, state_set, data_set, visual_set,
                                  interaction_set, relations_set, validation_set,
                                  access_set, domain_set):
            """Create vector with strategic attribute allocations."""
            return {
                EnhancedGrandClass.SEMANTIC_IDENTIFICATION: OR(semantic_set),
                EnhancedGrandClass.STATE_MANAGEMENT: OR(state_set) if state_set else ANY,
                EnhancedGrandClass.DATA_BINDING: OR(data_set) if data_set else (
                    ABSENT if data_set is not None and len(data_set) == 0 else ANY
                ),
                EnhancedGrandClass.VISUAL_PRESENTATION: OR(visual_set) if visual_set else ANY,
                EnhancedGrandClass.INTERACTION_MECHANICS: OR(interaction_set) if interaction_set else (
                    ABSENT if interaction_set is not None and len(interaction_set) == 0 else ANY
                ),
                EnhancedGrandClass.RELATIONAL_CONTEXT: OR(relations_set) if relations_set else ANY,
                EnhancedGrandClass.VALIDATION_RULES: OR(validation_set) if validation_set else (
                    ABSENT if validation_set is not None and len(validation_set) == 0 else ANY
                ),
                EnhancedGrandClass.ACCESSIBILITY_METADATA: OR(access_set) if access_set else ANY,
                EnhancedGrandClass.DOMAIN_SPECIFIC_IDENTIFIERS: OR(domain_set) if domain_set else ANY
            }
        
        # ===== DATA_INPUT Pattern (Rich - claims fewer attributes) =====
        data_input = Pattern(
            name="DATA_INPUT",
            # SELF: Core specialties only, ignores common attributes
            self_vector=create_strategic_vector(
                semantic_set=SEMANTIC_RICH,        # Ignores semantic (rich can afford to)
                state_set=STATE_ANY,               # Uncertain about state
                data_set=DATA_CORE,                # CORE: definitely has data
                visual_set=VISUAL_RICH,            # Ignores visual
                interaction_set=INTERACTIVE_CORE,  # CORE: definitely interactive
                relations_set=RELATIONS_RICH,      # Uncertain about relations
                validation_set=VALIDATION_CORE,    # CORE: definitely has validation
                access_set=ACCESS_UNCERTAIN,       # Uncertain about accessibility
                domain_set=DOMAIN_RICH             # Ignores domain IDs
            ),
            
            # PARENT: Mostly uncertain, definitely NOT interactive/data/validation
            parent_vector=create_strategic_vector(
                semantic_set=SEMANTIC_RICH,
                state_set=STATE_ANY,
                data_set=DATA_ABSENT,              # Definitely NOT data
                visual_set=None,                   # ANY
                interaction_set=NON_INTERACTIVE,   # Definitely NOT interactive
                relations_set=RELATIONS_RICH,
                validation_set=VALIDATION_ABSENT,  # Definitely NOT validation
                access_set=None,                   # ANY
                domain_set=DOMAIN_RICH
            ),
            
            # UP: Label - certain about semantic, relations, domain
            up_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,        # Claims semantic (like label)
                state_set=STATE_ANY,
                data_set=None,                     # ANY
                visual_set=None,                   # ANY
                interaction_set=NON_INTERACTIVE,   # Definitely NOT interactive
                relations_set=RELATIONS_POOR,      # Claims relations (has "for")
                validation_set=VALIDATION_ABSENT,
                access_set=None,
                domain_set=DOMAIN_POOR             # Claims domain IDs
            ),
            
            # DOWN: Help text - rich definition to help identify DATA_INPUT
            down_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,        # Claims semantic
                state_set=STATE_CERTAIN,           # Certain about state
                data_set=DATA_CORE,                # Has text content
                visual_set=None,                   # ANY
                interaction_set=NON_INTERACTIVE,
                relations_set=None,                # ANY
                validation_set=VALIDATION_CORE,    # Has validation info
                access_set=set(["aria-describedby", "role_alert"]),  # Certain accessibility
                domain_set=DOMAIN_POOR             # Claims domain
            ),
            
            # LEFT: Icon/indicator - mostly uncertain, definitely NOT interactive/relational
            left_vector=create_strategic_vector(
                semantic_set=None,                 # ANY
                state_set=None,                    # ANY
                data_set=None,                     # ANY
                visual_set=None,                   # ANY
                interaction_set=NON_INTERACTIVE,   # Definitely NOT interactive
                relations_set=set(),               # Definitely NOT relational (empty = NOT)
                validation_set=VALIDATION_ABSENT,
                access_set=None,                   # ANY
                domain_set=None                    # ANY
            ),
            
            # RIGHT: Next field - rich neighbor definition
            right_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,        # Claims semantic
                state_set=STATE_ANY,
                data_set=DATA_CORE,                # Has data
                visual_set=None,                   # ANY
                interaction_set=INTERACTIVE_CORE,  # Interactive
                relations_set=set(["data_next", "data_adjacent"]),  # Has "next" relation
                validation_set=None,               # ANY
                access_set=None,                   # ANY
                domain_set=DOMAIN_POOR             # Claims domain
            )
        )
        
        # Set strategic position biases for DATA_INPUT
        data_input.position_bias_matrix = np.array([
            # parent  up     down   left   right
            [0.30,   0.20,  0.10,  0.25,  0.15],  # parent row
            [0.25,   0.30,  0.10,  0.20,  0.15],  # up row  
            [0.10,   0.10,  0.40,  0.20,  0.20],  # down row
            [0.20,   0.15,  0.20,  0.30,  0.15],  # left row
            [0.15,   0.15,  0.20,  0.15,  0.35]   # right row
        ])
        data_input.pattern_bias = 0.15
        
        # ===== ACTION_ELEMENT Pattern (Rich - similar strategy) =====
        action_element = Pattern(
            name="ACTION_ELEMENT",
            # SELF: Core specialties only
            self_vector=create_strategic_vector(
                semantic_set=SEMANTIC_RICH,        # Ignores semantic
                state_set=STATE_ANY,               # Uncertain about state
                data_set=DATA_ABSENT,              # Definitely NOT data
                visual_set=VISUAL_RICH,            # Ignores visual
                interaction_set=INTERACTIVE_CORE,  # CORE: definitely interactive
                relations_set=set(["href", "formaction", "click_target"]),  # Claims relations
                validation_set=VALIDATION_ABSENT,  # Definitely NOT validation
                access_set=ACCESS_CORE,            # CORE: definitely accessible
                domain_set=DOMAIN_RICH             # Ignores domain
            ),
            
            # PARENT: Same as DATA_INPUT parent (consistent uncertainty)
            parent_vector=create_strategic_vector(
                semantic_set=SEMANTIC_RICH,
                state_set=STATE_ANY,
                data_set=DATA_ABSENT,
                visual_set=None,
                interaction_set=NON_INTERACTIVE,
                relations_set=RELATIONS_RICH,
                validation_set=VALIDATION_ABSENT,
                access_set=None,
                domain_set=DOMAIN_RICH
            ),
            
            # UP: Previous field - similar to DATA_INPUT right
            up_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_ANY,
                data_set=DATA_CORE,
                visual_set=None,
                interaction_set=INTERACTIVE_CORE,
                relations_set=set(["data_previous", "data_above"]),
                validation_set=None,
                access_set=None,
                domain_set=DOMAIN_POOR
            ),
            
            # DOWN: ABSENT - definitely nothing
            down_vector=create_strategic_vector(
                semantic_set=set(),                # Empty = NOT anything semantic
                state_set=set(),                   # NOT any state
                data_set=DATA_ABSENT,
                visual_set=set(),                  # NOT visual
                interaction_set=NON_INTERACTIVE,
                relations_set=set(),               # NOT relational
                validation_set=VALIDATION_ABSENT,
                access_set=set(),                  # NOT accessible
                domain_set=set()                   # NOT domain
            ),
            
            # LEFT: Secondary button - similar to self but different domain
            left_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_ANY,
                data_set=DATA_CORE,
                visual_set=None,
                interaction_set=INTERACTIVE_CORE,
                relations_set=set(["data_sibling", "data_left"]),
                validation_set=VALIDATION_ABSENT,  # Definitely NOT validation
                access_set=None,
                domain_set=set(["data_secondary", "data_cancel"])  # Different domain
            ),
            
            # RIGHT: ABSENT - definitely nothing (same as DOWN)
            right_vector=create_strategic_vector(
                semantic_set=set(),
                state_set=set(),
                data_set=DATA_ABSENT,
                visual_set=set(),
                interaction_set=NON_INTERACTIVE,
                relations_set=set(),
                validation_set=VALIDATION_ABSENT,
                access_set=set(),
                domain_set=set()
            )
        )
        
        # Set strategic position biases for ACTION_ELEMENT
        action_element.position_bias_matrix = np.array([
            # Button's parent is usually a container
            [0.40,   0.20,  0.05,  0.10,  0.05],  # parent row
            [0.20,   0.35,  0.05,  0.10,  0.05],  # up row
            [0.05,   0.05,  0.35,  0.05,  0.50],  # down row (strong for ABSENT)
            [0.10,   0.10,  0.05,  0.45,  0.05],  # left row  
            [0.05,   0.05,  0.35,  0.05,  0.50]   # right row (strong for ABSENT)
        ])
        action_element.pattern_bias = 0.10
        
        # ===== CONTEXT_ELEMENT Pattern (Moderate richness) =====
        context_element = Pattern(
            name="CONTEXT_ELEMENT",
            # SELF: Claims common attributes, definitely NOT interactive/data
            self_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,        # Claims semantic
                state_set=STATE_CERTAIN,           # Certain about state
                data_set=DATA_ABSENT,              # Definitely NOT data
                visual_set=VISUAL_POOR,            # Claims visual
                interaction_set=NON_INTERACTIVE,   # Definitely NOT interactive
                relations_set=RELATIONS_POOR,      # Claims relations
                validation_set=VALIDATION_ABSENT,  # Definitely NOT validation
                access_set=ACCESS_UNCERTAIN,       # Uncertain about accessibility
                domain_set=DOMAIN_POOR             # Claims domain
            ),
            
            # PARENT: Container with uncertainty
            parent_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_CERTAIN,
                data_set=DATA_ABSENT,
                visual_set=None,                   # ANY
                interaction_set=NON_INTERACTIVE,
                relations_set=None,                # ANY
                validation_set=VALIDATION_ABSENT,
                access_set=None,                   # ANY
                domain_set=DOMAIN_POOR
            ),
            
            # UP: Previous heading
            up_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_CERTAIN,
                data_set=DATA_ABSENT,
                visual_set=None,
                interaction_set=NON_INTERACTIVE,
                relations_set=set(["data_previous", "data_above"]),
                validation_set=VALIDATION_ABSENT,
                access_set=None,
                domain_set=DOMAIN_POOR
            ),
            
            # DOWN: Associated input - interactive neighbor
            down_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_CERTAIN,
                data_set=DATA_CORE,                # Has data
                visual_set=None,
                interaction_set=INTERACTIVE_CORE,  # Interactive
                relations_set=set(["data_associated", "data_described"]),  # Associated relation
                validation_set=None,               # ANY
                access_set=None,                   # ANY
                domain_set=DOMAIN_POOR
            ),
            
            # LEFT: ABSENT - definitely nothing
            left_vector=create_strategic_vector(
                semantic_set=set(),
                state_set=set(),
                data_set=DATA_ABSENT,
                visual_set=set(),
                interaction_set=NON_INTERACTIVE,
                relations_set=set(),
                validation_set=VALIDATION_ABSENT,
                access_set=set(),
                domain_set=set()
            ),
            
            # RIGHT: Horizontal layout neighbor
            right_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_CERTAIN,
                data_set=DATA_CORE,
                visual_set=None,
                interaction_set=INTERACTIVE_CORE,
                relations_set=set(["data_associated", "data_right"]),
                validation_set=None,
                access_set=None,
                domain_set=DOMAIN_POOR
            )
        )
        
        # Set strategic position biases for CONTEXT_ELEMENT
        context_element.position_bias_matrix = np.array([
            # Label context: parent and up important, left ABSENT
            [0.35,   0.20,  0.05,  0.05,  0.05],  # parent row
            [0.20,   0.35,  0.10,  0.05,  0.05],  # up row
            [0.05,   0.10,  0.50,  0.10,  0.10],  # down row (associated input)
            [0.05,   0.05,  0.10,  0.50,  0.10],  # left row (ABSENT expectation)
            [0.05,   0.05,  0.10,  0.10,  0.50]   # right row (horizontal neighbor)
        ])
        context_element.pattern_bias = 0.25
        
        # ===== STRUCTURAL Pattern (Poor - claims many attributes) =====
        structural = Pattern(
            name="STRUCTURAL",
            # SELF: Claims ALL common attributes, very certain
            self_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,        # Claims semantic
                state_set=STATE_CERTAIN,           # Certain about state
                data_set=DATA_ABSENT,              # Definitely NOT data
                visual_set=VISUAL_POOR,            # Claims visual
                interaction_set=NON_INTERACTIVE,   # Definitely NOT interactive
                relations_set=RELATIONS_POOR,      # Claims relations
                validation_set=VALIDATION_ABSENT,  # Definitely NOT validation
                access_set=ACCESS_CORE,            # Certain about accessibility
                domain_set=DOMAIN_POOR             # Claims domain
            ),
            
            # PARENT: Similar but with some uncertainty
            parent_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_CERTAIN,
                data_set=DATA_ABSENT,
                visual_set=None,                   # ANY (uncertain)
                interaction_set=NON_INTERACTIVE,
                relations_set=RELATIONS_POOR,
                validation_set=VALIDATION_ABSENT,
                access_set=None,                   # ANY (uncertain)
                domain_set=DOMAIN_POOR
            ),
            
            # UP: Previous container
            up_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_CERTAIN,
                data_set=DATA_ABSENT,
                visual_set=None,
                interaction_set=NON_INTERACTIVE,
                relations_set=set(["data_previous", "data_above"]),
                validation_set=VALIDATION_ABSENT,
                access_set=None,
                domain_set=DOMAIN_POOR
            ),
            
            # DOWN: Next container
            down_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_CERTAIN,
                data_set=DATA_ABSENT,
                visual_set=None,
                interaction_set=NON_INTERACTIVE,
                relations_set=set(["data_next", "data_below"]),
                validation_set=VALIDATION_ABSENT,
                access_set=None,
                domain_set=DOMAIN_POOR
            ),
            
            # LEFT: Sibling container
            left_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_CERTAIN,
                data_set=DATA_ABSENT,
                visual_set=None,
                interaction_set=NON_INTERACTIVE,
                relations_set=set(["data_sibling", "data_left"]),
                validation_set=VALIDATION_ABSENT,
                access_set=None,
                domain_set=DOMAIN_POOR
            ),
            
            # RIGHT: Sibling container (similar to LEFT)
            right_vector=create_strategic_vector(
                semantic_set=SEMANTIC_POOR,
                state_set=STATE_CERTAIN,
                data_set=DATA_ABSENT,
                visual_set=None,
                interaction_set=NON_INTERACTIVE,
                relations_set=set(["data_sibling", "data_right"]),
                validation_set=VALIDATION_ABSENT,
                access_set=None,
                domain_set=DOMAIN_POOR
            )
        )
        
        # Set strategic position biases for STRUCTURAL
        structural.position_bias_matrix = np.array([
            # Structural elements: all positions somewhat equal
            [0.25,   0.20,  0.15,  0.15,  0.10],  # parent row
            [0.20,   0.25,  0.15,  0.15,  0.10],  # up row
            [0.15,   0.15,  0.25,  0.15,  0.15],  # down row  
            [0.15,   0.15,  0.15,  0.25,  0.15],  # left row
            [0.10,   0.10,  0.15,  0.15,  0.30]   # right row
        ])
        structural.pattern_bias = 0.40
        
        # ===== UNKNOWN Pattern (Maximum entropy) =====
        unknown = Pattern(
            name="UNKNOWN",
            # SELF: All ANY (0.5) - maximum entropy
            self_vector=create_strategic_vector(
                semantic_set=None,     # ANY
                state_set=None,        # ANY
                data_set=None,         # ANY
                visual_set=None,       # ANY
                interaction_set=None,  # ANY
                relations_set=None,    # ANY
                validation_set=None,   # ANY
                access_set=None,       # ANY
                domain_set=None        # ANY
            ),
            
            # All neighbors also maximum entropy
            parent_vector=create_strategic_vector(
                semantic_set=None, state_set=None, data_set=None,
                visual_set=None, interaction_set=None, relations_set=None,
                validation_set=None, access_set=None, domain_set=None
            ),
            up_vector=create_strategic_vector(
                semantic_set=None, state_set=None, data_set=None,
                visual_set=None, interaction_set=None, relations_set=None,
                validation_set=None, access_set=None, domain_set=None
            ),
            down_vector=create_strategic_vector(
                semantic_set=None, state_set=None, data_set=None,
                visual_set=None, interaction_set=None, relations_set=None,
                validation_set=None, access_set=None, domain_set=None
            ),
            left_vector=create_strategic_vector(
                semantic_set=None, state_set=None, data_set=None,
                visual_set=None, interaction_set=None, relations_set=None,
                validation_set=None, access_set=None, domain_set=None
            ),
            right_vector=create_strategic_vector(
                semantic_set=None, state_set=None, data_set=None,
                visual_set=None, interaction_set=None, relations_set=None,
                validation_set=None, access_set=None, domain_set=None
            )
        )
        
        # UNKNOWN has uniform biases (complete uncertainty)
        unknown.position_bias_matrix = np.array([
            [0.20, 0.20, 0.20, 0.20, 0.20],
            [0.20, 0.20, 0.20, 0.20, 0.20],
            [0.20, 0.20, 0.20, 0.20, 0.20],
            [0.20, 0.20, 0.20, 0.20, 0.20],
            [0.20, 0.20, 0.20, 0.20, 0.20]
        ])
        unknown.pattern_bias = 0.20
        
        # Register all patterns
        self._register_pattern(data_input)
        self._register_pattern(action_element)
        self._register_pattern(context_element)
        self._register_pattern(structural)
        self._register_pattern(unknown)

    def _register_pattern(self, pattern: Pattern):
        self.patterns[pattern.name] = pattern
        # Don't try to use pattern.pattern_bias - it doesn't exist
        self.pattern_priority[pattern.name] = 0.10  # Temporary default
        
    def _update_priority_distribution(self):
        """Normalize priorities to sum to 1"""
        total = sum(self.pattern_priority.values())
        if total > 0:
            for name in self.pattern_priority:
                self.pattern_priority[name] /= total
    
    # ===== PUBLIC API =====
    
    def get_pattern(self, name: str) -> Pattern:
        """Get pattern by name"""
        return self.patterns.get(name)
    
    def get_all_patterns(self) -> List[Pattern]:
        """Get all registered patterns"""
        return list(self.patterns.values())

    def update_priority(self, pattern_name: str, new_priority: float):
        """Update priority for a pattern"""
        if pattern_name in self.pattern_priority:
            self.pattern_priority[pattern_name] = new_priority
            self._update_priority_distribution()
            
    def update_from_axon_queue(self, axon_network, coordinate: Tuple[int, ...]) -> Dict[str, float]:
        """
        Update ROSE priorities based on axon queue activity for this coordinate.
        
        Returns priority deltas for Nexus to apply.
        """
        # Get neuron ID for this coordinate
        neuron_id = axon_network.neuron_registry.get(coordinate, {}).get('id')
        if not neuron_id:
            return {}
        
        # Get recent axons for this neuron
        all_axons = axon_network.get_axon_log_for_neuron(neuron_id)
        current_time = time.time()
        recent_axons = [a for a in all_axons if time.time() - a['absolute_time'] <= 60]
                        
        # Calculate pattern frequencies from axons
        pattern_counts = defaultdict(int)
        for axon in recent_axons:
            axon_type = axon['axon_type']
            # Map axon types to patterns
            if 'SUCCESS' in axon_type:
                pattern = axon['data'].get('pattern', 'UNKNOWN')
                pattern_counts[pattern] += 3  # Success weight
            elif 'FAILURE' in axon_type:
                pattern = axon['data'].get('pattern', 'UNKNOWN')
                pattern_counts[pattern] -= 2  # Failure penalty
            elif 'DISCOVERY' in axon_type:
                pattern_counts['UNKNOWN'] += 1  # Discovery weight
        
        # Convert to priority updates
        updates = {}
        total = sum(abs(v) for v in pattern_counts.values()) or 1
        for pattern, count in pattern_counts.items():
            if pattern in self.patterns:
                # Normalize to [-0.2, 0.2] range
                updates[pattern] = (count / total) * 0.2
        
        return updates


"""
🧠 NEURON: DOM Neural Unit with ROSE Integration
"""

#!/usr/bin/env python3
"""
🌀 NEURON: Autonomous DOM Processing Unit with 25D Matrix Mathematics
Enhanced with matrix-based calculations and continuous Baesian recycling
""" 

# ===== Rerouting objects to maximize information gain, the membrane 

class VoidSystem:
    """Simplified void rerouting using T() transform as specified"""
    def __init__(self, axon_network):
        self.axon_network = axon_network
        self.membranes = {}  # void_coordinate -> MembraneState
        
    def register_void(self, void_coordinate, neuron_id, neuron_data):
        """Neuron registers at a void"""
        if void_coordinate not in self.membranes:
            self.membranes[void_coordinate] = self.MembraneState(void_coordinate)
            
        membrane = self.membranes[void_coordinate]
        membrane.add_neuron(neuron_id, neuron_data)
        
    def process_voids(self):
        """Process all active voids"""
        processed_any = False
        
        for void_coord, membrane in list(self.membranes.items()):
            if not membrane.port:
                continue
                
            # Process each unprocessed neuron
            for neuron_id, conn in list(membrane.connections.items()):
                if not conn['processed']:
                    # Get neuron object - FIX: axon_network needs get_neuron_by_id method
                    # For now, we'll find it by coordinate
                    neuron = None
                    for coord, neuron_data in self.axon_network.neuron_registry.items():
                        if neuron_data.get('id') == neuron_id:
                            # Need to store neuron references somewhere accessible
                            # This is a hack - you need a proper neuron lookup
                            pass
                    
                    if neuron:
                        processed = membrane.process_neuron(neuron_id, neuron)
                        if processed:
                            processed_any = True
                                
        return processed_any
        
    def get_reroute(self, neuron_id, void_coordinate):
        """Get reroute result for a neuron"""
        if void_coordinate in self.membranes:
            membrane = self.membranes[void_coordinate]
            if neuron_id in membrane.connections:
                conn = membrane.connections[neuron_id]
                if conn['processed']:
                    return {
                        'reroute_to': conn['reroute_to'],
                        'similarity': conn['similarity']
                    }
        return None
        
    class MembraneState:
        def __init__(self, void_coordinate):
            self.coordinate = void_coordinate
            self.void = True  # Waiting for connections
            self.port = False  # Processing
            self.connections = {}  # neuron_id -> connection_data
            
        def add_neuron(self, neuron_id, neuron_data):
            """Neuron connects to this void"""
            if self.void:
                self.void = False
                self.port = True
                
            self.connections[neuron_id] = {
                **neuron_data,
                'processed': False,
                'reroute_to': None,
                'similarity': 0.0
            }
            
        def process_neuron(self, neuron_id, neuron):
            """Process rerouting for specific neuron"""
            if neuron_id not in self.connections:
                return False
                
            conn = self.connections[neuron_id]
            
            # Get neuron's current expectation matrix
            if not hasattr(neuron, 'P_permuted') or neuron.P_permuted is None:
                # Fallback to original P matrix
                P_i_k = neuron.P_matrix.copy()
            else:
                P_i_k = neuron.P_permuted.copy()  # 5×25
            
            # Get position index
            position_idx = neuron.neighbor_positions.index(conn['input_direction'])
            
            # Find 4 candidate coordinates
            candidates = self._find_candidates(neuron, conn)
            
            # Find best reroute
            result = self._find_best_reroute(neuron, P_i_k, position_idx, candidates)
            
            if result:
                conn['processed'] = True
                conn['reroute_to'] = result['best_candidate']
                conn['similarity'] = result['best_similarity']
                
                # If all connections processed, return to waiting state
                if all(c['processed'] for c in self.connections.values()):
                    self.port = False
                    self.void = True
                    
                return True
                
            return False
            
        def _find_best_reroute(self, neuron, P_i_k, position_idx, candidates):
            """Find best reroute using simplified T() transform flow"""
            if not candidates:
                return None
                
            # Step 1: Transform original expectations to 87D
            P_87d = neuron.T(P_i_k)  # 5×87
            original_expectation_87d = P_87d[position_idx]  # 1×87
            
            # Step 2: Process each candidate
            profiles = []
            valid_candidates = []
            
            for i, candidate_coord in enumerate(candidates):
                if candidate_coord is None:
                    profiles.append(np.zeros(87))
                    valid_candidates.append(None)
                    continue
                    
                try:
                    # Get observation
                    obs_vector = neuron._observe_coordinate(candidate_coord)  # 1×25
                    
                    # Create modified matrix P_m
                    P_m = P_i_k.copy()  # 5×25
                    P_m[position_idx] = obs_vector  # Replace with observation
                    
                    # Transform modified matrix
                    Q = neuron.T(P_m)  # 5×87
                    
                    # Extract profile for this position
                    profile = Q[position_idx]  # 1×87
                    
                    profiles.append(profile)
                    valid_candidates.append(candidate_coord)
                    
                except Exception as e:
                    # Observation failed
                    profiles.append(np.zeros(87))
                    valid_candidates.append(None)
                    
            if not valid_candidates or all(c is None for c in valid_candidates):
                return None
                
            # Step 3: Compute similarities
            profiles_matrix = np.array(profiles)  # 4×87
            similarities = np.dot(profiles_matrix, original_expectation_87d)  # Shape: (4,)
            
            # Step 4: Select best candidate
            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]
            
            if best_similarity > 0 and valid_candidates[best_idx] is not None:
                return {
                    'best_candidate': valid_candidates[best_idx],
                    'best_similarity': float(best_similarity),
                    'all_similarities': similarities.tolist(),
                    'candidates': valid_candidates
                }
                
            return None
            
        def _find_candidates(self, neuron, connection):
            """Find 4 candidate coordinates around void"""
            void_coord = self.coordinate
            excluded = {void_coord, connection['neuron_coord']}
            
            # Exclude other reroutes from this membrane
            for other_id, other_conn in self.connections.items():
                if other_id != connection['neuron_id'] and other_conn['reroute_to']:
                    excluded.add(other_conn['reroute_to'])
                    
            # Spiral search for 4 candidates
            candidates = []
            directions = ['up', 'down', 'left', 'right']
            depth = 1
            
            while len(candidates) < 4 and depth <= 5:
                for direction in directions:
                    candidate = self._get_coordinate_in_direction(
                        void_coord, direction, depth
                    )
                    
                    if candidate is None or candidate in excluded:
                        continue
                        
                    # Check if coordinate has element
                    try:
                        xpath = neuron._coord_to_xpath(candidate)
                        element = neuron.dom_driver.find_element(By.XPATH, xpath)
                        if element:
                            candidates.append(candidate)
                            excluded.add(candidate)
                    except:
                        excluded.add(candidate)
                        
                    if len(candidates) == 4:
                        break
                        
                depth += 1
                
            # Pad to 4
            while len(candidates) < 4:
                candidates.append(None)
                
            return candidates[:4]
            
        def _get_coordinate_in_direction(self, base_coord, direction, distance):
            """Get coordinate in direction from base coordinate"""
            if not base_coord:
                return None
                
            coord = list(base_coord)
            
            if direction == "up" and len(coord) > 0:
                coord[-1] = max(0, coord[-1] - distance)
            elif direction == "down" and len(coord) > 0:
                coord[-1] += distance
            elif direction == "left" and len(coord) > 1:
                coord[-2] = max(0, coord[-2] - distance)
            elif direction == "right" and len(coord) > 1:
                coord[-2] += distance
            else:
                return None
                
            return tuple(coord)
    
          
class Neuron:
    
    pattern_names = ["DATA_INPUT", "ACTION_ELEMENT", "CONTEXT_ELEMENT", 
                        "STRUCTURAL", "UNKNOWN"]
    position_names = ["self", "parent", "up", "down", "left", "right"]
        
    """
    Autonomous DOM Neural Unit - COMPLETE IMPLEMENTATION
    Extracts everything once, uses for all operations with proper logging
    """
    def __init__(self, coordinate: Tuple[int, ...], priori_pattern: str, 
                    dom_driver: Any, axon_network: Any):
            # Core identity
            self.coordinate = coordinate
            self.id = self._generate_id()
            self.dom_driver = dom_driver
            self.axon_network = axon_network
            self.pending_coordinates = []  # [(position, coordinate)] - coordinates to retry
            self.stalled_positions = {}  # position -> (coordinate, stall_start_time)
            # FIX: Set current_pattern BEFORE calling axon_network.register_neuron
            self.current_pattern = priori_pattern  
            self.current_pattern_idx = self._get_pattern_idx(priori_pattern)
            
            # Now register with axon_network
            self.axon_network.register_neuron(self)
            
            self.learning_mode = "Normal" 
            # ===== PHASE 0: ONE-TIME EXTRACTION =====
            print(f"🧠 Neuron {self.id} initializing at {coordinate} as {priori_pattern}")
            

            # Create ROSE for dictionary definitions (ONCE)
            self.rose = ROSE(initial_pattern=priori_pattern, coordinate=coordinate)
            
            #extraction parameters 
            self.position_names = ["self", "parent", "up", "down", "left", "right"]
            self.neighbor_positions = ["parent", "up", "down", "left", "right"]
            
            # ULTIMATE FALLBACK - Rank 3 tensor Permutation X Identity X Position X relational space 
            
    
            # ADD UNKNOWN ENHANCEMENT FIELDS:
            self.unknown_perm_cache = {
                't_gamma_tensor': None,           # 5×5×87 base tensor
                'initial_bias_updated': False,
                'b_matrix_updated': False,    # T_gamma applied flag
                'cycle_history': []  # Track eigen update sequence
            }
            
            # UNKNOWN-specific eigen storage
            self.eigen_gamma = None          # γ from T_gamma
            self.eigen_gamma_v = None        # v_γ from T_gamma 
            self.eigen_zeta = None           # ζ from tensor fallback
            
            # Extract EVERYTHING once
            self._extract_all_expectations_once()
            
            self.membrane_waiting_for = None  # Void coordinate we're waiting on
            self.membrane_reroutes = {}  # position -> rerouted coordinate
            self.membrane_waiting = {}  # position -> void_coordinate
            self.membrane_active = False  # Currently waiting for membrane processing
            self.stalled = False #wait for reroute coordinate 

            # Initialize matrices from extracted data
            self._initialize_matrices_from_extracted_data()
            self.T_exp = self._init_T_exp()
            self.T_obs = None 
            

            # ===== EXACT FLOW VARIABLES =====
            self.eigen_alpha = None          # Dominant eigenvalue for S*
            self.eigen_alpha_v = None        # Dominant eigenvector for S*
            self.eigen_beta = None           # Dominant eigenvalue for B*
            self.eigen_beta_v = None         # Dominant eigenvector for B*
            self.b_initial = np.array([0.2, 0.2, 0.2, 0.2, 0.2])  # Exact as specified
            self.b_final = self.b_initial.copy()
            
            # 87D transformation storage
            self.S_matrix_87d = None          # T(E(X)) = S (expectation matrix in 87D)
            self.W_s_87d = None               # T(w[i,j]) = W_s (self observation in 87D)
            self.D_matrix_87d = None          # T(P_i_k | w_p_k) = D (position covariance in 87D)
 
            
            # ===== OBSERVATION STORAGE =====
            self.self_vector = None          # 1×25
            self.O_matrix = np.zeros((5, 25))  # 5×25 neighbor observations
            self.assignment = {}             # position -> expectation_row
            
            # ===== PROCESSING STATE =====
            self.processing_phase = "INITIAL"
            self.cycle_count = 0
            self.confidence_score = 0.0
            
            # Recycling tracking
            self.recycling_iteration = 0
            self.max_recycling_iterations = 25
            self.permutation_count = 0
            self.max_permutations = 5
            
            # ===== VOID & GROWTH TRACKING =====
            self.void_coordinates = set()
            
            # ===== MATRIX HISTORY (for debugging) =====
            self.D_matrices_history = deque(maxlen=10)
            self.b_vectors_history = deque(maxlen=10)
            self.B_matrices_history = deque(maxlen=10)
            
            # ===== PUBLIC NEXUS INTERFACE =====
            self.monitoring_active = False
            self.last_activity = time.time()
            
            # Fire creation axon
            self._fire_creation_axon()
            print(f"  ✓ Neuron initialized with exact flow specification")


    def _try_observe_with_locking(self, position: str, coordinate: Tuple) -> Optional[np.ndarray]:
        """Try to observe coordinate with locking, returns observation or None if locked"""
        if not coordinate:
            return np.zeros(25)
        
        # Skip if this is a void/membrane coordinate
        if coordinate in self.void_coordinates:
            return np.zeros(25)
        
        if hasattr(self, 'membrane_waiting') and coordinate in self.membrane_waiting.values():
            return np.zeros(25)
        
        if hasattr(self, 'membrane_reroutes') and coordinate in self.membrane_reroutes.values():
            return np.zeros(25)
        
        # Try to lock coordinate
        if not self.axon_network.lock_coordinate(coordinate, self.id):
            # Coordinate locked by someone else
            print(f"  🔒 {position} coordinate {coordinate} locked by another neuron")
            
            # Add to pending list for retry later
            if (position, coordinate) not in self.pending_coordinates:
                self.pending_coordinates.append((position, coordinate))
            
            return None  # Signal that we should try other positions first
        
        # We have the lock, proceed with observation
        try:
            xpath = self._coord_to_xpath(coordinate)
            element = self.dom_driver.find_element(By.XPATH, xpath)
            dom_state = self._observe_element(element)
            
            if dom_state.get('exists', False):
                obs_vector = self._dom_state_to_observation_vector(
                    dom_state, position, self.current_pattern_idx,
                    expectation_row=self.assignment.get(position)
                )
                
                # Release lock
                self.axon_network.unlock_coordinate(coordinate, self.id)
                
                return obs_vector
            else:
                # Void detected
                self._handle_void(position, coordinate)
                self.axon_network.unlock_coordinate(coordinate, self.id)
                return np.zeros(25)
                
        except Exception as e:
            # Error occurred, release lock
            self.axon_network.unlock_coordinate(coordinate, self.id)
            
            error_msg = str(e).lower()
            if "no such element" in error_msg or "stale" in error_msg:
                self._handle_void(position, coordinate)
            
            return np.zeros(25)

    # Utility reverse transform  
    def _dom_state_to_observation_vector_with_dict(self, dom_state: Dict, 
                                              expectation_dict: Dict[EnhancedGrandClass, AttributeExpression]) -> np.ndarray:
        """
        Convert DOM state to 25D vector using provided expectation dictionary
        """
        vector = np.zeros(25)
        
        if not dom_state.get('exists', False):
            return vector
        
        # Convert DOM attributes to our vocabulary
        our_attributes = self._dom_to_our_vocabulary(dom_state)
        
        # Evaluate each dimension
        all_dimensions = EnhancedGrandClass.get_all_dimensions()
        for i, dimension in enumerate(all_dimensions):
            if dimension in expectation_dict:
                expr = expectation_dict[dimension]
                observed_attrs = our_attributes.get(dimension, set())
                vector[i] = expr.evaluate(observed_attrs)
        
        return vector 
            
    # ===== Binary attribute relational transformation space =====

    def generate_permutation_matrix(self, m: int, k: int) -> np.ndarray:
        """
        Generate 5×5 permutation matrix for P_(m,k)[M(i)] = V[(m*i + k) MOD 5] #ignore -1 for starting position choice 
        """
        perm_matrix = np.zeros((5, 5), dtype=np.float32)
        for i in range(5):
            target_idx = (m * i + k) % 5
            perm_matrix[target_idx, i] = 1.0
        return perm_matrix
        

    def T(self, vectors_array: np.ndarray) -> np.ndarray: 
        """
        
        Transform n 25D vectors to n 87D binary vectors.
        
        Args:
            vectors_array: Shape (n, 25) - n vectors to transform together
        
        Returns:
            Shape (n, 87) - binary relational encoding
        """
        n = vectors_array.shape[0]
        output = np.zeros((n, 87), dtype=np.float32)
        
        # First 15 dimensions: combination features (already binary 0/1)
        output[:, :15] = vectors_array[:, 10:25]
        
        # For each base dimension d (0-8)
        for d in range(9):
            # Get values for this dimension across all vectors
            dim_values = vectors_array[:, d]
            
            # For each vector i
            for i in range(n):
                value_i = dim_values[i]
                
                # === SHARING QUESTIONS (4 flags) ===
                # Count how many vectors share this EXACT value
                same_mask = np.abs(dim_values - value_i) < 1e-6
                same_count = np.sum(same_mask)
                
                # Q1: ≥4 patterns share this value?
                if same_count >= 4:
                    output[same_mask, 15 + 8*d + 0] = 1
                
                # Q2: ≥3 patterns share this value?
                if same_count >= 3:
                    output[same_mask, 15 + 8*d + 1] = 1
                
                # Q3: Exactly 2 patterns share this value?
                if same_count == 2:
                    output[same_mask, 15 + 8*d + 2] = 1
                
                # Q4: Exactly 1 pattern has this value (unique)?
                if same_count == 1:
                    output[same_mask, 15 + 8*d + 3] = 1
                
                # === OPTIONALITY QUESTIONS (4 flags) ===
                # Only if value = 0.5 (asymmetric: 0.5 = 1, but 1 ≠ 0.5)
                if abs(value_i - 0.5) < 1e-6:
                    # Count how many vectors have 0.5 in this dimension
                    optional_mask = np.abs(dim_values - 0.5) < 1e-6
                    optional_count = np.sum(optional_mask)
                    
                    # Q5: ≥4 patterns have 0.5?
                    if optional_count >= 4:
                        output[optional_mask, 15 + 8*d + 4] = 1
                    
                    # Q6: ≥3 patterns have 0.5?
                    if optional_count >= 3:
                        output[optional_mask, 15 + 8*d + 5] = 1
                    
                    # Q7: Exactly 2 patterns have 0.5?
                    if optional_count == 2:
                        output[optional_mask, 15 + 8*d + 6] = 1
                    
                    # Q8: Exactly 1 pattern has 0.5?
                    if optional_count == 1:
                        output[optional_mask, 15 + 8*d + 7] = 1
                # If value ≠ 0.5, optionality flags remain 0 (asymmetric)
        
        return output


    #Tensor fallback array construction 

    def T_zeta(self) -> np.ndarray:
        """
        Collect ALL observations and transform to 5x6x87 relational tensor
        WITH void/membrane rerouting support
        """
        print("  🔧 Building T_zeta tensor with membrane awareness...")
        
        # Step 1: Collect 5x6x25 observation tensor
        O_25d = np.zeros((5, 6, 25))
        
        # Process any pending voids first
        if hasattr(self, 'membrane_waiting') and self.membrane_waiting:
            if hasattr(self.axon_network, 'void_system'):
                self.axon_network.void_system.process_voids()
        
        # For each pattern
        for pattern_idx, pattern_name in enumerate(self.pattern_names):
            # For each position (self + 5 neighbors)
            for pos_idx, position in enumerate(self.position_names):
                # Skip self position for membrane checks (self doesn't get rerouted)
                if position == "self":
                    coord = self.coordinate
                    use_reroute = False
                else:
                    # Get coordinate for this position
                    coord = self._get_coordinate_for_position(position)
                    use_reroute = True
                
                coord_to_observe = coord
                
                # ===== CHECK FOR MEMBRANE REROUTE (NEIGHBORS ONLY) =====
                if use_reroute and hasattr(self, 'membrane_reroutes') and position in self.membrane_reroutes:
                    reroute_coord = self.membrane_reroutes[position]
                    print(f"    🌀 T_zeta using reroute for {position}: {coord} → {reroute_coord}")
                    coord_to_observe = reroute_coord
                
                # ===== CHECK IF WAITING FOR MEMBRANE =====
                elif (use_reroute and hasattr(self, 'membrane_waiting') and 
                    position in self.membrane_waiting):
                    void_coord = self.membrane_waiting[position]
                    if hasattr(self.axon_network, 'void_system'):
                        reroute = self.axon_network.void_system.get_reroute(self.id, void_coord)
                        if reroute and reroute['reroute_to']:
                            # Reroute ready
                            if not hasattr(self, 'membrane_reroutes'):
                                self.membrane_reroutes = {}
                            self.membrane_reroutes[position] = reroute['reroute_to']
                            del self.membrane_waiting[position]
                            coord_to_observe = reroute['reroute_to']
                            print(f"    🌀 T_zeta got membrane reroute for {position}")
                        else:
                            # Still waiting
                            O_25d[pattern_idx, pos_idx, :] = np.zeros(25)
                            continue
                    else:
                        O_25d[pattern_idx, pos_idx, :] = np.zeros(25)
                        continue
                
                if not coord_to_observe:
                    O_25d[pattern_idx, pos_idx, :] = np.zeros(25)
                    continue
                    
                try:
                    # Observe element using this pattern's expectations
                    xpath = self._coord_to_xpath(coord_to_observe)
                    element = self.dom_driver.find_element(By.XPATH, xpath)
                    dom_state = self._observe_element(element)
                    
                    if dom_state.get('exists', False):
                        # Convert DOM state using this pattern's expectations
                        obs_vector = self._dom_state_to_observation_vector(
                            dom_state, 
                            position, 
                            pattern_idx,
                            expectation_row=None
                        )
                        O_25d[pattern_idx, pos_idx, :] = obs_vector
                        
                        # If this was a reroute, log successful observation
                        if use_reroute and coord_to_observe != coord:
                            print(f"    ✓ T_zeta successful reroute observation at {position}")
                    else:
                        # Void at observation coordinate
                        if use_reroute and coord_to_observe != coord:
                            # Reroute failed
                            print(f"    🌀 T_zeta reroute failed at {position}")
                            if hasattr(self, 'membrane_reroutes') and position in self.membrane_reroutes:
                                del self.membrane_reroutes[position]
                            
                            # Register original as void
                            if coord:
                                self._handle_void(position, coord)
                        
                        O_25d[pattern_idx, pos_idx, :] = np.zeros(25)
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    if "no such element" in error_msg or "stale" in error_msg:
                        # Void detected
                        if use_reroute:
                            if coord_to_observe != coord:
                                # Reroute failed
                                print(f"    🌀 T_zeta reroute void at {position}")
                                if hasattr(self, 'membrane_reroutes') and position in self.membrane_reroutes:
                                    del self.membrane_reroutes[position]
                            
                            # Register original as void
                            if coord:
                                self._handle_void(position, coord)
                    
                    O_25d[pattern_idx, pos_idx, :] = np.zeros(25)
        
        # Step 2: Transform to 5x6x87 relational tensor
        self.T_obs = np.zeros((5, 6, 87))
        
        # For each position
        for pos_idx in range(6):
            # Get all 5 pattern vectors at this position
            position_vectors = O_25d[:, pos_idx, :]  # 5×25
            
            # Transform together with T()
            transformed = self.T(position_vectors)  # 5×87
            
            # Store in tensor
            self.T_obs[:, pos_idx, :] = transformed
        
        print(f"  ✓ T_zeta tensor built with membrane support: {self.T_obs.shape}")
        return self.T_obs

    #===== Public access statistical methods - target setup
    def set_targeted_learning_mode(self: Optional[Set[Tuple[int, ...]]] = None):
        """
        Enable targeted learning mode with a constrained coordinate space.
        In this mode, neurons respect existing coordination but don't create new signals.
        """
        self.learning_mode = "TARGETED"
        
        print(f"🧠 Neuron {self.id} set to {self.learning_mode} learning mode")

    def _process_pending_reroutes(self):
        """Process any pending membrane reroutes"""
        if not hasattr(self, 'membrane_waiting') or not self.membrane_waiting:
            return
        
        if hasattr(self.axon_network, 'void_system'):
            # Process voids in the system
            self.axon_network.void_system.process_voids()
            
            # Check for any completed reroutes
            for position, void_coord in list(self.membrane_waiting.items()):
                reroute = self.axon_network.void_system.get_reroute(self.id, void_coord)
                if reroute and reroute['reroute_to']:
                    # Got a reroute
                    if not hasattr(self, 'membrane_reroutes'):
                        self.membrane_reroutes = {}
                    self.membrane_reroutes[position] = reroute['reroute_to']
                    del self.membrane_waiting[position]
                    print(f"    🌀 Processed reroute for {position}: {reroute['reroute_to']}")

    def _try_observe_with_void_handling(self, position, coordinate, is_reroute=False):
        """Try to observe coordinate with void handling"""
        if not coordinate:
            return np.zeros(25)
        
        # Try to lock coordinate
        if not self.axon_network.lock_coordinate(coordinate, self.id):
            print(f"    🔒 {position} coordinate locked, will retry")
            return np.zeros(25)
        
        try:
            xpath = self._coord_to_xpath(coordinate)
            element = self.dom_driver.find_element(By.XPATH, xpath)
            dom_state = self._observe_element(element)
            
            if dom_state.get('exists', False):
                # Successful observation
                obs_vector = self._dom_state_to_observation_vector(
                    dom_state, position, self.current_pattern_idx,
                    expectation_row=self.assignment.get(position)
                )
                
                # If this was a reroute and worked, log success
                if is_reroute:
                    print(f"    ✅ Successful reroute observation at {position}")
                
                return obs_vector
            else:
                # Element doesn't exist (void)
                print(f"    🌀 Void at coordinate {coordinate} for {position}")
                
                # Register void if it's not a reroute (reroute shouldn't be void)
                if not is_reroute:
                    self._handle_void(position, coordinate)
                else:
                    # Reroute failed - clear it
                    if hasattr(self, 'membrane_reroutes') and position in self.membrane_reroutes:
                        del self.membrane_reroutes[position]
                    print(f"    ❌ Reroute failed at {position}")
                
                return np.zeros(25)
                
        except Exception as e:
            error_msg = str(e).lower()
            if "no such element" in error_msg or "stale" in error_msg:
                # Void detected
                print(f"    🌀 Void detected at {position} ({coordinate})")
                
                if not is_reroute:
                    self._handle_void(position, coordinate)
                else:
                    # Reroute failed
                    if hasattr(self, 'membrane_reroutes') and position in self.membrane_reroutes:
                        del self.membrane_reroutes[position]
                    print(f"    ❌ Reroute void at {position}")
                
            else:
                print(f"    ⚠ Error observing {position}: {e}")
            
            return np.zeros(25)
            
        finally:
            # Always release lock
            self.axon_network.unlock_coordinate(coordinate, self.id)
            
    def _get_coordinate_to_observe(self, position):
        """Get coordinate to observe, checking for reroutes first"""
        original_coord = self._get_coordinate_for_position(position)
        
        # 1. Check if we have an active reroute for this position
        if hasattr(self, 'membrane_reroutes') and position in self.membrane_reroutes:
            reroute_coord = self.membrane_reroutes[position]
            print(f"    🌀 Using reroute for {position}: {original_coord} → {reroute_coord}")
            return reroute_coord, True
        
        # 2. Check if we're waiting for a membrane reroute
        if hasattr(self, 'membrane_waiting') and position in self.membrane_waiting:
            void_coord = self.membrane_waiting[position]
            if hasattr(self.axon_network, 'void_system'):
                reroute = self.axon_network.void_system.get_reroute(self.id, void_coord)
                if reroute and reroute['reroute_to']:
                    # Got a reroute
                    if not hasattr(self, 'membrane_reroutes'):
                        self.membrane_reroutes = {}
                    self.membrane_reroutes[position] = reroute['reroute_to']
                    del self.membrane_waiting[position]
                    print(f"    🌀 Got membrane reroute for {position}: {reroute['reroute_to']}")
                    return reroute['reroute_to'], True
            # Still waiting for reroute
            print(f"    ⏳ Waiting for membrane reroute at {position}")
            return None, False
        
        # 3. Use original coordinate
        return original_coord, False

    def _phase3_targeted_observation_with_locking(self):
        """Targeted mode with void rerouting"""
        for pos_idx, position in enumerate(self.neighbor_positions):
            coord, is_reroute = self._get_coordinate_to_observe(position)
            
            if not coord:
                self.O_matrix[pos_idx] = np.zeros(25)
                continue
            
            # ===== COORDINATION CHECK =====
            if self.axon_network.coordinate_has_neuron(coord):
                # Skip - already handled by another neuron
                self.O_matrix[pos_idx] = np.zeros(25)
                continue
            
            # ===== LOCKING CHECK =====
            if not self.axon_network.lock_coordinate(coord, self.id):
                # Coordinate locked, skip for now
                self.O_matrix[pos_idx] = np.zeros(25)
                continue
            
            try:
                # Observe with lock
                xpath = self._coord_to_xpath(coord)
                element = self.dom_driver.find_element(By.XPATH, xpath)
                dom_state = self._observe_element(element)
                
                if dom_state.get('exists', False):
                    obs_vector = self._dom_state_to_observation_vector(
                        dom_state, position, self.current_pattern_idx,
                        expectation_row=self.assignment.get(position)
                    )
                    self.O_matrix[pos_idx] = obs_vector
                else:
                    # Void detected
                    if not is_reroute:  # Don't register voids from reroutes
                        self._handle_void(position, coord)
                    self.O_matrix[pos_idx] = np.zeros(25)
                    
            except Exception as e:
                error_msg = str(e).lower()
                if ("no such element" in error_msg or "stale" in error_msg) and not is_reroute:
                    self._handle_void(position, coord)
                self.O_matrix[pos_idx] = np.zeros(25)
                
            finally:
                self.axon_network.unlock_coordinate(coord, self.id)


    def get_cycle_statistics(self) -> Dict:
        """Get comprehensive statistics for current cycle"""
        return {
            'cycle': self.cycle_count,
            'pattern': self.current_pattern,
            'confidence': float(self.confidence_score),
            
            # Matrix states
            'b_vector_entropy': float(-np.sum(self.b_vector * np.log(self.b_vector + 1e-10))),
            'B_matrix_trace': float(np.trace(self.B_matrix)),
            'B_matrix_determinant': float(np.linalg.det(self.B_matrix)),
            
            # Eigen analysis
            'dominant_eigenvalue_alpha': float(self.eigen_alpha) if self.eigen_alpha else 0.0,
            'dominant_eigenvalue_beta': float(self.eigen_beta) if self.eigen_beta else 0.0,
            
            # 87D transformation metrics
            'self_observation_87d_norm': float(np.linalg.norm(self.W_s_87d)) if hasattr(self, 'W_s_87d') else 0.0,
            'S_matrix_87d_norm': float(np.linalg.norm(self.S_matrix_87d)) if hasattr(self, 'S_matrix_87d') else 0.0,
            'D_matrix_87d_norm': float(np.linalg.norm(self.D_matrix_87d)) if hasattr(self, 'D_matrix_87d') else 0.0,
            
            # Position assignment quality
            'assignment_consistency': len(set(self.assignment.values())) / 5.0 if self.assignment else 0.0,
            'void_density': len(self.void_coordinates) / (self.cycle_count + 1),
            
            # Recycling state
            'recycling_completion': self.recycling_iteration / self.max_recycling_iterations,
            'permutation_completion': self.permutation_count / self.max_permutations,
            
            # Timing (if you want to add)
            'phase_duration': {
                'self_observation': 0.0,    # Can add timing
                'competitive_assignment': 0.0,
                'neighbor_observation': 0.0,
                'matrix_updates': 0.0,
                'confidence_decision': 0.0
            }
        }

    def get_pattern_transition_history(self) -> List[Dict]:
        """Get history of pattern transitions"""
        # You'd need to store this history in the neuron
        if not hasattr(self, 'pattern_transition_history'):
            self.pattern_transition_history = []
        return self.pattern_transition_history.copy()
        


    #==== TURE BINARY T -- covariance simmilarity resolution for unknown =====
   
    def _init_T_exp(self) -> np.ndarray:
        """
        Construct 5x6x87 expectation tensor exactly as specified:
        1. For each position k (0-5), take the vectors from each pattern at that position
        2. Transform those 5 vectors together with T()
        3. Get 87D relational encoding for that position across patterns
        """
        # Initialize 5x6x87 expectation tensor
        self.T_exp = np.zeros((5, 6, 87))
        
        # Get all 5 pattern expectation tensors
        pattern_expectations = []
        for pattern_name in self.pattern_names:
            pattern_idx = self._get_pattern_idx(pattern_name)
            # Get full expectation tensor for this pattern (6 positions × 25D)
            pattern_tensor = self.expectation_tensor[pattern_idx]  # 6×25
            pattern_expectations.append(pattern_tensor)
        
        # For each position (0-5 = self, parent, up, down, left, right)
        for pos_idx in range(6):
            # Collect vectors at this position from all patterns
            position_vectors = np.zeros((5, 25))
            for p_idx in range(5):
                position_vectors[p_idx] = pattern_expectations[p_idx][pos_idx]
            
            # Transform these 5 vectors together with T()
            transformed = self.T(position_vectors)  # 5×87
            
            # Store in tensor - each position gets its specific relational encoding
            self.T_exp[:, pos_idx, :] = transformed
        
        return self.T_exp

    def _extract_all_expectations_once(self):
        """Extract ALL expectation data from ROSE once and store locally"""
        pattern_names = Neuron.pattern_names 
        position_names = Neuron.position_names
        # ===== 1. NUMERIC TENSOR: 5×6×25 =====
        self.expectation_tensor = np.zeros((5, 6, 25))
        
        # ===== 2. EXPECTATION DICTIONARIES: 5×6 dicts =====
        self.expectation_dicts = np.empty((5, 6), dtype=object)
        
        # ===== 3. B MATRICES: 5 patterns × 5×5 each =====
        self.B_matrices_dict = {}
        
        # ===== 4. PATTERN SUM EXPECTATIONS: 5×25 =====
        self.pattern_sum_expectations = np.zeros((5, 25))
        
        # ===== 5. PATTERN SELF EXPECTATIONS: 5×25 (for X matrix) =====
        self.self_expectation_matrix = np.zeros((5, 25))
        
        # ===== 6. PATTERN NEIGHBOR EXPECTATIONS: 5×5×25 (for P matrices) =====
        self.neighbor_expectation_tensor = np.zeros((5, 5, 25))
        
        # Use the class variables directly
        for p_idx, pattern_name in enumerate(Neuron.pattern_names):
            pattern = self.rose.get_pattern(pattern_name)
            if not pattern:
                continue
            
            # Store B matrix
            self.B_matrices_dict[pattern_name] = pattern.position_bias_matrix.copy()
            
            # Track sum for this pattern
            pattern_sum = np.zeros(25)
            
            for pos_idx, position in enumerate(Neuron.position_names):
                # Get expectation dictionary
                expectation_dict = pattern.get_vector(position)
                
                # Store dictionary
                self.expectation_dicts[p_idx, pos_idx] = expectation_dict
                
                # Convert to numeric vector
                numeric_vector = self._expectation_dict_to_numeric_vector(expectation_dict)
                
                # Store in tensor
                self.expectation_tensor[p_idx, pos_idx, :] = numeric_vector
                
                # Accumulate to pattern sum (ALL 6 vectors)
                pattern_sum += numeric_vector
                
                # Store in specialized matrices
                if position == "self":
                    self.self_expectation_matrix[p_idx, :] = numeric_vector
                else:  # Neighbor position
                    neighbor_idx = Neuron.position_names.index(position) - 1
                    self.neighbor_expectation_tensor[p_idx, neighbor_idx, :] = numeric_vector
            
            # Store the complete pattern sum (all 6 vectors)
            self.pattern_sum_expectations[p_idx, :] = pattern_sum
            
            print(f"  ✓ Pattern {pattern_name}: sum vector norm = {np.linalg.norm(pattern_sum):.3f}")
        
        print(f"  ✓ Pattern sums initialized: shape {self.pattern_sum_expectations.shape}")

    def _expectation_dict_to_numeric_vector(self, expectation_dict: Dict[EnhancedGrandClass, AttributeExpression]) -> np.ndarray:
        """Convert expectation dictionary to 25D numeric vector"""
        vector = np.zeros(25)
        all_dimensions = EnhancedGrandClass.get_all_dimensions()
        
        for i, dimension in enumerate(all_dimensions):
            if dimension in expectation_dict:
                expr = expectation_dict[dimension]
                
                # Check expression type
                if expr.logic == LogicType.ANY:
                    vector[i] = 0.5  # ANY = 0.5 (uncertain)
                elif expr.logic == LogicType.NOT and (not expr.attributes or len(expr.attributes) == 0):
                    vector[i] = 0.0  # ABSENT = 0.0
                else:
                    vector[i] = 1.0  # Specific expectation = 1.0
        
        return vector
        
    def _get_pattern_idx(self, pattern_name: str) -> int:
        """Get index of pattern in pattern_names"""
        if pattern_name in self.pattern_names:
            return self.pattern_names.index(pattern_name)
        return 4  # Default to UNKNOWN
    

    # ===== STEP 0: Create transformed expectations =====

    def _resolve_equality_with_dot_product(self, candidate_rows: List[int], expectation_col: int) -> int:
            """
            Resolve equality by dot product in 25D space as specified.
            """
            if not hasattr(self, 'self_vector') or self.self_vector is None:
                return candidate_rows[0]  # Fallback
            
            best_dot = -1
            best_row = candidate_rows[0]
            
            for row_idx in candidate_rows:
                # Get expectation vector for this row (from current pattern's P matrix)
                expectation_vector = self.P_matrix[row_idx]  # 25D
                
                # Dot product with self observation
                dot_value = np.dot(expectation_vector, self.self_vector)
                
                if dot_value > best_dot:
                    best_dot = dot_value
                    best_row = row_idx
            
            return best_row
        
        # ===== PERMUTATION TRANSFORM Y =====
    
    def _apply_permutation_transform(self, indices: List[int], P_matrix: np.ndarray) -> np.ndarray:
        """
        Implement Y transform to reorder expectation matrix.
        indices: from H(B) operator
        Returns: Permuted P_i_k matrix
        """
        if P_matrix.shape[0] != 5:
            return P_matrix
        
        # Create permutation matrix
        perm_matrix = np.zeros((5, 5))
        for new_idx, old_idx in enumerate(indices):
            perm_matrix[new_idx, old_idx] = 1
        
        # Apply permutation: P_permuted = perm_matrix @ P
        return perm_matrix @ P_matrix
    

    def _apply_hierarchical_selection(self, B_matrix: np.ndarray) -> List[int]:
            """
            Implement H(B) operator as specified:
            - Choose 5 values across columns
            - Hierarchical selection: choose largest i for each j
            - If equality, resolve with dot product selection in 25D space
            - Returns index list for permutation
            """
            indices = []
            available_rows = list(range(5))
            
            for j in range(5):  # For each column j (expectation)
                best_value = -1
                best_rows = []
                
                # Find rows with highest probability in this column
                for i in available_rows:
                    value = B_matrix[i, j]
                    if value > best_value:
                        best_value = value
                        best_rows = [i]
                    elif abs(value - best_value) < 1e-10:  # Equality within tolerance
                        best_rows.append(i)
                
                if len(best_rows) == 1:
                    # Unique maximum
                    selected_row = best_rows[0]
                else:
                    # Resolve equality with dot product in 25D space
                    selected_row = self._resolve_equality_with_dot_product(best_rows, j)
                
                indices.append(selected_row)
                available_rows.remove(selected_row)
            
            return indices
        
    # Rename to clarify what it does

    def _compute_dominant_eigen(self, matrix: np.ndarray) -> Tuple[float, np.ndarray]:
            """Compute dominant eigenvalue and eigenvector"""
            try:
                eigenvalues, eigenvectors = np.linalg.eig(matrix)
                dominant_idx = np.argmax(np.abs(eigenvalues))
                eigenvalue = np.abs(eigenvalues[dominant_idx])
                eigenvector = eigenvectors[:, dominant_idx].real
                
                # Normalize eigenvector
                norm = np.linalg.norm(eigenvector)
                if norm > 0:
                    eigenvector = eigenvector / norm
                
                return float(eigenvalue), eigenvector
            except:
                return 1.0, np.ones(matrix.shape[0]) / np.sqrt(matrix.shape[0])
        
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector to sum to 1"""
        if vector.sum() > 0:
            return vector / vector.sum()
        return np.ones_like(vector) / len(vector)
  
    def _initialize_unknown_B_matrix(self):
        """Initialize B matrix for UNKNOWN pattern with proper uniform distribution"""
        if self.current_pattern == "UNKNOWN":
            print("  🔄 Initializing UNKNOWN B matrix")
            # Start with uniform distribution but with slight noise to break symmetry
            self.B_matrix = np.ones((5, 5)) / 5.0
            
            # Add tiny random variations to prevent perfect symmetry
            noise = np.random.uniform(-0.01, 0.01, (5, 5))
            self.B_matrix += noise
            
            # Row-normalize
            row_sums = self.B_matrix.sum(axis=1, keepdims=True)
            self.B_matrix = self.B_matrix / row_sums
            
            # Initialize unknown permutation cache if not already done
            if not hasattr(self, 'unknown_perm_cache'):
                self.unknown_perm_cache = {
                    't_gamma_tensor': None,
                    'initial_bias_updated': False,
                    'm_cycles': {
                        1: {'k_values': {}, 'W_p_matrix': None, 'completed': False},
                        2: {'k_values': {}, 'W_p_matrix': None, 'completed': False},
                        3: {'k_values': {}, 'W_p_matrix': None, 'completed': False},
                        4: {'k_values': {}, 'W_p_matrix': None, 'completed': False}
                    },
                    'current_m': 1,
                    'permutations_generated': set(),
                    'max_m': 4,
                    'cycle_history': []
                }
            
            print(f"  ✓ UNKNOWN B matrix initialized (trace: {np.trace(self.B_matrix):.3f})")
            
    
    def _initialize_matrices_from_extracted_data(self):
        """Initialize all operational matrices from extracted data"""
        pattern_idx = self.current_pattern_idx
        
        # X matrix: self expectations for all patterns (5×25)
        self.X_matrix = self.self_expectation_matrix.copy()
        
        # P matrix: neighbor expectations for current pattern (5×25)
        self.P_matrix = self.neighbor_expectation_tensor[pattern_idx].copy()
        
        # B matrix: position bias matrix for current pattern
        if self.current_pattern == "UNKNOWN":
            self.B_matrix = np.ones((5, 5)) / 5.0  # Uniform confusion matrix
        else:
            self.B_matrix = self.B_matrices_dict[self.current_pattern].copy()
        
        # b vector: pattern bias vector
        self.b_vector = np.ones(5) / 5.0
        
        # V matrix: eigen uncertainty matrix
        self.V_matrix = np.eye(5)
        
        # FIX: ADD THIS LINE - initialize pattern_base_vectors
        self.pattern_base_vectors = self.self_expectation_matrix[:, :9].copy()
        
        
    # ===== PUBLIC NEXUS INTERFACE=====

    @property
    def monitoring_active(self):
        return self.processing_phase == "MONITORING"
    
    @monitoring_active.setter
    def monitoring_active(self, value: bool):
        if not value and self.processing_phase == "MONITORING":
            self.processing_phase = "PROCESSING"
    
    # ===== PHASE 1: SELF OBSERVATION =====
 
    def _get_self_observation_25d(self) -> np.ndarray:
        """Get self observation in 25D space"""
        try:
            # Observe self element
            xpath = self._coord_to_xpath(self.coordinate)
            element = self.dom_driver.find_element(By.XPATH, xpath)
            dom_state = self._observe_element(element)
            
            if dom_state.get('exists', False):
                # Convert to observation vector
                return self._dom_state_to_observation_vector(
                    dom_state, 
                    "self", 
                    self.current_pattern_idx,
                    expectation_row=None
                )
        except:
            pass
        
        return np.zeros(25)

    def _update_b_from_covariance(self, covariance_matrix: np.ndarray, b_vector: np.ndarray) -> np.ndarray:
        """Update bias vector from covariance matrix eigen decomposition"""
        eigen_value, eigen_vector = self._compute_dominant_eigen(covariance_matrix)
        
        # Create eigen matrix
        eigen_matrix = eigen_value * np.outer(eigen_vector, eigen_vector)
        
        # Update bias
        updated_b = eigen_matrix @ b_vector
        return self._normalize_vector(updated_b)
    
    def _phase1_self_observation(self):
        """Self observation with coordinate locking"""
        # Our own coordinate - we should always be able to lock it
        if self.axon_network.lock_coordinate(self.coordinate, self.id):
            try:
                xpath = self._coord_to_xpath(self.coordinate)
                element = self.dom_driver.find_element(By.XPATH, xpath)
                dom_state = self._observe_element(element)
                
                if dom_state.get('exists', False):
                    self.self_vector = self._dom_state_to_observation_vector(
                        dom_state, "self", self.current_pattern_idx, None
                    )
                else:
                    # Our own element doesn't exist? This is catastrophic
                    print(f"  ⚠️  Our own coordinate {self.coordinate} doesn't exist!")
                    self.self_vector = np.zeros(25)
                    
            finally:
                # Always release our own coordinate
                self.axon_network.unlock_coordinate(self.coordinate, self.id)
        else:
            # Should never happen, but handle gracefully
            print(f"  ⚠️  Could not lock our own coordinate {self.coordinate}")
            self.self_vector = np.zeros(25)
            

    
    def _build_void_aware_t_gamma_tensor(self) -> np.ndarray:
        """
        T_gamma: Build 5×5×87 base positional tensor WITH void rerouting
        For each neighbor position, observe with all 5 pattern expectations
        Uses membrane reroutes when available
        """
        print("  🔧 Building void-aware T_gamma tensor...")
        
        # We need to observe each neighbor position with each pattern's expectations
        T_gamma_25d = np.zeros((5, 5, 25))
        
        for pos_idx, position in enumerate(self.neighbor_positions):
            # Get coordinate for this position (with potential reroute)
            original_coord = self._get_coordinate_for_position(position)
            coord_to_observe = original_coord
            
            # ===== CHECK FOR MEMBRANE REROUTE =====
            if hasattr(self, 'membrane_reroutes') and position in self.membrane_reroutes:
                reroute_coord = self.membrane_reroutes[position]
                print(f"    🌀 Using reroute for {position}: {original_coord} → {reroute_coord}")
                coord_to_observe = reroute_coord
            
            # ===== CHECK IF WAITING FOR MEMBRANE PROCESSING =====
            elif hasattr(self, 'membrane_waiting') and position in self.membrane_waiting:
                void_coord = self.membrane_waiting[position]
                # Check if membrane has processed this void
                if hasattr(self.axon_network, 'void_system'):
                    reroute = self.axon_network.void_system.get_reroute(self.id, void_coord)
                    if reroute and reroute['reroute_to']:
                        # Reroute ready - use it and update membrane_reroutes
                        if not hasattr(self, 'membrane_reroutes'):
                            self.membrane_reroutes = {}
                        self.membrane_reroutes[position] = reroute['reroute_to']
                        del self.membrane_waiting[position]
                        coord_to_observe = reroute['reroute_to']
                        print(f"    🌀 Membrane provided reroute for {position}: {reroute['reroute_to']}")
                    else:
                        # Still waiting for membrane processing
                        print(f"    ⏳ Waiting for membrane processing of void at {position}")
                        T_gamma_25d[:, pos_idx, :] = np.zeros((5, 25))
                        continue
                else:
                    # No void system available
                    T_gamma_25d[:, pos_idx, :] = np.zeros((5, 25))
                    continue
            
            if not coord_to_observe:
                print(f"    ⚠ No coordinate for {position}, using zeros")
                T_gamma_25d[:, pos_idx, :] = np.zeros((5, 25))
                continue
            
            # ===== OBSERVE COORDINATE (WITH VOID HANDLING) =====
            try:
                xpath = self._coord_to_xpath(coord_to_observe)
                element = self.dom_driver.find_element(By.XPATH, xpath)
                dom_state = self._observe_element(element)
                
                if not dom_state.get('exists', False):
                    # Element doesn't exist at rerouted coordinate either
                    print(f"    ⚠ Element not found at {position} ({coord_to_observe})")
                    
                    # If this was a reroute that failed, clear it and mark as void
                    if coord_to_observe != original_coord:
                        print(f"    🌀 Reroute failed, marking original as void: {original_coord}")
                        if hasattr(self, 'membrane_reroutes') and position in self.membrane_reroutes:
                            del self.membrane_reroutes[position]
                        
                        # Register original coordinate as void
                        if original_coord:
                            self._handle_void(position, original_coord)
                    
                    T_gamma_25d[:, pos_idx, :] = np.zeros((5, 25))
                    continue
                    
                # ===== SUCCESSFUL OBSERVATION =====
                # For each pattern, create observation using that pattern's expectations
                for pattern_idx in range(5):
                    # Get expectation dictionary for this pattern and position
                    if position == "parent":
                        pos_dict_idx = 1
                    elif position == "up":
                        pos_dict_idx = 2
                    elif position == "down":
                        pos_dict_idx = 3
                    elif position == "left":
                        pos_dict_idx = 4
                    elif position == "right":
                        pos_dict_idx = 5
                    else:
                        pos_dict_idx = 0
                    
                    expectation_dict = self.expectation_dicts[pattern_idx, pos_dict_idx]
                    
                    # Create observation vector using this pattern's expectations
                    obs_vector = self._dom_state_to_observation_vector_with_dict(
                        dom_state, expectation_dict
                    )
                    T_gamma_25d[pattern_idx, pos_idx, :] = obs_vector
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "no such element" in error_msg or "stale" in error_msg:
                    # Void detected at rerouted coordinate
                    print(f"    🌀 Void at rerouted coordinate {coord_to_observe}")
                    
                    # Clear failed reroute
                    if hasattr(self, 'membrane_reroutes') and position in self.membrane_reroutes:
                        del self.membrane_reroutes[position]
                    
                    # Register original as void if not already
                    if original_coord:
                        self._handle_void(position, original_coord)
                else:
                    print(f"    ⚠ Failed to observe {position} ({coord_to_observe}): {e}")
                
                T_gamma_25d[:, pos_idx, :] = np.zeros((5, 25))
                continue
        
        # Transform to 87D
        T_gamma_87d = np.zeros((5, 5, 87))
        for pos_idx in range(5):
            # Get all patterns at this position (5×25)
            patterns_at_pos = T_gamma_25d[:, pos_idx, :]
            
            # Transform together using T()
            transformed = self.T(patterns_at_pos)  # 5×87
            T_gamma_87d[:, pos_idx, :] = transformed
        
        print(f"  ✓ Void-aware T_gamma tensor built: shape {T_gamma_87d.shape}")
        
        # Log any pending membrane waits
        if hasattr(self, 'membrane_waiting') and self.membrane_waiting:
            print(f"  ⏳ Still waiting for {len(self.membrane_waiting)} membrane reroutes")
        
        return T_gamma_87d

    def _apply_gamma_update_to_B(self):
        """Apply γ eigen update directly to B matrix for UNKNOWN with void awareness"""
        print("  🔧 Applying γ update to B matrix with void awareness...")
        
        # Step 1: Build void-aware T_gamma tensor if not already done
        if self.unknown_perm_cache['t_gamma_tensor'] is None:
            print("  🔧 Building void-aware T_gamma tensor for γ update...")
            self.unknown_perm_cache['t_gamma_tensor'] = self._build_void_aware_t_gamma_tensor()
        
        T_gamma = self.unknown_perm_cache['t_gamma_tensor']  # 5×5×87
        
        # Check if tensor has any non-zero observations
        if np.all(T_gamma == 0):
            print("  ⚠ T_gamma tensor is all zeros (all voids?) - skipping γ update")
            return
        
        # Step 2: Compute T_gamma covariance matrix
        # Flatten positions: 5 patterns × (5×87) = 5×435
        T_gamma_flat = T_gamma.reshape(5, -1)
        
        # Compute covariance: G_gamma = T_gamma @ T_gamma.T (5×5)
        G_gamma = T_gamma_flat @ T_gamma_flat.T
        
        # Check if covariance is valid
        if np.all(G_gamma == 0):
            print("  ⚠ G_gamma covariance is all zeros - skipping γ update")
            return
        
        # Normalize rows (makes it a proper probability matrix)
        G_gamma_normalized = G_gamma.copy()
        row_sums = G_gamma_normalized.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        G_gamma_normalized = G_gamma_normalized / row_sums
        
        # Step 3: Eigen decomposition γ
        self.eigen_gamma, self.eigen_gamma_v = self._compute_dominant_eigen(G_gamma_normalized)
        
        # Step 4: Update B matrix with γ (not b_initial!)
        if self.eigen_gamma_v is not None:
            # Create γ update matrix
            M_gamma = self.eigen_gamma * np.outer(self.eigen_gamma_v, self.eigen_gamma_v)
            
            # Apply to B matrix: B_new = normalize(M_gamma @ B_old)
            B_updated = M_gamma @ self.B_matrix
            
            # Row-normalize to keep it a proper probability matrix
            row_sums = B_updated.sum(axis=1, keepdims=True)
            B_updated_normalized = np.divide(B_updated, row_sums, where=row_sums != 0)
            
            # Update B matrix
            self.B_matrix = B_updated_normalized
            self.unknown_perm_cache['cycle_history'].append('gamma_B')
            
            print(f"  ✓ γ = {self.eigen_gamma:.3f}")
            print(f"    B matrix trace after γ: {np.trace(self.B_matrix):.3f}")
            
            # Log membrane status
            if hasattr(self, 'membrane_waiting') and self.membrane_waiting:
                print(f"    ⏳ Still waiting for {len(self.membrane_waiting)} membrane reroutes")
            if hasattr(self, 'membrane_reroutes') and self.membrane_reroutes:
                print(f"    ✅ Using {len(self.membrane_reroutes)} active reroutes")
        
        self.unknown_perm_cache['b_matrix_updated'] = True
        
        # Log γ update with membrane info
        membrane_info = {}
        if hasattr(self, 'membrane_waiting'):
            membrane_info['waiting_for'] = list(self.membrane_waiting.keys())
        if hasattr(self, 'membrane_reroutes'):
            membrane_info['active_reroutes'] = list(self.membrane_reroutes.keys())
        
        self.fire_axon('UNKNOWN_UPDATE', {
            'update_type': 'gamma_B_matrix',
            'eigen_gamma': float(self.eigen_gamma) if self.eigen_gamma else 0.0,
            'B_matrix_trace': float(np.trace(self.B_matrix)),
            'B_matrix_diag': np.diag(self.B_matrix).tolist(),
            'history': self.unknown_perm_cache['cycle_history'].copy(),
            'membrane_status': membrane_info
        })


    def _filter_observation_with_expectation(self, observation: np.ndarray, 
                                            expectation_dict: Dict) -> np.ndarray:
        """
        Filter an observation through expectation dictionary
        Returns expectation-filtered observation vector
        """
        filtered = np.zeros_like(observation)
        
        # Convert DOM attributes to our vocabulary
        dom_state = {'exists': True}  # Simplified - in real code, would have actual DOM state
        our_attributes = self._dom_to_our_vocabulary(dom_state)
        
        # Evaluate each dimension
        all_dimensions = EnhancedGrandClass.get_all_dimensions()
        for i, dimension in enumerate(all_dimensions):
            if dimension in expectation_dict:
                expr = expectation_dict[dimension]
                observed_attrs = our_attributes.get(dimension, set())
                filtered[i] = expr.evaluate(observed_attrs)
        

    # ===== PHASE 2: COMPETITIVE ASSIGNMENT =====
    def _phase2_competitive_assignment(self):
        """Phase 2 - Clean version without ω"""
        # 1. H(B) gives indices (B matrix already γ-updated for UNKNOWN)
        indices = self._apply_hierarchical_selection(self.B_matrix)
        self.hierarchical_indices = indices.copy()
        
        # 2. Y applies permutation to expectation matrix
        P_i = self.P_matrix
        P_i_k = self._apply_permutation_transform(indices, P_i)
        self.P_permuted = P_i_k
        
        # 3. Store assignment
        self.assignment = {}
        for pos_idx, expectation_row in enumerate(indices):
            position = self.neighbor_positions[pos_idx] if pos_idx < len(self.neighbor_positions) else f"pos_{pos_idx}"
            self.assignment[position] = expectation_row
        
        # Log assignment
        self.fire_axon('HIERARCHICAL_ASSIGNMENT', {
            'indices': indices,
            'assignment': self.assignment,
            'B_matrix_trace': float(np.trace(self.B_matrix)),
            'B_matrix_γ_updated': self.unknown_perm_cache.get('b_matrix_updated', False) 
                                if self.current_pattern == "UNKNOWN" else False
        })
        
    # ===== Phase 3 : Neighbor processing ====== 


    def _observe_coordinate(self, coordinate: Tuple[int, ...]) -> np.ndarray:
        """Observe a coordinate and return 25D vector"""
        try:
            xpath = self._coord_to_xpath(coordinate)
            element = self.dom_driver.find_element(By.XPATH, xpath)
            dom_state = self._observe_element(element)
            
            if dom_state.get('exists', False):
                # Use current pattern's expectations
                return self._dom_state_to_observation_vector(
                    dom_state,
                    "neighbor",
                    self.current_pattern_idx,
                    expectation_row=None
                )
        except Exception as e:
            print(f"  ⚠ Failed to observe {coordinate}: {e}")
        
        return np.zeros(25)

    def _phase3_neighbor_observation(self):
        """Observe all neighbors with void rerouting support"""
        print(f"  🔄 Observing neighbors with void rerouting")
        
        observations = {}  # position -> observation vector
        positions_to_process = self.neighbor_positions.copy()
        
        # Process any pending membrane reroutes first
        self._process_pending_reroutes()
        
        for position in positions_to_process:
            # Get the coordinate to observe (original or rerouted)
            coord_to_observe, is_reroute = self._get_coordinate_to_observe(position)
            
            if not coord_to_observe:
                print(f"    ⚠ No coordinate for {position}")
                observations[position] = np.zeros(25)
                continue
            
            # Try to observe with locking
            obs_vector = self._try_observe_with_void_handling(position, coord_to_observe, is_reroute)
            observations[position] = obs_vector
        
        # Populate O_matrix
        for pos_idx, position in enumerate(self.neighbor_positions):
            if position in observations:
                self.O_matrix[pos_idx] = observations[position]
            else:
                self.O_matrix[pos_idx] = np.zeros(25)
        
        print(f"  ✅ Neighbor observation complete (with void handling)")
        return True


    def _is_void_or_membrane_coordinate(self, coord: Tuple, position: str) -> bool:
        """Check if coordinate is a void or has membrane - FIXED LOGIC"""
        if not coord:
            return False
        
        # Check our void list (coordinates we know are voids)
        if coord in self.void_coordinates:
            return True
        
        # Check if we're waiting for membrane at this coordinate
        if (hasattr(self, 'membrane_waiting') and 
            position in self.membrane_waiting and 
            self.membrane_waiting[position] == coord):
            return True  # We're waiting for a reroute for this void
        
        # Check axon network's void system
        if hasattr(self.axon_network, 'void_system'):
            # Check if coordinate has a membrane (being processed)
            if coord in self.axon_network.void_system.membranes:
                membrane = self.axon_network.void_system.membranes[coord]
                if membrane.port:  # Currently processing
                    return True
        
        return False

    def _observe_coordinate_with_locking(self, coord: Tuple, position: str) -> np.ndarray:
        """Observe a coordinate with proper locking"""
        # Try to lock
        if not self.axon_network.lock_coordinate(coord, self.id):
            # Couldn't lock - return zeros for now (will retry)
            return np.zeros(25)
        
        try:
            xpath = self._coord_to_xpath(coord)
            element = self.dom_driver.find_element(By.XPATH, xpath)
            dom_state = self._observe_element(element)
            
            if dom_state.get('exists', False):
                obs_vector = self._dom_state_to_observation_vector(
                    dom_state, position, self.current_pattern_idx,
                    expectation_row=self.assignment.get(position)
                )
                return obs_vector
            else:
                # Reroute failed - it's a void too
                return np.zeros(25)
        except:
            return np.zeros(25)
        finally:
            self.axon_network.unlock_coordinate(coord, self.id)

    def _handle_void(self, position, void_coordinate):
        """Handle void detection and register with membrane system"""
        # Create neuron_data dictionary
        neuron_data = {
            'neuron_id': self.id,
            'neuron_coordinate': self.coordinate,
            'input_direction': position,
            'pattern': self.current_pattern,
            'hierarchical_indices': getattr(self, 'hierarchical_indices', []),
            'confidence': self.confidence_score,
            'cycle': self.cycle_count
        }
        
        # Register with void system
        if hasattr(self.axon_network, 'void_system'):
            self.axon_network.void_system.register_void(
                void_coordinate=void_coordinate,
                neuron_id=self.id,
                neuron_data=neuron_data
            )
        

        self.membrane_waiting[position] = void_coordinate
        print(f"  ⏳ Added {position} to membrane_waiting for void at {void_coordinate}")

        
        # Also mark as void locally
        if void_coordinate not in self.void_coordinates:
            self.void_coordinates.add(void_coordinate)
            print(f"  🌀 Neuron {self.id} registered void at {position}: {void_coordinate}")
            
    def _register_with_membrane(self, void_coordinate: Tuple[int, ...], position: str):
        """Register this neuron with a membrane for rerouting"""
        # Get hierarchical indices from phase 2
        indices = getattr(self, 'hierarchical_indices', list(range(5)))
        
        # Add to membrane queue
        self.axon_network.void_queue.get_or_create(void_coordinate)
        
        # Create connection
        connection = MembraneNeuronConnection(
            neuron_id=self.id,
            neuron_coordinate=self.coordinate,
            input_direction=position,
            hierarchical_indices=indices
        )
        
        # Add to membrane
        membrane = self.axon_network.void_queue.membrane_registry[void_coordinate]
        membrane.add_connection(connection)
        
        # Set stall state
        self.stalled = True
        self.membrane_waiting_for = void_coordinate
        
        print(f"  🌀 Neuron {self.id} registered with membrane at {void_coordinate}")
        print(f"     Waiting for reroute from position {position}")

    def _membrane_processed(self, void_coordinate: Tuple[int, ...], reroute_coordinate: Tuple[int, ...]):
        """Callback when membrane processing completes"""
        if self.membrane_waiting_for == void_coordinate:
            self.stalled = False
            self.membrane_waiting_for = None
            print(f"  ✅ Membrane processing complete for {void_coordinate}")
            print(f"     Reroute to: {reroute_coordinate}")

    def _phase4_matrix_updates(self):
        """Phase 4 with UNKNOWN distinction and β update"""
        
        # ===== NORMAL D MATRIX CALCULATION (ALL PATTERNS) =====
        # Get permuted expectations in 87D
        if not hasattr(self, 'P_permuted') or self.P_permuted is None:
            P_matrix = self.P_matrix.copy()
        else:
            P_matrix = self.P_permuted.copy()
        
        P_i_k_87d = self.T(P_matrix)  # 5×87
        
        # Get neighbor observations in 87D
        W_p_87d = np.zeros((5, 87))
        observed_rows = []
        observed_indices = []
        
        for i in range(5):
            if np.any(self.O_matrix[i] != 0):
                observed_rows.append(self.O_matrix[i])
                observed_indices.append(i)
        
        if observed_rows:
            observed_array = np.array(observed_rows)
            transformed_observed = self.T(observed_array)
            for idx, row_idx in enumerate(observed_indices):
                W_p_87d[row_idx] = transformed_observed[idx]
        
        # Compute D = P_i_k_87d @ W_p_87d^T
        self.D_matrix_87d = P_i_k_87d @ W_p_87d.T  # 5×5
        
        # B^ = D(B) = D @ B
        B_hat = self.D_matrix_87d @ self.B_matrix
        
        # B* = Z(B^) = row normalize
        row_sums = B_hat.sum(axis=1, keepdims=True)
        B_star = np.divide(B_hat, row_sums, where=row_sums != 0)
        
        # ===== β UPDATE (ALL PATTERNS) =====
        self.eigen_beta, self.eigen_beta_v = self._compute_dominant_eigen(B_star)
        
        # Update B matrix
        self.B_matrix = B_star.copy()
        self.B_matrices_history.append(self.B_matrix.copy())
        
        # b_final_update = Z(β * (β_v @ β_v.T) @ b_initial)
        if self.eigen_beta_v is not None:
            beta_component = self.eigen_beta * np.outer(self.eigen_beta_v, self.eigen_beta_v)
            b_updated = beta_component @ self.b_initial
            self.b_final = self._normalize_vector(b_updated)
        else:
            self.b_final = self.b_initial.copy()
        
        # ===== UNKNOWN-SPECIFIC: RECORD β UPDATE =====
        if self.current_pattern == "UNKNOWN":
            self.unknown_perm_cache['cycle_history'].append('beta')
        
        # Update b_vector
        self.b_vector = self.b_final.copy()
        self.b_vectors_history.append(self.b_final.copy())



    # ===== FIX _phase5_tensor_fallback to match exact flow =====
    def _phase5_confidence_decision(self):
        # Get current pattern probability from b_final
        current_prob = self.b_final[self.current_pattern_idx]
        self.confidence_score = current_prob  # <-- Still uses absolute probability
        
        print(f"  🎯 Phase 5 - Pattern dominance check:")
        print(f"     - Current pattern: {self.current_pattern}")
        print(f"     - b_final: {[f'{x:.3f}' for x in self.b_final]}")
        
        # Find dominant pattern
        dominant_pattern_idx = np.argmax(self.b_final)
        
        if dominant_pattern_idx == self.current_pattern_idx:
            self._enter_positional_recycling()
            return "RECYCLING"
        else:
            return "TENSOR_FALLBACK"


    def _phase5_tensor_fallback(self) -> bool:
        """Phase 5 with clear α/γ/β/ζ roles"""
        # ===== NORMAL TENSOR FALLBACK =====
        # Build expectation tensor E = 5×6×87
        E = self.T_exp.copy()
        
        # Build observation tensor O = 5×6×87
        O_obs = self.T_zeta()
        
        # Compute grand covariance G ∈ ℝ^{5×5}
        E_flat = E.reshape(5, -1)
        O_flat = O_obs.reshape(5, -1)
        G = E_flat @ O_flat.T
        
        # Normalize
        G_normalized = G.copy()
        row_sums = G_normalized.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        G_normalized = G_normalized / row_sums
        
        # ===== ζ UPDATE (FINAL PATTERN DECISION) =====
        ζ, v_ζ = self._compute_dominant_eigen(G_normalized)
        
        # Store ζ results
        self.eigen_zeta = ζ
        self.eigen_zeta_v = v_ζ
        self.tensor_G_matrix = G.copy()
        
        # Update b_final with ζ (final pattern decision)
        b_grand = v_ζ * self.b_final if v_ζ is not None else self.b_final.copy()
        b_grand_normalized = self._normalize_vector(b_grand)
        
        # ===== PATTERN DECISION LOGIC =====
        dominant_pattern_idx = np.argmax(b_grand_normalized)
        dominant_prob = b_grand_normalized[dominant_pattern_idx]
        current_prob = b_grand_normalized[self.current_pattern_idx]
        
        # ===== UNKNOWN-SPECIFIC LOGIC =====
        if self.current_pattern == "UNKNOWN":
            print(f"  🔍 UNKNOWN pattern decision (after α/γ/β/ζ):")
            print(f"     - Current (UNKNOWN) probability: {current_prob:.3f}")
            print(f"     - Dominant pattern: {self.pattern_names[dominant_pattern_idx]} ({dominant_prob:.3f})")
            print(f"     - Eigen history: {self.unknown_perm_cache['cycle_history']}")
            
            # UNKNOWN decision: switch if another pattern is clearly better
            if dominant_pattern_idx != self.current_pattern_idx:
                if dominant_prob > current_prob + 0.05:  # 5% better
                    print(f"  🔄 UNKNOWN switching to {self.pattern_names[dominant_pattern_idx]}")
                    self._switch_pattern(self.pattern_names[dominant_pattern_idx], dominant_prob)
                    return True  # Pattern changed, restart cycle
                else:
                    # Another pattern slightly better but not enough
                    print(f"  ⚖️  UNKNOWN staying (dominant only {dominant_prob-current_prob:.3f} better)")
            else:
                # UNKNOWN remains dominant
                print(f"  ✅ UNKNOWN remains dominant ({current_prob:.3f})")
                
                # If UNKNOWN is confident, enter recycling
                if current_prob >= 0.5:
                    self._enter_positional_recycling()
        
        # ===== NORMAL PATTERN DECISION LOGIC =====
        else:
            # Normal pattern decision logic
            if dominant_pattern_idx != self.current_pattern_idx:
                if dominant_prob > current_prob + 0.05:
                    print(f"  🔄 Switching to {self.pattern_names[dominant_pattern_idx]}")
                    self._switch_pattern(self.pattern_names[dominant_pattern_idx], dominant_prob)
                    return True
        
        # Update bias with tensor result
        self.b_vector = b_grand_normalized.copy()
        self.b_final = b_grand_normalized.copy()
        
        # Check if we now have high confidence
        if b_grand_normalized[self.current_pattern_idx] >= 0.5:
            self._enter_positional_recycling()
        
        return False
        

    # ===== PHASE 5: CONFIDENCE & DECISION =====
    def _build_enhanced_tensors(self):
        """Build enhanced expectation tensors once during initialization"""
        # 1. Build base expectation tensor (5×6×25) - already have self.expectation_tensor
        self.T_base = self.expectation_tensor.copy()
        
        # 2. Apply T to get T_exp (5×6×87)
        self.T_exp = np.zeros((5, 6, 87))
        for pos_idx in range(6):
            # Get all patterns at this position (5×25)
            patterns_at_pos = self.T_base[:, pos_idx, :]  # 5×25
            
            # Transform using existing T() method
            transformed = self.T(patterns_at_pos)  # 5×87
            
            # Store in tensor
            self.T_exp[:, pos_idx, :] = transformed

    def _transform_single_with_reference(self, observation_25d: np.ndarray, 
                                    reference_vectors: np.ndarray) -> np.ndarray:
        """
        Transform single observation with reference to multiple vectors.
        Properly uses T() transform by stacking observation with references.
        
        Args:
            observation_25d: Single 25D observation vector
            reference_vectors: k×25 reference vectors (e.g., pattern expectations)
        
        Returns:
            87D relational encoding for the observation
        """
        # Stack observation with references
        combined = np.vstack([observation_25d, reference_vectors])  # (k+1)×25
        
        # Transform together with T()
        transformed = self.T(combined)  # (k+1)×87
        
        # Return only the observation's encoding (first row)
        return transformed[0]



    # ===== PHASE 6 : report ======

    def _phase6_cycle_completion(self):
        """Complete cycle with logging and cleanup"""
        # Update confidence score from b_final
        self.confidence_score = self.b_final[self.current_pattern_idx]
        
        # Log circuitry update
        self._log_circuitry_update()
        
        self.fire_axon('HEARTBEAT', {
        'neuron_id': self.id,
        'heartbeat_count': self.cycle_count  # Use cycle count as heartbeat number
    })

        # Fire cycle complete axon
        self.fire_axon('CYCLE_COMPLETE', {
            'cycle': self.cycle_count,
            'pattern': self.current_pattern,
            'confidence': self.confidence_score,
            'phase': self.processing_phase,
            'recycling_iteration': self.recycling_iteration,
            'dominant_pattern': self.pattern_names[np.argmax(self.b_vector)],
            'dominant_probability': float(np.max(self.b_vector)),
            'void_count': len(self.void_coordinates),
            'assignment_count': len(self.assignment)
        })
        
        # Report dot products - use the correct attribute
        if hasattr(self, 'D_matrix_87d') and self.D_matrix_87d is not None:
            self._report_dot_products(self.D_matrix_87d)
        else:
            print(f"  ⚠ D_matrix_87d not available for dot product reporting")
        
        # Update recycling
        self.recycling_iteration += 1
        self.b_inital = self.b_final #ensure vector is updated 
        self.process_cycle() #restart cycle -- neuron is destroyed when needed via nexus 
        
        print(f"  ✅ Cycle {self.cycle_count} complete - Confidence: {self.confidence_score:.3f}")
        

    # ===== DOM OBSERVATION METHODS =====
    
    def _observe_element(self, element) -> Dict[str, Any]:
        """Extract DOM attributes via Selenium"""
        try:
            dom_state = {
                'tag': element.tag_name.lower(),
                'attributes': self._extract_attributes(element),
                'states': self._extract_states(element),
                'text': element.text.strip() if element.text else '',
                'value': element.get_attribute('value') or '',
                'classes': element.get_attribute('class') or '',
                'id': element.get_attribute('id') or '',
                'exists': True
            }
            return dom_state
        except Exception as e:
            return {'exists': False, 'error': str(e)}
    
    def _extract_attributes(self, element) -> Dict[str, str]:
        """Extract all element attributes"""
        attributes = {}
        try:
            # Try JavaScript method first
            attrs = self.dom_driver.execute_script(
                "var items = {}; "
                "for (index = 0; index < arguments[0].attributes.length; ++index) {"
                "  items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value"
                "}; "
                "return items;", element)
            attributes.update(attrs)
        except:
            # Fallback for basic attributes
            for attr in ['type', 'name', 'placeholder', 'role', 'aria-label', 
                        'data-testid', 'data-cy', 'href', 'src', 'title', 'alt']:
                value = element.get_attribute(attr)
                if value:
                    attributes[attr] = value
        return attributes
    
    def _extract_states(self, element) -> List[str]:
        """Extract element states"""
        states = []
        try:
            if element.is_displayed():
                states.append('visible')
            else:
                states.append('hidden')
                
            if element.is_enabled():
                states.append('enabled')
            else:
                states.append('disabled')
                
            # Check common attributes
            for attr in ['readonly', 'required', 'checked', 'selected', 'disabled']:
                if element.get_attribute(attr):
                    states.append(attr)
                    
        except:
            pass
        return states
    
    def _dom_state_to_observation_vector(self, dom_state: Dict, position: str, 
                                        pattern_idx: int, expectation_row: int = None) -> np.ndarray:
        """
        Convert DOM state to 25D observation vector using AttributeExpression.evaluate()
        """
        vector = np.zeros(25)
        
        if not dom_state.get('exists', False):
            return vector
        
        # Get expectation dictionary for this position and pattern
        if position == "self":
            expectation_dict = self.expectation_dicts[pattern_idx, 0]  # 0 = "self"
        else:
            # Get position index (1=parent, 2=up, etc.)
            pos_idx = self.position_names.index(position)
            expectation_dict = self.expectation_dicts[pattern_idx, pos_idx]
        
        # Convert DOM attributes to our vocabulary
        our_attributes = self._dom_to_our_vocabulary(dom_state)
        
        # Evaluate each dimension
        all_dimensions = EnhancedGrandClass.get_all_dimensions()
        for i, dimension in enumerate(all_dimensions):
            if dimension in expectation_dict:
                expr = expectation_dict[dimension]
                observed_attrs = our_attributes.get(dimension, set())
                # Use AttributeExpression.evaluate() - returns 0.0 or 1.0
                vector[i] = expr.evaluate(observed_attrs)
        
        return vector
    
    def _dom_to_our_vocabulary(self, dom_state: Dict) -> Dict[EnhancedGrandClass, Set[str]]:
        """
        Map DOM observation to our attribute vocabulary.
        Simplified version - in production would use full EnhancedGrandClass definitions.
        """
        element_vectors = defaultdict(set)
        all_definitions = EnhancedGrandClass.get_base_attribute_definitions()
        
        # Extract from DOM
        tag = dom_state.get('tag', '')
        attrs = dom_state.get('attributes', {})
        states = dom_state.get('states', [])
        text = dom_state.get('text', '')
        value = dom_state.get('value', '')
        
        # Check each grand class
        for gc, definitions in all_definitions.items():
            for definition in definitions:
                if self._definition_matches_dom(definition, tag, attrs, states, text, value):
                    element_vectors[gc].add(definition)
        
        return element_vectors
    
    def _definition_matches_dom(self, definition: str, tag: str, attrs: Dict, 
                            states: List[str], text: str, value: str) -> bool:
        """Check if a definition matches DOM state"""
        # Tag matches
        if definition == tag:
            return True
        
        # State matches
        if definition in states:
            return True
        
        # Attribute value matches
        if definition in attrs.values():
            return True
        
        # Input type variations
        if definition.startswith('input_') and tag == 'input':
            expected_type = definition.replace('input_', '')
            return attrs.get('type') == expected_type
        
        # Role matches
        if definition.startswith('role_') and attrs.get('role'):
            expected_role = definition.replace('role_', '')
            return attrs.get('role') == expected_role
        
        # Data attribute matches
        if definition.startswith('data_') and definition.replace('_', '-') in attrs:
            return True
        
        return False
    
    # ===== PATTERN SWITCHING =====

    def _enter_positional_recycling(self):
        """Enter positional recycling loop after pattern confirmation"""
        print(f"  🔁 Entering positional recycling for {self.current_pattern}")
        self.processing_phase = "RECYCLING"
        self.recycling_iteration = 0
        
        # Reset position order
        self.neighbor_positions = ["parent", "up", "down", "left", "right"]
    
    def _switch_pattern(self, new_pattern: str, probability: float) -> bool:
        """Switch to new pattern with tensor-informed update"""
        old_pattern = self.current_pattern
        self.current_pattern = new_pattern
        self.current_pattern_idx = self._get_pattern_idx(new_pattern)
        
        # Update matrices for new pattern
        self.P_matrix = self.neighbor_expectation_tensor[self.current_pattern_idx].copy()
        self.B_matrix = self.B_matrices_dict[new_pattern].copy()
        
        # Reset recycling
        self.recycling_iteration = 0
        self.permutation_count = 0
        
        # Fire axon
        self.fire_axon('PATTERN_CHANGE', {
            'change_type': 'tensor_switch',
            'from_pattern': old_pattern,
            'to_pattern': new_pattern,
            'probability': float(probability),
            'confidence': probability,
            'source': 'tensor_fallback'
        })
        
        print(f"  🔄 Switched pattern: {old_pattern} → {new_pattern} (prob: {probability:.3f})")
        
        # Return True to indicate pattern changed
        return True
        
    # ===== UTILITY METHODS =====
    
    def _generate_id(self) -> str:
        return f"neuron_{hashlib.md5(str(self.coordinate).encode()).hexdigest()[:8]}"

    
    def _coord_to_xpath(self, coord: Tuple[int, ...]) -> str:
        """Convert coordinate to XPath"""
        if not coord:
            return "/html"
        
        if coord[0] != 0:
            coord = (0,) + coord
        
        xpath = "/html"
        for idx in coord[1:]:
            xpath += f"/*[{idx + 1}]"
        return xpath

    def _get_coordinate_for_position(self, position: str) -> Optional[Tuple[int, ...]]:
        """Get coordinate for neighbor position - CLEAN FIX"""
        if not self.coordinate:
            return None
        
        coord = list(self.coordinate)  # Fresh copy
        
        if position == "self":
            return tuple(coord)  # ===== ADDED =====
        elif position == "parent" and len(coord) > 1:
            return tuple(coord[:-1])
        elif position == "up" and len(coord) > 0:
            if coord[-1] > 0:
                coord[-1] -= 1
                return tuple(coord)
            return None  # No previous sibling
        elif position == "down":
            coord[-1] += 1
            return tuple(coord)
        elif position == "left" and len(coord) > 1:
            if coord[-2] > 0:
                coord[-2] -= 1
                return tuple(coord)
            return None  # No left neighbor
        elif position == "right" and len(coord) > 1:
            coord[-2] += 1
            return tuple(coord)
        
        return None

    def _permute_position_order(self):
        """Permute neighbor position order for recycling"""
        if self.permutation_count < self.max_permutations:
            # Simple rotation
            self.neighbor_positions = self.neighbor_positions[1:] + [self.neighbor_positions[0]]
            self.permutation_count += 1
            print(f"  🔄 Permuted position order: {self.neighbor_positions}")
    

    def _handle_hash_change(self, new_dom_state: Dict, new_hash: str):
        """Handle DOM hash change"""
        self.fire_axon('DOM_EVENT', {
            'event_type': 'hash_change',
            'old_hash': getattr(self, 'last_dom_hash', '')[:8],
            'new_hash': new_hash[:8],
            'action': 'return_to_processing'
        })
        self.processing_phase = "PROCESSING"
    
    def _handle_self_destruct(self, reason: str):
        """Handle neuron self-destruct"""
        self.fire_axon('SYSTEM_ALERT', {
            'alert_type': 'self_destruct',
            'reason': reason,
            'coordinate': self.coordinate
        })
        self.processing_phase = "DESTROYED"
    
    # ===== AXON COMMUNICATION =====

    def _fire_creation_axon(self):
        """Fire creation axon"""
        self.fire_axon('NEURON_CREATED', {
            'confidence': self.confidence_score,
            'b_vector_shape': self.b_vector.shape
        })

    def fire_axon(self, axon_type: str, data: Dict):
        """Fire axon through network - uses updated AxonNetwork structure"""
        axon_data = {
            'neuron_id': self.id,
            'coordinate': self.coordinate,
            'pattern': self.current_pattern,
            'cycle': self.cycle_count,
            **{k: v for k, v in data.items() if not isinstance(v, (np.ndarray, list, dict)) or len(str(v)) < 100}
        }
        
        # Use axon network (logs to pattern queue based on current pattern)
        self.axon_network.fire_axon(axon_type, axon_data, self)
    
    def _log_circuitry_update(self):
        """Log complete matrix state for current cycle"""
        # Get dot products from D matrix if available
        dot_products = {}
        if hasattr(self, 'D_matrix'):
            for i in range(min(5, self.D_matrix.shape[0])):
                for j in range(min(5, self.D_matrix.shape[1])):
                    dot_products[f'D_{i}_{j}'] = float(self.D_matrix[i, j])
        
        # Calculate eigen certainty
        eigen_certainty = self._calculate_eigen_certainty()
        eigen_category = self._get_eigen_category(eigen_certainty)
        
        # Fire circuitry axon with ALL matrix data
        self.fire_axon('CIRCUITRY_UPDATE', {
            'neuron_id': self.id,
            'cycle': self.cycle_count,
            'pattern': self.current_pattern,
            'pattern_idx': int(self.current_pattern_idx),
            
            # Pattern probabilities (b vector)
            'b_vector': self.b_vector.tolist() if hasattr(self.b_vector, 'tolist') 
                    else list(self.b_vector),
            
            # Position bias matrix (B matrix)
            'B_matrix_diag': np.diag(self.B_matrix).tolist(),
            'B_matrix_stats': {
                'mean': float(self.B_matrix.mean()),
                'std': float(self.B_matrix.std()),
                'trace': float(np.trace(self.B_matrix))
            },
            
            # Eigen data
            'V_matrix_trace': float(np.trace(self.V_matrix)) if hasattr(self, 'V_matrix') else 0.0,
            'eigen_certainty': eigen_certainty,
            'eigen_category': eigen_category,
            
            # Confidence
            'confidence': float(self.confidence_score),
            
            # Dot products (neighbor accuracies)
            'dot_products': dot_products,
            
            # Process state
            'recycling_iteration': self.recycling_iteration,
            'void_count': len(self.void_coordinates),
            'positions_observed': list(self.assignment.keys()),
            'assignment': self.assignment.copy()
        })
    
    def _calculate_eigen_certainty(self) -> float:
        """Calculate certainty from eigen decomposition"""
        try:
            eigenvalues, eigenvectors = np.linalg.eig(self.B_matrix)
            dominant_idx = np.argmax(np.abs(eigenvalues))
            dominant_eigenvalue = np.abs(eigenvalues[dominant_idx])
            return float(min(1.0, dominant_eigenvalue))
        except:
            return 0.0
    
    def _get_eigen_category(self, certainty: float) -> str:
        """Categorize eigen certainty into 5 levels"""
        if certainty >= 0.8:
            return "E1_HIGH_CERTAINTY"
        elif certainty >= 0.6:
            return "E2_MEDIUM_HIGH"
        elif certainty >= 0.4:
            return "E3_MEDIUM"
        elif certainty >= 0.2:
            return "E4_MEDIUM_LOW"
        else:
            return "E5_LOW_CERTAINTY"
   
    def _report_dot_products(self, D_matrix: np.ndarray):
        """Report critical dot products from D_matrix_87d"""
        if D_matrix is None or D_matrix.size == 0:
            return
        
        # Find best matches for each row (expectation pattern)
        best_matches = {}
        for i in range(min(5, D_matrix.shape[0])):
            best_j = np.argmax(D_matrix[i, :])
            best_value = D_matrix[i, best_j]
            position_name = self.neighbor_positions[i] if i < len(self.neighbor_positions) else f"pos_{i}"
            best_matches[position_name] = {
                'best_match_position': int(best_j),
                'relational_similarity': float(best_value)
            }
        
        self.fire_axon('DOT_PRODUCT_REPORT', {
            'matrix_space': '87D_relational',
            'best_matches': best_matches,
            'mean_relational_similarity': float(D_matrix.mean()),
            'convergence_score': sum(1 for m in best_matches.values() if m['relational_similarity'] > 0.7) / len(best_matches) 
                                if best_matches else 0
        })
            
    def _mark_void(self, coordinate: Tuple[int, ...], reason: str):
        """Mark coordinate as void - check for duplicate flags first"""
        if not coordinate:
            return
        
        # Check if void flag already sent recently
        if hasattr(self.axon_network, 'has_flag_been_sent'):
            if self.axon_network.has_flag_been_sent(coordinate, 'VOID'):
                # Flag already sent, just add to local void set
                if coordinate not in self.void_coordinates:
                    self.void_coordinates.add(coordinate)
                return
        
        # First time marking this void
        if coordinate and coordinate not in self.void_coordinates:
            self.void_coordinates.add(coordinate)
            
            # Record that we're sending this flag
            if hasattr(self.axon_network, 'record_flag_sent'):
                self.axon_network.record_flag_sent(coordinate, 'VOID')
            
            # Send void signal
            self.fire_axon('VOID_SIGNAL', {
                'coordinate': coordinate,
                'reason': reason[:100],
                'source_neuron': self.id,
                'total_voids': len(self.void_coordinates)
            })

    def _signal_growth(self, coordinate: Tuple[int, ...], vector: np.ndarray, position: str):
        """Signal growth opportunity - check for duplicate flags first"""
        if not coordinate:
            return
        
        # Check if growth flag already sent recently
        if hasattr(self.axon_network, 'has_flag_been_sent'):
            if self.axon_network.has_flag_been_sent(coordinate, 'GROWTH'):
                # Flag already sent
                return
        
        # Check if coordinate already has neuron
        if hasattr(self.axon_network, 'has_neuron_at_coordinate'):
            if self.axon_network.has_neuron_at_coordinate(coordinate):
                return
        
        # Check if coordinate is void
        if hasattr(self.axon_network, 'is_void_coordinate'):
            if self.axon_network.is_void_coordinate(coordinate):
                return
        
        # Record that we're sending this flag
        if hasattr(self.axon_network, 'record_flag_sent'):
            self.axon_network.record_flag_sent(coordinate, 'GROWTH')
        
        # Send growth signal
        self.fire_axon('GROWTH_SIGNAL', {
            'coordinate': coordinate,
            'from_position': position,
            'vector_norm': float(np.linalg.norm(vector)),
            'source_neuron': self.id
        })

    def process_cycle(self) -> bool:
        """Main processing cycle - ALWAYS completes"""
        self.cycle_count += 1
        
        print(f"\n🧠 Neuron {self.id} Cycle {self.cycle_count} [{self.current_pattern}]")
        
        # Reset stalled state if any
        if self.stalled:
            print(f"  ⏸️  Resuming from stall state")
            self.stalled = False
        
        # Phase 1: Self observation
        self._phase1_self_observation()
        
        # Phase 2: Competitive assignment
        self._phase2_competitive_assignment()
        
        # Phase 3: Neighbor observation WITH void handling
        try:
            if self.learning_mode == "TARGETED":
                self._phase3_targeted_observation_with_locking()
            else:
                self._phase3_neighbor_observation()  # Uses new method with reroutes
        except Exception as e:
            print(f"  ⚠ Neighbor observation error: {e}")
            # Continue with zeros for failed observations
        
        # Phase 4: Matrix updates (use whatever observations we have)
        self._phase4_matrix_updates()
        
        # Phase 5: Confidence decision
        decision = self._phase5_confidence_decision()
        
        if decision == "TENSOR_FALLBACK":
            pattern_changed = self._phase5_tensor_fallback()
            if pattern_changed:
                self._phase6_cycle_completion()
                return True
        
        # Always complete the cycle
        self._phase6_cycle_completion()
        return True

    def cleanup_locks(self):
        """Release any locks this neuron holds"""
        if hasattr(self.axon_network, 'coordinate_states'):
            # Find and remove all locks held by this neuron
            coordinates_to_remove = []
            for coord, state in self.axon_network.coordinate_states.items():
                if state['locked_by'] == self.id:
                    coordinates_to_remove.append(coord)
            
            for coord in coordinates_to_remove:
                del self.axon_network.coordinate_states[coord]
    def cleanup(self):
        """Clean up neuron resources"""
        # Release all locks
        self.cleanup_locks()
        
        # Clear pending coordinates
        self.pending_coordinates.clear()
        self.stalled_positions.clear()
        
        # Notify void system we're gone
        if hasattr(self.axon_network, 'void_system'):
            # Remove any membrane connections for this neuron
            for void_coord, membrane in self.axon_network.void_system.membranes.items():
                if self.id in membrane.connections:
                    del membrane.connections[self.id]

# ===== PUBLIC METHODS FOR NEXUS =====
   
    def get_matrix_sample(self) -> Dict:
        """Get matrix data for Nexus visualization - COMPRESSED"""
        return {
            'neuron_id': self.id,
            'pattern': self.current_pattern,
            'confidence': float(self.confidence_score),
            'phase': self.processing_phase,
            'cycle_count': self.cycle_count,
            'recycling_iteration': self.recycling_iteration,
            'dominant_pattern': self.pattern_names[np.argmax(self.b_vector)],
            'dominant_probability': float(np.max(self.b_vector)),
            'void_count': len(self.void_coordinates),
            'assignment_count': len(self.assignment)
        }
    
    def get_status(self) -> Dict:
        """Get neuron status for Nexus"""
        return {
            'id': self.id,
            'coordinate': self.coordinate,
            'pattern': self.current_pattern,
            'confidence': float(self.confidence_score),
            'phase': self.processing_phase,
            'cycle_count': self.cycle_count,
            'last_activity': self.last_activity,
            'void_count': len(self.void_coordinates),
            'monitoring_active': self.monitoring_active,
            'recycling_iteration': self.recycling_iteration,
            'max_recycling_iterations': self.max_recycling_iterations
        }
    
    def start_monitoring(self):
        """Start monitoring phase (called by Nexus if needed)"""
        if self.confidence_score >= 0.7:
            self.processing_phase = "MONITORING"
            self.monitoring_start_time = time.time()
    
    def stop_monitoring(self):
        """Stop monitoring phase"""
        if self.processing_phase == "MONITORING":
            self.processing_phase = "PROCESSING"




#====== Pathways of the brain, the corticial organization ===== 

"""
AXON NETWORK - Complete Implementation
Simple 6-queue system with all axon types for visualization and tracking
"""

class AxonNetwork:
    """Axon network with compressed, continuous logging by neuron_id"""
    
    def __init__(self, nexus_coordinate_space, session_start_time=None):
        
        self.session_start_time = session_start_time or time.time()
        self.neuron_registry = {}  # neuron_id -> weakref to neuron
        self.void_system = VoidSystem(self)
        self.coordinate_locks = {}  # coordinate -> {'locked_by': neuron_id, 'locked_at': timestamp}
        self.coordinate_lock_timeout = 1.0
        # Axon type definitions - UPDATE THIS
        self.axon_definitions = {
            'NEURON_CREATED': {'nexus': False, 'broadcast': True},
            'GROWTH_SIGNAL': {'nexus': True, 'broadcast': True},
            'VOID_SIGNAL': {'nexus': True, 'broadcast': True},
            'CYCLE_COMPLETE': {'nexus': False, 'broadcast': True},
            'DOT_PRODUCT_REPORT': {'nexus': False, 'broadcast': False},
            'PATTERN_CHANGE': {'nexus': False, 'broadcast': True},
            'DOM_EVENT': {'nexus': False, 'broadcast': True},
            'SYSTEM_ALERT': {'nexus': True, 'broadcast': False},
            'CIRCUITRY_UPDATE': {'nexus': False, 'broadcast': False, 'circuitry': True},
            'COMPETITIVE_ASSIGNMENT': {'nexus': False, 'broadcast': False},
            'HEARTBEAT': {'nexus': True, 'broadcast': True},  # ADD THIS LINE
            'NEXUS_CONTROL': {'nexus': True, 'broadcast': True},  # ADD THIS LINE
        }

        # 7 QUEUES - ALL DICTIONARIES keyed by neuron_id (except NEXUS)
        self.queues = {
            'DATA_INPUT': {},      # neuron_id -> list of axons
            'ACTION_ELEMENT': {},  # neuron_id -> list of axons  
            'CONTEXT_ELEMENT': {}, # neuron_id -> list of axons
            'STRUCTURAL': {},      # neuron_id -> list of axons
            'UNKNOWN': {},         # neuron_id -> list of axons
            'NEXUS': deque(maxlen=500),  # Still a queue for processing
            'CIRCUITRY': {}        # neuron_id -> continuous matrix history
        }
        
        # For circuitry: track tensor structure
        self.tensor_structure_logged = False
        self.tensor_structure = None
        
        self.historical_axons = deque(maxlen=2000)
        self.coordinate_space = nexus_coordinate_space
        self.axon_counter = 0
        self.test_node_suggestions = []
        self.active_test_nodes = {}
        self.neuron_registry = {}
        self.neuron_objects = {} #id ref 
        self.sent_flags = {}
    
    # ===== Public reporting access ===== 

    def dump_current_state(self, frames_dir: str, frame_number: int):
        """
        SIMPLY dump current state from queues.
        Called by Nexus periodically.
        """
        # 1. Create frames directory if it doesn't exist
        os.makedirs(frames_dir, exist_ok=True)
        
        # 2. DIRECT ACCESS TO QUEUES - that's all we need
        frame_data = {
            'frame': frame_number,
            'timestamp': time.time(),
            'session_time': time.time() - self.session_start_time,
            
            # ===== SIMPLY COPY WHAT'S IN THE QUEUES =====
            'neurons': self._extract_neurons_from_circuitry(),
            'axons': self._extract_axons_from_queues(),
            'system_events': list(self.queues['NEXUS'])[-20:],  # Last 20
            'circuitry_summary': self.get_all_circuitry_summary(),
            
            # Stats are already computed in get_all_circuitry_summary()
            'system_stats': self.get_queue_snapshots()
        }
        
        # 3. Save to file
        filename = f"frame_{frame_number:06d}.json"
        filepath = os.path.join(frames_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(frame_data, f, indent=2)
        
        print(f"📊 Frame {frame_number}: {len(frame_data['neurons'])} neurons from CIRCUITRY queue")
        
        return frame_number + 1
    
    def _extract_neurons_from_circuitry(self):
        """JUST extract neuron states from CIRCUITRY queue"""
        neurons = []
        
        for neuron_id, circuitry in self.queues['CIRCUITRY'].items():
            if circuitry['matrix_history']:
                latest = circuitry['matrix_history'][-1]
                
                # Get coordinate from registry
                coord = None
                for c, info in self.neuron_registry.items():
                    if info.get('id') == neuron_id:
                        coord = c
                        break
                
                if coord:
                    neuron = {
                        'neuron_id': neuron_id,
                        'coordinate': list(coord) if isinstance(coord, tuple) else coord,
                        'pattern': circuitry['pattern'],
                        'confidence': latest['confidence'],
                        'b_vector': latest['b_vector'],
                        'B_matrix_diag': latest['B_matrix_diag'],
                        'dot_products': latest['dot_products'],
                        'assignment': latest['assignment'],
                        'cycle': latest['cycle']
                    }
                    neurons.append(neuron)
        
        return neurons
    
    def _extract_axons_from_queues(self):
        """JUST extract recent axons from all pattern queues"""
        axons = []
        recent_time = time.time() - 2.0  # Last 2 seconds
        
        # Check all pattern queues
        for pattern in ['DATA_INPUT', 'ACTION_ELEMENT', 'CONTEXT_ELEMENT', 
                       'STRUCTURAL', 'UNKNOWN']:
            queue = self.queues[pattern]
            for neuron_id, axon_list in queue.items():
                if axon_list:
                    # Get most recent axon
                    latest_axon = axon_list[-1]
                    axon_time = self.session_start_time + latest_axon.get('session_time', 0)
                    
                    if axon_time >= recent_time:
                        axons.append(latest_axon)
        
        # Also get system axons
        for axon in list(self.queues['NEXUS'])[-10:]:
            axons.append(axon)
        
        return axons
    
    # ===== MAIN AXON FIRING METHOD =====
    
    def has_flag_been_sent(self, coordinate: Tuple, flag_type: str, timeout: float = 5.0) -> bool:
        """Check if a flag was recently sent for this coordinate"""
        key = (coordinate, flag_type)
        if key in self.sent_flags:
            # Check if flag is still fresh (within timeout)
            if time.time() - self.sent_flags[key] < timeout:
                return True
            else:
                # Flag expired, remove it
                del self.sent_flags[key]
        return False


    def lock_coordinate(self, coordinate: Tuple, neuron_id: str) -> bool:
        """Simple coordinate locking - returns True if lock acquired"""
        if coordinate in self.coordinate_locks:
            # Check if lock expired
            lock_time = self.coordinate_locks[coordinate][1]
            if time.time() - lock_time > self.coordinate_lock_timeout:
                # Lock expired, take it
                self.coordinate_locks[coordinate] = (neuron_id, time.time())
                return True
            return False  # Still locked by someone else
        
        # Coordinate free, lock it
        self.coordinate_locks[coordinate] = (neuron_id, time.time())
        return True

    def unlock_coordinate(self, coordinate: Tuple, neuron_id: str):
        """Release coordinate lock"""
        if coordinate in self.coordinate_locks:
            if self.coordinate_locks[coordinate][0] == neuron_id:
                del self.coordinate_locks[coordinate]

    def is_coordinate_locked(self, coordinate: Tuple, exclude_neuron: str = None) -> bool:
        """Check if coordinate is locked (optionally excluding specific neuron)"""
        if coordinate not in self.coordinate_locks:
            return False
        
        # Check timeout
        lock_time = self.coordinate_locks[coordinate][1]
        if time.time() - lock_time > self.coordinate_lock_timeout:
            del self.coordinate_locks[coordinate]
            return False
        
        # Check if we should exclude ourselves
        if exclude_neuron and self.coordinate_locks[coordinate][0] == exclude_neuron:
            return False
        
        return True
        
    # Add method to record flag
    def record_flag_sent(self, coordinate: Tuple, flag_type: str):
        """Record that a flag was sent for this coordinate"""
        key = (coordinate, flag_type)
        self.sent_flags[key] = time.time()

    def fire_axon(self, axon_type: str, data: Dict, source_neuron) -> str:
        """
        Fire axon with continuous logging by neuron_id.
        Returns axon_id for tracking.
        """
        self.axon_counter += 1
        session_time = time.time() - self.session_start_time
        
        # Handle None source (for system axons)
        if source_neuron is None:
            source_info = {
                'id': 'SYSTEM',
                'coordinate': (0, 0, 0),
                'pattern': 'SYSTEM',
                'state': 'SYSTEM'
            }
        else:
            source_info = {
                'id': source_neuron.id,
                'coordinate': source_neuron.coordinate,
                'pattern': source_neuron.current_pattern,
                'state': getattr(source_neuron, 'state', 'DEFAULT').value 
                        if hasattr(source_neuron, 'state') else 'UNKNOWN'
            }
        
        # Create axon
        axon = {
            'axon_id': f"axon_{self.axon_counter:06d}",
            'axon_type': axon_type,
            'session_time': session_time,
            'source': source_info,
            'data': data
        }
        
        # Get axon definition
        axon_def = self.axon_definitions.get(axon_type, 
                    {'nexus': False, 'broadcast': False, 'circuitry': False})
        
        # SPECIAL HANDLING FOR CIRCUITRY_UPDATE
        if axon_type == 'CIRCUITRY_UPDATE':
            self._handle_circuitry_update(axon, source_neuron)
        else:
            # STANDARD PATTERN QUEUE LOGGING
            pattern = source_neuron.current_pattern
            if pattern in self.queues and pattern != 'CIRCUITRY':
                # Get or create neuron's axon list
                if source_neuron.id not in self.queues[pattern]:
                    self.queues[pattern][source_neuron.id] = []
                
                # Calculate axon type count for this neuron
                axon_list = self.queues[pattern][source_neuron.id]
                axon_type_count = sum(1 for a in axon_list if a['axon_type'] == axon_type)
                axon['list_index'] = axon_type_count  # For visualization tracking
                
                # Add to neuron's continuous history
                axon_list.append(axon)
        
        # NEXUS QUEUE (for processing)
        if axon_def.get('nexus', False):
            self.queues['NEXUS'].append(axon)
        
        # BROADCAST HANDLING
        if axon_def.get('broadcast', False):
            self._handle_broadcast(axon)
        
        # Historical record
        self.historical_axons.append(axon)
        
        # Update neuron registry
        if source_neuron:
            self._update_neuron_registry(source_neuron, session_time)
        
        return axon['axon_id']
    
    def is_coordinate_currently_observed(self, coordinate: Tuple) -> bool:
        """Check if coordinate is being observed RIGHT NOW by checking pattern queues"""
        if not coordinate:
            return False
        
        current_time = time.time()
        
        # Check all pattern queues for VERY recent activity
        for pattern in ['DATA_INPUT', 'ACTION_ELEMENT', 'CONTEXT_ELEMENT', 
                    'STRUCTURAL', 'UNKNOWN']:
            for neuron_id, axons in self.queues[pattern].items():
                if axons:  # Has axons
                    last_axon = axons[-1]  # Most recent axon
                    
                    # Check if this axon is about this coordinate AND very recent
                    axon_data = last_axon.get('data', {})
                    axon_coord = axon_data.get('coordinate')
                    
                    # Also check source coordinate
                    source_coord = last_axon.get('source', {}).get('coordinate')
                    
                    if (axon_coord == coordinate or source_coord == coordinate):
                        # Check recency (within last 0.5 seconds)
                        axon_time = self.session_start_time + last_axon['session_time']
                        if current_time - axon_time < 0.5:
                            return True
        
        return False

    def _handle_circuitry_update(self, axon: Dict, source_neuron):
        """Handle circuitry updates - continuous matrix history"""
        neuron_id = source_neuron.id
        
        # First time? Log tensor structure once
        if not self.tensor_structure_logged and hasattr(source_neuron, 'expectation_tensor'):
            self.tensor_structure = {
                'logged_at': axon['session_time'],
                'tensor_shape': list(source_neuron.expectation_tensor.shape),
                'pattern_names': source_neuron.pattern_names,
                'position_names': source_neuron.position_names,
                'dimension_count': 25
            }
            self.tensor_structure_logged = True
        
        # Get or create neuron's circuitry history
        if neuron_id not in self.queues['CIRCUITRY']:
            self.queues['CIRCUITRY'][neuron_id] = {
                'neuron_id': neuron_id,
                'coordinate': source_neuron.coordinate,
                'matrix_history': [],  # List index = cycle/sample number
                'stats': {
                    'total_cycles': 0,
                    'pattern_cycles': defaultdict(int),
                    'pattern_switches': 0,
                    'matrix_updates': 0,
                    'confidence_history': []
                }
            }
        
        circuitry_entry = self.queues['CIRCUITRY'][neuron_id]
        
        # Extract matrix data from axon
        cycle = axon['data'].get('cycle', 0)
        pattern = axon['data'].get('pattern', 'UNKNOWN')
        
        # Create matrix snapshot
        matrix_snapshot = {
            'cycle': cycle,
            'session_time': axon['session_time'],
            'pattern': pattern,
            'pattern_idx': axon['data'].get('pattern_idx', -1),
            
            # Matrix states (for visualization)
            'b_vector': axon['data'].get('b_vector', []),
            'B_matrix_diag': axon['data'].get('B_matrix_diag', []),
            'V_matrix_trace': axon['data'].get('V_matrix_trace', 0.0),
            
            # Confidence metrics
            'confidence': axon['data'].get('confidence', 0.0),
            'eigen_certainty': axon['data'].get('eigen_certainty', 0.0),
            'eigen_category': axon['data'].get('eigen_category', 'UNKNOWN'),
            
            # Dot products for neighbor accuracy visualization
            'dot_products': axon['data'].get('dot_products', {}),
            
            # Process state
            'recycling_iteration': axon['data'].get('recycling_iteration', 0),
            'void_count': axon['data'].get('void_count', 0),
            'positions_observed': axon['data'].get('positions_observed', []),
            'assignment': axon['data'].get('assignment', {})
        }
        
        # Add to history (list index = sample/frame number)
        circuitry_entry['matrix_history'].append(matrix_snapshot)
        
        # Update stats
        circuitry_entry['stats']['total_cycles'] += 1
        circuitry_entry['stats']['pattern_cycles'][pattern] += 1
        circuitry_entry['stats']['matrix_updates'] += 1
        circuitry_entry['stats']['confidence_history'].append(matrix_snapshot['confidence'])
        
        # Check for pattern switch
        if (len(circuitry_entry['matrix_history']) > 1 and 
            circuitry_entry['matrix_history'][-2]['pattern'] != pattern):
            circuitry_entry['stats']['pattern_switches'] += 1
        
        # Update current pattern in circuitry entry
        circuitry_entry['pattern'] = pattern
    
    def _handle_broadcast(self, axon: Dict):
        """Handle broadcast axon types"""
        broadcast_log = axon.copy()
        original_type = axon['axon_type']
        broadcast_log['axon_type'] = f'BROADCAST_{original_type}_INTENT'
        
        pattern = axon['source']['pattern']
        if pattern in self.queues:
            if axon['source']['id'] not in self.queues[pattern]:
                self.queues[pattern][axon['source']['id']] = []
            self.queues[pattern][axon['source']['id']].append(broadcast_log)
    
    # ===== EXISTING METHODS (updated for new structure) =====
    
    def coordinate_has_neuron(self, coordinate: Tuple[int, ...]) -> bool:
        return coordinate in self.neuron_registry
    
    def get_void_coordinates(self) -> Set[Tuple[int, ...]]:
        if not hasattr(self, '_void_coordinates'):
            self._void_coordinates = set()
        return self._void_coordinates.copy()
    
    def add_void_coordinate(self, coordinate: Tuple[int, ...], source_neuron_id: str):
        if not hasattr(self, '_void_coordinates'):
            self._void_coordinates = set()
        
        if coordinate not in self._void_coordinates:
            self._void_coordinates.add(coordinate)
            
            # Fire void broadcast to all pattern queues
            void_axon = {
                'axon_id': f"void_{self.axon_counter}",
                'axon_type': 'VOID_BROADCAST',
                'session_time': time.time() - self.session_start_time,
                'source': {'id': source_neuron_id, 'coordinate': None, 'pattern': 'SYSTEM'},
                'data': {
                    'void_coordinate': coordinate,
                    'source_neuron': source_neuron_id,
                    'total_voids': len(self._void_coordinates)
                }
            }
            
            # Add to all pattern queues for affected neurons
            for pattern in ['DATA_INPUT', 'ACTION_ELEMENT', 'CONTEXT_ELEMENT', 
                          'STRUCTURAL', 'UNKNOWN']:
                if pattern in self.queues:
                    # This will be picked up by neurons when they check their queues
                    pass


    def get_axon_log_for_neuron(self, neuron_id: str, pattern_filter: str = None) -> List[Dict]:
        """Get axon history for specific neuron (compatible with existing calls)"""
        neuron_axons = []
        
        if pattern_filter and pattern_filter in self.queues:
            if neuron_id in self.queues[pattern_filter]:
                neuron_axons.extend(self.queues[pattern_filter][neuron_id])
        else:
            # Check all pattern queues
            for pattern_name in ['DATA_INPUT', 'ACTION_ELEMENT', 'CONTEXT_ELEMENT', 
                               'STRUCTURAL', 'UNKNOWN']:
                if neuron_id in self.queues[pattern_name]:
                    neuron_axons.extend(self.queues[pattern_name][neuron_id])
        
        return sorted(neuron_axons, key=lambda x: x['session_time'])
    
    def get_neuron(self, neuron_id: str):
            """Get neuron object by ID"""
            return self.neuron_objects.get(neuron_id)
        
    # Also add cleanup when neuron is removed
    def remove_neuron(self, neuron_id: str):
        """Remove neuron from network"""
        # Remove from neuron_objects
        if neuron_id in self.neuron_objects:
            del self.neuron_objects[neuron_id]
        
        # Remove from registry
        for coord, data in list(self.neuron_registry.items()):
            if data.get('id') == neuron_id:
                del self.neuron_registry[coord]
                break

    def register_neuron(self, neuron, neighbor_info: Dict = None):
            """Register neuron in network"""
            session_time = time.time() - self.session_start_time
            
            self.neuron_registry[neuron.coordinate] = {
                'id': neuron.id,
                'pattern': neuron.current_pattern,
                'state': getattr(neuron, 'state', 'DEFAULT').value if hasattr(neuron, 'state') else 'UNKNOWN',
                'neighbors': neighbor_info or {},
                'registered_at': session_time,
                'last_axon_at': session_time
            }
            
            self.neuron_objects[neuron.id] = neuron
        

    def _update_neuron_registry(self, neuron, session_time: float):
        """Update neuron's last activity time"""
        if neuron and neuron.coordinate in self.neuron_registry:
            self.neuron_registry[neuron.coordinate]['last_axon_at'] = session_time
            self.neuron_registry[neuron.coordinate]['state'] = (
                getattr(neuron, 'state', 'DEFAULT').value 
                if hasattr(neuron, 'state') else 'UNKNOWN'
            )
    
    def get_next_nexus_axon(self) -> Optional[Dict]:
        if not self.queues['NEXUS']:
            return None
        return self.queues['NEXUS'].popleft()
    
    def get_queue_snapshots(self) -> Dict:
        """Get complete queue snapshots for visualization"""
        current_session_time = time.time() - self.session_start_time
        
        # Count axons in pattern queues
        pattern_counts = {}
        for pattern_name in ['DATA_INPUT', 'ACTION_ELEMENT', 'CONTEXT_ELEMENT', 
                           'STRUCTURAL', 'UNKNOWN']:
            total_axons = sum(len(axon_list) for axon_list in self.queues[pattern_name].values())
            pattern_counts[pattern_name] = {
                'neuron_count': len(self.queues[pattern_name]),
                'axon_count': total_axons
            }
        
        return {
            'session': {
                'start_time': self.session_start_time,
                'current_time': current_session_time,
                'duration_seconds': current_session_time
            },
            'queues': pattern_counts,
            'circuitry': {
                'neuron_count': len(self.queues['CIRCUITRY']),
                'tensor_logged': self.tensor_structure_logged
            },
            'statistics': {
                'total_axons_fired': self.axon_counter,
                'neurons_registered': len(self.neuron_registry),
                'nexus_queue_size': len(self.queues['NEXUS'])
            }
        }
    
    # ===== NEW VISUALIZATION METHODS =====
    
    def get_neuron_circuitry_history(self, neuron_id: str) -> Dict:
        """Get complete circuitry history for a neuron"""
        if neuron_id not in self.queues['CIRCUITRY']:
            return {}
        
        entry = self.queues['CIRCUITRY'][neuron_id].copy()
        
        # Add tensor structure if available
        if self.tensor_structure:
            entry['tensor_structure'] = self.tensor_structure
        
        return entry
    
    def get_matrix_evolution(self, neuron_id: str, matrix_type: str = 'B') -> List:
        """Get matrix evolution data for visualization"""
        if neuron_id not in self.queues['CIRCUITRY']:
            return []
        
        history = self.queues['CIRCUITRY'][neuron_id]['matrix_history']
        
        if matrix_type == 'B':
            return [{'cycle': h['cycle'], 'diag': h['B_matrix_diag']} for h in history]
        elif matrix_type == 'b':
            return [{'cycle': h['cycle'], 'vector': h['b_vector'], 'pattern': h['pattern']} 
                    for h in history]
        elif matrix_type == 'confidence':
            return [{'cycle': h['cycle'], 'confidence': h['confidence'], 
                     'eigen': h['eigen_certainty']} for h in history]
        elif matrix_type == 'dot_products':
            # Return dot products for neighbor accuracy visualization
            result = []
            for h in history:
                for key, value in h['dot_products'].items():
                    result.append({
                        'cycle': h['cycle'],
                        'position': key,  # e.g., 'D_0_1'
                        'value': value,
                        'pattern': h['pattern']
                    })
            return result
        
        return []
    
    def get_all_circuitry_summary(self) -> Dict:
        """Get summary of all neurons' circuitry for dashboard"""
        summary = {
            'neurons': {},
            'aggregate': {
                'total_neurons': len(self.queues['CIRCUITRY']),
                'total_cycles': 0,
                'average_confidence': 0.0,
                'pattern_distribution': defaultdict(int),
                'eigen_distribution': defaultdict(int)
            }
        }
        
        all_confidences = []
        for neuron_id, circuitry in self.queues['CIRCUITRY'].items():
            # Neuron summary
            summary['neurons'][neuron_id] = {
                'pattern': circuitry['pattern'],
                'total_cycles': circuitry['stats']['total_cycles'],
                'pattern_switches': circuitry['stats']['pattern_switches'],
                'latest_confidence': circuitry['matrix_history'][-1]['confidence'] 
                    if circuitry['matrix_history'] else 0.0,
                'eigen_category': circuitry['matrix_history'][-1]['eigen_category'] 
                    if circuitry['matrix_history'] else 'UNKNOWN'
            }
            
            # Update aggregate stats
            summary['aggregate']['total_cycles'] += circuitry['stats']['total_cycles']
            for pattern, count in circuitry['stats']['pattern_cycles'].items():
                summary['aggregate']['pattern_distribution'][pattern] += count
            
            if circuitry['matrix_history']:
                latest = circuitry['matrix_history'][-1]
                all_confidences.append(latest['confidence'])
                summary['aggregate']['eigen_distribution'][latest['eigen_category']] += 1
        
        if all_confidences:
            summary['aggregate']['average_confidence'] = sum(all_confidences) / len(all_confidences)
        
        return summary



# END -- and the angels sang, for thee my love 
