#!/usr/bin/env python3
"""
🧠 NEXUS 25D NEURAL VISUALIZER - COMPLETE VERSION
Full feature set with timeline, draggable legend, and all original functionality
"""

import pygame
import json
import time
import math
import os
import sys
import random
from typing import Dict, List, Tuple, Any, Optional, Deque, Set
from collections import deque, defaultdict
from dataclasses import dataclass, field
import numpy as np

# ===== NEXUS COLOR SYSTEMS =====

PATTERN_COLORS = {
    'ACTION_ELEMENT': (155, 0, 60),       # Burgundy
    'DATA_INPUT': (60, 65, 72),          # Metallic Grey
    'CONTEXT_ELEMENT': (0, 47, 108),     # Neon Purple
    'STRUCTURAL': (30, 130, 80),         # Forest Green  
    'UNKNOWN': (0, 0, 0),                # Royal Navy (distinctive for UNKNOWN)
    'NEXUS': (255, 255, 255),            # Brighter Gold
}

# Eigen value colors (α, β, γ, ζ)
EIGEN_COLORS = {
    'alpha': (100, 255, 100),    # Green - α eigen value
    'beta': (100, 200, 255),     # Blue - β eigen value  
    'gamma': (255, 100, 255),    # Purple - γ eigen value (NEW for UNKNOWN)
    'zeta': (255, 255, 100),     # Yellow - ζ eigen value
}

# State colors from Nexus health states
STATE_COLORS = {
    'STABLE': (100, 255, 100),      # Green - High confidence
    'LEARNING': (100, 200, 255),    # Blue - Active learning
    'NOISY': (255, 255, 100),       # Yellow - Uncertain
    'RIGID': (255, 100, 100),       # Red - Over-constrained
    'DEAD': (150, 150, 150),        # Gray - No activity
    'CONFUSED': (159, 0, 255),      # Purple - Conflicting signals
    'UNKNOWN': (200, 200, 200),     # Light Gray - Unknown state
    'GAMMA_ACTIVE': (255, 50, 255), # Bright Purple - γ active
    'GAMMA_LEARNING': (200, 100, 255), # Lavender - γ learning
    'UNKNOWN_EXPLORING': (100, 100, 255), # Blue - Unknown exploring
}

# Axon colors for Nexus-specific axon types
AXON_COLORS = {
    'HEARTBEAT': (200, 200, 200),           # Gray pulse
    'GROWTH_SIGNAL': (100, 255, 100),       # Green growth
    'SYSTEM_ALERT': (255, 100, 100),        # Red alert
    'MATRIX_UPDATE': (100, 200, 255),       # Blue matrix update
    'GAMMA_UPDATE': (255, 100, 255),        # Purple γ update
    'VOID_SIGNAL': (180, 100, 255),         # Purple void
}

# State pulse speeds for Nexus states
STATE_PULSE_SPEEDS = {
    'STABLE': 0.3,      # Slow pulse (very stable)
    'LEARNING': 0.1,    # Medium pulse (active learning)
    'NOISY': 0.01,      # Faster pulse (uncertain)
    'RIGID': 0.2,       # Medium-slow (over-constrained)
    'DEAD': 0.0,        # No pulse (dead)
    'CONFUSED': 0.1,    # Very fast pulse (conflicted)
    'UNKNOWN': 0.25,    # Medium pulse
    'GAMMA_ACTIVE': 0.15,   # Active γ pulse
    'GAMMA_LEARNING': 0.2,  # Learning γ pulse
}

# ===== TIMELINE SEQUENCER =====
# Add these before the NexusVisualizer class definition

import numpy as np
import pygame
import time
import json
import os
import math
import random
from collections import deque, defaultdict

# Color definitions
PATTERN_COLORS = {
    'ACTION_ELEMENT': (255, 100, 100),
    'DATA_INPUT': (100, 180, 255),
    'CONTEXT_ELEMENT': (255, 200, 100),
    'STRUCTURAL': (150, 255, 150),
    'UNKNOWN': (200, 200, 200),
}

STATE_COLORS = {
    'STABLE': (100, 255, 100),
    'LEARNING': (255, 200, 100),
    'NOISY': (255, 255, 100),
    'RIGID': (255, 100, 100),
    'CONFUSED': (255, 100, 255),
    'DEAD': (100, 100, 100),
    'UNKNOWN': (200, 200, 200),
}

EIGEN_COLORS = {
    'alpha': (255, 100, 100),
    'beta': (100, 200, 255),
    'gamma': (255, 100, 255),
    'zeta': (100, 255, 200),
}

AXON_COLORS = {
    'ACTIVATION': (255, 200, 100),
    'INHIBITION': (100, 180, 255),
    'UNKNOWN': (200, 200, 200),
}

# Supporting classes
class VisualNeuron:
    """Visual representation of a neuron"""
    def __init__(self, neuron_id, coordinate, pattern, confidence, current_state,
                 eigen_alpha=0.0, eigen_beta=0.0, eigen_gamma=0.0, eigen_zeta=0.0):
        self.id = neuron_id
        self.coordinate = coordinate
        self.pattern = pattern
        self.confidence = confidence
        self.current_state = current_state
        self.eigen_alpha = eigen_alpha
        self.eigen_beta = eigen_beta
        self.eigen_gamma = eigen_gamma
        self.eigen_zeta = eigen_zeta
        
        self.position = None
        self.is_unknown_pattern = False
        self.has_gamma_update = False
        self.health_status = 'UNKNOWN'
        self.health_score = 0.0
        self.cycle = 0
        self.pulse_value = 0.0
        self.pulse_speed = random.uniform(2.0, 4.0)
    
    def update_pulse(self, delta_time):
        """Update pulsing animation"""
        self.pulse_value += delta_time * self.pulse_speed
        if self.pulse_value > math.pi * 2:
            self.pulse_value -= math.pi * 2

class TimelineSequencer:
    """Timeline control for replay mode"""
    def __init__(self):
        self.is_playing = False
        self.playback_speed = 1.0
        self.current_time = 0.0
        self.last_frame_time = 0.0
        self.frame_interval = 0.1  # 10 FPS base
    
    def update(self, delta_time):
        """Update timeline"""
        if self.is_playing:
            self.current_time += delta_time * self.playback_speed
    
    def should_advance_frame(self):
        """Check if we should advance to next frame"""
        if self.current_time - self.last_frame_time >= self.frame_interval:
            self.last_frame_time = self.current_time
            return True
        return False
    
    def get_progress(self):
        """Get playback progress (0 to 1)"""
        return self.current_time % 1.0

class SessionBrowser:
    """Session file browser"""
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.sessions = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_items = 15



    def select_next(self):
        """Select next session"""
        if self.sessions:
            self.selected_index = min(self.selected_index + 1, len(self.sessions) - 1)
            self._adjust_scroll()
    
    def select_prev(self):
        """Select previous session"""
        if self.sessions:
            self.selected_index = max(self.selected_index - 1, 0)
            self._adjust_scroll()
    
    def scan_sessions(self):
        """Scan for session directories"""
        self.sessions = []
        
        if not os.path.exists(self.base_dir):
            return
        
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            if os.path.isdir(item_path):
                # Check if it's a nexus session
                if item.startswith('nexus_'):
                    # Check for frames directory
                    frames_dir = os.path.join(item_path, 'frames')
                    if os.path.exists(frames_dir):
                        # Count frames_*.json files
                        frame_files = [f for f in os.listdir(frames_dir) if f.startswith('frame_') and f.endswith('.json')]
                        frame_count = len(frame_files)
                    else:
                        frame_count = 0
                    
                    if frame_count > 0:
                        # Get modification time
                        mod_time = os.path.getmtime(item_path)
                        time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(mod_time))
                        
                        self.sessions.append({
                            'id': item,
                            'path': item_path,
                            'frame_count': frame_count,
                            'modified': mod_time,
                            'time_str': time_str,
                            'has_frames_dir': os.path.exists(frames_dir)
                        })
        
        # Sort by modification time (newest first)
        self.sessions.sort(key=lambda x: x['modified'], reverse=True)
        
    def _adjust_scroll(self):
        """Adjust scroll to keep selected item visible"""
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_items:
            self.scroll_offset = self.selected_index - self.visible_items + 1
    
    def get_selected_session(self):
        """Get currently selected session"""
        if self.sessions and 0 <= self.selected_index < len(self.sessions):
            return self.sessions[self.selected_index]
        return None

class Particle:
    """Particle for visual effects"""
    def __init__(self, position, color, velocity, lifetime=1.0):
        self.position = position
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.age = 0.0
        self.size = random.uniform(2.0, 6.0)
        
