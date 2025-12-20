import subprocess
import urllib.parse
import undetected_chromedriver as uc
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import time
import hashlib
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
import pygame
import pygame.locals as pg_locals
from pathlib import Path
import json
import math
import os
import subprocess

# ===== DATABASE SYSTEM =====

class VengerDatabase:
    """Database for storing and loading DOM snapshots"""
    
    def __init__(self, base_path="TheDevengers"):
        self.base_path = base_path
        self.current_site = None
        self.site_path = None
        self.pages = []
        self.current_page_idx = 0
        self.is_loaded = False
        
        os.makedirs(base_path, exist_ok=True)
    
    def prompt_for_database(self):
        """Prompt user to create or load a database"""
        print("\n" + "="*60)
        print("🗄️  VENGER DATABASE")
        print("="*60)
        
        sites = self._get_existing_sites()
        
        if sites:
            print("📂 Existing databases:")
            for i, site in enumerate(sites):
                print(f"  [{i}] {site}")
            print()
        
        print("Options:")
        print("  [n] - Create new database")
        if sites:
            print(f"  [0-{len(sites)-1}] - Load existing database")
        print("  [Enter] - Skip database (single session)")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'n':
            return self._create_new_site()
        elif choice.isdigit() and sites:
            idx = int(choice)
            if 0 <= idx < len(sites):
                return self._load_site(sites[idx])
        
        print("Continuing without database...")
        return False
    
    def _get_existing_sites(self):
        """Get list of existing database sites"""
        sites = []
        if os.path.exists(self.base_path):
            for item in os.listdir(self.base_path):
                item_path = os.path.join(self.base_path, item)
                if os.path.isdir(item_path):
                    page_files = [f for f in os.listdir(item_path) if f.startswith('page_')]
                    if page_files or os.path.exists(os.path.join(item_path, "meta.json")):
                        sites.append(item)
        return sorted(sites)
    
    def _create_new_site(self):
        """Create a new database site"""
        site_name = input("Enter job site name (e.g., 'workday_hhmi'): ").strip()
        if not site_name:
            print("❌ Site name cannot be empty")
            return False
        
        site_name = site_name.lower().replace(' ', '_')
        self.current_site = site_name
        self.site_path = os.path.join(self.base_path, site_name)
        
        if os.path.exists(self.site_path):
            overwrite = input(f"Site '{site_name}' already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("Aborting...")
                return False
        
        os.makedirs(self.site_path, exist_ok=True)
        
        meta = {
            'site_name': site_name,
            'created': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_pages': 0,
            'url': '',
            'description': input("Brief description (optional): ").strip() or "",
            'version': '1.0'
        }
        
        meta_path = os.path.join(self.site_path, "meta.json")
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        
        print(f"✅ Created site: {site_name}")
        print(f"📁 Location: {self.site_path}")
        return True
    
    def _load_site(self, site_name):
        """Load an existing database site"""
        self.current_site = site_name
        self.site_path = os.path.join(self.base_path, site_name)
        
        if not os.path.exists(self.site_path):
            print(f"❌ Site not found: {site_name}")
            return False
        
        # Load metadata
        meta_path = os.path.join(self.site_path, "meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                print(f"📊 Site: {meta.get('site_name', site_name)}")
            except:
                pass
        
        # Load all pages
        self.pages = []
        page_files = sorted([f for f in os.listdir(self.site_path) 
                           if f.startswith('page_') and f.endswith('.json')])
        
        for filename in page_files:
            filepath = os.path.join(self.site_path, filename)
            try:
                with open(filepath, 'r') as f:
                    page_data = json.load(f)
                    
                    # Convert coordinate strings back to tuples
                    if 'coordinate_space' in page_data:
                        reconstructed_space = {}
                        for coord_str, node_data in page_data['coordinate_space'].items():
                            coord = self._string_to_coordinate(coord_str)
                            reconstructed_space[coord] = node_data
                        page_data['coordinate_space'] = reconstructed_space
                    
                    # Parse PeterBot paths if they exist
                    if 'peterbot_paths' in page_data:
                        parsed_paths = []
                        for path in page_data['peterbot_paths']:
                            parsed_path = [self._string_to_coordinate(coord_str) for coord_str in path]
                            parsed_paths.append(parsed_path)
                        page_data['peterbot_paths'] = parsed_paths
                    
                    self.pages.append(page_data)
            except Exception as e:
                print(f"⚠️ Could not load {filename}: {e}")
        
        self.current_page_idx = 0
        self.is_loaded = True
        
        print(f"✅ Loaded {len(self.pages)} pages from {site_name}")
        return True
    
    def _string_to_coordinate(self, coord_str):
        """Convert string to coordinate tuple"""
        if not coord_str:
            return ()
        
        # Handle old format: "(0,1,2)"
        if coord_str.startswith('(') and coord_str.endswith(')'):
            coord_str = coord_str[1:-1]
        
        if not coord_str:
            return ()
        
        if "," in coord_str:
            parts = coord_str.split(",")
            return tuple(int(part.strip()) for part in parts if part.strip())
        
        try:
            return (int(coord_str),)
        except:
            return ()
    
    def save_current_page(self, snapshot, page_name="", url="", paths=None):
        """Save current page to database"""
        if not self.current_site or not self.site_path:
            print("⚠️ No site loaded - cannot save")
            return None
        
        # Get shaved elements
        shaved_elements = set()
        if hasattr(snapshot, 'visualizer') and hasattr(snapshot.visualizer, 'shaved_elements'):
            shaved_elements = snapshot.visualizer.shaved_elements
        
        # Generate page name
        if not page_name:
            page_name = f"page_{len(self.pages) + 1}"
            if url:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                if parsed.path:
                    path_parts = parsed.path.split('/')
                    if len(path_parts) > 1:
                        page_name = path_parts[-1] or path_parts[-2]
        
        page_name = page_name.replace(' ', '_').lower()[:50]
        
        page_data = {
            'page_name': page_name,
            'url': url or "",
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'dom_stats': getattr(snapshot, 'dom_stats', {}),
            'interaction_label': getattr(snapshot, 'interaction_label', 'scan')
        }
        
        branch_coords = getattr(snapshot, 'branch_coordinates', {})
        if branch_coords:
            serializable_coords = {}
            shaved_count = 0
            
            for coord, node in branch_coords.items():
                if coord in shaved_elements:
                    shaved_count += 1
                    continue
                
                coord_str = self._coordinate_to_string(coord)
                
                node_data = {
                    'type': node.type,
                    'structural_role': node.structural_role,
                    'pattern_roles': node.pattern_roles,
                    'is_interactive': node.is_interactive,
                    'text': node.text,
                    'classes': node.classes,
                    'depth': node.depth,
                    'is_offline': True,
                    'hash': node.current_hash,
                }
                serializable_coords[coord_str] = node_data
            
            page_data['coordinate_space'] = serializable_coords
            page_data['total_elements'] = len(serializable_coords)
            
            if shaved_count > 0:
                print(f"🔪 Excluded {shaved_count} shaved elements")
        
        if paths:
            filtered_paths = []
            for path in paths:
                path_contains_shaved = False
                for coord in path:
                    if coord in shaved_elements:
                        path_contains_shaved = True
                        break
                
                if not path_contains_shaved:
                    safe_path = [self._coordinate_to_string(coord) for coord in path]
                    filtered_paths.append(safe_path)
            
            if filtered_paths:
                page_data['peterbot_paths'] = filtered_paths
        
        # Save file
        page_num = len([f for f in os.listdir(self.site_path) if f.startswith('page_')]) + 1
        filename = f"page_{page_num:03d}_{page_name}.json"
        filepath = os.path.join(self.site_path, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(page_data, f, indent=2)
            
            print(f"💾 Saved: {filename}")
            print(f"   📍 {page_name}")
            print(f"   🔗 {url or 'No URL'}")
            print(f"   📊 {page_data.get('total_elements', 0)} elements")
            
            if self.is_loaded:
                self.pages.append(page_data)
            
            return filename
            
        except Exception as e:
            print(f"❌ Failed to save page: {e}")
            return None
    
    def _coordinate_to_string(self, coord):
        """Convert coordinate tuple to string"""
        if not coord:
            return "()"
        return ",".join(str(x) for x in coord)
    
    def list_saved_pages_with_options(self):
        """List all saved pages with options to load/delete"""
        if not self.site_path or not os.path.exists(self.site_path):
            print("❌ No database folder found")
            return []
        
        page_files = sorted([f for f in os.listdir(self.site_path) 
                           if f.startswith('page_') and f.endswith('.json')])
        
        if not page_files:
            print("📭 No saved pages found")
            return []
        
        print(f"\n📄 PAGES in '{self.current_site}':")
        print("="*60)
        
        for i, filename in enumerate(page_files):
            filepath = os.path.join(self.site_path, filename)
            try:
                with open(filepath, 'r') as f:
                    page_data = json.load(f)
                    page_name = page_data.get('page_name', filename.replace('.json', ''))
                    elements = page_data.get('total_elements', 0)
                    timestamp = page_data.get('timestamp', 'Unknown')
                    
                    current_marker = "👉" if i == self.current_page_idx else "  "
                    print(f"{current_marker}[{i}] {page_name}")
                    print(f"     📊 {elements} elements | 📅 {timestamp}")
                    print(f"     📁 {filename}")
                    
            except Exception as e:
                print(f"[{i}] ❌ Corrupted: {filename}")
        
        print("\n💡 Commands:")
        print("   load <num>    - Load page")
        print("   delete <num>  - Delete page")
        print("   cleanup       - Delete ALL pages")
        print("   back          - Return")
        
        return page_files
    
    def load_page_by_index(self, index):
        """Load a page by its index"""
        page_files = [f for f in os.listdir(self.site_path) 
                     if f.startswith('page_') and f.endswith('.json')]
        
        if not page_files:
            print("❌ No saved pages")
            return None
        
        sorted_pages = sorted(page_files)
        
        if 0 <= index < len(sorted_pages):
            filename = sorted_pages[index]
            filepath = os.path.join(self.site_path, filename)
            try:
                with open(filepath, 'r') as f:
                    page_data = json.load(f)
                    
                    if 'coordinate_space' in page_data:
                        reconstructed_space = {}
                        for coord_str, node_data in page_data['coordinate_space'].items():
                            coord = self._string_to_coordinate(coord_str)
                            reconstructed_space[coord] = node_data
                        page_data['coordinate_space'] = reconstructed_space
                    
                    print(f"✅ Loaded: {filename}")
                    return page_data
                    
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")
                return None
        else:
            print(f"❌ Invalid index. Available: 0-{len(sorted_pages)-1}")
            return None
    
    def delete_page_by_index(self, index):
        """Delete a page by index"""
        page_files = [f for f in os.listdir(self.site_path) 
                     if f.startswith('page_') and f.endswith('.json')]
        
        if not page_files:
            print("❌ No saved pages")
            return False
        
        sorted_pages = sorted(page_files)
        
        if 0 <= index < len(sorted_pages):
            filename = sorted_pages[index]
            filepath = os.path.join(self.site_path, filename)
            
            try:
                with open(filepath, 'r') as f:
                    page_data = json.load(f)
                    page_name = page_data.get('page_name', filename)
            except:
                page_name = filename
            
            confirm = input(f"⚠️ Delete '{page_name}'? (y/n): ").strip().lower()
            if confirm == 'y':
                os.remove(filepath)
                print(f"🗑️  Deleted: {filename}")
                self._update_metadata()
                return True
            else:
                print("❌ Deletion cancelled")
                return False
        else:
            print(f"❌ Invalid index. Available: 0-{len(sorted_pages)-1}")
            return False
    
    def cleanup_all_pages(self):
        """Delete all saved pages"""
        page_files = [f for f in os.listdir(self.site_path) 
                     if f.startswith('page_') and f.endswith('.json')]
        
        if not page_files:
            print("📭 No pages to delete")
            return
        
        print(f"⚠️  WARNING: This will delete {len(page_files)} pages!")
        print("   This action cannot be undone!")
        
        confirm = input("Type 'DELETE' to confirm: ").strip()
        if confirm == "DELETE":
            deleted_count = 0
            for filename in page_files:
                filepath = os.path.join(self.site_path, filename)
                os.remove(filepath)
                deleted_count += 1
            
            meta_path = os.path.join(self.site_path, "meta.json")
            if os.path.exists(meta_path):
                os.remove(meta_path)
            
            self._update_metadata()
            print(f"\n✅ Cleanup complete! Deleted {deleted_count} pages.")
        else:
            print("❌ Cleanup cancelled")
    
    def _update_metadata(self):
        """Update site metadata"""
        if not self.site_path:
            return
        
        meta_path = os.path.join(self.site_path, "meta.json")
        meta = {}
        
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
            except:
                pass
        
        meta['site_name'] = self.current_site
        meta['last_updated'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        page_files = [f for f in os.listdir(self.site_path) if f.startswith('page_')]
        meta['total_pages'] = len(page_files)
        
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
    
    def get_current_page(self):
        """Get current page data"""
        if self.is_loaded and 0 <= self.current_page_idx < len(self.pages):
            return self.pages[self.current_page_idx]
        return None
    
    def get_current_page_name(self):
        """Get current page name"""
        page = self.get_current_page()
        if page:
            return page.get('page_name', f"Page {self.current_page_idx + 1}")
        return "No page loaded"
    
    def next_page(self):
        """Move to next page"""
        if self.is_loaded and self.current_page_idx < len(self.pages) - 1:
            self.current_page_idx += 1
            print(f"➡️ Page {self.current_page_idx + 1}/{len(self.pages)}: {self.get_current_page_name()}")
            return True
        elif self.is_loaded:
            print("⚠️ Already on last page")
        return False
    
    def prev_page(self):
        """Move to previous page"""
        if self.is_loaded and self.current_page_idx > 0:
            self.current_page_idx -= 1
            print(f"⬅️ Page {self.current_page_idx + 1}/{len(self.pages)}: {self.get_current_page_name()}")
            return True
        elif self.is_loaded:
            print("⚠️ Already on first page")
        return False
    
    def get_page_count(self):
        """Get total page count"""
        if self.is_loaded:
            return len(self.pages)
        return 0
    
    def is_active(self):
        """Check if database is active"""
        return self.is_loaded and self.current_site is not None

# ===== PATTERN DETECTION SYSTEM =====

class PatternDetectors:
    """Detect fundamental interaction patterns"""
    
    @staticmethod
    def detect_action_element(branch_tuple, element_data, parent_data, siblings, coordinate_space):
        """Detect action elements (buttons, links, submits)"""
        if element_data.get('type') in ['button', 'a', 'input']:
            element_type = element_data.get('type', '')
            text = element_data.get('text', '').strip()
            
            if element_type in ['button', 'a']:
                return 'ACTION_ELEMENT'
            
            if element_type == 'input':
                input_type = element_data.get('attributes', {}).get('type', '')
                if input_type in ['submit', 'button', 'reset']:
                    return 'ACTION_ELEMENT'
                
                action_words = ['submit', 'login', 'search', 'go', 'send', 'apply', 'next', 'continue']
                if any(word in text.lower() for word in action_words):
                    return 'ACTION_ELEMENT'
        
        return None
    
    @staticmethod
    def detect_data_input(branch_tuple, element_data, parent_data, siblings, coordinate_space):
        """Detect data input elements"""
        if element_data.get('type') in ['input', 'textarea', 'select']:
            element_type = element_data.get('type', '')
            
            if element_type in ['textarea', 'select']:
                return 'DATA_INPUT'
            
            if element_type == 'input':
                input_type = element_data.get('attributes', {}).get('type', '')
                if input_type not in ['submit', 'button', 'reset', 'image']:
                    return 'DATA_INPUT'
        
        return None
    
    @staticmethod
    def detect_context_element(branch_tuple, element_data, parent_data, siblings, coordinate_space):
        """Detect context elements (labels, help text)"""
        element_type = element_data.get('type', '')
        text = element_data.get('text', '').strip()
        
        if element_type == 'label':
            return 'CONTEXT_ELEMENT'
        
        if text and len(text) > 2:
            has_interactive_sibling = any(
                s.get('type') in ['input', 'button', 'textarea', 'select'] 
                for s in siblings
            )
            
            parent_has_interactive = False
            if parent_data:
                parent_children = PatternDetectors._get_child_branches(branch_tuple[:-1], coordinate_space)
                parent_has_interactive = any(
                    coordinate_space.get(child, {}).get('type') in ['input', 'button', 'textarea', 'select']
                    for child in parent_children
                )
            
            if has_interactive_sibling or parent_has_interactive:
                return 'CONTEXT_ELEMENT'
        
        return None
    
    @staticmethod
    def detect_state_indicator(branch_tuple, element_data, parent_data, siblings, coordinate_space):
        """Detect state indicators (validation, progress, status)"""
        element_type = element_data.get('type', '')
        text = element_data.get('text', '').strip()
        classes = element_data.get('classes', '').lower()
        
        if text and ('*' in text or 'required' in text.lower()):
            return 'STATE_INDICATOR'
        
        validation_terms = ['error', 'valid', 'invalid', 'warning', 'success', 'fail']
        if any(term in text.lower() for term in validation_terms) or any(term in classes for term in validation_terms):
            return 'STATE_INDICATOR'
        
        progress_terms = ['progress', 'loading', 'spinner', 'complete', 'step']
        if any(term in text.lower() for term in progress_terms) or any(term in classes for term in progress_terms):
            return 'STATE_INDICATOR'
        
        if element_type in ['progress', 'meter']:
            return 'STATE_INDICATOR'
        
        return None
    
    @staticmethod
    def _get_child_branches(parent_branch, coordinate_space):
        """Get child branches for a parent coordinate"""
        children = []
        child_index = 0
        while True:
            child_branch = parent_branch + (child_index,)
            if child_branch in coordinate_space:
                children.append(child_branch)
                child_index += 1
            else:
                break
        return children

class PatternRegistry:
    """Registry for pattern detectors"""
    
    def __init__(self):
        self.detectors = []
        self.active_mode = "general"
        self.mode_configs = {
            "general": [
                (PatternDetectors.detect_action_element, 0.95),
                (PatternDetectors.detect_data_input, 0.95),
                (PatternDetectors.detect_context_element, 0.90),
                (PatternDetectors.detect_state_indicator, 0.85),
            ],
            "authentication": [
                (PatternDetectors.detect_data_input, 0.98),
                (PatternDetectors.detect_action_element, 0.96),
                (PatternDetectors.detect_context_element, 0.92),
                (PatternDetectors.detect_state_indicator, 0.88),
            ],
            "job_application": [
                (PatternDetectors.detect_data_input, 0.98),
                (PatternDetectors.detect_action_element, 0.96),
                (PatternDetectors.detect_context_element, 0.94),
                (PatternDetectors.detect_state_indicator, 0.90),
            ]
        }
    
    def prompt_for_mode(self, current_url):
        """Prompt user to select pattern mode"""
        print(f"\n🎯 PATTERN MODE SELECTION")
        print(f"📍 Current URL: {current_url}")
        print("Available modes:")
        print("  'general' - All fundamental patterns")
        print("  'job_application' - Form-heavy patterns")
        print("  'authentication' - Login/signup patterns")
        print("  'none' - Disable pattern enhancement")
        
        choice = input("Select pattern mode (enter for general): ").strip().lower()
        if choice in self.mode_configs:
            self.active_mode = choice
        else:
            self.active_mode = "general"
        
        print(f"✅ Pattern mode set to: {self.active_mode}")
        return self.active_mode
    
    def run_detection_pipeline(self, branch_tuple, element_data, parent_data, coordinate_space):
        """Run pattern detection on an element"""
        if self.active_mode == "none":
            return []
        
        siblings = []
        if branch_tuple and len(branch_tuple) > 0:
            parent_branch = branch_tuple[:-1]
            siblings = self._get_sibling_elements(parent_branch, coordinate_space)
        
        detected_patterns = []
        for detector_func, confidence in self.mode_configs.get(self.active_mode, []):
            try:
                detected_pattern = detector_func(branch_tuple, element_data, parent_data, siblings, coordinate_space)
                if detected_pattern:
                    detected_patterns.append(detected_pattern)
            except Exception:
                continue
        
        return detected_patterns
    
    def _get_sibling_elements(self, parent_branch, coordinate_space):
        """Get sibling elements for pattern analysis"""
        siblings = []
        if parent_branch in coordinate_space:
            children = self._get_child_branches(parent_branch, coordinate_space)
            siblings = [coordinate_space.get(child) for child in children if coordinate_space.get(child)]
        return siblings
    
    def _get_child_branches(self, parent_branch, coordinate_space):
        """Get child branches of a parent coordinate"""
        children = []
        child_index = 0
        while True:
            child_branch = parent_branch + (child_index,)
            if child_branch in coordinate_space:
                children.append(child_branch)
                child_index += 1
            else:
                break
        return children

class StructuralPatterns:
    """Basic structural role classification"""
    
    INTERACTIVE_TAGS = {
        'button', 'input', 'a', 'select', 'textarea', 
        'details', 'summary', 'menu', 'menuitem'
    }
    
    STRUCTURAL_TAGS = {
        'div', 'section', 'main', 'article', 'nav', 
        'header', 'footer', 'aside', 'figure'
    }
    
    CONTENT_TAGS = {
        'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'label', 'li', 'td', 'th', 'caption', 'figcaption'
    }
    
    FORM_CONTEXTS = {
        ('form', 'input'): 'FORM_FIELD',
        ('form', 'button'): 'FORM_SUBMIT',
        ('form', 'select'): 'FORM_FIELD', 
        ('form', 'textarea'): 'FORM_FIELD',
        ('form', 'label'): 'FORM_LABEL'
    }
    
    NAVIGATION_CONTEXTS = {
        ('nav', 'a'): 'NAV_LINK',
        ('ul', 'a'): 'NAV_LINK',
        ('ol', 'a'): 'NAV_LINK'
    }
    
    pattern_registry = PatternRegistry()
    
    @classmethod
    def get_basic_structural_role(cls, element_data, parent_data=None):
        """Get basic structural role for element"""
        tag = element_data.get('type', 'unknown').lower()
        
        if tag in cls.INTERACTIVE_TAGS:
            base_role = 'INTERACTIVE'
        elif tag in cls.STRUCTURAL_TAGS:
            base_role = 'STRUCTURAL'
        elif tag in cls.CONTENT_TAGS:
            base_role = 'CONTENT'
        else:
            base_role = 'UNKNOWN'
        
        if parent_data:
            parent_tag = parent_data.get('type', 'unknown').lower()
            context_key = (parent_tag, tag)
            
            if context_key in cls.FORM_CONTEXTS:
                base_role = cls.FORM_CONTEXTS[context_key]
            if context_key in cls.NAVIGATION_CONTEXTS:
                base_role = cls.NAVIGATION_CONTEXTS[context_key]
        
        return base_role

# ===== CORE DATA STRUCTURES =====

class CoordinateNode:
    """Represents a DOM element as a coordinate node"""
    
    def __init__(self, coordinate, element_data):
        self.coordinate = coordinate if isinstance(coordinate, tuple) else (coordinate,)
        
        if hasattr(element_data, 'get'):
            self.type = element_data.get('type', 'unknown')
            self.structural_role = element_data.get('structural_role', 'UNKNOWN')
            self.pattern_roles = element_data.get('pattern_roles', [])
            self.is_interactive = element_data.get('is_interactive', False)
            self.text = element_data.get('text', '')
            self.classes = element_data.get('classes', '')
            self.depth = element_data.get('depth', len(self.coordinate))
            self.is_offline = element_data.get('is_offline', False)
            self.current_hash = element_data.get('hash', '')
        else:
            self.type = 'unknown'
            self.structural_role = 'UNKNOWN'
            self.pattern_roles = []
            self.is_interactive = False
            self.text = ''
            self.classes = ''
            self.depth = len(self.coordinate)
            self.is_offline = False
            self.current_hash = ''
        
        self.current_data = element_data if hasattr(element_data, 'get') else {}
        self.element_type = self.type
        self.element_hash = self.current_hash
        self.attributes = self.current_data.get('attributes', {})
        self.color = self._calculate_node_color()
    
    def _calculate_node_color(self):
        """Calculate color based on patterns and role"""
        color_palette = {
            'ACTION_ELEMENT': (255, 180, 50),
            'DATA_INPUT': (80, 180, 255),
            'CONTEXT_ELEMENT': (100, 220, 220),
            'STATE_INDICATOR': (200, 100, 255),
            'INTERACTIVE': (255, 200, 80),
            'STRUCTURAL': (100, 150, 220),
            'CONTENT': (180, 180, 240),
            'FORM_FIELD': (80, 200, 220),
            'FORM_SUBMIT': (255, 150, 80),
            'NAV_LINK': (100, 240, 180),
            'UNKNOWN': (150, 150, 200),
        }
        
        for pattern in self.pattern_roles:
            if pattern in color_palette:
                return color_palette[pattern]
        
        if self.structural_role in color_palette:
            return color_palette[self.structural_role]
        
        return color_palette['UNKNOWN']
    
    def calculate_current_hash(self, element_data=None):
        """Calculate hash for element"""
        if element_data is None:
            element_data = self.current_data
        
        content_parts = [
            f"type:{element_data.get('type', '')}",
            f"text:{element_data.get('text', '')}",
            f"classes:{element_data.get('classes', '')}",
            f"visible:{element_data.get('is_visible', False)}",
            f"enabled:{element_data.get('is_enabled', False)}"
        ]
        content = "|".join(content_parts)
        return hashlib.md5(content.encode()).hexdigest()[:16]

@dataclass
class DOMSnapshot:
    """Snapshot of DOM structure"""
    branch_coordinates: Dict[Tuple[int, ...], CoordinateNode]
    timestamp: float
    dom_stats: Dict[str, Any]
    interaction_label: Optional[str] = None
    target_element: Optional[Tuple[int, ...]] = None

# ===== DOM SCANNER =====

class DOMScanner:
    """Scans DOM and detects patterns"""
    
    def __init__(self, driver, verbose=False):
        self.driver = driver
        self.verbose = verbose
        self.coordinate_space = {}
        self.element_to_coord = {}
        self.siblings_per_depth = {}
        self.max_dom_depth = 0
        self.pattern_mode_set = False
        self.pattern_registry = PatternRegistry()
        self.scan_progress = 0
        self.scan_total = 0
        self.scan_start_time = 0
    
    def scan_dom(self, prompt_for_patterns=True):
        """Scan DOM and detect patterns"""
        print("🔍 Scanning DOM...")
        
        self.coordinate_space = {}
        self.element_to_coord = {}
        self.siblings_per_depth = {}
        self.max_dom_depth = 0
        
        if not self.driver:
            raise RuntimeError("No browser driver available")
        
        try:
            self.scan_total = self._estimate_dom_size()
            self.scan_progress = 0
            self.scan_start_time = time.time()
            
            print(f"📊 ~{self.scan_total} elements")
            print()
            
            root = self.driver.find_element(By.XPATH, "/*")
            success = self._scan_dom_tree_with_progress(root, (0,))
            
            if not success:
                raise RuntimeError("Scan failed")
            
            print("\r" + " " * 100 + "\r", end="")
            
            if prompt_for_patterns and not self.pattern_mode_set:
                try:
                    current_url = self.driver.current_url
                    self.pattern_registry.prompt_for_mode(current_url)
                    self.pattern_mode_set = True
                except Exception as e:
                    print(f"⚠️ Pattern prompt failed: {e}")
            
            if self.pattern_mode_set and self.pattern_registry.active_mode != "none":
                print("🎯 Running pattern detection...")
                self._detect_patterns()
            
            branch_coordinates = {}
            for branch_tuple, raw_data in self.coordinate_space.items():
                node = CoordinateNode(branch_tuple, raw_data)
                branch_coordinates[branch_tuple] = node
            
            stats = self._compute_dom_stats()
            
            print(f"✅ Scan complete: {len(branch_coordinates)} elements")
            return DOMSnapshot(
                branch_coordinates=branch_coordinates,
                timestamp=time.time(),
                dom_stats=stats
            )
            
        except Exception as e:
            print(f"❌ Scan failed: {e}")
            raise
    
    def _scan_dom_tree_with_progress(self, element, current_branch, depth=0, max_depth=50):
        """Recursively scan DOM tree with progress display"""
        if depth > max_depth:
            return True
        
        try:
            element_data = self._extract_element_data(element, current_branch)
            self.coordinate_space[current_branch] = element_data
            self.element_to_coord[element] = current_branch
            
            self.scan_progress += 1
            if self.scan_progress % 50 == 0:
                percent = (self.scan_progress / self.scan_total) * 100
                bar_width = 50
                filled = int(bar_width * self.scan_progress // self.scan_total)
                bar = '█' * filled + '░' * (bar_width - filled)
                print(f"\r[{bar}] {percent:.1f}%", end="")
            
            children = element.find_elements(By.XPATH, "./*")
            for i, child in enumerate(children):
                child_branch = current_branch + (i,)
                self._scan_dom_tree_with_progress(child, child_branch, depth + 1, max_depth)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error at {current_branch}: {e}")
            return True
    
    def _detect_patterns(self):
        """Run pattern detection on scanned elements"""
        patterns_detected = 0
        
        for branch_tuple, element_data in self.coordinate_space.items():
            parent_data = None
            if len(branch_tuple) > 1:
                parent_branch = branch_tuple[:-1]
                parent_data = self.coordinate_space.get(parent_branch)
            
            detected_patterns = self.pattern_registry.run_detection_pipeline(
                branch_tuple, element_data, parent_data, self.coordinate_space
            )
            
            if detected_patterns:
                element_data['pattern_roles'] = detected_patterns
                patterns_detected += 1
        
        print(f"✅ {patterns_detected} pattern instances detected")
    
    def _estimate_dom_size(self):
        """Estimate DOM size for progress bar"""
        try:
            count = self.driver.execute_script("return document.querySelectorAll('*').length;")
            return max(count + int(count * 0.1), 100)
        except:
            return 1000
    
    def _extract_element_data(self, element, branch_tuple):
        """Extract basic element data"""
        try:
            tag = element.tag_name.lower() if element.tag_name else "unknown"
            classes = element.get_attribute('class') or ""
            text = (element.text or "")[:30]
            
            element_dict = {'type': tag, 'classes': classes, 'text': text}
            parent_data = None
            
            if len(branch_tuple) > 1:
                parent_branch = branch_tuple[:-1]
                parent_data = self.coordinate_space.get(parent_branch)
            
            structural_role = StructuralPatterns.get_basic_structural_role(element_dict, parent_data)
            
            is_interactive = (
                tag in ['button', 'input', 'a', 'select', 'textarea', 'form'] or
                structural_role in ['INTERACTIVE', 'FORM_FIELD', 'FORM_SUBMIT', 'NAV_LINK']
            )
            
            content = f"{tag}|{classes}|{text}"
            element_hash = hashlib.md5(content.encode()).hexdigest()[:10]
            
            return {
                'type': tag,
                'classes': classes,
                'text': text,
                'hash': element_hash,
                'structural_role': structural_role,
                'depth': len(branch_tuple),
                'sibling_index': branch_tuple[-1] if branch_tuple else 0,
                'raw_element': element,
                'is_interactive': is_interactive,
                'pattern_roles': []
            }
            
        except Exception as e:
            return {
                'type': 'error', 'classes': '', 'text': str(e), 'hash': 'error',
                'structural_role': 'UNKNOWN', 'depth': len(branch_tuple),
                'sibling_index': branch_tuple[-1] if branch_tuple else 0,
                'raw_element': element, 'is_interactive': False, 'pattern_roles': []
            }
    
    def _compute_dom_stats(self):
        """Compute DOM statistics"""
        max_depth = self.max_dom_depth
        total_elements = len(self.coordinate_space)
        
        leaf_nodes = 0
        branch_nodes = 0
        for branch in self.coordinate_space.keys():
            children = self._get_child_branches(branch, self.coordinate_space)
            if len(children) == 0:
                leaf_nodes += 1
            else:
                branch_nodes += 1
        
        return {
            'total_elements': total_elements,
            'max_depth': max_depth,
            'leaf_nodes': leaf_nodes,
            'branch_nodes': branch_nodes,
            'tree_complexity': leaf_nodes / max(1, branch_nodes)
        }
    
    @staticmethod
    def _get_child_branches(parent_branch, coordinate_space):
        """Get children of a branch"""
        children = []
        child_index = 0
        while True:
            child_branch = parent_branch + (child_index,)
            if child_branch in coordinate_space:
                children.append(child_branch)
                child_index += 1
            else:
                break
        return children

# ===== VISUALIZER =====
class DOMStructureVisualizer:
    """WHERE MATHEMATICS BECOMES VISIBLE TRUTH"""

    def __init__(self, screen_width=1400, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = 35
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 0.1
        self.hovered_element = None
        self.show_path_mode = False 
        self.monitoring_active = False 
        self.recording_mode = False
        self.offline_mode = False
        # SHAVING ATTRIBUTES    
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("🌌 DOM STRUCTURE EXPLORER - Fundamental Patterns")
        
        self.shaved_elements = set()
        self.page_shaved_elements = {}  # {page_id: set_of_shaved_coords}
        self.page_shaved_map = {}
        self.current_page_id = None
        self.highlight_rect_start = None
        self.highlight_rect_end = None
        self.highlight_mode = False
        self.highlight_color = (255, 0, 0, 100)
    

        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 32)
        self.bold_font = pygame.font.Font(None, 28)
        
        # 🎨 ENHANCED SPACE-THEMED COLORS
        self.COSMIC_BG = (5, 8, 20)  # Deeper space blue
        self.GRID_COLOR = (30, 45, 90)  # Dimmer grid
        self.AXIS_COLOR = (80, 120, 200)  # Softer axis lines
        self.TEXT_COLOR = (180, 200, 255)  # Softer text
        self.PANEL_BG = (15, 25, 50)  # Darker panels
        self.HOVER_HIGHLIGHT = (255, 220, 100)  # Warmer gold
        self.PATH_MODE_COLOR = (100, 255, 150)  # Keep path green
        
        # 🎨 FUNDAMENTAL PATTERN GLOW COLORS
        self.pattern_glow_colors = {
            'ACTION_ELEMENT': (255, 180, 50),    # Nebula Orange
            'DATA_INPUT': (80, 180, 255),        # Quasar Blue
            'CONTEXT_ELEMENT': (100, 220, 220),  # Starlight Cyan
            'STATE_INDICATOR': (200, 100, 255),  # Pulsar Purple
        }
        
        # 🆕 INITIALIZE PATH ATTRIBUTES
        self.peterbot_paths = []
        self.peterbot_highlights = set()
        self.peterbot_analysis_info = None
        self.peterbot_analysis = None
        self.path_mode = False

        self.stars = []
        self._generate_diverse_starfield(150)  # 🎨 MORE STARS

        self.path_direction_colors = {
            'up': (220, 100, 100),    # Softer red
            'down': (100, 220, 100),  # Softer green  
            'left': (100, 100, 220),  # Softer blue
            'right': (220, 220, 100), # Softer yellow
        }

        self.shaved_elements = set()
        self.page_shaved_elements = {}  # {page_id: set_of_shaved_coords}
        self.page_shaved_map = {}
        self.current_page_id = None
        self.highlight_rect_start = None
        self.highlight_rect_end = None
        self.highlight_mode = False
        self.highlight_color = (255, 0, 0, 100)

    def _generate_diverse_starfield(self, num_stars):
        """CREATE DIVERSE COSMIC BACKGROUND WITH DIFFERENT COLOR STARS"""
        star_colors = [
            (255, 255, 255),  # White stars
            (200, 220, 255),  # Blue-white stars  
            (255, 220, 180),  # Yellow stars
            (220, 180, 255),  # Purple stars
            (180, 255, 220),  # Green stars
        ]
        
        for _ in range(num_stars):
            color = random.choice(star_colors)
            self.stars.append({
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height), 
                'size': random.uniform(0.3, 2.0),  # 🎨 VARIED SIZES
                'speed': random.uniform(0.1, 1.0),
                'brightness': random.uniform(0.2, 1.0),
                'color': color
            })

    def _draw_starfield(self):
        """DRAW THE ANIMATED DIVERSE COSMIC BACKGROUND"""
        time_val = pygame.time.get_ticks() * 0.001
        for star in self.stars:
            pulse = 0.3 + 0.7 * abs(math.sin(time_val * star['speed'] + star['x'] * 0.01))
            brightness = star['brightness'] * pulse
            r, g, b = star['color']
            color = (r * brightness, g * brightness, b * brightness)
            pygame.draw.circle(self.screen, color, (star['x'], star['y']), star['size'])

    def _zoom_at_position(self, mouse_pos, zoom_in=True):
        """ZOOM AT SPECIFIC MOUSE POSITION - KEEPS THAT POSITION UNDER MOUSE"""
        old_zoom = self.zoom
        
        # Calculate zoom factor
        zoom_factor = 1.1 if zoom_in else 0.9
        new_zoom = self.zoom * zoom_factor
        
        # Clamp zoom
        new_zoom = max(0.05, min(5.0, new_zoom))
        
        if new_zoom == self.zoom:
            return  # No change
        
        # Get mouse position in world coordinates before zoom
        mouse_world_x = (mouse_pos[0] - self.screen_width // 2 - self.pan_x) / self.zoom
        mouse_world_y = (mouse_pos[1] - 150 - self.pan_y) / self.zoom
        
        # Apply zoom
        self.zoom = new_zoom
        
        # Adjust pan to keep mouse over same world point
        self.pan_x = mouse_pos[0] - self.screen_width // 2 - mouse_world_x * self.zoom
        self.pan_y = mouse_pos[1] - 150 - mouse_world_y * self.zoom

    def _draw_hover_info(self, node: Optional[CoordinateNode]):
        """ENHANCED HOVER INFO WITH SIMPLE ICONS - NO EMOJIS"""
        if not node:
            return
        
        info_lines = []
        
        # === BASIC INFO ===
        info_lines.append(f"> COORDINATE: {node.coordinate}")
        info_lines.append(f"> DEPTH: {node.depth} | SIBLING INDEX: {node.coordinate[-1] if node.coordinate else 0}")
        info_lines.append("")
        
        # === ELEMENT INFO ===
        info_lines.append(f"> TYPE: {node.type}")
        info_lines.append(f"> STRUCTURAL ROLE: {node.structural_role}")
        
        if node.pattern_roles:
            info_lines.append(f"> PATTERNS: {', '.join(node.pattern_roles)}")
        
        # === CONTENT INFO ===
        if node.text and node.text.strip():
            text_preview = node.text[:50] + ("..." if len(node.text) > 50 else "")
            info_lines.append(f"> TEXT: '{text_preview}'")
        
        if node.classes and node.classes.strip():
            classes_preview = node.classes[:40] + ("..." if len(node.classes) > 40 else "")
            info_lines.append(f"> CLASSES: {classes_preview}")
        
        # === INTERACTIVITY ===
        info_lines.append(f"> INTERACTIVE: {'YES' if node.is_interactive else 'NO'}")
        
        if node.is_interactive:
            interactive_type = "CLICKABLE" if node.type in ['button', 'a'] else "INPUT" if node.type == 'input' else "INTERACTIVE"
            info_lines.append(f"  --> {interactive_type} element")
        
        # === OFFLINE STATUS ===
        if hasattr(node, 'is_offline'):
            info_lines.append(f"> OFFLINE MODE: {'Yes' if node.is_offline else 'No'}")
        
        # === PATH INFORMATION ===
        if hasattr(self, 'peterbot_paths') and self.peterbot_paths:
            path_roles = []
            for i, path in enumerate(self.peterbot_paths):
                if node.coordinate in path:
                    position = path.index(node.coordinate)
                    is_target = (position == len(path) - 1)
                    is_start = (position == 0)
                    
                    if is_target:
                        path_roles.append(f"* TARGET of Path {i+1}")
                    elif is_start:
                        path_roles.append(f"* START of Path {i+1}")
                    else:
                        path_roles.append(f"* Step {position+1} in Path {i+1}")
            
            if path_roles:
                info_lines.append("")
                info_lines.append("> PATH ROLES:")
                info_lines.extend(path_roles[:3])
        
        # === CONNECTIONS INFO ===
        if hasattr(self, 'app') and hasattr(self.app, 'current_snapshot') and self.app.current_snapshot:
            # Check if this node has children
            children = []
            child_index = 0
            while True:
                child_coord = node.coordinate + (child_index,)
                if child_coord in self.app.current_snapshot.branch_coordinates:
                    children.append(child_coord)
                    child_index += 1
                else:
                    break
            
            if children:
                info_lines.append("")
                info_lines.append(f"> CHILDREN: {len(children)} direct descendants")
            
            # Check parent
            if node.coordinate and len(node.coordinate) > 0:
                parent_coord = node.coordinate[:-1]
                if parent_coord in self.app.current_snapshot.branch_coordinates:
                    parent_node = self.app.current_snapshot.branch_coordinates[parent_coord]
                    info_lines.append(f"> PARENT: {parent_coord} ({parent_node.type})")
        
        # === SHAVED STATUS ===
        if hasattr(self, 'shaved_elements') and node.coordinate in self.shaved_elements:
            info_lines.append("")
            info_lines.append("> SHAVED: This element is hidden")
            info_lines.append("  * Not visible in visualization")
            info_lines.append("  * Excluded from PeterBot analysis")
            info_lines.append("  * Press X to un-shave (if in shaving mode)")
        
        # Draw the info panel
        info_panel_height = min(400, 30 + (len(info_lines) * 20))
        info_panel = pygame.Rect(self.screen_width - 500, self.screen_height - info_panel_height, 480, info_panel_height - 10)
        
        # Background with gradient effect
        pygame.draw.rect(self.screen, self.PANEL_BG, info_panel, border_radius=10)
        pygame.draw.rect(self.screen, self.AXIS_COLOR, info_panel, 3, border_radius=10)
        
        # Add subtle header
        header_rect = pygame.Rect(info_panel.x, info_panel.y, info_panel.width, 30)
        pygame.draw.rect(self.screen, (40, 60, 100), header_rect, border_radius=10)
        header_text = self.small_font.render("ELEMENT INSPECTOR", True, (200, 220, 255))
        self.screen.blit(header_text, (info_panel.x + 10, info_panel.y + 8))
        
        # Draw all info lines
        y_offset = info_panel.y + 40
        for line in info_lines:
            # Color coding for different types of info
            if line.startswith("> COORDINATE") or line.startswith("> DEPTH"):
                color = (100, 220, 255)  # Cyan for coordinates
            elif line.startswith("> TYPE") or line.startswith("> STRUCTURAL") or line.startswith("> PATTERNS"):
                color = (255, 220, 100)  # Yellow for element info
            elif line.startswith("> TEXT") or line.startswith("> CLASSES"):
                color = (220, 180, 255)  # Purple for content
            elif line.startswith("> INTERACTIVE"):
                color = (100, 255, 150) if node.is_interactive else (200, 100, 100)  # Green/Red for interactive
            elif "* TARGET" in line or "* START" in line or "PATH" in line:
                color = (255, 150, 150)  # Red for path info
            elif line.startswith("> SHAVED"):
                color = (255, 100, 100)  # Bright red for shaved
            elif line.startswith("> CHILDREN") or line.startswith("> PARENT"):
                color = (150, 220, 150)  # Green for connections
            elif "-->" in line:
                color = (180, 220, 255)  # Light blue for sub-info
            else:
                color = self.TEXT_COLOR
            
            # Wrap long lines
            if len(line) > 60:
                parts = []
                current = line
                while len(current) > 60:
                    split_pos = current[:60].rfind(' ')
                    if split_pos == -1:
                        split_pos = 60
                    parts.append(current[:split_pos])
                    current = current[split_pos:].strip()
                if current:
                    parts.append(current)
                
                for part in parts:
                    text_surface = self.small_font.render(part, True, color)
                    self.screen.blit(text_surface, (info_panel.x + 10, y_offset))
                    y_offset += 18
            else:
                text_surface = self.small_font.render(line, True, color)
                self.screen.blit(text_surface, (info_panel.x + 10, y_offset))
                y_offset += 18
        
        # Add subtle border glow based on element type
        if node.is_interactive:
            glow_color = (100, 255, 100, 30)
        elif node.pattern_roles and 'ACTION_ELEMENT' in node.pattern_roles:
            glow_color = (255, 200, 50, 30)
        elif node.pattern_roles and 'DATA_INPUT' in node.pattern_roles:
            glow_color = (80, 180, 255, 30)
        else:
            glow_color = (100, 100, 200, 30)
        
        # Draw glow effect
        glow_surface = pygame.Surface((info_panel.width + 10, info_panel.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, glow_color, 
                        (5, 5, info_panel.width, info_panel.height), 
                        border_radius=12)
        self.screen.blit(glow_surface, (info_panel.x - 5, info_panel.y - 5))
                                    
    def _generate_path_info(self, node: CoordinateNode) -> List[str]:
        """GENERATE REVERSE TRANSFORM PATH INFORMATION FOR NODE"""
        coord = node.coordinate
        
        depth = len(coord)
        sibling_counts = self._get_sibling_counts_along_path(coord)
        
        structural_path = self._generate_structural_path(coord)
        xpath_equivalent = self._generate_xpath_equivalent(coord)
        css_equivalent = self._generate_css_equivalent(coord)
        
        return [
            "=== PATH DISPLAY MODE ===",
            "Press T to toggle back to element view",
            f"Coordinate: {coord}",
            f"Structural: {structural_path}",
            f"XPath: {xpath_equivalent}",
            f"CSS: {css_equivalent}",
            f"Depth: {depth} steps from root",
            f"Complexity: {self._assess_branching_complexity(sibling_counts)}",
            f"Siblings: {sibling_counts}",
            f"Element Type: {node.type}",
            f"Role: {node.structural_role}",
            f"Patterns: {', '.join(node.pattern_roles)}"
        ]

    def _generate_structural_path(self, coord: Tuple[int, ...]) -> str:
        """GENERATE HUMAN-READABLE STRUCTURAL PATH"""
        if not coord:
            return "root"
        
        path_parts = ["root"]
        for i, branch_index in enumerate(coord):
            path_parts.append(f"child[{branch_index + 1}]")
        
        return " → ".join(path_parts)

    def _generate_xpath_equivalent(self, coord: Tuple[int, ...]) -> str:
        """GENERATE XPATH EQUIVALENT FROM COORDINATE"""
        if not coord:
            return "/*[1]"
        
        xpath_parts = ["/*[1]"]
        for branch_index in coord:
            xpath_parts.append(f"/*[{branch_index + 1}]")
        
        return "".join(xpath_parts)

    def _generate_css_equivalent(self, coord: Tuple[int, ...]) -> str:
        """GENERATE CSS EQUIVALENT APPROXIMATION"""
        if not coord:
            return ":root"
        
        css_parts = [":root"]
        for branch_index in coord:
            css_parts.append(f" > *:nth-child({branch_index + 1})")
        
        return "".join(css_parts)

    def _get_sibling_counts_along_path(self, coord: Tuple[int, ...]) -> List[int]:
        """GET SIBLING COUNTS AT EACH LEVEL ALONG THE PATH"""
        sibling_counts = []
        current_path = ()
        
        for i in range(len(coord)):
            current_path = coord[:i]
            sibling_counts.append(coord[i] + 1)
        
        return sibling_counts

    def _assess_branching_complexity(self, sibling_counts: List[int]) -> str:
        """ASSESS BRANCHING COMPLEXITY BASED ON SIBLING COUNTS"""
        if not sibling_counts:
            return "Unknown"
        
        avg_siblings = sum(sibling_counts) / len(sibling_counts)
        if avg_siblings < 3:
            return "Low complexity"
        elif avg_siblings < 7:
            return "Medium complexity"
        else:
            return "High complexity"
    
    
    def _draw_element_node(self, screen_pos, node, branch_tuple):
        """DRAW COORDINATENODE WITH TARGET NODE HIGHLIGHTING"""
        if branch_tuple in self.shaved_elements:
            return
        
        # 🎯 CHECK IF THIS IS A PATH TARGET NODE (last in any path)
        is_target_node = False
        if hasattr(self, 'peterbot_paths') and self.peterbot_paths:
            for path in self.peterbot_paths:
                if path and branch_tuple == path[-1]:  # Last node in path
                    is_target_node = True
                    break
        
        # 🎯 TARGET NODES GET SPECIAL COLOR
        if is_target_node:
            # Pulse animation for target nodes
            pulse = 2.0 + math.sin(pygame.time.get_ticks() * 0.01) * 1.0
            base_size = 10
            
            # Red/orange glow for target nodes
            target_color = (255, 100, 50)  # Orange-red
            for i in range(3):
                glow_size = base_size + pulse + (i * 3)
                alpha = 100 - (i * 25)
                glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*target_color, alpha), 
                                (glow_size, glow_size), glow_size)
                self.screen.blit(glow_surface, (screen_pos[0] - glow_size, screen_pos[1] - glow_size))
            
            # Draw the node
            pygame.draw.circle(self.screen, target_color, screen_pos, base_size)
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, base_size, 2)
            
            # Add target symbol
            target_text = "🎯"
            symbol_surface = pygame.font.Font(None, 20).render(target_text, True, (255, 255, 255))
            text_rect = symbol_surface.get_rect(center=screen_pos)
            self.screen.blit(symbol_surface, text_rect)
            
        else:
            # Normal node drawing
            base_size = 8
            pygame.draw.circle(self.screen, node.color, screen_pos, base_size)
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, base_size, 2)
            
    def _get_element_symbol(self, element_type):
        """GET SYMBOL FOR ELEMENT TYPE"""
        symbols = {
            'button': 'B', 'input': 'I', 'a': 'L', 'textarea': 'T',
            'select': 'S', 'form': 'F', 'div': 'D', 'span': 'S'
        }
        return symbols.get(element_type, element_type[0].upper() if element_type else '?')
    
    def _draw_structure_legend(self):
        """CLEAN LEGEND WITH FUNDAMENTAL PATTERNS - FIXED: Handle missing analysis_info"""
        legend_x, legend_y = 20, 240
        legend_width = 320
        legend_height = 520
        
        legend_rect = pygame.Rect(legend_x - 10, legend_y - 10, legend_width, legend_height)
        pygame.draw.rect(self.screen, self.PANEL_BG, legend_rect, border_radius=8)
        pygame.draw.rect(self.screen, self.AXIS_COLOR, legend_rect, 2, border_radius=8)
        
        # 🎯 SHOW CURRENT MODE AT THE TOP
        if self.path_mode:
            mode_text = self.bold_font.render("🔍 PATH MODE ACTIVE", True, (100, 255, 100))
        else:
            mode_text = self.bold_font.render("FUNDAMENTAL PATTERNS", True, (255, 255, 200))
        self.screen.blit(mode_text, (legend_x, legend_y))
        
        y_offset = legend_y + 35
        
        if self.path_mode:
            # 🆕 PATH MODE LEGEND WITH ICONS
            path_header = self.small_font.render("PATH DIRECTION ICONS:", True, (255, 255, 200))
            self.screen.blit(path_header, (legend_x, y_offset))
            y_offset += 25
            
            # 🆕 ICON EXPLANATIONS
            direction_explanations = [
                ((220, 100, 100), "🔼", "Up", "Move to parent element"),
                ((100, 220, 100), "🔽", "Down", "Move to child element"),  
                ((100, 100, 220), "◀️", "Left", "Move to previous sibling"),
                ((220, 220, 100), "▶️", "Right", "Move to next sibling"),
            ]
            
            for color, icon, title, description in direction_explanations:
                # Draw colored icon
                icon_font = pygame.font.Font(None, 24)
                icon_surface = icon_font.render(icon, True, color)
                self.screen.blit(icon_surface, (legend_x + 5, y_offset))
                
                title_text = self.small_font.render(f"{title}", True, self.TEXT_COLOR)
                desc_text = self.small_font.render(description, True, (180, 180, 220))
                
                self.screen.blit(title_text, (legend_x + 35, y_offset))
                self.screen.blit(desc_text, (legend_x + 35, y_offset + 12))
                y_offset += 30
            
            y_offset += 15
            
            # 🆕 ADD PETERBOT IMPORT INFO - FIXED: Check if analysis_info exists
            if hasattr(self, 'peterbot_analysis_info') and self.peterbot_analysis_info:
                analysis_info = self.peterbot_analysis_info
                import_header = self.small_font.render("PETERBOT IMPORT DATA:", True, (100, 255, 150))
                self.screen.blit(import_header, (legend_x, y_offset))
                y_offset += 20
                
                # 🎯 SAFE ACCESS: Use .get() with defaults
                import_lines = [
                    f"Changes: {analysis_info.get('changed_count', 0)}",
                    f"Paths: {analysis_info.get('path_count', 0)}",
                    f"Type: {analysis_info.get('type', 'unknown')}"
                ]
                
                for line in import_lines:
                    info_surface = self.small_font.render(line, True, (200, 255, 200))
                    self.screen.blit(info_surface, (legend_x + 10, y_offset))
                    y_offset += 18
                
                y_offset += 10
            else:
                # 🎯 Show basic path info if analysis_info is missing
                if hasattr(self, 'peterbot_paths') and self.peterbot_paths:
                    import_header = self.small_font.render("PATH DATA:", True, (100, 255, 150))
                    self.screen.blit(import_header, (legend_x, y_offset))
                    y_offset += 20
                    
                    import_lines = [
                        f"Paths: {len(self.peterbot_paths)}",
                        f"Status: Imported"
                    ]
                    
                    for line in import_lines:
                        info_surface = self.small_font.render(line, True, (200, 255, 200))
                        self.screen.blit(info_surface, (legend_x + 10, y_offset))
                        y_offset += 18
                    
                    y_offset += 10
            
            # Path mode instructions
            instructions = [
                "PATH MODE FEATURES:",
                "• Elements dimmed for focus",
                "• Icons show navigation direction", 
                "• Colors indicate DOM movement",
                "• Press P to exit path mode"
            ]
            
            for instruction in instructions:
                inst_text = self.small_font.render(instruction, True, (200, 200, 255))
                self.screen.blit(inst_text, (legend_x, y_offset))
                y_offset += 20
                        
        else:
            # 🎯 FUNDAMENTAL PATTERN LEGEND WITH GLOW EFFECTS
            state_header = self.small_font.render("FUNDAMENTAL PATTERNS:", True, (255, 255, 200))
            self.screen.blit(state_header, (legend_x, y_offset))
            y_offset += 25
            
            # 🎯 FUNDAMENTAL PATTERN EXPLANATIONS
            pattern_explanations = [
                ((255, 180, 50), "ACTION ELEMENT", "Buttons, links, triggers"),
                ((80, 180, 255), "DATA INPUT", "Inputs, textareas, selects"), 
                ((100, 220, 220), "CONTEXT ELEMENT", "Labels, help text, context"),
                ((200, 100, 255), "STATE INDICATOR", "Progress, validation, states"),
            ]
            
            for color, title, description in pattern_explanations:
                # Draw pulsing glow effect
                pulse = 1.5 + math.sin(pygame.time.get_ticks() * 0.01) * 1.0
                for i in range(2):
                    glow_size = 5 + pulse + (i * 1)
                    alpha = 80 - (i * 30)
                    glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    r, g, b = color
                    rgba_color = (r, g, b, alpha)
                    pygame.draw.circle(glow_surface, rgba_color, (glow_size, glow_size), glow_size)
                    self.screen.blit(glow_surface, (legend_x + 8 - glow_size, y_offset + 8 - glow_size))
                
                # Draw center circle
                pygame.draw.circle(self.screen, color, (legend_x + 8, y_offset + 8), 5)
                pygame.draw.circle(self.screen, (255, 255, 255), (legend_x + 8, y_offset + 8), 5, 1)
                
                title_text = self.small_font.render(title, True, self.TEXT_COLOR)
                desc_text = self.small_font.render(description, True, (180, 180, 220))
                
                self.screen.blit(title_text, (legend_x + 25, y_offset))
                self.screen.blit(desc_text, (legend_x + 25, y_offset + 12))
                y_offset += 30
            
            y_offset += 15
            
            # 🎯 SHOW PATH MODE AVAILABILITY
            if hasattr(self, 'peterbot_paths') and self.peterbot_paths:
                path_notice = self.small_font.render("💡 Paths available! Press P for Path Mode", True, (100, 255, 100))
                self.screen.blit(path_notice, (legend_x, y_offset))
                y_offset += 25
            
            # Connection color grid (only in normal mode)
            grid_header = self.small_font.render("CONNECTION COLOR MAP", True, (255, 255, 200))
            self.screen.blit(grid_header, (legend_x, y_offset))
            y_offset += 25

            depth_labels = ["0-2", "3-5", "6-8", "9-11", "12+"]
            for i, label in enumerate(depth_labels):
                label_text = self.small_font.render(label, True, self.TEXT_COLOR)
                self.screen.blit(label_text, (legend_x + 65 + (i * 38), y_offset))

            y_offset += 20

            sibling_ranges = ["1-9", "10-18", "19-27", "28-36", "36+"]
            color_grid = [
                [(180, 100, 255), (160, 90, 235), (140, 80, 215), (120, 70, 195), (100, 60, 175)],
                [(160, 140, 240), (140, 130, 220), (120, 120, 200), (100, 110, 180), (80, 100, 160)],
                [(140, 180, 220), (120, 170, 200), (100, 160, 180), (80, 150, 160), (60, 140, 140)],
                [(120, 220, 200), (100, 210, 180), (80, 200, 160), (60, 190, 140), (40, 180, 120)],
                [(100, 255, 180), (80, 240, 160), (60, 225, 140), (40, 210, 120), (20, 195, 100)]
            ]

            for row, (sibling_label, colors) in enumerate(zip(sibling_ranges, color_grid)):
                sibling_text = self.small_font.render(sibling_label, True, self.TEXT_COLOR)
                self.screen.blit(sibling_text, (legend_x + 15, y_offset + (row * 22)))
                
                for col, color in enumerate(colors):
                    cell_rect = pygame.Rect(legend_x + 65 + (col * 38), y_offset + (row * 22), 32, 16)
                    pygame.draw.rect(self.screen, color, cell_rect)
                    pygame.draw.rect(self.screen, self.AXIS_COLOR, cell_rect, 1)

            y_offset += 120

            note_font = pygame.font.Font(None, 16)
            note_text = note_font.render("* Black = Extreme cases (60+ siblings or 20+ depth)", True, (150, 150, 150))
            self.screen.blit(note_text, (legend_x, y_offset))
            
    # KEEP ALL OTHER VISUALIZER METHODS UNCHANGED
    def _draw_peterbot_paths(self, center_x, center_y):
        """FIXED: DRAW PATHS WITH DIRECTION-CODED COLORS - WITH SAFETY CHECKS"""
        if not hasattr(self, 'peterbot_paths') or not self.peterbot_paths:
            return
        
        for i, path in enumerate(self.peterbot_paths):
            if len(path) < 2:
                continue
                
            # Draw connecting lines between path points with direction colors
            for j in range(len(path) - 1):
                start_pos = self._branch_to_screen(path[j], center_x, center_y)
                end_pos = self._branch_to_screen(path[j+1], center_x, center_y)
                
                # 🎯 FIX: Only draw if both positions are valid
                if start_pos and end_pos:
                    # Determine direction and get appropriate color
                    direction = self._get_path_direction(path[j], path[j+1])
                    path_color = self.path_direction_colors.get(direction, (200, 200, 200))
                    
                    # Thick, pulsing line for paths
                    pulse = 2 + math.sin(pygame.time.get_ticks() * 0.01 + i) * 1.5
                    line_width = int(8 + pulse)
                    
                    pygame.draw.line(self.screen, path_color, start_pos, end_pos, line_width)
                    
                    # Draw animated direction arrows
                    self._draw_path_arrow(start_pos, end_pos, path_color, direction)
                    
                    # Draw path nodes with highlights
                    for coord_pos in [start_pos, end_pos]:
                        pygame.draw.circle(self.screen, path_color, coord_pos, 10)
                        pygame.draw.circle(self.screen, (255, 255, 255), coord_pos, 10, 3)

    def _get_path_direction(self, from_coord, to_coord):
        """FIXED: DETERMINE PATH DIRECTION BETWEEN COORDINATES - HANDLES NESTED TUPLES"""
        if not from_coord or not to_coord:
            return 'unknown'
        
        def get_final_index(coord):
            """Extract final index from potentially nested coordinate"""
            if isinstance(coord, (tuple, list)) and coord:
                return get_final_index(coord[-1])
            return coord if coord is not None else 0
        
        from_len = len(from_coord) if from_coord else 0
        to_len = len(to_coord) if to_coord else 0
        
        if from_len > to_len:
            return 'up'    # Moving to parent (shorter coordinate)
        elif from_len < to_len:
            return 'down'  # Moving to child (longer coordinate)
        else:
            # Same depth - check sibling movement using final indices
            from_final = get_final_index(from_coord)
            to_final = get_final_index(to_coord)
            
            if from_final < to_final:
                return 'right'  # Moving to next sibling
            else:
                return 'left'   # Moving to previous sibling

    def _draw_path_arrow(self, start_pos, end_pos, color, direction):
        """DRAW DIRECTION ICONS INSTEAD OF ARROWS"""
        # Calculate midpoint
        mid_x = (start_pos[0] + end_pos[0]) // 2
        mid_y = (start_pos[1] + end_pos[1]) // 2
        
        # 🆕 USE ICONS INSTEAD OF ARROWS
        icons = {
            'up': '🔼',     # Triangle up
            'down': '🔽',   # Triangle down  
            'left': '◀️',   # Triangle left
            'right': '▶️',  # Triangle right
        }
        
        icon = icons.get(direction, '🔘')  # Default circle
        
        # Draw icon with pulsing effect
        pulse = 1 + math.sin(pygame.time.get_ticks() * 0.02) * 0.3
        icon_size = int(20 + pulse)
        
        # Create icon surface
        icon_font = pygame.font.Font(None, icon_size)
        icon_surface = icon_font.render(icon, True, color)
        icon_rect = icon_surface.get_rect(center=(int(mid_x), int(mid_y)))
        
        # Add subtle glow behind icon
        glow_surface = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*color, 80), (icon_size//2, icon_size//2), icon_size//2)
        self.screen.blit(glow_surface, (icon_rect.centerx - icon_size//2, icon_rect.centery - icon_size//2))
        
        self.screen.blit(icon_surface, icon_rect)

    def _draw_structural_grid(self, center_x, center_y):
        """DRAW THE GUIDING GRID OF REALITY"""
        for i in range(-15, 16):
            x = center_x + i * self.cell_size * self.zoom
            pygame.draw.line(self.screen, self.GRID_COLOR, 
                        (x, 80), (x, self.screen_height - 120), 1)
        
        for i in range(25):
            y = center_y + i * self.cell_size * self.zoom
            pygame.draw.line(self.screen, self.GRID_COLOR,
                        (80, y), (self.screen_width - 80, y), 1)
        
        pygame.draw.line(self.screen, (100, 255, 100),
                    (center_x, 80), (center_x, self.screen_height - 120), 2)
        
        pygame.draw.line(self.screen, (100, 150, 255),
                    (80, center_y), (self.screen_width - 80, center_y), 2)
        
        depth_label = self.font.render("DOM Depth", True, (100, 150, 255))
        sibling_label = self.font.render("Sibling Position", True, (100, 255, 100))
        self.screen.blit(depth_label, (center_x - 200, center_y - 40))
        self.screen.blit(sibling_label, (center_x + 50, center_y + 20 * self.cell_size * self.zoom))
        
    def _branch_to_screen(self, branch_tuple, center_x, center_y):
        """FIXED: TRANSFORM MATHEMATICAL COORDINATES TO VISIBLE SPACE - HANDLES NESTED TUPLES"""
        if not branch_tuple:
            return None
            
        depth = len(branch_tuple)
        
        # 🎯 CRITICAL FIX: Extract the LAST integer value from potentially nested coordinates
        def extract_final_index(coord):
            """Recursively extract the final integer index from nested tuples"""
            if isinstance(coord, (tuple, list)):
                if coord:  # If not empty
                    return extract_final_index(coord[-1])
                else:
                    return 0
            else:
                return int(coord) if coord is not None else 0
        
        sibling_index = extract_final_index(branch_tuple)
        
        # 🚨 SAFETY: Ensure we have valid integers
        depth = int(depth) if depth is not None else 0
        sibling_index = int(sibling_index) if sibling_index is not None else 0
        
        x = center_x + int(sibling_index * self.cell_size * self.zoom)
        y = center_y + int(depth * self.cell_size * self.zoom)
        
        if (50 <= x <= self.screen_width - 50 and 100 <= y <= self.screen_height - 150):
            return (int(x), int(y))
        return None

    def _draw_dom_connections(self, snapshot: DOMSnapshot, center_x, center_y):
        """DRAW COLOR-CODED CONNECTORS - EXCLUDE SHAVED ELEMENTS AND THEIR CONNECTIONS"""
        for branch_tuple, node in snapshot.branch_coordinates.items():
            # 🎯 SKIP SHAVED ELEMENTS AND THEIR CONNECTIONS
            if branch_tuple in self.shaved_elements:
                continue  # Don't draw connections from shaved elements
                
            if len(branch_tuple) > 0:
                parent_branch = branch_tuple[:-1]
                
                # 🎯 SKIP IF PARENT IS SHAVED
                if parent_branch in self.shaved_elements:
                    continue  # Don't draw connections to shaved parent
                
                if parent_branch in snapshot.branch_coordinates:
                    parent_pos = self._branch_to_screen(parent_branch, center_x, center_y)
                    child_pos = self._branch_to_screen(branch_tuple, center_x, center_y)
                    
                    if parent_pos and child_pos:
                        connection_color = self._get_branching_color(parent_branch, branch_tuple, snapshot)
                        pygame.draw.line(self.screen, connection_color, parent_pos, child_pos, 2)

    def _get_branching_color(self, parent_branch, child_branch, snapshot):
        """GET COLOR BASED ON 5x5 COSMIC GRID - DISCRETE COLORS"""
        parent_children = self._get_child_count(parent_branch, snapshot)
        child_depth = len(child_branch)
        
        if parent_children <= 9:
            sibling_bin = 0
        elif parent_children <= 18:
            sibling_bin = 1  
        elif parent_children <= 27:
            sibling_bin = 2
        elif parent_children <= 36:
            sibling_bin = 3
        else:
            sibling_bin = 4
        
        if child_depth <= 2:
            depth_bin = 0
        elif child_depth <= 5:
            depth_bin = 1
        elif child_depth <= 8:
            depth_bin = 2
        elif child_depth <= 11:
            depth_bin = 3
        else:
            depth_bin = 4
        
        color_grid = [
            [(180, 100, 255), (160, 90, 235), (140, 80, 215), (120, 70, 195), (100, 60, 175)],
            [(160, 140, 240), (140, 130, 220), (120, 120, 200), (100, 110, 180), (80, 100, 160)],
            [(140, 180, 220), (120, 170, 200), (100, 160, 180), (80, 150, 160), (60, 140, 140)],
            [(120, 220, 200), (100, 210, 180), (80, 200, 160), (60, 190, 140), (40, 180, 120)],
            [(100, 255, 180), (80, 240, 160), (60, 225, 140), (40, 210, 120), (20, 195, 100)]
        ]
        
        if parent_children > 60 or child_depth > 20:
            return (0, 0, 0)
        
        return color_grid[sibling_bin][depth_bin]

    def _get_child_count(self, parent_branch, snapshot):
        """COUNT CHILDREN FOR BRANCHING PATTERN ANALYSIS"""
        if parent_branch in snapshot.branch_coordinates:
            children = []
            child_index = 0
            while True:
                child_branch = parent_branch + (child_index,)
                if child_branch in snapshot.branch_coordinates:
                    children.append(child_branch)
                    child_index += 1
                else:
                    break
            return len(children)
        return 0

    def _draw_path_mode_overlay(self):
        """DRAW PATH-FOCUSED OVERLAY - ONLY IF PATHS EXIST"""
        if not self.path_mode or not hasattr(self, 'peterbot_paths') or not self.peterbot_paths:
            return
            
        # Create semi-transparent dark overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Dark semi-transparent
        
        # Cut out holes around path elements to highlight them
        for path in self.peterbot_paths:
            for coord in path:
                screen_pos = self._branch_to_screen(coord, 
                                                self.screen_width//2 + self.pan_x,
                                                150 + self.pan_y)
                if screen_pos:
                    # Cut larger hole around path elements
                    pygame.draw.circle(overlay, (0, 0, 0, 0), screen_pos, 60)
        
        self.screen.blit(overlay, (0, 0))
        
        # Draw path-focused header
        mode_text = self.title_font.render("PATH MODE - Interaction Path Analysis", True, (255, 255, 100))
        self.screen.blit(mode_text, (self.screen_width//2 - 250, 20))
        
        path_count = len(self.peterbot_paths)
        help_text = self.small_font.render(f"Showing {path_count} paths | Press P for normal view | Colors show DOM navigation direction", True, (200, 200, 255))
        self.screen.blit(help_text, (self.screen_width//2 - 350, 60))

    def update_hover(self, mouse_pos, current_snapshot: DOMSnapshot):
        """UPDATE WHAT ELEMENT IS UNDER THE LIGHT OF UNDERSTANDING"""
        self.hovered_element = None
        
        if not current_snapshot:
            return
            
        center_x = self.screen_width // 2 + self.pan_x
        center_y = 150 + self.pan_y
        
        closest_dist = 30
        closest_element = None
        
        for branch_tuple, node in current_snapshot.branch_coordinates.items():
            screen_pos = self._branch_to_screen(branch_tuple, center_x, center_y)
            if screen_pos:
                dist = math.sqrt((screen_pos[0] - mouse_pos[0])**2 + 
                               (screen_pos[1] - mouse_pos[1])**2)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_element = branch_tuple
        
        self.hovered_element = closest_element
   
    def _toggle_highlight_mode(self):
        """TOGGLE HIGHLIGHT MODE FOR SHAVING ELEMENTS"""
        self.highlight_mode = not self.highlight_mode
        if self.highlight_mode:
            print("\n" + "="*60)
            print("🔴 HIGHLIGHT MODE ACTIVATED")
            print("="*60)
            print("📋 INSTRUCTIONS:")
            print("1. Drag mouse to draw red selection box")
            print("2. Elements inside the box will be marked for removal")
            print("3. Press X again to confirm and shave selected elements")
            print("4. Press ESC to cancel without shaving")
            print("\n💡 Shaved elements will:")
            print("   • Disappear from visualization")
            print("   • Have their connections removed")
            print("   • Be excluded from PeterBot analysis")
        else:
            if self.highlight_rect_start and self.highlight_rect_end:
                self._shave_selected_elements()
            else:
                print("✅ Highlight mode deactivated - no elements selected")
            self.highlight_rect_start = None
            self.highlight_rect_end = None

    def _shave_elements_in_rectangle(self, start_pos, end_pos):
        """SHAVE ALL ELEMENTS WITHIN SELECTION RECTANGLE"""
        # Calculate rectangle boundaries
        x1, y1 = start_pos
        x2, y2 = end_pos
        rect_x = min(x1, x2)
        rect_y = min(y1, y2)
        rect_width = abs(x2 - x1)
        rect_height = abs(y2 - y1)
        
        highlight_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
        
        # Find elements within the highlighted area
        shaved_count = 0
        if hasattr(self, 'app') and hasattr(self.app, 'current_snapshot'):
            center_x = self.screen_width // 2 + self.pan_x
            center_y = 150 + self.pan_y
            
            for branch_tuple, node in self.app.current_snapshot.branch_coordinates.items():
                screen_pos = self._branch_to_screen(branch_tuple, center_x, center_y)
                if screen_pos and highlight_rect.collidepoint(screen_pos):
                    if branch_tuple not in self.shaved_elements:
                        self.shaved_elements.add(branch_tuple)
                        shaved_count += 1
                        # Also remove from PeterBot analysis if it exists
                        if hasattr(self, 'peterbot_highlights'):
                            self.peterbot_highlights.discard(branch_tuple)
        
        print(f"\n✅ SHAVED {shaved_count} ELEMENTS")
        print(f"📊 Total shaved elements: {len(self.shaved_elements)}")
        print("💡 These elements are now hidden from visualization and PeterBot analysis")

    def _draw_highlight_rectangle(self):
        """DRAW TRANSPARENT RED HIGHLIGHT RECTANGLE WITH LIVE FEEDBACK"""
        if not self.highlight_mode or not self.highlight_rect_start:
            return
        
        current_pos = pygame.mouse.get_pos()
        
        # Calculate rectangle
        x1, y1 = self.highlight_rect_start
        x2, y2 = current_pos
        rect_x = min(x1, x2)
        rect_y = min(y1, y2)
        rect_width = abs(x2 - x1)
        rect_height = abs(y2 - y1)
        
        # Draw semi-transparent red rectangle
        highlight_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        highlight_surface.fill(self.highlight_color)
        self.screen.blit(highlight_surface, (rect_x, rect_y))
        
        # Draw outline
        pygame.draw.rect(self.screen, (255, 50, 50), 
                        (rect_x, rect_y, rect_width, rect_height), 2)
        
        # Draw instructions based on mode
        if rect_width < 10 and rect_height < 10:  # Single click mode
            info_text = "Click to shave element | Release mouse to confirm"
            info_color = (255, 150, 150)
        else:  # Rectangle drag mode
            info_text = "Drag to shave multiple elements | Release mouse to confirm"
            info_color = (255, 100, 100)
        
        info_surface = self.small_font.render(info_text, True, info_color)
        self.screen.blit(info_surface, (rect_x, rect_y - 25))
        
        # Draw live element count in area
        if hasattr(self, 'app') and hasattr(self.app, 'current_snapshot'):
            center_x = self.screen_width // 2 + self.pan_x
            center_y = 150 + self.pan_y
            elements_in_area = 0
            
            for branch_tuple, node in self.app.current_snapshot.branch_coordinates.items():
                screen_pos = self._branch_to_screen(branch_tuple, center_x, center_y)
                if screen_pos and pygame.Rect(rect_x, rect_y, rect_width, rect_height).collidepoint(screen_pos):
                    elements_in_area += 1
            
            count_text = f"Elements in area: {elements_in_area}"
            count_surface = self.small_font.render(count_text, True, (255, 150, 150))
            self.screen.blit(count_surface, (rect_x, rect_y + rect_height + 5))

    def _start_highlighting(self, pos):
        """START DRAWING HIGHLIGHT RECTANGLE"""
        if self.highlight_mode:
            self.highlight_rect_start = pos
            print("🎯 Started selection - drag to define area")

    def _update_highlighting(self, pos):
        """UPDATE HIGHLIGHT RECTANGLE SIZE"""
        if self.highlight_mode and self.highlight_rect_start:
            self.highlight_rect_end = pos
   
    def _draw_shaving_info(self):
        """DRAW SHAVING INFO AT TOP CENTER - ONLY ONCE AT TOP CENTER"""
        if not self.shaved_elements:
            return
        
        # Calculate statistics
        total_elements = 0
        if hasattr(self, 'app') and hasattr(self.app, 'current_snapshot') and self.app.current_snapshot:
            total_elements = len(self.app.current_snapshot.branch_coordinates)
        
        shaved_count = len(self.shaved_elements)
        visible_count = total_elements - shaved_count
        
        # Create shaving info text
        shaving_text = f"🔪 SHAVED: {shaved_count} elements hidden"
        if total_elements > 0:
            shaving_text += f" | 📊 Visible: {visible_count} elements"
        
        # Draw at top center
        center_x = self.screen_width // 2
        shaving_surface = self.font.render(shaving_text, True, (255, 150, 150))
        text_rect = shaving_surface.get_rect(center=(center_x, 75))
        
        # Draw background
        bg_rect = text_rect.inflate(40, 15)
        pygame.draw.rect(self.screen, (40, 15, 15), bg_rect, border_radius=8)
        pygame.draw.rect(self.screen, (200, 50, 50), bg_rect, 2, border_radius=8)
        
        # Draw text
        self.screen.blit(shaving_surface, text_rect)
        
        # If in highlight mode, show additional instructions
        if self.highlight_mode:
            highlight_text = "Drag to select elements to shave | Press X to confirm"
            highlight_surface = self.small_font.render(highlight_text, True, (255, 200, 200))
            highlight_rect = highlight_surface.get_rect(center=(center_x, 100))
            self.screen.blit(highlight_surface, highlight_rect)

    def _toggle_recording_mode(self):
        """TOGGLE PETERBOT RECORDING MODE - SHOW TERMINAL INSTRUCTIONS"""
        self.recording_mode = not self.recording_mode
        
        if self.recording_mode:
            print("\n" + "="*60)
            print("🎬 PETERBOT RECORDING MODE ACTIVATED")
            print("="*60)
            
            # Create priori file for PeterBot
            priori_path = self._create_priori_file()
            
            if priori_path:
                # Extract timestamp from filename
                timestamp = priori_path.split('_')[-1].replace('.json', '')
                
                print("\n📋 TERMINAL INSTRUCTIONS:")
                print("1. OPEN A NEW TERMINAL WINDOW/TAB")
                print("2. RUN THIS COMMAND:")
                print(f"   python3 PeterBot.py --priori venger_priori_{timestamp}.json")
                print("\n3. Return here and wait for PeterBot to complete")
                print("4. Type 'import' when PeterBot finishes to load results")
                print("\n🔴 RED OVERLAY: Recording mode active - PyGame window remains open")
                print("   Perform interactions in the browser, then check PeterBot terminal")
                
            else:
                print("❌ Failed to create priori file - recording mode disabled")
                self.recording_mode = False
                
        else:
            print("⏹️ PETERBOT RECORDING MODE DEACTIVATED")
    
    def handle_events(self):
        """HANDLE KEY EVENTS WITH SMOOTH MOVEMENT - FIXED"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.highlight_mode:
                        self.highlight_mode = False
                        self.highlight_rect_start = None
                        self.highlight_rect_end = None
                        print("❌ Highlight mode cancelled")
                        return None
                    else:
                        return 'quit_and_reattach'
                elif event.key == pygame.K_c:
                    if self.highlight_mode:
                        print("⚠️ Exit shaving mode first (Press X)")
                        return None
                    return 'capture'
                elif event.key == pygame.K_p:  # PATH MODE TOGGLE
                    if self.highlight_mode:
                        print("⚠️ Exit shaving mode first (Press X)")
                        return None
                    self._toggle_path_mode()
                    return None
                elif event.key == pygame.K_t:
                    if self.highlight_mode:
                        print("⚠️ Exit shaving mode first (Press X)")
                        return None
                    self.show_path_mode = not self.show_path_mode
                    return None
                elif event.key == pygame.K_x:  # TOGGLE SHAVING MODE
                    self._toggle_highlight_mode()
                    return None
                elif event.key == pygame.K_m:
                    if self.highlight_mode:
                        print("⚠️ Exit shaving mode first (Press X)")
                        return None
                    
                    # 🚨 CRITICAL FIX: Handle 'M' key for both offline and online modes
                    if hasattr(self, 'app') and self.app:
                        # Check if we need to launch browser (offline mode)
                        if hasattr(self.app, 'offline_mode') and self.app.offline_mode:
                            print("\n" + "="*60)
                            print("🚀 LAUNCHING BROWSER FROM OFFLINE MODE")
                            print("="*60)
                            
                            # Try to get URL from current page
                            url = ""
                            if hasattr(self.app, 'database') and self.app.database.is_active():
                                current_page = self.app.database.get_current_page()
                                if current_page:
                                    url = current_page.get('url', '')
                            
                            if url:
                                print(f"🌐 Loading page URL: {url[:80]}...")
                            else:
                                print("⚠️ No URL found in current page")
                                url = input("Enter URL to load: ").strip()
                                if not url:
                                    print("❌ No URL provided - cannot launch browser")
                                    return None
                            
                            # Launch browser
                            print("🚀 Starting browser...")
                            self.app.driver = setup_browser(9223)
                            if not self.app.driver:
                                print("❌ Failed to launch browser")
                                return None
                            
                            # Navigate to URL
                            try:
                                self.app.driver.get(url)
                                time.sleep(3)
                                self.app.current_url = self.app.driver.current_url
                                self.app.offline_mode = False
                                print(f"✅ Browser launched: {self.app.current_url[:80]}...")
                                
                                # Initialize scanner
                                if not hasattr(self.app, 'scanner') or not self.app.scanner:
                                    self.app.scanner = DOMScanner(self.app.driver)
                                
                                # Now trigger recording mode
                                return 'toggle_recording'
                                
                            except Exception as e:
                                print(f"❌ Failed to navigate to URL: {e}")
                                return None
                        else:
                            # Already in online mode, just trigger recording
                            return 'toggle_recording'
                    else:
                        print("❌ No app reference - cannot start recording")
                    return None
                elif event.key == pygame.K_r:
                    if self.highlight_mode:
                        print("⚠️ Exit shaving mode first (Press X)")
                        return None
                    self.pan_x, self.pan_y = 0, 0
                    self.zoom = 1.0
                    return None
                elif event.key == pygame.K_RIGHT:
                    if self.highlight_mode:
                        print("⚠️ Exit shaving mode first (Press X)")
                        return None
                    return 'next_page'
                elif event.key == pygame.K_LEFT:
                    if self.highlight_mode:
                        print("⚠️ Exit shaving mode first (Press X)")
                        return None
                    return 'prev_page'
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self._zoom_at_position(pygame.mouse.get_pos(), zoom_in=True)
                    return None
                elif event.key == pygame.K_MINUS:
                    self._zoom_at_position(pygame.mouse.get_pos(), zoom_in=False)
                    return None
                elif event.key == pygame.K_HOME:
                    self.pan_x, self.pan_y = 0, 0
                    self.zoom = 1.0
                    print("🏠 View reset to center (zoom=1.0)")
                    return None
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.highlight_mode:
                        self.highlight_rect_start = event.pos
                        print(f"🎯 Selection started at {event.pos}")
                elif event.button == 4:  # Scroll up - Zoom IN
                    self._zoom_at_position(event.pos, zoom_in=True)
                elif event.button == 5:  # Scroll down - Zoom OUT
                    self._zoom_at_position(event.pos, zoom_in=False)
                    
            elif event.type == pygame.MOUSEBUTTONUP and self.highlight_mode:
                if event.button == 1:  # Left mouse button released
                    if self.highlight_rect_start:
                        print(f"🎯 Selection ended at {event.pos}")
                        self._finish_shaving(event.pos)
            elif event.type == pygame.MOUSEMOTION and self.highlight_mode:
                if self.highlight_rect_start and pygame.mouse.get_pressed()[0]:
                    self.highlight_rect_end = event.pos
        
        # Smooth movement handling (unchanged)
        keys = pygame.key.get_pressed()
        
        if not self.highlight_mode:
            base_speed = 20.0
            move_speed = base_speed / max(0.1, self.zoom)
            
            acceleration = 1.0
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                acceleration = 2.5
            
            final_speed = move_speed * acceleration
            
            if keys[pygame.K_w]:
                self.pan_y += final_speed
            if keys[pygame.K_s]:
                self.pan_y -= final_speed
            if keys[pygame.K_d]:
                self.pan_x -= final_speed
            if keys[pygame.K_a]:
                self.pan_x += final_speed
            
            if keys[pygame.K_q]:
                self._zoom_at_position(pygame.mouse.get_pos(), zoom_in=False)
            if keys[pygame.K_e]:
                self._zoom_at_position(pygame.mouse.get_pos(), zoom_in=True)
            
            if keys[pygame.K_LEFTBRACKET]:
                self._zoom_at_position(pygame.mouse.get_pos(), zoom_in=False)
            if keys[pygame.K_RIGHTBRACKET]:
                self._zoom_at_position(pygame.mouse.get_pos(), zoom_in=True)
                        
        return None
        
    
        
    def _create_priori_file(self):
        """FIXED: CREATE ENHANCED PRIORI WITH ALL PETERBOT DATA - EXCLUDE SHAVED ELEMENTS"""
        try:
            if not hasattr(self, 'app') or not self.app.current_snapshot:
                print("❌ No current snapshot available")
                return None
                
            snapshot = self.app.current_snapshot
            timestamp = int(time.time())
            
            # Count non-shaved elements
            total_elements = len(snapshot.branch_coordinates)
            shaved_count = len(self.shaved_elements) if hasattr(self, 'shaved_elements') else 0
            visible_count = total_elements - shaved_count
            
            priori_data = {
                'url': self.app.driver.current_url if self.app.driver else 'unknown',
                'timestamp': timestamp,
                'total_coordinates': total_elements,
                'visible_coordinates': visible_count,
                'shaved_coordinates': shaved_count,
                'coordinate_space': {},
                'metadata': {
                    'source': 'venger_recording_mode',
                    'window_geometry': {
                        'screen_width': self.screen_width,
                        'screen_height': self.screen_height,
                        'cell_size': self.cell_size
                    },
                    'shaving_info': {
                        'shaved_count': shaved_count,
                        'visible_count': visible_count,
                        'shaving_active': shaved_count > 0
                    }
                }
            }
            
            # 🎯 FIXED: Export ALL data PeterBot expects, EXCLUDING SHAVED ELEMENTS
            for coord, node in snapshot.branch_coordinates.items():
                # 🚨 SKIP SHAVED ELEMENTS
                if hasattr(self, 'shaved_elements') and coord in self.shaved_elements:
                    continue
                
                # 🎯 USE PETERBOT'S EXPECTED FIELD NAMES
                priori_data['coordinate_space'][str(coord)] = {
                    'type': node.type,
                    'structural_role': node.structural_role,
                    'hash': node.current_hash,
                    'text': node.text,
                    'classes': node.classes,
                    'depth': node.depth,
                    'is_interactive': node.is_interactive,
                    'pattern_roles': node.pattern_roles,
                }
            
            # Ensure TheDevengers directory exists
            devengers_path = "TheDevengers"
            os.makedirs(devengers_path, exist_ok=True)
            
            # Save enhanced priori file
            priori_filename = f"venger_priori_{timestamp}.json"
            priori_path = os.path.join(devengers_path, priori_filename)
            
            with open(priori_path, 'w') as f:
                json.dump(priori_data, f, indent=2)
            
            print(f"\n💾 ENHANCED Priori file created: {priori_path}")
            print(f"🔢 Total elements: {total_elements}")
            print(f"🔪 Shaved elements: {shaved_count} (excluded)")
            print(f"📤 Passing to PeterBot: {visible_count} elements")
            
            # 🎯 SHOW PETERBOT-READY DATA SUMMARY
            pattern_count = sum(1 for coord_data in priori_data['coordinate_space'].values()
                            if coord_data.get('pattern_roles'))
            interactive_count = sum(1 for coord_data in priori_data['coordinate_space'].values()
                                if coord_data.get('is_interactive'))
            
            print(f"🎯 Patterns: {pattern_count} elements with pattern roles")
            print(f"🖱️ Interactive: {interactive_count} elements marked for PeterBot targeting")
            print("✅ PeterBot integration data: READY (shaved elements filtered out)")
            
            return priori_path
                
        except Exception as e:
            print(f"❌ Failed to create enhanced priori file: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def get_filtered_coordinates(self):
        """GET COORDINATES FILTERED TO EXCLUDE SHAVED ELEMENTS"""
        if not self.current_snapshot:
            return {}
        
        filtered = {}
        shaved_count = 0
        
        for coord, node in self.current_snapshot.branch_coordinates.items():
            # Check if element is shaved
            if (hasattr(self, 'visualizer') and 
                hasattr(self.visualizer, 'shaved_elements') and 
                coord in self.visualizer.shaved_elements):
                shaved_count += 1
                continue
            
            filtered[coord] = node
        
        if shaved_count > 0:
            print(f"🔪 Filtered out {shaved_count} shaved elements")
        
        return filtered
        
    def _toggle_path_mode(self):
        """TOGGLE PATH-FOCUSED VIEW MODE WITH VALIDATION"""
        # Check if we have any paths (non-empty list)
        if not hasattr(self, 'peterbot_paths') or not self.peterbot_paths:
            print("❌ No path data available. Import PeterBot results first with 'import' command.")
            return
                
        self.path_mode = not self.path_mode
        if self.path_mode:
            print("🔍 PATH MODE: Focusing on interaction paths")
            print(f"   - Showing {len(self.peterbot_paths)} paths with direction colors")
            print("   - Press P to return to normal view")
        else:
            print("🌌 NORMAL MODE: Showing full DOM structure")

    def _shave_element_at_position(self, pos):
        """SHAVE SINGLE ELEMENT AT MOUSE POSITION"""
        if not hasattr(self, 'app') or not hasattr(self.app, 'current_snapshot') or not self.app.current_snapshot:
            print("❌ No current snapshot available")
            return
        
        center_x = self.screen_width // 2 + self.pan_x
        center_y = 150 + self.pan_y
        
        # Find closest element to click position
        closest_dist = 30
        closest_element = None
        
        for branch_tuple, node in self.app.current_snapshot.branch_coordinates.items():
            screen_pos = self._branch_to_screen(branch_tuple, center_x, center_y)
            if screen_pos:
                dist = math.sqrt((screen_pos[0] - pos[0])**2 + 
                            (screen_pos[1] - pos[1])**2)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_element = branch_tuple
        
        if closest_element:
            if closest_element not in self.shaved_elements:
                self.shaved_elements.add(closest_element)
                
                # Also remove from PeterBot highlights if they exist
                if hasattr(self, 'peterbot_highlights'):
                    self.peterbot_highlights.discard(closest_element)
                
                element_data = self.app.current_snapshot.branch_coordinates[closest_element]
                print(f"✅ Shaved single element: {closest_element}")
                print(f"   Type: {element_data.type}")
                print(f"   Text: {element_data.text[:30]}")
                print(f"   Total shaved: {len(self.shaved_elements)} elements")
            else:
                print(f"⚠️ Element {closest_element} already shaved")
        else:
            print("❌ No element found at click position")
            print(f"   Mouse position: {pos}")
            print(f"   Center offset: ({center_x}, {center_y})")

    def _immediately_delete_from_json(self, shaved_coords):
        """IMMEDIATELY delete shaved elements from current page's JSON file"""
        if not hasattr(self, 'app') or not self.app.database.is_active():
            return
        
        if not self.current_page_id:
            print("⚠️ No current page ID for JSON update")
            return
        
        # Find the JSON file for current page
        site_path = self.app.database.site_path
        page_files = [f for f in os.listdir(site_path) if f.startswith('page_') and f.endswith('.json')]
        
        for filename in page_files:
            filepath = os.path.join(site_path, filename)
            try:
                with open(filepath, 'r') as f:
                    page_data = json.load(f)
                
                # Check if this is our current page
                if page_data.get('page_name') == self.current_page_id:
                    # Convert shaved coords to string format
                    shaved_strs = set()
                    for coord in shaved_coords:
                        coord_str = str(coord).replace(' ', '')
                        clean_coord = coord_str.strip('()')
                        shaved_strs.add(clean_coord)
                        shaved_strs.add(f"({clean_coord})")
                    
                    # Filter out shaved elements
                    original_count = len(page_data.get('coordinate_space', {}))
                    new_space = {}
                    deleted_count = 0
                    
                    for coord_str, element_data in page_data.get('coordinate_space', {}).items():
                        clean_coord_str = coord_str.strip('()')
                        if (clean_coord_str in shaved_strs or 
                            coord_str in shaved_strs):
                            deleted_count += 1
                            continue
                        new_space[coord_str] = element_data
                    
                    if deleted_count > 0:
                        page_data['coordinate_space'] = new_space
                        page_data['total_elements'] = len(new_space)
                        
                        # Clean up PeterBot paths
                        if 'peterbot_paths' in page_data and page_data['peterbot_paths']:
                            new_paths = []
                            for path in page_data['peterbot_paths']:
                                path_has_shaved = False
                                for coord_str in path:
                                    clean_coord_str = coord_str.strip('()')
                                    if (clean_coord_str in shaved_strs or 
                                        coord_str in shaved_strs):
                                        path_has_shaved = True
                                        break
                                if not path_has_shaved:
                                    new_paths.append(path)
                            page_data['peterbot_paths'] = new_paths
                        
                        with open(filepath, 'w') as f:
                            json.dump(page_data, f, indent=2)
                        
                        print(f"💾 Updated {filename}: deleted {deleted_count} elements")
                        break
                    
            except Exception as e:
                print(f"❌ Failed to update {filename}: {e}")   

    def _finish_shaving(self, end_pos):
        """PERMANENTLY DELETE ELEMENTS FROM CURRENT PAGE WITH PAGE TRACKING"""
        if not self.highlight_mode or not self.highlight_rect_start:
            return
        
        # Check if this was a click or drag
        start_pos = self.highlight_rect_start
        distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
        
        elements_to_shave = []
        
        if distance < 10:  # Single click
            # Find element at click position
            center_x = self.screen_width // 2 + self.pan_x
            center_y = 150 + self.pan_y
            closest_element = None
            closest_dist = 30
            
            for branch_tuple, node in self.app.current_snapshot.branch_coordinates.items():
                screen_pos = self._branch_to_screen(branch_tuple, center_x, center_y)
                if screen_pos:
                    dist = math.sqrt((screen_pos[0] - end_pos[0])**2 + 
                                (screen_pos[1] - end_pos[1])**2)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_element = branch_tuple
            
            if closest_element:
                elements_to_shave.append(closest_element)
        else:  # Drag selection
            # Calculate rectangle
            x1, y1 = start_pos
            x2, y2 = end_pos
            rect_x = min(x1, x2)
            rect_y = min(y1, y2)
            rect_width = abs(x2 - x1)
            rect_height = abs(y2 - y1)
            
            highlight_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
            center_x = self.screen_width // 2 + self.pan_x
            center_y = 150 + self.pan_y
            
            for branch_tuple, node in self.app.current_snapshot.branch_coordinates.items():
                screen_pos = self._branch_to_screen(branch_tuple, center_x, center_y)
                if screen_pos and highlight_rect.collidepoint(screen_pos):
                    elements_to_shave.append(branch_tuple)
        
        # 🚨 **PERMANENTLY DELETE ELEMENTS FROM THIS PAGE**
        if elements_to_shave and hasattr(self.app, 'current_snapshot'):
            for branch_tuple in elements_to_shave:
                # 1. DELETE FROM CURRENT SNAPSHOT (main data structure)
                if branch_tuple in self.app.current_snapshot.branch_coordinates:
                    del self.app.current_snapshot.branch_coordinates[branch_tuple]
                
                # 2. ADD TO SHAVED SET
                self.shaved_elements.add(branch_tuple)
                
                # 🚨 3. TRACK PER PAGE FOR PERSISTENCE
                if hasattr(self, 'current_page_id') and self.current_page_id:
                    if not hasattr(self, 'page_shaved_map'):
                        self.page_shaved_map = {}
                    if self.current_page_id not in self.page_shaved_map:
                        self.page_shaved_map[self.current_page_id] = set()
                    self.page_shaved_map[self.current_page_id].add(branch_tuple)
                
                # 4. REMOVE FROM PETERBOT PATHS
                if hasattr(self, 'peterbot_paths'):
                    new_paths = []
                    for path in self.peterbot_paths:
                        if branch_tuple not in path:
                            new_paths.append(path)
                    self.peterbot_paths = new_paths
                
                # 5. REMOVE FROM PETERBOT HIGHLIGHTS
                if hasattr(self, 'peterbot_highlights'):
                    self.peterbot_highlights.discard(branch_tuple)
            
            print(f"🔥 PERMANENTLY DELETED {len(elements_to_shave)} ELEMENTS")
            print(f"📊 Remaining elements: {len(self.app.current_snapshot.branch_coordinates)}")
            
            # 🚨 6. IMMEDIATELY UPDATE JSON FILE FOR THIS PAGE
            self._immediately_delete_from_json(elements_to_shave)
        
        # Reset
        self.highlight_rect_start = None
        self.highlight_rect_end = None
        
    def _shave_selected_elements(self):
        """PERMANENTLY DELETE ELEMENTS FROM CURRENT PAGE BASED ON SELECTION"""
        if not self.highlight_rect_start or not self.highlight_rect_end:
            return
        
        # Calculate rectangle
        x1, y1 = self.highlight_rect_start
        x2, y2 = self.highlight_rect_end
        rect_x = min(x1, x2)
        rect_y = min(y1, y2)
        rect_width = abs(x2 - x1)
        rect_height = abs(y2 - y1)
        
        highlight_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
        
        # Find elements within the highlighted area
        elements_to_shave = []
        if hasattr(self, 'app') and hasattr(self.app, 'current_snapshot'):
            center_x = self.screen_width // 2 + self.pan_x
            center_y = 150 + self.pan_y
            
            for branch_tuple, node in self.app.current_snapshot.branch_coordinates.items():
                screen_pos = self._branch_to_screen(branch_tuple, center_x, center_y)
                if screen_pos and highlight_rect.collidepoint(screen_pos):
                    elements_to_shave.append(branch_tuple)
        
        # 🚨 PERMANENTLY DELETE ELEMENTS
        if elements_to_shave and hasattr(self.app, 'current_snapshot'):
            for branch_tuple in elements_to_shave:
                # 1. DELETE FROM CURRENT SNAPSHOT
                if branch_tuple in self.app.current_snapshot.branch_coordinates:
                    del self.app.current_snapshot.branch_coordinates[branch_tuple]
                
                # 2. ADD TO SHAVED SET
                self.shaved_elements.add(branch_tuple)
                
                # 3. TRACK PER PAGE
                if hasattr(self, 'current_page_id') and self.current_page_id:
                    if not hasattr(self, 'page_shaved_map'):
                        self.page_shaved_map = {}
                    if self.current_page_id not in self.page_shaved_map:
                        self.page_shaved_map[self.current_page_id] = set()
                    self.page_shaved_map[self.current_page_id].add(branch_tuple)
                
                # 4. REMOVE FROM PETERBOT PATHS
                if hasattr(self, 'peterbot_paths'):
                    new_paths = []
                    for path in self.peterbot_paths:
                        if branch_tuple not in path:
                            new_paths.append(path)
                    self.peterbot_paths = new_paths
                
                # 5. REMOVE FROM PETERBOT HIGHLIGHTS
                if hasattr(self, 'peterbot_highlights'):
                    self.peterbot_highlights.discard(branch_tuple)
            
            print(f"🔥 PERMANENTLY DELETED {len(elements_to_shave)} ELEMENTS")
            print(f"📊 Remaining elements: {len(self.app.current_snapshot.branch_coordinates)}")
        
        # Reset
        self.highlight_rect_start = None
        self.highlight_rect_end = None
        
    def _draw_control_panel(self, snapshot: DOMSnapshot):
        """FIXED CONTROL PANEL - STATIC POSITIONS WITH OFFLINE MODE AND SHAVING SUPPORT - ALWAYS VISIBLE"""
        # Main title - LEFT SIDE - ALWAYS VISIBLE
        title = self.title_font.render("DOM STRUCTURE EXPLORER", True, (255, 255, 200))
        subtitle = self.small_font.render("Fundamental Patterns Revealed - No More DOM Darkness", True, (200, 220, 255))
        self.screen.blit(title, (20, 15))
        self.screen.blit(subtitle, (20, 50))
        
        if self.recording_mode:
            # TOP CENTER - Highly visible recording indicator
            rec_text = "🔴 RECORDING MODE ACTIVE - Press M to stop"
            rec_surface = self.font.render(rec_text, True, (255, 100, 100))
            rec_rect = rec_surface.get_rect(center=(self.screen_width // 2, 35))
            
            # Draw background with pulsing effect
            pulse = 1.0 + math.sin(pygame.time.get_ticks() * 0.005) * 0.3
            bg_color = (40 + int(pulse * 10), 0, 0)
            border_color = (255, 50 + int(pulse * 20), 50 + int(pulse * 20))
            
            pygame.draw.rect(self.screen, bg_color, rec_rect.inflate(30, 12), border_radius=8)
            pygame.draw.rect(self.screen, border_color, rec_rect.inflate(30, 12), 3, border_radius=8)
            # Add recording icon
            rec_icon = "⏺️"
            icon_surface = pygame.font.Font(None, 36).render(rec_icon, True, (255, 100, 100))
            self.screen.blit(icon_surface, (rec_rect.left - 35, rec_rect.top - 2))
            
            self.screen.blit(rec_surface, rec_rect)

        # 🆕 ADD OFFLINE MODE STATUS INDICATOR - ALWAYS VISIBLE
        if hasattr(self, 'app') and hasattr(self.app, 'offline_mode') and self.app.offline_mode:
            offline_status = "💾 OFFLINE MODE"
            offline_color = (100, 200, 255)
            offline_surface = self.font.render(offline_status, True, offline_color)
            self.screen.blit(offline_surface, (self.screen_width - 150, 15))
            
            offline_help = "Press M to launch browser"
            offline_help_surface = self.small_font.render(offline_help, True, (200, 220, 255))
            self.screen.blit(offline_help_surface, (self.screen_width - 150, 40))
        
        # 🆕 ADD PAGE NAVIGATION INFO - TOP RIGHT CORNER - ALWAYS VISIBLE
        if hasattr(self, 'app') and hasattr(self.app, 'database') and self.app.database.is_active():
            current_page = self.app.database.get_current_page()
            if current_page:
                page_name = current_page.get('page_name', 'Unknown')
                current_idx = self.app.database.current_page_idx + 1
                total_pages = self.app.database.get_page_count()
                
                # Draw page info box
                page_box = pygame.Rect(self.screen_width - 320, 15, 300, 60)
                pygame.draw.rect(self.screen, self.PANEL_BG, page_box, border_radius=8)
                pygame.draw.rect(self.screen, self.AXIS_COLOR, page_box, 2, border_radius=8)
                
                page_info = f"📄 {page_name}"
                page_surface = self.font.render(page_info, True, (255, 255, 200))
                self.screen.blit(page_surface, (self.screen_width - 310, 25))
                
                nav_info = f"Page {current_idx} of {total_pages} | ← → arrows to navigate"
                nav_surface = self.small_font.render(nav_info, True, (200, 220, 255))
                self.screen.blit(nav_surface, (self.screen_width - 310, 50))
        
        # DOM statistics - LEFT SIDE - ALWAYS VISIBLE
        stats = snapshot.dom_stats
        stats_text = [
            f"Elements: {stats['total_elements']}",
            f"Max Depth: {stats['max_depth']}", 
            f"Leaves: {stats['leaf_nodes']} | Branches: {stats['branch_nodes']}",
            f"Complexity: {stats['tree_complexity']:.2f}"
        ]
        
        for i, text in enumerate(stats_text):
            stat_surface = self.font.render(text, True, self.TEXT_COLOR)
            self.screen.blit(stat_surface, (20, 90 + i * 25))
        
        # 🆕 SHAVING INFORMATION - BELOW DOM STATS - ALWAYS VISIBLE IF ELEMENTS ARE SHAVED
        y_offset = 200
        if hasattr(self, 'shaved_elements') and self.shaved_elements:
            shaved_count = len(self.shaved_elements)
            visible_count = stats['total_elements'] - shaved_count
            
            shaving_info = [
                f"🔪 SHAVED: {shaved_count} elements hidden",
                f"📊 VISIBLE: {visible_count} elements shown"
            ]
            
            for i, text in enumerate(shaving_info):
                shave_surface = self.font.render(text, True, (255, 150, 150))
                self.screen.blit(shave_surface, (20, y_offset + i * 25))
            
            y_offset += 60
        
        # Scan generation information - SIMPLIFIED WITHOUT highlight_delta
        y_offset += 20
        
        # Simple status - no change detection (old import system removed)
        if snapshot.interaction_label and snapshot.interaction_label != "initial":
            status_text = f"CURRENT SCAN - {snapshot.interaction_label}"
        else:
            status_text = "CURRENT SCAN"
        
        status_color = (200, 255, 200)
        status_surface = self.font.render(status_text, True, status_color)
        self.screen.blit(status_surface, (20, y_offset))
        y_offset += 30
        
        # Interaction info - LEFT SIDE - ALWAYS VISIBLE IF EXISTS
        if snapshot.interaction_label and snapshot.interaction_label != "initial":
            y_offset += 10
            interaction_text = f"Last Action: {snapshot.interaction_label}"
            interaction_surface = self.font.render(interaction_text, True, (255, 200, 100))
            self.screen.blit(interaction_surface, (20, y_offset))
            y_offset += 25
            
            if snapshot.target_element:
                target_text = f"Target Element: {snapshot.target_element}"
                target_surface = self.small_font.render(target_text, True, (255, 200, 100))
                self.screen.blit(target_surface, (40, y_offset))
                y_offset += 20
        
        # 🆕 PETERBOT ANALYSIS INFO SECTION - ALWAYS VISIBLE IF EXISTS
        if hasattr(self, 'peterbot_analysis_info') and self.peterbot_analysis_info:
            analysis_info = self.peterbot_analysis_info
            y_offset += 20
            
            analysis_header = self.font.render("🎯 PETERBOT ANALYSIS", True, (255, 255, 100))
            self.screen.blit(analysis_header, (20, y_offset))
            y_offset += 30
            
            analysis_lines = [
                f"Analysis Type: {analysis_info['type'].upper()}",
                f"Changed Elements: {analysis_info['changed_count']}",
                f"Interaction Paths: {analysis_info['path_count']}",
                f"Status: IMPORTED & VISUALIZED"
            ]
            
            for line in analysis_lines:
                info_surface = self.small_font.render(line, True, (200, 255, 200))
                self.screen.blit(info_surface, (40, y_offset))
                y_offset += 20
            
            # Show analysis message if available
            if analysis_info.get('message'):
                y_offset += 10
                message_text = f"Summary: {analysis_info['message']}"
                message_surface = self.small_font.render(message_text, True, (255, 200, 100))
                self.screen.blit(message_surface, (20, y_offset))
                y_offset += 25
        
        # RIGHT SIDE CONTROLS GUIDE - MOVED TO TOP RIGHT - ALWAYS VISIBLE
        controls_x = self.screen_width - 350
        controls_y = 80  # TOP RIGHT position
        
        controls = [
            "CONTROLS:",
            "WASD - Navigate the structure",
            "Q/E - Zoom in/out", 
            "R - Reset view",
            "C - Capture interaction",
            "T - Select target (when capturing)",
            "X - Shave/hide elements",
            "ESC - Exit application",
            "",
            "TERMINAL COMMANDS:",
            "save - Save sequence to file",
            "continue - Scan current page", 
            "end - Stop scanning",
            "import - Load PeterBot results",
            "pages - List database pages",
            "goto <n> - Jump to page",
            "",
            "ELEMENT TYPE SYMBOLS:"
        ]
        
        for i, text in enumerate(controls):
            color = (255, 255, 200) if i == 0 or i == 8 or i == 16 else (200, 220, 255)
            control_surface = self.small_font.render(text, True, color)
            self.screen.blit(control_surface, (controls_x, controls_y + i * 20))
        
        # ADD THE ELEMENT TYPE SYMBOLS WITH CIRCLES - ALWAYS VISIBLE
        element_symbols_y = controls_y + len(controls) * 20 + 10
        
        type_symbols = [
            ("B", "Button", (255, 200, 50)),
            ("I", "Input", (80, 180, 255)),
            ("L", "Link", (100, 255, 150)),
            ("T", "Textarea", (80, 180, 255)),
            ("S", "Select", (80, 180, 255)),
            ("F", "Form", (100, 150, 255)),
            ("D", "Div", (100, 150, 255))
        ]
        
        for i, (symbol, name, color) in enumerate(type_symbols):
            y_pos = element_symbols_y + (i * 25)
            
            # Draw colored circle with symbol
            pygame.draw.circle(self.screen, color, (controls_x + 8, y_pos + 8), 8)
            pygame.draw.circle(self.screen, (255, 255, 255), (controls_x + 8, y_pos + 8), 8, 1)
            symbol_text = self.small_font.render(symbol, True, (0, 0, 0))
            self.screen.blit(symbol_text, (controls_x + 5, y_pos + 3))
            
            # Element name
            name_text = self.small_font.render(name, True, self.TEXT_COLOR)
            self.screen.blit(name_text, (controls_x + 25, y_pos))

        # Path display info - LEFT BOTTOM - ALWAYS VISIBLE
        mode_status = "PATH DISPLAY: ON" if self.show_path_mode else "PATH DISPLAY: OFF"
        mode_color = self.PATH_MODE_COLOR if self.show_path_mode else self.TEXT_COLOR
        mode_surface = self.font.render(mode_status, True, mode_color)
        self.screen.blit(mode_surface, (20, self.screen_height - 40))
        
        mode_help = "Press T to toggle path information display"
        help_surface = self.small_font.render(mode_help, True, self.TEXT_COLOR)
        self.screen.blit(help_surface, (20, self.screen_height - 20))
        
        # 🆕 MODE-SPECIFIC STATUS DISPLAY - ALWAYS VISIBLE
        if hasattr(self, 'app') and hasattr(self.app, 'offline_mode') and self.app.offline_mode:
            # OFFLINE MODE STATUS
            status_text = "💾 OFFLINE MODE - Press M to launch browser"
            status_color = (100, 200, 255)  # Blue
            help_text = "No browser connected. Load saved pages with ← → arrows"
            
            # Draw status
            status_surface = self.font.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
            self.screen.blit(status_surface, status_rect)

            help_surface = self.small_font.render(help_text, True, self.TEXT_COLOR)
            help_rect = help_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 10))
            self.screen.blit(help_surface, help_rect)
        else:
            # LIVE MODE: RECORDING STATUS
            if self.recording_mode:
                status_text = "[REC] RECORDING - PeterBot mode active"
                status_color = (255, 100, 100)  # Bright red
                help_text = "Start PeterBot manually, then type 'import' when done"
                
                # 🆕 RED OVERLAY WHEN RECORDING
                overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 30))  # Semi-transparent red
                self.screen.blit(overlay, (0, 0))
                
                # 🆕 CENTER MESSAGE
                center_text = "RECORDING MODE ACTIVE - Press M to stop"
                center_surface = self.title_font.render(center_text, True, (255, 255, 255))
                center_rect = center_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
                
                # Background for center text
                bg_rect = center_rect.inflate(40, 20)
                pygame.draw.rect(self.screen, (50, 0, 0), bg_rect, border_radius=8)
                pygame.draw.rect(self.screen, (255, 100, 100), bg_rect, 2, border_radius=8)
                self.screen.blit(center_surface, center_rect)
            else:
                status_text = "[REC] READY - Press M to start recording"
                status_color = (200, 200, 200)  # Gray
                help_text = "Press M to enable PeterBot coordination mode"
            
            # Draw recording status
            status_surface = self.font.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
            self.screen.blit(status_surface, status_rect)

            help_surface = self.small_font.render(help_text, True, self.TEXT_COLOR)
            help_rect = help_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 10))
            self.screen.blit(help_surface, help_rect)

        # Path availability indicator - ALWAYS VISIBLE
        has_paths = hasattr(self, 'peterbot_paths') and self.peterbot_paths
        path_status = "🟢 PATHS AVAILABLE (Press P)" if has_paths else "🔴 NO PATHS (Import PeterBot first)"
        path_color = (100, 255, 100) if has_paths else (200, 100, 100)
        path_surface = self.small_font.render(path_status, True, path_color)
        self.screen.blit(path_surface, (20, self.screen_height - 100))
        
        # 🎯 SHAVING MODE INDICATOR - BOTTOM CENTER - ALWAYS VISIBLE IF ACTIVE
        if self.highlight_mode:
            shave_mode_text = "🔴 SHAVING MODE - Drag to select, Press X to confirm"
            shave_mode_surface = self.font.render(shave_mode_text, True, (255, 100, 100))
            shave_mode_rect = shave_mode_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 70))
            self.screen.blit(shave_mode_surface, shave_mode_rect)
            
    def draw_dom_structure(self, snapshot: DOMSnapshot):
        """RENDER WITH PATH MODE AND HIGHLIGHTING SUPPORT"""
        self.screen.fill(self.COSMIC_BG)
        self._draw_starfield()
        
        center_x = self.screen_width // 2 + self.pan_x
        center_y = 150 + self.pan_y
        
        if not self.path_mode:
            self._draw_structural_grid(center_x, center_y)
            self._draw_dom_connections(snapshot, center_x, center_y)
            
            for branch_tuple, node in snapshot.branch_coordinates.items():
                if branch_tuple in self.shaved_elements:
                    continue
                screen_pos = self._branch_to_screen(branch_tuple, center_x, center_y)
                if screen_pos:
                    self._draw_element_node(screen_pos, node, branch_tuple)
        
        self._draw_peterbot_paths(center_x, center_y)
        
        if self.path_mode:
            self._draw_path_mode_overlay()
        
        if self.highlight_mode:
            self._draw_highlight_rectangle()
        
        # 🚨 CRITICAL FIX: ALWAYS DRAW THESE UI ELEMENTS
        self._draw_control_panel(snapshot)
        self._draw_structure_legend()
        
        # Only draw hover info when there's actually something hovered
        if self.hovered_element:
            self._draw_hover_info(snapshot.branch_coordinates.get(self.hovered_element))
        
        self._draw_shaving_info()
        
    def update_display(self):
        """REFRESH THE WINDOW TO REALITY"""
        pygame.display.flip()

# ===== BROWSER MANAGEMENT =====

def setup_browser(port=9223):
    """Launch Chrome with remote debugging"""
    print(f"🚀 Starting Chrome with remote debugging on port {port}...")
    
    try:
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        options.add_argument(f"--remote-debugging-port={port}")
        options.add_argument("--remote-allow-origins=*")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--window-position=-1500,0")
        options.add_argument("--window-size=1200,800")
        
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Browser launched with remote debugging enabled!")
        return driver
        
    except Exception as e:
        print(f"❌ Browser launch failed: {e}")
        return None

def attach_to_existing_browser(port=9223):
    """Attach to existing Chrome instance"""
    print(f"🔗 Attaching to browser on port {port}...")
    
    try:
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        
        driver = uc.Chrome(options=options)
        print(f"✅ Attached to browser: {driver.current_url}")
        return driver
        
    except Exception as e:
        print(f"⚠️ Undetected chromedriver attach failed: {e}")
        
        try:
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            
            service = Service()
            driver = webdriver.Chrome(service=service, options=options)
            print(f"✅ Attached to browser: {driver.current_url}")
            return driver
            
        except Exception as e2:
            print(f"❌ Could not attach to browser: {e2}")
            return None

# ===== MAIN APPLICATION =====

class DOMInteractionCaptureApp:
    """Main application class"""
    
    def __init__(self):
        self.driver = None
        self.database = VengerDatabase()
        self.scanner = None
        self.visualizer = None
        self.current_snapshot = None
        self.offline_mode = False
        self.current_url = ""
        self.visualizer_initialized = False
        self.database_initialized = False
        self.recording_mode = False

    def _create_enhanced_priori_file(self):
        """CREATE ENHANCED PRIORI WITH PETERBOT INSTRUCTIONS"""
        if not hasattr(self, 'current_snapshot') or not self.current_snapshot:
            print("❌ No current snapshot - scan a page first!")
            return None
        
        # Use the existing visualizer method
        if hasattr(self, 'visualizer') and hasattr(self.visualizer, '_create_priori_file'):
            priori_path = self.visualizer._create_priori_file()
            
            # Add PeterBot instructions to the file
            if priori_path and os.path.exists(priori_path):
                try:
                    with open(priori_path, 'r') as f:
                        priori_data = json.load(f)
                    
                    # Add PeterBot-specific instructions
                    priori_data['peterbot_instructions'] = {
                        'mode': 'recording',
                        'timestamp': int(time.time()),
                        'url': self.driver.current_url if self.driver else '',
                        'elements_count': len(self.current_snapshot.branch_coordinates),
                        'interactive_count': sum(1 for node in self.current_snapshot.branch_coordinates.values() 
                                            if node.is_interactive),
                        'instructions': [
                            "1. Monitor browser for DOM changes",
                            "2. Record all user interactions",
                            "3. Capture audio input if available",
                            "4. Track navigation patterns",
                            "5. Generate interaction paths"
                        ]
                    }
                    
                    with open(priori_path, 'w') as f:
                        json.dump(priori_data, f, indent=2)
                    
                    print(f"✅ Enhanced priori with PeterBot instructions: {priori_path}")
                    return priori_path
                    
                except Exception as e:
                    print(f"⚠️ Could not enhance priori file: {e}")
                    return priori_path  # Return original if enhancement fails
            
        print("❌ Could not create priori file")
        return None

    def _toggle_recording_mode_standard(self):
        """STANDARD RECORDING MODE TOGGLE (LIVE MODE) WITH BROWSER LAUNCH"""
        self.recording_mode = not self.recording_mode
        
        if self.recording_mode:
            print("\n" + "="*60)
            print("🎬 PETERBOT RECORDING MODE ACTIVATED")
            print("="*60)
            
            # 🚨 LAUNCH BROWSER IF NOT OPEN
            if not self.driver:
                print("🚀 Launching browser for PeterBot...")
                self.driver = setup_browser(9223)
                if not self.driver:
                    print("❌ Failed to launch browser - recording mode disabled")
                    self.recording_mode = False
                    return None
                
                # Initialize scanner
                if not hasattr(self, 'scanner') or not self.scanner:
                    self.scanner = DOMScanner(self.driver)
                
                print("✅ Browser launched successfully!")
            
            # Ensure visualizer knows about recording mode for red overlay
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.recording_mode = True
            
            # 🚨 CREATE ENHANCED PRIORI WITH PETERBOT INSTRUCTIONS
            priori_path = self._create_enhanced_priori_file()
            
            if priori_path:
                # Extract timestamp from filename
                timestamp = priori_path.split('_')[-1].replace('.json', '')
                
                print("\n" + "="*60)
                print("📋 PETERBOT INSTRUCTIONS - SWITCH TO TERMINAL")
                print("="*60)
                print("\n1. ✅ Browser is ready")
                print("2. ✅ Priori file created")
                print("\n3. SWITCH TO TERMINAL WINDOW (ALT+TAB)")
                print("4. RUN THIS COMMAND:")
                print(f"   python3 PeterBot.py --priori venger_priori_{timestamp}.json")
                print("\n5. Wait for PeterBot to complete")
                print("6. Return here and type 'import' when done")
                print("\n" + "="*60)
                print("🔴 RED OVERLAY: Recording mode active")
                print("   PyGame remains open - browser is ready for PeterBot")
                print("="*60)
                
                # Also show URL for reference
                if self.driver:
                    try:
                        current_url = self.driver.current_url
                        print(f"\n📍 Current browser URL: {current_url[:100]}...")
                    except:
                        pass
                    
                return True
            else:
                print("❌ Failed to create priori file - recording mode disabled")
                self.recording_mode = False
                if hasattr(self, 'visualizer') and self.visualizer:
                    self.visualizer.recording_mode = False
                return False
                    
        else:
            print("⏹️ PETERBOT RECORDING MODE DEACTIVATED")
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.recording_mode = False
            return None
        

    def initialize(self):
        """Initialize application"""
        print("DOM Interaction Capturer")
        print("=" * 60)
        
        # Database initialization
        print("\n" + "=" * 60)
        print("🗄️  DATABASE CONFIGURATION")
        print("=" * 60)
        
        use_db = input("Use database to save pages? (y/n, Enter=y): ").strip().lower()
        
        if use_db in ['y', 'yes', '']:
            self.database_initialized = self.database.prompt_for_database()
            
            if self.database_initialized:
                print(f"\n✅ Database loaded: {self.database.current_site}")
                print(f"📄 Pages available: {self.database.get_page_count()}")
                
                if self.database.get_page_count() > 0:
                    offline_choice = input("\nLoad pages in offline mode (no browser)? (y/n, Enter=y): ").strip().lower()
                    if offline_choice in ['y', 'yes', '']:
                        self.offline_mode = True
                        self.driver = None
                        print("🚫 Entering offline mode with saved pages")
                    else:
                        print("🌐 Proceeding with browser connection")
                else:
                    print("📭 No saved pages found - proceeding with browser")
            else:
                print("⚠️ Database not initialized")
        else:
            print("⚠️ Running without database")
        
        # Browser setup
        if not self.offline_mode:
            print("\n" + "=" * 60)
            print("🌐 BROWSER CONFIGURATION")
            print("=" * 60)
            
            print("\nBrowser options:")
            print("  1) Launch new Chrome with remote debugging")
            print("  2) Attach to existing Chrome")
            print("  3) Cancel and go to offline mode")
            
            choice = input("\nSelect option (1-3, Enter=1): ").strip()
            
            if choice == "2":
                port = input("Debug port (default 9223): ").strip()
                port = int(port) if port.isdigit() else 9223
                self.driver = attach_to_existing_browser(port)
            elif choice == "3":
                print("💾 Switching to offline mode")
                self.driver = None
                self.offline_mode = True
            else:
                self.driver = setup_browser(9223)
            
            if self.driver:
                self.current_url = self.driver.current_url
                print(f"\n✅ Connected to browser: {self.current_url}")
                self.scanner = DOMScanner(self.driver)
            elif not self.offline_mode:
                print("⚠️ No browser connection - switching to offline mode")
                self.offline_mode = True
        
        print("\n" + "=" * 60)
        print("📋 INSTRUCTIONS")
        print("=" * 60)
        
        if self.offline_mode:
            print("\n💾 OFFLINE MODE COMMANDS:")
            print("  'pages'     - List pages in database")
            print("  'goto <n>'  - Load page from database")
            print("  'M'         - Launch browser")
            print("  'help'      - Show all commands")
        else:
            print("\n🌐 LIVE MODE COMMANDS:")
            print("  'scan'      - Scan current page")
            print("  'M'         - Toggle PeterBot recording")
            print("  'save'      - Save current page")
            print("  'import'    - Load PeterBot results")
            print("  'help'      - Show all commands")
        
        print("\n💡 Type a command to begin...")
        return True
    def _show_full_status_and_menu(self):
        """Show status and menu"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("="*60)
        print("VENGER - DOM DATABASE SYSTEM")
        print("="*60)
        
        print("\n📊 CURRENT STATUS:")
        print("-"*30)
        
        mode = "💾 OFFLINE" if self.offline_mode else "🌐 ONLINE"
        print(f"{mode} MODE")
        
        if self.driver:
            try:
                url = self.driver.current_url
                if len(url) > 50:
                    url = url[:47] + "..."
                print(f"🌐 Browser: {url}")
            except:
                print("🌐 Browser: Connected")
        else:
            print("🌐 Browser: Disconnected")
        
        if self.database.is_active():
            print(f"🗄️  Database: {self.database.current_site}")
            print(f"📄 Pages: {self.database.get_page_count()}")
            if self.database.get_page_count() > 0:
                current_page = self.database.get_current_page_name()
                print(f"📄 Current page: {current_page}")
        else:
            print("🗄️  Database: Not loaded")
        
        if self.visualizer_initialized:
            print("🎮 Visualizer: ACTIVE (use ESC to return to terminal)")
        
        print("\n" + "="*60)
        print("📋 AVAILABLE COMMANDS:")
        print("="*60)
        
        print("\n🗄️  DATABASE:")
        print("  database      - Select/create database")  # 🆕 ADDED
        print("  pages         - List all saved pages")
        print("  goto <n>      - Go to page n")
        print("  loadurl <n>   - Load page n's URL in browser")
        print("  save [name]   - Save current scan")
        print("  delete <n>    - Delete page n")
        print("  cleanup       - Delete ALL pages")
        
        print("\n🌐 BROWSER:")
        print("  online [url]  - Launch browser (optional URL)")
        print("  offline       - Switch to offline mode")
        print("  browser       - Browser control")
        
        print("\n🔍 SCANNING:")
        print("  scan          - Scan current page")
        
        print("\n🛠️  SYSTEM:")
        print("  import        - Import PeterBot results")
        print("  status        - Detailed status")
        print("  clear         - Clear screen")
        print("  help          - Show help")
        print("  quit          - Exit")
        
        print("\n" + "="*60)
        print("💡 Type a command and press Enter")
        print("="*60)
        
    def _scan_page(self):
        """Scan current page then detach browser for visualization"""
        if not self.driver:
            print("❌ No browser connected!")
            print("💡 Press 'M' to launch browser first")
            return
        
        print("\n🔍 Scanning current page...")
        
        try:
            scan_url = self.driver.current_url
            print(f"📍 Scanning URL: {scan_url[:100]}")
            self.current_url = scan_url
            
            self.current_snapshot = self.scanner.scan_dom()
            print(f"✅ Scan complete: {len(self.current_snapshot.branch_coordinates)} elements")
            
            interactive_count = sum(1 for node in self.current_snapshot.branch_coordinates.values() if node.is_interactive)
            pattern_count = sum(1 for node in self.current_snapshot.branch_coordinates.values() if node.pattern_roles)
            print(f"🖱️ Interactive: {interactive_count} elements")
            print(f"🎯 Patterns: {pattern_count} elements")
            
            # 🚨 DETACH BROWER HERE (after scan, before save prompt)
            print("\n🔄 Detaching browser for visualization...")
            # We keep self.driver reference but stop using it
            
            if not self.visualizer_initialized:
                print("\n🎮 Starting visualizer...")
                self.visualizer = DOMStructureVisualizer()
                self.visualizer.app = self
                self.visualizer_initialized = True
                print("✅ Visualizer started!")
                
                if self.database.is_active():
                    auto_save = input("\n💾 Save this scan to database? (y/n, Enter=n): ").strip().lower()
                    if auto_save == 'y':
                        self._save_current_page_to_db()
                
                print("\n🎮 Visualizer controls:")
                print("  WASD - Navigate structure")
                print("  Q/E  - Zoom in/out")
                print("  C    - Capture interaction")
                print("  ESC  - Exit to terminal")
                print("\n💡 Browser is detached. Close visualizer to re-attach.")
                
            else:
                # Visualizer already running, just update snapshot
                print("✅ Updated visualization with new scan")
                
        except Exception as e:
            print(f"❌ Scan failed: {e}")

    def _load_database_page(self, page_data, page_idx=None):
        """Load page from database into visualizer with shaving memory"""
        try:
            page_name = page_data.get('page_name', 'Unknown')
            print(f"\n📄 Loading: {page_name}")
            
            # 🚨 SET CURRENT PAGE ID FOR SHAVING TRACKING
            page_id = page_data.get('page_name', f'page_{page_idx if page_idx is not None else "unknown"}')
            self.current_page_id = page_id
            
            coordinate_space = {}
            
            if 'coordinate_space' in page_data:
                for coord_key, element_data in page_data['coordinate_space'].items():
                    try:
                        if isinstance(coord_key, str):
                            coord = self.database._string_to_coordinate(coord_key)
                        else:
                            coord = coord_key if isinstance(coord_key, tuple) else tuple(coord_key)
                        
                        node = CoordinateNode(coord, element_data)
                        coordinate_space[coord] = node
                    except Exception as e:
                        print(f"⚠️ Failed to create node from {coord_key}: {e}")
                        continue
            
            snapshot = DOMSnapshot(
                branch_coordinates=coordinate_space,
                timestamp=time.time(),
                dom_stats=page_data.get('dom_stats', {}),
                interaction_label=f"loaded_{page_name}"
            )
            
            self.current_snapshot = snapshot
            
            # 🚨 RESTORE SHAVED ELEMENTS FOR THIS PAGE
            if hasattr(self, 'page_shaved_map') and page_id in self.page_shaved_map:
                self.shaved_elements = self.page_shaved_map[page_id].copy()
                print(f"🔪 Restored {len(self.shaved_elements)} previously shaved elements")
            else:
                self.shaved_elements = set()
            
            # Load PeterBot paths if they exist
            if 'peterbot_paths' in page_data and page_data['peterbot_paths']:
                parsed_paths = []
                for path in page_data['peterbot_paths']:
                    parsed_path = [self.database._string_to_coordinate(coord_str) for coord_str in path]
                    parsed_paths.append(parsed_path)
                
                if hasattr(self, 'peterbot_paths'):
                    self.peterbot_paths = parsed_paths
                    print(f"🛣️ Loaded {len(parsed_paths)} PeterBot paths")
            
            if not self.visualizer_initialized:
                print("\n🎮 Starting visualizer...")
                self.visualizer = DOMStructureVisualizer()
                self.visualizer.app = self
                self.visualizer_initialized = True
                print("✅ Visualizer started!")
                
            print(f"✅ Loaded {len(coordinate_space)} elements")
            return True
            
        except Exception as e:
            print(f"❌ Error loading page: {e}")
            return False

    def _show_mode_specific_menu(self):
        """Show simplified menu for current mode"""
        print("\n" + "="*60)
        
        if self.offline_mode:
            print("💾 OFFLINE MODE - Database Only")
            print("="*60)
            print("\n📋 COMMANDS:")
            print("  database      - Select/create database")  # 🆕 ADDED
            print("  pages         - List pages in database")
            print("  goto <n>      - Load page from database")
            print("  load <n>      - Load page n's URL for PeterBot prep")
            print("  online [url]  - Launch browser (optional URL)")
            print("  main          - Show full menu")
            print("  help          - Show help")
            print("  quit          - Exit")
        else:
            print("🌐 ONLINE MODE - Browser Connected")
            print("="*60)
            print("\n📋 COMMANDS:")
            print("  database      - Select/create database")  # 🆕 ADDED
            print("  tabs          - List all open browser tabs")
            print("  switch <n>    - Switch to tab n")
            print("  scan          - Scan current page")
            print("  load <n>      - Load saved page URL")
            print("  M             - Toggle PeterBot recording (in visualizer)")
            print("  save          - Save current page")
            print("  import        - Load PeterBot results")
            print("  offline       - Switch to offline mode")
            print("  main          - Show full menu")
            print("  help          - Show help")
            print("  quit          - Exit")
        
        if self.driver:
            try:
                current_url = self.driver.current_url
                print(f"\n💡 Current URL: {current_url[:80] + '...' if len(current_url) > 80 else current_url}")
            except:
                print(f"\n💡 Current URL: {self.current_url[:80] + '...' if len(self.current_url) > 80 else self.current_url}")
        elif self.current_url:
            print(f"\n💡 Last URL: {self.current_url[:80] + '...' if len(self.current_url) > 80 else self.current_url}")
        
        if self.database.is_active():
            print(f"📁 Database: {self.database.current_site} ({self.database.get_page_count()} pages)")
        
        print("="*60)

    def _list_browser_tabs(self):
        """List all open browser tabs"""
        if not self.driver:
            print("❌ No browser connected")
            return
        
        try:
            # Get all window handles
            window_handles = self.driver.window_handles
            print(f"\n📋 Browser Tabs ({len(window_handles)} total):")
            
            # Get current window handle
            current_handle = self.driver.current_window_handle
            
            for i, handle in enumerate(window_handles):
                try:
                    # Switch to the tab temporarily to get URL
                    self.driver.switch_to.window(handle)
                    url = self.driver.current_url
                    title = self.driver.title or "No title"
                    
                    current_marker = " 👈 CURRENT" if handle == current_handle else ""
                    print(f"  [{i}] {title[:50]}")
                    print(f"      {url[:80]}...{current_marker}")
                except Exception as e:
                    print(f"  [{i}] Could not access tab: {e}")
            
            # Switch back to original tab
            self.driver.switch_to.window(current_handle)
            
        except Exception as e:
            print(f"❌ Failed to list tabs: {e}")

    def _switch_to_tab(self, tab_number):
        """Switch to a specific browser tab"""
        if not self.driver:
            print("❌ No browser connected")
            return False
        
        try:
            window_handles = self.driver.window_handles
            
            if 0 <= tab_number < len(window_handles):
                target_handle = window_handles[tab_number]
                self.driver.switch_to.window(target_handle)
                
                # Update current URL
                self.current_url = self.driver.current_url
                
                print(f"✅ Switched to tab {tab_number}")
                print(f"📍 URL: {self.current_url[:80]}...")
                return True
            else:
                print(f"❌ Invalid tab number. Available: 0-{len(window_handles)-1}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to switch tabs: {e}")
            return False  

    def _save_current_page_to_db(self, page_name=""):
        """Save current page to database - DEBUG VERSION"""
        print(f"\n💾 DEBUG: Starting save process...")
        print(f"   - Has snapshot: {self.current_snapshot is not None}")
        print(f"   - Database active: {self.database.is_active()}")
        print(f"   - Offline mode: {self.offline_mode}")
        print(f"   - Page name provided: '{page_name}'")
        
        if not self.current_snapshot:
            print("❌ DEBUG: No current snapshot to save")
            return None
        
        if not self.database.is_active():
            print("❌ DEBUG: No database loaded!")
            create_now = input("Create a database now? (y/n): ").strip().lower()
            if create_now == 'y':
                site_name = input("Enter site name: ").strip()
                if site_name:
                    if self.database._create_new_site():
                        print(f"✅ Created database: {site_name}")
                        self.database.is_loaded = True
                        self.database_initialized = True
                    else:
                        print("❌ Failed to create database")
                        return None
                else:
                    print("❌ Site name cannot be empty")
                    return None
            else:
                return None
        
        # Get URL
        url = ""
        if not self.offline_mode and self.driver:
            try:
                url = self.driver.current_url
                print(f"✅ DEBUG: Got URL from browser: {url[:80]}...")
            except Exception as e:
                print(f"⚠️ DEBUG: Could not get URL from browser: {e}")
        elif self.offline_mode and not url:
            url = input("Enter URL for this page: ").strip() or ""
        
        # Generate page name if not provided
        if not page_name:
            if url:
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                if parsed.path:
                    path_parts = parsed.path.split('/')
                    if len(path_parts) > 1:
                        page_name = path_parts[-1] or path_parts[-2]
                        print(f"✅ DEBUG: Generated page name from URL: {page_name}")
            if not page_name:
                page_name = input("Enter page name: ").strip() or f"page_{len(self.database.pages) + 1}"
                print(f"✅ DEBUG: Using user-provided page name: {page_name}")
        
        page_name = page_name.replace(' ', '_').replace('/', '_').lower()[:50]
        
        # Get PeterBot paths if available
        paths = None
        if hasattr(self, 'visualizer') and hasattr(self.visualizer, 'peterbot_paths') and self.visualizer.peterbot_paths:
            paths = self.visualizer.peterbot_paths
            print(f"✅ DEBUG: Found {len(paths)} PeterBot paths")
        
        print(f"💾 DEBUG: Saving page: {page_name}")
        print(f"   - URL: {url[:80]}..." if url else "   - URL: (none)")
        print(f"   - Elements: {len(self.current_snapshot.branch_coordinates)}")
        print(f"   - Paths: {len(paths) if paths else 0}")
        
        filename = self.database.save_current_page(
            snapshot=self.current_snapshot,
            page_name=page_name,
            url=url,
            paths=paths
        )
        
        if filename:
            print(f"✅ DEBUG: Page saved to database: {filename}")
            return filename
        else:
            print("❌ DEBUG: Failed to save page")
            return None
            
    def _import_peterbot_results(self):
        """Import PeterBot results"""
        print("\n📥 IMPORTING PETERBOT RESULTS...")
        
        results_path = self._find_latest_results()
        if not results_path:
            print("❌ No PeterBot result files found")
            return
        
        try:
            with open(results_path, 'r') as f:
                results = json.load(f)
            
            print(f"✅ Loaded PeterBot results")
            
            paths = []
            analysis_info = {}
            
            if 'spidey_bot_analysis' in results:
                spidey_data = results['spidey_bot_analysis']
                interaction_paths = spidey_data.get('interaction_paths', {})
                
                if 'coordinate_paths' in interaction_paths:
                    for path in interaction_paths['coordinate_paths']:
                        tuple_path = [tuple(coord) for coord in path if isinstance(coord, (list, tuple))]
                        if len(tuple_path) >= 2:
                            paths.append(tuple_path)
                
                monitoring_summary = spidey_data.get('monitoring_summary', {})
                analysis_info = {
                    'type': 'peterbot',
                    'changed_count': monitoring_summary.get('total_changes_detected', 0),
                    'path_count': len(paths),
                    'timestamp': spidey_data.get('timestamp', time.time()),
                    'message': f"PeterBot - {spidey_data.get('page_type', 'general')}"
                }
            elif 'enhanced_data' in results:
                enhanced_data = results.get('enhanced_data', {})
                interaction_paths = enhanced_data.get('interaction_paths', {})
                
                if 'coordinate_paths' in interaction_paths:
                    for path in interaction_paths['coordinate_paths']:
                        tuple_path = [tuple(coord) for coord in path if isinstance(coord, (list, tuple))]
                        if len(tuple_path) >= 2:
                            paths.append(tuple_path)
                
                pattern_analysis = enhanced_data.get('pattern_analysis', {})
                analysis_info = {
                    'type': 'peterbot',
                    'changed_count': pattern_analysis.get('total_pattern_changes_in_selected', 0),
                    'path_count': len(paths),
                    'timestamp': results.get('timestamp', time.time()),
                    'message': results.get('message', '')
                }
            else:
                analysis_info = {
                    'type': 'unknown',
                    'changed_count': 0,
                    'path_count': len(paths),
                    'timestamp': time.time(),
                    'message': 'Imported results'
                }
            
            print(f"🛣️ Found {len(paths)} paths")
            
            if hasattr(self, 'visualizer') and self.visualizer:
                self.visualizer.peterbot_paths = paths
                self.visualizer.peterbot_analysis_info = analysis_info
                print(f"✅ Updated visualization with {len(paths)} paths")
            
            os.remove(results_path)
            print("🧹 Cleaned up results file")
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    def _find_latest_results(self):
        """Find latest PeterBot results file"""
        devengers_path = "TheDevengers"
        if not os.path.exists(devengers_path):
            return None
        
        result_files = [f for f in os.listdir(devengers_path) if f.startswith('spidey_bot_results_')]
        
        if not result_files:
            return None
        
        latest_file = max(result_files, key=lambda x: int(x.split('_')[-1].replace('.json', '')))
        return os.path.join(devengers_path, latest_file)
    
    def _handle_database_navigation(self, direction):
        """Handle database page navigation"""
        if not self.database.is_active():
            print("⚠️ No database loaded")
            return False
        
        success = False
        if direction == 'next':
            success = self.database.next_page()
        elif direction == 'prev':
            success = self.database.prev_page()
        
        if success:
            page_data = self.database.get_current_page()
            if page_data:
                self._load_database_page(page_data)
                return True
        
        return False

    def _load_url_from_database_page(self, page_num):
        """Load URL from database page WITHOUT auto-triggering PeterBot"""
        if not self.database.is_active():
            print("❌ No database loaded")
            return False
        
        if not (0 <= page_num < len(self.database.pages)):
            print(f"❌ Invalid page: {page_num}")
            return False
        
        page_data = self.database.pages[page_num]
        url = page_data.get('url', '')
        
        if not url:
            print("❌ This page has no URL saved")
            return False
        
        print(f"\n🌐 Loading URL from page {page_num}: {url[:80]}...")
        
        if not self.driver:
            print("🚀 Launching browser...")
            self.driver = setup_browser(9223)
            if not self.driver:
                print("❌ Failed to launch browser")
                return False
            self.scanner = DOMScanner(self.driver)
        
        try:
            self.driver.get(url)
            time.sleep(3)
            self.current_url = self.driver.current_url
            self.offline_mode = False
            print(f"✅ Navigated to: {self.current_url[:80]}...")
            
            # 🚨 CRITICAL: Load the snapshot from database for this page
            if self.database.is_active():
                page_data = self.database.pages[page_num]
                self._load_database_page(page_data, page_num)
                print(f"✅ Loaded snapshot from database: {len(self.current_snapshot.branch_coordinates)} elements")
            
            return True
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False

    def _switch_to_online_mode(self, url=None):
        """Switch to online mode"""
        print("\n🌐 Switching to online mode...")
        
        if not self.driver:
            self.driver = setup_browser(9223)
            if not self.driver:
                print("❌ Failed to launch browser")
                return False
        
        if url:
            try:
                self.driver.get(url)
                time.sleep(3)
                self.current_url = self.driver.current_url
                print(f"✅ Navigated to: {self.current_url[:80]}...")
            except Exception as e:
                print(f"⚠️ Could not navigate to {url}: {e}")
        
        self.offline_mode = False
        
        if not hasattr(self, 'scanner') or not self.scanner:
            self.scanner = DOMScanner(self.driver)
        
        print("✅ Online mode ready. Type 'scan' to capture current page.")
        return True
   
    def _select_database(self):
        """Prompt for database selection (can be called from terminal)"""
        print("\n" + "="*60)
        print("🗄️  DATABASE SELECTION")
        print("="*60)
        
        # Use the existing database prompt method
        success = self.database.prompt_for_database()
        
        if success:
            print(f"\n✅ Database loaded: {self.database.current_site}")
            print(f"📄 Pages available: {self.database.get_page_count()}")
            
            # 🆕 AUTOMATICALLY SHOW PAGES
            if self.database.get_page_count() > 0:
                print("\n" + "="*60)
                print("📄 AVAILABLE PAGES:")
                print("="*60)
                
                for i, page_data in enumerate(self.database.pages):
                    page_name = page_data.get('page_name', f'Page {i+1}')
                    elements = page_data.get('total_elements', 0)
                    timestamp = page_data.get('timestamp', 'Unknown')
                    
                    current_marker = "👉" if i == self.database.current_page_idx else "  "
                    print(f"{current_marker}[{i}] {page_name}")
                    print(f"     📊 {elements} elements | 📅 {timestamp}")
            
            # Ask about offline mode if there are pages
            if self.database.get_page_count() > 0 and self.driver is None:
                offline_choice = input("\nLoad pages in offline mode (no browser)? (y/n, Enter=y): ").strip().lower()
                if offline_choice in ['y', 'yes', '']:
                    self.offline_mode = True
                    print("💾 Entering offline mode with saved pages")
                else:
                    print("🌐 Proceeding with browser connection")
                    
            # 🆕 SHOW COMMANDS AFTER DATABASE SELECTION
            print("\n" + "="*60)
            print("📋 AVAILABLE COMMANDS:")
            print("="*60)
            print("  goto <n>      - Load page n into visualizer")
            print("  load <n>      - Load page n's URL in browser")
            print("  pages         - List all pages with options")
            print("  main          - Return to main menu")
            print("="*60)
            
        else:
            print("⚠️ No database loaded")
        
        return success
        
    def run_interaction_loop(self):
        """Main interaction loop with browser detachment support"""
        print("\n🎮 STARTING INTERACTION LOOP...")
        self._show_mode_specific_menu()
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # 🚨 CRITICAL FIX: Always check for PyGame events when visualizer is initialized
            if self.visualizer_initialized and self.visualizer:
                # Process PyGame events
                event = self.visualizer.handle_events()
                
                if event == 'quit_and_reattach':  # ESC pressed in visualizer
                    print("\n" + "="*60)
                    print("🔄 CLOSING VISUALIZER")
                    print("="*60)
                    
                    self.visualizer_initialized = False
                    
                    # Reset visualizer modes
                    if self.visualizer:
                        self.visualizer.recording_mode = False
                        self.visualizer.highlight_mode = False
                        self.visualizer.path_mode = False
                    
                    # Show menu
                    self._show_mode_specific_menu()
                    continue  # Back to terminal input
                        
                elif event == 'quit':  # Full quit from visualizer
                    running = False
                    continue
                elif event == 'capture':
                    if not self.offline_mode and self.driver:
                        print("\n📸 Capture triggered from visualizer")
                        print("💡 Return to terminal (ESC) to process capture")
                elif event == 'toggle_recording':  # 'M' key pressed
                    # Call the recording mode toggle
                    success = self._toggle_recording_mode_standard()
                    # Ensure visualizer state is updated
                    if hasattr(self.visualizer, 'recording_mode'):
                        self.visualizer.recording_mode = self.recording_mode
                    continue
                elif event == 'next_page':
                    self._handle_database_navigation('next')
                    continue
                elif event == 'prev_page':
                    self._handle_database_navigation('prev')
                    continue
                
                # Update visualization
                if self.current_snapshot:
                    mouse_pos = pygame.mouse.get_pos()
                    self.visualizer.update_hover(mouse_pos, self.current_snapshot)
                    self.visualizer.draw_dom_structure(self.current_snapshot)
                    self.visualizer.update_display()
                
                clock.tick(60)
                continue  # Skip terminal input when visualizer is active
            
            # Terminal command processing (only when visualizer is NOT active)
            try:
                user_input = input("\nvenger> ").strip()
                
                if user_input == "":
                    continue
                
                parts = user_input.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Handle mode-agnostic commands first
                if cmd == 'main':
                    self._show_full_status_and_menu()
                    continue
                elif cmd == 'status':
                    self._show_full_status_and_menu()
                    continue
                elif cmd == 'clear' or cmd == 'cls':
                    self._show_full_status_and_menu()
                    continue
                elif cmd == 'help':
                    self._show_mode_specific_menu()
                    continue
                elif cmd == 'quit' or cmd == 'exit':
                    running = False
                    continue
                elif cmd == 'database':  # 🆕 NEW COMMAND
                    self._select_database()
                    self._show_mode_specific_menu()
                    continue
                
                # Handle mode-specific commands
                if self.offline_mode:
                    # OFFLINE MODE COMMANDS
                    if cmd == 'scan':
                        print("❌ Cannot scan in offline mode. Use 'online' first.")
                    elif cmd == 'tabs':
                        print("❌ No browser in offline mode. Use 'online' first.")
                    elif cmd == 'load':
                        if args and args[0].isdigit():
                            page_num = int(args[0])
                            print(f"\n🌐 Loading page {page_num} URL for PeterBot...")
                            
                            # Just load the URL, don't auto-trigger PeterBot prep
                            if self._load_url_from_database_page(page_num):
                                print("\n✅ URL loaded in browser")
                                print("💡 Now press 'M' in PyGame to create priori file for PeterBot")
                            else:
                                print("❌ Failed to load URL")
                        else:
                            print("❌ Usage: load <page_number>")
                            
                    elif cmd == 'switch':
                        print("❌ No browser in offline mode. Use 'online' first.")
                    elif cmd == 'pages':
                        self.database.list_saved_pages_with_options()
                    elif cmd == 'goto':
                        if args and args[0].isdigit():
                            page_num = int(args[0])
                            if 0 <= page_num < len(self.database.pages):
                                self.database.current_page_idx = page_num
                                page_data = self.database.get_current_page()
                                if page_data:
                                    # 🚨 CRITICAL: This should start the visualizer
                                    self._load_database_page(page_data)
                                    print("\n✅ Page loaded into visualizer")
                                    print("🎮 Use WASD to navigate, M to launch browser, ESC to return")
                                else:
                                    print("❌ Failed to load page data")
                            else:
                                print(f"❌ Invalid page number. Available: 0-{len(self.database.pages)-1}")
                        else:
                            print("❌ Usage: goto <page_number>")
                    elif cmd == 'loadurl':
                        if args and args[0].isdigit():
                            self._load_url_from_database_page(int(args[0]))
                        else:
                            print("❌ Usage: loadurl <page_number>")
                    elif cmd == 'online':
                        url = ' '.join(args) if args else None
                        self._switch_to_online_mode(url)
                        self._show_mode_specific_menu()
                    elif cmd == 'offline':
                        print("⚠️ Already in offline mode")
                    elif cmd == 'save':
                        page_name = ' '.join(args) if args else ""
                        print(f"\n💾 Attempting to save with page name: '{page_name}'")
                        self._save_current_page_to_db(page_name)
                    elif cmd == 'import':
                        self._import_peterbot_results()
                    elif cmd == 'delete':
                        if args and args[0].isdigit():
                            self.database.delete_page_by_index(int(args[0]))
                        else:
                            print("❌ Usage: delete <page_number>")
                    elif cmd == 'cleanup':
                        confirm = input("⚠️ DELETE ALL PAGES? Type 'DELETE' to confirm: ")
                        if confirm == "DELETE":
                            self.database.cleanup_all_pages()
                        else:
                            print("❌ Cleanup cancelled")
                    elif cmd == 'M':  # 🚨 Handle 'M' command from terminal too
                        print("\n📝 Note: 'M' key is for PyGame visualizer mode")
                        print("💡 Launch visualizer first with 'goto <n>'")
                    else:
                        print(f"❌ Unknown command: {cmd}")
                        print("💡 Type 'main' for full menu or 'help' for mode-specific commands")
                
                else:
                    # ONLINE MODE COMMANDS (unchanged)
                    if cmd == 'scan':
                        self._scan_page()
                    elif cmd == 'tabs':
                        self._list_browser_tabs()
                    elif cmd == 'load':
                        if args and args[0].isdigit():
                            page_num = int(args[0])
                            if self._load_url_from_database_page(page_num):
                                # 🚨 AUTO-TRIGGER PETERBOT PREP AFTER LOADING
                                print("\n🔄 Auto-preparing for PeterBot...")
                                self._toggle_recording_mode_standard()
                        else:
                            print("❌ Usage: load <page_number>")
                    elif cmd == 'switch':
                        if args and args[0].isdigit():
                            self._switch_to_tab(int(args[0]))
                        else:
                            print("❌ Usage: switch <tab_number>")
                    elif cmd == 'online':
                        url = ' '.join(args) if args else None
                        self._switch_to_online_mode(url)
                    elif cmd == 'offline':
                        self.offline_mode = True
                        print("✅ Offline mode active")
                        self._show_mode_specific_menu()
                    elif cmd == 'save':
                        page_name = ' '.join(args) if args else ""
                        self._save_current_page_to_db(page_name)
                    elif cmd == 'pages':
                        self.database.list_saved_pages_with_options()
                    elif cmd == 'goto':
                        if args and args[0].isdigit():
                            page_num = int(args[0])
                            if 0 <= page_num < len(self.database.pages):
                                self.database.current_page_idx = page_num
                                page_data = self.database.get_current_page()
                                if page_data:
                                    self._load_database_page(page_data)
                                    print("\n✅ Page loaded into visualizer")
                                    print("🎮 Use WASD to navigate, M for PeterBot, ESC to return")
                            else:
                                print(f"❌ Invalid page number. Available: 0-{len(self.database.pages)-1}")
                        else:
                            print("❌ Usage: goto <page_number>")
                    elif cmd == 'loadurl':
                        if args and args[0].isdigit():
                            self._load_url_from_database_page(int(args[0]))
                        else:
                            print("❌ Usage: loadurl <page_number>")
                    elif cmd == 'import':
                        self._import_peterbot_results()
                    elif cmd == 'delete':
                        if args and args[0].isdigit():
                            self.database.delete_page_by_index(int(args[0]))
                        else:
                            print("❌ Usage: delete <page_number>")
                    elif cmd == 'cleanup':
                        confirm = input("⚠️ DELETE ALL PAGES? Type 'DELETE' to confirm: ")
                        if confirm == "DELETE":
                            self.database.cleanup_all_pages()
                        else:
                            print("❌ Cleanup cancelled")
                    elif cmd == 'M':
                        print("\n📝 Note: 'M' key is for PyGame visualizer mode")
                        print("💡 Launch visualizer first with 'scan' or 'goto <n>'")
                    else:
                        print(f"❌ Unknown command: {cmd}")
                        print("💡 Type 'main' for full menu or 'help' for mode-specific commands")
                        
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                running = False
            except Exception as e:
                print(f"⚠️ Error: {e}")
        
        self.shutdown()
        
    def shutdown(self):
        """Shutdown application with graceful browser handling"""
        print("\n" + "=" * 60)
        print("🔥 REMOVING SHAVED ELEMENTS FROM DATABASE")
        print("=" * 60)
        
        time.sleep(0.5)
        
        # Try to clean up shaved elements if visualizer was used
        if (hasattr(self, 'visualizer') and 
            hasattr(self.visualizer, 'shaved_elements') and 
            len(self.visualizer.shaved_elements) > 0 and
            self.database.is_active()):
            
            print(f"\n🔪 Deleting {len(self.visualizer.shaved_elements)} shaved elements...")
            
            import glob
            page_files = glob.glob(os.path.join(self.database.site_path, "page_*.json"))
            
            deleted_total = 0
            processed_pages = 0
            
            for page_file in page_files:
                try:
                    with open(page_file, 'r') as f:
                        page_data = json.load(f)
                    
                    if 'coordinate_space' not in page_data:
                        continue
                    
                    original_count = len(page_data['coordinate_space'])
                    
                    shaved_coord_strs = set()
                    for coord in self.visualizer.shaved_elements:
                        coord_str = str(coord).replace(' ', '')
                        clean_coord = coord_str.strip('()')
                        shaved_coord_strs.add(clean_coord)
                        shaved_coord_strs.add(f"({clean_coord})")
                    
                    new_space = {}
                    deleted_from_this_page = 0
                    
                    for coord_str, element_data in page_data['coordinate_space'].items():
                        clean_coord_str = coord_str.strip('()')
                        if (clean_coord_str in shaved_coord_strs or 
                            coord_str in shaved_coord_strs):
                            deleted_from_this_page += 1
                            continue
                        new_space[coord_str] = element_data
                    
                    if deleted_from_this_page > 0:
                        page_data['coordinate_space'] = new_space
                        page_data['total_elements'] = len(new_space)
                        
                        if 'peterbot_paths' in page_data and page_data['peterbot_paths']:
                            new_paths = []
                            for path in page_data['peterbot_paths']:
                                path_has_shaved = False
                                for coord_str in path:
                                    clean_coord_str = coord_str.strip('()')
                                    if (clean_coord_str in shaved_coord_strs or 
                                        coord_str in shaved_coord_strs):
                                        path_has_shaved = True
                                        break
                                if not path_has_shaved:
                                    new_paths.append(path)
                            page_data['peterbot_paths'] = new_paths
                        
                        with open(page_file, 'w') as f:
                            json.dump(page_data, f, indent=2)
                        
                        deleted_total += deleted_from_this_page
                        processed_pages += 1
                        
                        print(f"  ✅ {os.path.basename(page_file)}: Deleted {deleted_from_this_page} elements")
                    
                except Exception as e:
                    print(f"  ❌ Error processing {os.path.basename(page_file)}: {e}")
            
            print(f"\n🔥 TOTAL: Deleted {deleted_total} shaved elements from {processed_pages} pages")
        else:
            print("📭 No shaved elements to delete")
        
        print("\n💾 Closing database...")
        if self.database.is_active():
            self.database._update_metadata()
            print(f"📁 Database: {self.database.current_site}")
        
        # 🚨 GRACEFUL BROWSER HANDLING
        print("\n🌐 Handling browser connection...")
        if hasattr(self, 'driver') and self.driver:
            try:
                # Test if browser is still connected
                final_url = self.driver.current_url
                print(f"✅ Browser still connected: {final_url[:80]}...")
                
                # Ask user what to do with browser
                print("\n📋 Browser options:")
                print("  1) Keep browser open")
                print("  2) Close browser")
                print("  3) Leave as-is (default)")
                
                choice = input("\nSelect option (1-3, Enter=3): ").strip()
                
                if choice == "1":
                    print("🔓 Browser left open for manual use")
                elif choice == "2":
                    self.driver.quit()
                    print("📴 Browser closed")
                else:
                    print("🔓 Browser connection preserved")
                    
            except Exception as e:
                print(f"⚠️ Browser already closed or disconnected: {e}")
        else:
            print("🌐 No active browser connection")
        
        # Clean up PyGame if it was initialized
        print("\n🎮 Cleaning up visualization...")
        if hasattr(self, 'visualizer_initialized') and self.visualizer_initialized:
            if pygame.get_init():
                pygame.quit()
                print("✅ PyGame closed")
            else:
                print("📭 PyGame not active")
        else:
            print("📭 Visualizer not active")
        
        print("\n👋 Session ended gracefully")
        
def main():
    """Main entry point"""
    app = DOMInteractionCaptureApp()
    
    try:
        if app.initialize():
            app.run_interaction_loop()
        app.shutdown()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        app.shutdown()
    except Exception as e:
        print(f"❌ Application error: {e}")
        app.shutdown()

if __name__ == "__main__":
    main()
