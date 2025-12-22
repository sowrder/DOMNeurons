#!/usr/bin/env python3
"""
🕷️ SPIDEY BOT - Ultimate DOM Monitoring Engine
Complete fusion of PeterBot's intelligence with DOMinator's proven coordinate system
100% Venger compatible - Zero semantic changes to PeterBot's monitoring
"""

import threading 
import subprocess
import random
import pygame
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Optional, Any
import hashlib
from selenium.webdriver.common.by import By
import argparse
import sys
import select 
from collections import defaultdict, deque
import math
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
import traceback
from Neurons import *
#Neuron-Axon priori node evolution - Stores Neuron and Axon Objects implementation 
from selenium import webdriver



# ===== PETERBOT'S COMPLETE PATTERN SYSTEM =====
class PatternDetectors:
    """PETERBOT'S PATTERN DETECTION - COMPLETE PRESERVATION"""
    
    @staticmethod
    def is_focus_element(pattern_type):
        """CHECK IF PATTERN TYPE IS A USER INTERACTION FOCUS ELEMENT"""
        focus_patterns = ['DATA_INPUT', 'ACTION_ELEMENT', 'TOGGLE_ELEMENT', 'SELECTION_ELEMENT']
        return pattern_type in focus_patterns
    

    @staticmethod
    def get_propagation_expectations(pattern_type, element_type):
        """Return propagation expectations for a pattern type."""
        expectations = {
            'DATA_INPUT': {
                'expects_nearby': ['STATE_INDICATOR', 'CONTEXT_ELEMENT'],
                'likely_new_nodes': ['validation_message', 'suggestion_box', 'dropdown'],
                'propagation_direction': 'OUTWARD',
                'time_window': 0.5,
                'interaction_flow': 'VALUE_CHANGE -> VALIDATION -> UI_UPDATE'
            },
            'ACTION_ELEMENT': {
                'expects_nearby': ['STATE_INDICATOR', 'CONTEXT_ELEMENT', 'DATA_INPUT'],
                'likely_new_nodes': ['loading_indicator', 'result_display', 'navigation_element'],
                'propagation_direction': 'BIDIRECTIONAL',
                'time_window': 1.0,
                'interaction_flow': 'CLICK -> LOADING -> CONTENT_UPDATE'
            },
            'STATE_INDICATOR': {
                'expects_nearby': ['DATA_INPUT', 'ACTION_ELEMENT'],
                'likely_new_nodes': [],
                'propagation_direction': 'REACTIVE',
                'time_window': 0.3,
                'interaction_flow': 'SOURCE_CHANGE -> INDICATOR_UPDATE'
            },
            'CONTEXT_ELEMENT': {
                'expects_nearby': ['DATA_INPUT', 'ACTION_ELEMENT'],
                'likely_new_nodes': [],
                'propagation_direction': 'STATIC_OR_REACTIVE',
                'time_window': 0.4,
                'interaction_flow': 'RELATED_CHANGE -> CONTEXT_UPDATE'
            }
        }
        
        base_expectation = expectations.get(pattern_type, {
            'expects_nearby': ['ANY'],
            'likely_new_nodes': [],
            'propagation_direction': 'UNKNOWN',
            'time_window': 0.3,
            'interaction_flow': 'UNKNOWN'
        })
        
        # Element-type specific adjustments
        if element_type == 'input':
            if pattern_type == 'DATA_INPUT':
                base_expectation['likely_new_nodes'].extend(['autocomplete', 'password_toggle'])
        elif element_type == 'button':
            if pattern_type == 'ACTION_ELEMENT':
                base_expectation['likely_new_nodes'].extend(['tooltip', 'confirmation'])
        
        return base_expectation
    
    @staticmethod
    def get_all_focus_patterns():
        """RETURN ALL PATTERNS THAT ARE USER FOCUS ELEMENTS"""
        return ['DATA_INPUT', 'ACTION_ELEMENT', 'TOGGLE_ELEMENT', 'SELECTION_ELEMENT']
    
    @staticmethod  
    def get_all_response_patterns():
        """RETURN ALL PATTERNS THAT ARE SYSTEM RESPONSE ELEMENTS"""
        return ['STATE_INDICATOR', 'CONTEXT_ELEMENT', 'RESULT_CONTAINER', 'NAVIGATION_ELEMENT']
    
    @staticmethod
    def get_focus_priority(pattern_type):
        """PRIORITY ORDER FOR MONITORING FREQUENCY"""
        priority_map = {
            'DATA_INPUT': 10,       # User typing - highest priority
            'ACTION_ELEMENT': 9,    # User clicked
            'TOGGLE_ELEMENT': 8,    # User toggled
            'SELECTION_ELEMENT': 7, # User selected
            'STATE_INDICATOR': 3,   # System feedback
            'CONTEXT_ELEMENT': 2,   # Context update
            'RESULT_CONTAINER': 2,  # Results display
            'NAVIGATION_ELEMENT': 2,# Navigation change
            'UNKNOWN': 1
        }
        return priority_map.get(pattern_type, 1)
    
    @staticmethod
    def get_expected_response_for_focus(focus_pattern):
        """WHAT RESPONSE PATTERNS EACH FOCUS PATTERN EXPECTS"""
        expectations = {
            'DATA_INPUT': ['STATE_INDICATOR', 'CONTEXT_ELEMENT', 'SUGGESTION_LIST'],
            'ACTION_ELEMENT': ['STATE_INDICATOR', 'RESULT_CONTAINER', 'NAVIGATION_ELEMENT'],
            'TOGGLE_ELEMENT': ['CONTEXT_ELEMENT', 'DEPENDENT_SECTION'],
            'SELECTION_ELEMENT': ['STATE_INDICATOR', 'DEPENDENT_FIELDS']
        }
        return expectations.get(focus_pattern, [])
    
    @staticmethod
    def detect_unison_pattern(node_change, neighbor_change, my_patterns, their_patterns, my_type, their_type):
        """Detect specific unison interaction patterns."""
        # Time-based unison already checked by caller
        
        # Pattern: Input with immediate validation
        if ('DATA_INPUT' in my_patterns and 
            'STATE_INDICATOR' in their_patterns and
            'validation' in str(neighbor_change.get('debug_info', '')).lower()):
            return 'INPUT_VALIDATION_FLOW'
        
        # Pattern: Button click with loading state
        if ('ACTION_ELEMENT' in my_patterns and
            any(term in str(neighbor_change.get('debug_info', '')).lower() 
                for term in ['loading', 'spinner', 'progress'])):
            return 'ACTION_LOADING_FLOW'
        
        # Pattern: Input change with suggestion dropdown
        if ('DATA_INPUT' in my_patterns and
            their_type in ['div', 'ul', 'datalist'] and
            any(term in str(neighbor_change.get('text', '')).lower()
                for term in ['suggest', 'option', 'list'])):
            return 'INPUT_SUGGESTION_FLOW'
        
        # Pattern: Checkbox/radio with label update
        if (my_type in ['checkbox', 'radio'] and
            'CONTEXT_ELEMENT' in their_patterns and
            'checked' in str(node_change.get('debug_info', '')).lower()):
            return 'TOGGLE_LABEL_FLOW'
        
        # Generic pattern based on relationship
        if 'DATA_INPUT' in my_patterns and 'CONTEXT_ELEMENT' in their_patterns:
            return 'INPUT_CONTEXT_SYNC'
        
        if 'ACTION_ELEMENT' in my_patterns and 'STATE_INDICATOR' in their_patterns:
            return 'ACTION_FEEDBACK_SYNC'
        
        return None

    @staticmethod
    def detect_action_element(branch_tuple, element_data, parent_data, siblings, coordinate_space):
        """ACTION_ELEMENT DETECTION - COMPLETE"""
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
        """DATA_INPUT DETECTION - COMPLETE"""
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
        """CONTEXT_ELEMENT DETECTION - COMPLETE"""
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
        """STATE_INDICATOR DETECTION - COMPLETE"""
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
        """CHILD BRANCHES FOR PATTERN ANALYSIS - COMPLETE"""
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



# ===== ADD TO YOUR NEURON-AXON MODULE =====

# Add TimingController class
class TimingController:
    """Simple timing controller for neuron observation intervals"""
    
    @staticmethod
    def get_interval_for_pattern(pattern, is_active=False, has_sync_partner=False):
        """Get observation interval based on pattern"""
        intervals = {
            'DATA_INPUT': 0.1,           # 100ms - rapid typing
            'ACTION_ELEMENT': 0.2,       # 200ms - click responses
            'TOGGLE_ELEMENT': 0.3,       # 300ms - state changes
            'SELECTION_ELEMENT': 0.3,    # 300ms - selection changes
            'STATE_INDICATOR': 0.5,      # 500ms - validation feedback
            'CONTEXT_ELEMENT': 0.5,      # 500ms - context updates
            'DYNAMIC_CONTAINER': 0.05,   # 50ms - rapid content generation
            'STRUCTURAL': 2.0,           # 2s - static elements
        }
        return intervals.get(pattern, 2.0)