# ===== NEXUS VISUALIZER - COMPLETE WITH STATISTICS PAGE =====
class DraggableWindow:
    """Universal draggable window system for all panels"""
    def __init__(self, x, y, width, height, title="", min_width=200, min_height=150):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.min_width = min_width
        self.min_height = min_height
        self.visible = True
        
        # Dragging state
        self.dragging = False
        self.resizing = False
        self.drag_offset = (0, 0)
        self.resize_start_size = (0, 0)
        self.resize_start_pos = (0, 0)
        
        # Title bar area (top 30px)
        self.title_bar_rect = pygame.Rect(x, y, width, 30)
        
        # Resize handle (bottom-right 20x20px)
        self.resize_handle_rect = pygame.Rect(
            x + width - 20, 
            y + height - 20, 
            20, 20
        )
        
        # Content area (inside padding)
        self.content_rect = pygame.Rect(
            x + 5,
            y + 35,
            width - 10,
            height - 45
        )
    

    def handle_event(self, event, mouse_pos):
        """Handle mouse events for dragging/resizing"""
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.title_bar_rect.collidepoint(mouse_pos):
                    self.dragging = True
                    self.drag_offset = (
                        mouse_pos[0] - self.rect.x,
                        mouse_pos[1] - self.rect.y
                    )
                    return True
                elif self.resize_handle_rect.collidepoint(mouse_pos):
                    self.resizing = True
                    self.resize_start_size = (self.rect.width, self.rect.height)
                    self.resize_start_pos = mouse_pos
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                self.resizing = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = mouse_pos[0] - self.drag_offset[0]
                self.rect.y = mouse_pos[1] - self.drag_offset[1]
                self._update_sub_rects()
                return True
            elif self.resizing:
                dx = mouse_pos[0] - self.resize_start_pos[0]
                dy = mouse_pos[1] - self.resize_start_pos[1]
                
                new_width = max(self.min_width, self.resize_start_size[0] + dx)
                new_height = max(self.min_height, self.resize_start_size[1] + dy)
                
                self.rect.width = new_width
                self.rect.height = new_height
                self._update_sub_rects()
                return True
        
        return False
    
    def _update_sub_rects(self):
        """Update all sub-rectangles when window moves/resizes"""
        self.title_bar_rect = pygame.Rect(
            self.rect.x, 
            self.rect.y, 
            self.rect.width, 
            30
        )
        self.resize_handle_rect = pygame.Rect(
            self.rect.x + self.rect.width - 20,
            self.rect.y + self.rect.height - 20,
            20, 20
        )
        self.content_rect = pygame.Rect(
            self.rect.x + 5,
            self.rect.y + 35,
            max(0, self.rect.width - 10),
            max(0, self.rect.height - 45)
        )
    
    def draw(self, screen, font=None, content_callback=None):
        """Draw the window with title bar and resize handle"""
        if not self.visible:
            return
            
        # Window background
        window_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(window_surface, (20, 25, 40, 240), 
                        window_surface.get_rect(), border_radius=8)
        pygame.draw.rect(window_surface, (60, 80, 120, 150),
                        window_surface.get_rect(), 2, border_radius=8)
        screen.blit(window_surface, self.rect)
        
        # Title bar
        title_bar_surface = pygame.Surface((self.rect.width, 30), pygame.SRCALPHA)
        pygame.draw.rect(title_bar_surface, (40, 50, 80, 200),
                        title_bar_surface.get_rect(), border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.rect(title_bar_surface, (80, 100, 160, 150),
                        title_bar_surface.get_rect(), 1, border_top_left_radius=8, border_top_right_radius=8)
        screen.blit(title_bar_surface, (self.rect.x, self.rect.y))
        
        # Title text
        if self.title and font:
            title_text = font.render(self.title, True, (200, 220, 255))
            screen.blit(title_text, (self.rect.x + 10, self.rect.y + 8))
        
        # Close button (X in top-right)
        close_rect = pygame.Rect(
            self.rect.x + self.rect.width - 25,
            self.rect.y + 5,
            20, 20
        )
        pygame.draw.rect(screen, (255, 100, 100, 150), close_rect, border_radius=4)
        if font:
            close_text = font.render("×", True, (255, 255, 255))
            screen.blit(close_text, (close_rect.x + 6, close_rect.y + 2))
        
        # Resize handle (bottom-right triangle)
        resize_points = [
            (self.rect.x + self.rect.width - 5, self.rect.y + self.rect.height - 15),
            (self.rect.x + self.rect.width - 15, self.rect.y + self.rect.height - 5),
            (self.rect.x + self.rect.width - 5, self.rect.y + self.rect.height - 5)
        ]
        pygame.draw.polygon(screen, (100, 120, 180, 200), resize_points)
        
        # Call content callback if provided
        if content_callback:
            content_callback(screen, self.content_rect, self.font if hasattr(self, 'font') else font)

    def toggle_visibility(self):
        """Toggle window visibility"""
        self.visible = not self.visible
    
    def contains_point(self, point):
        """Check if point is inside window"""
        return self.rect.collidepoint(point) and self.visible



class NexusVisualizer:
    """Complete Nexus visualizer with statistics page and proper coordinate placement"""
    
    # Mode constants
    MODE_REPLAY = "replay"
    MODE_LIVE = "live"
    MODE_BROWSER = "browser"
    MODE_LOADING = "loading"
    MODE_STATISTICS = "statistics"  # NEW: Statistics page
    
    def __init__(self, session_id: str = None):
        print("🧠 NEXUS 25D VISUALIZER - COMPLETE VERSION")
        print("=" * 60)
        
        # Initialize Pygame
        pygame.init()
        self.screen_width = 1400
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Nexus 25D Neural Visualizer - Complete")
        
        # Fonts
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.mono_font = pygame.font.Font(None, 18)
        
        # Core systems
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        self.running = True
        
        # Session management
        self.base_dir = "Cognition"
        self.session_id = session_id
        self.session_dir = None
        self.browser = SessionBrowser(self.base_dir)
        
        # Mode and state
        self.mode = self.MODE_BROWSER
        self.browser.scan_sessions()
        
        # Data
        self.frames = []
        self.current_frame_index = 0
        self.current_frame_data = None
        self.neurons = {}  # neuron_id -> VisualNeuron
        self.coordinate_map = {}  # coordinate -> neuron_id
        self.active_neurons = {}  # coordinate -> neuron_data
        self.active_axon_beams = []
        
        # Timeline
        self.timeline = TimelineSequencer()
        self.animation_start_time = 0
        self.last_frame_time = 0
        self.frame_duration = 1.0
        
        # View controls - MATCHING SPIDEY COORDINATE SELECTOR STYLE
        self.pan_x, self.pan_y = 0, 0
        self.zoom = 1.0
        self.cell_size = 25  # Same as SpideyCoordinateSelector
        self.dragging_view = False
        self.drag_start_pos = (0, 0)
        self.drag_start_pan = (0, 0)
        
        # Legend controls
        self.show_legend = True
        self.legend_dragging = False
        self.legend_resizing = False
        self.legend_position = (self.screen_width - 450, 100)
        self.legend_size = (400, 720)
        self.legend_change_mode = False
        self.legend_drag_start = (0, 0)
        self.legend_original_pos = (0, 0)
        self.legend_resize_start = (0, 0)
        self.legend_original_size = (0, 0)
        
        # UI state
        self.show_axons = True
        self.show_grid = True
        self.show_eigen_values = True
        self.show_change_highlights = True
        self.show_processing_states = True
        
        # Hover and selection
        self.hovered_neuron_id = None
        self.selected_neuron_id = None
        self.hovered_button = None
        self.active_button = None
        self.hovered_session_index = None
        self.hover_info = None
        self.last_click_time = 0
        
        # Timeline UI
        self.timeline_handle_rect = None
        self.timeline_button_rects = {}
        
        # Particles
        self.particles = []
        
        # State change highlights
        self.state_change_highlights = []
        
        # Color arrays for pulsing
        self.color_array = None
        self.state_indices = {
            'STABLE': 0, 'LEARNING': 1, 'NOISY': 2, 'RIGID': 3,
            'CONFUSED': 4, 'DEAD': 5, 'UNKNOWN': 6
        }
        self.state_freqs = {
            'STABLE': 20, 'LEARNING': 16, 'NOISY': 12, 
            'RIGID': 4, 'CONFUSED': 8, 'DEAD': 1, 'UNKNOWN': 2
        }
        self._init_color_arrays()
        
        # Statistics data for statistics page
        self.statistics_data = {
            'total_frames': 0,
            'total_neurons': 0,
            'unknown_count': 0,
            'gamma_updated_count': 0,
            'avg_confidence': 0.0,
            'frame_data': [],  # Per-frame statistics for graphing
            'neuron_data': [], # Per-neuron statistics
            'eigen_trends': {}, # Eigen value trends over time
            'session_metrics': {}, # Overall session metrics
        }
        
        # Statistics page state
        self.stat_page_state = {
            'view': 'overview',  # 'overview', 'eigen', 'confidence', 'unknown'
            'time_range': 'all',  # 'all', 'recent', 'early'
            'selected_metric': 'confidence',
            'scroll_offset': 0,
            'graph_points': 100,  # Max points to show on graphs
        }
        
        # UI buttons
        self.ui_buttons = {}
        self._init_ui_buttons()
        
        # Terminal logs
        self.logs = deque(maxlen=50)
        
        # Statistics graph surfaces
        self.graph_surface = None
        self.graph_dirty = True
        # Initialize draggable windows
        self.windows = {}
        
        # Legend window
        self.windows['legend'] = DraggableWindow(
            self.screen_width - 450, 100, 400, 720, 
            "NEXUS 25D LEGEND"
        )
        
        # Stats window (for visualization mode)
        self.windows['stats'] = DraggableWindow(
            20, 120, 320, 180,
            "SESSION STATISTICS"
        )
        
        # Timeline window
        self.windows['timeline'] = DraggableWindow(
            20, self.screen_height - 100, 
            self.screen_width // 3, 80,
            "TIMELINE CONTROLS"
        )
        
        # Logs window
        self.windows['logs'] = DraggableWindow(
            20, self.screen_height - 200,
            400, 180,
            "TERMINAL LOGS")
        # Initialize previous selected neuron tracking
        self.previous_selected_neuron_id = None
        self.dragging_timeline = False
        
        # Initialize windows visibility
        self.windows['legend'].visible = True
        self.windows['stats'].visible = True
        self.windows['timeline'].visible = True
        self.windows['logs'].visible = True
        
        for window in self.windows.values():
            window.font = self.font
        
        print("✅ Visualizer initialized")
    
    # ===== COORDINATE PLACEMENT (MATCHING SPIDEY SELECTOR) =====
    def _coord_to_screen(self, coord, center_x=None, center_y=None):
        """EXACT SpideySelector coordinate placement"""
        if not coord:
            return None
        
        if center_x is None:
            center_x = self.screen_width // 2 + self.pan_x
        if center_y is None:
            center_y = self.screen_height // 2 + self.pan_y
        
        # CRITICAL: SpideySelector uses tuples, your data might be lists
        # Convert to tuple for consistent handling
        if isinstance(coord, list):
            coord_tuple = tuple(coord)
        else:
            coord_tuple = coord
        
        # SPIDEY EXACT LOGIC:
        depth = len(coord_tuple)
        sibling_index = 0
        
        # Get sibling index from last element
        if coord_tuple:
            last_elem = coord_tuple[-1]
            if isinstance(last_elem, (int, float)):
                sibling_index = int(last_elem)
            elif isinstance(last_elem, (list, tuple)) and last_elem:
                # Handle nested coordinates
                if isinstance(last_elem[0], (int, float)):
                    sibling_index = int(last_elem[0])
        
        # SPIDEY EXACT: X = sibling_index * cell_size, Y = depth * cell_size
        x = center_x + sibling_index * 25 * self.zoom  # cell_size=25
        y = center_y + depth * 25 * self.zoom
        
        return (int(x), int(y))

    def update_neuron_positions(self):
        """Update ALL neuron positions after pan/zoom"""
        center_x = self.screen_width // 2 + self.pan_x
        center_y = self.screen_height // 2 + self.pan_y
        
        for neuron in self.neurons.values():
            neuron.position = self._coord_to_screen(neuron.coordinate, center_x, center_y)
            
    def _draw_white_grid(self, center_x, center_y):
        """Draw grid lines EXACTLY like SpideySelector"""
        if not self.show_grid:
            return
            
        # Vertical lines - Spidey's exact range (-30 to 31)
        for i in range(-30, 31):
            x = center_x + i * 25 * self.zoom
            if 50 <= x <= self.screen_width - 50:
                pygame.draw.line(self.screen, (100, 100, 100, 50),
                            (x, 100), (x, self.screen_height - 150), 1)
        
        # Horizontal lines - Spidey's exact range (40)
        for i in range(40):
            y = center_y + i * 25 * self.zoom
            if 100 <= y <= self.screen_height - 150:
                pygame.draw.line(self.screen, (100, 100, 100, 50),
                            (50, y), (self.screen_width - 50, y), 1)
        
        # Axes - thicker lines like Spidey
        pygame.draw.line(self.screen, (150, 150, 150, 100),
                        (center_x, 100), (center_x, self.screen_height - 150), 2)
        pygame.draw.line(self.screen, (150, 150, 150, 100),
                        (50, center_y), (self.screen_width - 50, center_y), 2)
        
        # Depth labels (Spidey style)
        for i in range(0, 40, 5):
            y = center_y + i * 25 * self.zoom
            if 100 <= y <= self.screen_height - 150:
                depth_label = self.small_font.render(f"Depth {i}", True, (180, 180, 180))
                self.screen.blit(depth_label, (center_x - 60, y - 10))
        
        # Sibling labels (Spidey style)
        for i in range(-30, 31, 10):
            x = center_x + i * 25 * self.zoom
            if 50 <= x <= self.screen_width - 50:
                sibling_label = self.small_font.render(f"Sib {i}", True, (180, 180, 180))
                self.screen.blit(sibling_label, (x - 15, center_y + 20))
                
    def _update_particles(self, delta_time: float):
        """Update particle system with physics"""
        active_particles = []
        
        for particle in self.particles[:]:  # Copy for safe iteration
            # Update physics
            particle.age += delta_time
            
            # Apply velocity
            particle.position = (
                particle.position[0] + particle.velocity[0] * delta_time,
                particle.position[1] + particle.velocity[1] * delta_time
            )
            
            # Apply gravity/drag
            drag_factor = 0.95  # Air resistance
            particle.velocity = (
                particle.velocity[0] * drag_factor,
                particle.velocity[1] * drag_factor + 50 * delta_time  # Gravity
            )
            
            # Update size and color
            lifetime_ratio = particle.age / particle.lifetime
            
            # Shrink over time
            particle.size = max(0.5, particle.size * (1.0 - lifetime_ratio * 0.7))
            
            # Fade out
            alpha = int(255 * (1.0 - lifetime_ratio))
            
            # Draw particle if still alive
            if particle.age < particle.lifetime:
                # Create particle surface
                surf_size = int(particle.size * 2)
                surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                
                # Draw particle with glow
                center = (surf_size // 2, surf_size // 2)
                
                # Outer glow
                glow_size = particle.size * 1.5
                glow_alpha = int(alpha * 0.3)
                glow_color = (*particle.color, glow_alpha)
                pygame.draw.circle(surf, glow_color, center, int(glow_size))
                
                # Main particle
                main_color = (*particle.color, alpha)
                pygame.draw.circle(surf, main_color, center, int(particle.size))
                
                # Highlight
                highlight_size = particle.size * 0.4
                highlight_color = (255, 255, 255, int(alpha * 0.8))
                highlight_pos = (
                    center[0] - highlight_size * 0.7,
                    center[1] - highlight_size * 0.7
                )
                pygame.draw.circle(surf, highlight_color, 
                                (int(highlight_pos[0]), int(highlight_pos[1])), 
                                int(highlight_size))
                
                # Blit to screen
                self.screen.blit(surf, 
                            (particle.position[0] - surf_size // 2,
                                particle.position[1] - surf_size // 2))
                
                active_particles.append(particle)
        
        self.particles = active_particles

    def _draw_white_grid(self, center_x, center_y):
        """Draw white grid lines matching SpideyCoordinateSelector style"""
        if not self.show_grid:
            return
            
        # Vertical lines
        for i in range(-30, 31):
            x = center_x + i * self.cell_size * self.zoom
            if 50 <= x <= self.screen_width - 50:
                pygame.draw.line(self.screen, (100, 100, 100, 50),
                               (x, 100), (x, self.screen_height - 150), 1)
        
        # Horizontal lines
        for i in range(40):
            y = center_y + i * self.cell_size * self.zoom
            if 100 <= y <= self.screen_height - 150:
                pygame.draw.line(self.screen, (100, 100, 100, 50),
                               (50, y), (self.screen_width - 50, y), 1)
        
        # Axes - thicker lines
        pygame.draw.line(self.screen, (150, 150, 150, 100),
                        (center_x, 100), (center_x, self.screen_height - 150), 2)
        pygame.draw.line(self.screen, (150, 150, 150, 100),
                        (50, center_y), (self.screen_width - 50, center_y), 2)
    
    def _draw_connections(self):
        """Draw parent-child connections - FIXED"""
        if not self.show_axons:
            return
        
        center_x = self.screen_width // 2 + self.pan_x
        center_y = self.screen_height // 2 + self.pan_y
        
        for neuron in self.neurons.values():
            coord = neuron.coordinate
            if not coord or len(coord) <= 1:  # Skip root/level 1 nodes
                continue
            
            # Get parent coordinate
            parent_coord = coord[:-1]
            
            # CRITICAL: Convert both to tuples for dictionary lookup
            if isinstance(coord, list):
                coord_tuple = tuple(coord)
            else:
                coord_tuple = coord
            
            if isinstance(parent_coord, list):
                parent_coord_tuple = tuple(parent_coord)
            else:
                parent_coord_tuple = parent_coord
            
            # Find parent neuron by coordinate
            parent_id = self.coordinate_map.get(parent_coord_tuple)
            if not parent_id or parent_id not in self.neurons:
                continue
            
            parent = self.neurons[parent_id]
            
            # Get screen positions
            child_pos = self._coord_to_screen(coord, center_x, center_y)
            parent_pos = self._coord_to_screen(parent_coord, center_x, center_y)
            
            if not child_pos or not parent_pos:
                continue
            
            # Draw connection
            color = (120, 140, 180, 40)  # Spidey's connection color
            pygame.draw.line(self.screen, color, parent_pos, child_pos, 1)
            
            # Draw red hover connection if needed
            if (self.hovered_neuron_id and 
                (neuron.id == self.hovered_neuron_id or parent.id == self.hovered_neuron_id)):
                self._draw_red_hover_connection(parent_pos, child_pos)
                
    def _draw_hover_path_connections(self, center_x, center_y, hover_coord):
        """Draw red hover path for hovered coordinate (Spidey exact)"""
        # Get all connections that involve the hovered coordinate or its children
        for neuron in self.neurons.values():
            coord = neuron.coordinate
            if len(coord) <= 1:
                continue
            
            parent_coord = coord[:-1]
            
            # Check if this connection is part of hover path
            is_hover_connection = False
            
            # Convert to tuples for comparison
            if isinstance(coord, list):
                coord_tuple = tuple(coord)
            else:
                coord_tuple = coord
            
            if isinstance(parent_coord, list):
                parent_coord_tuple = tuple(parent_coord)
            else:
                parent_coord_tuple = parent_coord
            
            if isinstance(hover_coord, list):
                hover_coord_tuple = tuple(hover_coord)
            else:
                hover_coord_tuple = hover_coord
            
            # Check if connection involves hovered coordinate
            if coord_tuple == hover_coord_tuple or parent_coord_tuple == hover_coord_tuple:
                is_hover_connection = True
            # Check if connection is to/from a child of hovered
            elif (len(coord_tuple) > len(hover_coord_tuple) and 
                coord_tuple[:len(hover_coord_tuple)] == hover_coord_tuple):
                is_hover_connection = True
            elif (len(parent_coord_tuple) > len(hover_coord_tuple) and 
                parent_coord_tuple[:len(hover_coord_tuple)] == hover_coord_tuple):
                is_hover_connection = True
            
            if is_hover_connection:
                child_pos = self._coord_to_screen(coord, center_x, center_y)
                parent_pos = self._coord_to_screen(parent_coord, center_x, center_y)
                
                if child_pos and parent_pos:
                    self._draw_spidey_red_hover_connection(parent_pos, child_pos)

    def _draw_spidey_red_hover_connection(self, start_pos, end_pos):
        """Draw EXACT Spidey red hover connection with glow and arrow"""
        current_time = time.time()
        
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = max(1, math.sqrt(dx*dx + dy*dy))
        angle = math.atan2(dy, dx)
        
        pulse = 0.5 + 0.5 * math.sin(current_time * 3)
        
        # Draw glow (Spidey's exact glow)
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
        
        # Draw solid line (Spidey's exact red)
        pygame.draw.line(self.screen, (220, 60, 80), start_pos, end_pos, 3)
        
        # Draw arrow (Spidey style)
        arrow_distance = 0.8
        arrow_x = start_pos[0] + dx * arrow_distance
        arrow_y = start_pos[1] + dy * arrow_distance
        
        arrow_text = "▶"
        arrow_surface = self.small_font.render(arrow_text, True, (255, 200, 200, int(255 * pulse)))
        arrow_angle = math.degrees(-angle) - 90
        arrow_rotated = pygame.transform.rotate(arrow_surface, arrow_angle)
        arrow_rect = arrow_rotated.get_rect(center=(int(arrow_x), int(arrow_y)))
        self.screen.blit(arrow_rotated, arrow_rect)

    def _is_child_of_hovered(self, coord, hover_coord):
        """Check if coordinate is a child of hovered node (Spidey exact)"""
        if not hover_coord:
            return False
        
        if len(coord) <= len(hover_coord):
            return False
        
        # Convert both to tuples for comparison
        if isinstance(coord, list):
            coord_tuple = tuple(coord)
        else:
            coord_tuple = coord
        
        if isinstance(hover_coord, list):
            hover_coord_tuple = tuple(hover_coord)
        else:
            hover_coord_tuple = hover_coord
        
        return coord_tuple[:len(hover_coord_tuple)] == hover_coord_tuple

    def _draw_red_hover_connection(self, start_pos, end_pos):
        """Draw red hover connection matching Spidey style"""
        current_time = time.time()
        
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        length = max(1, math.sqrt(dx*dx + dy*dy))
        angle = math.atan2(dy, dx)
        
        pulse = 0.5 + 0.5 * math.sin(current_time * 3)
        
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
        
        # Draw solid line
        pygame.draw.line(self.screen, (220, 60, 80), start_pos, end_pos, 3)
        
    def _is_child_of_hovered(self, coord, hover_coord):
        """Check if coordinate is a child of hovered node"""
        if not hover_coord:
            return False
        
        if len(coord) <= len(hover_coord):
            return False
        
        # Convert both to tuples for comparison
        if isinstance(coord, list):
            coord_tuple = tuple(coord)
        else:
            coord_tuple = coord
        
        if isinstance(hover_coord, list):
            hover_coord_tuple = tuple(hover_coord)
        else:
            hover_coord_tuple = hover_coord
        
        return coord_tuple[:len(hover_coord_tuple)] == hover_coord_tuple
            
      
    # ===== STATISTICS PAGE METHODS =====
    
    def _switch_to_statistics_mode(self):
        """Switch to statistics visualization mode"""
        if not self.frames:
            self._add_log("⚠️ No data loaded for statistics")
            return
        
        self.mode = self.MODE_STATISTICS
        self._analyze_statistics_data()
        self.graph_dirty = True
        self._add_log("📊 Switched to Statistics Mode")

    def _analyze_statistics_data(self):
        """Analyze frame data for statistics display"""
        if not self.frames:
            return
        
        self.statistics_data['frame_data'] = []
        self.statistics_data['neuron_data'] = []
        self.statistics_data['eigen_trends'] = {
            'alpha': [], 'beta': [], 'gamma': [], 'zeta': []
        }
        
        # Helper function to convert ANYTHING to float
        def safe_float(value, default=0.0):
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return float(value)
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Helper function to convert timestamp
        def safe_timestamp(value):
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        
        # Process each frame
        for frame in self.frames:
            frame_stats = {
                'frame': frame.get('frame', 0),
                'timestamp': safe_timestamp(frame.get('timestamp', 0)),  # CONVERT TIMESTAMP
                'total_neurons': len(frame.get('neurons', [])),
                'total_axons': len(frame.get('axons', [])),
                'unknown_count': 0,
                'gamma_updated_count': 0,
                'avg_confidence': 0.0,
                'eigen_alpha_sum': 0.0,
                'eigen_beta_sum': 0.0,
                'eigen_gamma_sum': 0.0,
                'eigen_zeta_sum': 0.0,
                'neuron_states': defaultdict(int),
            }
            
            neurons = frame.get('neurons', [])
            if neurons:
                confidences = []
                for neuron in neurons:
                    # Convert confidence to float
                    confidence = safe_float(neuron.get('confidence', 0.0))
                    confidences.append(confidence)
                    
                    # Count unknowns
                    if neuron.get('pattern') == 'UNKNOWN':
                        frame_stats['unknown_count'] += 1
                    
                    # Count gamma updates
                    unknown_specific = neuron.get('unknown_specific', {})
                    if unknown_specific.get('has_gamma_update', False):
                        frame_stats['gamma_updated_count'] += 1
                    
                    # Sum eigen values - use safe_float
                    eigen_system = neuron.get('eigen_system', {})
                    
                    frame_stats['eigen_alpha_sum'] += safe_float(eigen_system.get('alpha', 0.0))
                    frame_stats['eigen_beta_sum'] += safe_float(eigen_system.get('beta', 0.0))
                    frame_stats['eigen_gamma_sum'] += safe_float(eigen_system.get('gamma', 0.0))
                    frame_stats['eigen_zeta_sum'] += safe_float(eigen_system.get('zeta', 0.0))
                    
                    # Track states
                    state = neuron.get('current_state', 'UNKNOWN')
                    frame_stats['neuron_states'][state] += 1
                
                frame_stats['avg_confidence'] = sum(confidences) / len(confidences) if confidences else 0.0
            
            self.statistics_data['frame_data'].append(frame_stats)
            
            # Update eigen trends
            if neurons:
                self.statistics_data['eigen_trends']['alpha'].append(
                    frame_stats['eigen_alpha_sum'] / len(neurons))
                self.statistics_data['eigen_trends']['beta'].append(
                    frame_stats['eigen_beta_sum'] / len(neurons))
                self.statistics_data['eigen_trends']['gamma'].append(
                    frame_stats['eigen_gamma_sum'] / len(neurons))
                self.statistics_data['eigen_trends']['zeta'].append(
                    frame_stats['eigen_zeta_sum'] / len(neurons))
        
        # Calculate overall metrics
        if self.statistics_data['frame_data']:
            last_frame = self.statistics_data['frame_data'][-1]
            first_frame = self.statistics_data['frame_data'][0]
            
            # Use safe_timestamp for duration calculation
            last_timestamp = safe_timestamp(last_frame['timestamp'])
            first_timestamp = safe_timestamp(first_frame['timestamp'])
            session_duration = last_timestamp - first_timestamp if len(self.statistics_data['frame_data']) > 1 else 0
            
            self.statistics_data['session_metrics'] = {
                'total_frames': len(self.statistics_data['frame_data']),
                'peak_neurons': max(f['total_neurons'] for f in self.statistics_data['frame_data']),
                'avg_neurons': sum(f['total_neurons'] for f in self.statistics_data['frame_data']) / len(self.statistics_data['frame_data']),
                'peak_unknown': max(f['unknown_count'] for f in self.statistics_data['frame_data']),
                'final_confidence': safe_float(last_frame['avg_confidence']),
                'final_unknown': last_frame['unknown_count'],
                'session_duration': session_duration,
            }
        
        self._add_log(f"📈 Analyzed {len(self.statistics_data['frame_data'])} frames for statistics")
        
    def _draw_confidence_statistics(self):
        """Draw confidence statistics and trends"""
        if not self.statistics_data['frame_data']:
            no_data = self.font.render("No confidence data available", True, (200, 200, 200))
            self.screen.blit(no_data, (self.screen_width // 2 - no_data.get_width() // 2, 200))
            return
        
        # Left panel: Confidence distribution
        panel_x = 20
        panel_y = 180
        panel_width = 400
        panel_height = 300
        
        # Panel background
        surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (panel_x, panel_y))
        
        # Title
        title = self.font.render("CONFIDENCE DISTRIBUTION", True, (255, 255, 180))
        self.screen.blit(title, (panel_x + 20, panel_y + 20))
        
        # Get current frame confidence data
        current_frame = self.statistics_data['frame_data'][-1] if self.statistics_data['frame_data'] else {}
        avg_confidence = current_frame.get('avg_confidence', 0.0)
        
        # Confidence gauge
        gauge_x = panel_x + panel_width // 2
        gauge_y = panel_y + 100
        gauge_radius = 80
        
        # Draw gauge background
        for i in range(0, 100, 10):
            angle = i * 3.6 * math.pi / 180
            start_angle = math.pi * 1.2 + angle
            end_angle = start_angle + 3.6 * 10 * math.pi / 180
            
            # Color based on confidence level
            if i < 40:
                color = (255, 100, 100, 100)  # Red
            elif i < 70:
                color = (255, 255, 100, 100)  # Yellow
            else:
                color = (100, 255, 100, 100)  # Green
            
            pygame.draw.arc(self.screen, color, 
                        (gauge_x - gauge_radius, gauge_y - gauge_radius, 
                        gauge_radius * 2, gauge_radius * 2),
                        start_angle, end_angle, 10)
        
        # Draw needle
        needle_angle = math.pi * 1.2 + (avg_confidence * 180) * math.pi / 180
        needle_x = gauge_x + math.cos(needle_angle) * gauge_radius * 0.9
        needle_y = gauge_y + math.sin(needle_angle) * gauge_radius * 0.9
        
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (gauge_x, gauge_y), (needle_x, needle_y), 4)
        pygame.draw.circle(self.screen, (50, 50, 80), (gauge_x, gauge_y), 10)
        pygame.draw.circle(self.screen, (255, 255, 255), (gauge_x, gauge_y), 10, 2)
        
        # Confidence value
        confidence_text = f"{avg_confidence:.3f}"
        confidence_surf = self.font.render(confidence_text, True, self._confidence_color(avg_confidence))
        confidence_rect = confidence_surf.get_rect(center=(gauge_x, gauge_y))
        self.screen.blit(confidence_surf, confidence_rect)
        
        # Labels
        low_text = self.small_font.render("Low", True, (255, 100, 100))
        high_text = self.small_font.render("High", True, (100, 255, 100))
        self.screen.blit(low_text, (gauge_x - gauge_radius - 20, gauge_y + 10))
        self.screen.blit(high_text, (gauge_x + gauge_radius, gauge_y + 10))
        
        # Right panel: Confidence trend graph
        graph_x = panel_x + panel_width + 20
        graph_y = panel_y
        graph_width = self.screen_width - graph_x - 20
        graph_height = panel_height
        
        # Background
        surf = pygame.Surface((graph_width, graph_height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (graph_x, graph_y))
        
        # Title
        title = self.font.render("CONFIDENCE TREND OVER TIME", True, (255, 255, 180))
        self.screen.blit(title, (graph_x + 20, graph_y + 20))
        
        # Draw confidence trend graph
        self._draw_confidence_trend_graph(graph_x + 20, graph_y + 60, graph_width - 40, graph_height - 100)
        
        # Bottom panel: Detailed statistics
        stats_y = panel_y + panel_height + 20
        stats_height = self.screen_height - stats_y - 150
        
        self._draw_confidence_details(20, stats_y, self.screen_width - 40, stats_height)
        
    def _draw_confidence_trend_graph(self, x, y, width, height):
        """Draw confidence trend graph"""
        if not self.statistics_data['frame_data']:
            return
        
        frames = self.statistics_data['frame_data']
        
        # Determine which frames to show
        if self.stat_page_state['time_range'] == 'recent' and len(frames) > 50:
            frames_to_show = frames[-50:]
        elif self.stat_page_state['time_range'] == 'early' and len(frames) > 50:
            frames_to_show = frames[:50]
        else:
            frames_to_show = frames[-100:] if len(frames) > 100 else frames
        
        if not frames_to_show:
            return
        
        # Draw graph background
        pygame.draw.rect(self.screen, (10, 15, 25), (x, y, width, height))
        pygame.draw.rect(self.screen, (40, 60, 100), (x, y, width, height), 1)
        
        # Draw grid lines and labels
        for i in range(0, 11):  # 0.0 to 1.0
            confidence_level = i / 10.0
            y_pos = y + height - (confidence_level * height)
            
            # Grid line
            pygame.draw.line(self.screen, (40, 60, 100, 100),
                           (x, y_pos), (x + width, y_pos), 1)
            
            # Label
            label = self.small_font.render(f"{confidence_level:.1f}", True, (180, 200, 255))
            self.screen.blit(label, (x - 25, y_pos - 8))
        
        # Draw confidence zones
        zone_colors = [
            (255, 100, 100, 30),  # Red: 0.0-0.4
            (255, 255, 100, 30),  # Yellow: 0.4-0.6
            (255, 180, 100, 30),  # Orange: 0.6-0.8
            (100, 255, 100, 30),  # Green: 0.8-1.0
        ]
        
        zone_heights = [0.4 * height, 0.2 * height, 0.2 * height, 0.2 * height]
        current_y = y + height
        
        for i, (color, zone_height) in enumerate(zip(zone_colors, zone_heights)):
            zone_rect = pygame.Rect(x, current_y - zone_height, width, zone_height)
            zone_surf = pygame.Surface((width, zone_height), pygame.SRCALPHA)
            zone_surf.fill(color)
            self.screen.blit(zone_surf, (x, current_y - zone_height))
            current_y -= zone_height
        
        # Draw confidence values
        confidences = [f['avg_confidence'] for f in frames_to_show]
        
        if len(confidences) > 1:
            points = []
            for i, confidence in enumerate(confidences):
                x_pos = x + (i / len(confidences) * width)
                y_pos = y + height - (confidence * height)
                points.append((x_pos, y_pos))
            
            # Draw line
            for i in range(len(points) - 1):
                color = self._confidence_color((confidences[i] + confidences[i + 1]) / 2)
                pygame.draw.line(self.screen, color, points[i], points[i + 1], 3)
            
            # Draw points
            for point, confidence in zip(points, confidences):
                pygame.draw.circle(self.screen, self._confidence_color(confidence), 
                                 (int(point[0]), int(point[1])), 4)
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                 (int(point[0]), int(point[1])), 4, 1)
        
        # Draw current confidence indicator
        current_conf = confidences[-1] if confidences else 0.0
        current_y = y + height - (current_conf * height)
        pygame.draw.line(self.screen, (255, 255, 255, 150),
                        (x, current_y), (x + width, current_y), 1)
        
        # Draw frame labels
        if len(frames_to_show) > 1:
            x_step = max(1, len(frames_to_show) // 10)
            for i in range(0, len(frames_to_show), x_step):
                x_pos = x + (i / len(frames_to_show) * width)
                frame_num = frames_to_show[i]['frame']
                label = self.small_font.render(str(frame_num), True, (180, 200, 255))
                self.screen.blit(label, (x_pos - 10, y + height + 5))
    
    def _draw_confidence_details(self, x, y, width, height):
        """Draw detailed confidence statistics"""
        if not self.statistics_data['frame_data']:
            return
        
        frames = self.statistics_data['frame_data']
        
        # Background
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (x, y))
        
        # Title
        title = self.font.render("CONFIDENCE DETAILS", True, (255, 255, 180))
        self.screen.blit(title, (x + 20, y + 20))
        
        # Calculate statistics
        confidences = [f['avg_confidence'] for f in frames]
        
        if confidences:
            min_conf = min(confidences)
            max_conf = max(confidences)
            avg_conf = sum(confidences) / len(confidences)
            
            # Count confidence levels
            low_count = sum(1 for c in confidences if c < 0.4)
            medium_count = sum(1 for c in confidences if 0.4 <= c < 0.6)
            high_count = sum(1 for c in confidences if c >= 0.6)
            
            # Draw statistics
            stats_x = x + 30
            stats_y = y + 70
            line_height = 25
            
            stats = [
                ("Frames Analyzed:", f"{len(frames)}"),
                ("Minimum Confidence:", f"{min_conf:.3f}"),
                ("Maximum Confidence:", f"{max_conf:.3f}"),
                ("Average Confidence:", f"{avg_conf:.3f}"),
                ("Low Confidence (<0.4):", f"{low_count} ({low_count/len(frames)*100:.1f}%)"),
                ("Medium Confidence (0.4-0.6):", f"{medium_count} ({medium_count/len(frames)*100:.1f}%)"),
                ("High Confidence (≥0.6):", f"{high_count} ({high_count/len(frames)*100:.1f}%)"),
            ]
            
            for label, value in stats:
                label_surf = self.small_font.render(label, True, (200, 220, 255))
                value_surf = self.small_font.render(value, True, (180, 255, 180))
                
                self.screen.blit(label_surf, (stats_x, stats_y))
                self.screen.blit(value_surf, (stats_x + 250, stats_y))
                stats_y += line_height
            
            # Draw histogram
            hist_x = x + width // 2 + 50
            hist_y = y + 70
            hist_width = width // 2 - 100
            hist_height = height - 100
            
            self._draw_confidence_histogram(hist_x, hist_y, hist_width, hist_height, confidences)
    
    def _draw_confidence_histogram(self, x, y, width, height, confidences):
        """Draw confidence histogram"""
        # Background
        pygame.draw.rect(self.screen, (10, 15, 25), (x, y, width, height))
        pygame.draw.rect(self.screen, (40, 60, 100), (x, y, width, height), 1)
        
        # Create histogram bins
        bins = 10
        bin_counts = [0] * bins
        
        for confidence in confidences:
            bin_idx = min(bins - 1, int(confidence * bins))
            bin_counts[bin_idx] += 1
        
        max_count = max(bin_counts) if bin_counts else 1
        
        # Draw histogram bars
        bar_width = width // bins
        for i in range(bins):
            bar_height = int((bin_counts[i] / max_count) * (height * 0.8))
            bar_x = x + i * bar_width
            bar_y = y + height - bar_height
            
            # Color based on confidence level
            confidence_level = (i + 0.5) / bins
            color = self._confidence_color(confidence_level)
            
            pygame.draw.rect(self.screen, color, (bar_x + 2, bar_y, bar_width - 4, bar_height))
            pygame.draw.rect(self.screen, (255, 255, 255), (bar_x + 2, bar_y, bar_width - 4, bar_height), 1)
            
            # Draw count
            if bin_counts[i] > 0:
                count_text = self.small_font.render(str(bin_counts[i]), True, (255, 255, 255))
                count_rect = count_text.get_rect(center=(bar_x + bar_width // 2, bar_y - 10))
                self.screen.blit(count_text, count_rect)
            
            # Draw bin label
            bin_label = f"{i/bins:.1f}-{(i+1)/bins:.1f}"
            label_text = self.small_font.render(bin_label, True, (180, 200, 255))
            label_rect = label_text.get_rect(center=(bar_x + bar_width // 2, y + height + 15))
            self.screen.blit(label_text, label_rect)    

    def _draw_control_hints(self):
        """Draw control hints panel"""
        hints = [
            "WASD: Pan | Q/E: Zoom | TAB: Stats",
            "SPACE: Play/Pause | ←/→: Frame Nav",
            "L: Legend | G: Grid | A: Axons | E: Eigen",
            "U: UNKNOWN | R: Reset | ESC: Back"
        ]
        
        panel_width = 350
        panel_height = 100
        panel_x = 20
        panel_y = self.screen_height - panel_height - 20
        
        # Panel background
        surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 180), surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, (60, 80, 120, 120), surf.get_rect(), 1, border_radius=8)
        self.screen.blit(surf, (panel_x, panel_y))
        
        # Draw hints
        y_offset = panel_y + 15
        for hint in hints:
            hint_surf = self.small_font.render(hint, True, (200, 220, 255, 200))
            self.screen.blit(hint_surf, (panel_x + 15, y_offset))
            y_offset += 20



    def _draw_ui_panel(self):
        """Draw main UI panel with session info"""
        if self.mode == self.MODE_BROWSER or self.mode == self.MODE_LOADING or self.mode == self.MODE_STATISTICS:
            return
        
        # Mode indicator
        mode_text = f"MODE: {self.mode.upper()}"
        
        # Color based on mode
        if self.mode == self.MODE_REPLAY:
            mode_color = (100, 200, 255)  # Blue
        elif self.mode == self.MODE_LIVE:
            mode_color = (255, 100, 100)  # Red
        else:
            mode_color = (255, 255, 200)  # Yellow
        
        mode_surf = self.title_font.render(mode_text, True, mode_color)
        mode_rect = mode_surf.get_rect(center=(self.screen_width // 2, 30))
        
        # Background for mode indicator
        bg_rect = mode_rect.inflate(30, 15)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 25, 40, 200), bg_surf.get_rect(), border_radius=10)
        pygame.draw.rect(bg_surf, (mode_color[0]//2, mode_color[1]//2, mode_color[2]//2, 150), 
                        bg_surf.get_rect(), 2, border_radius=10)
        self.screen.blit(bg_surf, bg_rect)
        self.screen.blit(mode_surf, mode_rect)
        
        # Session info panel (top-left)
        info_panel_width = 400
        info_panel_height = 80
        info_panel_x = 20
        info_panel_y = 20
        
        # Panel background
        info_surf = pygame.Surface((info_panel_width, info_panel_height), pygame.SRCALPHA)
        pygame.draw.rect(info_surf, (20, 25, 40, 200), info_surf.get_rect(), border_radius=8)
        pygame.draw.rect(info_surf, (60, 80, 120, 150), info_surf.get_rect(), 2, border_radius=8)
        self.screen.blit(info_surf, (info_panel_x, info_panel_y))
        
        # Session info
        if self.session_id:
            session_text = f"Session: {self.session_id[:25]}{'...' if len(self.session_id) > 25 else ''}"
            session_surf = self.small_font.render(session_text, True, (180, 200, 255))
            self.screen.blit(session_surf, (info_panel_x + 15, info_panel_y + 15))
        
        # Frame info
        frame_text = f"Frame: {self.current_frame_index + 1}/{len(self.frames) if self.frames else 0}"
        frame_surf = self.small_font.render(frame_text, True, (180, 200, 255))
        self.screen.blit(frame_surf, (info_panel_x + 15, info_panel_y + 40))
        
        # Statistics panel (top-right)
        self._draw_statistics_panel()
        
        # Control hints panel (bottom-left)
        if self.mode == self.MODE_REPLAY:
            self._draw_control_hints()

    def _draw_unknown_statistics(self):
        """Draw UNKNOWN pattern statistics"""
        if not self.statistics_data['frame_data']:
            no_data = self.font.render("No UNKNOWN data available", True, (200, 200, 200))
            self.screen.blit(no_data, (self.screen_width // 2 - no_data.get_width() // 2, 200))
            return
        
        # Top panel: Overview
        panel_x = 20
        panel_y = 180
        panel_width = self.screen_width - 40
        panel_height = 200
        
        # Background
        surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (panel_x, panel_y))
        
        # Title
        title = self.font.render("UNKNOWN PATTERN ANALYSIS", True, (255, 255, 180))
        self.screen.blit(title, (panel_x + 20, panel_y + 20))
        
        # Calculate UNKNOWN statistics
        frames = self.statistics_data['frame_data']
        
        if frames:
            current_frame = frames[-1]
            current_unknown = current_frame.get('unknown_count', 0)
            current_gamma = current_frame.get('gamma_updated_count', 0)
            total_neurons = current_frame.get('total_neurons', 1)
            
            # Calculate trends
            unknown_counts = [f.get('unknown_count', 0) for f in frames]
            gamma_counts = [f.get('gamma_updated_count', 0) for f in frames]
            
            max_unknown = max(unknown_counts) if unknown_counts else 0
            max_gamma = max(gamma_counts) if gamma_counts else 0
            
            # Draw statistics
            stats_x = panel_x + 30
            stats_y = panel_y + 70
            line_height = 25
            
            stats = [
                ("Current UNKNOWN Neurons:", f"{current_unknown}/{total_neurons} ({current_unknown/total_neurons*100:.1f}%)"),
                ("Current γ-updated Neurons:", f"{current_gamma}/{current_unknown} ({current_gamma/current_unknown*100:.1f}%" if current_unknown > 0 else "0/0 (0%)"),
                ("Peak UNKNOWN Count:", f"{max_unknown}"),
                ("Peak γ-updated Count:", f"{max_gamma}"),
                ("UNKNOWN Frames:", f"{sum(1 for f in frames if f.get('unknown_count', 0) > 0)}/{len(frames)}"),
                ("γ-active Frames:", f"{sum(1 for f in frames if f.get('gamma_updated_count', 0) > 0)}/{len(frames)}"),
            ]
            
            for label, value in stats:
                label_surf = self.small_font.render(label, True, (200, 220, 255))
                value_surf = self.small_font.render(value, True, (180, 255, 180))
                
                self.screen.blit(label_surf, (stats_x, stats_y))
                self.screen.blit(value_surf, (stats_x + 300, stats_y))
                stats_y += line_height
        
        # Bottom panels: Graphs
        graphs_y = panel_y + panel_height + 20
        graph_height = self.screen_height - graphs_y - 150
        graph_width = (self.screen_width - 60) // 2
        
        # UNKNOWN count graph
        self._draw_unknown_count_graph(panel_x, graphs_y, graph_width, graph_height)
        
        # γ-updated graph
        self._draw_gamma_updated_graph(panel_x + graph_width + 20, graphs_y, graph_width, graph_height)

    def _draw_unknown_count_graph(self, x, y, width, height):
        """Draw UNKNOWN count over time graph"""
        if not self.statistics_data['frame_data']:
            return
        
        frames = self.statistics_data['frame_data']
        
        # Background
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (x, y))
        
        # Title
        title = self.font.render("UNKNOWN COUNT TREND", True, (255, 255, 180))
        self.screen.blit(title, (x + 20, y + 20))
        
        # Get data
        if self.stat_page_state['time_range'] == 'recent' and len(frames) > 50:
            frames_to_show = frames[-50:]
        elif self.stat_page_state['time_range'] == 'early' and len(frames) > 50:
            frames_to_show = frames[:50]
        else:
            frames_to_show = frames[-100:] if len(frames) > 100 else frames
        
        if not frames_to_show:
            return
        
        unknown_counts = [f.get('unknown_count', 0) for f in frames_to_show]
        max_count = max(unknown_counts) if unknown_counts else 1
        
        # Graph area
        graph_padding = 60
        graph_x = x + graph_padding
        graph_y = y + 60
        graph_width = width - graph_padding * 2
        graph_height = height - 100
        
        # Draw graph background
        pygame.draw.rect(self.screen, (10, 15, 25), 
                        (graph_x, graph_y, graph_width, graph_height))
        pygame.draw.rect(self.screen, (40, 60, 100), 
                        (graph_x, graph_y, graph_width, graph_height), 1)
        
        # Draw Y-axis labels
        if max_count > 0:
            y_label_interval = max(1, max_count // 5)
            for i in range(0, max_count + 1, y_label_interval):
                if i == 0:
                    continue
                y_pos = graph_y + graph_height - (i / max_count * graph_height)
                if y_pos >= graph_y:
                    label = self.small_font.render(str(i), True, (180, 200, 255))
                    self.screen.blit(label, (graph_x - 40, y_pos - 8))
                    pygame.draw.line(self.screen, (40, 60, 100, 100),
                                   (graph_x, y_pos), (graph_x + graph_width, y_pos), 1)
        
        # Draw the graph
        if len(unknown_counts) > 1:
            points = []
            for i, count in enumerate(unknown_counts):
                x_pos = graph_x + (i / len(unknown_counts) * graph_width)
                y_pos = graph_y + graph_height - (count / max_count * graph_height)
                points.append((x_pos, y_pos))
            
            # Draw filled area
            fill_points = points.copy()
            fill_points.append((points[-1][0], graph_y + graph_height))
            fill_points.append((points[0][0], graph_y + graph_height))
            
            if len(fill_points) >= 3:
                fill_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.polygon(fill_surf, (255, 100, 100, 80), fill_points)
                self.screen.blit(fill_surf, (x, y))
            
            # Draw line
            for i in range(len(points) - 1):
                pygame.draw.line(self.screen, (255, 100, 100), points[i], points[i + 1], 3)
            
            # Draw points
            for point, count in zip(points, unknown_counts):
                if count > 0:
                    pygame.draw.circle(self.screen, (255, 100, 100), (int(point[0]), int(point[1])), 4)
                    pygame.draw.circle(self.screen, (255, 255, 255), (int(point[0]), int(point[1])), 4, 1)
        
        # Draw legend
        legend_x = graph_x + 10
        legend_y = graph_y + 10
        current_count = unknown_counts[-1] if unknown_counts else 0
        legend_text = self.small_font.render(f"Current: {current_count}", True, (255, 100, 100))
        self.screen.blit(legend_text, (legend_x, legend_y))
    
    def _draw_gamma_updated_graph(self, x, y, width, height):
        """Draw γ-updated count over time graph"""
        if not self.statistics_data['frame_data']:
            return
        
        frames = self.statistics_data['frame_data']
        
        # Background
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (x, y))
        
        # Title
        title = self.font.render("γ-UPDATED COUNT TREND", True, (255, 255, 180))
        self.screen.blit(title, (x + 20, y + 20))
        
        # Get data
        if self.stat_page_state['time_range'] == 'recent' and len(frames) > 50:
            frames_to_show = frames[-50:]
        elif self.stat_page_state['time_range'] == 'early' and len(frames) > 50:
            frames_to_show = frames[:50]
        else:
            frames_to_show = frames[-100:] if len(frames) > 100 else frames
        
        if not frames_to_show:
            return
        
        gamma_counts = [f.get('gamma_updated_count', 0) for f in frames_to_show]
        max_count = max(gamma_counts) if gamma_counts else 1
        
        # Graph area
        graph_padding = 60
        graph_x = x + graph_padding
        graph_y = y + 60
        graph_width = width - graph_padding * 2
        graph_height = height - 100
        
        # Draw graph background
        pygame.draw.rect(self.screen, (10, 15, 25), 
                        (graph_x, graph_y, graph_width, graph_height))
        pygame.draw.rect(self.screen, (40, 60, 100), 
                        (graph_x, graph_y, graph_width, graph_height), 1)
        
        # Draw Y-axis labels
        if max_count > 0:
            y_label_interval = max(1, max_count // 5)
            for i in range(0, max_count + 1, y_label_interval):
                if i == 0:
                    continue
                y_pos = graph_y + graph_height - (i / max_count * graph_height)
                if y_pos >= graph_y:
                    label = self.small_font.render(str(i), True, (180, 200, 255))
                    self.screen.blit(label, (graph_x - 40, y_pos - 8))
                    pygame.draw.line(self.screen, (40, 60, 100, 100),
                                   (graph_x, y_pos), (graph_x + graph_width, y_pos), 1)
        
        # Draw the graph
        if len(gamma_counts) > 1:
            points = []
            for i, count in enumerate(gamma_counts):
                x_pos = graph_x + (i / len(gamma_counts) * graph_width)
                y_pos = graph_y + graph_height - (count / max_count * graph_height)
                points.append((x_pos, y_pos))
            
            # Draw filled area
            fill_points = points.copy()
            fill_points.append((points[-1][0], graph_y + graph_height))
            fill_points.append((points[0][0], graph_y + graph_height))
            
            if len(fill_points) >= 3:
                fill_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                pygame.draw.polygon(fill_surf, (255, 100, 255, 80), fill_points)
                self.screen.blit(fill_surf, (x, y))
            
            # Draw line
            for i in range(len(points) - 1):
                pygame.draw.line(self.screen, (255, 100, 255), points[i], points[i + 1], 3)
            
            # Draw points
            for point, count in zip(points, gamma_counts):
                if count > 0:
                    pygame.draw.circle(self.screen, (255, 100, 255), (int(point[0]), int(point[1])), 4)
                    pygame.draw.circle(self.screen, (255, 255, 255), (int(point[0]), int(point[1])), 4, 1)
        
        # Draw legend
        legend_x = graph_x + 10
        legend_y = graph_y + 10
        current_count = gamma_counts[-1] if gamma_counts else 0
        legend_text = self.small_font.render(f"Current: {current_count}", True, (255, 100, 255))
        self.screen.blit(legend_text, (legend_x, legend_y))
        
        # Draw percentage if we have unknown counts
        unknown_counts = [f.get('unknown_count', 0) for f in frames_to_show]
        if unknown_counts and unknown_counts[-1] > 0:
            percentage = (gamma_counts[-1] / unknown_counts[-1] * 100) if unknown_counts[-1] > 0 else 0
            percent_text = self.small_font.render(f"({percentage:.1f}% of UNKNOWN)", True, (200, 200, 255))
            self.screen.blit(percent_text, (legend_x, legend_y + 20))

    def _draw_axon_comets(self):
        """Draw axon animations with comet trails - PROPERLY FIXED VERSION"""
        current_time = time.time()
        
        for i, beam in enumerate(self.active_axon_beams[:]):  # Copy for safe iteration
            axon_type = beam.get('axon_type', 'UNKNOWN')
            
            # DEBUG: Log beam data to understand structure
            # print(f"Beam {i}: Type={axon_type}, Data keys={beam.keys()}")
            
            # Get source and target data - USE YOUR EXPORT STRUCTURE
            source_data = beam.get('source', {})
            target_data = beam.get('target', {})
            
            # SOURCE: Based on your export structure
            source_coord = None
            if 'coordinate' in source_data:
                source_coord = source_data['coordinate']
            elif 'coordinate' in source_data.get('data', {}):
                source_coord = source_data['data']['coordinate']
            
            # TARGET: Based on your export structure (heartbeat axons target themselves)
            target_coord = None
            if 'coordinate' in target_data:
                target_coord = target_data['coordinate']
            elif 'coordinate' in target_data.get('data', {}):
                target_coord = target_data['data']['coordinate']
            
            # If still no target_coord, use source_coord (self-targeting for heartbeats)
            if target_coord is None and source_coord is not None:
                target_coord = source_coord
            
            # DEBUG: Log coordinates
            # print(f"  Source coord: {source_coord}, Target coord: {target_coord}")
            
            # Skip if missing coordinates
            if source_coord is None or target_coord is None:
                # print(f"  ⚠️ Skipping axon {i}: missing coordinates")
                if beam in self.active_axon_beams:
                    self.active_axon_beams.remove(beam)
                continue
            
            # Get screen positions
            source_pos = self._coord_to_screen(source_coord)
            target_pos = self._coord_to_screen(target_coord)
            
            if not source_pos or not target_pos:
                # print(f"  ⚠️ Skipping axon {i}: invalid screen positions")
                if beam in self.active_axon_beams:
                    self.active_axon_beams.remove(beam)
                continue
            
            # Get animation progress
            start_time = beam.get('start_time', current_time)
            duration = beam.get('duration', 1.5)
            
            elapsed = current_time - start_time
            progress = min(1.0, elapsed / duration)
            
            # Get color based on axon type - USE YOUR AXON_COLORS mapping
            if axon_type in AXON_COLORS:
                base_color = AXON_COLORS[axon_type]
            elif axon_type == 'HEARTBEAT':
                base_color = (200, 200, 200)  # Gray for heartbeats
            elif axon_type == 'GROWTH_SIGNAL':
                base_color = (100, 255, 100)  # Green for growth
            elif axon_type == 'SYSTEM_ALERT':
                base_color = (255, 100, 100)  # Red for alerts
            elif 'GAMMA' in axon_type:
                base_color = (255, 100, 255)  # Purple for gamma
            else:
                base_color = (150, 150, 200)  # Default blue-ish
            
            # Calculate pulse effect
            pulse = 0.8 + 0.4 * math.sin(current_time * 8.0 + i)
            color = tuple(min(255, int(c * pulse)) for c in base_color)
            
            # Projectile position
            head_x = source_pos[0] + (target_pos[0] - source_pos[0]) * progress
            head_y = source_pos[1] + (target_pos[1] - source_pos[1]) * progress
            
            # Draw trail (comet tail)
            trail_length = 5  # Number of trail segments
            for j in range(trail_length):
                trail_progress = max(0.0, progress - (j * 0.05))
                
                # Calculate trail position
                trail_x = source_pos[0] + (target_pos[0] - source_pos[0]) * trail_progress
                trail_y = source_pos[1] + (target_pos[1] - source_pos[1]) * trail_progress
                
                # Calculate trail properties
                trail_alpha = int(200 * (1.0 - j * 0.2) * (1.0 - progress * 0.3))
                trail_color = (*color, trail_alpha)
                trail_size = max(1, int(5 * (1.0 - j * 0.3) * self.zoom))
                
                # Draw trail segment
                pygame.draw.circle(self.screen, trail_color, 
                                (int(trail_x), int(trail_y)), trail_size)
            
            # Draw main projectile (head)
            head_size = max(2, int(7 * self.zoom * pulse))
            head_color = (*color, 255)
            
            # Draw glowing effect around head
            glow_size = head_size + 3
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, 100), 
                            (glow_size, glow_size), glow_size)
            self.screen.blit(glow_surf, (head_x - glow_size, head_y - glow_size))
            
            # Draw main head
            pygame.draw.circle(self.screen, head_color, 
                            (int(head_x), int(head_y)), head_size)
            pygame.draw.circle(self.screen, (255, 255, 255), 
                            (int(head_x), int(head_y)), head_size, 1)
            
            # Draw absorption effect at target
            if progress > 0.9:
                absorb_progress = (progress - 0.9) / 0.1
                absorb_size = int(head_size * 3 * (1.0 - absorb_progress))
                absorb_alpha = int(180 * (1.0 - absorb_progress))
                absorb_color = (*color, absorb_alpha)
                
                if absorb_size > 0:
                    absorb_surf = pygame.Surface((absorb_size * 2, absorb_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(absorb_surf, absorb_color, 
                                    (absorb_size, absorb_size), absorb_size)
                    self.screen.blit(absorb_surf, 
                                (target_pos[0] - absorb_size, target_pos[1] - absorb_size))
            
            # Remove completed axons
            if progress >= 1.0:
                self.active_axon_beams.remove(beam)
                
                # Create absorption particles
                for k in range(10):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(20, 80)
                    velocity = (
                        math.cos(angle) * speed,
                        math.sin(angle) * speed
                    )
                    
                    particle = Particle(
                        position=target_pos,
                        color=color,
                        velocity=velocity,
                        lifetime=random.uniform(0.3, 0.8)
                    )
                    self.particles.append(particle)

    def _draw_state_change_highlights(self):
        """Draw highlights for state changes with pulsing effects"""
        if not self.show_change_highlights:
            return
        
        current_time = time.time()
        active_highlights = []
        
        for highlight in self.state_change_highlights[:]:  # Copy for safe iteration
            elapsed = current_time - highlight['start_time']
            duration = highlight.get('duration', 1.5)
            progress = min(1.0, elapsed / duration)
            
            if progress >= 1.0:
                continue
            
            screen_pos = highlight.get('screen_pos')
            if not screen_pos:
                continue
            
            # Calculate pulse effect
            pulse_count = highlight.get('pulse_count', 3)
            pulse_progress = progress * pulse_count
            current_pulse = int(pulse_progress)
            pulse_phase = pulse_progress - current_pulse
            
            # Only draw during pulse phases (not between pulses)
            if pulse_phase < 0.8:  # 80% of time in pulse, 20% between pulses
                # Calculate pulse size with easing
                if pulse_phase < 0.5:
                    # Expand phase
                    ease_progress = pulse_phase * 2
                    pulse_size = highlight['max_size'] * (0.3 + 0.7 * ease_progress)
                else:
                    # Contract phase
                    ease_progress = (pulse_phase - 0.5) * 2
                    pulse_size = highlight['max_size'] * (1.0 - 0.7 * ease_progress)
                
                # Fade out over time
                alpha = int(255 * (1.0 - progress) * (1.0 - pulse_phase * 0.5))
                
                # Get color
                base_color = highlight.get('color', (255, 255, 255))
                color = (*base_color, alpha)
                
                # Create pulse surface
                surf_size = int(pulse_size * 2)
                surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                
                # Draw outer pulse ring
                ring_width = max(2, int(4 * self.zoom))
                pygame.draw.circle(surf, color, 
                                 (surf_size // 2, surf_size // 2),
                                 int(pulse_size), ring_width)
                
                # Draw inner glow
                inner_size = pulse_size * 0.7
                inner_alpha = int(alpha * 0.5)
                inner_color = (*base_color, inner_alpha)
                pygame.draw.circle(surf, inner_color,
                                 (surf_size // 2, surf_size // 2),
                                 int(inner_size))
                
                # Blit to screen
                self.screen.blit(surf, 
                               (screen_pos[0] - surf_size // 2, 
                                screen_pos[1] - surf_size // 2))
                
                # Add to active list
                active_highlights.append(highlight)
        
        # Update highlights list
        self.state_change_highlights = active_highlights
    
    def _add_state_change_highlight(self, neuron, change_type):
        """Add a state change highlight for a neuron"""
        if not neuron.position:
            return
        
        # Determine color based on change type
        if change_type == 'pattern_change':
            color = (255, 200, 50)  # Gold
            max_size = 20
        elif change_type == 'state_change':
            color = STATE_COLORS.get(neuron.current_state, (200, 200, 200))
            max_size = 18
        elif change_type == 'confidence_boost':
            color = (100, 255, 100)  # Green
            max_size = 16
        elif change_type == 'eigen_update':
            color = (100, 200, 255)  # Blue
            max_size = 15
        elif change_type == 'gamma_update':
            color = (255, 100, 255)  # Purple
            max_size = 22
        else:
            color = (255, 255, 255)  # White
            max_size = 15
        
        highlight = {
            'screen_pos': neuron.position,
            'color': color,
            'max_size': max_size * self.zoom,
            'start_time': time.time(),
            'duration': 1.5,
            'pulse_count': 3,
            'neuron_id': neuron.id,
            'change_type': change_type
        }
        
        self.state_change_highlights.append(highlight)
    

    def _draw_statistics_tabs(self):
        """Draw statistics mode tabs - FIXED with click detection"""
        tabs = [
            ('overview', '📊 OVERVIEW'),
            ('eigen', 'αβγζ EIGEN'),
            ('confidence', '🎯 CONFIDENCE'),
            ('unknown', '❓ UNKNOWN'),
        ]
        
        tab_width = 200
        tab_height = 40
        tab_x = 20
        tab_y = 120
        
        self.stat_tab_rects = {}  # Store for click detection
        
        for i, (tab_id, tab_label) in enumerate(tabs):
            tab_rect = pygame.Rect(tab_x + i * (tab_width + 10), tab_y, tab_width, tab_height)
            self.stat_tab_rects[tab_id] = tab_rect
            
            # Determine colors
            if self.stat_page_state['view'] == tab_id:
                bg_color = (60, 80, 160)
                border_color = (100, 120, 200)
                text_color = (255, 255, 255)
            elif tab_rect.collidepoint(pygame.mouse.get_pos()):
                bg_color = (70, 90, 170)
                border_color = (100, 120, 200)
                text_color = (240, 240, 255)
            else:
                bg_color = (40, 50, 100)
                border_color = (60, 80, 140)
                text_color = (200, 220, 240)
            
            # Draw tab
            pygame.draw.rect(self.screen, bg_color, tab_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, tab_rect, 2, border_radius=8)
            
            # Draw label
            label_surf = self.font.render(tab_label, True, text_color)
            label_rect = label_surf.get_rect(center=tab_rect.center)
            self.screen.blit(label_surf, label_rect)

    def _draw_statistics_ui_buttons(self):
        """Draw UI buttons for statistics mode - FIXED with click detection"""
        button_width = 180
        button_height = 32
        button_x = self.screen_width - button_width - 20
        button_y = 120
        
        buttons = [
            ('back_to_viz', button_x, button_y, button_width, button_height,
            '← BACK TO VIZ', 'Return to visualization'),
            ('export_stats', button_x, button_y + 40, button_width, button_height,
            '📊 EXPORT STATS', 'Export statistics to file'),
            ('time_all', button_x, button_y + 80, button_width, button_height,
            'TIME: ALL', 'Show all time data'),
            ('time_recent', button_x, button_y + 120, button_width, button_height,
            'TIME: RECENT', 'Show recent 50 frames'),
            ('time_early', button_x, button_y + 160, button_width, button_height,
            'TIME: EARLY', 'Show first 50 frames'),
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for btn_id, x, y, w, h, label, tooltip in buttons:
            rect = pygame.Rect(x, y, w, h)
            
            # Determine if active or hovered
            is_active = False
            if btn_id == 'time_all' and self.stat_page_state['time_range'] == 'all':
                is_active = True
            elif btn_id == 'time_recent' and self.stat_page_state['time_range'] == 'recent':
                is_active = True
            elif btn_id == 'time_early' and self.stat_page_state['time_range'] == 'early':
                is_active = True
            
            is_hovered = rect.collidepoint(mouse_pos)
            
            # Set colors
            if btn_id == self.active_button or is_active:
                bg_color = (80, 100, 180)
                border_color = (120, 140, 220)
                text_color = (255, 255, 255)
            elif is_hovered:
                bg_color = (70, 90, 170)
                border_color = (100, 120, 200)
                text_color = (240, 240, 255)
            else:
                bg_color = (60, 80, 160)
                border_color = (80, 100, 180)
                text_color = (220, 220, 240)
            
            # Draw button
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=6)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=6)
            
            # Draw label
            label_surf = self.small_font.render(label, True, text_color)
            label_rect = label_surf.get_rect(center=rect.center)
            self.screen.blit(label_surf, label_rect)
            
            # Store for click detection
            if not hasattr(self, 'stat_button_rects'):
                self.stat_button_rects = {}
            self.stat_button_rects[btn_id] = rect

    def _draw_statistics_overview(self):
        """Draw overview statistics"""
        if not self.statistics_data['frame_data']:
            no_data = self.font.render("No statistics data available", True, (200, 200, 200))
            self.screen.blit(no_data, (self.screen_width // 2 - no_data.get_width() // 2, 200))
            return
        
        metrics = self.statistics_data['session_metrics']
        
        # Main metrics panel
        panel_x = 20
        panel_y = 180
        panel_width = 450
        panel_height = 300
        
        # Panel background
        surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (panel_x, panel_y))
        
        # Title
        title = self.font.render("SESSION METRICS", True, (255, 255, 180))
        self.screen.blit(title, (panel_x + 20, panel_y + 20))
        
        y_offset = panel_y + 60
        
        # Key metrics
        key_metrics = [
            ("Total Frames", f"{metrics['total_frames']}"),
            ("Peak Neurons", f"{metrics['peak_neurons']}"),
            ("Avg Neurons", f"{metrics['avg_neurons']:.1f}"),
            ("Peak UNKNOWN", f"{metrics['peak_unknown']}"),
            ("Final Confidence", f"{metrics['final_confidence']:.3f}"),
            ("Final UNKNOWN", f"{metrics['final_unknown']}"),
            ("Duration", f"{metrics['session_duration']:.1f}s"),
        ]
        
        for label, value in key_metrics:
            label_surf = self.small_font.render(label, True, (200, 220, 255))
            value_surf = self.small_font.render(value, True, (180, 255, 180))
            
            self.screen.blit(label_surf, (panel_x + 30, y_offset))
            self.screen.blit(value_surf, (panel_x + 250, y_offset))
            y_offset += 30
        
        # Graph panel
        graph_x = panel_x + panel_width + 20
        graph_y = panel_y
        graph_width = self.screen_width - graph_x - 20
        graph_height = panel_height
        
        # Draw neuron count graph
        self._draw_neuron_count_graph(graph_x, graph_y, graph_width, graph_height)
        
        # Frame-by-frame metrics below
        metrics_y = panel_y + panel_height + 20
        metrics_height = self.screen_height - metrics_y - 150
        
        # Draw frame metrics table
        self._draw_frame_metrics_table(20, metrics_y, self.screen_width - 40, metrics_height)
        
    def _draw_neuron_labels(self):
        """Draw neuron coordinate labels with smart positioning"""
        if self.zoom < 0.8:  # Only show labels when zoomed in
            return
        
        for neuron in self.neurons.values():
            pos = neuron.position
            if not pos:
                continue
            
            # Only show labels for visible neurons
            if not (50 <= pos[0] <= self.screen_width - 50 and 
                   100 <= pos[1] <= self.screen_height - 150):
                continue
            
            coord = neuron.coordinate
            if not coord:
                continue
            
            # Create label based on coordinate
            if len(coord) <= 2:
                # Simple label for shallow coordinates
                label = str(coord[-1]) if coord else "R"
            else:
                # Compact label for deeper coordinates
                label_parts = []
                for i, part in enumerate(coord[-3:]):  # Last 3 parts
                    if isinstance(part, (int, float)):
                        label_parts.append(str(int(part)))
                    elif isinstance(part, list) and part:
                        label_parts.append(str(part[0]) if isinstance(part[0], (int, float)) else "?")
                    else:
                        label_parts.append("?")
                
                label = ".".join(label_parts)
                if len(coord) > 3:
                    label = "..." + label
            
            # Create label surface
            label_surf = self.small_font.render(label, True, (255, 255, 255, 200))
            label_rect = label_surf.get_rect()
            
            # Position label to avoid overlapping
            offset_x, offset_y = self._calculate_label_offset(neuron, pos, label_rect.size)
            
            # Draw label background for better readability
            bg_padding = 2
            bg_rect = label_rect.inflate(bg_padding * 2, bg_padding * 2)
            bg_rect.center = (pos[0] + offset_x, pos[1] + offset_y)
            
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (0, 0, 0, 150), bg_surf.get_rect(), border_radius=3)
            pygame.draw.rect(bg_surf, (255, 255, 255, 50), bg_surf.get_rect(), 1, border_radius=3)
            
            self.screen.blit(bg_surf, bg_rect)
            
            # Draw label text
            text_pos = (bg_rect.x + bg_padding, bg_rect.y + bg_padding)
            self.screen.blit(label_surf, text_pos)
    
    def _calculate_label_offset(self, neuron, pos, label_size):
        """Calculate optimal label offset to avoid overlaps"""
        # Default offset (right side of neuron)
        offset_x = 15
        offset_y = -8
        
        # Check for potential overlaps
        label_width, label_height = label_size
        
        # Get potential label position
        label_rect = pygame.Rect(
            pos[0] + offset_x,
            pos[1] + offset_y,
            label_width,
            label_height
        )
        
        # Check for overlaps with other neurons
        overlap_count = 0
        for other_neuron in self.neurons.values():
            if other_neuron.id == neuron.id or not other_neuron.position:
                continue
            
            other_pos = other_neuron.position
            neuron_radius = 8 * self.zoom
            
            # Create a rectangle around the other neuron
            other_rect = pygame.Rect(
                other_pos[0] - neuron_radius,
                other_pos[1] - neuron_radius,
                neuron_radius * 2,
                neuron_radius * 2
            )
            
            if label_rect.colliderect(other_rect):
                overlap_count += 1
        
        # If too many overlaps, try different positions
        if overlap_count > 0:
            positions = [
                (15, -8),   # Right top
                (15, 8),    # Right bottom
                (-15 - label_width, -8),  # Left top
                (-15 - label_width, 8),   # Left bottom
                (0, -20 - label_height),  # Top center
                (0, 20),                  # Bottom center
            ]
            
            # Find position with fewest overlaps
            best_position = positions[0]
            min_overlaps = overlap_count
            
            for test_offset in positions[1:]:
                test_rect = pygame.Rect(
                    pos[0] + test_offset[0],
                    pos[1] + test_offset[1],
                    label_width,
                    label_height
                )
                
                test_overlaps = 0
                for other_neuron in self.neurons.values():
                    if other_neuron.id == neuron.id or not other_neuron.position:
                        continue
                    
                    other_pos = other_neuron.position
                    neuron_radius = 8 * self.zoom
                    
                    other_rect = pygame.Rect(
                        other_pos[0] - neuron_radius,
                        other_pos[1] - neuron_radius,
                        neuron_radius * 2,
                        neuron_radius * 2
                    )
                    
                    if test_rect.colliderect(other_rect):
                        test_overlaps += 1
                
                if test_overlaps < min_overlaps:
                    min_overlaps = test_overlaps
                    best_position = test_offset
            
            offset_x, offset_y = best_position
        
        return offset_x, offset_y

    def _draw_neuron_count_graph(self, x, y, width, height):
        """Draw neuron count over time graph"""
        if not self.statistics_data['frame_data']:
            return
        
        # Background
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (x, y))
        
        # Title
        title = self.font.render("NEURON COUNT OVER TIME", True, (255, 255, 180))
        self.screen.blit(title, (x + 20, y + 20))
        
        # Graph area
        graph_padding = 60
        graph_area_x = x + graph_padding
        graph_area_y = y + 60
        graph_area_width = width - graph_padding * 2
        graph_area_height = height - 100
        
        # Draw graph background
        pygame.draw.rect(self.screen, (10, 15, 25), 
                        (graph_area_x, graph_area_y, graph_area_width, graph_area_height))
        pygame.draw.rect(self.screen, (40, 60, 100), 
                        (graph_area_x, graph_area_y, graph_area_width, graph_area_height), 1)
        
        # Get data
        frames = self.statistics_data['frame_data']
        if not frames:
            return
        
        # Determine which frames to show based on time range
        if self.stat_page_state['time_range'] == 'recent' and len(frames) > 50:
            frames_to_show = frames[-50:]
        elif self.stat_page_state['time_range'] == 'early' and len(frames) > 50:
            frames_to_show = frames[:50]
        else:
            frames_to_show = frames[-100:] if len(frames) > 100 else frames
        
        if not frames_to_show:
            return
        
        # Find min/max for scaling
        neuron_counts = [f['total_neurons'] for f in frames_to_show]
        max_count = max(neuron_counts) if neuron_counts else 1
        min_count = min(neuron_counts) if neuron_counts else 0
        
        # Draw Y-axis labels
        y_label_interval = max(1, max_count // 5)
        for i in range(0, max_count + 1, y_label_interval):
            if i == 0:
                continue
            y_pos = graph_area_y + graph_area_height - (i / max_count * graph_area_height)
            if y_pos >= graph_area_y:
                # Label
                label = self.small_font.render(str(i), True, (180, 200, 255))
                self.screen.blit(label, (graph_area_x - 40, y_pos - 8))
                # Grid line
                pygame.draw.line(self.screen, (40, 60, 100, 100),
                               (graph_area_x, y_pos),
                               (graph_area_x + graph_area_width, y_pos), 1)
        
        # Draw X-axis labels (frame numbers)
        if len(frames_to_show) > 1:
            x_step = max(1, len(frames_to_show) // 10)
            for i in range(0, len(frames_to_show), x_step):
                x_pos = graph_area_x + (i / len(frames_to_show) * graph_area_width)
                frame_num = frames_to_show[i]['frame']
                label = self.small_font.render(str(frame_num), True, (180, 200, 255))
                self.screen.blit(label, (x_pos - 10, graph_area_y + graph_area_height + 10))
        
        # Draw the line graph
        points = []
        for i, frame in enumerate(frames_to_show):
            x_pos = graph_area_x + (i / len(frames_to_show) * graph_area_width)
            y_pos = graph_area_y + graph_area_height - (frame['total_neurons'] / max_count * graph_area_height)
            points.append((x_pos, y_pos))
        
        if len(points) > 1:
            # Draw line
            for i in range(len(points) - 1):
                pygame.draw.line(self.screen, (100, 180, 255),
                               points[i], points[i + 1], 2)
            
            # Draw points
            for point in points:
                pygame.draw.circle(self.screen, (100, 200, 255), (int(point[0]), int(point[1])), 3)
                pygame.draw.circle(self.screen, (255, 255, 255), (int(point[0]), int(point[1])), 3, 1)
        
        # Draw legend
        legend_x = graph_area_x + 10
        legend_y = graph_area_y + 10
        legend_text = self.small_font.render(f"Neurons: {frames_to_show[-1]['total_neurons']}", True, (100, 200, 255))
        self.screen.blit(legend_text, (legend_x, legend_y))
    
    def _draw_frame_metrics_table(self, x, y, width, height):
        """Draw frame-by-frame metrics table"""
        if not self.statistics_data['frame_data']:
            return
        
        # Background
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (x, y))
        
        # Title
        title = self.font.render("FRAME METRICS", True, (255, 255, 180))
        self.screen.blit(title, (x + 20, y + 20))
        
        # Column headers
        headers = ["Frame", "Neurons", "Axons", "UNKNOWN", "γ-updated", "Confidence"]
        col_width = width // len(headers)
        header_y = y + 60
        
        for i, header in enumerate(headers):
            header_surf = self.small_font.render(header, True, (255, 255, 180))
            self.screen.blit(header_surf, (x + i * col_width + 10, header_y))
        
        # Draw separator
        pygame.draw.line(self.screen, (60, 80, 120),
                        (x, header_y + 25),
                        (x + width, header_y + 25), 2)
        
        # Frame data rows
        frames = self.statistics_data['frame_data']
        start_idx = self.stat_page_state['scroll_offset']
        end_idx = min(start_idx + 15, len(frames))
        
        row_height = 30
        for row_idx in range(start_idx, end_idx):
            frame = frames[row_idx]
            row_y = header_y + 40 + (row_idx - start_idx) * row_height
            
            # Highlight current frame
            if frame['frame'] == self.current_frame_index:
                highlight_rect = pygame.Rect(x, row_y - 5, width, row_height)
                pygame.draw.rect(self.screen, (40, 60, 100, 150), highlight_rect)
            
            # Frame number
            frame_surf = self.small_font.render(str(frame['frame']), True, (200, 220, 255))
            self.screen.blit(frame_surf, (x + 10, row_y))
            
            # Neurons
            neurons_surf = self.small_font.render(str(frame['total_neurons']), True, (180, 255, 180))
            self.screen.blit(neurons_surf, (x + col_width + 10, row_y))
            
            # Axons
            axons_surf = self.small_font.render(str(frame['total_axons']), True, (180, 220, 255))
            self.screen.blit(axons_surf, (x + col_width * 2 + 10, row_y))
            
            # UNKNOWN count
            unknown_surf = self.small_font.render(str(frame['unknown_count']), True, 
                                                 (255, 100, 100) if frame['unknown_count'] > 0 else (200, 200, 200))
            self.screen.blit(unknown_surf, (x + col_width * 3 + 10, row_y))
            
            # Gamma updated
            gamma_surf = self.small_font.render(str(frame['gamma_updated_count']), True,
                                               (255, 100, 255) if frame['gamma_updated_count'] > 0 else (200, 200, 200))
            self.screen.blit(gamma_surf, (x + col_width * 4 + 10, row_y))
            
            # Confidence
            conf_surf = self.small_font.render(f"{frame['avg_confidence']:.3f}", True,
                                              self._confidence_color(frame['avg_confidence']))
            self.screen.blit(conf_surf, (x + col_width * 5 + 10, row_y))
        
        # Scroll indicators
        if start_idx > 0:
            up_arrow = self.small_font.render("▲", True, (200, 220, 255))
            self.screen.blit(up_arrow, (x + width - 30, y + 30))
        
        if end_idx < len(frames):
            down_arrow = self.small_font.render("▼", True, (200, 220, 255))
            self.screen.blit(down_arrow, (x + width - 30, y + height - 30))
    
    def _confidence_color(self, confidence):
        """Get color for confidence value"""
        if confidence > 0.8:
            return (100, 255, 100)  # Green
        elif confidence > 0.6:
            return (255, 255, 100)  # Yellow
        elif confidence > 0.4:
            return (255, 180, 100)  # Orange
        else:
            return (255, 100, 100)  # Red
    
    def _draw_eigen_statistics(self):
        """Draw eigen value statistics"""
        if not self.statistics_data['eigen_trends']:
            no_data = self.font.render("No eigen data available", True, (200, 200, 200))
            self.screen.blit(no_data, (self.screen_width // 2 - no_data.get_width() // 2, 200))
            return
        
        # Draw eigen value graphs
        eigen_types = ['alpha', 'beta', 'gamma', 'zeta']
        eigen_colors = {
            'alpha': EIGEN_COLORS['alpha'],
            'beta': EIGEN_COLORS['beta'],
            'gamma': EIGEN_COLORS['gamma'],
            'zeta': EIGEN_COLORS['zeta']
        }
        
        # Calculate grid
        graphs_per_row = 2
        graph_width = (self.screen_width - 60) // graphs_per_row
        graph_height = 300
        
        for i, eigen_type in enumerate(eigen_types):
            row = i // graphs_per_row
            col = i % graphs_per_row
            
            x = 20 + col * (graph_width + 20)
            y = 180 + row * (graph_height + 20)
            
            self._draw_eigen_graph(x, y, graph_width, graph_height, eigen_type, eigen_colors[eigen_type])
            
    def _draw_eigen_graph(self, x, y, width, height, eigen_type, color):
        """Draw a single eigen value graph"""
        if eigen_type not in self.statistics_data['eigen_trends']:
            return
        
        values = self.statistics_data['eigen_trends'][eigen_type]
        if not values:
            return
        
        # Background
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=12)
        self.screen.blit(surf, (x, y))
        
        # Title
        title_text = f"{eigen_type.upper()} EIGEN VALUE"
        title = self.font.render(title_text, True, color)
        self.screen.blit(title, (x + 20, y + 20))
        
        # Current value
        current_value = values[-1] if values else 0
        value_text = f"Current: {current_value:.3f}"
        value_surf = self.small_font.render(value_text, True, (200, 220, 255))
        self.screen.blit(value_surf, (x + width - 150, y + 20))
        
        # Graph area
        graph_padding = 40
        graph_x = x + graph_padding
        graph_y = y + 60
        graph_width = width - graph_padding * 2
        graph_height = height - 100
        
        # Draw graph
        max_value = max(values) if values else 1.0
        min_value = min(values) if values else 0.0
        value_range = max_value - min_value
        
        if len(values) > 1:
            # Draw line
            points = []
            for i, value in enumerate(values[-100:]):  # Last 100 points
                x_pos = graph_x + (i / min(len(values), 100) * graph_width)
                y_pos = graph_y + graph_height - ((value - min_value) / value_range * graph_height) if value_range > 0 else graph_y + graph_height // 2
                points.append((x_pos, y_pos))
            
            for i in range(len(points) - 1):
                pygame.draw.line(self.screen, color, points[i], points[i + 1], 2)
            
            # Fill area under line
            if len(points) > 1:
                fill_points = points.copy()
                fill_points.append((points[-1][0], graph_y + graph_height))
                fill_points.append((points[0][0], graph_y + graph_height))
                
                if len(fill_points) >= 3:
                    fill_surf = pygame.Surface((width, height), pygame.SRCALPHA)
                    pygame.draw.polygon(fill_surf, (*color, 50), fill_points)
                    self.screen.blit(fill_surf, (x, y))

    # ===== UPDATED EVENT HANDLING FOR STATISTICS =====
    


    # ===== EXPORT STATISTICS =====
    
    def _export_statistics(self):
        """Export statistics to JSON file"""
        if not self.session_id or not self.statistics_data['frame_data']:
            self._add_log("⚠️ No statistics data to export")
            return
        
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"statistics_{self.session_id}_{timestamp}.json"
            
            # Create export data
            export_data = {
                'session_id': self.session_id,
                'export_time': time.time(),
                'export_timestamp': timestamp,
                'total_frames': len(self.statistics_data['frame_data']),
                'session_metrics': self.statistics_data['session_metrics'],
                'frame_summary': self.statistics_data['frame_data'],
                'eigen_trends': self.statistics_data['eigen_trends'],
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self._add_log(f"📊 Statistics exported to {filename}")
            
        except Exception as e:
            self._add_log(f"❌ Error exporting statistics: {e}")
    
    # ===== SESSION MANAGEMENT METHODS ===== 

    def _update_neurons_from_frame(self):
        """Update neurons from current frame data"""
        if not self.current_frame_data:
            return
        
        self.neurons = {}
        self.coordinate_map = {}
        self.active_axon_beams = []
        
        # Helper function to convert to float
        def to_float(value, default=0.0):
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            return default
        
        # Process neurons from frame
        frame_neurons = self.current_frame_data.get('neurons', [])
        for neuron_data in frame_neurons:
            # Convert confidence to float
            confidence = neuron_data.get('confidence', 0.0)
            confidence = to_float(confidence, 0.0)
            
            # Get eigen system
            eigen_system = neuron_data.get('eigen_system', {})
            
            # Get coordinate and convert to tuple for dictionary key
            coord = neuron_data.get('coordinate', [])
            if isinstance(coord, list):
                coord_tuple = tuple(coord)
            else:
                coord_tuple = coord
            
            neuron = VisualNeuron(
                neuron_id=neuron_data.get('neuron_id', 'unknown'),
                coordinate=coord_tuple,  # Store as tuple
                pattern=neuron_data.get('pattern', 'UNKNOWN'),
                confidence=confidence,
                current_state=neuron_data.get('current_state', 'UNKNOWN'),
                eigen_alpha=to_float(eigen_system.get('alpha', 0.0)),
                eigen_beta=to_float(eigen_system.get('beta', 0.0)),
                eigen_gamma=to_float(eigen_system.get('gamma', 0.0)),
                eigen_zeta=to_float(eigen_system.get('zeta', 0.0))
            )
            
            # Set additional properties
            neuron.is_unknown_pattern = (neuron.pattern == 'UNKNOWN')
            
            # Check for gamma updates
            unknown_specific = neuron_data.get('unknown_specific', {})
            neuron.has_gamma_update = unknown_specific.get('has_gamma_update', False)
            
            # Convert health score to float
            health_score = neuron_data.get('health_score', 0.0)
            neuron.health_score = to_float(health_score, 0.0)
            neuron.health_status = neuron_data.get('health_status', 'UNKNOWN')
            
            # Convert cycle to int
            cycle = neuron_data.get('cycle', 0)
            if isinstance(cycle, (int, float)):
                neuron.cycle = int(cycle)
            elif isinstance(cycle, str):
                try:
                    neuron.cycle = int(float(cycle))
                except:
                    neuron.cycle = 0
            else:
                neuron.cycle = 0
            
            # Calculate screen position
            neuron.position = self._coord_to_screen(neuron.coordinate)
            
            # Store neuron
            self.neurons[neuron.id] = neuron
            
            # Add to coordinate map - coord_tuple is already a tuple
            if coord_tuple:
                self.coordinate_map[coord_tuple] = neuron.id
        
        # Process axons from frame - FIXED FOR YOUR EXPORT STRUCTURE
        frame_axons = self.current_frame_data.get('axons', [])
        for axon_data in frame_axons:
            # CORRECTED: Use the exact structure from your export
            axon_beam = {
                'axon_type': axon_data.get('axon_type', 'UNKNOWN'),
                'source': axon_data.get('source', {}),
                'target': axon_data.get('target', {}),
                'start_time': time.time(),
                'duration': random.uniform(1.0, 2.0),
                'axon_id': len(self.active_axon_beams)  # Use integer, not string
            }
            self.active_axon_beams.append(axon_beam)
        
        self._add_log(f"✅ Updated {len(self.neurons)} neurons and {len(self.active_axon_beams)} axons")


    # ===== TIMELINE CONTROL METHODS =====
    
    def go_to_frame(self, frame_index):
        """Go to specific frame index"""
        if not self.frames:
            return
        
        frame_index = max(0, min(frame_index, len(self.frames) - 1))
        
        if frame_index != self.current_frame_index:
            self.current_frame_index = frame_index
            self.current_frame_data = self.frames[frame_index]
            self._update_neurons_from_frame()
            
            # Check for state changes
            self._detect_state_changes()
            
            self._add_log(f"📊 Frame {frame_index + 1}/{len(self.frames)}")
    
    def next_frame(self):
        """Advance to next frame"""
        if not self.frames:
            return
        
        if self.current_frame_index < len(self.frames) - 1:
            self.go_to_frame(self.current_frame_index + 1)
    
    def prev_frame(self):
        """Go to previous frame"""
        if not self.frames:
            return
        
        if self.current_frame_index > 0:
            self.go_to_frame(self.current_frame_index - 1)
    
    def toggle_playback(self):
        """Toggle playback state"""
        self.timeline.is_playing = not self.timeline.is_playing
        if self.timeline.is_playing:
            self._add_log("▶ Playback started")
        else:
            self._add_log("‖ Playback paused")
    
    def adjust_playback_speed(self, factor):
        """Adjust playback speed"""
        self.timeline.playback_speed *= factor
        self.timeline.playback_speed = max(0.1, min(5.0, self.timeline.playback_speed))
        self._add_log(f"⏩ Playback speed: {self.timeline.playback_speed:.1f}x")
    
    # ===== STATE CHANGE DETECTION =====
    
    def _detect_state_changes(self):
        """Detect state changes between frames"""
        if not self.frames or self.current_frame_index == 0:
            return
        
        prev_frame = self.frames[self.current_frame_index - 1]
        curr_frame = self.frames[self.current_frame_index]
        
        prev_neurons = {n['neuron_id']: n for n in prev_frame.get('neurons', [])}
        curr_neurons = {n['neuron_id']: n for n in curr_frame.get('neurons', [])}
        
        for neuron_id, curr_neuron in curr_neurons.items():
            prev_neuron = prev_neurons.get(neuron_id)
            
            if not prev_neuron:
                # New neuron
                if neuron_id in self.neurons:
                    self._add_state_change_highlight(self.neurons[neuron_id], 'new')
                continue
            
            # Check for pattern changes
            if prev_neuron.get('pattern') != curr_neuron.get('pattern'):
                if neuron_id in self.neurons:
                    self._add_state_change_highlight(self.neurons[neuron_id], 'pattern_change')
            
            # Check for state changes
            if prev_neuron.get('current_state') != curr_neuron.get('current_state'):
                if neuron_id in self.neurons:
                    self._add_state_change_highlight(self.neurons[neuron_id], 'state_change')
            
            # Check for confidence boost
            if curr_neuron.get('confidence', 0) - prev_neuron.get('confidence', 0) > 0.1:
                if neuron_id in self.neurons:
                    self._add_state_change_highlight(self.neurons[neuron_id], 'confidence_boost')
            
            # Check for gamma updates
            prev_gamma = prev_neuron.get('unknown_specific', {}).get('has_gamma_update', False)
            curr_gamma = curr_neuron.get('unknown_specific', {}).get('has_gamma_update', False)
            
            if not prev_gamma and curr_gamma:
                if neuron_id in self.neurons:
                    self._add_state_change_highlight(self.neurons[neuron_id], 'gamma_update')
    
    # ===== EVENT HANDLER COMPLETION =====

    def _handle_left_click_complete(self, pos):
        """Complete left click handler with all button support"""
        current_time = time.time()
        
        # ===== STATISTICS MODE CLICKS =====
        if self.mode == self.MODE_STATISTICS:
            # Check statistics tabs first
            if hasattr(self, 'stat_tab_rects'):
                for tab_id, tab_rect in self.stat_tab_rects.items():
                    if tab_rect.collidepoint(pos):
                        self.stat_page_state['view'] = tab_id
                        self._add_log(f"📊 Switched to {tab_id} view")
                        return
            
            # Check statistics buttons
            if hasattr(self, 'stat_button_rects'):
                for btn_id, btn_rect in self.stat_button_rects.items():
                    if btn_rect.collidepoint(pos):
                        self.active_button = btn_id
                        
                        if btn_id == 'back_to_viz':
                            self.mode = self.MODE_REPLAY
                            self._add_log("🎬 Returned to visualization")
                        elif btn_id == 'export_stats':
                            self._export_statistics()
                        elif btn_id == 'time_all':
                            self.stat_page_state['time_range'] = 'all'
                            self._add_log("🕒 Showing all time data")
                        elif btn_id == 'time_recent':
                            self.stat_page_state['time_range'] = 'recent'
                            self._add_log("🕒 Showing recent 50 frames")
                        elif btn_id == 'time_early':
                            self.stat_page_state['time_range'] = 'early'
                            self._add_log("🕒 Showing first 50 frames")
                        
                        # Double click detection
                        if current_time - self.last_click_time < 0.3:
                            self._add_log(f"⚡ Double-clicked {btn_id}")
                        self.last_click_time = current_time
                        return
            
            # If clicked outside buttons in stats mode, do nothing
            return
        
        # ===== REGULAR UI BUTTONS (all modes) =====
        for button_name, button_info in self.ui_buttons.items():
            if button_info['rect'].collidepoint(pos):
                self.active_button = button_name
                
                if button_name == 'mode_live':
                    self.mode = self.MODE_LIVE
                    self._add_log("🔴 Switched to Live Mode")
                    
                elif button_name == 'mode_replay':
                    self.mode = self.MODE_REPLAY
                    self._add_log("🎬 Switched to Replay Mode")
                    
                elif button_name == 'mode_browser':
                    self.mode = self.MODE_BROWSER
                    self._add_log("📁 Switched to Browser Mode")
                    
                elif button_name == 'mode_stats':  # NEW: Statistics button
                    if self.frames and len(self.frames) > 0:
                        self.mode = self.MODE_STATISTICS
                        self._analyze_statistics_data()
                        self._add_log("📊 Switched to Statistics Mode")
                    else:
                        self._add_log("⚠️ Load a session first to view statistics")
                    
                elif button_name == 'toggle_legend':
                    self.show_legend = not self.show_legend
                    self._add_log(f"{'✅' if self.show_legend else '❌'} Legend")
                    
                elif button_name == 'toggle_axons':
                    self.show_axons = not self.show_axons
                    self._add_log(f"{'✅' if self.show_axons else '❌'} Axons")
                    
                elif button_name == 'toggle_grid':
                    self.show_grid = not self.show_grid
                    self._add_log(f"{'✅' if self.show_grid else '❌'} Grid")
                    
                elif button_name == 'toggle_eigen':
                    self.show_eigen_values = not self.show_eigen_values
                    self._add_log(f"{'✅' if self.show_eigen_values else '❌'} Eigen values")
                    
                elif button_name == 'reset_view':
                    self.pan_x, self.pan_y = 0, 0
                    self.zoom = 1.0
                    self.update_neuron_positions()
                    self._add_log("⟲ View reset")
                
                # Double click detection
                if current_time - self.last_click_time < 0.3:
                    self._add_log(f"⚡ Double-clicked {button_name}")
                self.last_click_time = current_time
                return
        
        # ===== TIMELINE CONTROLS (REPLAY mode only) =====
        if self.mode == self.MODE_REPLAY:
            # Check timeline handle
            if self.timeline_handle_rect and self.timeline_handle_rect.collidepoint(pos):
                self.dragging_timeline = True
                return
            
            # Check timeline buttons
            if hasattr(self, 'timeline_button_rects'):
                for btn_id, rect in self.timeline_button_rects.items():
                    if rect.collidepoint(pos):
                        self.active_button = btn_id
                        
                        if btn_id == 'timeline_play':
                            self.toggle_playback()
                        elif btn_id == 'timeline_prev':
                            self.prev_frame()
                        elif btn_id == 'timeline_next':
                            self.next_frame()
                        elif btn_id == 'timeline_slower':
                            self.adjust_playback_speed(0.8)
                        elif btn_id == 'timeline_faster':
                            self.adjust_playback_speed(1.2)
                        
                        # Double click detection
                        if current_time - self.last_click_time < 0.3:
                            self._add_log(f"⚡ Double-clicked {btn_id}")
                        self.last_click_time = current_time
                        return
        
        # ===== WINDOW DRAGGING/RESIZING =====
        for window_name, window in self.windows.items():
            if window.handle_event(
                pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': pos}),
                pos
            ):
                # Check if close button was clicked
                close_rect = pygame.Rect(
                    window.rect.x + window.rect.width - 25,
                    window.rect.y + 5,
                    20, 20
                )
                if close_rect.collidepoint(pos):
                    window.visible = False
                    self._add_log(f"❌ Closed {window_name} window")
                return
        
        # ===== BROWSER MODE CLICKS =====
        if self.mode == self.MODE_BROWSER:
            # Check if click is on a session item
            panel_x = 100
            panel_y = 120
            panel_width = self.screen_width - 200
            item_height = 40
            
            # Calculate which session was clicked
            relative_y = pos[1] - panel_y - 50  # 50 is header height
            if relative_y > 0:
                item_index = relative_y // item_height
                actual_index = self.browser.scroll_offset + item_index
                
                if 0 <= actual_index < len(self.browser.sessions):
                    self.browser.selected_index = actual_index
                    self.browser._adjust_scroll()
                    self._add_log(f"📁 Selected session {actual_index + 1}: {self.browser.sessions[actual_index]['id'][:20]}...")
                    
                    # Double click to load
                    if current_time - self.last_click_time < 0.3:
                        selected = self.browser.get_selected_session()
                        if selected:
                            self.session_id = selected['id']
                            self.mode = self.MODE_LOADING
                            self._add_log(f"📥 Loading session: {self.session_id}")
                    
                    self.last_click_time = current_time
                    return
            
            # If clicked outside sessions, check scroll arrows
            if hasattr(self.browser, 'scroll_indicators'):
                # Handle scroll up arrow
                if self.browser.scroll_offset > 0 and pos[0] > panel_x + panel_width - 40 and pos[1] < panel_y + 30:
                    self.browser.selected_index = max(0, self.browser.selected_index - 1)
                    self.browser._adjust_scroll()
                    return
                
                # Handle scroll down arrow
                if (self.browser.scroll_offset + self.browser.visible_items < len(self.browser.sessions) and 
                    pos[0] > panel_x + panel_width - 40 and pos[1] > panel_y + panel_height - 30):
                    self.browser.selected_index = min(len(self.browser.sessions) - 1, self.browser.selected_index + 1)
                    self.browser._adjust_scroll()
                    return
        
        # ===== NEURON CLICK =====
        if self.mode in [self.MODE_REPLAY, self.MODE_LIVE]:
            clicked_neuron = None
            
            # Check all neurons for click
            for neuron in self.neurons.values():
                if neuron.position:
                    distance = math.sqrt(
                        (pos[0] - neuron.position[0])**2 + 
                        (pos[1] - neuron.position[1])**2
                    )
                    neuron_radius = 10 * self.zoom
                    if distance <= neuron_radius:
                        clicked_neuron = neuron
                        break
            
            if clicked_neuron:
                self.selected_neuron_id = clicked_neuron.id
                
                # Toggle selection on double click
                if current_time - self.last_click_time < 0.3:
                    if self.selected_neuron_id == self.previous_selected_neuron_id:
                        # Center view on neuron
                        center_x = self.screen_width // 2
                        center_y = self.screen_height // 2
                        
                        if clicked_neuron.position:
                            self.pan_x = center_x - clicked_neuron.position[0]
                            self.pan_y = center_y - clicked_neuron.position[1]
                            self.update_neuron_positions()
                            self._add_log(f"🎯 Centered view on neuron: {clicked_neuron.id[:12]}...")
                    else:
                        self._add_log(f"🎯 Selected neuron: {clicked_neuron.id[:12]}...")
                else:
                    self._add_log(f"🎯 Selected neuron: {clicked_neuron.id[:12]}...")
                
                self.previous_selected_neuron_id = self.selected_neuron_id
                self.last_click_time = current_time
                return
        
        # ===== START VIEW DRAGGING (if not clicking on anything else) =====
        if self.mode in [self.MODE_REPLAY, self.MODE_LIVE, self.MODE_BROWSER]:
            self.dragging_view = True
            self.drag_start_pos = pos
            self.drag_start_pan = (self.pan_x, self.pan_y)
            self._add_log("🖱️ Started view dragging")
        
        self.last_click_time = current_time

    def _handle_keydown(self, key):
        """Complete keyboard handling with proper statistics navigation"""
        # ===== ESCAPE HANDLER (works in all modes) =====
        if key == pygame.K_ESCAPE:
            if self.mode == self.MODE_STATISTICS:
                self.mode = self.MODE_REPLAY
                self._add_log("🎬 Returned to visualization from statistics")
            elif self.mode == self.MODE_REPLAY:
                self.mode = self.MODE_BROWSER
                self._add_log("📁 Returned to browser")
            elif self.mode == self.MODE_LIVE:
                self.mode = self.MODE_BROWSER
                self._add_log("📁 Returned to browser")
            elif self.mode == self.MODE_LOADING:
                self.mode = self.MODE_BROWSER
                self._add_log("⚠️ Cancelled loading")
            elif self.mode == self.MODE_BROWSER:
                self.running = False
                self._add_log("👋 Exiting visualizer")
            return
        
        # ===== BROWSER MODE =====
        if self.mode == self.MODE_BROWSER:
            if key == pygame.K_UP:
                self.browser.select_prev()
                self._add_log(f"⬆️ Selected session {self.browser.selected_index + 1}/{len(self.browser.sessions)}")
            elif key == pygame.K_DOWN:
                self.browser.select_next()
                self._add_log(f"⬇️ Selected session {self.browser.selected_index + 1}/{len(self.browser.sessions)}")
            elif key == pygame.K_LEFT:
                self.browser.selected_index = max(0, self.browser.selected_index - 5)
                self.browser._adjust_scroll()
                self._add_log(f"⏪ Jumped back 5 sessions")
            elif key == pygame.K_RIGHT:
                self.browser.selected_index = min(len(self.browser.sessions) - 1, self.browser.selected_index + 5)
                self.browser._adjust_scroll()
                self._add_log(f"⏩ Jumped forward 5 sessions")
            elif key == pygame.K_HOME:
                self.browser.selected_index = 0
                self.browser._adjust_scroll()
                self._add_log("⏮️ Jumped to first session")
            elif key == pygame.K_END:
                self.browser.selected_index = max(0, len(self.browser.sessions) - 1)
                self.browser._adjust_scroll()
                self._add_log("⏭️ Jumped to last session")
            elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                selected = self.browser.get_selected_session()
                if selected:
                    self.session_id = selected['id']
                    self.mode = self.MODE_LOADING
                    self._add_log(f"📥 Loading session: {self.session_id}")
                else:
                    self._add_log("⚠️ No session selected")
            elif key == pygame.K_r:
                self.browser.scan_sessions()
                self._add_log(f"🔄 Refreshed, found {len(self.browser.sessions)} sessions")
            elif key == pygame.K_TAB:
                # Try to load the first session if available
                if self.browser.sessions:
                    selected = self.browser.sessions[0]
                    self.session_id = selected['id']
                    self.mode = self.MODE_LOADING
                    self._add_log(f"📥 Quick-loading first session: {self.session_id}")
        
        # ===== STATISTICS MODE =====
        elif self.mode == self.MODE_STATISTICS:
            # ARROW KEYS for navigating between statistics views
            if key == pygame.K_LEFT:
                views = ['overview', 'eigen', 'confidence', 'unknown']
                current_idx = views.index(self.stat_page_state['view'])
                next_idx = (current_idx - 1) % len(views)
                self.stat_page_state['view'] = views[next_idx]
                self._add_log(f"📊 Switched to {views[next_idx]} view")
            
            elif key == pygame.K_RIGHT:
                views = ['overview', 'eigen', 'confidence', 'unknown']
                current_idx = views.index(self.stat_page_state['view'])
                next_idx = (current_idx + 1) % len(views)
                self.stat_page_state['view'] = views[next_idx]
                self._add_log(f"📊 Switched to {views[next_idx]} view")
            
            # UP/DOWN for scrolling tables
            elif key == pygame.K_UP:
                if self.stat_page_state['scroll_offset'] > 0:
                    self.stat_page_state['scroll_offset'] -= 1
            
            elif key == pygame.K_DOWN:
                max_offset = max(0, len(self.statistics_data.get('frame_data', [])) - 15)
                if self.stat_page_state['scroll_offset'] < max_offset:
                    self.stat_page_state['scroll_offset'] += 1
            
            # TAB returns to visualization
            elif key == pygame.K_TAB:
                self.mode = self.MODE_REPLAY
                self._add_log("🎬 Returned to visualization")
            
            # HOME/END for table navigation
            elif key == pygame.K_HOME:
                self.stat_page_state['scroll_offset'] = 0
            
            elif key == pygame.K_END:
                max_offset = max(0, len(self.statistics_data.get('frame_data', [])) - 15)
                self.stat_page_state['scroll_offset'] = max_offset
            
            # S for export statistics
            elif key == pygame.K_s:
                self._export_statistics()
            
            # TIME RANGE shortcuts
            elif key == pygame.K_1:
                self.stat_page_state['time_range'] = 'all'
                self._add_log("🕒 Showing all time data")
            
            elif key == pygame.K_2:
                self.stat_page_state['time_range'] = 'recent'
                self._add_log("🕒 Showing recent 50 frames")
            
            elif key == pygame.K_3:
                self.stat_page_state['time_range'] = 'early'
                self._add_log("🕒 Showing first 50 frames")
        
        # ===== VISUALIZATION MODES (REPLAY/LIVE) =====
        elif self.mode in [self.MODE_REPLAY, self.MODE_LIVE]:
            # TAB switches to statistics mode
            if key == pygame.K_TAB:
                self._switch_to_statistics_mode()
                return
            
            # SPACE for play/pause (in replay mode only)
            if key == pygame.K_SPACE and self.mode == self.MODE_REPLAY:
                self.toggle_playback()
                return
            
            # WASD NAVIGATION - Continuous movement is handled elsewhere, but we still log
            if key == pygame.K_w:
                self._add_log("⬆️ Pan up (hold for continuous)")
            elif key == pygame.K_s:
                self._add_log("⬇️ Pan down (hold for continuous)")
            elif key == pygame.K_a:
                self._add_log("⬅️ Pan left (hold for continuous)")
            elif key == pygame.K_d:
                self._add_log("➡️ Pan right (hold for continuous)")
            
            # ZOOM CONTROLS
            elif key == pygame.K_q:  # Zoom in
                old_zoom = self.zoom
                self.zoom = min(3.0, self.zoom * 1.1)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                center_x = self.screen_width // 2
                center_y = self.screen_height // 2
                self.pan_x -= int((mouse_x - center_x) * (self.zoom - old_zoom) / old_zoom)
                self.pan_y -= int((mouse_y - center_y) * (self.zoom - old_zoom) / old_zoom)
                self.update_neuron_positions()
                self._add_log(f"🔍 Zoom in: {self.zoom:.1f}x")
            
            elif key == pygame.K_e:  # Zoom out
                old_zoom = self.zoom
                self.zoom = max(0.1, self.zoom / 1.1)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                center_x = self.screen_width // 2
                center_y = self.screen_height // 2
                self.pan_x -= int((mouse_x - center_x) * (self.zoom - old_zoom) / old_zoom)
                self.pan_y -= int((mouse_y - center_y) * (self.zoom - old_zoom) / old_zoom)
                self.update_neuron_positions()
                self._add_log(f"🔎 Zoom out: {self.zoom:.1f}x")
            
            # TOGGLE CONTROLS (with modifiers to avoid conflicts)
            elif key == pygame.K_l:  # Toggle legend
                self.show_legend = not self.show_legend
                self._add_log(f"{'✅' if self.show_legend else '❌'} Legend")
            
            elif key == pygame.K_g:  # Toggle grid
                self.show_grid = not self.show_grid
                self._add_log(f"{'✅' if self.show_grid else '❌'} Grid")
            
            elif key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+C for axons
                self.show_axons = not self.show_axons
                self._add_log(f"{'✅' if self.show_axons else '❌'} Axons")
            
            elif key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+V for eigen values
                self.show_eigen_values = not self.show_eigen_values
                self._add_log(f"{'✅' if self.show_eigen_values else '❌'} Eigen values")
            
            # RESET VIEW
            elif key == pygame.K_r:
                self.pan_x, self.pan_y = 0, 0
                self.zoom = 1.0
                self.update_neuron_positions()
                self._add_log("⟲ View reset")
            
            # TIMELINE CONTROLS (REPLAY mode only)
            elif self.mode == self.MODE_REPLAY:
                if key == pygame.K_COMMA or key == pygame.K_LESS:  # Slower playback
                    self.adjust_playback_speed(0.8)
                
                elif key == pygame.K_PERIOD or key == pygame.K_GREATER:  # Faster playback
                    self.adjust_playback_speed(1.2)
                
                elif key == pygame.K_HOME:  # Go to first frame
                    if self.frames:
                        self.go_to_frame(0)
                
                elif key == pygame.K_END:  # Go to last frame
                    if self.frames:
                        self.go_to_frame(len(self.frames) - 1)
        
        # ===== LOADING MODE =====
        elif self.mode == self.MODE_LOADING:
            # Only ESCAPE is handled above
            pass

    def _handle_keyup(self, key):
        """Handle key release for smooth movement"""
        # This method is called from the main loop when KEYUP events are detected
        # We don't need to do much here since continuous movement is handled in run()
        pass

    def _switch_to_statistics_mode(self):
        """Switch to statistics visualization mode"""
        if not self.frames:
            self._add_log("⚠️ No data loaded for statistics")
            return
        
        self.mode = self.MODE_STATISTICS
        self._analyze_statistics_data()
        self.graph_dirty = True
        self._add_log("📊 Switched to Statistics Mode")

    def _handle_ui_button_click(self, button_name, current_time):
        """Handle UI button clicks"""
        if button_name == 'mode_live':
            self.mode = self.MODE_LIVE
            self._add_log("🔴 Switched to Live Mode")
            
        elif button_name == 'mode_replay':
            self.mode = self.MODE_REPLAY
            self._add_log("🎬 Switched to Replay Mode")
            
        elif button_name == 'mode_browser':
            self.mode = self.MODE_BROWSER
            self._add_log("📁 Switched to Browser Mode")
            
        elif button_name == 'toggle_legend':
            self.show_legend = not self.show_legend
            self._add_log(f"{'✅' if self.show_legend else '❌'} Legend {'shown' if self.show_legend else 'hidden'}")
            
        elif button_name == 'toggle_axons':
            self.show_axons = not self.show_axons
            self._add_log(f"{'✅' if self.show_axons else '❌'} Axons {'shown' if self.show_axons else 'hidden'}")
            
        elif button_name == 'toggle_grid':
            self.show_grid = not self.show_grid
            self._add_log(f"{'✅' if self.show_grid else '❌'} Grid {'shown' if self.show_grid else 'hidden'}")
            
        elif button_name == 'toggle_eigen':
            self.show_eigen_values = not self.show_eigen_values
            self._add_log(f"{'✅' if self.show_eigen_values else '❌'} Eigen values {'shown' if self.show_eigen_values else 'hidden'}")
            
        elif button_name == 'reset_view':
            self.pan_x, self.pan_y = 0, 0
            self.zoom = 1.0
            self.update_neuron_positions()
            self._add_log("⟲ View reset")
        
        # Double click detection
        if current_time - self.last_click_time < 0.3:
            self._add_log(f"⚡ Double-clicked {button_name}")
        self.last_click_time = current_time



    # ===== MAIN LOOP =====

    def run(self):
        """Main run loop with smooth WASD navigation"""
        print("\n🚀 Starting Nexus 25D Visualizer...")
        print("=" * 60)
        
        # Main loop
        while self.running:
            delta_time = self.clock.tick(self.target_fps) / 1000.0
            
            # ===== CHECK FOR LOADING STATE AND LOAD =====
            if self.mode == self.MODE_LOADING:
                success = self.load_session_data()
                if success:
                    self.mode = self.MODE_REPLAY
                    self._add_log(f"✅ Successfully loaded session: {self.session_id}")
                else:
                    self.mode = self.MODE_BROWSER
                    self._add_log(f"❌ Failed to load session: {self.session_id}")
                continue
            
            # ===== SMOOTH WASD NAVIGATION =====
            if self.mode in [self.MODE_REPLAY, self.MODE_LIVE]:
                keys = pygame.key.get_pressed()
                pan_speed = 300 * delta_time 
                moved = False
                
                if keys[pygame.K_s]:
                    self.pan_y -= pan_speed
                    moved = True
                if keys[pygame.K_w]:
                    self.pan_y += pan_speed
                    moved = True
                if keys[pygame.K_d]:
                    self.pan_x -= pan_speed
                    moved = True
                if keys[pygame.K_a]:
                    self.pan_x += pan_speed
                    moved = True
                
                if moved:
                    self.update_neuron_positions()
            
            # ===== HANDLE EVENTS =====
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event.key)
                    
                elif event.type == pygame.KEYUP:
                    self._handle_keyup(event.key)
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self._handle_left_click_complete(event.pos)
                    elif event.button == 4:  # Scroll up
                        self._handle_zoom(event.pos, 1.1)
                    elif event.button == 5:  # Scroll down
                        self._handle_zoom(event.pos, 0.9)
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    self._handle_mouseup(event.pos, event.button)
                    
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_mousemotion(event.pos)
            
            # ===== UPDATE TIMELINE IF PLAYING =====
            if self.mode == self.MODE_REPLAY and self.timeline.is_playing:
                self.timeline.update(delta_time)
                if self.timeline.should_advance_frame():
                    if self.current_frame_index < len(self.frames) - 1:
                        self.next_frame()
                    else:
                        self.timeline.is_playing = False
                        self._add_log("⏹️ End of recording reached")
            
            # ===== UPDATE PARTICLES =====
            self._update_particles(delta_time)
            
            # ===== DRAW EVERYTHING =====
            self.draw()

            
        pygame.quit()
        print("✅ Visualizer shutdown complete")
  

    def load_session_data(self):
        """Load session data from file"""
        if not self.session_id:
            self._add_log("❌ No session ID specified")
            return False
        
        try:
            session_path = os.path.join(self.base_dir, self.session_id)
            if not os.path.exists(session_path):
                self._add_log(f"❌ Session path not found: {session_path}")
                return False
            
            # Check for frames directory
            frames_dir = os.path.join(session_path, "frames")
            if not os.path.exists(frames_dir):
                self._add_log(f"❌ Frames directory not found: {frames_dir}")
                return False
            
            # Load all frame files from frames directory
            self.frames = []
            # CHANGE THIS LINE: look for frames_*.json files
            frame_files = sorted([f for f in os.listdir(frames_dir) if f.startswith('frame_') and f.endswith('.json')])
            
            if not frame_files:
                self._add_log(f"❌ No frames_*.json files found in {frames_dir}")
                # Try to show what files ARE there for debugging
                all_files = os.listdir(frames_dir)
                self._add_log(f"ℹ️ Files in frames directory: {all_files[:10]}{'...' if len(all_files) > 10 else ''}")
                return False
            
            self._add_log(f"📥 Found {len(frame_files)} frame files")
            
            for i, frame_file in enumerate(frame_files):
                frame_path = os.path.join(frames_dir, frame_file)
                try:
                    with open(frame_path, 'r') as f:
                        frame_data = json.load(f)
                        self.frames.append(frame_data)
                        
                    # Show progress for large sessions
                    if len(frame_files) > 50 and i % (len(frame_files) // 10) == 0:
                        progress = (i + 1) / len(frame_files) * 100
                        self._add_log(f"📥 Loading... {progress:.0f}% ({i + 1}/{len(frame_files)})")
                        
                except Exception as e:
                    self._add_log(f"⚠️ Error loading frame {frame_file}: {e}")
                    continue
            
            if not self.frames:
                self._add_log("❌ No valid frame data loaded")
                return False
            
            self._add_log(f"✅ Loaded {len(self.frames)} frames from {self.session_id}")
            
            # Initialize with first frame
            self.current_frame_index = 0
            self.current_frame_data = self.frames[0] if self.frames else None
            self._update_neurons_from_frame()
            
            # Update statistics data
            self._analyze_statistics_data()
            
            return True
            
        except Exception as e:
            self._add_log(f"❌ Error loading session: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _handle_mouseup(self, pos, button):
        """Handle mouse button up"""
        self.dragging_view = False
        self.dragging_timeline = False
        self.active_button = None
        
        # Handle legend window mouseup
        if self.show_legend and hasattr(self, 'legend_window'):
            self.legend_window.handle_event(
                pygame.event.Event(pygame.MOUSEBUTTONUP, {'button': button, 'pos': pos}),
                pos
            )
        
        if button == 1:  # Left button
            # Finalize timeline drag if active
            if hasattr(self, 'dragging_timeline') and self.dragging_timeline:
                if self.frames:
                    # Calculate which frame based on click position
                    if hasattr(self, 'timeline_handle_rect') and self.timeline_handle_rect:
                        timeline_x = 20
                        timeline_width = self.screen_width // 3 - 120
                        
                        # Get click position relative to timeline
                        if pos[0] < timeline_x:
                            progress = 0.0
                        elif pos[0] > timeline_x + timeline_width:
                            progress = 1.0
                        else:
                            progress = (pos[0] - timeline_x) / timeline_width
                        
                        progress = max(0.0, min(1.0, progress))
                        frame_index = int(progress * (len(self.frames) - 1))
                        self.go_to_frame(frame_index)
                        
                        self._add_log(f"⏱️ Jumped to frame {frame_index + 1}")

    def _handle_mousemotion(self, pos):
        """Handle mouse motion"""
        # Update hover states
        self.hovered_button = None
        self.hovered_neuron_id = None
        
        # ===== UPDATE HOVER STATES =====
        
        # Check UI buttons
        for button_name, button_info in self.ui_buttons.items():
            if button_info['rect'].collidepoint(pos):
                self.hovered_button = button_name
                break
        
        # Check timeline buttons
        if self.mode == self.MODE_REPLAY and hasattr(self, 'timeline_button_rects'):
            for btn_id, rect in self.timeline_button_rects.items():
                if rect.collidepoint(pos):
                    self.hovered_button = btn_id
                    break
        
        # Check statistics tabs and buttons
        if self.mode == self.MODE_STATISTICS:
            if hasattr(self, 'stat_tab_rects'):
                for tab_id, rect in self.stat_tab_rects.items():
                    if rect.collidepoint(pos):
                        self.hovered_button = f"tab_{tab_id}"
                        break
            
            if hasattr(self, 'stat_button_rects') and not self.hovered_button:
                for btn_id, rect in self.stat_button_rects.items():
                    if rect.collidepoint(pos):
                        self.hovered_button = btn_id
                        break
        
        # Check for neuron hover (only if not hovering over buttons)
        if not self.hovered_button and self.mode in [self.MODE_REPLAY, self.MODE_LIVE]:
            for neuron in self.neurons.values():
                if neuron.position:
                    distance = math.sqrt(
                        (pos[0] - neuron.position[0])**2 + 
                        (pos[1] - neuron.position[1])**2
                    )
                    neuron_radius = 12 * self.zoom
                    if distance <= neuron_radius:
                        self.hovered_neuron_id = neuron.id
                        break
        
        # ===== HANDLE DRAGGING =====
        
        # View dragging
        if self.dragging_view:
            dx = pos[0] - self.drag_start_pos[0]
            dy = pos[1] - self.drag_start_pos[1]
            self.pan_x = self.drag_start_pan[0] + dx
            self.pan_y = self.drag_start_pan[1] + dy
            self.update_neuron_positions()
        
        # Timeline dragging
        elif self.dragging_timeline:
            if self.frames:
                timeline_x = 20
                timeline_width = self.screen_width // 3 - 120
                
                if pos[0] < timeline_x:
                    progress = 0.0
                elif pos[0] > timeline_x + timeline_width:
                    progress = 1.0
                else:
                    progress = (pos[0] - timeline_x) / timeline_width
                
                progress = max(0.0, min(1.0, progress))
                self.timeline.current_time = progress * len(self.frames) * self.timeline.frame_interval
        
        # Handle legend window mousemotion
        if self.show_legend and hasattr(self, 'legend_window'):
            self.legend_window.handle_event(
                pygame.event.Event(pygame.MOUSEMOTION, {'pos': pos}),
                pos
            )

    def _handle_zoom(self, mouse_pos, factor):
        """Handle mouse wheel zoom with center adjustment"""
        old_zoom = self.zoom
        self.zoom = max(0.1, min(3.0, self.zoom * factor))
        
        # Adjust pan to keep mouse position centered
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        self.pan_x -= int((mouse_pos[0] - center_x) * (self.zoom - old_zoom) / old_zoom)
        self.pan_y -= int((mouse_pos[1] - center_y) * (self.zoom - old_zoom) / old_zoom)
        
        self.update_neuron_positions()
        zoom_action = "in" if factor > 1 else "out"
        self._add_log(f"🔍 Zoom {zoom_action}: {self.zoom:.1f}x")

    # ===== HELPER METHODS =====
    
    def _add_log(self, message):
        """Add a message to the log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    # ===== UPDATED DRAW METHOD =====

    def _draw_statistics_panel(self):
        """Draw statistics panel in visualization mode"""
        if self.mode in [self.MODE_BROWSER, self.MODE_LOADING, self.MODE_STATISTICS]:
            return
        
        panel_width = 320
        panel_height = 180
        panel_x = 20
        panel_y = 120
        
        # Background
        surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=8)
        self.screen.blit(surf, (panel_x, panel_y))
        
        y_offset = panel_y + 15
        
        # Get current statistics
        current_frame = self.current_frame_data
        neuron_count = len(self.neurons)
        axon_count = len(self.active_axon_beams)
        
        # Calculate UNKNOWN and gamma stats
        unknown_count = 0
        gamma_updated_count = 0
        avg_confidence = 0.0
        
        if self.neurons:
            confidences = []
            for neuron in self.neurons.values():
                confidences.append(neuron.confidence)
                if neuron.is_unknown_pattern:
                    unknown_count += 1
                    if neuron.has_gamma_update:
                        gamma_updated_count += 1
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        stats = [
            f"Neurons: {neuron_count}",
            f"Active Axons: {axon_count}",
            f"Frame: {self.current_frame_index + 1}/{len(self.frames) if self.frames else 0}",
            f"FPS: {self.clock.get_fps():.1f}",
            f"Zoom: {self.zoom:.1f}x",
            f"Pan: ({self.pan_x}, {self.pan_y})",
        ]
        
        # Add UNKNOWN stats if available
        if unknown_count > 0:
            stats.append(f"UNKNOWN: {unknown_count}")
            stats.append(f"γ-updated: {gamma_updated_count}")
        
        # Add confidence
        stats.append(f"Confidence: {avg_confidence:.3f}")
        
        if self.mode == self.MODE_REPLAY:
            playback_status = '▶' if self.timeline.is_playing else '‖'
            stats.append(f"Playback: {playback_status} {self.timeline.playback_speed:.1f}x")
        
        for stat in stats:
            stat_surf = self.small_font.render(stat, True, (200, 220, 255))
            self.screen.blit(stat_surf, (panel_x + 10, y_offset))
            y_offset += 20
            
        # Draw border
        pygame.draw.rect(self.screen, (60, 80, 120, 150), 
                        (panel_x, panel_y, panel_width, panel_height), 2, border_radius=8)

    def update_neuron_positions(self):
        """Update screen positions for all neurons"""
        for neuron in self.neurons.values():
            screen_pos = self._coord_to_screen(neuron.coordinate)
            if screen_pos:
                neuron.position = screen_pos
    
    def _init_color_arrays(self):
        """Initialize color arrays for pulsing states"""
        self.color_array = np.zeros((3, 7, 1000), dtype=np.uint8)
        
        base_colors = {
            'STABLE': (0, 255, 0),        # Green
            'LEARNING': (255, 165, 0),    # Orange
            'NOISY': (255, 255, 0),       # Yellow
            'RIGID': (255, 0, 0),         # Red
            'CONFUSED': (255, 0, 255),    # Purple
            'DEAD': (100, 100, 100),      # Gray
            'UNKNOWN': (200, 200, 200),   # Light Gray
        }
        
        for state_name, state_idx in self.state_indices.items():
            freq = self.state_freqs[state_name]
            num_colors = 1000 // max(1, freq)
            
            base_r, base_g, base_b = base_colors[state_name]
            
            for k in range(num_colors):
                t = k / max(1, num_colors)
                brightness = 0.4 + 0.6 * math.sin(t * math.pi * 2)
                
                r = int(base_r * brightness)
                g = int(base_g * brightness)
                b = int(base_b * brightness)
                
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                if k < self.color_array.shape[2]:
                    self.color_array[0, state_idx, k] = r
                    self.color_array[1, state_idx, k] = g
                    self.color_array[2, state_idx, k] = b
    
    def _draw_neuron_view(self):
        """Draw neuron visualization view"""
        # Draw grid
        center_x = self.screen_width // 2 + self.pan_x
        center_y = self.screen_height // 2 + self.pan_y
        
        if self.show_grid:
            self._draw_white_grid(center_x, center_y)
        
        # Draw connections
        if self.show_axons:
            self._draw_connections()
        
        # Draw neurons
        self._draw_neurons()
        
        # Draw axon comets
        if self.show_axons:
            self._draw_axon_comets()
        
        # Draw state highlights
        if self.show_change_highlights:
            self._draw_state_change_highlights()
        
        # Draw processing states
        if self.show_processing_states:
            self._draw_neurons()  # Already includes inner dots
        
        # Draw neuron labels if zoomed in
        if self.zoom >= 0.8:
            self._draw_neuron_labels()
        
        # Draw hover info
        if self.hovered_neuron_id:
            self._draw_hover_info()
        
        # Draw legend
        if self.show_legend:
            self._draw_updated_legend()
        
        # Draw UI
        self._draw_ui_panel()
        self._draw_ui_buttons()
        self._draw_logs()
        
        # Draw timeline if in replay mode
        if self.mode == self.MODE_REPLAY:
            self._draw_timeline_controls()
    
    def _draw_neurons(self):
        """Draw all neurons with SpideySelector styling"""
        current_time = time.time()
        center_x = self.screen_width // 2 + self.pan_x
        center_y = self.screen_height // 2 + self.pan_y
        
        for neuron in self.neurons.values():
            # Get screen position using Spidey exact method
            pos = self._coord_to_screen(neuron.coordinate, center_x, center_y)
            if not pos:
                continue
                
            neuron.position = pos
            
            # Get pattern color (Spidey style)
            pattern_color = PATTERN_COLORS.get(neuron.pattern, (200, 200, 200))
            
            # Determine node size based on state (Spidey sizes)
            if neuron.id == self.hovered_neuron_id:
                base_size = 8  # Hovered nodes are slightly larger
            elif neuron.id == self.selected_neuron_id:
                base_size = 9  # Selected nodes are largest
            else:
                base_size = 6  # Normal nodes
            
            # Apply zoom
            node_size = max(3, int(base_size * self.zoom))
            
            # Draw outer circle (pattern color) - Spidey style
            pygame.draw.circle(self.screen, pattern_color, pos, node_size)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, node_size, 1)
            
            # Draw inner state indicator (Spidey's small white dot)
            state_color = STATE_COLORS.get(neuron.current_state, (200, 200, 200))
            inner_size = max(2, int(node_size * 0.6))
            pygame.draw.circle(self.screen, state_color, pos, inner_size)
            
            # Draw eigen indicators if enabled (small dots around node)
            if self.show_eigen_values:
                self._draw_eigen_indicators(neuron, pos, node_size)
            
            # REMOVED: Unknown highlighting code
            
            # Draw coordinate label if zoomed in (Spidey style)
            if self.zoom > 1.2:
                coord_str = str(neuron.coordinate[-1]) if neuron.coordinate else "0"
                if len(neuron.coordinate) > 1:
                    coord_str = f"{neuron.coordinate[-2]}.{coord_str}"
                
                label_surf = self.small_font.render(coord_str, True, (255, 255, 255, 200))
                label_rect = label_surf.get_rect(center=(pos[0], pos[1] + node_size + 10))
                
                # Background for readability
                bg_rect = label_rect.inflate(4, 2)
                bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(bg_surf, (0, 0, 0, 150), bg_surf.get_rect(), border_radius=2)
                self.screen.blit(bg_surf, bg_rect)
                
                self.screen.blit(label_surf, label_rect)
                
    def _draw_eigen_indicators(self, neuron, pos, base_size):
        """Draw eigen value indicators around neuron (small colored dots)"""
        eigen_values = [
            ('alpha', neuron.eigen_alpha, EIGEN_COLORS['alpha']),
            ('beta', neuron.eigen_beta, EIGEN_COLORS['beta']),
            ('gamma', neuron.eigen_gamma, EIGEN_COLORS['gamma']),
            ('zeta', neuron.eigen_zeta, EIGEN_COLORS['zeta']),
        ]
        
        radius = base_size * 1.8
        angles = [0, math.pi/2, math.pi, 3*math.pi/2]  # Right, Down, Left, Up
        
        for i, (label, value, color) in enumerate(eigen_values):
            if value > 0.1:  # Only show significant values
                angle = angles[i]
                x = pos[0] + math.cos(angle) * radius
                y = pos[1] + math.sin(angle) * radius
                
                dot_size = max(1, int(3 * value * self.zoom))
                pygame.draw.circle(self.screen, color, (int(x), int(y)), dot_size)
                
                # Label for very high values when zoomed in
                if value > 0.5 and self.zoom > 1.5:
                    label_surf = self.small_font.render(label[0], True, (255, 255, 255, 180))
                    label_rect = label_surf.get_rect(center=(int(x), int(y)))
                    self.screen.blit(label_surf, label_rect)
    
    def _draw_unknown_indicator(self, neuron, pos, base_size, current_time):
        """Draw indicator for UNKNOWN pattern neurons (subtle pulsing)"""
        if not neuron.is_unknown_pattern:
            return
        
        # Subtle pulse effect
        pulse = 0.7 + 0.3 * math.sin(current_time * 2)
        
        # Draw a thin ring around the node
        ring_radius = base_size + 3
        ring_width = max(1, int(2 * self.zoom))
        
        # Create ring surface
        ring_size = int((ring_radius + ring_width) * 2)
        ring_surface = pygame.Surface((ring_size, ring_size), pygame.SRCALPHA)
        
        # Draw ring with pulse alpha
        ring_alpha = int(150 * pulse)
        pygame.draw.circle(ring_surface, (100, 150, 255, ring_alpha),
                        (ring_size//2, ring_size//2), ring_radius, ring_width)
        
        self.screen.blit(ring_surface, (pos[0] - ring_size//2, pos[1] - ring_size//2))
        
        # Gamma update indicator (if applicable)
        if neuron.has_gamma_update:
            gamma_size = base_size + 2
            gamma_surface = pygame.Surface((gamma_size * 2, gamma_size * 2), pygame.SRCALPHA)
            gamma_alpha = int(100 * (0.5 + 0.5 * math.sin(current_time * 3)))
            pygame.draw.circle(gamma_surface, (255, 100, 255, gamma_alpha),
                            (gamma_size, gamma_size), gamma_size, 2)
            self.screen.blit(gamma_surface, (pos[0] - gamma_size, pos[1] - gamma_size))
            
    def _draw_eigen_values(self, neuron, pos, base_size):
        """Draw eigen values around neuron"""
        eigen_values = [
            ('α', neuron.eigen_alpha, EIGEN_COLORS['alpha']),
            ('β', neuron.eigen_beta, EIGEN_COLORS['beta']),
            ('γ', neuron.eigen_gamma, EIGEN_COLORS['gamma']),
            ('ζ', neuron.eigen_zeta, EIGEN_COLORS['zeta']),
        ]
        
        radius = base_size * 1.8
        angles = [0, math.pi/2, math.pi, 3*math.pi/2]  # Right, Down, Left, Up
        
        for i, (label, value, color) in enumerate(eigen_values):
            if value > 0.1:  # Only show significant values
                angle = angles[i]
                x = pos[0] + math.cos(angle) * radius
                y = pos[1] + math.sin(angle) * radius
                
                dot_size = max(2, int(4 * value * self.zoom))
                pygame.draw.circle(self.screen, color, (int(x), int(y)), dot_size)
                
                # Draw small label for significant values
                if value > 0.3 and self.zoom > 1.2:
                    label_surf = self.small_font.render(label, True, (255, 255, 255, 180))
                    label_rect = label_surf.get_rect(center=(int(x), int(y)))
                    self.screen.blit(label_surf, label_rect)

    def _draw_updated_legend(self):
        """Draw draggable legend panel"""
        # Use the draggable window system
        def draw_legend_content(screen, content_rect, font):
            x, y = content_rect.x, content_rect.y
            width, height = content_rect.width, content_rect.height
            
            # Title
            title = font.render("NEXUS 25D LEGEND", True, (255, 255, 200))
            screen.blit(title, (x + 15, y + 10))
            
            y_offset = y + 40
            
            # Eigen states
            eigen_title = self.small_font.render("EIGEN STATES:", True, (255, 255, 180))
            screen.blit(eigen_title, (x + 15, y_offset))
            y_offset += 25
            
            eigen_states = [
                ('α (Alpha)', EIGEN_COLORS['alpha']),
                ('β (Beta)', EIGEN_COLORS['beta']),
                ('γ (Gamma)', EIGEN_COLORS['gamma']),
                ('ζ (Zeta)', EIGEN_COLORS['zeta']),
            ]
            
            for i, (label, color) in enumerate(eigen_states):
                state_y = y_offset + i * 30
                pygame.draw.circle(screen, color, (x + 25, state_y + 8), 6)
                label_surf = self.small_font.render(label, True, (200, 220, 255))
                screen.blit(label_surf, (x + 40, state_y))
            
            y_offset += len(eigen_states) * 30 + 15
            
            # Patterns
            pattern_title = self.small_font.render("PATTERNS:", True, (255, 255, 180))
            screen.blit(pattern_title, (x + 15, y_offset))
            y_offset += 25
            
            patterns = [
                ('ACT', PATTERN_COLORS['ACTION_ELEMENT']),
                ('DATA', PATTERN_COLORS['DATA_INPUT']),
                ('CTX', PATTERN_COLORS['CONTEXT_ELEMENT']),
                ('STR', PATTERN_COLORS['STRUCTURAL']),
                ('UNK', PATTERN_COLORS['UNKNOWN']),
            ]
            
            patterns_per_column = 3
            column_width = width // 2 - 20
            
            for i, (label, color) in enumerate(patterns):
                col = 0 if i < patterns_per_column else 1
                row = i if col == 0 else i - patterns_per_column
                
                pattern_x = x + 20 + (col * column_width)
                pattern_y = y_offset + row * 25
                
                pygame.draw.circle(screen, color, (pattern_x, pattern_y + 8), 6)
                pygame.draw.circle(screen, (255, 255, 255), (pattern_x, pattern_y + 8), 6, 1)
                pygame.draw.circle(screen, (150, 150, 150), (pattern_x, pattern_y + 8), 2)
                
                label_surf = self.small_font.render(label, True, (200, 220, 255))
                screen.blit(label_surf, (pattern_x + 15, pattern_y))
            
            y_offset += patterns_per_column * 25 + 15
            
            # Statistics
            stats_title = self.small_font.render("STATISTICS:", True, (255, 255, 180))
            screen.blit(stats_title, (x + 15, y_offset))
            y_offset += 25
            
            # Safely get frame index
            try:
                current_frame = int(self.current_frame_index) + 1
            except (ValueError, TypeError):
                current_frame = 1
                
            total_frames = len(self.frames) if self.frames else 0
            
            stats = [
                f"Frame: {current_frame}/{total_frames}",
                f"Neurons: {len(self.neurons)}",
                f"UNKNOWN: {self.statistics_data.get('unknown_count', 0)}",
                f"γ-updated: {self.statistics_data.get('gamma_updated_count', 0)}",
                f"Confidence: {self.statistics_data.get('avg_confidence', 0.0):.2f}",
            ]
            
            for stat in stats:
                stat_surf = self.small_font.render(stat, True, (200, 220, 255))
                screen.blit(stat_surf, (x + 25, y_offset))
                y_offset += 22
        
        # Draw the window
        if 'legend' in self.windows and self.windows['legend'].visible:
            self.windows['legend'].draw(self.screen, self.font, draw_legend_content)
        elif self.show_legend:
            # Fallback: Draw directly
            panel_x, panel_y = self.legend_position
            panel_width, panel_height = self.legend_size
            
            # Draw panel background
            surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            pygame.draw.rect(surf, (20, 20, 40, 240), 
                            surf.get_rect(), border_radius=8)
            pygame.draw.rect(surf, (80, 80, 120, 150),
                            surf.get_rect(), 2, border_radius=8)
            self.screen.blit(surf, (panel_x, panel_y))
            
            # Draw title
            title = self.font.render("NEXUS 25D VISUALIZER", True, (255, 255, 200))
            self.screen.blit(title, (panel_x + 15, panel_y + 10))
            
            # Draw content using the same layout as above
            y_offset = panel_y + 40
            
            # Eigen states
            eigen_title = self.small_font.render("EIGEN STATES:", True, (255, 255, 180))
            self.screen.blit(eigen_title, (panel_x + 15, y_offset))
            y_offset += 25
            
            eigen_states = [
                ('α (Alpha)', EIGEN_COLORS['alpha']),
                ('β (Beta)', EIGEN_COLORS['beta']),
                ('γ (Gamma)', EIGEN_COLORS['gamma']),
                ('ζ (Zeta)', EIGEN_COLORS['zeta']),
            ]
            
            for i, (label, color) in enumerate(eigen_states):
                state_y = y_offset + i * 30
                pygame.draw.circle(self.screen, color, (panel_x + 25, state_y + 8), 6)
                label_surf = self.small_font.render(label, True, (200, 220, 255))
                self.screen.blit(label_surf, (panel_x + 40, state_y))
            
            y_offset += len(eigen_states) * 30 + 15
            
            # Patterns
            pattern_title = self.small_font.render("PATTERNS:", True, (255, 255, 180))
            self.screen.blit(pattern_title, (panel_x + 15, y_offset))
            y_offset += 25
            
            patterns = [
                ('ACT', PATTERN_COLORS['ACTION_ELEMENT']),
                ('DATA', PATTERN_COLORS['DATA_INPUT']),
                ('CTX', PATTERN_COLORS['CONTEXT_ELEMENT']),
                ('STR', PATTERN_COLORS['STRUCTURAL']),
                ('UNK', PATTERN_COLORS['UNKNOWN']),
            ]
            
            patterns_per_column = 3
            column_width = panel_width // 2 - 20
            
            for i, (label, color) in enumerate(patterns):
                col = 0 if i < patterns_per_column else 1
                row = i if col == 0 else i - patterns_per_column
                
                pattern_x = panel_x + 20 + (col * column_width)
                pattern_y = y_offset + row * 25
                
                pygame.draw.circle(self.screen, color, (pattern_x, pattern_y + 8), 6)
                pygame.draw.circle(self.screen, (255, 255, 255), (pattern_x, pattern_y + 8), 6, 1)
                pygame.draw.circle(self.screen, (150, 150, 150), (pattern_x, pattern_y + 8), 2)
                
                label_surf = self.small_font.render(label, True, (200, 220, 255))
                self.screen.blit(label_surf, (pattern_x + 15, pattern_y))
            
            y_offset += patterns_per_column * 25 + 15
            
            # Statistics
            stats_title = self.small_font.render("STATISTICS:", True, (255, 255, 180))
            self.screen.blit(stats_title, (panel_x + 15, y_offset))
            y_offset += 25
            
            # Safely get frame index
            try:
                current_frame = int(self.current_frame_index) + 1
            except (ValueError, TypeError):
                current_frame = 1
                
            total_frames = len(self.frames) if self.frames else 0
            
            stats = [
                f"Frame: {current_frame}/{total_frames}",
                f"Neurons: {len(self.neurons)}",
                f"UNKNOWN: {self.statistics_data.get('unknown_count', 0)}",
                f"γ-updated: {self.statistics_data.get('gamma_updated_count', 0)}",
                f"Confidence: {self.statistics_data.get('avg_confidence', 0.0):.2f}",
            ]
            
            for stat in stats:
                stat_surf = self.small_font.render(stat, True, (200, 220, 255))
                self.screen.blit(stat_surf, (panel_x + 25, y_offset))
                y_offset += 22


    def _draw_hover_info(self):
        """Draw hover information panel"""
        if not self.hovered_neuron_id or self.hovered_neuron_id not in self.neurons:
            return
        
        neuron = self.neurons[self.hovered_neuron_id]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Create panel
        panel_width = 400
        panel_height = 350
        panel_x = mouse_x + 20
        panel_y = mouse_y + 20
        
        if panel_x + panel_width > self.screen_width:
            panel_x = mouse_x - panel_width - 20
        if panel_y + panel_height > self.screen_height:
            panel_y = mouse_y - panel_height - 20
        
        # Background
        surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 240), surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, (80, 100, 180, 150), surf.get_rect(), 2, border_radius=8)
        self.screen.blit(surf, (panel_x, panel_y))
        
        y_offset = panel_y + 15
        
        # Title
        title = f"Neuron: {neuron.id[:15]}..."
        title_surf = self.font.render(title, True, (255, 255, 200))
        self.screen.blit(title_surf, (panel_x + 15, y_offset))
        y_offset += 30
        
        # Coordinate
        coord_str = str(neuron.coordinate)[:30] + "..." if len(str(neuron.coordinate)) > 30 else str(neuron.coordinate)
        coord_surf = self.small_font.render(f"Coord: {coord_str}", True, (200, 220, 255))
        self.screen.blit(coord_surf, (panel_x + 15, y_offset))
        y_offset += 25
        
        # Pattern
        pattern_color = PATTERN_COLORS.get(neuron.pattern, (200, 200, 200))
        pygame.draw.circle(self.screen, pattern_color, (panel_x + 15, y_offset + 8), 6)
        pattern_text = f"Pattern: {neuron.pattern}"
        pattern_surf = self.small_font.render(pattern_text, True, (200, 220, 255))
        self.screen.blit(pattern_surf, (panel_x + 30, y_offset))
        y_offset += 25
        
        # State
        state_color = STATE_COLORS.get(neuron.current_state, (200, 200, 200))
        pygame.draw.circle(self.screen, state_color, (panel_x + 15, y_offset + 8), 6)
        state_text = f"State: {neuron.current_state}"
        state_surf = self.small_font.render(state_text, True, (200, 220, 255))
        self.screen.blit(state_surf, (panel_x + 30, y_offset))
        y_offset += 25
        
        # Confidence
        conf_text = f"Confidence: {neuron.confidence:.2f}"
        conf_surf = self.small_font.render(conf_text, True, (200, 220, 255))
        self.screen.blit(conf_surf, (panel_x + 15, y_offset))
        y_offset += 20
        
        # Eigen values
        eigen_text = f"Eigen Values:"
        eigen_surf = self.small_font.render(eigen_text, True, (255, 255, 180))
        self.screen.blit(eigen_surf, (panel_x + 15, y_offset))
        y_offset += 20
        
        eigen_values = [
            ('α', neuron.eigen_alpha, EIGEN_COLORS['alpha']),
            ('β', neuron.eigen_beta, EIGEN_COLORS['beta']),
            ('γ', neuron.eigen_gamma, EIGEN_COLORS['gamma']),
            ('ζ', neuron.eigen_zeta, EIGEN_COLORS['zeta']),
        ]
        
        for i, (label, value, color) in enumerate(eigen_values):
            row = i % 2
            col = i // 2
            value_x = panel_x + 20 + (col * 180)
            value_y = y_offset + (row * 20)
            
            pygame.draw.circle(self.screen, color, (value_x, value_y + 8), 4)
            value_text = f"{label}: {value:.2f}"
            value_surf = self.small_font.render(value_text, True, (200, 220, 255))
            self.screen.blit(value_surf, (value_x + 10, value_y))
        
        y_offset += 40
        
        # Health info
        if hasattr(neuron, 'health_status') and neuron.health_status != 'UNKNOWN':
            health_text = f"Health: {neuron.health_status}"
            health_surf = self.small_font.render(health_text, True, (200, 220, 255))
            self.screen.blit(health_surf, (panel_x + 15, y_offset))
            y_offset += 20
            
            score_text = f"Score: {neuron.health_score:.2f}"
            score_surf = self.small_font.render(score_text, True, (200, 220, 255))
            self.screen.blit(score_surf, (panel_x + 15, y_offset))
            y_offset += 20
        
        # UNKNOWN specific info
        if neuron.is_unknown_pattern:
            unknown_text = "UNKNOWN PATTERN"
            unknown_surf = self.small_font.render(unknown_text, True, (100, 150, 255))
            self.screen.blit(unknown_surf, (panel_x + 15, y_offset))
            y_offset += 20
            
            if neuron.has_gamma_update:
                gamma_text = "γ-Updated"
                gamma_surf = self.small_font.render(gamma_text, True, (255, 100, 255))
                self.screen.blit(gamma_surf, (panel_x + 15, y_offset))
                y_offset += 20
        
        # Timing info
        cycle_text = f"Cycle: {neuron.cycle}"
        cycle_surf = self.small_font.render(cycle_text, True, (180, 200, 255))
        self.screen.blit(cycle_surf, (panel_x + 15, y_offset))
        y_offset += 20
    
    def _draw_timeline_controls(self):
        """Draw timeline controls for replay mode"""
        if not self.frames:
            return
        
        panel_width = self.screen_width // 3
        panel_height = 80
        timeline_x = 20
        timeline_y = self.screen_height - panel_height - 150
        
        # Panel background
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (25, 25, 50, 220), 
                        panel_surf.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surf, (70, 90, 140, 120),
                        panel_surf.get_rect(), 2, border_radius=8)
        self.screen.blit(panel_surf, (timeline_x, timeline_y))
        
        # Title
        title = self.small_font.render("TIMELINE CONTROLS", True, (200, 220, 255))
        self.screen.blit(title, (timeline_x + 10, timeline_y + 8))
        
        # Progress bar
        bar_width = panel_width - 120
        bar_x = timeline_x + 10
        bar_y = timeline_y + 30
        bar_height = 15
        
        pygame.draw.rect(self.screen, (60, 70, 90), 
                        (bar_x, bar_y, bar_width, bar_height), border_radius=7)
        
        progress = self.timeline.get_progress()
        fill_width = int(bar_width * progress)
        
        if fill_width > 0:
            fill_surf = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(fill_surf, (100, 180, 255, 220),
                            fill_surf.get_rect(), border_radius=7)
            self.screen.blit(fill_surf, (bar_x, bar_y))
        
        pygame.draw.rect(self.screen, (80, 100, 180, 150), 
                        (bar_x, bar_y, bar_width, bar_height), 1, border_radius=7)
        
        # Handle
        handle_x = bar_x + int(bar_width * progress)
        handle_y = bar_y + bar_height // 2
        handle_radius = 8
        
        handle_rect = pygame.Rect(handle_x - handle_radius, handle_y - handle_radius, 
                                handle_radius * 2, handle_radius * 2)
        self.timeline_handle_rect = handle_rect
        
        pygame.draw.circle(self.screen, (150, 200, 255), (handle_x, handle_y), handle_radius)
        pygame.draw.circle(self.screen, (80, 120, 200), (handle_x, handle_y), handle_radius, 2)
        
        # Buttons
        button_width = 60
        button_height = 24
        button_y = bar_y + bar_height + 10
        
        control_buttons = [
            ('timeline_play', timeline_x + 10, button_y, button_width, button_height, 
            'PLAY', 'Play/Pause'),
            ('timeline_prev', timeline_x + 80, button_y, button_width, button_height, 
            'PREV', 'Previous Frame'),
            ('timeline_next', timeline_x + 150, button_y, button_width, button_height, 
            'NEXT', 'Next Frame'),
            ('timeline_slower', timeline_x + 220, button_y, button_width, button_height, 
            'SLOW', 'Decrease Speed'),
            ('timeline_faster', timeline_x + 290, button_y, button_width, button_height, 
            'FAST', 'Increase Speed'),
        ]
        
        self.timeline_button_rects = {}
        
        for btn_id, x, y, w, h, label, tooltip in control_buttons:
            rect = pygame.Rect(x, y, w, h)
            self.timeline_button_rects[btn_id] = rect
            
            if btn_id == self.active_button:
                bg_color = (80, 100, 180, 200)
                border_color = (120, 140, 220)
                text_color = (255, 255, 255)
            elif btn_id == self.hovered_button:
                bg_color = (70, 90, 170, 180)
                border_color = (100, 120, 200)
                text_color = (240, 240, 255)
            else:
                bg_color = (60, 80, 160, 150)
                border_color = (80, 100, 180, 120)
                text_color = (220, 220, 240)
            
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=4)
            pygame.draw.rect(self.screen, border_color, rect, 1, border_radius=4)
            
            label_surf = self.small_font.render(label, True, text_color)
            label_rect = label_surf.get_rect(center=rect.center)
            self.screen.blit(label_surf, label_rect)
    
    def _draw_ui_buttons(self):
        """Draw UI buttons"""
        for button_name, button_info in self.ui_buttons.items():
            rect = button_info['rect'].copy()
            label = button_info['label']
            
            if button_name == self.active_button:
                bg_color = (80, 100, 180)
                border_color = (120, 140, 220)
                text_color = (255, 255, 255)
            elif button_name == self.hovered_button:
                bg_color = (70, 90, 170)
                border_color = (100, 120, 200)
                text_color = (240, 240, 255)
            else:
                bg_color = (60, 80, 160)
                border_color = (80, 100, 180)
                text_color = (220, 220, 240)
            
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=6)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=6)
            
            label_surf = self.small_font.render(label, True, text_color)
            label_rect = label_surf.get_rect(center=rect.center)
            self.screen.blit(label_surf, label_rect)
    
    def _draw_logs(self):
        """Draw terminal logs"""
        if not self.logs:
            return
        
        terminal_width = self.screen_width // 3
        terminal_height = 150
        terminal_x = 20
        terminal_y = self.screen_height - terminal_height - 5
        
        # Background
        surf = pygame.Surface((terminal_width, terminal_height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (15, 18, 25, 240), surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 1, border_radius=8)
        self.screen.blit(surf, (terminal_x, terminal_y))
        
        # Title
        title = self.small_font.render("TERMINAL LOGS", True, (200, 220, 255))
        self.screen.blit(title, (terminal_x + 10, terminal_y + 8))
        
        # Logs (last 7)
        y_offset = terminal_y + 30
        visible_logs = list(self.logs)[-7:]
        
        for log in visible_logs:
            log_surf = self.mono_font.render(log, True, (180, 220, 180))
            log_rect = log_surf.get_rect(x=terminal_x + 10, y=y_offset)
            
            # Truncate if too long
            if log_rect.width > terminal_width - 20:
                truncated = log[:40] + "..." if len(log) > 40 else log
                log_surf = self.mono_font.render(truncated, True, (180, 220, 180))
            
            self.screen.blit(log_surf, (terminal_x + 10, y_offset))
            y_offset += 18
    
    def _draw_browser(self):
        """Draw session browser"""
        # Title
        title = self.title_font.render("NEXUS SESSION BROWSER", True, (255, 255, 200))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 40))
        
        subtitle = self.small_font.render("Select a session and press ENTER to load", True, (200, 220, 255))
        self.screen.blit(subtitle, (self.screen_width // 2 - subtitle.get_width() // 2, 80))
        
        # Sessions panel
        panel_width = self.screen_width - 200
        panel_height = self.screen_height - 200
        panel_x = 100
        panel_y = 120
        
        surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (20, 25, 40, 220), surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, (60, 80, 120, 150), surf.get_rect(), 2, border_radius=8)
        self.screen.blit(surf, (panel_x, panel_y))
        
        # Column headers
        headers = ["SESSION ID", "FRAMES", "MODIFIED", "PATH"]
        header_x = panel_x + 20
        
        for i, header in enumerate(headers):
            header_surf = self.font.render(header, True, (255, 255, 180))
            x = header_x + i * 250
            self.screen.blit(header_surf, (x, panel_y + 15))
        
        # Sessions list
        y_offset = panel_y + 50
        sessions_to_show = self.browser.sessions[
            self.browser.scroll_offset:
            self.browser.scroll_offset + self.browser.visible_items
        ]
        
        self.hovered_session_index = None
        mouse_pos = pygame.mouse.get_pos()
        
        for i, session in enumerate(sessions_to_show):
            item_index = self.browser.scroll_offset + i
            item_y = y_offset + i * 40
            
            # Highlight selected or hovered
            is_selected = item_index == self.browser.selected_index
            item_rect = pygame.Rect(panel_x + 10, item_y, panel_width - 20, 35)
            
            if item_rect.collidepoint(mouse_pos):
                self.hovered_session_index = item_index
                pygame.draw.rect(self.screen, (40, 60, 100, 150), item_rect, border_radius=6)
            elif is_selected:
                pygame.draw.rect(self.screen, (60, 80, 140, 180), item_rect, border_radius=6)
            
            # Draw session info
            col_x = panel_x + 20
            
            # Session ID
            id_text = session['id'][:20] + "..." if len(session['id']) > 20 else session['id']
            id_surf = self.small_font.render(id_text, True, (200, 220, 255))
            self.screen.blit(id_surf, (col_x, item_y + 10))
            
            # Frame count
            frames_text = str(session['frame_count'])
            frames_surf = self.small_font.render(frames_text, True, (180, 255, 180))
            self.screen.blit(frames_surf, (col_x + 250, item_y + 10))
            
            # Modified time
            time_text = session['time_str']
            time_surf = self.small_font.render(time_text, True, (200, 200, 240))
            self.screen.blit(time_surf, (col_x + 500, item_y + 10))
            
            # Path (truncated)
            path_text = session['path'][:40] + "..." if len(session['path']) > 40 else session['path']
            path_surf = self.small_font.render(path_text, True, (200, 220, 240))
            self.screen.blit(path_surf, (col_x + 750, item_y + 10))
        
        # Scroll indicators
        if self.browser.scroll_offset > 0:
            up_arrow = self.font.render("▲", True, (200, 220, 255))
            self.screen.blit(up_arrow, (panel_x + panel_width - 40, panel_y + 10))
        
        if self.browser.scroll_offset + self.browser.visible_items < len(self.browser.sessions):
            down_arrow = self.font.render("▼", True, (200, 220, 255))
            self.screen.blit(down_arrow, (panel_x + panel_width - 40, panel_y + panel_height - 30))
        
        # Instructions
        instructions = [
            "↑↓: Navigate • ENTER: Load • ESC: Exit • HOME/END: Jump to ends",
            f"Showing {len(sessions_to_show)} of {len(self.browser.sessions)} sessions"
        ]
        
        y_pos = panel_y + panel_height + 20
        for instruction in instructions:
            instr_surf = self.small_font.render(instruction, True, (180, 200, 255))
            self.screen.blit(instr_surf, (panel_x, y_pos))
            y_pos += 20
    
    def _draw_loading_screen(self):
        """Draw loading screen"""
        # Background
        self.screen.fill((15, 18, 25))
        
        # Title
        title = self.title_font.render("NEXUS 25D VISUALIZER", True, (255, 255, 200))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 150))
        
        # Loading text
        loading_text = f"Loading session: {self.session_id}"
        loading_surf = self.font.render(loading_text, True, (200, 220, 255))
        self.screen.blit(loading_surf, (self.screen_width // 2 - loading_surf.get_width() // 2, 250))
        
        # Progress bar
        bar_width = 600
        bar_height = 30
        bar_x = self.screen_width // 2 - bar_width // 2
        bar_y = 320
        
        pygame.draw.rect(self.screen, (40, 50, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=15)
        
        # Animated progress
        if self.frames:
            progress = min(1.0, len(self.frames) / 100.0)  # Estimate
            fill_width = int(bar_width * progress)
            
            if fill_width > 0:
                pygame.draw.rect(self.screen, (100, 180, 255), 
                               (bar_x, bar_y, fill_width, bar_height), border_radius=15)
        
        pygame.draw.rect(self.screen, (80, 100, 180), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=15)
        
        # Loading animation
        current_time = time.time()
        pulse = 0.5 + 0.5 * math.sin(current_time * 3)
        
        for i in range(3):
            dot_x = self.screen_width // 2 - 20 + i * 20
            dot_y = bar_y + bar_height + 40
            
            alpha = int(200 * (1.0 - i * 0.3) * pulse)
            color = (100, 180, 255, alpha)
            
            surf = pygame.Surface((15, 15), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (7, 7), 7)
            self.screen.blit(surf, (dot_x, dot_y))

    def draw(self):
        """Main drawing method"""
        # Clear screen
        self.screen.fill((10, 12, 18))
        
        if self.mode == self.MODE_BROWSER:
            self._draw_browser()
        elif self.mode == self.MODE_LOADING:
            self._draw_loading_screen()
        elif self.mode == self.MODE_STATISTICS:
            # Draw statistics page
            self.screen.fill((10, 12, 18))
            
            # Title
            title = self.title_font.render("NEXUS 25D STATISTICS DASHBOARD", True, (255, 255, 200))
            self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 30))
            
            # Session info
            if self.session_id:
                session_text = f"Session: {self.session_id[:30]}{'...' if len(self.session_id) > 30 else ''}"
                session_surf = self.small_font.render(session_text, True, (180, 200, 255))
                self.screen.blit(session_surf, (20, 80))
            
            # Statistics tabs
            self._draw_statistics_tabs()
            
            # Content based on current view
            if self.stat_page_state['view'] == 'overview':
                self._draw_statistics_overview()
            elif self.stat_page_state['view'] == 'eigen':
                self._draw_eigen_statistics()
            elif self.stat_page_state['view'] == 'confidence':
                self._draw_confidence_statistics()
            elif self.stat_page_state['view'] == 'unknown':
                self._draw_unknown_statistics()
            
            # Draw UI buttons for statistics mode
            self._draw_statistics_ui_buttons()
            
            # Draw logs at bottom
            self._draw_logs()
        else:
            self._draw_neuron_view()
        
        pygame.display.flip()
        
    # ===== UPDATED UI BUTTONS =====
    def _init_ui_buttons(self):
        """Initialize UI buttons including statistics button"""
        button_width = 110
        button_height = 32
        
        self.ui_buttons = {
            'mode_live': {
                'rect': pygame.Rect(20, 120, button_width, button_height),
                'label': '🔴 LIVE',
                'tooltip': 'Switch to Live Mode'
            },
            'mode_replay': {
                'rect': pygame.Rect(140, 120, button_width, button_height),
                'label': '🎬 REPLAY',
                'tooltip': 'Switch to Replay Mode'
            },
            'mode_browser': {
                'rect': pygame.Rect(260, 120, button_width, button_height),
                'label': '📁 BROWSE',
                'tooltip': 'Browse Sessions'
            },
            'mode_stats': {  # NEW: Statistics button
                'rect': pygame.Rect(380, 120, button_width, button_height),
                'label': '📊 STATS',
                'tooltip': 'Switch to Statistics Mode'
            },
            'toggle_legend': {
                'rect': pygame.Rect(self.screen_width - 130, 130, 120, 28),
                'label': '[?] LEGEND',
                'tooltip': 'Toggle Legend'
            },
            'toggle_axons': {
                'rect': pygame.Rect(self.screen_width - 130, 165, 120, 28),
                'label': '~ AXONS',
                'tooltip': 'Toggle Axons'
            },
            'toggle_grid': {
                'rect': pygame.Rect(self.screen_width - 130, 200, 120, 28),
                'label': '# GRID',
                'tooltip': 'Toggle Grid'
            },
            'toggle_eigen': {
                'rect': pygame.Rect(self.screen_width - 130, 235, 120, 28),
                'label': 'αβγζ VALUES',
                'tooltip': 'Show Eigen Values'
            },
            # REMOVED: 'toggle_unknown' button
            'reset_view': {
                'rect': pygame.Rect(self.screen_width - 130, 270, 120, 28),
                'label': '⟲ RESET',
                'tooltip': 'Reset View (Pan/Zoom)'
            },
        }
        
    # ===== UPDATED BUTTON HANDLING =====


# ===== MAIN EXECUTION =====

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Nexus 25D Neural Visualizer")
    parser.add_argument("--session", type=str, help="Direct session ID to load")
    parser.add_argument("--fps", type=int, default=60, help="Target FPS")
    
    args = parser.parse_args()
    
    visualizer = NexusVisualizer(session_id=args.session)
    visualizer.target_fps = args.fps
    
    try:
        visualizer.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Visualizer interrupted by user")
    except Exception as e:
        print(f"\n❌ Visualizer error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("✅ Visualizer shutdown complete")