# ===== UPDATED COSMIC BACKGROUND =====
class CosmicBackground:
    """DEEP SPACE BACKGROUND WITH SPIDERBOT THEME"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # SpiderBot color scheme - dark with white accents
        self.star_colors = [
            (255, 255, 255),    # Pure white
            (230, 230, 230),    # Light gray
            (220, 220, 255),    # Subtle blue-white
        ]
        
        # Subtle nebula effects in dark colors
        self.nebula_colors = [
            (30, 15, 40, 20),   # Deep purple
            (15, 25, 40, 15),   # Deep blue
            (40, 10, 30, 10),   # Dark magenta
        ]
        
        # Generate stars
        self.stars = []
        self._generate_starfield(250)
        
        # Nebula clouds
        self.nebulas = []
        self._generate_nebulas(4)
        
        # Particle effects
        self.particles = []
    
    def _generate_starfield(self, num_stars: int):
        """CREATE STARFIELD"""
        for _ in range(num_stars):
            self.stars.append({
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'size': random.uniform(0.2, 1.5),
                'speed': random.uniform(0.1, 1.5),
                'brightness': random.uniform(0.3, 0.9),
                'color': random.choice(self.star_colors),
                'frequency': random.uniform(0.5, 2.5),
                'phase': random.uniform(0, math.pi * 2),
            })
    
    def _generate_nebulas(self, num_nebulas: int):
        """CREATE SUBTLE NEBULA CLOUDS"""
        for _ in range(num_nebulas):
            nebula = {
                'x': random.randint(-100, self.screen_width + 100),
                'y': random.randint(-100, self.screen_height + 100),
                'width': random.randint(150, 300),
                'height': random.randint(100, 250),
                'color': random.choice(self.nebula_colors),
                'speed_x': random.uniform(-0.05, 0.05),
                'speed_y': random.uniform(-0.05, 0.05),
                'rotation': random.uniform(0, math.pi * 2),
                'rotation_speed': random.uniform(-0.0005, 0.0005),
            }
            self.nebulas.append(nebula)
    
    def update(self):
        """UPDATE STAR PULSES AND NEBULA MOVEMENT"""
        current_time = pygame.time.get_ticks() * 0.001
        
        # Update nebula positions
        for nebula in self.nebulas:
            nebula['x'] += nebula['speed_x']
            nebula['y'] += nebula['speed_y']
            nebula['rotation'] += nebula['rotation_speed']
            
            # Wrap around screen
            if nebula['x'] < -300:
                nebula['x'] = self.screen_width + 300
            elif nebula['x'] > self.screen_width + 300:
                nebula['x'] = -300
            if nebula['y'] < -300:
                nebula['y'] = self.screen_height + 300
            elif nebula['y'] > self.screen_height + 300:
                nebula['y'] = -300
    
    def draw(self, screen):
        """DRAW THE COSMIC BACKGROUND"""
        # Draw deep space background - BLACK with no blue
        screen.fill((0, 0, 0))
        
        # Draw nebulas
        for nebula in self.nebulas:
            nebula_surface = pygame.Surface((nebula['width'], nebula['height']), pygame.SRCALPHA)
            r, g, b, a = nebula['color']
            pygame.draw.ellipse(nebula_surface, (r, g, b, a), 
                              (0, 0, nebula['width'], nebula['height']))
            
            rotated = pygame.transform.rotate(nebula_surface, math.degrees(nebula['rotation']))
            screen.blit(rotated, 
                       (nebula['x'] - rotated.get_width() // 2,
                        nebula['y'] - rotated.get_height() // 2))
        
        # Draw stars
        current_time = pygame.time.get_ticks() * 0.001
        for star in self.stars:
            pulse = 0.5 + 0.5 * math.sin(current_time * star['frequency'] + star['phase'])
            brightness = star['brightness'] * pulse
            
            r, g, b = star['color']
            final_color = (
                int(r * brightness),
                int(g * brightness),
                int(b * brightness)
            )
            
            pygame.draw.circle(screen, final_color, 
                             (int(star['x']), int(star['y'])), 
                             star['size'])
        
        # Draw particles
        for particle in self.particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
                continue
            
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            particle['size'] *= 0.95
            
            alpha = int(255 * (particle['life'] / particle['max_life']))
            particle_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*particle['color'], alpha),
                             (int(particle['size']), int(particle['size'])), 
                             int(particle['size']))
            screen.blit(particle_surface, 
                       (int(particle['x'] - particle['size']), 
                        int(particle['y'] - particle['size'])))
    
    def add_particles(self, x: float, y: float, count: int = 10, color: Tuple[int, int, int] = (255, 100, 100)):
        """ADD PARTICLES"""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            self.particles.append({
                'x': x,
                'y': y,
                'speed_x': math.cos(angle) * speed,
                'speed_y': math.sin(angle) * speed,
                'size': random.uniform(1, 3),
                'color': color,
                'life': random.randint(20, 40),
                'max_life': 40
            })

# ===== ELEGANT CELESTIAL ORB WITH BRANCHES =====
class ConstellationWhale:
    """CELESTIAL ORB WITH BRANCHES - FAST & BLUEISH GLOW"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Simple time tracking
        self.current_time = 0.0
        
        # Simple geometry - main orb
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.radius = 40
        
        # Faster movement
        self.speed_x = random.uniform(-0.6, 0.6)
        self.speed_y = random.uniform(-0.6, 0.6)
        
        # Animation states
        self.pulse_phase = 0
        self.rotation = 0
        
        # More orbiting points (branches) - increased from 3 to 8
        self.orbit_points = 8
        self.orbit_distance = 80  # Increased from 60
        self.orbit_speeds = [random.uniform(1.0, 1.8) for _ in range(self.orbit_points)]  # Faster
        
        # Subtle blueish color palette
        self.blueish_colors = [
            (220, 230, 255),  # Light blue-white
            (200, 220, 255),  # Soft blue
            (180, 210, 255),  # Blue tint
        ]
    
    def update(self):
        """FASTER UPDATE"""
        # Update time
        self.current_time += 0.016  # ~60 FPS
        
        # Faster floating
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Bounce off edges (faster response)
        margin = 80  # Smaller margin for more movement
        if self.x < margin or self.x > self.screen_width - margin:
            self.speed_x *= -1.1  # More bounce
            self.x = max(margin, min(self.x, self.screen_width - margin))
        
        if self.y < margin or self.y > self.screen_height - margin:
            self.speed_y *= -1.1  # More bounce
            self.y = max(margin, min(self.y, self.screen_height - margin))
        
        # Faster pulse and rotation
        self.pulse_phase += 0.05  # Increased from 0.03
        self.rotation += 0.01  # Increased from 0.005
    
    def draw(self, screen):
        """DRAW WITH BLUEISH GLOW AND BRANCHES"""
        # Draw main orb with faster pulse
        pulse = 0.8 + 0.2 * math.sin(self.pulse_phase * 1.5)  # Faster pulse
        current_radius = self.radius * pulse
        
        # Main orb glow (blueish)
        glow_size = current_radius * 1.8  # Larger glow
        glow_surface = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (180, 200, 255, 50),  # Blueish glow
                         (int(glow_size), int(glow_size)), int(glow_size))
        screen.blit(glow_surface, (int(self.x - glow_size), int(self.y - glow_size)))
        
        # Secondary outer glow (very subtle)
        outer_glow = pygame.Surface((int(glow_size * 2.5), int(glow_size * 2.5)), pygame.SRCALPHA)
        pygame.draw.circle(outer_glow, (150, 180, 255, 20),
                         (int(glow_size * 1.25), int(glow_size * 1.25)), int(glow_size * 1.25))
        screen.blit(outer_glow, (int(self.x - glow_size * 1.25), int(self.y - glow_size * 1.25)))
        
        # Main orb (blueish white)
        main_color = self.blueish_colors[0]
        pygame.draw.circle(screen, main_color, 
                         (int(self.x), int(self.y)), int(current_radius))
        
        # Orb highlight (subtle blue)
        highlight_size = current_radius * 0.4
        highlight_x = self.x - current_radius * 0.3
        highlight_y = self.y - current_radius * 0.3
        pygame.draw.circle(screen, (240, 245, 255, 200),  # Very light blue
                         (int(highlight_x), int(highlight_y)), int(highlight_size))
        
        # Draw orbiting points (more branches, faster)
        for i in range(self.orbit_points):
            angle = self.rotation * self.orbit_speeds[i] + i * (2 * math.pi / self.orbit_points)
            
            # Vary distances for more interesting pattern
            base_distance = self.orbit_distance * (0.8 + 0.4 * math.sin(self.pulse_phase * 0.8 + i * 0.5))
            distance = base_distance * (1.0 + 0.2 * math.sin(self.current_time * 1.2 + i * 0.3))
            
            orbit_x = self.x + math.cos(angle) * distance
            orbit_y = self.y + math.sin(angle) * distance
            
            # Orbit point with faster pulse
            orbit_pulse = 0.5 + 0.5 * math.sin(self.pulse_phase * 2.0 + i)  # Faster
            orbit_size = 4 + orbit_pulse * 3  # Slightly larger
            
            # Draw connection line (blueish, some longer than others)
            line_length = distance * (0.3 + 0.7 * math.sin(self.pulse_phase * 0.5 + i))
            line_end_x = self.x + math.cos(angle) * line_length
            line_end_y = self.y + math.sin(angle) * line_length
            
            line_alpha = int(60 + 60 * math.sin(self.pulse_phase * 1.2 + i))
            line_color = (200, 220, 255, line_alpha)  # Blueish
            
            # Thicker lines for some branches
            line_width = 1 + int(orbit_pulse * 1.5)
            pygame.draw.line(screen, line_color,
                           (int(self.x), int(self.y)),
                           (int(line_end_x), int(line_end_y)), line_width)
            
            # Draw extended line to orbit point (thinner)
            if line_length < distance:
                pygame.draw.line(screen, (200, 220, 255, line_alpha // 2),
                               (int(line_end_x), int(line_end_y)),
                               (int(orbit_x), int(orbit_y)), 1)
            
            # Orbit point (choose color from palette based on position)
            point_color_idx = i % len(self.blueish_colors)
            point_color = self.blueish_colors[point_color_idx]
            
            # Add slight color variation based on pulse
            r, g, b = point_color
            pulse_factor = 0.8 + 0.2 * orbit_pulse
            final_color = (
                int(r * pulse_factor),
                int(g * pulse_factor),
                int(b * pulse_factor)
            )
            
            pygame.draw.circle(screen, final_color,
                             (int(orbit_x), int(orbit_y)), int(orbit_size))
            
            # Glow on orbit points
            point_glow = pygame.Surface((int(orbit_size * 2.5), int(orbit_size * 2.5)), pygame.SRCALPHA)
            glow_alpha = int(40 + 30 * orbit_pulse)
            pygame.draw.circle(point_glow, (180, 200, 255, glow_alpha),
                             (int(orbit_size * 1.25), int(orbit_size * 1.25)), 
                             int(orbit_size * 1.25))
            screen.blit(point_glow, 
                       (int(orbit_x - orbit_size * 1.25), int(orbit_y - orbit_size * 1.25)))
            
            # Tiny secondary points on some branches (extra detail)
            if i % 3 == 0:  # Every 3rd branch gets a secondary point
                secondary_angle = angle + math.pi/6  # Offset angle
                secondary_distance = distance * 0.6
                secondary_x = self.x + math.cos(secondary_angle) * secondary_distance
                secondary_y = self.y + math.sin(secondary_angle) * secondary_distance
                
                secondary_size = 2 + orbit_pulse * 1.5
                pygame.draw.circle(screen, (230, 240, 255),
                                 (int(secondary_x), int(secondary_y)), int(secondary_size))
        
        # More trail particles for faster movement
        if int(self.current_time * 40) % 3 == 0:  # More frequent
            for _ in range(2):  # 2 particles at a time
                trail_angle = random.uniform(0, math.pi * 2)
                trail_distance = random.uniform(self.radius * 0.5, self.radius * 1.5)
                trail_x = self.x + math.cos(trail_angle) * trail_distance
                trail_y = self.y + math.sin(trail_angle) * trail_distance
                
                trail_size = random.uniform(1, 3)
                trail_alpha = random.randint(40, 100)
                trail_surface = pygame.Surface((int(trail_size * 2), int(trail_size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (180, 200, 255, trail_alpha),
                                 (int(trail_size), int(trail_size)), int(trail_size))
                screen.blit(trail_surface, 
                           (int(trail_x - trail_size), int(trail_y - trail_size)))
                

# ===== UNIFIED SPIDEY COORDINATE SELECTOR =====
class SpideyCoordinateSelector:
    """🕸️ UNIFIED INTERFACE - Selection AND Confirmation in one screen"""
    
    MODE_SELECTION = "selection"
    MODE_CONFIRMATION = "confirmation"
    
    def __init__(self, coordinate_space, selected_coords=None, screen_width=1200, screen_height=800):
        self.coordinate_space = coordinate_space
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Mode state
        self.mode = self.MODE_SELECTION
        
        # Selection state - shared across modes
        if selected_coords:
            self.selected_coordinates = set(selected_coords)
            self.confirmed_coordinates = set(selected_coords)  # Start with all selected confirmed
        else:
            self.selected_coordinates = set()
            self.confirmed_coordinates = set()
        
        # Display coordinates (mode-specific)
        self.selection_display_coords = set()  # For selection mode (grid)
        self.confirmation_display_coords = set()  # For confirmation mode (tree)
        self._update_display_coordinates()
        
        # Hover and drag state
        self.hovered_coordinate = None
        self.drag_start_pos = None
        self.drag_current_pos = None
        self.dragging_selection = False
        self.drag_selected_coords = set()
        self.last_drag_update = 0
        
        # Navigation state (shared across modes)
        self.pan_x, self.pan_y = 0, 0
        self.zoom = 1.0
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        
        # Tree layout for confirmation mode
        self.coord_positions = {}  # Will be calculated when in confirmation mode
        
        # Initialize PyGame
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("🕸️ SPIDERBOT - Unified Coordinate Interface")
        
        # ===== SHARED COLOR SCHEME =====
        self.BG_COLOR = (0, 0, 0)  # Pure black
        self.TEXT_COLOR = (220, 220, 220)  # Light gray text
        self.PANEL_BG = (20, 20, 30, 220)  # Dark transparent panels
        
        # Selection colors (shared)
        self.SELECTION_COLOR = (255, 200, 50)  # Gold for selection
        self.HOVER_COLOR = (255, 100, 100)  # Red for hover
        self.DRAG_RECT_COLOR = (255, 200, 50, 80)
        self.DRAG_HIGHLIGHT = (255, 200, 50, 120)
        
        # Mode-specific colors
        self.GRID_COLOR = (100, 100, 100)  # Gray grid lines (selection mode)
        self.AXIS_COLOR = (150, 150, 150)  # Light gray axes (selection mode)
        self.PATH_COLOR = (150, 150, 200)  # Light purple for paths (confirmation mode)
        self.ROOT_COLOR = (255, 200, 50)  # Gold for root (confirmation mode)
        self.UNCONFIRMED_COLOR = (255, 100, 100)  # Red for unconfirmed (confirmation mode)
        
        # Hover path colors
        self.HOVER_PATH_COLOR = (180, 40, 60)  # Maroon/Red base
        self.HOVER_PATH_GLOW = (255, 80, 80, 100)  # Red glow
        
        # Pattern colors (visible on legend - shared)
        self.PATTERN_COLORS = {
            'ACTION_ELEMENT': ((255, 100, 50), (255, 180, 80), (255, 120, 70)),     # Orange
            'DATA_INPUT': ((50, 180, 255), (100, 220, 255), (70, 200, 255)),        # Blue
            'CONTEXT_ELEMENT': ((50, 220, 180), (100, 240, 220), (70, 230, 200)),   # Teal
            'STATE_INDICATOR': ((200, 80, 255), (220, 120, 255), (210, 100, 255)),  # Purple
            'INTERACTIVE': ((255, 180, 50), (255, 220, 100), (255, 200, 75)),       # Yellow
            'STRUCTURAL': ((100, 150, 220), (140, 190, 255), (120, 170, 240)),      # Light Blue
            'CONTENT': ((180, 100, 220), (220, 140, 255), (200, 120, 240)),         # Lavender
            'FORM_FIELD': ((80, 200, 220), (120, 240, 255), (100, 220, 240)),       # Teal
            'FORM_SUBMIT': ((255, 120, 80), (255, 160, 120), (255, 140, 100)),      # Orange-Red
            'NAV_LINK': ((80, 220, 120), (120, 255, 160), (100, 240, 140)),         # Green
            'UNKNOWN': ((150, 150, 180), (180, 180, 210), (165, 165, 195)),         # Gray
        }
        
        # Fonts (shared)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 32)
        self.bold_font = pygame.font.Font(None, 28)
        
        # Layout (mode-specific defaults)
        self.cell_size = 25  # For selection mode grid
        self.row_height = 40  # For confirmation mode tree
        
        # Cosmic elements (shared)
        self.cosmic_bg = CosmicBackground(screen_width, screen_height)
        self.constellation_whale = ConstellationWhale(screen_width, screen_height)
        
        # Performance
        self.last_draw_time = 0
        self.draw_fps = 60
        
        print(f"🕸️ Unified SpiderBot Interface initialized in {self.mode} mode")
    
    def _update_display_coordinates(self):
        """Update display coordinates based on current mode."""
        if self.mode == self.MODE_SELECTION:
            # Selection mode shows all coordinates
            self.selection_display_coords = set(self.coordinate_space.keys())
        else:  # MODE_CONFIRMATION
            # Confirmation mode shows selected + paths to root
            self.confirmation_display_coords = set()
            for coord in self.selected_coordinates:
                current = coord
                while True:
                    self.confirmation_display_coords.add(current)
                    if len(current) <= 1:
                        break
                    current = current[:-1]
            
            # Recalculate tree layout
            self.coord_positions = self._calculate_tree_layout()
    def switch_mode(self, direction="right"):
        """Switch between selection and confirmation modes."""
        old_mode = self.mode
        self.mode = self.MODE_CONFIRMATION if self.mode == self.MODE_SELECTION else self.MODE_SELECTION
        
        # 🔥 CRITICAL FIX: When switching TO confirmation mode, 
        # ALL selected coordinates should be confirmed by default
        if old_mode == self.MODE_SELECTION and self.mode == self.MODE_CONFIRMATION:
            # Copy all selected coordinates to confirmed
            self.confirmed_coordinates = set(self.selected_coordinates)
            print(f"✅ Auto-confirmed {len(self.selected_coordinates)} selected coordinates")
        
        # Update display coordinates for new mode
        self._update_display_coordinates()
        
        # Reset interactive states
        self.hovered_coordinate = None
        self.dragging_selection = False
        self.drag_start_pos = None
        self.drag_current_pos = None
        self.drag_selected_coords.clear()
        
        print(f"🔄 Switched from {old_mode} to {self.mode} mode")
        print(f"   Selected: {len(self.selected_coordinates)} coordinates")
        print(f"   Confirmed: {len(self.confirmed_coordinates)} coordinates")
        
    # ===== SHARED COORDINATE METHODS =====
    
    def _coord_to_screen(self, coord, center_x=None, center_y=None):
        """Convert coordinate to screen position based on current mode."""
        if not coord:
            return None
        
        if self.mode == self.MODE_SELECTION:
            # Grid-based positioning
            if center_x is None:
                center_x = self.screen_width // 2 + self.pan_x
            if center_y is None:
                center_y = self.screen_height // 2 + self.pan_y
            
            depth = len(coord)
            sibling_index = coord[-1] if coord else 0
            
            x = center_x + int(sibling_index * self.cell_size * self.zoom)
            y = center_y + int(depth * self.cell_size * self.zoom)
            
            if (50 <= x <= self.screen_width - 50 and 100 <= y <= self.screen_height - 150):
                return (int(x), int(y))
        
        else:  # MODE_CONFIRMATION
            # Tree-based positioning from pre-calculated layout
            if coord in self.coord_positions:
                pos = self.coord_positions[coord]
                # Apply pan/zoom to tree layout
                x = pos[0] + self.pan_x
                y = pos[1] + self.pan_y
                return (int(x), int(y))
        
        return None
    
    def _find_coordinate_at_position(self, mouse_pos):
        """Find coordinate at mouse position (mode-aware)."""
        if self.mode == self.MODE_SELECTION:
            center_x = self.screen_width // 2 + self.pan_x
            center_y = self.screen_height // 2 + self.pan_y
            
            closest_dist = 20
            closest_coord = None
            
            for coord in self.selection_display_coords:
                screen_pos = self._coord_to_screen(coord, center_x, center_y)
                if screen_pos:
                    dist = math.sqrt((screen_pos[0] - mouse_pos[0])**2 + 
                                   (screen_pos[1] - mouse_pos[1])**2)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_coord = coord
            
            return closest_coord
        
        else:  # MODE_CONFIRMATION
            closest_dist = 20
            closest_coord = None
            
            for coord, pos in self.coord_positions.items():
                screen_pos = self._coord_to_screen(coord)
                if screen_pos:
                    dist = math.sqrt((screen_pos[0] - mouse_pos[0])**2 + 
                                   (screen_pos[1] - mouse_pos[1])**2)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_coord = coord
            
            return closest_coord
    
    # ===== SHARED DRAWING METHODS =====
    
    def _draw_background(self):
        """Draw cosmic background (shared)."""
        self.cosmic_bg.update()
        self.constellation_whale.update()
        self.cosmic_bg.draw(self.screen)
        self.constellation_whale.draw(self.screen)
    
    def _draw_coordinate_node(self, coord, is_in_current_display=True):
        """Draw a coordinate node (mode-aware)."""
        screen_pos = self._coord_to_screen(coord)
        if not screen_pos or not is_in_current_display:
            return
        
        node_data = self.coordinate_space.get(coord, {})
        
        # Determine state
        in_drag_selection = coord in self.drag_selected_coords
        is_selected = coord in self.selected_coordinates
        is_hovered = coord == self.hovered_coordinate
        is_confirmed = coord in self.confirmed_coordinates
        
        # Get color based on pattern
        patterns = node_data.get('pattern_roles', [])
        structural_role = node_data.get('structural_role', 'UNKNOWN')
        
        # Get the appropriate color tuple
        color_tuple = self.PATTERN_COLORS['UNKNOWN']
        for pattern in patterns:
            if pattern in self.PATTERN_COLORS:
                color_tuple = self.PATTERN_COLORS[pattern]
                break
        if color_tuple == self.PATTERN_COLORS['UNKNOWN'] and structural_role in self.PATTERN_COLORS:
            color_tuple = self.PATTERN_COLORS[structural_role]
        
        # Choose color and size based on mode and state
        if self.mode == self.MODE_SELECTION:
            if is_selected:
                color = color_tuple[1]  # Selected color
                base_size = 8
                # Gold glow for selection
                for glow_size in [12, 9, 6]:
                    glow_alpha = int(150 * (1 - (glow_size - 6) / 6))
                    glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (*self.SELECTION_COLOR, glow_alpha),
                                     (glow_size, glow_size), glow_size)
                    self.screen.blit(glow_surface, (screen_pos[0] - glow_size, screen_pos[1] - glow_size))
            elif in_drag_selection:
                color = self.DRAG_HIGHLIGHT[:3]
                base_size = 7
                drag_surface = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.circle(drag_surface, self.DRAG_HIGHLIGHT,
                                 (7, 7), 7)
                self.screen.blit(drag_surface, (screen_pos[0] - 7, screen_pos[1] - 7))
            elif is_hovered:
                color = self.HOVER_COLOR  # Red for hover
                base_size = 7
                hover_surface = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.circle(hover_surface, (*self.HOVER_COLOR, 120),
                                 (7, 7), 7)
                self.screen.blit(hover_surface, (screen_pos[0] - 7, screen_pos[1] - 7))
            else:
                color = color_tuple[0]  # Normal color
                base_size = 6
        
        else:  # MODE_CONFIRMATION
            if coord == (0,):
                color = self.ROOT_COLOR
                base_size = 10
                label = "R"
            elif is_selected:
                if is_confirmed:
                    color = color_tuple[1]  # Selected color
                    label = "✓"
                else:
                    color = self.UNCONFIRMED_COLOR
                    label = "?"
                base_size = 8
            else:
                color = self.PATH_COLOR
                base_size = 6
                label = str(coord[-1]) if coord else "0"
            
            # Draw label for confirmation mode
            label_surface = self.small_font.render(label, True, (255, 255, 255))
            label_rect = label_surface.get_rect(center=screen_pos)
            self.screen.blit(label_surface, label_rect)
        
        # Draw the node
        pygame.draw.circle(self.screen, color, screen_pos, base_size)
        pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, base_size, 1)
        
        # Pattern indicator (small dot for selection mode)
        if patterns and self.mode == self.MODE_SELECTION:
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, 2)
    
    def _draw_hover_path(self):
        """Draw glowing path from root to hovered coordinate."""
        if not self.hovered_coordinate:
            return
        
        if self.mode == self.MODE_SELECTION:
            # Get path from root (grid-based)
            path = []
            current = self.hovered_coordinate
            while True:
                path.insert(0, current)
                if len(current) <= 1:
                    break
                current = current[:-1]
            
            # Single pulse for entire path
            pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.01)
            
            for i in range(len(path) - 1):
                start_coord = path[i]
                end_coord = path[i + 1]
                
                start_pos = self._coord_to_screen(start_coord)
                end_pos = self._coord_to_screen(end_coord)
                
                if start_pos and end_pos:
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    length = max(1, math.sqrt(dx*dx + dy*dy))
                    angle = math.atan2(dy, dx)
                    
                    # Draw glow
                    glow_width = int(length)
                    glow_height = 8
                    glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
                    
                    pygame.draw.line(glow_surface, (255, 150, 150, int(200 * pulse)),
                                   (0, glow_height//2), (glow_width, glow_height//2), 4)
                    pygame.draw.line(glow_surface, (255, 100, 100, int(100 * pulse)),
                                   (0, glow_height//2), (glow_width, glow_height//2), 8)
                    
                    rotated = pygame.transform.rotate(glow_surface, math.degrees(-angle))
                    rotated_rect = rotated.get_rect()
                    rotated_rect.center = (
                        start_pos[0] + dx * 0.5,
                        start_pos[1] + dy * 0.5
                    )
                    
                    self.screen.blit(rotated, rotated_rect)
                    
                    # Solid line
                    pygame.draw.line(self.screen, (220, 60, 80),
                                   start_pos, end_pos, 3)
                    
                    # Clean arrow
                    arrow_x = start_pos[0] + dx * 0.6
                    arrow_y = start_pos[1] + dy * 0.6
                    
                    arrow_text = ">"
                    arrow_surface = self.small_font.render(arrow_text, True, (255, 200, 200, int(255 * pulse)))
                    arrow_rotated = pygame.transform.rotate(arrow_surface, math.degrees(-angle) + 90)
                    arrow_rect = arrow_rotated.get_rect(center=(int(arrow_x), int(arrow_y)))
                    self.screen.blit(arrow_rotated, arrow_rect)
        
        else:  # MODE_CONFIRMATION
            # Similar logic but for tree layout
            if self.hovered_coordinate not in self.coord_positions:
                return
            
            path = []
            current = self.hovered_coordinate
            while True:
                if current in self.coord_positions:
                    path.insert(0, current)
                if len(current) <= 1:
                    break
                current = current[:-1]
            
            pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.01)
            
            for i in range(len(path) - 1):
                start_coord = path[i]
                end_coord = path[i + 1]
                
                if start_coord in self.coord_positions and end_coord in self.coord_positions:
                    start_pos = self.coord_positions[start_coord]
                    end_pos = self.coord_positions[end_coord]
                    
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    length = max(1, math.sqrt(dx*dx + dy*dy))
                    angle = math.atan2(dy, dx)
                    
                    # Apply pan/zoom
                    start_screen = self._coord_to_screen(start_coord)
                    end_screen = self._coord_to_screen(end_coord)
                    
                    if start_screen and end_screen:
                        pygame.draw.line(self.screen, (220, 60, 80),
                                       start_screen, end_screen, 3)
    
    def _draw_legend(self):
        """Draw unified legend showing mode and status."""
        legend_width = 320 if self.mode == self.MODE_SELECTION else 250
        legend_height = 260 if self.mode == self.MODE_SELECTION else 180
        legend_x = self.screen_width - legend_width - 20
        legend_y = 20
        
        # Legend background
        legend_rect = pygame.Rect(legend_x, legend_y, legend_width, legend_height)
        legend_surface = pygame.Surface((legend_rect.width, legend_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(legend_surface, self.PANEL_BG, legend_surface.get_rect(), border_radius=8)
        pygame.draw.rect(legend_surface, (100, 100, 120, 200), legend_surface.get_rect(), 2, border_radius=8)
        self.screen.blit(legend_surface, legend_rect)
        
        y_offset = legend_y + 15
        
        # Mode indicator
        mode_text = "SELECTION MODE" if self.mode == self.MODE_SELECTION else "CONFIRMATION MODE"
        mode_color = (100, 255, 100) if self.mode == self.MODE_SELECTION else (255, 200, 50)
        mode_surface = self.font.render(mode_text, True, mode_color)
        self.screen.blit(mode_surface, (legend_x + 15, y_offset))
        y_offset += 30
        
        # Statistics
        stats_text = f"Selected: {len(self.selected_coordinates)}"
        if self.mode == self.MODE_CONFIRMATION:
            stats_text += f" | Confirmed: {len(self.confirmed_coordinates)}"
        stats_surface = self.small_font.render(stats_text, True, (200, 220, 255))
        self.screen.blit(stats_surface, (legend_x + 15, y_offset))
        y_offset += 25
        
        if self.mode == self.MODE_SELECTION:
            # Pattern colors legend
            title = self.font.render("PATTERN COLORS", True, (255, 255, 180))
            self.screen.blit(title, (legend_x + 15, y_offset))
            y_offset += 35
            
            patterns = [
                ('Action', (255, 100, 50)),
                ('Input', (50, 180, 255)),
                ('Context', (50, 220, 180)),
                ('State', (200, 80, 255)),
                ('Interactive', (255, 180, 50)),
                ('Structural', (100, 150, 220)),
                ('Content', (180, 100, 220)),
                ('Navigation', (80, 220, 120)),
            ]
            
            col1_x = legend_x + 15
            col2_x = legend_x + 160
            row_height = 22
            
            for i, (name, color) in enumerate(patterns):
                col_x = col1_x if i % 2 == 0 else col2_x
                row_y = y_offset + (i // 2) * row_height
                
                pygame.draw.rect(self.screen, color, (col_x, row_y, 10, 10))
                pygame.draw.rect(self.screen, (255, 255, 255), (col_x, row_y, 10, 10), 1)
                
                name_surface = self.small_font.render(name, True, self.TEXT_COLOR)
                self.screen.blit(name_surface, (col_x + 15, row_y - 2))
            
            y_offset += (len(patterns) // 2) * row_height + 10
            
            states_title = self.small_font.render("STATES", True, (255, 255, 180))
            self.screen.blit(states_title, (legend_x + 15, y_offset))
            y_offset += 15
            
            states = [
                ('Normal', (200, 200, 200)),
                ('Selected', self.SELECTION_COLOR),
                ('Hover', self.HOVER_COLOR),
                ('Drag', self.DRAG_HIGHLIGHT[:3]),
                ('Path', self.HOVER_PATH_COLOR),
            ]
            
            for i, (name, color) in enumerate(states):
                row_y = y_offset + i * 20
                pygame.draw.rect(self.screen, color, (legend_x + 15, row_y, 8, 8))
                pygame.draw.rect(self.screen, (255, 255, 255), (legend_x + 15, row_y, 8, 8), 1)
                
                state_surface = self.small_font.render(name, True, color)
                self.screen.blit(state_surface, (legend_x + 28, row_y - 2))
        
        else:  # Confirmation mode legend
            title = self.small_font.render("CONFIRMATION STATUS", True, (255, 255, 180))
            self.screen.blit(title, (legend_x + 15, y_offset))
            y_offset += 25
            
            status_items = [
                ('● Confirmed', (100, 255, 100)),
                ('● Unconfirmed', self.UNCONFIRMED_COLOR),
                ('● Path Node', self.PATH_COLOR),
                ('● Root', self.ROOT_COLOR),
                ('━ Hover Path', (220, 60, 80)),
                ('✓ Selected', self.SELECTION_COLOR),
            ]
            
            for i, (text, color) in enumerate(status_items):
                row_y = y_offset + i * 22
                
                if text.startswith('●'):
                    pygame.draw.circle(self.screen, color, (legend_x + 15, row_y + 8), 5)
                    pygame.draw.circle(self.screen, (255, 255, 255), (legend_x + 15, row_y + 8), 5, 1)
                elif text.startswith('━'):
                    pygame.draw.line(self.screen, color, (legend_x + 13, row_y + 8),
                                   (legend_x + 23, row_y + 8), 3)
                elif text.startswith('✓'):
                    check_surface = self.small_font.render("✓", True, color)
                    self.screen.blit(check_surface, (legend_x + 12, row_y + 3))
                
                text_surface = self.small_font.render(text, True, self.TEXT_COLOR)
                self.screen.blit(text_surface, (legend_x + 30, row_y))
    
    def _draw_hover_info(self):
        """Draw hover information panel (mode-aware)."""
        if not self.hovered_coordinate:
            return
        
        node_data = self.coordinate_space.get(self.hovered_coordinate, {})
        
        # Panel dimensions
        panel_width = 450 if self.mode == self.MODE_SELECTION else 420
        panel_x = self.screen_width - panel_width - 20
        panel_y = 310 if self.mode == self.MODE_SELECTION else 210
        
        # Build information
        info_lines = []
        
        # Coordinate info
        coord_str = f"({','.join(map(str, self.hovered_coordinate))})"
        info_lines.append(("Coordinate:", coord_str, self.HOVER_COLOR))
        
        # Type and depth
        elem_type = node_data.get('type', 'unknown')
        info_lines.append(("Type:", elem_type, self.TEXT_COLOR))
        info_lines.append(("Depth:", str(len(self.hovered_coordinate)), self.TEXT_COLOR))
        
        if self.mode == self.MODE_SELECTION:
            # Patterns
            patterns = node_data.get('pattern_roles', [])
            if patterns:
                patterns_text = ', '.join(patterns)
                info_lines.append(("Patterns:", patterns_text, (100, 255, 100)))
            else:
                info_lines.append(("Patterns:", "None", (200, 200, 200)))
            
            # Structural role
            structural_role = node_data.get('structural_role', 'UNKNOWN')
            role_color = (255, 200, 100) if structural_role != 'UNKNOWN' else self.TEXT_COLOR
            info_lines.append(("Structural Role:", structural_role, role_color))
            
            # Interactive status
            is_interactive = node_data.get('is_interactive', False)
            interactive_color = (100, 255, 100) if is_interactive else (255, 100, 100)
            interactive_text = "Yes" if is_interactive else "No"
            info_lines.append(("Interactive:", interactive_text, interactive_color))
            
            # Text content
            text_content = node_data.get('text', '')
            if text_content:
                clean_text = text_content.strip().replace('\n', ' ').replace('\t', ' ')
                if len(clean_text) > 50:
                    clean_text = clean_text[:47] + "..."
                info_lines.append(("Text:", clean_text, (200, 220, 255)))
            
            # Classes
            classes = node_data.get('classes', '')
            if classes and classes.strip():
                clean_classes = classes.strip()
                if len(clean_classes) > 40:
                    clean_classes = clean_classes[:37] + "..."
                info_lines.append(("Classes:", clean_classes, (200, 200, 220)))
            
            # Sibling information
            if len(self.hovered_coordinate) > 0:
                sibling_index = self.hovered_coordinate[-1]
                info_lines.append(("Sibling Index:", str(sibling_index), (220, 200, 220)))
            
            # Hash
            element_hash = node_data.get('hash', '')
            if element_hash and element_hash != 'error':
                info_lines.append(("Hash:", element_hash[:12], (180, 180, 200)))
        
        else:  # Confirmation mode info
            # Selection status
            is_selected = self.hovered_coordinate in self.selected_coordinates
            selection_status = "SELECTED" if is_selected else "NOT SELECTED"
            selection_color = (100, 255, 100) if is_selected else (255, 100, 100)
            info_lines.append(("Selection:", selection_status, selection_color))
            
            # Confirmation status
            is_confirmed = self.hovered_coordinate in self.confirmed_coordinates
            confirmation_status = "CONFIRMED ✓" if is_confirmed else "UNCONFIRMED ?"
            confirmation_color = (100, 255, 100) if is_confirmed else self.UNCONFIRMED_COLOR
            info_lines.append(("Status:", confirmation_status, confirmation_color))
            
            # Text content if available
            text_content = node_data.get('text', '')
            if text_content:
                clean_text = text_content.strip().replace('\n', ' ').replace('\t', ' ')
                if len(clean_text) > 40:
                    clean_text = clean_text[:37] + "..."
                info_lines.append(("Text:", clean_text, (200, 220, 255)))
        
        # Calculate panel height
        line_height = 20
        title_height = 30
        padding = 20
        panel_height = title_height + (len(info_lines) * line_height) + padding
        
        # Draw panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.PANEL_BG, panel_surface.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surface, (100, 150, 200, 200), panel_surface.get_rect(), 2, border_radius=8)
        self.screen.blit(panel_surface, panel_rect)
        
        y_offset = panel_y + 15
        
        # Title
        title_text = "NODE INFORMATION"
        title_surface = self.font.render(title_text, True, (255, 255, 180))
        self.screen.blit(title_surface, (panel_x + 15, y_offset))
        y_offset += 25
        
        # Draw all information lines
        for label, value, color in info_lines:
            label_surface = self.small_font.render(label, True, (180, 200, 220))
            self.screen.blit(label_surface, (panel_x + 15, y_offset))
            
            value_surface = self.small_font.render(str(value), True, color)
            value_x = panel_x + (120 if self.mode == self.MODE_SELECTION else 100)
            self.screen.blit(value_surface, (value_x, y_offset))
            y_offset += 20
    
    # ===== MODE-SPECIFIC DRAWING METHODS =====
    
    def _draw_selection_interface(self):
        """Draw selection mode interface (grid-based)."""
        center_x = self.screen_width // 2 + self.pan_x
        center_y = self.screen_height // 2 + self.pan_y
        
        # Draw white grid
        self._draw_white_grid(center_x, center_y)
        
        # Draw normal connections (white, no arrows)
        self._draw_selection_connections(center_x, center_y)
        
        # Draw hover path and its children (red with arrows)
        if self.hovered_coordinate:
            self._draw_hover_path()
        
        # Draw drag-selected coords
        self._draw_drag_selected_coords(center_x, center_y)
        
        # Draw all coordinate nodes
        for coord in self.selection_display_coords:
            self._draw_coordinate_node(coord, True)
        
        # Draw drag selection rectangle
        self._draw_drag_selection()
        
        # Draw UI elements
        self._draw_control_panel()
        self._draw_legend()
        self._draw_hover_info()
        self._draw_selection_summary()
        self._draw_viewport_info()
    
    def _draw_confirmation_interface(self):
        """Draw confirmation mode interface (tree-based)."""
        # Draw connections
        self._draw_confirmation_connections()
        
        # Draw hover path if applicable
        if self.hovered_coordinate:
            self._draw_hover_path()
        
        # Draw drag-selected coords
        self._draw_drag_selected_coords_tree()
        
        # Draw all coordinate nodes
        for coord in self.confirmation_display_coords:
            self._draw_coordinate_node(coord, True)
        
        # Draw drag selection rectangle
        self._draw_drag_selection()
        
        # Draw UI elements
        self._draw_title()
        self._draw_instructions()
        self._draw_summary()
        self._draw_hover_info()
        self._draw_legend()
    
    def _draw_white_grid(self, center_x, center_y):
        """Draw white grid lines for selection mode."""
        # Vertical lines
        for i in range(-30, 31):
            x = center_x + i * self.cell_size * self.zoom
            if 50 <= x <= self.screen_width - 50:
                pygame.draw.line(self.screen, self.GRID_COLOR,
                               (x, 100), (x, self.screen_height - 150), 1)
        
        # Horizontal lines
        for i in range(40):
            y = center_y + i * self.cell_size * self.zoom
            if 100 <= y <= self.screen_height - 150:
                pygame.draw.line(self.screen, self.GRID_COLOR,
                               (50, y), (self.screen_width - 50, y), 1)
        
        # Axes
        pygame.draw.line(self.screen, self.AXIS_COLOR,
                       (center_x, 100), (center_x, self.screen_height - 150), 2)
        pygame.draw.line(self.screen, self.AXIS_COLOR,
                       (50, center_y), (self.screen_width - 50, center_y), 2)
        
        # Labels
        depth_label = self.font.render("DOM Depth", True, (180, 180, 180))
        sibling_label = self.font.render("Sibling Index", True, (180, 180, 180))
        self.screen.blit(depth_label, (center_x - 60, center_y - 40))
        self.screen.blit(sibling_label, (center_x + 20, center_y + 20 * self.cell_size * self.zoom))
    
    def _draw_selection_connections(self, center_x, center_y):
        """Draw white connections for selection mode."""
        for coord in self.selection_display_coords:
            if len(coord) > 1:  # Not root
                parent_coord = coord[:-1]
                
                start_pos = self._coord_to_screen(parent_coord, center_x, center_y)
                end_pos = self._coord_to_screen(coord, center_x, center_y)
                
                if start_pos and end_pos:
                    # Check if this connection is part of hover path
                    is_hover_path = False
                    if self.hovered_coordinate:
                        is_hover_path = (coord == self.hovered_coordinate or 
                                      parent_coord == self.hovered_coordinate or
                                      self._is_child_of_hovered(coord))
                    
                    if is_hover_path:
                        # Draw RED hover connection
                        self._draw_red_hover_connection(start_pos, end_pos, coord)
                    else:
                        # Draw normal white connection
                        line_surface = pygame.Surface((abs(end_pos[0] - start_pos[0]) + 4,
                                                     abs(end_pos[1] - start_pos[1]) + 4), pygame.SRCALPHA)
                        pygame.draw.line(line_surface, (255, 255, 255, 40),
                                       (2, 2), 
                                       (end_pos[0] - start_pos[0] + 2, end_pos[1] - start_pos[1] + 2),
                                       3)
                        pygame.draw.line(line_surface, (255, 255, 255, 120),
                                       (2, 2), 
                                       (end_pos[0] - start_pos[0] + 2, end_pos[1] - start_pos[1] + 2),
                                       1)
                        self.screen.blit(line_surface, (start_pos[0] - 2, start_pos[1] - 2))
    
    def _draw_confirmation_connections(self):
        """Draw connections for confirmation mode (tree layout)."""
        for coord in self.confirmation_display_coords:
            if len(coord) > 1:
                parent_coord = coord[:-1]
                if parent_coord in self.coord_positions and coord in self.coord_positions:
                    start_pos = self._coord_to_screen(parent_coord)
                    end_pos = self._coord_to_screen(coord)
                    
                    if start_pos and end_pos:
                        # Draw connection line
                        pygame.draw.line(self.screen, self.PATH_COLOR, start_pos, end_pos, 2)
                        
                        # Add arrow
                        dx = end_pos[0] - start_pos[0]
                        dy = end_pos[1] - start_pos[1]
                        angle = math.atan2(dy, dx)
                        arrow_x = start_pos[0] + dx * 0.6
                        arrow_y = start_pos[1] + dy * 0.6
                        
                        arrow_text = ">"
                        arrow_surface = self.small_font.render(arrow_text, True, (255, 255, 255, 180))
                        arrow_rotated = pygame.transform.rotate(arrow_surface, math.degrees(-angle) + 90)
                        arrow_rect = arrow_rotated.get_rect(center=(int(arrow_x), int(arrow_y)))
                        self.screen.blit(arrow_rotated, arrow_rect)
    
    def _draw_red_hover_connection(self, start_pos, end_pos, coord):
        """Draw red hover connection for selection mode."""
        current_time = pygame.time.get_ticks() * 0.001
        
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = max(1, math.sqrt(dx*dx + dy*dy))
        angle = math.atan2(dy, dx)
        
        pulse = 0.5 + 0.5 * math.sin(current_time * 3)
        
        # Check if immediate child
        is_immediate_child = False
        if self.hovered_coordinate and len(coord) == len(self.hovered_coordinate) + 1:
            if coord[:-1] == self.hovered_coordinate:
                is_immediate_child = True
        
        # Choose colors
        if is_immediate_child:
            inner_glow_color = (100, 255, 100)  # Green
            outer_glow_color = (60, 200, 60)
            line_color = (80, 220, 80)
            glow_alpha_inner = int(180 + 75 * pulse)
            glow_alpha_outer = int(100 + 50 * pulse)
        else:
            inner_glow_color = (255, 100, 100)  # Red
            outer_glow_color = (255, 60, 60)
            line_color = (220, 40, 40)
            glow_alpha_inner = int(180 + 75 * pulse)
            glow_alpha_outer = int(100 + 50 * pulse)
        
        # Draw glow
        glow_width = int(length)
        glow_height = 10
        glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
        
        pygame.draw.line(glow_surface, (*inner_glow_color, glow_alpha_inner),
                    (0, glow_height//2), (glow_width, glow_height//2), 5)
        pygame.draw.line(glow_surface, (*outer_glow_color, glow_alpha_outer),
                    (0, glow_height//2), (glow_width, glow_height//2), 8)
        
        rotated = pygame.transform.rotate(glow_surface, math.degrees(-angle))
        rotated_rect = rotated.get_rect()
        rotated_rect.center = (
            start_pos[0] + dx * 0.5,
            start_pos[1] + dy * 0.5
        )
        
        self.screen.blit(rotated, rotated_rect)
        
        # Draw solid line
        pygame.draw.line(self.screen, line_color, start_pos, end_pos, 3)
        
        # Draw arrow for immediate children
        if is_immediate_child:
            arrow_distance = 0.8
            arrow_x = start_pos[0] + dx * arrow_distance
            arrow_y = start_pos[1] + dy * arrow_distance
            
            arrow_size = 12 + 4 * pulse
            arrow_text = "▶"
            arrow_surface = self.small_font.render(arrow_text, True, (255, 255, 255, int(255 * pulse)))
            arrow_angle = math.degrees(-angle) - 90
            arrow_rotated = pygame.transform.rotate(arrow_surface, arrow_angle)
            arrow_rect = arrow_rotated.get_rect(center=(int(arrow_x), int(arrow_y)))
            
            arrow_glow = pygame.Surface((int(arrow_size * 1.5), int(arrow_size * 1.5)), pygame.SRCALPHA)
            pygame.draw.circle(arrow_glow, (255, 255, 255, int(100 * pulse)),
                            (int(arrow_size * 0.75), int(arrow_size * 0.75)),
                            int(arrow_size * 0.75))
            self.screen.blit(arrow_glow, 
                        (int(arrow_x - arrow_size * 0.75), int(arrow_y - arrow_size * 0.75)))
            
            self.screen.blit(arrow_rotated, arrow_rect)
    
    def _draw_drag_selected_coords(self, center_x=None, center_y=None):
        """Highlight coords in drag selection (selection mode)."""
        if not self.dragging_selection or not self.drag_selected_coords:
            return
        
        for coord in self.drag_selected_coords:
            if self.mode == self.MODE_SELECTION:
                screen_pos = self._coord_to_screen(coord, center_x, center_y)
            else:
                screen_pos = self._coord_to_screen(coord)
            
            if screen_pos:
                pulse = 1.5 + math.sin(pygame.time.get_ticks() * 0.01) * 0.5
                
                outer_surface = pygame.Surface((int(24 + pulse * 4), int(24 + pulse * 4)), pygame.SRCALPHA)
                pygame.draw.circle(outer_surface, self.DRAG_HIGHLIGHT,
                                 (int(12 + pulse * 2), int(12 + pulse * 2)),
                                 int(12 + pulse * 2))
                self.screen.blit(outer_surface, (screen_pos[0] - int(12 + pulse * 2),
                                               screen_pos[1] - int(12 + pulse * 2)))
                
                inner_surface = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(inner_surface, (255, 200, 50, 180),
                                 (8, 8), 8)
                self.screen.blit(inner_surface, (screen_pos[0] - 8, screen_pos[1] - 8))
    
    def _draw_drag_selected_coords_tree(self):
        """Highlight coords in drag selection (confirmation mode)."""
        if not self.dragging_selection or not self.drag_selected_coords:
            return
        
        for coord in self.drag_selected_coords:
            if coord in self.coord_positions:
                pos = self.coord_positions[coord]
                screen_pos = self._coord_to_screen(coord)
                if screen_pos:
                    highlight_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                    pygame.draw.circle(highlight_surface, self.DRAG_HIGHLIGHT, (10, 10), 10)
                    self.screen.blit(highlight_surface, (screen_pos[0] - 10, screen_pos[1] - 10))
    
    # ===== UI PANEL METHODS =====
    
    def _draw_control_panel(self):
        """Draw control panel for selection mode."""
        title = self.title_font.render("SPIDERBOT - COORDINATE SELECTION", True, (255, 255, 200))
        subtitle = self.small_font.render("Monitoring Engine", True, (200, 220, 220))
        
        panel_width = 500
        panel_height = 130
        panel_rect = pygame.Rect(20, 20, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.PANEL_BG, panel_surface.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surface, (100, 100, 120, 200), panel_surface.get_rect(), 2, border_radius=8)
        self.screen.blit(panel_surface, panel_rect)
        
        self.screen.blit(title, (30, 30))
        self.screen.blit(subtitle, (30, 65))
        
        instructions = [
            "LEFT CLICK: Select/deselect | LEFT DRAG: Multi-select",
            "HOVER: Shows path to root | RIGHT DRAG: Pan view",
            "SCROLL: Zoom | RIGHT/LEFT: Switch modes | ENTER: Finish (in confirmation)",
            "ESC: Cancel | R: Reset | TAB: Toggle mode"
        ]
        
        for i, text in enumerate(instructions):
            instr_surface = self.small_font.render(text, True, self.TEXT_COLOR)
            self.screen.blit(instr_surface, (30, 90 + i * 20))
    
    def _draw_title(self):
        """Draw title panel for confirmation mode."""
        title = self.title_font.render("SPIDERBOT - PATH CONFIRMATION", True, (255, 255, 200))
        subtitle = self.small_font.render("Toggle confirmation for selected paths", True, (200, 220, 220))
        
        panel_rect = pygame.Rect(20, 20, 600, 80)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.PANEL_BG, panel_surface.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surface, (100, 150, 200, 200), panel_surface.get_rect(), 2, border_radius=8)
        self.screen.blit(panel_surface, panel_rect)
        
        self.screen.blit(title, (30, 30))
        self.screen.blit(subtitle, (30, 60))
    
    def _draw_instructions(self):
        """Draw instructions for confirmation mode."""
        instructions = [
            "Click selected nodes (colored) to toggle confirmation",
            "LEFT CLICK + DRAG: Multi-toggle | RIGHT CLICK + DRAG: Pan",
            "SCROLL: Zoom | LEFT/RIGHT: Switch modes | ENTER: Finish",
            "ESC: Cancel | R: Reset | TAB: Toggle mode",
        ]
        
        for i, text in enumerate(instructions):
            color = (255, 255, 150) if i == 0 else self.TEXT_COLOR
            instr_surface = self.small_font.render(text, True, color)
            self.screen.blit(instr_surface, (30, 120 + i * 20))
    
    def _draw_selection_summary(self):
        """Draw selection summary for selection mode."""
        summary_rect = pygame.Rect(20, self.screen_height - 100, self.screen_width - 40, 80)
        summary_surface = pygame.Surface((summary_rect.width, summary_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(summary_surface, self.PANEL_BG, summary_surface.get_rect(), border_radius=8)
        pygame.draw.rect(summary_surface, (100, 100, 120, 200), summary_surface.get_rect(), 2, border_radius=8)
        self.screen.blit(summary_surface, summary_rect)
        
        # Selection count
        count_text = f"Selected: {len(self.selected_coordinates)} coordinates"
        count_surface = self.font.render(count_text, True, (100, 255, 100))
        self.screen.blit(count_surface, (40, self.screen_height - 85))
        
        # Hover info if applicable
        if self.hovered_coordinate:
            hover_text = f"Hover: {self.hovered_coordinate}"
            hover_surface = self.small_font.render(hover_text, True, self.HOVER_COLOR)
            self.screen.blit(hover_surface, (40, self.screen_height - 60))
        
        # Mode switching instruction
        mode_text = "Press RIGHT ARROW or TAB to switch to Confirmation Mode"
        mode_surface = self.small_font.render(mode_text, True, (255, 255, 150))
        mode_x = self.screen_width // 2 - mode_surface.get_width() // 2
        self.screen.blit(mode_surface, (mode_x, self.screen_height - 35))
    
    def _draw_summary(self):
        """Draw confirmation summary for confirmation mode."""
        summary_rect = pygame.Rect(20, self.screen_height - 100, self.screen_width - 40, 80)
        summary_surface = pygame.Surface((summary_rect.width, summary_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(summary_surface, self.PANEL_BG, summary_surface.get_rect(), border_radius=8)
        pygame.draw.rect(summary_surface, (100, 150, 200, 200), summary_surface.get_rect(), 2, border_radius=8)
        self.screen.blit(summary_surface, summary_rect)
        
        # Confirmed count
        count_text = f"Confirmed: {len(self.confirmed_coordinates)} / {len(self.selected_coordinates)}"
        count_surface = self.font.render(count_text, True, (100, 255, 100))
        self.screen.blit(count_surface, (40, self.screen_height - 85))
        
        # Instructions
        if self.dragging_selection:
            help_text = "Release mouse to toggle confirmation for highlighted coordinates"
        else:
            help_text = "Press ENTER to continue with confirmed coordinates | LEFT/RIGHT: Switch modes"
        
        help_surface = self.small_font.render(help_text, True, (255, 255, 150))
        help_x = self.screen_width // 2 - help_surface.get_width() // 2
        self.screen.blit(help_surface, (help_x, self.screen_height - 50))
    
    def _draw_viewport_info(self):
        """Show viewport information for selection mode."""
        info_text = [
            f"Zoom: {self.zoom:.1f}x",
            f"Nodes: {len(self.selection_display_coords)}",
            f"Selected: {len(self.selected_coordinates)}",
        ]
        
        panel_width = 140
        panel_height = 65
        panel_x = self.screen_width - panel_width - 20
        panel_y = 290
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, self.PANEL_BG, panel_surface.get_rect(), border_radius=6)
        pygame.draw.rect(panel_surface, (100, 100, 120, 200), panel_surface.get_rect(), 1, border_radius=6)
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        for i, text in enumerate(info_text):
            info_surface = self.small_font.render(text, True, (200, 255, 200))
            self.screen.blit(info_surface, (panel_x + 10, panel_y + 10 + i * 18))
    
    # ===== TREE LAYOUT METHODS =====
    
    def _calculate_tree_layout(self):
        """Calculate tree layout positions for confirmation mode."""
        positions = {}
        
        # Group by depth
        depth_groups = {}
        for coord in self.confirmation_display_coords:
            depth = len(coord)
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(coord)
        
        # Sort by depth
        for depth in sorted(depth_groups.keys()):
            coords_at_depth = depth_groups[depth]
            coords_at_depth.sort(key=lambda x: x[-1] if x else 0)
            
            # Calculate positions
            x_spacing = (self.screen_width - 200) / max(len(coords_at_depth), 1)
            base_y = 150 + depth * 70 * self.zoom + self.pan_y
            
            for i, coord in enumerate(coords_at_depth):
                x_pos = 100 + x_spacing * (i + 0.5) + self.pan_x
                positions[coord] = (int(x_pos), int(base_y))
        
        return positions
    
    # ===== DRAG SELECTION METHODS =====
    
    def _draw_drag_selection(self):
        """Draw drag selection rectangle."""
        if not self.dragging_selection or not self.drag_start_pos or not self.drag_current_pos:
            return
        
        rect = self._get_drag_rectangle()
        if rect.width > 5 or rect.height > 5:
            drag_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(drag_surface, self.DRAG_RECT_COLOR, (0, 0, rect.width, rect.height))
            pygame.draw.rect(drag_surface, (255, 200, 50, 200), (0, 0, rect.width, rect.height), 2)
            self.screen.blit(drag_surface, (rect.x, rect.y))
            
            if self.drag_selected_coords:
                count_text = f"{len(self.drag_selected_coords)}"
                count_surface = self.small_font.render(count_text, True, (255, 200, 50))
                count_pos = (rect.x + rect.width // 2 - count_surface.get_width() // 2,
                           rect.y + rect.height // 2 - count_surface.get_height() // 2)
                self.screen.blit(count_surface, count_pos)
    
    def _get_drag_rectangle(self):
        """Get current drag rectangle."""
        if not self.drag_start_pos or not self.drag_current_pos:
            return pygame.Rect(0, 0, 0, 0)
        
        x1, y1 = self.drag_start_pos
        x2, y2 = self.drag_current_pos
        
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return pygame.Rect(left, top, width, height)
    
    def _handle_drag_start(self, mouse_pos):
        """Start drag selection."""
        self.drag_start_pos = mouse_pos
        self.drag_current_pos = mouse_pos
        self.dragging_selection = True
        self.drag_selected_coords.clear()
        self.cosmic_bg.add_particles(mouse_pos[0], mouse_pos[1], 5)
    
    def _handle_drag_update(self, mouse_pos):
        """Update drag selection."""
        if not self.dragging_selection or not self.drag_start_pos:
            return
        
        self.drag_current_pos = mouse_pos
        current_time = time.time()
        
        if current_time - self.last_drag_update > 0.05:
            self._update_drag_selection()
            self.last_drag_update = current_time
    
    def _update_drag_selection(self):
        """Update which coords are in drag rectangle."""
        if not self.drag_start_pos or not self.drag_current_pos:
            return
        
        rect = self._get_drag_rectangle()
        if rect.width < 2 and rect.height < 2:
            return
        
        self.drag_selected_coords.clear()
        
        if self.mode == self.MODE_SELECTION:
            center_x = self.screen_width // 2 + self.pan_x
            center_y = self.screen_height // 2 + self.pan_y
            
            for coord in self.selection_display_coords:
                screen_pos = self._coord_to_screen(coord, center_x, center_y)
                if screen_pos and rect.collidepoint(screen_pos):
                    self.drag_selected_coords.add(coord)
        
        else:  # MODE_CONFIRMATION
            for coord, pos in self.coord_positions.items():
                screen_pos = self._coord_to_screen(coord)
                if screen_pos and rect.collidepoint(screen_pos):
                    self.drag_selected_coords.add(coord)
    
    def _handle_drag_end(self):
        """Finish drag selection - toggle selection/confirmation."""
        if not self.dragging_selection:
            return
        
        if self.drag_selected_coords:
            toggled_count = 0
            
            for coord in self.drag_selected_coords:
                if self.mode == self.MODE_SELECTION:
                    # Toggle selection
                    if coord in self.selected_coordinates:
                        self.selected_coordinates.remove(coord)
                        # Also remove from confirmed if it was there
                        if coord in self.confirmed_coordinates:
                            self.confirmed_coordinates.remove(coord)
                    else:
                        self.selected_coordinates.add(coord)
                    toggled_count += 1
                else:  # MODE_CONFIRMATION
                    # Toggle confirmation (only for selected coordinates)
                    if coord in self.selected_coordinates:
                        if coord in self.confirmed_coordinates:
                            self.confirmed_coordinates.remove(coord)
                        else:
                            self.confirmed_coordinates.add(coord)
                        toggled_count += 1
            
            if toggled_count > 0:
                print(f"✅ Toggled {toggled_count} coordinates via drag selection")
                
                # Visual feedback
                if self.drag_current_pos:
                    self.cosmic_bg.add_particles(
                        self.drag_current_pos[0], 
                        self.drag_current_pos[1], 
                        15, 
                        (100, 255, 100)
                    )
        
        self.dragging_selection = False
        self.drag_start_pos = None
        self.drag_current_pos = None
        self.drag_selected_coords.clear()
        
        # Update display for confirmation mode
        if self.mode == self.MODE_CONFIRMATION:
            self._update_display_coordinates()
    
    # ===== CLICK HANDLING =====
    
    def _handle_selection_click(self, mouse_pos):
        """Handle click in selection mode."""
        coord = self._find_coordinate_at_position(mouse_pos)
        if coord:
            if coord in self.selected_coordinates:
                self.selected_coordinates.remove(coord)
                # Also remove from confirmed
                if coord in self.confirmed_coordinates:
                    self.confirmed_coordinates.remove(coord)
                print(f"❌ Deselected: {coord}")
                self.cosmic_bg.add_particles(mouse_pos[0], mouse_pos[1], 5, (255, 100, 100))
            else:
                self.selected_coordinates.add(coord)
                print(f"✅ Selected: {coord}")
                self.cosmic_bg.add_particles(mouse_pos[0], mouse_pos[1], 8, (100, 255, 100))
    
    def _handle_confirmation_click(self, mouse_pos):
        """Handle click in confirmation mode."""
        coord = self._find_coordinate_at_position(mouse_pos)
        if coord and coord in self.selected_coordinates:
            if coord in self.confirmed_coordinates:
                self.confirmed_coordinates.remove(coord)
                print(f"Unconfirmed: {coord}")
            else:
                self.confirmed_coordinates.add(coord)
                print(f"Confirmed: {coord}")
    
    # ===== HELPER METHODS =====
    
    def _is_child_of_hovered(self, coord):
        """Check if coordinate is a child of hovered node."""
        if not self.hovered_coordinate:
            return False
        
        if len(coord) <= len(self.hovered_coordinate):
            return False
        
        return coord[:len(self.hovered_coordinate)] == self.hovered_coordinate
    
    # ===== MAIN LOOP =====
    
    def run_selection(self):
        """Main selection loop handling both modes."""
        print("🕸️ UNIFIED SPIDERBOT INTERFACE ACTIVATED")
        print("🎯 Use LEFT/RIGHT arrows to switch between Selection and Confirmation modes")
        
        clock = pygame.time.Clock()
        running = True
        
        pan_speed = 15
        keys_held = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False, 
            pygame.K_UP: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False,
            pygame.K_w: False, pygame.K_s: False
        }
        
        while running:
            # Handle continuous key presses
            needs_recalc = False
            
            if keys_held[pygame.K_LEFT] or keys_held[pygame.K_a]:
                self.pan_x += pan_speed
                needs_recalc = True
            if keys_held[pygame.K_RIGHT] or keys_held[pygame.K_d]:
                self.pan_x -= pan_speed
                needs_recalc = True
            if keys_held[pygame.K_UP] or keys_held[pygame.K_w]:
                self.pan_y += pan_speed
                needs_recalc = True
            if keys_held[pygame.K_DOWN] or keys_held[pygame.K_s]:
                self.pan_y -= pan_speed
                needs_recalc = True
            
            if needs_recalc and self.mode == self.MODE_CONFIRMATION:
                self.coord_positions = self._calculate_tree_layout()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.confirmed_coordinates.clear()
                    self.selected_coordinates.clear()
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.mode == self.MODE_CONFIRMATION:
                        running = False  # Finish in confirmation mode
                    elif event.key == pygame.K_ESCAPE:
                        self.confirmed_coordinates.clear()
                        self.selected_coordinates.clear()
                        running = False
                    elif event.key == pygame.K_TAB or event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                        self.switch_mode("right" if event.key in [pygame.K_TAB, pygame.K_RIGHT] else "left")
                    elif event.key == pygame.K_r:
                        self.pan_x, self.pan_y = 0, 0
                        self.zoom = 1.0
                        if self.mode == self.MODE_CONFIRMATION:
                            self.coord_positions = self._calculate_tree_layout()
                        print("🔄 View reset")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.zoom = min(3.0, self.zoom * 1.2)
                        if self.mode == self.MODE_CONFIRMATION:
                            self.coord_positions = self._calculate_tree_layout()
                    elif event.key == pygame.K_MINUS:
                        self.zoom = max(0.3, self.zoom * 0.8)
                        if self.mode == self.MODE_CONFIRMATION:
                            self.coord_positions = self._calculate_tree_layout()
                    elif event.key == pygame.K_HOME:
                        self.pan_x, self.pan_y = 0, 0
                        self.zoom = 1.0
                        if self.mode == self.MODE_CONFIRMATION:
                            self.coord_positions = self._calculate_tree_layout()
                        print("🏠 Returned to center")
                    elif event.key in keys_held:
                        keys_held[event.key] = True
                
                elif event.type == pygame.KEYUP:
                    if event.key in keys_held:
                        keys_held[event.key] = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self._handle_drag_start(event.pos)
                    elif event.button == 3:  # Right click
                        self.dragging = True
                        self.last_mouse_pos = event.pos
                    elif event.button == 4:  # Scroll up
                        self.zoom = min(3.0, self.zoom * 1.1)
                        if self.mode == self.MODE_CONFIRMATION:
                            self.coord_positions = self._calculate_tree_layout()
                    elif event.button == 5:  # Scroll down
                        self.zoom = max(0.3, self.zoom * 0.9)
                        if self.mode == self.MODE_CONFIRMATION:
                            self.coord_positions = self._calculate_tree_layout()
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click release
                        if self.dragging_selection:
                            rect = self._get_drag_rectangle()
                            if rect.width > 5 or rect.height > 5:  # Was a drag
                                self._handle_drag_end()
                            else:  # Was a click
                                if self.mode == self.MODE_SELECTION:
                                    self._handle_selection_click(event.pos)
                                else:
                                    self._handle_confirmation_click(event.pos)
                                self.dragging_selection = False
                                self.drag_start_pos = None
                        else:
                            if self.mode == self.MODE_SELECTION:
                                self._handle_selection_click(event.pos)
                            else:
                                self._handle_confirmation_click(event.pos)
                    elif event.button == 3:  # Right click release
                        self.dragging = False
                
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                    
                    # Update hover
                    self.hovered_coordinate = self._find_coordinate_at_position(mouse_pos)
                    
                    # Update drag
                    if self.dragging_selection:
                        self._handle_drag_update(mouse_pos)
                    
                    # Handle panning
                    if self.dragging:
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]
                        self.pan_x += dx
                        self.pan_y += dy
                        self.last_mouse_pos = event.pos
                        if self.mode == self.MODE_CONFIRMATION:
                            self.coord_positions = self._calculate_tree_layout()
            
            # Draw everything
            self._draw_background()
            if self.mode == self.MODE_SELECTION:
                self._draw_selection_interface()
            else:
                self._draw_confirmation_interface()
            
            pygame.display.flip()
            clock.tick(self.draw_fps)
        
        pygame.quit()

        # ✅ Return the selected coordinates
        if self.mode == self.MODE_CONFIRMATION:
            print(f"✅ Confirmation complete: {len(self.confirmed_coordinates)} paths confirmed")
            return list(self.confirmed_coordinates)
        else:
            print(f"✅ Selection complete: {len(self.selected_coordinates)} coordinates chosen")
            return list(self.selected_coordinates)
            


# ===== Central Brain -- Nexus ===== 
#!/usr/bin/env python3
"""
🌀 NEXUS-CORE: Minimalist Coordinator & Adaptive Pattern Corrector
Coordinates neurons, corrects patterns, exports visualization data
"""

# ==== NEXUS CENTRAL ENGINE - Beta ==== 
#!/usr/bin/env python3
"""
🌀 NEXUS: Simplified Coordinator for 25D Neural Network

Core Responsibilities:
1. Coordinate selection via SpiderBot UI
2. Browser attachment and DOM access  
3. Neuron factory (creates neurons at coordinates)
4. 1-second heartbeat export with rich matrix data
5. Visualizer JSON export bridge
6. Growth signal processing

Simplified: Neurons handle their own pattern matching via ROSE instances.
Nexus only coordinates creation and exports rich data.
"""

class Nexus:
    
    def __init__(self, port="9223"):
        # ===== SESSION TIMING =====
        import uuid
        self.session_id = f"nexus_{uuid.uuid4().hex[:8]}"
        self.session_start_time = None
        
        # ===== OUTPUT DIRECTORIES (SAME STRUCTURE) =====
        self.cognition_dir = "Cognition"
        os.makedirs(self.cognition_dir, exist_ok=True)
        
        self.session_dir = os.path.join(self.cognition_dir, self.session_id)
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Create frames directory (SAME STRUCTURE)
        self.frames_dir = os.path.join(self.session_dir, "frames")
        os.makedirs(self.frames_dir, exist_ok=True)
        
        # Matrix directory (optional, for backward compatibility)
        self.matrix_dir = os.path.join(self.session_dir, "matrix")
        os.makedirs(self.matrix_dir, exist_ok=True)
        
        # ===== CORE SYSTEMS (UNCHANGED) =====
        self.driver = None
        self.coordinate_space = {}
        self.selected_coordinates = []
        self.axon_network = None
        self.neurons: Dict[Tuple, Neuron] = {}
        self.growth_signals_processed = 0
        self.void_coordinates = set()
        
        # ===== MONITORING STATE (UNCHANGED) =====
        self.monitoring_active = False
        
        # ===== SIMPLIFIED FRAME SYSTEM =====
        self.frame_counter = 0
        self.last_dump_time = 0
        self.dump_interval = 1.0  # Dump every 1 second
        
        # ===== ENTER KEY LISTENER (UNCHANGED) =====
        self._enter_key_thread = None
        self._stop_enter_thread = threading.Event()
        
        # ===== NEURON THREADS (UNCHANGED) =====
        self.neuron_threads = {}
        
        # ===== STATISTICS (SIMPLIFIED) =====
        self.B_matrix_history = []
        self.assignment_history = []
        
        print(f"🌀 NEXUS 25D initialized: {self.session_id}")
        print(f"📁 Session directory: {self.session_dir}")
        print(f"📁 Frames will be saved to: {self.frames_dir}")
    
    # ===== SIMPLIFIED FRAME DUMPING =====
    
    def _dump_visualization_frame(self):
        """Periodically dump visualization data from axon network"""
        current_time = time.time()
        
        # Check if it's time to dump
        if current_time - self.last_dump_time < self.dump_interval:
            return
        
        try:
            # Ask axon network to create visualization frame
            frame_number = self.frame_counter
            self.frame_counter += 1
            
            # Create visualizer-friendly data structure
            frame_data = {
                'frame': frame_number,
                'session_time': current_time - self.session_start_time,
                'timestamp': current_time,
                'session_id': self.session_id,
                
                # Get neurons from axon network
                'neurons': self._get_neuron_states(),
                
                # Get axons from axon network
                'axons': self._get_active_axons(),
                
                # System stats
                'system_stats': {
                    'total_neurons': len(self.neurons),
                    'monitoring_active': self.monitoring_active,
                    'session_duration': current_time - self.session_start_time
                }
            }
            
            # Save to file (SAME DIRECTORY STRUCTURE)
            filename = f"frame_{frame_number:06d}.json"
            filepath = os.path.join(self.frames_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(frame_data, f, indent=2)
            
            print(f"📊 Frame {frame_number} dumped: {len(frame_data['neurons'])} neurons")
            self.last_dump_time = current_time
            
        except Exception as e:
            print(f"⚠️ Frame dump error: {e}")
    
    def _get_neuron_states(self):
        """Get current state of all neurons for visualization"""
        neuron_states = []
        
        for coord, neuron in self.neurons.items():
            if neuron.processing_phase == "DESTROYED":
                continue
            
            # Get neuron's current state
            neuron_state = {
                'neuron_id': neuron.id,
                'coordinate': list(coord) if isinstance(coord, tuple) else coord,
                'pattern': neuron.current_pattern,
                'confidence': neuron.confidence_score,
                'current_state': 'ACTIVE' if neuron.confidence_score > 0.5 else 'LEARNING',
                'processing_phase': neuron.processing_phase,
                'cycle': neuron.cycle_count,
                'recycling_iteration': neuron.recycling_iteration,
                
                # Matrix data (if available)
                'b_vector': neuron.b_vector.tolist() if hasattr(neuron, 'b_vector') else [0.2]*5,
                'B_matrix_trace': float(np.trace(neuron.B_matrix)) if hasattr(neuron, 'B_matrix') else 0.0,
                
                # Eigen values (if available)
                'eigen_system': {
                    'alpha': float(getattr(neuron, 'eigen_alpha', 0.0)),
                    'beta': float(getattr(neuron, 'eigen_beta', 0.0)),
                    'gamma': float(getattr(neuron, 'eigen_gamma', 0.0)),
                    'zeta': float(getattr(neuron, 'eigen_zeta', 0.0)),
                },
                
                # Void/membrane status
                'void_count': len(getattr(neuron, 'void_coordinates', set())),
                'has_growth_signals': getattr(neuron, 'has_growth_signals', False),
                
                # Health/connection info
                'health_status': 'UNKNOWN',
                'health_score': 0.0,
                'assignment_count': len(getattr(neuron, 'assignment', {})),
                'pattern_probabilities': neuron.b_vector.tolist() if hasattr(neuron, 'b_vector') else [0.2]*5
            }
            
            # Add UNKNOWN-specific data
            if neuron.current_pattern == "UNKNOWN":
                neuron_state['unknown_specific'] = {
                    'is_unknown_pattern': True,
                    'has_gamma_update': getattr(neuron.unknown_perm_cache, 'b_matrix_updated', False),
                    'cycle_history': getattr(neuron.unknown_perm_cache, 'cycle_history', []),
                }
            
            neuron_states.append(neuron_state)
        
        return neuron_states
    
    def _get_active_axons(self):
        """Get active axons for visualization"""
        active_axons = []
        
        if not hasattr(self, 'axon_network'):
            return active_axons
        
        # Get recent axons from all pattern queues
        recent_time = time.time() - 2.0  # Last 2 seconds
        
        for pattern in ['DATA_INPUT', 'ACTION_ELEMENT', 'CONTEXT_ELEMENT', 
                       'STRUCTURAL', 'UNKNOWN', 'NEXUS']:
            if pattern in self.axon_network.queues:
                queue = self.axon_network.queues[pattern]
                
                if pattern == 'NEXUS':
                    # NEXUS queue is a deque
                    for axon in list(queue)[-20:]:  # Last 20 axons
                        if self._is_visualizable_axon(axon):
                            active_axons.append(self._format_axon_for_viz(axon))
                else:
                    # Pattern queues are dicts
                    for neuron_id, axons in queue.items():
                        if axons:
                            for axon in axons[-5:]:  # Last 5 axons per neuron
                                if self._is_visualizable_axon(axon):
                                    active_axons.append(self._format_axon_for_viz(axon))
        
        return active_axons
    
    def _is_visualizable_axon(self, axon):
        """Check if axon should be visualized"""
        axon_type = axon.get('axon_type', '')
        
        # Visualize these axon types
        visualizable_types = [
            'GROWTH_SIGNAL',
            'VOID_SIGNAL', 
            'CIRCUITRY_UPDATE',
            'DOT_PRODUCT_REPORT',
            'PATTERN_CHANGE',
            'UNKNOWN_UPDATE',
            'HIERARCHICAL_ASSIGNMENT'
        ]
        
        return axon_type in visualizable_types
    
    def _format_axon_for_viz(self, axon):
        """Format axon for visualizer"""
        source = axon.get('source', {})
        data = axon.get('data', {})
        
        # Determine target
        target_coord = data.get('coordinate') or source.get('coordinate')
        
        return {
            'axon_type': axon.get('axon_type', 'UNKNOWN'),
            'source': {
                'id': source.get('id', ''),
                'coordinate': source.get('coordinate'),
                'pattern': source.get('pattern', 'UNKNOWN')
            },
            'target': {
                'id': data.get('neuron_id', ''),
                'coordinate': target_coord
            },
            'data': {
                'neuron_id': data.get('neuron_id', ''),
                'confidence': data.get('confidence', 0.0),
                'cycle': data.get('cycle', 0),
                'coordinate': data.get('coordinate')
            },
            'session_time': axon.get('session_time', 0)
        }
    
    # ===== MAIN MONITORING LOOP (SIMPLIFIED) =====
    
    def run_monitoring(self, priori_data: Dict, use_unknown_for_all: bool = False):
        """Complete monitoring loop with SIMPLIFIED frame dumping"""
        print("\n🌀 NEXUS 25D - SIMPLIFIED MONITORING")
        
        # === SETUP PHASE (UNCHANGED) ===
        self.coordinate_space = self._load_coordinate_space(priori_data)
        if not self.coordinate_space:
            print("❌ No coordinate space loaded")
            return
        
        selector = SpideyCoordinateSelector(
            coordinate_space=self.coordinate_space,
            selected_coords=None,
            screen_width=1200,
            screen_height=800
        )
        self.selected_coordinates = selector.run_selection()
        
        if not self.selected_coordinates:
            print("❌ No coordinates selected")
            return
        
        print(f"\n🎯 {len(self.selected_coordinates)} coordinates selected")
        
        if not self.attach_to_browser():
            print("❌ Failed to attach to browser")
            return
        
        self.session_start_time = time.time()
        
        self.axon_network = AxonNetwork(
            nexus_coordinate_space={coord: self.coordinate_space.get(coord, {}) 
                                    for coord in self.selected_coordinates},
            session_start_time=self.session_start_time
        )
        
        print("\n🧠 CREATING INITIAL NEURONS...")
        self._initialize_from_priori(priori_data, use_unknown_for_all=use_unknown_for_all)
        
        if not self.neurons:
            print("❌ No neurons created")
            return
        
        for coord, neuron in self.neurons.items():
            self.axon_network.register_neuron(neuron, {})
            print(f"✅ {neuron.id} at {coord}")
        
        print(f"🎯 {len(self.neurons)} neurons ready")
        
        # === START NEURON THREADS (UNCHANGED) ===
        print("\n🚀 STARTING NEURON THREADS")
        self._start_all_neuron_threads()
        
        # === START ENTER KEY LISTENER (UNCHANGED) ===
        self._start_enter_key_listener()
        
        print("\n" + "="*70)
        print("🌀 MONITORING ACTIVE")
        print("- Press ENTER to stop")
        print(f"- Dumping frames every {self.dump_interval}s to {self.frames_dir}")
        print(f"- {len(self.neurons)} neurons active")
        print("="*70)
        
        self.monitoring_active = True
        self.last_dump_time = time.time()
        
        try:
            while self.monitoring_active:
                # === 1. PROCESS NEXUS AXONS ===
                self._process_nexus_axons_simple()
                
                # === 2. DUMP VISUALIZATION FRAME ===
                self._dump_visualization_frame()
                
                # === 3. CHECK FOR ENTER KEY ===
                if self._check_for_enter_key():
                    print("\n⏹️ ENTER detected - Stopping...")
                    self.monitoring_active = False
                    break
                
                # Small delay
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Ctrl+C - Emergency shutdown!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # === CLEAN SHUTDOWN ===
            self._stop_enter_key_listener()
            self._perform_graceful_shutdown()
    
    def _process_nexus_axons_simple(self):
        """Simple axon processing without heartbeat tracking"""
        axon_counts = {'growth': 0, 'void': 0, 'total': 0}
        
        # Process axons until queue is empty
        while True:
            axon = self.axon_network.get_next_nexus_axon()
            if not axon:
                break
            
            axon_type = axon.get('axon_type', '')
            axon_counts['total'] += 1
            
            if axon_type == 'GROWTH_SIGNAL':
                self._handle_growth_signal(axon)
                axon_counts['growth'] += 1
            elif axon_type == 'SYSTEM_ALERT':
                data = axon.get('data', {})
                alert_type = data.get('alert_type', 'UNKNOWN')
                print(f"🚨 System alert: {alert_type}")
        
        # Simple status update
        if axon_counts['total'] > 0:
            status = f"📨 Axons: {axon_counts['total']}"
            if axon_counts['growth'] > 0:
                status += f" 🌱{axon_counts['growth']}"
            print(f"  {status}")
    
    # ===== KEEP ALL EXISTING UTILITY METHODS =====
    
    def _load_coordinate_space(self, priori_data: Dict) -> Dict[Tuple, Dict]:
        """UNCHANGED - Load coordinate space from priori data"""
        # ... keep existing implementation ...
        pass
    
    def attach_to_browser(self, port="9223") -> bool:
        """UNCHANGED - Attach to Chrome debug port"""
        # ... keep existing implementation ...
        pass
    
    def _determine_priori_pattern(self, coord_data: Dict) -> str:
        """UNCHANGED - Determine initial ROSE pattern"""
        # ... keep existing implementation ...
        pass
    
    def _initialize_from_priori(self, priori_data: Dict, use_unknown_for_all: bool = False):
        """UNCHANGED - Initialize neurons from priori data"""
        # ... keep existing implementation ...
        pass
    
    def _start_all_neuron_threads(self):
        """UNCHANGED - Start all neurons in their own threads"""
        # ... keep existing implementation ...
        pass
    
    def _check_and_start_new_neurons(self):
        """UNCHANGED - Start threads for new neurons"""
        # ... keep existing implementation ...
        pass
    
    def _handle_growth_signal(self, axon: Dict):
        """UNCHANGED - Create neuron at requested coordinate"""
        # ... keep existing implementation ...
        pass
    
    def _start_enter_key_listener(self):
        """UNCHANGED - Start background thread to listen for ENTER"""
        # ... keep existing implementation ...
        pass
    
    def _stop_enter_key_listener(self):
        """UNCHANGED - Stop the ENTER key listener thread"""
        # ... keep existing implementation ...
        pass
    
    def _check_for_enter_key(self) -> bool:
        """UNCHANGED - SIMPLE Enter key check"""
        # ... keep existing implementation ...
        pass
    
    def _perform_graceful_shutdown(self):
        """UNCHANGED with minor cleanup - Simple graceful shutdown"""
        print("\n" + "="*60)
        print("🌀 NEXUS SHUTDOWN")
        print("="*60)
        
        # Stop monitoring
        self.monitoring_active = False
        
        # Destroy neurons
        print("💀 Destroying neurons...")
        neurons_destroyed = 0
        for coord, neuron in list(self.neurons.items()):
            try:
                neuron.processing_phase = "DESTROYED"
                neurons_destroyed += 1
            except:
                pass
        
        print(f"  Destroyed {neurons_destroyed} neurons")
        
        # Final frame dump
        print("📤 Final frame dump...")
        self._dump_visualization_frame()
        
        # Close browser
        if self.driver:
            try:
                self.driver.quit()
                print("🧹 Browser closed")
            except:
                pass
        
        # Summary
        print(f"\n✅ Shutdown complete")
        print(f"   Frames: {self.frame_counter}")
        print(f"   Directory: {self.session_dir}")
        print("="*60)
    
    def cleanup(self):
        """UNCHANGED - Cleanup resources"""
        print("\n🧹 Cleaning up Nexus...")
        self.monitoring_active = False
        
        # Stop enter key listener
        self._stop_enter_key_listener()
        
        # Close browser if still open
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except:
                pass
        
        print("✅ Nexus cleanup complete")
        




# ===== MAIN EXECUTION =====
def main_enhanced():
    """MINIMAL MAIN FUNCTION - NO CONFLICTS"""
    parser = argparse.ArgumentParser(description='🕷️ Spidey Bot - DOM Monitoring')
    parser.add_argument('--priori', type=str, required=True, 
                       help='Priori filename from Venger')
    parser.add_argument('--port', type=str, default='9223',
                       help='Chrome debug port (default: 9223)')
    parser.add_argument('--test-unknown', action='store_true',
                       help='Test mode: all neurons as UNKNOWN pattern')
    
    args = parser.parse_args()
    
    print("🕷️ SPIDEY BOT - COSMIC NEURAL NETWORK")
    print(f"📁 Priori file: {args.priori}")
    print(f"🔌 Port: {args.port}")
    
    # Load priori data
    devengers_path = "TheDevengers"
    if not os.path.exists(devengers_path):
        os.makedirs(devengers_path, exist_ok=True)
    
    priori_path = os.path.join(devengers_path, args.priori)
    
    if not os.path.exists(priori_path):
        print(f"❌ Priori file not found: {priori_path}")
        return
    
    try:
        with open(priori_path, 'r') as f:
            priori_data = json.load(f)
        
        total_coords = len(priori_data.get('coordinate_space', {}))
        print(f"✅ Loaded priori: {total_coords} coordinates")
    except Exception as e:
        print(f"❌ Failed to load priori: {e}")
        return
    
    # Create Nexus instance
    nexus = Nexus()
    
    try:
        print(f"\n{'='*60}")
        print("🚀 STARTING MONITORING")
        print(f"{'='*60}")
        
        # Get test mode from command line ONLY
        use_unknown_for_all = args.test_unknown
        if use_unknown_for_all:
            print("🧪 TEST MODE: All neurons as UNKNOWN")
        else:
            print("🎯 NORMAL MODE: Using priori patterns")
        
        # === SINGLE ENTRY POINT ===
        # Everything happens inside nexus.run_monitoring()
        # It will:
        # 1. Load coordinate space
        # 2. Run SpiderBot selection
        # 3. Attach to browser
        # 4. Create neurons
        # 5. Start coordination loop
        nexus.run_monitoring(priori_data, use_unknown_for_all=use_unknown_for_all)
        
        # === AFTER MONITORING ===
        print(f"\n{'='*60}")
        print("✅ MONITORING COMPLETE")
        print(f"{'='*60}")
        
        # Show session info
        if hasattr(nexus, 'session_dir'):
            session_name = os.path.basename(nexus.session_dir)
            print(f"📊 Session data: {nexus.session_dir}")
            print(f"🎬 Replay: python cosmic_visualizer.py --session {session_name}")
        
    except KeyboardInterrupt:
        print("\n🛑 Monitoring cancelled")
    except Exception as e:
        print(f"\n❌ Monitoring failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if hasattr(nexus, 'cleanup'):
            nexus.cleanup()
        print("\n🏁 Session ended")

# ===== MAIN ENTRY POINT =====
if __name__ == "__main__":
    main_enhanced()

