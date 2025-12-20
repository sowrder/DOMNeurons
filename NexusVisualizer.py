#!/usr/bin/env python3
"""
🧠 NEXUS NEURAL VISUALIZER - COMPLETE WORKING VERSION
Optimized for Nexus heartbeat export format with frame animation
"""


import pygame
import json
import time
import math
import os
import sys
import random  # Added missing import
from typing import Dict, List, Tuple, Any, Optional, Deque, Set
from collections import deque, defaultdict
from dataclasses import dataclass, field
import threading
import numpy as np
import vispy
from vispy import gloo, app
from vispy.scene import SceneCanvas
 
# ===== ENHANCED COLOR SYSTEM =====
PATTERN_COLORS = {
    'ACTION_ELEMENT': (155, 0, 60),       # Burgundy
    'DATA_INPUT': (60, 65, 72),          # Metallic Grey
    'CONTEXT_ELEMENT': (0, 47, 108),     # Neon Purple
    'STRUCTURAL': (30, 130, 80),           # Forest Green  
    'UNKNOWN': (0, 0, 0),                 # Royal Navy 
    'NEXUS': (255, 255, 255),               # Brighter Gold
}

# ===== STATE PULSE CONFIGURATION =====
STATE_PULSE_SPEEDS = {
    'STABLE': 0.3,      # Slow pulse (very stable)
    'LEARNING': 0.1,    # Medium pulse (active learning)
    'NOISY': 0.01,       # Faster pulse (uncertain)
    'RIGID': 0.2,       # Medium-slow (over-constrained)
    'DEAD': 0.0,        # No pulse (dead)
    'CONFUSED': 0.1,    # Very fast pulse (conflicted)
    'UNKNOWN': 0.25,    # Medium pulse
}


# ===== SIMPLIFIED PARTICLE TYPES =====
# Your AXON_COLORS needs these:
AXON_COLORS = {
    # 5 confidence levels (hash confidence)
    'HASH_CONF_0': (150, 150, 150),   # Gray - super weak
    'HASH_CONF_1': (255, 100, 100),   # Red - low confidence
    'HASH_CONF_2': (194, 178, 128),   # Sandy Yellow - medium
    'HASH_CONF_3': (100, 180, 255),   # Blue - good confidence
    'HASH_CONF_4': (100, 255, 100),   # Green - highest confidence
    
    # Special cases
    'COORDINATE_VOID': (180, 100, 255),  # Purple - void/fizzle
    'NEIGHBOR_FOUND': (255, 215, 0),     # Gold - neighbor found (optional)
}


# ===== PARTICLE BEHAVIORS =====
PARTICLE_BEHAVIORS = {
    'NEIGHBOR_DETECTED': 'ABSORB',      # Gold particle absorbed into neuron
    'COORDINATE_VOID': 'DISSIPATE',     # Purple particle fades out
    'HEARTBEAT': 'PULSE',               # Grey pulse from center outward
    'HASH_EXTRACTED': 'TRAIL',          # Blue trail along coordinate path
    'CONFIDENCE_UPDATE': 'GLOW',        # Green glow based on confidence delta
}

STATE_COLORS = {
    # From neighbor_system['health'] or eigenvalue analysis
    'STABLE': (100, 255, 100),      # Green - High confidence, stable
    'LEARNING': (100, 200, 255),    # Blue - Active learning
    'NOISY': (255, 255, 100),       # Yellow - Uncertain, noisy data
    'RIGID': (255, 100, 100),       # Red - Over-constrained, rigid
    'DEAD': (150, 150, 150),        # Gray - No activity
    'CONFUSED': (159, 0, 255),    # Purple - Conflicting signals
    'UNKNOWN': (200, 200, 200)      # Gray - No eigenvalue data
}




class Particle:
    """Simple particle for axon animations"""
    def __init__(self, axon_type: str, source_pos, target_pos=None):
        self.axon_type = axon_type
        self.color = AXON_COLORS.get(axon_type, (200, 200, 200))
        self.source_pos = source_pos
        self.target_pos = target_pos or source_pos
        self.behavior = PARTICLE_BEHAVIORS.get(axon_type, 'TRAIL')
        
        # Animation state
        self.progress = 0.0
        self.size = 3.0
        self.alpha = 255
        self.created_at = time.time()
        self.speed = random.uniform(0.5, 1.5)
        
        # For special behaviors
        if self.behavior == 'ABSORB':
            self.absorbed = False
        elif self.behavior == 'DISSIPATE':
            self.dissipation_rate = random.uniform(0.3, 0.7)
  
    def update(self):
        """Update visualizer state"""
        current_time = time.time()
        
        # Handle navigation keys
        if self.keys_held[pygame.K_LSHIFT] or self.keys_held[pygame.K_RSHIFT]:
            effective_pan_speed = self.pan_speed * 2.5
        else:
            effective_pan_speed = self.pan_speed
        
        if self.keys_held[pygame.K_LEFT] or self.keys_held[pygame.K_a]:
            self.pan_x += effective_pan_speed
        if self.keys_held[pygame.K_RIGHT] or self.keys_held[pygame.K_d]:
            self.pan_x -= effective_pan_speed
        if self.keys_held[pygame.K_UP] or self.keys_held[pygame.K_w]:
            self.pan_y += effective_pan_speed
        if self.keys_held[pygame.K_DOWN] or self.keys_held[pygame.K_s]:
            self.pan_y -= effective_pan_speed
        
        # Update hover info
        self._update_hover_info()
        
        # Mode-specific updates
        if self.mode == self.MODE_REPLAY and self.timeline.frames:
            # Get next sequence from timeline
            frame = self.timeline.update()
            if frame:
                self._load_current_sequence(frame)
                self.current_sequence_index = self.timeline.current_frame_index
                self.last_frame_time = current_time
        
        elif self.mode == self.MODE_LIVE:
            # Check for new animation sequences
            if current_time - self.last_live_update >= self.live_update_interval:
                # Process any new frames in background
                processed = self.timeline_builder.process_new_frames()
                if processed > 0:
                    self.animation_sequences = self.timeline_builder.get_frames()
                    self._add_log(f"📥 Processed {processed} new animation sequences")
                
                # If no current sequence, load the latest
                if not self.current_sequence and self.animation_sequences:
                    self._load_current_sequence(self.animation_sequences[-1])
                    self.current_sequence_index = len(self.animation_sequences) - 1
                
                self.last_live_update = current_time
        
        # Set sequence index for NeuralAnalyzer caching - ONLY IF IT EXISTS
        if hasattr(self, 'neural_analyzer') and self.neural_analyzer:
            self.neural_analyzer.set_current_sequence_index(self.current_sequence_index)

    def get_position(self):
        """Get current position based on progress"""
        if self.behavior in ['DISSIPATE', 'PULSE']:
            return self.source_pos  # Stays in place
        
        # Linear interpolation for trail/absorb
        x = self.source_pos[0] + (self.target_pos[0] - self.source_pos[0]) * self.progress
        y = self.source_pos[1] + (self.target_pos[1] - self.source_pos[1]) * self.progress
        return (int(x), int(y))
    
    def draw(self, screen):
        """Draw particle"""
        if self.alpha <= 0:
            return
        
        pos = self.get_position()
        color_with_alpha = (*self.color, self.alpha)
        
        # Create surface for alpha blending
        particle_surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        
        if self.behavior == 'PULSE':
            # Pulsing circle for heartbeat
            pygame.draw.circle(particle_surf, color_with_alpha,
                             (int(self.size), int(self.size)), int(self.size))
        else:
            # Solid circle for other particles
            pygame.draw.circle(particle_surf, color_with_alpha,
                             (int(self.size), int(self.size)), int(self.size))
        
        screen.blit(particle_surf, (pos[0] - self.size, pos[1] - self.size))

class ParticleAnimationSystem:
    """Manages all particle animations"""
    def __init__(self):
        self.particles = []
        self.max_particles = 100
    
    def add_particle(self, axon_data: Dict, source_neuron, target_neuron=None):
        """Create particle from axon data"""
        axon_type = axon_data.get('type', 'UNKNOWN')
        
        if axon_type not in PARTICLE_COLORS:
            return  # Skip unknown axon types
        
        # Get positions
        source_pos = source_neuron.position if source_neuron else (0, 0)
        target_pos = None
        
        if target_neuron:
            target_pos = target_neuron.position
        elif 'target_coordinate' in axon_data.get('data', {}):
            # Try to find target by coordinate
            target_coord = tuple(axon_data['data']['target_coordinate'])
            # Look up neuron by coordinate...
        
        # Create particle
        particle = Particle(axon_type, source_pos, target_pos)
        
        # Add to list, remove oldest if at limit
        self.particles.append(particle)
        if len(self.particles) > self.max_particles:
            self.particles.pop(0)
    
    def update(self, delta_time: float):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update(delta_time)]
    
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)
            
# ===== ENHANCED DATA STRUCTURES =====

class VisualNeuron:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'unknown')
        self.coordinate = kwargs.get('coordinate', ())
        self.pattern = kwargs.get('pattern', 'UNKNOWN')
        self.state = kwargs.get('state', 'DEFAULT')
        self.similarity = kwargs.get('similarity', 0.5)
        self.action_step = kwargs.get('action_step', 0)
        self.action_cycle = kwargs.get('action_cycle', 0)
        self.dom_connected = kwargs.get('dom_connected', False)
        self.heartbeat_available = kwargs.get('heartbeat_available', False)
        self.heartbeat_data = kwargs.get('heartbeat_data', {})
        self.heartbeat_time = kwargs.get('heartbeat_time', 0)
        self.axons_this_frame = kwargs.get('axons_this_frame', 0)
        self.axons_types = kwargs.get('axons_types', [])
        self.position = kwargs.get('position', (0, 0))
        self.last_activity = kwargs.get('last_activity', time.time())
        self.current_size = 6.0  # For animation
        
    @property
    def position(self):
        """Calculate position based on coordinate"""
        if hasattr(self, '_position'):
            return self._position
        return (0, 0)
    
    @position.setter
    def position(self, value):
        self._position = value

# If VisualQueue doesn't have a size parameter in __init__, update it:
class VisualQueue:
    def __init__(self, pattern, axon_count=0, neuron_count=0, position=(0, 0), size=15):
        self.pattern = pattern
        self.axon_count = axon_count
        self.neuron_count = neuron_count
        self.position = position
        self.size = size  # Add size parameter
        self.pulse = 0.0
        self.axon_types = {}

    def add_axon(self, axon_type: str):
        """Record axon activity"""
        self.axon_count += 1
        if axon_type not in self.axon_types:
            self.axon_types[axon_type] = 0
        self.axon_types[axon_type] += 1
        self.pulse = 1.0

# ===== TIMELINE SEQUENCER =====
# ===== UPDATED TIMELINE BUILDER FOR NEXUS SAMPLED EXPORTS =====

class TimelineBuilder:
    """Builds coordinated animation sequences from Nexus sampled exports"""
    
    def __init__(self, session_dir: str):
        print(f"📅 TIMELINE BUILDER - Loading session: {session_dir}")
        self.session_dir = session_dir
        
        # Look for Nexus format files
        self.frames_dir = os.path.join(session_dir, "frames")
        self.matrix_dir = os.path.join(session_dir, "matrix")
        
        # Create directories if they don't exist
        os.makedirs(self.frames_dir, exist_ok=True)
        os.makedirs(self.matrix_dir, exist_ok=True)
        
        # Core tracking structures
        self.neuron_registry = {}
        self.matrix_registry = {}
        self.animation_sequences = []
        self.frame_files = []
        self.matrix_files = []
        
        # Scan for files
        self._scan_frame_files()
        self._scan_matrix_files()
        
        # Process data
        if self.frame_files or self.matrix_files:
            self._process_all_data()
            print(f"✅ Built {len(self.animation_sequences)} animation sequences")
            print(f"📊 Loaded {len(self.matrix_registry)} neuron matrix histories")
        else:
            print(f"⚠️ No animation or matrix files found")
            print(f"   Frames directory: {self.frames_dir}")
            print(f"   Matrix directory: {self.matrix_dir}")
    
    def _scan_frame_files(self):
        """Scan for Nexus frame files"""
        if not os.path.exists(self.frames_dir):
            print(f"⚠️ Frames directory not found: {self.frames_dir}")
            return
        
        # Nexus exports frames_*.json or frame_*.json
        import glob
        self.frame_files = glob.glob(os.path.join(self.frames_dir, 'frame_*.json'))
        
        # Also look for chunk files
        chunk_files = glob.glob(os.path.join(self.frames_dir, 'frames_*.json'))
        self.frame_files.extend(chunk_files)
        
        # Remove duplicates and sort
        self.frame_files = sorted(list(set(self.frame_files)))
        print(f"📁 Found {len(self.frame_files)} animation frame files")
    
    def _scan_matrix_files(self):
        """Scan for Nexus matrix evolution files"""
        if not os.path.exists(self.matrix_dir):
            print(f"⚠️ Matrix directory not found: {self.matrix_dir}")
            return
        
        # Nexus exports matrix_evolution_*.json
        import glob
        self.matrix_files = glob.glob(os.path.join(self.matrix_dir, 'matrix_evolution_*.json'))
        
        # Remove duplicates and sort
        self.matrix_files = sorted(list(set(self.matrix_files)))
        print(f"📊 Found {len(self.matrix_files)} matrix evolution files")
    
    def _process_all_data(self):
        """Process all Nexus export data"""
        current_frame_idx = 0
        
        # Process animation frames
        for frame_file in self.frame_files:
            try:
                with open(frame_file, 'r') as f:
                    frame_content = json.load(f)
                
                # Handle Nexus chunk format (list of frames)
                if isinstance(frame_content, list):
                    # File contains list of frames
                    for frame_data in frame_content:
                        sequence = self._build_animation_sequence(frame_data, current_frame_idx)
                        if sequence:
                            self.animation_sequences.append(sequence)
                            current_frame_idx += 1
                else:
                    # File contains single frame
                    sequence = self._build_animation_sequence(frame_content, current_frame_idx)
                    if sequence:
                        self.animation_sequences.append(sequence)
                        current_frame_idx += 1
                        
            except Exception as e:
                print(f"⚠️ Error processing frame file {frame_file}: {e}")
        
        # Process matrix evolution files
        for matrix_file in self.matrix_files:
            try:
                with open(matrix_file, 'r') as f:
                    matrix_content = json.load(f)
                
                # Handle Nexus matrix format
                if isinstance(matrix_content, list):
                    # List of matrix entries
                    for matrix_data in matrix_content:
                        self._process_matrix_evolution(matrix_data)
                else:
                    # Single matrix entry
                    self._process_matrix_evolution(matrix_content)
                        
            except Exception as e:
                print(f"⚠️ Error processing matrix file {matrix_file}: {e}")
        
        # Build statistics
        if self.animation_sequences or self.matrix_registry:
            self._build_cumulative_statistics()
        
        print(f"📊 Built neuron registry with {len(self.neuron_registry)} neurons")
        print(f"📈 Matrix evolution data for {len(self.matrix_registry)} neurons")
    
    def _build_animation_sequence(self, frame_data: Dict, frame_idx: int) -> Dict:
        """Convert Nexus export format to animation sequence"""
        # Extract basic frame info
        session_time = frame_data.get('session_time', 0)
        timestamp = frame_data.get('timestamp', time.time())
        
        # Initialize sequence structure
        sequence = {
            'frame': frame_idx,
            'session_time': session_time,
            'timestamp': timestamp,
            'neurons': [],  # LIST format for Nexus compatibility
            'axons': [],    # Heartbeats as axons
            'system_stats': frame_data.get('system_stats', {}),
            'eigen_system_data': [],
            'matrix_relationship_data': []
        }
        
        # Process neuron data from Nexus format
        neurons_data = frame_data.get('neurons', [])
        
        for neuron_data in neurons_data:
            # Extract Nexus neuron format
            neuron_id = neuron_data.get('neuron_id', f'neuron_{frame_idx}')
            coord = neuron_data.get('coordinate', [0, 0])
            coord_tuple = tuple(coord) if isinstance(coord, list) else coord
            
            # Extract eigen values
            eigen_alpha = neuron_data.get('eigen_alpha', 0.0)
            eigen_beta = neuron_data.get('eigen_beta', 0.0)
            eigen_zeta = neuron_data.get('eigen_zeta', 0.0)
            
            # Get matrix relationships
            matrix_relationships = neuron_data.get('matrix_relationships', {})
            
            # Create neuron animation data in Nexus format
            neuron_anim = {
                'neuron_id': neuron_id,
                'coordinate': list(coord_tuple),  # Convert to list for JSON
                'pattern': neuron_data.get('pattern', 'UNKNOWN'),
                'confidence': neuron_data.get('confidence', 0.5),
                'current_state': 'UNKNOWN',  # Will be determined from eigen
                'processing_phase': neuron_data.get('processing_phase', 'UNKNOWN'),
                'frame': frame_idx,
                'session_time': session_time,
                'timestamp': timestamp,
                
                # Matrix relationships
                'matrix_relationships': matrix_relationships,
                'health_status': neuron_data.get('health_status', 'UNKNOWN'),
                'health_score': neuron_data.get('health_score', 0.0),
                'position_assignments': {},
                
                # Pattern probabilities
                'pattern_probabilities': neuron_data.get('pattern_probabilities', [0.2, 0.2, 0.2, 0.2, 0.2]),
                'dominant_pattern': neuron_data.get('dominant_pattern', 'UNKNOWN'),
                'dominant_probability': neuron_data.get('dominant_probability', 0.2),
                
                # Dot products
                'dot_products': neuron_data.get('dot_products', {}),
                
                # Void and growth
                'void_coordinates': neuron_data.get('void_coordinates', []),
                'has_growth_signals': neuron_data.get('has_growth_signals', False),
                
                # Timing
                'cycle': neuron_data.get('cycle', 0),
                'recycling_iteration': neuron_data.get('recycling_iteration', 0),
                
                # For hover info
                'neighbor_system': {
                    'connected_neighbors': 0,
                    'successful_matches': 0,
                    'health': neuron_data.get('health_status', 'UNKNOWN')
                }
            }
            
            # Determine state from eigen values
            current_state = self._determine_state_from_eigen(
                eigen_alpha, eigen_beta, eigen_zeta, 
                neuron_data.get('health_status', 'UNKNOWN')
            )
            neuron_anim['current_state'] = current_state
            
            # Add to sequence
            sequence['neurons'].append(neuron_anim)
            
            # Add to eigen_system_data if has eigen values
            if any([eigen_alpha, eigen_beta, eigen_zeta]):
                eigen_system_entry = {
                    'frame': frame_idx,
                    'neuron_id': neuron_id,
                    'coordinate': list(coord_tuple),
                    'pattern': neuron_anim['pattern'],
                    'confidence': neuron_anim['confidence'],
                    'eigen_alpha': eigen_alpha,
                    'eigen_beta': eigen_beta,
                    'eigen_zeta': eigen_zeta,
                    'health_status': neuron_anim['health_status'],
                    'health_score': neuron_anim['health_score'],
                    'timestamp': timestamp
                }
                sequence['eigen_system_data'].append(eigen_system_entry)
            
            # Add to matrix_relationship_data
            matrix_entry = {
                'frame': frame_idx,
                'neuron_id': neuron_id,
                'pattern': neuron_anim['pattern'],
                'confidence': neuron_anim['confidence'],
                'b_vector': neuron_anim['pattern_probabilities'],
                'B_matrix_trace': matrix_relationships.get('B_matrix_trace', 0.0),
                'dot_products': neuron_anim['dot_products'],
                'position_assignment_quality': 0.0
            }
            sequence['matrix_relationship_data'].append(matrix_entry)
            
            # Track neuron in registry
            self._track_neuron_changes(neuron_anim, frame_idx)
        
        # Process axons (heartbeats as axons)
        axons_data = frame_data.get('axons', [])
        for axon in axons_data:
            sequence['axons'].append(axon)
        
        return sequence
    
    def _determine_state_from_eigen(self, alpha: float, beta: float, zeta: float, 
                                   health_status: str) -> str:
        """Determine state from 3 eigen values"""
        # If health_status already provided, use it
        if health_status and health_status != 'UNKNOWN':
            return health_status
        
        # Calculate from 3 eigen values
        eigen_sum = alpha + beta + zeta
        eigen_balance = abs(alpha - beta) + abs(beta - zeta) + abs(zeta - alpha)
        
        # Nexus state determination logic
        if eigen_sum < 0.1:
            return 'DEAD'
        elif eigen_balance < 0.1:
            return 'RIGID'
        elif zeta > 0.7 and alpha > 0.6:
            return 'STABLE'
        elif eigen_sum > 1.0:
            return 'LEARNING'
        elif beta > 0.5 and zeta < 0.3:
            return 'CONFUSED'
        else:
            # Use alpha as overall strength indicator
            if alpha > 0.7:
                return 'STABLE'
            elif alpha > 0.4:
                return 'LEARNING'
            else:
                return 'NOISY'
    
    def _process_matrix_evolution(self, matrix_data: Dict):
        """Process matrix evolution data into registry"""
        neuron_id = matrix_data.get('neuron_id')
        if not neuron_id:
            return
        
        # Initialize neuron in matrix registry
        if neuron_id not in self.matrix_registry:
            self.matrix_registry[neuron_id] = {
                'neuron_id': neuron_id,
                'coordinate': matrix_data.get('coordinate'),
                'pattern_history': [],
                'matrix_history': [],
                'eigen_history': [],
                'statistics': {
                    'total_cycles': 0,
                    'pattern_switches': 0,
                    'matrix_updates': 0,
                    'confidence_history': [],
                    'entropy_history': []
                }
            }
        
        registry = self.matrix_registry[neuron_id]
        
        # Store pattern history
        pattern = matrix_data.get('pattern', 'UNKNOWN')
        registry['pattern_history'].append({
            'cycle': matrix_data.get('cycle', 0),
            'pattern': pattern,
            'timestamp': matrix_data.get('timestamp', time.time())
        })
        
        # Store matrix evolution snapshot
        matrix_snapshot = {
            'cycle': matrix_data.get('cycle', 0),
            'timestamp': matrix_data.get('timestamp', time.time()),
            'pattern': pattern,
            
            # Lightweight matrix aggregates (not full matrices)
            'B_trace': matrix_data.get('B_trace', 0.0),
            'B_det': matrix_data.get('B_det', 0.0),
            'b_entropy': matrix_data.get('b_entropy', 0.0),
            
            # Pattern probability vector
            'b_vector': matrix_data.get('b_vector', [0.2, 0.2, 0.2, 0.2, 0.2]),
            
            # Eigen triplet
            'eigen_triplet': matrix_data.get('eigen_triplet', [0.0, 0.0, 0.0]),
            
            # Assignment quality
            'assignment_quality': matrix_data.get('assignment_quality', 0.0),
            
            # Performance metrics
            'success_rate': matrix_data.get('success_rate', 0.0),
            'void_density': matrix_data.get('void_density', 0.0)
        }
        
        registry['matrix_history'].append(matrix_snapshot)
        
        # Store eigen history
        eigen_triplet = matrix_data.get('eigen_triplet', [0.0, 0.0, 0.0])
        registry['eigen_history'].append({
            'cycle': matrix_data.get('cycle', 0),
            'alpha': eigen_triplet[0],
            'beta': eigen_triplet[1],
            'zeta': eigen_triplet[2]
        })
        
        # Update statistics
        registry['statistics']['total_cycles'] += 1
        registry['statistics']['matrix_updates'] += 1
        
        # Track pattern switches
        if (len(registry['pattern_history']) > 1 and 
            registry['pattern_history'][-2]['pattern'] != pattern):
            registry['statistics']['pattern_switches'] += 1
        
        # Track confidence (from pattern probability)
        b_vector = matrix_data.get('b_vector', [])
        if b_vector:
            confidence = max(b_vector)
            registry['statistics']['confidence_history'].append(confidence)
        
        # Track entropy
        entropy = matrix_data.get('b_entropy', 0.0)
        registry['statistics']['entropy_history'].append(entropy)
    
    def _track_neuron_changes(self, neuron_anim: Dict, frame_idx: int):
        """Track neuron state and pattern changes"""
        neuron_id = neuron_anim['neuron_id']
        
        if neuron_id not in self.neuron_registry:
            self.neuron_registry[neuron_id] = {
                'id': neuron_id,
                'coordinate': neuron_anim['coordinate'],
                'first_seen': frame_idx,
                'last_seen': frame_idx,
                'pattern_history': [],
                'state_history': [],
                'eigen_history': [],
                'confidence_history': [],
                'matrix_available': neuron_id in self.matrix_registry,
                'sample_type': neuron_anim.get('sample_type', 'ANIMATION_SAMPLE')
            }
        
        registry = self.neuron_registry[neuron_id]
        registry['last_seen'] = frame_idx
        
        # Track pattern changes
        current_pattern = neuron_anim['pattern']
        current_confidence = neuron_anim['confidence']
        
        if not registry['pattern_history'] or registry['pattern_history'][-1][1] != current_pattern:
            pattern_event = (frame_idx, current_pattern, current_confidence)
            registry['pattern_history'].append(pattern_event)
        
        # Track state changes
        current_state = neuron_anim['current_state']
        
        if not registry['state_history'] or registry['state_history'][-1][1] != current_state:
            state_event = (frame_idx, current_state, current_confidence)
            registry['state_history'].append(state_event)
        
        # Track confidence
        registry['confidence_history'].append((frame_idx, current_confidence))
    
    def _update_cumulative_stats(self, sequence: Dict):
        """Update cumulative statistics from TimelineBuilder sequence"""
        frame_num = sequence.get('frame', 0)
        
        # Get stats from TimelineBuilder format
        system_stats = sequence.get('system_stats', {})
        
        # Update cumulative totals
        self.cumulative_stats['total_frames'] = max(self.cumulative_stats['total_frames'], frame_num + 1)
        self.cumulative_stats['total_neurons'] = system_stats.get('total_neurons', 0)
        self.cumulative_stats['total_axons'] = system_stats.get('total_axons', 0)
        self.cumulative_stats['eigen_active_neurons'] = system_stats.get('eigen_active_neurons', 0)
        
        # Track average eigen values
        eigen_data = sequence.get('eigen_system_data', [])
        if eigen_data:
            alphas = [n.get('eigen_alpha', 0) for n in eigen_data]
            betas = [n.get('eigen_beta', 0) for n in eigen_data]
            zetas = [n.get('eigen_zeta', 0) for n in eigen_data]
            
            if 'avg_eigen_alpha' not in self.cumulative_stats:
                self.cumulative_stats['avg_eigen_alpha'] = []
                self.cumulative_stats['avg_eigen_beta'] = []
                self.cumulative_stats['avg_eigen_zeta'] = []
            
            self.cumulative_stats['avg_eigen_alpha'].append(np.mean(alphas) if alphas else 0)
            self.cumulative_stats['avg_eigen_beta'].append(np.mean(betas) if betas else 0)
            self.cumulative_stats['avg_eigen_zeta'].append(np.mean(zetas) if zetas else 0)
            
            # Keep last 100 samples
            max_history = 100
            for key in ['avg_eigen_alpha', 'avg_eigen_beta', 'avg_eigen_zeta']:
                if len(self.cumulative_stats[key]) > max_history:
                    self.cumulative_stats[key] = self.cumulative_stats[key][-max_history:]
        
        # Store frame history
        frame_data = {
            'frame': frame_num,
            'neurons': system_stats.get('total_neurons', 0),
            'eigen_neurons': system_stats.get('eigen_active_neurons', 0),
            'axons': system_stats.get('total_axons', 0)
        }
        
        if 'frame_history' not in self.cumulative_stats:
            self.cumulative_stats['frame_history'] = deque(maxlen=100)
        self.cumulative_stats['frame_history'].append(frame_data)
        
    def process_new_frames(self) -> int:
        """Scan for and process any new frames added since initialization"""
        current_frame_count = len(self.animation_sequences)
        current_file_count = len(self.frame_files)
        
        # Rescan for new frame files
        old_frame_files = set(self.frame_files)
        self._scan_frame_files()
        new_frame_files = [f for f in self.frame_files if f not in old_frame_files]
        
        if not new_frame_files:
            return 0
        
        print(f"🔄 Found {len(new_frame_files)} new frame files")
        
        # Process only the new files
        current_frame_idx = len(self.animation_sequences)
        new_sequences_added = 0
        
        for frame_file in new_frame_files:
            try:
                with open(frame_file, 'r') as f:
                    frame_content = json.load(f)
                
                # Handle Nexus chunk format
                if isinstance(frame_content, list):
                    for frame_data in frame_content:
                        sequence = self._build_animation_sequence(frame_data, current_frame_idx)
                        if sequence:
                            self.animation_sequences.append(sequence)
                            current_frame_idx += 1
                            new_sequences_added += 1
                else:
                    sequence = self._build_animation_sequence(frame_content, current_frame_idx)
                    if sequence:
                        self.animation_sequences.append(sequence)
                        current_frame_idx += 1
                        new_sequences_added += 1
                        
            except Exception as e:
                print(f"⚠️ Error processing new frame file {frame_file}: {e}")
        
        # Also check for new matrix files
        self._scan_matrix_files()
        
        # Update statistics with new data
        if new_sequences_added > 0:
            self._build_cumulative_statistics()
            print(f"📥 Added {new_sequences_added} new animation sequences")
            print(f"📊 Total sequences: {len(self.animation_sequences)}")
        
        return new_sequences_added
    
    def get_frames(self):
        """Get all animation sequences"""
        return self.animation_sequences
    
    def get_neuron_history(self, neuron_id: str) -> Dict:
        """Get complete history for a neuron"""
        neuron_data = self.neuron_registry.get(neuron_id, {})
        matrix_data = self.matrix_registry.get(neuron_id, {})
        
        return {
            'neuron_info': neuron_data,
            'matrix_history': matrix_data.get('matrix_history', []),
            'eigen_history': matrix_data.get('eigen_history', []),
            'statistics': matrix_data.get('statistics', {})
        }
    
    def get_matrix_evolution_data(self, neuron_id: str, data_type: str = 'all') -> List:
        """Get matrix evolution data for visualization"""
        if neuron_id not in self.matrix_registry:
            return []
        
        history = self.matrix_registry[neuron_id]['matrix_history']
        
        if data_type == 'B_trace':
            return [{'cycle': h['cycle'], 'value': h.get('B_trace', 0.0)} 
                    for h in history]
        elif data_type == 'b_entropy':
            return [{'cycle': h['cycle'], 'value': h.get('b_entropy', 0.0)} 
                    for h in history]
        elif data_type == 'eigen_alpha':
            eigen_history = self.matrix_registry[neuron_id].get('eigen_history', [])
            return [{'cycle': h['cycle'], 'value': h.get('alpha', 0.0)} 
                    for h in eigen_history]
        else:
            # Return all available data
            return history

# ===== ENHANCED SESSION BROWSER =====
class SessionBrowser:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.sessions = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_items = 8
    
    def handle_keydown(self, key):
        """Handle keyboard events for browser navigation - accepts integer key code"""
        if key == pygame.K_UP:
            if self.selected_index > 0:
                self.selected_index -= 1
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                return True
        
        elif key == pygame.K_DOWN:
            if self.selected_index < len(self.sessions) - 1:
                self.selected_index += 1
                if self.selected_index >= self.scroll_offset + self.visible_items:
                    self.scroll_offset += 1
                return True
        
        elif key == pygame.K_PAGEUP:
            if self.selected_index > 0:
                self.selected_index = max(0, self.selected_index - self.visible_items)
                self.scroll_offset = max(0, self.scroll_offset - self.visible_items)
                return True
        
        elif key == pygame.K_PAGEDOWN:
            if self.sessions:
                self.selected_index = min(len(self.sessions) - 1, 
                                        self.selected_index + self.visible_items)
                if self.selected_index >= self.scroll_offset + self.visible_items:
                    self.scroll_offset = min(len(self.sessions) - self.visible_items,
                                           self.scroll_offset + self.visible_items)
                return True
        
        elif key == pygame.K_HOME:
            if self.sessions:
                self.selected_index = 0
                self.scroll_offset = 0
                return True
        
        elif key == pygame.K_END:
            if self.sessions:
                self.selected_index = len(self.sessions) - 1
                self.scroll_offset = max(0, len(self.sessions) - self.visible_items)
                return True
        
        return False

    def scan_sessions(self):
        """Scan for nexus sessions with flexible detection - LOOKS FOR nexus* folders"""
        self.sessions = []
        if not os.path.exists(self.base_dir):
            print("⚠️ Cognition directory not found")
            return
            
        print(f"📁 Scanning {self.base_dir} for nexus* sessions...")
        
        session_count = 0
        # Look for nexus* folders
        for folder in os.listdir(self.base_dir):
            if not folder.startswith('nexus_'):
                continue
                
            path = os.path.join(self.base_dir, folder)
            if not os.path.isdir(path):
                continue
            
            # Check for session structure
            frames_dir = os.path.join(path, "frames")
            timeline_file = os.path.join(path, "timeline.json")
            matrix_dir = os.path.join(path, "matrix_samples")
            
            has_frames = os.path.exists(frames_dir) and os.path.isdir(frames_dir)
            has_timeline = os.path.exists(timeline_file)
            has_matrix = os.path.exists(matrix_dir) and os.path.isdir(matrix_dir)
            
            # Skip if no data at all
            if not (has_frames or has_timeline):
                continue
            
            # Determine session status
            if has_timeline:
                session_status = "COMPLETE"
                # Check if frames folder is empty and can be deleted
                if has_frames:
                    frame_files = [f for f in os.listdir(frames_dir) 
                                if f.startswith('frames_') and f.endswith('.json')]
                    if len(frame_files) == 0:
                        session_status = "CLEANUP_READY"
            elif has_frames:
                # Check if frames folder has content
                frame_files = [f for f in os.listdir(frames_dir) 
                            if f.startswith('frames_') and f.endswith('.json')]
                if len(frame_files) > 0:
                    session_status = f"ACTIVE ({len(frame_files)} chunks)"
                else:
                    session_status = "EMPTY"
            else:
                session_status = "UNKNOWN"
            
            # Get basic session info
            neuron_count = 0
            frame_count = 0
            first_frame = 0
            last_frame = 0
            last_modified = 0
            
            # Get info from timeline if exists
            if has_timeline:
                try:
                    with open(timeline_file, 'r') as f:
                        timeline_data = json.load(f)
                    if isinstance(timeline_data, list):
                        frame_count = len(timeline_data)
                        if frame_count > 0:
                            first_frame = timeline_data[0].get('frame', 0)
                            last_frame = timeline_data[-1].get('frame', 0)
                            
                            # Estimate neuron count from first frame
                            if len(timeline_data) > 0:
                                frame_data = timeline_data[0]
                                neurons_data = frame_data.get('data', {}).get('neurons', {})
                                neuron_count = len(neurons_data) if isinstance(neurons_data, dict) else 0
                    
                    last_modified = os.path.getmtime(timeline_file)
                except Exception as e:
                    print(f"  ⚠️ Error reading timeline for {folder}: {e}")
            
            # If no timeline, check frames for info
            elif has_frames:
                try:
                    # Get info from first chunk file
                    frame_files = sorted([f for f in os.listdir(frames_dir) 
                                        if f.startswith('frames_') and f.endswith('.json')])
                    
                    if frame_files:
                        first_chunk = os.path.join(frames_dir, frame_files[0])
                        with open(first_chunk, 'r') as f:
                            chunk_data = json.load(f)
                        
                        if isinstance(chunk_data, list) and len(chunk_data) > 0:
                            first_frame_data = chunk_data[0]
                            neurons_data = first_frame_data.get('data', {}).get('neurons', {})
                            neuron_count = len(neurons_data) if isinstance(neurons_data, dict) else 0
                            frame_count = len(chunk_data)
                            first_frame = first_frame_data.get('frame', 0)
                        
                        # Get modification time from newest frame file
                        if frame_files:
                            newest_file = os.path.join(frames_dir, frame_files[-1])
                            last_modified = os.path.getmtime(newest_file)
                        else:
                            last_modified = os.path.getmtime(frames_dir)
                except Exception as e:
                    print(f"  ⚠️ Error reading frames for {folder}: {e}")
                    last_modified = os.path.getmtime(path)
            
            # Format time string
            if last_modified > 0:
                time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(last_modified))
            else:
                time_str = "Unknown"
            
            session_info = {
                'id': folder,
                'path': path,
                'frames_dir': frames_dir if has_frames else None,
                'timeline_file': timeline_file if has_timeline else None,
                'matrix_dir': matrix_dir if has_matrix else None,
                'has_frames': has_frames,
                'has_timeline': has_timeline,
                'has_matrix': has_matrix,
                'status': session_status,
                'neuron_count': neuron_count,
                'frame_count': frame_count,
                'first_frame': first_frame,
                'last_frame': last_frame,
                'last_modified': last_modified,
                'time_str': time_str,
                'size_bytes': self._get_session_size(path),
                'needs_cleanup': (has_frames and has_timeline and 
                                os.path.exists(frames_dir) and 
                                len(os.listdir(frames_dir)) == 0)
            }
            
            self.sessions.append(session_info)
            session_count += 1
            
            print(f"  ✓ Found {session_status} session: {folder}")
            print(f"     - Timeline: {has_timeline}, Frames: {has_frames}")
            print(f"     - Neurons: {neuron_count}, Frames: {frame_count}")
            print(f"     - Last modified: {time_str}")
            print()
        
        # Sort by modification time (newest first)
        self.sessions.sort(key=lambda x: x['last_modified'], reverse=True)
        
        print(f"📁 Found {session_count} nexus sessions")
        
        # Print summary
        for i, session in enumerate(self.sessions):
            print(f"  {i}: {session['id']} - {session['status']} ({session['frame_count']} frames)")
        
        return session_count
        
    def _get_session_size(self, path):
        """Calculate total size of session directory in MB"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.isfile(filepath):
                        total_size += os.path.getsize(filepath)
        except:
            pass
        return total_size / (1024 * 1024)  # Convert to MB
    
    def get_selected_session(self):
        """Get currently selected session"""
        if 0 <= self.selected_index < len(self.sessions):
            return self.sessions[self.selected_index]
        return None
    
    def cleanup_empty_frames_folder(self, session_info):
        """Clean up empty frames folder after timeline completion"""
        if not session_info or not session_info.get('needs_cleanup', False):
            return False
        
        frames_dir = session_info.get('frames_dir')
        if not frames_dir or not os.path.exists(frames_dir):
            return False
        
        try:
            # Double-check folder is empty
            contents = os.listdir(frames_dir)
            if len(contents) == 0:
                os.rmdir(frames_dir)
                print(f"🧹 Cleaned up empty frames folder: {frames_dir}")
                return True
            else:
                print(f"⚠️ Frames folder not empty ({len(contents)} items), skipping cleanup")
                return False
        except Exception as e:
            print(f"⚠️ Error cleaning up frames folder: {e}")
            return False
    
# "===== ANIMATION PLAN STRUCTURES =====
@dataclass
class AnimationPlan:
    """Animation plan from Nexus axon and state data"""
    frame_number: int
    timestamp: float
    axon_animations: List[Dict] = field(default_factory=list)
    state_animations: List[Dict] = field(default_factory=list)
    particle_animations: List[Dict] = field(default_factory=list)

#===== Animation Parcer and Processor 
class TimelineBuilder:
    """Builds coordinated animation sequences from new 3 eigen system exports"""
    
    def __init__(self, session_dir: str):
        print(f"📅 TIMELINE BUILDER - Loading session: {session_dir}")
        self.session_dir = session_dir
        
        # Look for frames in both possible locations
        self.frames_dir = os.path.join(session_dir, "frames")
        self.matrix_dir = None
        
        # Try multiple possible matrix directory names
        possible_matrix_dirs = [
            os.path.join(session_dir, "matrix_evolution"),
            os.path.join(session_dir, "matrix"),
            os.path.join(session_dir, "87d_matrix_samples")
        ]
        
        for dir_path in possible_matrix_dirs:
            if os.path.exists(dir_path):
                self.matrix_dir = dir_path
                print(f"📊 Found matrix directory: {dir_path}")
                break
        
        if not self.matrix_dir:
            print(f"⚠️ No matrix directory found, tried: {possible_matrix_dirs}")
            self.matrix_dir = os.path.join(session_dir, "matrix_evolution")
            os.makedirs(self.matrix_dir, exist_ok=True)
        
        # Core tracking structures
        self.neuron_registry = {}
        self.matrix_registry = {}
        self.animation_sequences = []
        self.frame_files = []
        self.matrix_files = []
        
        # Scan for files
        self._scan_frame_files()
        self._scan_matrix_files()
        
        # Process data
        if self.frame_files or self.matrix_files:
            self._process_all_data()
            print(f"✅ Built {len(self.animation_sequences)} animation sequences")
            print(f"📊 Loaded {len(self.matrix_registry)} neuron matrix histories")
        else:
            print(f"⚠️ No animation or matrix files found")
            print(f"   Frames directory: {self.frames_dir}")
            print(f"   Matrix directory: {self.matrix_dir}")
    
    def _convert_axon_to_animation(self, axon_data: Dict, frame_idx: int, session_time: float) -> Dict:
            """Convert axon data to animation format"""
            axon_type = axon_data.get('axon_type', 'UNKNOWN')
            source = axon_data.get('source', {})
            target = axon_data.get('target', {})
            
            # Extract coordinates
            source_coord = source.get('coordinate')
            target_coord = target.get('coordinate')
            
            # Convert to tuples if they are lists
            if isinstance(source_coord, list):
                source_coord = tuple(source_coord)
            if isinstance(target_coord, list):
                target_coord = tuple(target_coord)
            
            axon_anim = {
                'axon_type': axon_type,
                'source_coord': source_coord,
                'target_coord': target_coord,
                'confidence': axon_data.get('data', {}).get('confidence', 0.5),
                'frame': frame_idx,
                'session_time': session_time,
                'timestamp': time.time(),
                'source_info': source,
                'target_info': target,
                'axon_data': axon_data.get('data', {})
            }
            
            # Map axon types to visualizer categories
            if 'HEARTBEAT' in axon_type:
                axon_anim['category'] = 'HEARTBEAT'
            elif 'VOID' in axon_type:
                axon_anim['category'] = 'COORDINATE_VOID'
            elif 'NEIGHBOR' in axon_type:
                axon_anim['category'] = 'NEIGHBOR_DETECTED'
            elif 'HASH' in axon_type or 'EXTRACTED' in axon_type:
                axon_anim['category'] = 'HASH_EXTRACTED'
            elif 'GROWTH' in axon_type:
                axon_anim['category'] = 'NEURON_GROWTH_SIGNAL'
            else:
                axon_anim['category'] = 'UNKNOWN'
            
            return axon_anim

    def _scan_frame_files(self):
        """Scan for animation frame files - FLEXIBLE SCANNING"""
        if not os.path.exists(self.frames_dir):
            print(f"⚠️ Frames directory not found: {self.frames_dir}")
            return
        
        # Look for multiple possible file patterns
        file_patterns = [
            'animation_*.json',    # TimelineBuilder format
            'frames_*.json',       # Nexus format
            'heartbeat_*.json',    # Alternative Nexus format
            'frame_*.json'         # Generic format
        ]
        
        self.frame_files = []
        for pattern in file_patterns:
            import glob
            files = glob.glob(os.path.join(self.frames_dir, pattern))
            self.frame_files.extend(files)
        
        # Remove duplicates and sort
        self.frame_files = sorted(list(set(self.frame_files)))
        print(f"📁 Found {len(self.frame_files)} animation frame files")
    
    def _scan_matrix_files(self):
        """Scan for matrix evolution files - FLEXIBLE SCANNING"""
        if not os.path.exists(self.matrix_dir):
            print(f"⚠️ Matrix directory not found: {self.matrix_dir}")
            return
        
        # Look for multiple possible file patterns
        file_patterns = [
            'matrix_*.json',           # TimelineBuilder format
            'matrix_evolution_*.json', # Alternative format
            '87d_matrix_*.json',       # 87D format
            'neuron_matrix_*.json'     # Nexus format
        ]
        
        self.matrix_files = []
        for pattern in file_patterns:
            import glob
            files = glob.glob(os.path.join(self.matrix_dir, pattern))
            self.matrix_files.extend(files)
        
        # Remove duplicates and sort
        self.matrix_files = sorted(list(set(self.matrix_files)))
        print(f"📊 Found {len(self.matrix_files)} matrix evolution files")
    
    def _process_all_data(self):
        """Process all animation and matrix data - HANDLE NEXUS FORMAT"""
        current_frame_idx = 0
        
        # Process animation frames
        for frame_file in self.frame_files:
            try:
                with open(frame_file, 'r') as f:
                    frame_content = json.load(f)
                
                # Handle different file formats
                if isinstance(frame_content, list):
                    # File contains list of frames
                    for frame_data in frame_content:
                        sequence = self._build_animation_sequence(frame_data, current_frame_idx)
                        if sequence:
                            self.animation_sequences.append(sequence)
                            current_frame_idx += 1
                else:
                    # File contains single frame
                    sequence = self._build_animation_sequence(frame_content, current_frame_idx)
                    if sequence:
                        self.animation_sequences.append(sequence)
                        current_frame_idx += 1
                        
            except Exception as e:
                print(f"⚠️ Error processing frame file {frame_file}: {e}")
        
        # Process matrix evolution files
        for matrix_file in self.matrix_files:
            try:
                with open(matrix_file, 'r') as f:
                    matrix_content = json.load(f)
                
                # Handle different formats
                if isinstance(matrix_content, list):
                    # List of matrix entries
                    for matrix_data in matrix_content:
                        self._process_matrix_evolution(matrix_data)
                else:
                    # Single matrix entry
                    self._process_matrix_evolution(matrix_content)
                        
            except Exception as e:
                print(f"⚠️ Error processing matrix file {matrix_file}: {e}")
        
        # Build statistics
        if self.animation_sequences or self.matrix_registry:
            self._build_cumulative_statistics()
        
        print(f"📊 Built neuron registry with {len(self.neuron_registry)} neurons")
        print(f"📈 Matrix evolution data for {len(self.matrix_registry)} neurons")

    def _build_animation_sequence(self, frame_data: Dict, frame_idx: int) -> Dict:
        """Convert NEW export format to animation sequence"""
        # Extract basic frame info
        session_time = frame_data.get('session_time', 0)
        timestamp = frame_data.get('timestamp', time.time())
        
        sequence = {
            'frame': frame_idx,
            'session_time': session_time,
            'timestamp': timestamp,
            'neuron_animations': [],
            'axon_animations': [],
            'particle_animations': [],
            'state_change_animations': [],
            'pattern_change_animations': [],
            'eigen_system_data': [],
            'matrix_relationship_data': []  # NEW: For graphing
        }
        
        # Process neuron data from NEW export
        neurons_data = frame_data.get('neurons', [])
        if isinstance(neurons_data, dict):
            neurons_data = list(neurons_data.values())
        
        for neuron_data in neurons_data:
            # Convert coordinate
            coord = neuron_data.get('coordinate', [0, 0])
            coord_tuple = tuple(coord) if isinstance(coord, list) else coord
            
            # Extract NEW 3 eigen system
            eigen_alpha = neuron_data.get('eigen_alpha', 0.0)
            eigen_beta = neuron_data.get('eigen_beta', 0.0)
            eigen_zeta = neuron_data.get('eigen_zeta', 0.0)
            
            # Get matrix relationships
            matrix_relationships = neuron_data.get('matrix_relationships', {})
            health_status = matrix_relationships.get('health_status', 'UNKNOWN')
            health_score = matrix_relationships.get('health_score', 0.5)
            
            # Get position assignments
            position_assignments = neuron_data.get('position_assignments', {})
            
            # Determine current state from NEW 3 eigen system
            current_state = self._determine_state_from_new_eigen(
                eigen_alpha, eigen_beta, eigen_zeta, health_status
            )
            
            # Extract pattern and confidence
            pattern = neuron_data.get('pattern', 'UNKNOWN')
            confidence = neuron_data.get('confidence', 0.5)
            
            # Create neuron animation data
            neuron_anim = {
                'neuron_id': neuron_data.get('neuron_id', f'neuron_{frame_idx}'),
                'coordinate': coord_tuple,
                'pattern': pattern,
                'current_state': current_state,
                'confidence': confidence,
                'processing_phase': neuron_data.get('processing_phase', 'UNKNOWN'),
                'frame': frame_idx,
                'session_time': session_time,
                'timestamp': timestamp,
                
                # NEW: 3 eigen values
                'eigenvalues': [eigen_alpha, eigen_beta, eigen_zeta],
                'eigen_alpha': eigen_alpha,
                'eigen_beta': eigen_beta,
                'eigen_zeta': eigen_zeta,
                'primary_strength': max(eigen_alpha, eigen_beta, eigen_zeta),
                
                # NEW: Matrix relationships
                'matrix_relationships': matrix_relationships,
                'health_status': health_status,
                'health_score': health_score,
                'position_assignments': position_assignments,
                
                # Pattern probabilities from b_vector
                'pattern_probabilities': matrix_relationships.get('b_vector', [0.2, 0.2, 0.2, 0.2, 0.2]),
                'dominant_pattern': matrix_relationships.get('dominant_pattern', 'UNKNOWN'),
                'dominant_probability': matrix_relationships.get('dominant_probability', 0.2),
                
                # Dot products for neighbor connections
                'dot_products': matrix_relationships.get('dot_products', {}),
                
                # Void and growth
                'void_coordinates': neuron_data.get('void_coordinates', []),
                'has_growth_signals': neuron_data.get('has_growth_signals', False),
                
                # Timing
                'cycle': neuron_data.get('cycle', 0),
                'recycling_iteration': neuron_data.get('recycling_iteration', 0),
                
                # For hover info
                'neighbor_system': {
                    'connected_neighbors': len(position_assignments),
                    'successful_matches': sum(1 for pos, row in position_assignments.items() if row >= 0),
                    'health': health_status
                }
            }
            
            # Add to sequence
            sequence['neuron_animations'].append(neuron_anim)
            
            # Track eigen system data separately
            if any([eigen_alpha, eigen_beta, eigen_zeta]):
                eigen_system_entry = {
                    'frame': frame_idx,
                    'neuron_id': neuron_anim['neuron_id'],
                    'coordinate': coord_tuple,
                    'pattern': pattern,
                    'confidence': confidence,
                    'eigen_alpha': eigen_alpha,
                    'eigen_beta': eigen_beta,
                    'eigen_zeta': eigen_zeta,
                    'health_status': health_status,
                    'health_score': health_score,
                    'timestamp': timestamp
                }
                sequence['eigen_system_data'].append(eigen_system_entry)
            
            # Track matrix relationship data for advanced graphs
            matrix_entry = {
                'frame': frame_idx,
                'neuron_id': neuron_anim['neuron_id'],
                'pattern': pattern,
                'confidence': confidence,
                'b_vector': matrix_relationships.get('b_vector', []),
                'B_matrix_trace': matrix_relationships.get('B_matrix_trace', 0.0),
                'dot_products': matrix_relationships.get('dot_products', {}),
                'position_assignment_quality': len(position_assignments) / 5.0 if position_assignments else 0.0
            }
            sequence['matrix_relationship_data'].append(matrix_entry)
            
            # Track neuron in registry
            self._track_neuron_changes(neuron_anim, frame_idx)
        
        # Process axons (unchanged for now)
        axons_data = frame_data.get('axons', [])
        for axon in axons_data:
            axon_anim = self._convert_axon_to_animation(axon, frame_idx, session_time)
            if axon_anim:
                sequence['axon_animations'].append(axon_anim)
        
        # Add system stats
        sequence['system_stats'] = {
            'total_neurons': len(sequence['neuron_animations']),
            'total_axons': len(sequence['axon_animations']),
            'eigen_active_neurons': len([n for n in sequence['neuron_animations'] 
                                        if any([n['eigen_alpha'], n['eigen_beta'], n['eigen_zeta']])]),
            'matrix_active_neurons': len([n for n in sequence['neuron_animations'] 
                                         if n.get('matrix_relationships')]),
            'avg_confidence': np.mean([n['confidence'] for n in sequence['neuron_animations']]) 
                            if sequence['neuron_animations'] else 0.0
        }
        
        return sequence
    
    def _determine_state_from_new_eigen(self, alpha: float, beta: float, zeta: float, 
                                       health_status: str) -> str:
        """Determine state from 3 eigen values"""
        # If health_status already provided, use it
        if health_status and health_status != 'UNKNOWN':
            return health_status
        
        # Calculate from 3 eigen values
        eigen_sum = alpha + beta + zeta
        eigen_balance = abs(alpha - beta) + abs(beta - zeta) + abs(zeta - alpha)
        
        # Your exact logic
        if eigen_sum < 0.1:
            return 'DEAD'
        elif eigen_balance < 0.1:
            return 'RIGID'
        elif zeta > 0.7 and alpha > 0.6:
            return 'STABLE'
        elif eigen_sum > 1.0:
            return 'LEARNING'
        elif beta > 0.5 and zeta < 0.3:
            return 'CONFUSED'
        else:
            # Use alpha as overall strength indicator
            if alpha > 0.7:
                return 'STABLE'
            elif alpha > 0.4:
                return 'LEARNING'
            else:
                return 'NOISY'
    
    def _process_matrix_evolution(self, matrix_data: Dict):
        """Process matrix evolution data into registry"""
        neuron_id = matrix_data.get('neuron_id')
        if not neuron_id:
            return
        
        # Initialize neuron in matrix registry
        if neuron_id not in self.matrix_registry:
            self.matrix_registry[neuron_id] = {
                'neuron_id': neuron_id,
                'coordinate': matrix_data.get('coordinate'),
                'pattern_history': [],
                'matrix_history': [],
                'eigen_history': [],
                'statistics': {
                    'total_cycles': 0,
                    'pattern_switches': 0,
                    'matrix_updates': 0,
                    'confidence_history': [],
                    'entropy_history': []
                }
            }
        
        registry = self.matrix_registry[neuron_id]
        
        # Store pattern history
        pattern_history = matrix_data.get('pattern_history', [])
        if pattern_history:
            registry['pattern_history'].extend(pattern_history)
        
        # Store matrix evolution snapshot
        matrix_snapshot = {
            'cycle': matrix_data.get('cycle', 0),
            'timestamp': matrix_data.get('timestamp', time.time()),
            'pattern': matrix_data.get('pattern', 'UNKNOWN'),
            
            # Eigen system
            'eigen_system': matrix_data.get('eigen_system', {}),
            
            # Position bias matrix
            'position_bias_matrix': matrix_data.get('position_bias_matrix', {}),
            
            # Pattern bias vector
            'pattern_bias_vector': matrix_data.get('pattern_bias_vector', {}),
            
            # Relational encoding
            'relational_encoding': matrix_data.get('relational_encoding', {}),
            
            # Assignment quality
            'assignment_quality': matrix_data.get('assignment_quality', {}),
            
            # Recycling state
            'recycling_state': matrix_data.get('recycling_state', {}),
            
            # Performance metrics
            'performance_metrics': matrix_data.get('performance_metrics', {})
        }
        
        registry['matrix_history'].append(matrix_snapshot)
        
        # Store eigen history separately
        eigen_system = matrix_data.get('eigen_system', {})
        if eigen_system:
            registry['eigen_history'].append({
                'cycle': matrix_data.get('cycle', 0),
                'alpha': eigen_system.get('alpha', 0.0),
                'beta': eigen_system.get('beta', 0.0),
                'zeta': eigen_system.get('zeta', 0.0),
                'tensor_G_trace': eigen_system.get('tensor_G_trace', 0.0)
            })
        
        # Update statistics
        registry['statistics']['total_cycles'] += 1
        registry['statistics']['matrix_updates'] += 1
        
        # Track pattern switches
        if (len(registry['matrix_history']) > 1 and 
            registry['matrix_history'][-2]['pattern'] != matrix_snapshot['pattern']):
            registry['statistics']['pattern_switches'] += 1
        
        # Track confidence
        pattern_bias = matrix_data.get('pattern_bias_vector', {})
        confidence = pattern_bias.get('dominant_probability', 0.0)
        registry['statistics']['confidence_history'].append(confidence)
        
        # Track entropy
        entropy = pattern_bias.get('entropy', 0.0)
        registry['statistics']['entropy_history'].append(entropy)
    
    def _track_neuron_changes(self, neuron_anim: Dict, frame_idx: int):
        """Track neuron state and pattern changes"""
        neuron_id = neuron_anim['neuron_id']
        
        if neuron_id not in self.neuron_registry:
            self.neuron_registry[neuron_id] = {
                'id': neuron_id,
                'coordinate': neuron_anim['coordinate'],
                'first_seen': frame_idx,
                'last_seen': frame_idx,
                'pattern_history': [],
                'state_history': [],
                'eigen_history': [],
                'confidence_history': [],
                'axon_counts': defaultdict(int),
                'matrix_available': neuron_id in self.matrix_registry
            }
        
        registry = self.neuron_registry[neuron_id]
        registry['last_seen'] = frame_idx
        
        # Track pattern changes
        current_pattern = neuron_anim['pattern']
        current_confidence = neuron_anim['confidence']
        
        if not registry['pattern_history'] or registry['pattern_history'][-1][1] != current_pattern:
            pattern_event = (frame_idx, current_pattern, current_confidence)
            registry['pattern_history'].append(pattern_event)
        
        # Track state changes
        current_state = neuron_anim['current_state']
        eigenvalues = neuron_anim['eigenvalues']
        
        if not registry['state_history'] or registry['state_history'][-1][1] != current_state:
            state_event = (frame_idx, current_state, current_confidence, eigenvalues)
            registry['state_history'].append(state_event)
        
        # Track eigen history
        eigen_entry = (frame_idx, eigenvalues[0], eigenvalues[1], eigenvalues[2])
        registry['eigen_history'].append(eigen_entry)
        
        # Track confidence
        registry['confidence_history'].append((frame_idx, current_confidence))
    
    def _build_cumulative_statistics(self):
        """Build comprehensive statistics from both data sources"""
        print("📊 Building cumulative statistics from new export format...")
        
        # Calculate additional metrics for each neuron
        for neuron_id, registry in self.neuron_registry.items():
            # Calculate average confidence
            confidences = [ch[1] for ch in registry['confidence_history']]
            registry['avg_confidence'] = np.mean(confidences) if confidences else 0
            
            # Calculate state stability
            state_changes = len(registry['state_history'])
            lifetime = registry['last_seen'] - registry['first_seen'] + 1
            registry['state_stability'] = 1.0 - (state_changes / max(lifetime, 1))
            
            # Calculate pattern stability
            pattern_changes = len(registry['pattern_history'])
            registry['pattern_stability'] = 1.0 - (pattern_changes / max(lifetime, 1))
            
            # If matrix data available, enrich registry
            if neuron_id in self.matrix_registry:
                matrix_data = self.matrix_registry[neuron_id]
                registry['matrix_data'] = {
                    'total_cycles': matrix_data['statistics']['total_cycles'],
                    'pattern_switches': matrix_data['statistics']['pattern_switches'],
                    'avg_confidence': np.mean(matrix_data['statistics']['confidence_history']) 
                                    if matrix_data['statistics']['confidence_history'] else 0,
                    'avg_entropy': np.mean(matrix_data['statistics']['entropy_history']) 
                                 if matrix_data['statistics']['entropy_history'] else 0,
                    'eigen_history_length': len(matrix_data['eigen_history'])
                }
        
        # Build cross-neuron statistics
        self.cross_neuron_stats = {
            'total_neurons': len(self.neuron_registry),
            'neurons_with_matrix': len(self.matrix_registry),
            'avg_state_stability': np.mean([r.get('state_stability', 0) 
                                           for r in self.neuron_registry.values()]),
            'avg_pattern_stability': np.mean([r.get('pattern_stability', 0) 
                                            for r in self.neuron_registry.values()]),
            'eigen_active_neurons': sum(1 for r in self.neuron_registry.values() 
                                       if len(r.get('eigen_history', [])) > 0)
        }
        
        print(f"📈 Cross-neuron stats: {self.cross_neuron_stats}")

    def process_new_frames(self) -> int:
            """Scan for and process any new animation frames that have been added
            since initialization. Returns number of new frames processed."""
            # Store current count for comparison
            current_frame_count = len(self.animation_sequences)
            current_file_count = len(self.frame_files)
            
            # Rescan for new frame files
            old_frame_files = set(self.frame_files)
            self._scan_frame_files()
            new_frame_files = [f for f in self.frame_files if f not in old_frame_files]
            
            if not new_frame_files:
                return 0
            
            print(f"🔄 Found {len(new_frame_files)} new frame files")
            
            # Process only the new files
            current_frame_idx = len(self.animation_sequences)
            new_sequences_added = 0
            
            for frame_file in new_frame_files:
                try:
                    with open(frame_file, 'r') as f:
                        frame_content = json.load(f)
                    
                    # Handle different file formats
                    if isinstance(frame_content, list):
                        # File contains list of frames
                        for frame_data in frame_content:
                            sequence = self._build_animation_sequence(frame_data, current_frame_idx)
                            if sequence:
                                self.animation_sequences.append(sequence)
                                current_frame_idx += 1
                                new_sequences_added += 1
                    else:
                        # File contains single frame
                        sequence = self._build_animation_sequence(frame_content, current_frame_idx)
                        if sequence:
                            self.animation_sequences.append(sequence)
                            current_frame_idx += 1
                            new_sequences_added += 1
                            
                except Exception as e:
                    print(f"⚠️ Error processing new frame file {frame_file}: {e}")
            
            # Also check for new matrix files
            self._scan_matrix_files()
            
            # Update statistics with new data
            if new_sequences_added > 0:
                self._build_cumulative_statistics()
                print(f"📥 Added {new_sequences_added} new animation sequences")
                print(f"📊 Total sequences: {len(self.animation_sequences)}")
            
            return new_sequences_added
        
    def get_frames(self):
        """Get all animation sequences - used by NexusVisualizer"""
        return self.animation_sequences

# ===== UPDATED NEXUS VISUALIZER =====

class NexusVisualizer:
    """Main visualizer - uses coordinated animation sequences with 3 eigen system"""
    
    MODE_LIVE = "live"
    MODE_REPLAY = "replay"
    MODE_BROWSER = "browser"
    MODE_LOADING = "loading"
    
    # ===== ENHANCED COLOR SYSTEM FOR 3 EIGEN =====
    PATTERN_COLORS = {
        'DATA_INPUT': (100, 200, 255),      # Blue - data patterns
        'ACTION_ELEMENT': (255, 100, 100),  # Red - action patterns
        'CONTEXT_ELEMENT': (100, 255, 100), # Green - context patterns
        'STRUCTURAL': (255, 255, 100),      # Yellow - structural patterns
        'UNKNOWN': (150, 150, 150),         # Gray - unknown patterns
        'NEXUS': (255, 200, 100),           # Orange - nexus control
    }
    
    # EIGEN STATE COLORS (based on 3 eigen system)
    EIGEN_STATE_COLORS = {
        'STABLE': (100, 255, 100),      # Green - high eigen values, balanced
        'LEARNING': (100, 200, 255),    # Blue - high alpha/beta, learning
        'NOISY': (255, 255, 100),       # Yellow - unstable eigen values
        'RIGID': (255, 100, 100),       # Red - over-constrained, low eigen
        'CONFUSED': (255, 100, 255),    # Purple - conflicting eigen values
        'DEAD': (100, 100, 100),        # Dark gray - near-zero eigen values
        'UNKNOWN': (200, 200, 200),     # Light gray - no eigen data
    }
    
    # EIGEN VALUE COLORS (for α, β, ζ visualization)
    EIGEN_VALUE_COLORS = {
        'alpha': (100, 255, 100),    # Green - α (self covariance)
        'beta': (100, 200, 255),     # Blue - β (position covariance)
        'zeta': (255, 100, 255),     # Purple - ζ (tensor covariance)
    }
    
    # AXON COLORS FOR NEW EXPORT STRUCTURE
    AXON_COLORS = {
        # Hash confidence levels (from dot products)
        'HASH_CONF_0': (150, 150, 150),   # Gray - super weak
        'HASH_CONF_1': (255, 100, 100),   # Red - low confidence
        'HASH_CONF_2': (255, 200, 100),   # Orange - medium confidence
        'HASH_CONF_3': (100, 200, 255),   # Blue - good confidence
        'HASH_CONF_4': (100, 255, 100),   # Green - highest confidence
        
        # Special axon types
        'NEIGHBOR_DETECTED': (183, 110, 121),  # Rose gold
        'COORDINATE_VOID': (180, 100, 255),    # Purple
        'HEARTBEAT': (200, 200, 200),          # Gray pulse
        'MATRIX_UPDATE': (100, 255, 255),      # Cyan - matrix evolution
        'PATTERN_CHANGE': (255, 255, 100),     # Yellow - pattern switch
    }
    
    # STATE PULSE SPEEDS (based on 3 eigen system)
    STATE_PULSE_SPEEDS = {
        'STABLE': 0.5,      # Slow, steady pulse
        'LEARNING': 0.3,    # Medium pulse (active learning)
        'NOISY': 0.2,       # Fast, erratic pulse
        'RIGID': 0.4,       # Slow, rigid pulse
        'CONFUSED': 0.1,    # Very fast, confused pulse
        'DEAD': 0.0,        # No pulse
        'UNKNOWN': 0.25,    # Default pulse
    }
    
    def __init__(self, session_id=None, screen_width=1400, screen_height=900):
        print("🧠 NEXUS 3 EIGEN SYSTEM VISUALIZER")
        print("=" * 70)
        
        # ===== SESSION SETUP =====
        self.session_id = session_id or "live_3eigen_session"
        self.base_dir = "Cognition"
        self.session_dir = os.path.join(self.base_dir, self.session_id)
        
        # Create session directories if they don't exist
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(os.path.join(self.session_dir, "frames"), exist_ok=True)
        os.makedirs(os.path.join(self.session_dir, "matrix_evolution"), exist_ok=True)
        os.makedirs(os.path.join(self.session_dir, "statistics"), exist_ok=True)
        
        # ===== TIMELINE BUILDER WITH NEW EXPORTS =====
        self.timeline_builder = TimelineBuilder(self.session_dir)
        self.animation_sequences = self.timeline_builder.animation_sequences
        
        # ===== 3 EIGEN SYSTEM TRACKING =====
        self.eigen_tracking = {
            'alpha_history': [],
            'beta_history': [],
            'zeta_history': [],
            'health_state_history': [],
            'neuron_eigen_data': {}  # neuron_id -> eigen history
        }
        
        # ===== MATRIX EVOLUTION DATA =====
        self.matrix_data_available = len(self.timeline_builder.matrix_registry) > 0
        self.matrix_neuron_ids = list(self.timeline_builder.matrix_registry.keys())[:10]  # First 10
        
        # ===== CUMULATIVE STATISTICS =====
        if hasattr(self.timeline_builder, 'cumulative_stats'):
            self.cumulative_stats = self.timeline_builder.cumulative_stats
        else:
            self.cumulative_stats = {
                'total_cycles': 0,
                'total_frames': len(self.animation_sequences),
                'neurons_with_matrix': len(self.timeline_builder.matrix_registry),
                'avg_eigen_alpha': 0.0,
                'avg_eigen_beta': 0.0,
                'avg_eigen_zeta': 0.0,
                'pattern_distribution': {},
                'health_state_distribution': {},
                'matrix_quality_stats': {}
            }
        
        # ===== NEURON STATE TRACKING =====
        self.neuron_history = {}  # neuron_id -> history across frames
        self.previous_neuron_states = {}
        self.state_change_highlights = []
        
        # ===== ALWAYS START IN BROWSER MODE =====
        self.mode = self.MODE_BROWSER
        print("📁 Starting in BROWSER mode (default)")
        
        # ===== BROWSER =====
        self.browser = SessionBrowser(self.base_dir)

        # Force browser initialization
        self.browser.scan_sessions()
        
        # Clear any pre-loaded sequences to ensure clean browser start
        self.animation_sequences = []
        self.current_sequence = None

        # ===== VISUALIZATION CONFIGURATION =====
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen_mode = "neuron_view"  # "neuron_view", "stats_view", "matrix_view"
        self.fullscreen = False
        self.legend_dragging = False
        self.legend_resizing = False
        self.legend_drag_start = (0, 0)
        self.legend_original_pos = (0, 0)
        self.legend_resize_start = (0, 0)
        self.legend_original_size = (450, 800)  # Larger for 3 eigen info
        self.legend_position = (self.screen_width - 470, 100)
        self.legend_size = (450, 800)
        self.legend_change_mode = False
        
        # ===== STATISTICS SCREEN CONFIG =====
        self.stats_surface = None
        self.stats_graph_mode = "3_eigen_analysis"  # Default to 3 eigen analysis
        self.current_graph_index = 0
        self.graph_positions = []
        
        # REMOVED THE DIRECT ASSIGNMENT HERE - it's handled by the property
        
        # ===== MATRIX VIEW CONFIG =====
        self.matrix_view_mode = "position_bias"  # "position_bias", "pattern_bias", "eigen_3d"
        self.selected_matrix_neuron = None
        self.matrix_cycle_index = 0
        self.matrix_history_length = 20
        
        # ===== VISUALIZATION VARIABLES =====
        self.running = True
        self.neurons = {}
        self.coordinate_map = {}
        self.frame_cache = {}
        self.cached_surfaces = {}
        self.cache_valid_for = 1.0
        
        # ===== HOVER SYSTEM =====
        self.hover_info = None
        self.hovered_neuron_id = None
        self.hovered_matrix_data = None
        
        # ===== COORDINATE POSITIONING =====
        self.cell_size = 28  # Slightly larger for more detail
        self.pan_x, self.pan_y = 0, 0
        self.zoom = 1.0
        self.dragging_view = False
        self.drag_start_pos = (0, 0)
        self.drag_start_pan = (0, 0)
        
        # ===== CURRENT ANIMATION STATE =====
        self.current_sequence_index = 0
        self.current_sequence = None
        self.active_neurons = {}
        self.active_axon_beams = []
        self.active_particles = []
        
        # ===== ANIMATION TIMING =====
        self.animation_start_time = 0
        self.last_frame_time = 0
        self.frame_duration = 1.0
        
        # ===== COLOR ARRAYS FOR 3 EIGEN PULSING =====
        self.color_array = None
        self._init_3eigen_color_arrays()
        
        # ===== NAVIGATION =====
        self.keys_held = {
            pygame.K_LEFT: False, pygame.K_RIGHT: False,
            pygame.K_UP: False, pygame.K_DOWN: False,
            pygame.K_a: False, pygame.K_d: False,
            pygame.K_w: False, pygame.K_s: False,
            pygame.K_LSHIFT: False, pygame.K_RSHIFT: False,
            pygame.K_e: False  # Eigen view toggle
        }
        self.pan_speed = 25
        
        # ===== UI STATE =====
        self.show_legend = True
        self.show_axons = True
        self.show_grid = True
        self.show_eigen_values = True  # NEW: Show α,β,ζ values
        self.show_matrix_connections = True  # NEW: Show matrix relationships
        self.show_change_highlights = True
        self.show_processing_states = True
        
        self.focused_neuron_id = None
        self.selected_neurons = set()
        
        # ===== TIMELINE FOR REPLAY =====
        self.timeline = TimelineSequencer()
        if self.animation_sequences:
            self.timeline.load_frames(self.animation_sequences)
        
        
        # ===== TERMINAL LOGS =====
        self.logs = deque(maxlen=50)
        
        # ===== UI BUTTONS =====
        self.ui_buttons = {}
        self.hovered_button = None
        self.active_button = None
        self.hovered_session_index = None
        
        # ===== INITIALIZE PYGAME =====
        print("🔍 Initializing PyGame for 3 eigen visualization...")
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            pygame.display.set_caption(f"🧠 NEXUS 3 EIGEN VISUALIZER - {self.session_id}")
            print(f"✅ Screen created: {screen_width}x{screen_height}")
        except Exception as e:
            print(f"❌ PyGame initialization failed: {e}")
            raise
        
        # ===== FONTS =====
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 20)
        self.mono_font = pygame.font.Font(None, 22)
        self.eigen_font = pygame.font.Font(None, 32)  # For eigen value display
        
        # ===== INITIALIZE UI =====
        self._init_3eigen_ui_buttons()
        
        # ===== PERFORMANCE =====
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        
        # ===== BACKGROUND PROCESSING =====
        self.last_live_update = time.time()
        self.live_update_interval = 2.0
        
        # ===== 3 EIGEN SYSTEM INITIALIZATION =====
        self._init_3eigen_system()
        
        print("✅ 3 Eigen System Visualizer ready")
        print(f"   Mode: {self.mode}")
        print(f"   Sequences: {len(self.animation_sequences)}")
        print(f"   Matrix Data: {len(self.timeline_builder.matrix_registry)} neurons")
        print(f"   Screen Mode: {self.screen_mode}")
        print("=" * 70)
    
    # Add this property definition BEFORE any other methods:
    @property
    def graph_sets(self):
        """Property to get graph sets configuration"""
        return {
            "3_eigen_analysis": [
                '3_eigen_system',
                'matrix_evolution',
                'pattern_bias',
                'position_bias'
            ],
            "health_monitoring": [
                'health_states',
                'confidence_trend',
                'pattern_dist',
                'axon_activity'
            ],
            "pattern_analysis": [
                'pattern_bias',
                'pattern_dist',
                'position_bias',
                'health_states'
            ],
            "matrix_analysis": [
                'matrix_evolution',
                'position_bias',
                'pattern_bias',
                '3_eigen_system'
            ]
        }

    def _init_3eigen_color_arrays(self):
        """Initialize color arrays for 3 eigen system pulsing"""
        print("🎨 Initializing 3 eigen color arrays...")
        
        # Define state frequencies for 3 eigen system
        self.state_freqs = {
            'STABLE': 18,      # Steady pulse
            'LEARNING': 14,    # Active learning pulse
            'NOISY': 22,       # Erratic fast pulse
            'RIGID': 6,        # Slow rigid pulse
            'CONFUSED': 10,    # Confused medium pulse
            'DEAD': 2,         # Very slow pulse
            'UNKNOWN': 8,      # Default pulse
        }
        
        self.state_indices = {
            'STABLE': 0, 'LEARNING': 1, 'NOISY': 2, 'RIGID': 3,
            'CONFUSED': 4, 'DEAD': 5, 'UNKNOWN': 6
        }
        
        # Create 3D color array: [RGB, state, time]
        self.color_array = np.zeros((3, 7, 1000), dtype=np.uint8)
        
        # Base colors for each state
        base_colors = {
            'STABLE': (0, 255, 0),        # Pure Green
            'LEARNING': (100, 200, 255),  # Learning Blue
            'NOISY': (255, 255, 0),       # Noisy Yellow
            'RIGID': (255, 100, 100),     # Rigid Red
            'CONFUSED': (255, 100, 255),  # Confused Purple
            'DEAD': (80, 80, 80),         # Dead Gray
            'UNKNOWN': (180, 180, 180),   # Unknown Light Gray
        }
        
        # Generate color cycles with 3 eigen influence
        for state_name, state_idx in self.state_indices.items():
            freq = self.state_freqs[state_name]
            num_colors = 1000 // freq
            
            base_r, base_g, base_b = base_colors[state_name]
            
            for k in range(num_colors):
                t = k / num_colors
                
                # Different pulse patterns for different states
                if state_name == 'STABLE':
                    brightness = 0.6 + 0.4 * math.sin(t * math.pi * 2)  # Smooth pulse
                elif state_name == 'LEARNING':
                    brightness = 0.5 + 0.5 * math.sin(t * math.pi * 4)  # Faster learning pulse
                elif state_name == 'NOISY':
                    brightness = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * math.pi * 8))  # Erratic
                elif state_name == 'CONFUSED':
                    brightness = 0.5 + 0.5 * abs(math.sin(t * math.pi * 3))  # Uneven pulse
                else:
                    brightness = 0.5 + 0.5 * math.sin(t * math.pi * 2)  # Default
                
                r = int(base_r * brightness)
                g = int(base_g * brightness)
                b = int(base_b * brightness)
                
                # Clamp values
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                self.color_array[0, state_idx, k] = r
                self.color_array[1, state_idx, k] = g
                self.color_array[2, state_idx, k] = b
        
        print(f"✅ Color arrays initialized with {self.color_array.shape} dimensions")
    
    def _init_3eigen_ui_buttons(self):
        """Initialize UI buttons for 3 eigen system"""
        button_width = 110
        button_height = 32
        
        self.ui_buttons = {
            'mode_live': {
                'rect': pygame.Rect(20, 120, button_width, button_height),
                'label': '🔴 LIVE',
                'tooltip': 'Switch to Live Mode with 3 eigen tracking'
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
            'toggle_legend': {
                'rect': pygame.Rect(self.screen_width - 130, 130, 120, 28),
                'label': '[?] 3E LEGEND',
                'tooltip': 'Toggle 3 Eigen Legend'
            },
            'toggle_axons': {
                'rect': pygame.Rect(self.screen_width - 130, 165, 120, 28),
                'label': '~ MATRIX AXONS',
                'tooltip': 'Toggle Matrix Relationship Axons'
            },
            'toggle_grid': {
                'rect': pygame.Rect(self.screen_width - 130, 200, 120, 28),
                'label': '# EIGEN GRID',
                'tooltip': 'Toggle Eigen Coordinate Grid'
            },
            'toggle_eigen': {
                'rect': pygame.Rect(self.screen_width - 130, 235, 120, 28),
                'label': 'αβζ VALUES',
                'tooltip': 'Show/Hide α,β,ζ Eigen Values'
            },
            'toggle_matrix': {
                'rect': pygame.Rect(self.screen_width - 130, 270, 120, 28),
                'label': '▦ CONNECTIONS',
                'tooltip': 'Show Matrix Relationship Connections'
            },
            'stats_view': {
                'rect': pygame.Rect(self.screen_width - 130, 305, 120, 28),
                'label': '📊 STATS',
                'tooltip': 'Switch to Statistics View'
            },
            'matrix_view': {
                'rect': pygame.Rect(self.screen_width - 130, 340, 120, 28),
                'label': '▦ MATRIX VIEW',
                'tooltip': 'Switch to Matrix Evolution View'
            },
            'focus_best_eigen': {
                'rect': pygame.Rect(self.screen_width - 130, 375, 120, 28),
                'label': '⭐ BEST αβζ',
                'tooltip': 'Focus on Neuron with Highest Eigen Values'
            },
            'export_stats': {
                'rect': pygame.Rect(self.screen_width - 130, 410, 120, 28),
                'label': '💾 EXPORT',
                'tooltip': 'Export 3 Eigen Statistics'
            }
        }
    
    def _init_3eigen_system(self):
        """Initialize 3 eigen system tracking"""
        print("🧮 Initializing 3 eigen system tracking...")
        
        # Extract initial eigen data if available
        if self.animation_sequences:
            for sequence in self.animation_sequences[:10]:  # First 10 sequences
                for neuron in sequence.get('eigen_system_data', []):
                    neuron_id = neuron.get('neuron_id')
                    alpha = neuron.get('eigen_alpha', 0)
                    beta = neuron.get('eigen_beta', 0)
                    zeta = neuron.get('eigen_zeta', 0)
                    
                    if neuron_id and (alpha > 0 or beta > 0 or zeta > 0):
                        if neuron_id not in self.eigen_tracking['neuron_eigen_data']:
                            self.eigen_tracking['neuron_eigen_data'][neuron_id] = {
                                'alpha_history': [],
                                'beta_history': [],
                                'zeta_history': [],
                                'health_history': [],
                                'coordinate': neuron.get('coordinate'),
                                'pattern': neuron.get('pattern', 'UNKNOWN')
                            }
                        
                        self.eigen_tracking['neuron_eigen_data'][neuron_id]['alpha_history'].append(alpha)
                        self.eigen_tracking['neuron_eigen_data'][neuron_id]['beta_history'].append(beta)
                        self.eigen_tracking['neuron_eigen_data'][neuron_id]['zeta_history'].append(zeta)
                        self.eigen_tracking['neuron_eigen_data'][neuron_id]['health_history'].append(
                            neuron.get('health_status', 'UNKNOWN')
                        )
        
        # Initialize matrix view selection
        if self.matrix_neuron_ids:
            self.selected_matrix_neuron = self.matrix_neuron_ids[0]
        
        print(f"✅ 3 eigen system initialized: {len(self.eigen_tracking['neuron_eigen_data'])} neurons with eigen data")
    
    def _load_current_sequence(self, sequence: Dict):
        """Load and activate an animation sequence with 3 eigen data"""
        if not sequence:
            return
        
        self.current_sequence = sequence
        self.animation_start_time = time.time()
        
        # Clear previous state
        self.active_neurons.clear()
        self.active_axon_beams.clear()
        self.active_particles.clear()
        self.neurons.clear()
        self.coordinate_map.clear()
        
        # Load neuron states from sequence
        for neuron_anim in sequence.get('neuron_animations', []):
            coord = neuron_anim.get('coordinate')
            if coord:
                coord_tuple = tuple(coord) if isinstance(coord, list) else coord
                self.active_neurons[coord_tuple] = neuron_anim
                
                # Also populate neurons dict for connections
                neuron_id = neuron_anim.get('neuron_id', f'neuron_{len(self.neurons)}')
                visual_neuron = VisualNeuron(
                    id=neuron_id,
                    coordinate=coord_tuple,
                    pattern=neuron_anim.get('pattern', 'UNKNOWN'),
                    state=neuron_anim.get('current_state', 'UNKNOWN'),
                    similarity=neuron_anim.get('confidence', 0.5)
                )
                self.neurons[neuron_id] = visual_neuron
                self.coordinate_map[coord_tuple] = neuron_id
        
        # Load axon beams (including matrix relationship axons)
        for axon_anim in sequence.get('axon_animations', []):
            self.active_axon_beams.append({
                **axon_anim,
                'start_time': time.time(),
                'progress': 0.0
            })
        
        # Load particle animations
        for particle_anim in sequence.get('particle_animations', []):
            self.active_particles.append({
                **particle_anim,
                'start_time': time.time(),
                'progress': 0.0
            })
        
        # Update cumulative statistics
        self._update_cumulative_stats(sequence)
        
        # Update 3 eigen tracking
        self._update_3eigen_tracking(sequence)
        
        print(f"📥 Loaded sequence {sequence.get('frame', 0)} with {len(self.active_neurons)} neurons")
    
    def _update_3eigen_tracking(self, sequence: Dict):
        """Update 3 eigen system tracking from sequence"""
        eigen_data = sequence.get('eigen_system_data', [])
        if not eigen_data:
            return
        
        # Track average eigen values
        alphas = [n.get('eigen_alpha', 0) for n in eigen_data]
        betas = [n.get('eigen_beta', 0) for n in eigen_data]
        zetas = [n.get('eigen_zeta', 0) for n in eigen_data]
        
        if alphas:
            self.eigen_tracking['alpha_history'].append(np.mean(alphas))
        if betas:
            self.eigen_tracking['beta_history'].append(np.mean(betas))
        if zetas:
            self.eigen_tracking['zeta_history'].append(np.mean(zetas))
        
        # Track health states
        health_states = [n.get('health_status', 'UNKNOWN') for n in eigen_data]
        state_counts = {}
        for state in health_states:
            state_counts[state] = state_counts.get(state, 0) + 1
        self.eigen_tracking['health_state_history'].append(state_counts)
        
        # Keep history manageable
        max_history = 100
        for key in ['alpha_history', 'beta_history', 'zeta_history', 'health_state_history']:
            if len(self.eigen_tracking[key]) > max_history:
                self.eigen_tracking[key] = self.eigen_tracking[key][-max_history:]
    
    def _update_cumulative_stats(self, sequence: Dict):
        """Update cumulative statistics from sequence"""
        frame_num = sequence.get('frame', 0)
        
        # Count axons in this frame
        frame_axons = len(sequence.get('axon_animations', []))
        
        # Count eigen-active neurons
        eigen_neurons = len(sequence.get('eigen_system_data', []))
        
        # Update cumulative totals
        self.cumulative_stats['total_cycles'] += frame_axons
        self.cumulative_stats['total_frames'] = max(self.cumulative_stats['total_frames'], frame_num + 1)
        
        # Update pattern distribution
        for neuron in sequence.get('neuron_animations', []):
            pattern = neuron.get('pattern', 'UNKNOWN')
            self.cumulative_stats['pattern_distribution'][pattern] = \
                self.cumulative_stats['pattern_distribution'].get(pattern, 0) + 1
        
        # Update health state distribution
        for neuron in sequence.get('eigen_system_data', []):
            health = neuron.get('health_status', 'UNKNOWN')
            self.cumulative_stats['health_state_distribution'][health] = \
                self.cumulative_stats['health_state_distribution'].get(health, 0) + 1
        
        # Store frame history
        frame_data = {
            'frame': frame_num,
            'neurons': len(sequence.get('neuron_animations', [])),
            'eigen_neurons': eigen_neurons,
            'axons': frame_axons
        }
        
        if 'frame_history' not in self.cumulative_stats:
            self.cumulative_stats['frame_history'] = deque(maxlen=100)
        self.cumulative_stats['frame_history'].append(frame_data)

    def _load_matrix_data(self):
        """Load matrix data from session directory - with 87D support"""
        matrix_dir = os.path.join(self.session_dir, "87d_matrix_samples")
        matrix_file = os.path.join(matrix_dir, "87d_matrix_data.json")
        
        if os.path.exists(matrix_file):
            try:
                with open(matrix_file, 'r') as f:
                    data = json.load(f)
                    print(f"📊 Loaded 87D matrix data: {len(data)} samples")
                    return data
            except Exception as e:
                print(f"⚠️ Error loading 87D matrix data: {e}")
        
    def _toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            # Get the current display mode
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            self.screen_width = info.current_w
            self.screen_height = info.current_h
            self._add_log("🖥️ Entered fullscreen mode")
        else:
            self.screen = pygame.display.set_mode((1200, 800))
            self.screen_width = 1200
            self.screen_height = 800
            self._add_log("🖥️ Entered windowed mode")
        
        # Reinitialize UI elements for new screen size
        self._init_ui_buttons()
        self._clear_frame_cache()
        
        # Create or recreate stats surface
        if self.screen_mode == "stats_view":
            self._init_stats_surface()

    def _clear_frame_cache(self):
            """Clear frame cache when view parameters change"""
            self.frame_cache.clear()

    def _coord_to_screen(self, coord, center_x=None, center_y=None):
        """Convert coordinate to screen position EXACTLY LIKE SPIDEY"""
        if not coord:
            return None
        
        if center_x is None:
            center_x = self.screen_width // 2 + self.pan_x
        if center_y is None:
            center_y = self.screen_height // 2 + self.pan_y
        
        # Ensure coord is tuple
        if isinstance(coord, list):
            coord_tuple = tuple(coord)
        else:
            coord_tuple = coord
        
        depth = len(coord_tuple) - 1
        sibling_index = coord_tuple[-1] if len(coord_tuple) > 0 else 0
        
        # EXACT SPIDEY FORMULA
        x = center_x + int(sibling_index * self.cell_size * self.zoom)
        y = center_y + int(depth * self.cell_size * self.zoom)
        
        return (int(x), int(y))

    def _update_hover_info(self):
        """Update hover information for the current hovered neuron"""
        if not self.hovered_neuron_id:
            self.hover_info = None
            return
        
        # Find the neuron in current sequence
        for coord, neuron_data in self.active_neurons.items():
            if neuron_data.get('neuron_id') == self.hovered_neuron_id:
                self.hover_info = {
                    'neuron_data': neuron_data,
                    'coordinate': coord,
                    'screen_pos': self._coord_to_screen(coord),
                    'hover_time': time.time()
                }
                break
        else:
            self.hover_info = None

    def _draw_hover_info(self):
        """Draw hover information with cumulative statistics from TimelineBuilder - UPDATED"""
        if not self.hover_info or not self.hovered_neuron_id:
            return
        
        neuron_data = self.hover_info['neuron_data']
        neuron_id = neuron_data.get('neuron_id')
        coord = self.hover_info['coordinate']
        screen_pos = self.hover_info['screen_pos']
        
        if not screen_pos:
            return
        
        # Get cumulative lifecycle data from TimelineBuilder
        neuron_lifecycle = self.timeline_builder.get_neuron_lifecycle(neuron_id)
        
        # Get eigen values
        eigenvalues = neuron_data.get('eigenvalues', [])
        
        # Create hover panel
        panel_width = 400  # Slightly wider for eigen info
        panel_height = 460 if neuron_lifecycle else 340
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Position panel
        panel_x = mouse_x + 20
        panel_y = mouse_y + 20
        
        if panel_x + panel_width > self.screen_width:
            panel_x = mouse_x - panel_width - 20
        if panel_y + panel_height > self.screen_height:
            panel_y = mouse_y - panel_height - 20
        
        # Draw panel
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (15, 15, 30, 230), 
                        panel_surf.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surf, (80, 100, 180, 150),
                        panel_surf.get_rect(), 2, border_radius=8)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        y_offset = panel_y + 15
        
        # Title with eigen indicator if available
        if eigenvalues:
            title_text = "NEURON DETAILS (EIGEN)"
        else:
            title_text = "NEURON DETAILS"
        
        title = self.font.render(title_text, True, (255, 255, 200))
        self.screen.blit(title, (panel_x + 15, y_offset))
        y_offset += 35
        
        # Connection line
        line_end_x = panel_x if mouse_x < panel_x else panel_x + panel_width
        line_end_y = panel_y + 50
        
        pygame.draw.line(self.screen, (100, 150, 255, 180),
                        screen_pos,
                        (line_end_x, line_end_y), 2)
        
        # Information columns
        col1_width = 130
        col2_x = panel_x + col1_width + 10
        
        # BASIC INFO SECTION
        basic_rows = [
            ("ID:", neuron_id[:18] + ("..." if len(neuron_id) > 18 else ""), (220, 220, 255)),
            ("Coordinate:", str(coord), (200, 220, 255)),
            ("Pattern:", neuron_data.get('pattern', 'UNKNOWN'), 
            PATTERN_COLORS.get(neuron_data.get('pattern', 'UNKNOWN'), (255, 255, 255))),
            ("Current State:", neuron_data.get('current_state', 'UNKNOWN'), 
            STATE_COLORS.get(neuron_data.get('current_state', 'UNKNOWN'), (255, 255, 255))),
            ("Confidence:", f"{neuron_data.get('confidence', 0) * 100:.1f}%", 
            self._get_similarity_color(neuron_data.get('confidence', 0))),
            ("Frame:", str(neuron_data.get('frame', 'N/A')), (180, 200, 220)),
        ]
        
        for label, value, color in basic_rows:
            label_surf = self.small_font.render(label, True, (180, 200, 220))
            self.screen.blit(label_surf, (panel_x + 15, y_offset))
            
            value_surf = self.small_font.render(str(value), True, color)
            self.screen.blit(value_surf, (col2_x, y_offset))
            
            y_offset += 22
        
        # EIGEN VALUE SECTION (if available)
        if eigenvalues:
            y_offset += 5
            pygame.draw.line(self.screen, (80, 100, 180, 100),
                            (panel_x + 10, y_offset),
                            (panel_x + panel_width - 10, y_offset), 1)
            y_offset += 10
            
            eigen_title = self.small_font.render("EIGEN VALUES:", True, (255, 255, 180))
            self.screen.blit(eigen_title, (panel_x + 15, y_offset))
            y_offset += 25
            
            # Show eigen values with appropriate labels
            eigen_labels = ['α', 'β', 'ζ'] if len(eigenvalues) >= 3 else ['E1', 'E2', 'E3']
            
            for i, (label, value) in enumerate(zip(eigen_labels, eigenvalues[:3])):
                # Determine color based on value
                if value >= 0.8:
                    value_color = (100, 255, 100)
                elif value >= 0.6:
                    value_color = (255, 255, 100)
                elif value >= 0.4:
                    value_color = (255, 200, 100)
                elif value >= 0.2:
                    value_color = (255, 150, 100)
                else:
                    value_color = (255, 100, 100)
                
                label_surf = self.small_font.render(f"{label}:", True, (200, 220, 255))
                self.screen.blit(label_surf, (panel_x + 25, y_offset))
                
                value_text = f"{value:.3f}"
                value_surf = self.small_font.render(value_text, True, value_color)
                self.screen.blit(value_surf, (col2_x, y_offset))
                
                # Simple progress bar
                bar_width = 100
                bar_height = 6
                bar_x = col2_x + 70
                bar_y = y_offset + 3
                
                # Background
                pygame.draw.rect(self.screen, (40, 40, 60), 
                            (bar_x, bar_y, bar_width, bar_height), border_radius=3)
                
                # Filled portion
                fill_width = int(bar_width * min(1.0, value))
                if fill_width > 0:
                    pygame.draw.rect(self.screen, value_color, 
                                (bar_x, bar_y, fill_width, bar_height), border_radius=3)
                
                y_offset += 22
        
        if neuron_lifecycle:
            # LIFECYCLE STATISTICS SECTION
            life_title = self.small_font.render("LIFECYCLE STATISTICS:", True, (255, 255, 180))
            self.screen.blit(life_title, (panel_x + 15, y_offset))
            y_offset += 25
            
            first_seen = neuron_lifecycle.get('first_seen', 'N/A')
            last_seen = neuron_lifecycle.get('last_seen', 'N/A')
            lifetime = f"{last_seen - first_seen + 1}" if isinstance(first_seen, int) and isinstance(last_seen, int) else "N/A"
            axon_counts = neuron_lifecycle.get('axon_counts', {})
            
            life_rows = [
                ("First Seen:", f"Frame {first_seen}", (180, 200, 220)),
                ("Last Seen:", f"Frame {last_seen}", (180, 200, 220)),
                ("Lifetime:", f"{lifetime} frames", (200, 220, 255)),
                ("Total Axons:", str(axon_counts.get('total', 0)), (200, 220, 255)),
                ("Hash Axons:", str(axon_counts.get('hash', 0)), 
                self._get_hash_confidence_color(min(1.0, axon_counts.get('hash', 0)/10.0))),
                ("Void Axons:", str(axon_counts.get('void', 0)), AXON_COLORS['COORDINATE_VOID']),
                ("Neighbor Axons:", str(axon_counts.get('neighbor', 0)), (183, 110, 121)),  # Rose gold
            ]
            
            for label, value, color in life_rows:
                label_surf = self.small_font.render(label, True, (180, 200, 220))
                self.screen.blit(label_surf, (panel_x + 25, y_offset))
                
                value_surf = self.small_font.render(str(value), True, color)
                self.screen.blit(value_surf, (col2_x, y_offset))
                
                y_offset += 22
            
            # State history
            state_history = neuron_lifecycle.get('recent_states', [])
            if state_history:
                y_offset += 5
                state_title = self.small_font.render("Recent States:", True, (180, 200, 220))
                self.screen.blit(state_title, (panel_x + 15, y_offset))
                y_offset += 20
                
                # Show last 3 states
                recent_states = state_history[-3:] if len(state_history) > 3 else state_history
                for state_data in recent_states:
                    if isinstance(state_data, tuple) and len(state_data) >= 3:
                        frame, state, confidence = state_data[:3]
                        state_str = f"Frame {frame}: {state} ({confidence*100:.0f}%)"
                        state_color = STATE_COLORS.get(state, (200, 200, 200))
                        state_surf = self.small_font.render(state_str, True, state_color)
                        self.screen.blit(state_surf, (panel_x + 30, y_offset))
                        y_offset += 18
            
            # Pattern history
            pattern_history = neuron_lifecycle.get('recent_patterns', [])
            if pattern_history:
                y_offset += 5
                pattern_title = self.small_font.render("Pattern History:", True, (180, 200, 220))
                self.screen.blit(pattern_title, (panel_x + 15, y_offset))
                y_offset += 20
                
                for pattern_data in pattern_history:
                    if isinstance(pattern_data, tuple) and len(pattern_data) >= 2:
                        frame, pattern = pattern_data[:2]
                        pattern_str = f"Frame {frame}: {pattern}"
                        pattern_color = PATTERN_COLORS.get(pattern, (200, 200, 200))
                        pattern_surf = self.small_font.render(pattern_str, True, pattern_color)
                        self.screen.blit(pattern_surf, (panel_x + 30, y_offset))
                        y_offset += 18
        
        # GLOBAL STATS
        if y_offset < panel_y + panel_height - 50:
            y_offset += 10
            pygame.draw.line(self.screen, (80, 100, 180, 80),
                            (panel_x + 10, y_offset),
                            (panel_x + panel_width - 10, y_offset), 1)
            y_offset += 15
            
            global_title = self.small_font.render("Session Totals:", True, (180, 200, 255))
            self.screen.blit(global_title, (panel_x + 15, y_offset))
            y_offset += 20
            
            global_stats = [
                f"Total Frames: {self.cumulative_stats.get('total_frames', 0)}",
                f"Total Neurons: {self.cumulative_stats.get('total_neurons', 0)}",
                f"Total Axons: {self.cumulative_stats.get('total_cycles', 0)}",
                f"State Changes: {self.cumulative_stats.get('state_changes', 0)}",
                f"Pattern Changes: {self.cumulative_stats.get('pattern_changes', 0)}",
            ]
            
            for stat in global_stats:
                stat_surf = self.small_font.render(stat, True, (200, 220, 255))
                self.screen.blit(stat_surf, (panel_x + 25, y_offset))
                y_offset += 18

    def _get_hash_confidence_color(self, confidence: float) -> Tuple[int, int, int]:
        """Get color based on hash confidence level"""
        if confidence >= 0.8:
            return AXON_COLORS.get('HASH_CONF_4', (100, 255, 100))
        elif confidence >= 0.6:
            return AXON_COLORS.get('HASH_CONF_3', (100, 180, 255))
        elif confidence >= 0.4:
            return AXON_COLORS.get('HASH_CONF_2', (255, 200, 100))
        elif confidence >= 0.2:
            return AXON_COLORS.get('HASH_CONF_1', (255, 100, 100))
        else:
            return AXON_COLORS.get('HASH_CONF_0', (150, 150, 150))

    def _create_state_change_highlight(self, coord, neuron_id, old_state, new_state):
        """Create visual feedback for neuron state changes"""
        screen_pos = self._coord_to_screen(coord)
        if not screen_pos:
            return
        
        # Create a pulse animation for state changes
        highlight = {
            'type': 'state_change',
            'neuron_id': neuron_id,
            'coord': coord,
            'screen_pos': screen_pos,
            'old_state': old_state,
            'new_state': new_state,
            'start_time': time.time(),
            'duration': 1.5,  # 1.5 second highlight
            'max_size': 15 * self.zoom
        }
        
        # Color based on state transition
        color_map = {
            ('STABLE', 'LEARNING'): (100, 200, 255),  # Green → Blue
            ('LEARNING', 'STABLE'): (100, 255, 100),  # Blue → Green
            ('STABLE', 'NOISY'): (255, 255, 100),     # Green → Yellow
            ('NOISY', 'STABLE'): (100, 255, 100),     # Yellow → Green
            ('CONFUSED', 'STABLE'): (100, 255, 100),  # Purple → Green
            ('RIGID', 'STABLE'): (100, 255, 100),     # Red → Green
            ('STABLE', 'CONFUSED'): (255, 150, 255),  # Green → Purple
            ('LEARNING', 'NOISY'): (255, 255, 100),   # Blue → Yellow
            ('NOISY', 'LEARNING'): (100, 200, 255),   # Yellow → Blue
        }
        
        highlight['color'] = color_map.get((old_state, new_state), (255, 255, 255))
        self.state_change_highlights.append(highlight)

    def _load_current_sequence(self, frame_data: Dict):
        """Load frame data from Nexus - SIMPLE EXTRACTION"""
        if not frame_data:
            return
        
        self.current_sequence = frame_data
        self.animation_start_time = time.time()
        
        # Clear previous state
        self.active_neurons.clear()
        self.active_axon_beams.clear()
        self.neurons.clear()
        self.coordinate_map.clear()
        
        # Extract data from frame
        data = frame_data.get('data', {})
        neurons_data = data.get('neurons', {})
        axons_data = data.get('axons', [])
        
        # ===== LOAD NEURONS =====
        for neuron_id, neuron_data in neurons_data.items():
            coord = neuron_data.get('coordinate')
            if not coord:
                continue
            
            coord_tuple = tuple(coord) if isinstance(coord, list) else coord
            
            # Store in active_neurons
            self.active_neurons[coord_tuple] = neuron_data
            
            # Create VisualNeuron
            visual_neuron = VisualNeuron(
                id=neuron_id,
                coordinate=coord_tuple,
                pattern=neuron_data.get('pattern', 'UNKNOWN'),
                state=neuron_data.get('state', 'UNKNOWN'),
                similarity=neuron_data.get('similarity', 0.5)
            )
            self.neurons[neuron_id] = visual_neuron
            self.coordinate_map[coord_tuple] = neuron_id
        
        # ===== LOAD AXONS =====
        for axon in axons_data:
            axon_type = axon.get('axon_type', 'UNKNOWN')
            source_info = axon.get('source', {})
            
            # Create axon beam
            axon_beam = {
                'axon_type': axon_type,
                'source_coord': tuple(source_info.get('coordinate', (0, 0))) if source_info.get('coordinate') else None,
                'target_coord': tuple(axon.get('data', {}).get('coordinate', (0, 0))) if axon.get('data', {}).get('coordinate') else None,
                'confidence': axon.get('data', {}).get('confidence', 0.5),
                'start_time': time.time(),
                'progress': 0.0
            }
            
            self.active_axon_beams.append(axon_beam)
        
        # Update frame counter
        self.current_sequence_index = frame_data.get('frame', 0)
        self._update_cumulative_stats(frame_data)
        






















    def _draw_state_change_highlights(self):
        """Draw highlights for neurons that changed state"""
        if not self.state_change_highlights or not self.show_change_highlights:
            return
        
        current_time = time.time()
        
        # Filter and update highlights
        active_highlights = []
        
        for highlight in self.state_change_highlights:
            elapsed = current_time - highlight['start_time']
            progress = min(1.0, elapsed / highlight['duration'])
            
            if progress >= 1.0:
                continue  # Remove expired highlights
            
            # Draw pulsing circle
            screen_pos = highlight.get('screen_pos')
            if not screen_pos:
                continue
            
            # Calculate pulse size
            pulse_size = highlight['max_size'] * (0.3 + 0.7 * math.sin(progress * math.pi))
            
            # Fade out towards the end
            alpha = int(200 * (1.0 - progress))
            color = (*highlight.get('color', (255, 255, 255)), alpha)
            
            # Draw pulse
            temp_surface = pygame.Surface((int(pulse_size * 2), int(pulse_size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color,
                            (int(pulse_size), int(pulse_size)),
                            int(pulse_size))
            self.screen.blit(temp_surface, 
                            (screen_pos[0] - pulse_size, screen_pos[1] - pulse_size))
            
            active_highlights.append(highlight)
        
        self.state_change_highlights = active_highlights

    def _cache_current_frame(self):
        """Cache the visual elements of the current frame"""
        if self.current_sequence_index in self.frame_cache:
            return
        
        frame_cache = {
            'timestamp': time.time(),
            'neurons': self.active_neurons.copy(),
            'axon_beams': self.active_axon_beams.copy(),
            'particles': self.active_particles.copy()
        }
        
        # Create batched surfaces for this frame
        self._create_batched_surfaces(frame_cache)
        self.frame_cache[self.current_sequence_index] = frame_cache


    # ===== DRAWING METHODS =====
    
    def _draw_grid(self):
        """Draw grid EXACTLY LIKE SPIDEY"""
        center_x = self.screen_width // 2 + self.pan_x
        center_y = self.screen_height // 2 + self.pan_y
        
        # Vertical lines (sibling axis)
        for i in range(-20, 21):
            x = center_x + i * self.cell_size * self.zoom
            pygame.draw.line(self.screen, (100, 100, 100, 50),
                           (x, 100), (x, self.screen_height - 150), 1)
        
        # Horizontal lines (depth axis)
        for i in range(30):
            y = center_y + i * self.cell_size * self.zoom
            pygame.draw.line(self.screen, (100, 100, 100, 50),
                           (50, y), (self.screen_width - 50, y), 1)
        
        # Axes
        pygame.draw.line(self.screen, (150, 150, 150),
                        (center_x, 100), (center_x, self.screen_height - 150), 2)
        pygame.draw.line(self.screen, (150, 150, 150),
                        (50, center_y), (self.screen_width - 50, center_y), 2)

    # ===== MAIN UPDATE LOOP =====

    def update(self):
        """Update visualizer state"""
        current_time = time.time()
        
        # Handle navigation keys
        if self.keys_held[pygame.K_LSHIFT] or self.keys_held[pygame.K_RSHIFT]:
            effective_pan_speed = self.pan_speed * 2.5
        else:
            effective_pan_speed = self.pan_speed
        
        if self.keys_held[pygame.K_LEFT] or self.keys_held[pygame.K_a]:
            self.pan_x += effective_pan_speed
        if self.keys_held[pygame.K_RIGHT] or self.keys_held[pygame.K_d]:
            self.pan_x -= effective_pan_speed
        if self.keys_held[pygame.K_UP] or self.keys_held[pygame.K_w]:
            self.pan_y += effective_pan_speed
        if self.keys_held[pygame.K_DOWN] or self.keys_held[pygame.K_s]:
            self.pan_y -= effective_pan_speed
        
        # Update hover info
        self._update_hover_info()
        
        # Mode-specific updates
        if self.mode == self.MODE_REPLAY and self.timeline.frames:
            # Get next sequence from timeline
            frame = self.timeline.update()
            if frame:
                self._load_current_sequence(frame)
                self.current_sequence_index = self.timeline.current_frame_index
                self.last_frame_time = current_time
        
        elif self.mode == self.MODE_LIVE:
            # Check for new animation sequences
            if current_time - self.last_live_update >= self.live_update_interval:
                # Process any new frames in background
                if self.timeline_builder:
                    processed = self.timeline_builder.process_new_frames()
                    if processed > 0:
                        self.timeline.frames = self.timeline_builder.get_frames()
                        self._add_log(f"📥 Processed {processed} new frames")
                
                # If no current sequence, load the latest
                if not self.current_sequence and self.timeline.frames:
                    self._load_current_sequence(self.timeline.frames[-1])
                    self.current_sequence_index = len(self.timeline.frames) - 1
                
                self.last_live_update = current_time
                
    def _draw_neuron_labels(self):
        """Draw neuron coordinate labels (must be done fresh each frame)"""
        if not self.active_neurons:
            return
        
        # Only draw labels if zoomed in enough
        if self.zoom < 0.8:
            return
        
        for coord, neuron_data in self.active_neurons.items():
            if len(coord) <= 2:
                screen_pos = self._coord_to_screen(coord)
                if screen_pos:
                    label = str(coord[-1]) if coord else "R"
                    label_surf = self.small_font.render(label, True, (255, 255, 255, 200))
                    label_rect = label_surf.get_rect(center=screen_pos)
                    self.screen.blit(label_surf, label_rect)

    def _draw_connections(self):
        """Draw transparent parent-child connections"""
        if len(self.neurons) < 2:
            return
        
        # Very transparent connections
        for neuron in self.neurons.values():
            coord = neuron.coordinate
            if len(coord) <= 1:
                continue
            
            parent_coord = coord[:-1]
            parent_id = self.coordinate_map.get(parent_coord)
            
            if parent_id and parent_id in self.neurons:
                parent = self.neurons[parent_id]
                
                # Get positions
                child_pos = self._coord_to_screen(coord)
                parent_pos = self._coord_to_screen(parent_coord)
                
                if child_pos and parent_pos:
                    # Very subtle connection lines
                    color = (120, 140, 180, 40)  # Very transparent
                    pygame.draw.line(self.screen, color, parent_pos, child_pos, 1)

    def _init_color_arrays(self):
        """Initialize the 3D color arrays - SIMPLE BRIGHTNESS PULSING"""
        # Define state frequencies (Hz)
        self.state_freqs = {
            'STABLE': 20, 'LEARNING': 16, 'NOISY': 12, 
            'RIGID': 4, 'CONFUSED': 8, 'DEAD': 1, 'UNKNOWN': 2
        }
        
        self.state_indices = {
            'STABLE': 0, 'LEARNING': 1, 'NOISY': 2, 'RIGID': 3,
            'CONFUSED': 4, 'DEAD': 5, 'UNKNOWN': 6
        }
        
        self.color_array = np.zeros((3, 7, 1000), dtype=np.uint8)
        
        # BASE COLORS (full brightness)
        base_colors = {
            'STABLE': (0, 255, 0),        # Pure Green
            'LEARNING': (255, 165, 0),    # Pure Orange
            'NOISY': (255, 255, 0),       # Pure Yellow
            'RIGID': (255, 0, 0),         # Pure Red
            'CONFUSED': (255, 0, 255),    # Pure Magenta
            'DEAD': (100, 100, 100),      # Medium Gray
            'UNKNOWN': (200, 200, 200),   # Light Gray
        }
        
        # Generate color cycles - JUST PULSE BRIGHTNESS
        for state_name, state_idx in self.state_indices.items():
            freq = self.state_freqs[state_name]
            num_colors = 1000 // freq
            
            base_r, base_g, base_b = base_colors[state_name]
            
            for k in range(num_colors):
                t = k / num_colors
                
                # Simple brightness pulse (0.4 to 1.0)
                # This keeps the exact hue, just varies brightness
                brightness = 0.4 + 0.6 * math.sin(t * math.pi * 2)
                
                r = int(base_r * brightness)
                g = int(base_g * brightness)
                b = int(base_b * brightness)
                
                # Clamp
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                self.color_array[0, state_idx, k] = r
                self.color_array[1, state_idx, k] = g
                self.color_array[2, state_idx, k] = b
   
    def _draw_inner_dots(self):
        """Draw dots using precomputed 3D color arrays - UPDATED FOR 3 EIGEN VALUES"""
        if not self.active_neurons:
            return
        
        current_time = time.time()
        
        for coord, neuron_data in self.active_neurons.items():
            screen_pos = self._coord_to_screen(coord)
            if not screen_pos:
                continue
            
            # Get neuron properties
            state = neuron_data.get('current_state', 'UNKNOWN')
            confidence = neuron_data.get('confidence', 0.5)
            
            # Get eigen values (could be 3 values or legacy format)
            eigenvalues = neuron_data.get('eigenvalues', [])
            
            # Calculate combined eigen strength from available values
            if eigenvalues:
                eigen_strength = sum(eigenvalues) / len(eigenvalues)
            else:
                eigen_strength = 0.5  # Default
            
            # Outer neuron size
            base_outer_size = 6.0
            outer_size = int(base_outer_size * (0.8 + confidence * 0.4) * self.zoom)
            
            # Inner dot is 40% of outer radius
            inner_size = max(1, int(outer_size * 0.4))
            
            # Get state index (default to UNKNOWN if not found)
            state_idx = self.state_indices.get(state, self.state_indices['UNKNOWN'])
            freq = self.state_freqs.get(state, self.state_freqs['UNKNOWN'])
            
            # Calculate which color in the cycle to use
            cycle_time = current_time % (1.0 / freq)
            color_index = int(cycle_time * freq * 1000) % (1000 // freq)
            
            # Get RGB values from array
            r = self.color_array[0, state_idx, color_index]
            g = self.color_array[1, state_idx, color_index]
            b = self.color_array[2, state_idx, color_index]
            
            # Apply eigen strength to color (brighter for higher eigen values)
            brightness = 0.5 + 0.5 * eigen_strength
            
            # If we have specific 3 eigen values, tint the color
            if len(eigenvalues) >= 3:
                eigen_alpha, eigen_beta, eigen_zeta = eigenvalues[:3]
                # Add eigen-based tint: red for alpha, green for beta, blue for zeta
                r_tint = int(r * (1.0 + eigen_alpha * 0.3))
                g_tint = int(g * (1.0 + eigen_beta * 0.3))
                b_tint = int(b * (1.0 + eigen_zeta * 0.3))
                
                r = min(255, r_tint)
                g = min(255, g_tint)
                b = min(255, b_tint)
            
            # Apply confidence brightness
            final_color = (
                min(255, int(r * brightness)),
                min(255, int(g * brightness)),
                min(255, int(b * brightness))
            )
            
            # Draw the glowing dot
            pygame.draw.circle(self.screen, final_color, screen_pos, inner_size)
            
    def _draw_void_branches(self, beam, current_time):
        """Draw void axon attempting to reach specific void coordinates (always purple)
        ONLY animates when there's an actual void coordinate target
        """
        source_coord = beam.get('source_coord')
        target_coord = beam.get('target_coord')  # The void coordinate that failed
        
        # CRITICAL: If no target_coord, don't animate at all!
        if not source_coord or not target_coord:
            return
        
        source_pos = self._coord_to_screen(source_coord)
        target_pos = self._coord_to_screen(target_coord)
        
        if not source_pos or not target_pos:
            return
        
        start_time = beam.get('start_time', current_time)
        duration = 2.0  # Void attempts linger longer
        
        elapsed = current_time - start_time
        progress = min(1.0, elapsed / duration)
        
        # Void color (ALWAYS purple for void calls)
        void_color = AXON_COLORS.get('COORDINATE_VOID', (180, 100, 255))
        
        # Calculate direction to target void coordinate
        dx = target_pos[0] - source_pos[0]
        dy = target_pos[1] - source_pos[1]
        distance = math.sqrt(dx*dx + dy*dy) if (dx != 0 or dy != 0) else 1
        
        # Show 2 attempts to reach the void coordinate (cleaner, less resource-intensive)
        num_attempts = 2
        for attempt in range(num_attempts):
            # Each attempt fades out faster
            attempt_progress = progress * (1.0 - (attempt * 0.3))  # Faster fade
            if attempt_progress <= 0:
                continue
            
            # Attempt reaches a fraction of the distance then fizzles
            # First attempt goes further than second
            attempt_distance = distance * min(0.9, attempt_progress * (0.9 - attempt * 0.3))
            
            # Subtle jitter for each attempt (less CPU intensive)
            jitter_x = math.sin(current_time * 8 + attempt) * 3 * (1.0 - attempt_progress)
            jitter_y = math.cos(current_time * 6 + attempt) * 3 * (1.0 - attempt_progress)
            
            attempt_end_x = source_pos[0] + (dx / distance) * attempt_distance + jitter_x
            attempt_end_y = source_pos[1] + (dy / distance) * attempt_distance + jitter_y
            
            # Fading color as attempt fails
            attempt_alpha = int(180 * (1.0 - attempt_progress))
            attempt_color = (*void_color, attempt_alpha)
            attempt_width = max(1, int(2 * (1.0 - attempt_progress) * self.zoom))
            
            # Draw the attempt line
            pygame.draw.line(self.screen, attempt_color,
                        source_pos, 
                        (int(attempt_end_x), int(attempt_end_y)), 
                        attempt_width)
            
            # Simple fizzle particles at the end (fewer particles)
            num_fizzle_particles = 2  # Reduced from 4
            for p in range(num_fizzle_particles):
                fizzle_angle = random.random() * math.pi * 2
                fizzle_dist = 4 * (1.0 - attempt_progress) * self.zoom  # Smaller
                fizzle_x = attempt_end_x + math.cos(fizzle_angle) * fizzle_dist
                fizzle_y = attempt_end_y + math.sin(fizzle_angle) * fizzle_dist
                
                fizzle_size = max(1, int(2 * (1.0 - attempt_progress) * self.zoom))
                fizzle_alpha = int(120 * (1.0 - attempt_progress) * (1.0 - p/num_fizzle_particles))
                fizzle_color = (*void_color, fizzle_alpha)
                
                pygame.draw.circle(self.screen, fizzle_color,
                                (int(fizzle_x), int(fizzle_y)), fizzle_size)
        
        # Simple void source pulse (less intense)
        if progress < 0.8:  # Only pulse for first 80% of duration
            pulse_size = max(1, int(6 * (0.5 + 0.3 * math.sin(current_time * 2)) * self.zoom))  # Smaller, slower
            pulse_alpha = int(60 * (1.0 - progress * 0.5))  # More transparent
            pulse_color = (*void_color, pulse_alpha)
            pygame.draw.circle(self.screen, pulse_color, source_pos, pulse_size, 1)  # Outline only

    def _draw_axon_comets(self):
        """Draw ALL axon animations - ORIGINAL COMPLETE VERSION - NO SUPER CALLS"""
        if not self.active_axon_beams:
            return
        
        current_time = time.time()
        
        for beam in self.active_axon_beams:
            axon_type = beam.get('axon_type', 'UNKNOWN')
            
            # === HANDLE NEIGHBOR AXONS (rose gold zap) ===
            if 'NEIGHBOR' in str(axon_type).upper():
                self._draw_neighbor_zap(beam, current_time)
                continue
            
            # === HANDLE VOID AXONS (purple branching) ===
            if 'VOID' in str(axon_type).upper():
                self._draw_void_branches(beam, current_time)
                continue
            
            # === HANDLE HASH AXONS (confidence-based projectiles) ===
            source_coord = beam.get('source_coord')
            target_coord = beam.get('target_coord')
            
            # Get screen positions
            source_pos = self._coord_to_screen(source_coord) if source_coord else None
            target_pos = self._coord_to_screen(target_coord) if target_coord else None
            
            # Skip if we don't have valid positions
            if not source_pos or not target_pos:
                continue
            
            # Get axon properties
            confidence = beam.get('confidence', 0.5)
            start_time = beam.get('start_time', current_time)
            duration = 1.5
            
            # Calculate progress
            elapsed = current_time - start_time
            progress = min(1.0, elapsed / duration)
            
            # === CONFIDENCE-BASED COLOR MAPPING ===
            if confidence >= 0.8:
                base_color = AXON_COLORS['HASH_CONF_4']  # Bright Green
            elif confidence >= 0.6:
                base_color = AXON_COLORS['HASH_CONF_3']  # Bright Blue
            elif confidence >= 0.4:
                base_color = AXON_COLORS['HASH_CONF_2']  # Bright Yellow
            elif confidence >= 0.2:
                base_color = AXON_COLORS['HASH_CONF_1']  # Bright Red
            else:
                base_color = AXON_COLORS['HASH_CONF_0']  # Gray
            
            # Make projectile lively with pulsating size
            pulse = 0.8 + 0.4 * math.sin(current_time * 8.0)
            head_size = max(2, int(5 * confidence * self.zoom * pulse))
            
            # Projectile position along path
            head_x = source_pos[0] + (target_pos[0] - source_pos[0]) * progress
            head_y = source_pos[1] + (target_pos[1] - source_pos[1]) * progress
            
            # Draw lively projectile with trail
            for i in range(3):  # 3-part trail
                trail_progress = max(0.0, progress - (i * 0.1))
                trail_x = source_pos[0] + (target_pos[0] - source_pos[0]) * trail_progress
                trail_y = source_pos[1] + (target_pos[1] - source_pos[1]) * trail_progress
                
                trail_alpha = int(150 * (1.0 - i * 0.3) * (1.0 - progress * 0.5))
                trail_color = (*base_color, trail_alpha)
                trail_size = max(1, int(head_size * (1.0 - i * 0.4)))
                
                pygame.draw.circle(self.screen, trail_color, 
                                (int(trail_x), int(trail_y)), trail_size)
            
            # Draw main projectile head
            head_color = (*base_color, 200)
            pygame.draw.circle(self.screen, head_color, 
                            (int(head_x), int(head_y)), head_size)
            
            # ABSORB ANIMATION at target when progress > 0.9
            if progress > 0.9:
                absorb_progress = (progress - 0.9) / 0.1
                
                # Shrinking circle that covers neuron
                absorb_size = int(head_size * (1.0 - absorb_progress))
                absorb_alpha = int(180 * (1.0 - absorb_progress))
                absorb_color = (*base_color, absorb_alpha)
                
                if absorb_size > 0:
                    pygame.draw.circle(self.screen, absorb_color, 
                                    target_pos, absorb_size)


    def _draw_neighbor_zap(self, beam, current_time):
        """Draw neighbor detection as thin, smooth rose gold electric zap"""
        source_coord = beam.get('source_coord')
        target_coord = beam.get('target_coord')
        
        if not source_coord or not target_coord:
            return
        
        source_pos = self._coord_to_screen(source_coord)
        target_pos = self._coord_to_screen(target_coord)
        
        if not source_pos or not target_pos:
            return
        
        # If source and target are the same position, skip
        if source_pos == target_pos:
            return
        
        start_time = beam.get('start_time', current_time)
        duration = 0.4  # Shorter, quicker zap (was 0.5)
        
        elapsed = current_time - start_time
        progress = min(1.0, elapsed / duration)
        
        # ROSE GOLD colors (ALWAYS same for neighbor detection)
        rose_gold_main = (183, 110, 121)     # Main rose gold
        rose_gold_light = (255, 180, 190)    # Light rose gold for glow
        rose_gold_spark = (255, 200, 180)    # Spark highlight
        
        # Zap is only visible during first 60% of duration (quicker)
        if progress > 0.6:
            return
        
        # Calculate main zap line with smoother, thinner lightning
        zap_points = []
        dx = target_pos[0] - source_pos[0]
        dy = target_pos[1] - source_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Safety check for zero distance
        if distance == 0:
            return
        
        # Create smoother lightning path with fewer segments
        num_segments = max(2, int(distance / 20))  # Fewer segments for smoother line
        zap_points.append(source_pos)
        
        for i in range(1, num_segments):
            t = i / num_segments
            base_x = source_pos[0] + dx * t
            base_y = source_pos[1] + dy * t
            
            if i < num_segments - 1:
                perp_x = -dy / distance
                perp_y = dx / distance
                # Smoother, smaller offset
                offset = math.sin(current_time * 15 + i) * 6 * (1.0 - t) * (1.0 - progress)
                jag_x = base_x + perp_x * offset
                jag_y = base_y + perp_y * offset
            else:
                jag_x = base_x
                jag_y = base_y
            
            zap_points.append((int(jag_x), int(jag_y)))
        
        zap_points.append(target_pos)
        
        # Draw THINNER main rose gold lightning bolt
        bolt_width = max(1, int(2 * self.zoom))  # Thinner (was 4)
        for j in range(len(zap_points) - 1):
            pygame.draw.line(self.screen, rose_gold_main, 
                            zap_points[j], zap_points[j+1], bolt_width)
        
        # Draw inner white-hot core (thinner)
        core_width = max(1, int(1 * self.zoom))  # Thinner (was 2)
        for j in range(len(zap_points) - 1):
            pygame.draw.line(self.screen, (255, 240, 220),
                            zap_points[j], zap_points[j+1], core_width)
        
        # Rose gold glow around bolt (thinner, more transparent)
        glow_width = max(1, int(2 * self.zoom))  # Thinner (was 3)
        glow_alpha = int(60 * (1.0 - progress))  # More transparent (was 80)
        for j in range(len(zap_points) - 1):
            temp_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            pygame.draw.line(temp_surface, (*rose_gold_light, glow_alpha),
                            zap_points[j], zap_points[j+1], glow_width)
            self.screen.blit(temp_surface, (0, 0))
        
        # Fewer, smaller rose gold spark particles
        spark_count = 4  # Reduced from 8
        for i in range(spark_count):
            spark_angle = random.random() * math.pi * 2
            spark_dist = 5 * (1.0 - progress) * self.zoom  # Smaller (was 8)
            spark_x = source_pos[0] + math.cos(spark_angle) * spark_dist
            spark_y = source_pos[1] + math.sin(spark_angle) * spark_dist
            spark_size = max(1, int(2 * (1.0 - progress) * self.zoom))  # Smaller (was 3)
            spark_alpha = int(180 * (1.0 - progress))  # More transparent
            
            pygame.draw.circle(self.screen, (*rose_gold_spark, spark_alpha),
                            (int(spark_x), int(spark_y)), spark_size)
            
            if progress > 0.2:  # Earlier target sparks
                spark_angle2 = random.random() * math.pi * 2
                spark_dist2 = 5 * progress * self.zoom  # Smaller
                spark_x2 = target_pos[0] + math.cos(spark_angle2) * spark_dist2
                spark_y2 = target_pos[1] + math.sin(spark_angle2) * spark_dist2
                spark_size2 = max(1, int(2 * progress * self.zoom))  # Smaller
                spark_alpha2 = int(180 * progress)  # More transparent
                
                pygame.draw.circle(self.screen, (*rose_gold_spark, spark_alpha2),
                                (int(spark_x2), int(spark_y2)), spark_size2)

    def _draw_void_branches(self, beam, current_time):
        """Draw void axon as branching trails that dissipate outward"""
        source_coord = beam.get('source_coord')
        if not source_coord:
            return
        
        source_pos = self._coord_to_screen(source_coord)
        if not source_pos:
            return
        
        start_time = beam.get('start_time', current_time)
        duration = 2.0
        
        elapsed = current_time - start_time
        progress = min(1.0, elapsed / duration)
        
        # Void color (purple)
        void_color = AXON_COLORS.get('COORDINATE_VOID', (180, 100, 255))
        
        # Create 5-8 branching trails
        num_branches = 8
        max_branch_length = 30 * self.zoom
        
        for i in range(num_branches):
            # Calculate branch angle and length
            branch_angle = (i / num_branches) * math.pi * 2
            branch_length = max_branch_length * progress
            
            # Add slight wobble to branches
            wobble = math.sin(current_time * 5 + i) * 0.3
            current_angle = branch_angle + wobble
            
            # Branch end position
            end_x = source_pos[0] + math.cos(current_angle) * branch_length
            end_y = source_pos[1] + math.sin(current_angle) * branch_length
            
            # Branch color fades as it extends
            branch_alpha = int(180 * (1.0 - progress))
            branch_color = (*void_color, branch_alpha)
            
            # Draw main branch line
            branch_width = max(1, int(2 * (1.0 - progress) * self.zoom))
            pygame.draw.line(self.screen, branch_color, 
                            source_pos, (int(end_x), int(end_y)), branch_width)

    def _draw_graph_hover_info(self):
        """Draw hover info for graphs"""
        if hasattr(self, 'hovered_button') and self.hovered_button:
            # Simple tooltip for buttons
            pass

    def _draw_graph_navigation(self):
        """Draw graph navigation controls"""
        if len(self.graph_sets.get(self.stats_graph_mode, [])) > 4:
            # Draw navigation arrows if there are more than 4 graphs
            nav_text = f"Use ← → to navigate graphs"
            nav_surf = self.small_font.render(nav_text, True, (180, 200, 255))
            nav_rect = nav_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
            self.screen.blit(nav_surf, nav_rect)

    def _draw_neurons(self):
        """Draw neurons with outer pattern circle and inner pulsing dot - ORIGINAL DESIGN"""
        if not self.active_neurons:
            return
        
        current_time = time.time()
        
        for coord, neuron_data in self.active_neurons.items():
            screen_pos = self._coord_to_screen(coord)
            if not screen_pos:
                continue
            
            # ===== 1. OUTER CIRCLE - PATTERN COLOR =====
            pattern = neuron_data.get('pattern', 'UNKNOWN')
            pattern_color = PATTERN_COLORS.get(pattern, (200, 200, 200))
            
            # Outer circle size based on confidence
            base_size = 6.0
            confidence = neuron_data.get('confidence', neuron_data.get('similarity', 0.5))
            outer_size = int(base_size * (0.8 + confidence * 0.4) * self.zoom)
            
            # Draw outer circle (pattern color)
            pygame.draw.circle(self.screen, pattern_color, screen_pos, outer_size)
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, outer_size, 1)
            
            # ===== 2. INNER PULSING DOT - EIGEN STATE COLOR =====
            state = neuron_data.get('current_state', 'UNKNOWN')
            
            # Get state index (default to UNKNOWN if not found)
            state_idx = self.state_indices.get(state, self.state_indices['UNKNOWN'])
            freq = self.state_freqs.get(state, self.state_freqs['UNKNOWN'])
            
            # Calculate which color in the cycle to use
            cycle_time = current_time % (1.0 / freq)
            color_index = int(cycle_time * freq * 1000) % (1000 // freq)
            
            # Get RGB values from array
            r = self.color_array[0, state_idx, color_index]
            g = self.color_array[1, state_idx, color_index]
            b = self.color_array[2, state_idx, color_index]
            
            # Inner dot is 40% of outer radius
            inner_size = max(1, int(outer_size * 0.4))
            
            # Apply confidence brightness
            brightness = 0.5 + 0.5 * confidence
            final_color = (
                min(255, int(r * brightness)),
                min(255, int(g * brightness)),
                min(255, int(b * brightness))
            )
            
            # Draw the glowing inner dot
            pygame.draw.circle(self.screen, final_color, screen_pos, inner_size)

    def get_animation_sequences(self):
        """Get all animation sequences"""
        return self.animation_sequences

    def draw(self):
        """Main drawing method"""
        # Clear background
        self.screen.fill((10, 10, 20))
        
        if self.mode == self.MODE_BROWSER:
            self._draw_browser()
            pygame.display.flip()
            return
            
        elif self.mode == self.MODE_LOADING:
            self._draw_loading_screen()
            pygame.display.flip()
            return
        
        # ===== SCREEN SWITCHING =====
        if self.screen_mode == "stats_view":
            self._draw_statistics_screen()
            pygame.display.flip()
            return
        
        # ===== NEURON VIEW =====
        if self.show_grid:
            self._draw_grid()
        
        self._draw_connections()
        self._draw_neurons()
        
        if self.show_axons:
            self._draw_axon_comets()
        
        if self.show_processing_states:
            self._draw_inner_dots()
        
        # Draw state and pattern change effects
        if self.show_change_highlights:
            self._draw_state_change_highlights()
        
        # ===== PYGAME UI (ON TOP) =====
        if self.zoom >= 0.8:
            self._draw_neuron_labels()
        
        if self.hovered_neuron_id:
            self._draw_hover_info()
        
        self._draw_ui_panel()
        
        if self.show_legend:
            self._draw_updated_legend()
        
        if self.focused_neuron_id:
            self._draw_focused_info()
        
        self._draw_ui_buttons()
        self._draw_logs()
        
        if self.mode == self.MODE_REPLAY:
            self._draw_timeline_controls()
        
        pygame.display.flip()

    def run(self):
        """Main visualizer loop"""
        print("🧠 NEXUS VISUALIZER - MAIN LOOP")
        print("=" * 60)
        
        # Initialize based on mode
        if self.mode == self.MODE_BROWSER:
            print("🔄 Entering browser mode initialization")
            # Scan for sessions
            session_count = self.browser.scan_sessions()
            print(f"📁 Found {session_count} sessions")
            if session_count == 0:
                self._add_log("No Nexus sessions found. Create one in Cognition/ directory.")
        elif self.mode == self.MODE_LIVE and self.session_id:
            print(f"🔄 Entering live mode for session: {self.session_id}")
            # For live mode, check if we have any initial data
            if self.timeline_builder and hasattr(self.timeline_builder, 'animation_sequences'):
                self.animation_sequences = self.timeline_builder.animation_sequences
                if self.animation_sequences:
                    self._load_current_sequence(self.animation_sequences[0])
                    if hasattr(self, 'timeline'):
                        self.timeline.load_frames(self.animation_sequences)
                    print(f"🚀 Loaded {len(self.animation_sequences)} initial frames")
        else:
            print(f"🔄 Starting in mode: {self.mode}")
        
        print("🎬 Entering main loop")
        frame_count = 0
        
        try:
            # Main loop
            while self.running:
                frame_count += 1
                
                # Handle events
                for event in pygame.event.get():
                    self.handle_events_single(event)
                
                # Update state
                self.update()
                
                # Draw everything
                self.draw()
                
                # Cap frame rate
                self.clock.tick(self.target_fps)
                
        except Exception as e:
            print(f"❌ Exception in main loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Cleanup
            print("🧹 Cleaning up resources...")
            pygame.quit()
            print("✅ Cleanup complete")
            print(f"📊 Total frames rendered: {frame_count}")

    # ===== SESSION MANAGEMENT =====
    
    def _load_current_sequence(self, sequence: Dict):
        """Load and activate an animation sequence"""
        if not sequence:
            return
        
        self.current_sequence = sequence
        self.animation_start_time = time.time()
        
        # Clear previous state
        self.active_neurons.clear()
        self.active_axon_beams.clear()
        self.active_particles.clear()
        self.neurons.clear()
        self.coordinate_map.clear()
        
        # Load neuron states from sequence
        for neuron_anim in sequence.get('neuron_animations', []):
            coord = neuron_anim.get('coordinate')
            if coord:
                coord_tuple = tuple(coord) if isinstance(coord, list) else coord
                self.active_neurons[coord_tuple] = neuron_anim
                
                # Also populate neurons dict for connections
                neuron_id = neuron_anim.get('neuron_id', 'unknown')
                visual_neuron = VisualNeuron(
                    id=neuron_id,
                    coordinate=coord_tuple,
                    pattern=neuron_anim.get('pattern', 'UNKNOWN'),
                    state=neuron_anim.get('current_state', 'UNKNOWN'),
                    similarity=neuron_anim.get('confidence', 0.5)
                )
                self.neurons[neuron_id] = visual_neuron
                self.coordinate_map[coord_tuple] = neuron_id
        
        # Load axon beams
        for axon_anim in sequence.get('axon_animations', []):
            self.active_axon_beams.append({
                **axon_anim,
                'start_time': time.time(),
                'progress': 0.0
            })
        
        # Load particle animations
        for particle_anim in sequence.get('particle_animations', []):
            self.active_particles.append({
                **particle_anim,
                'start_time': time.time(),
                'progress': 0.0
            })
        self._update_cumulative_stats(sequence)
    
    def _update_cumulative_stats(self, sequence: Dict):
        """Update cumulative statistics from sequence"""
        frame_num = sequence.get('frame', 0)
        
        # Count axons in this frame
        frame_axons = len(sequence.get('axon_animations', []))
        
        # Count axon types
        frame_hashes = sum(1 for a in sequence.get('axon_animations', []) 
                        if 'HASH' in str(a.get('axon_type', '')).upper())
        frame_voids = sum(1 for a in sequence.get('axon_animations', [])
                        if 'VOID' in str(a.get('axon_type', '')).upper())
        frame_neighbors = sum(1 for a in sequence.get('axon_animations', [])
                            if 'NEIGHBOR' in str(a.get('axon_type', '')).upper())
        
        # Initialize missing keys if they don't exist
        if 'total_hashes' not in self.cumulative_stats:
            self.cumulative_stats['total_hashes'] = 0
        if 'total_voids' not in self.cumulative_stats:
            self.cumulative_stats['total_voids'] = 0
        if 'total_neighbors' not in self.cumulative_stats:
            self.cumulative_stats['total_neighbors'] = 0
        if 'total_cycles' not in self.cumulative_stats:
            self.cumulative_stats['total_cycles'] = 0
        if 'neuron_activity' not in self.cumulative_stats:
            self.cumulative_stats['neuron_activity'] = {}
        
        # Update cumulative totals
        self.cumulative_stats['total_cycles'] += frame_axons
        self.cumulative_stats['total_hashes'] += frame_hashes
        self.cumulative_stats['total_voids'] += frame_voids
        self.cumulative_stats['total_neighbors'] += frame_neighbors
        
        # Track neuron activity
        for neuron_anim in sequence.get('neuron_animations', []):
            neuron_id = neuron_anim.get('neuron_id')
            if neuron_id:
                if neuron_id not in self.cumulative_stats['neuron_activity']:
                    self.cumulative_stats['neuron_activity'][neuron_id] = {
                        'first_seen': frame_num,
                        'last_seen': frame_num,
                        'state_history': [],
                        'hash_count': 0,
                        'void_count': 0
                    }
                
                activity = self.cumulative_stats['neuron_activity'][neuron_id]
                activity['last_seen'] = frame_num
                activity['state_history'].append({
                    'frame': frame_num,
                    'state': neuron_anim.get('current_state', 'UNKNOWN'),
                    'confidence': neuron_anim.get('confidence', 0.5)
                })
        
        # Count axons per neuron in this frame
        for axon_anim in sequence.get('axon_animations', []):
            axon_type = axon_anim.get('axon_type', '')
            source_info = axon_anim.get('source_info', {}) or axon_anim.get('source', {})
            source_id = source_info.get('id')
            
            if source_id and source_id in self.cumulative_stats['neuron_activity']:
                activity = self.cumulative_stats['neuron_activity'][source_id]
                if 'HASH' in str(axon_type).upper():
                    activity['hash_count'] += 1
                elif 'VOID' in str(axon_type).upper():
                    activity['void_count'] += 1
        
        # Store frame history
        frame_data = {
            'frame': frame_num,
            'neurons': len(sequence.get('neuron_animations', [])),
            'axons': frame_axons,
            'hashes': frame_hashes,
            'voids': frame_voids,
            'neighbors': frame_neighbors
        }
        
        if 'frame_history' not in self.cumulative_stats:
            self.cumulative_stats['frame_history'] = deque(maxlen=100)
        self.cumulative_stats['frame_history'].append(frame_data)  

    def _load_current_sequence(self, sequence: Dict):
        """Load TimelineBuilder sequence format"""
        if not sequence:
            return
        
        self.current_sequence = sequence
        self.animation_start_time = time.time()
        
        # Clear previous state
        self.active_neurons.clear()
        self.active_axon_beams.clear()
        self.neurons.clear()
        self.coordinate_map.clear()
        
        # ===== LOAD NEURONS FROM TIMELINEBUILDER FORMAT =====
        neurons_data = sequence.get('neurons', [])  # TimelineBuilder uses LIST, not dict!
        axons_data = sequence.get('axons', [])
        
        # Load neurons
        for neuron_data in neurons_data:
            coord = neuron_data.get('coordinate')
            if not coord:
                continue
            
            coord_tuple = tuple(coord) if isinstance(coord, list) else coord
            neuron_id = neuron_data.get('neuron_id', f'neuron_{len(self.neurons)}')
            
            # Store in active_neurons
            self.active_neurons[coord_tuple] = neuron_data
            
            # Create VisualNeuron
            visual_neuron = VisualNeuron(
                id=neuron_id,
                coordinate=coord_tuple,
                pattern=neuron_data.get('pattern', 'UNKNOWN'),
                state=neuron_data.get('current_state', 'UNKNOWN'),  # Note: current_state not state
                similarity=neuron_data.get('confidence', 0.5),
                processing_phase=neuron_data.get('processing_phase', 'UNKNOWN'),
                cycle=neuron_data.get('cycle', 0),
                heartbeat_data=neuron_data  # Store full data for hover
            )
            self.neurons[neuron_id] = visual_neuron
            self.coordinate_map[coord_tuple] = neuron_id
        
        # ===== LOAD AXONS =====
        for axon in axons_data:
            axon_type = axon.get('axon_type', 'UNKNOWN')
            source = axon.get('source', {})
            
            axon_beam = {
                'axon_type': axon_type,
                'source_coord': tuple(source.get('coordinate', (0, 0))) if source.get('coordinate') else None,
                'target_coord': tuple(axon.get('target', {}).get('coordinate', (0, 0))) 
                            if axon.get('target') and axon['target'].get('coordinate') else None,
                'confidence': axon.get('data', {}).get('confidence', 0.5),
                'start_time': time.time(),
                'progress': 0.0
            }
            
            self.active_axon_beams.append(axon_beam)
        
        # Update frame counter
        self.current_sequence_index = sequence.get('frame', 0)
        
        # Update 3 eigen tracking
        self._update_3eigen_tracking(sequence)
        
        # Update hover system
        if self.hovered_neuron_id:
            self._update_hover_info()
        
        print(f"📥 Loaded TimelineBuilder frame {self.current_sequence_index}")


    def _draw_updated_legend(self):
        """Draw legend with scaled-down pulsing using the same array logic"""
        if self.legend_change_mode:
            # Gray out the background when in change mode
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
        
        # Use current legend position and size
        panel_width, panel_height = self.legend_size
        panel_x, panel_y = self.legend_position
        
        # Create legend panel with draggable title bar
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        # Draw main panel
        pygame.draw.rect(panel_surf, (20, 20, 40, 240), 
                        panel_surf.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surf, (80, 80, 120, 150),
                        panel_surf.get_rect(), 2, border_radius=8)
        
        # Draw draggable title bar
        title_bar_height = 35
        title_bar_color = (40, 40, 70, 200) if not self.legend_dragging else (60, 60, 100, 200)
        pygame.draw.rect(panel_surf, title_bar_color, 
                        (0, 0, panel_width, title_bar_height), border_top_left_radius=8, border_top_right_radius=8)
        
        # Draw resize handle in bottom right corner
        resize_handle_size = 20
        resize_color = (100, 120, 180, 180) if not self.legend_resizing else (140, 160, 220, 200)
        pygame.draw.rect(panel_surf, resize_color,
                        (panel_width - resize_handle_size, panel_height - resize_handle_size,
                        resize_handle_size, resize_handle_size), border_bottom_right_radius=8)
        
        # Draw resize handle icon (corner lines)
        pygame.draw.line(panel_surf, (200, 220, 255),
                        (panel_width - 15, panel_height - 8),
                        (panel_width - 8, panel_height - 8), 2)
        pygame.draw.line(panel_surf, (200, 220, 255),
                        (panel_width - 8, panel_height - 15),
                        (panel_width - 8, panel_height - 8), 2)
        
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        # Store legend rect for mouse interaction
        self.legend_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.legend_title_rect = pygame.Rect(panel_x, panel_y, panel_width, title_bar_height)
        self.legend_resize_rect = pygame.Rect(panel_x + panel_width - resize_handle_size,
                                            panel_y + panel_height - resize_handle_size,
                                            resize_handle_size, resize_handle_size)
        
        # Draw title text
        title = self.font.render("NEXUS 25D VISUALIZER", True, (255, 255, 200))
        self.screen.blit(title, (panel_x + 15, panel_y + 8))
        
        # Draw change mode button
        change_button_width = 80
        change_button_x = panel_x + panel_width - change_button_width - 10
        change_button_y = panel_y + 5
        change_button_height = 25
        
        # Draw change dimensions button
        change_button_color = (60, 80, 160) if not self.legend_change_mode else (100, 120, 200)
        change_border_color = (80, 100, 180) if not self.legend_change_mode else (120, 140, 220)
        
        change_button_rect = pygame.Rect(change_button_x, change_button_y, change_button_width, change_button_height)
        self.legend_change_button = change_button_rect
        
        pygame.draw.rect(self.screen, change_button_color, change_button_rect, border_radius=4)
        pygame.draw.rect(self.screen, change_border_color, change_button_rect, 1, border_radius=4)
        
        button_text = "CHANGE" if not self.legend_change_mode else "DONE"
        text_color = (220, 220, 240) if not self.legend_change_mode else (240, 240, 255)
        button_surf = self.small_font.render(button_text, True, text_color)
        button_text_rect = button_surf.get_rect(center=change_button_rect.center)
        self.screen.blit(button_surf, button_text_rect)
        
        # Draw close button (X)
        close_button_size = 20
        close_button_x = panel_x + panel_width - close_button_size - 10
        close_button_y = panel_y + 8
        close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
        self.legend_close_button = close_button_rect
        
        # Draw close button
        close_color = (180, 80, 80)
        pygame.draw.rect(self.screen, close_color, close_button_rect, border_radius=3)
        pygame.draw.rect(self.screen, (220, 100, 100), close_button_rect, 1, border_radius=3)
        
        # Draw X
        pygame.draw.line(self.screen, (255, 255, 255),
                        (close_button_x + 5, close_button_y + 5),
                        (close_button_x + close_button_size - 5, close_button_y + close_button_size - 5), 2)
        pygame.draw.line(self.screen, (255, 255, 255),
                        (close_button_x + close_button_size - 5, close_button_y + 5),
                        (close_button_x + 5, close_button_y + close_button_size - 5), 2)
        
        y_offset = panel_y + 40  # Start after title bar
        
        # EIGEN STATES SECTION - SCALED DOWN FREQUENCIES (1/2 speed)
        eigen_title = self.small_font.render("EIGEN STATES (Pulsing):", True, (255, 255, 180))
        self.screen.blit(eigen_title, (panel_x + 15, y_offset))
        y_offset += 25
        
        current_time = time.time()
        
        # Scale factor for legend (slower than actual neurons)
        SCALE_FACTOR = 0.5  # Half speed for legend
        
        eigen_states = [
            ('STABLE', 0),
            ('LEARNING', 1),
            ('NOISY', 2),
            ('RIGID', 3),
            ('CONFUSED', 4),
            ('DEAD', 5),
            ('UNKNOWN', 6),
        ]
        
        # Calculate column layout based on legend width
        column_width = panel_width // 2 - 20
        state_items_per_column = (len(eigen_states) + 1) // 2
        
        for i, (state_name, state_idx) in enumerate(eigen_states):
            # Determine column
            col = 0 if i < state_items_per_column else 1
            row = i if col == 0 else i - state_items_per_column
            
            state_x = panel_x + 20 + (col * column_width)
            state_y = y_offset + row * 30
            
            # Get the state's frequency
            freq = self.state_freqs.get(state_name, self.state_freqs['UNKNOWN'])
            
            # Calculate scaled position in cycle (0 to 1)
            scaled_freq = freq * SCALE_FACTOR
            cycle_time = current_time % (1.0 / scaled_freq)
            cycle_position = cycle_time * scaled_freq  # 0 to 1
            
            # Map to array index (0 to 999)
            color_index = int(cycle_position * 1000) % 1000
            
            # Get color from array
            r = self.color_array[0, state_idx, color_index]
            g = self.color_array[1, state_idx, color_index]
            b = self.color_array[2, state_idx, color_index]
            
            pulse_color = (r, g, b)
            
            # Draw pulsing circle
            circle_radius = 6
            circle_x = state_x
            circle_y = state_y + circle_radius
            
            # Outer circle (base color - index 0 from array)
            base_r = self.color_array[0, state_idx, 0]
            base_g = self.color_array[1, state_idx, 0]
            base_b = self.color_array[2, state_idx, 0]
            base_color = (base_r, base_g, base_b)
            
            pygame.draw.circle(self.screen, base_color, (circle_x, circle_y), circle_radius)
            pygame.draw.circle(self.screen, (255, 255, 255), (circle_x, circle_y), circle_radius, 1)
            
            # Pulsing inner dot
            inner_radius = circle_radius * 0.4
            pygame.draw.circle(self.screen, pulse_color, (circle_x, circle_y), int(inner_radius))
            
            # State name
            name_surf = self.small_font.render(state_name, True, (200, 220, 255))
            self.screen.blit(name_surf, (state_x + 15, state_y))
        
        y_offset += state_items_per_column * 30 + 15
        
        # NEURON PATTERNS SECTION - SIMPLIFIED
        pattern_title = self.small_font.render("NEURON PATTERNS (Outer Circle):", True, (255, 255, 180))
        self.screen.blit(pattern_title, (panel_x + 15, y_offset))
        y_offset += 25
        
        # SIMPLE abbreviations only
        patterns = [
            ("ACT", PATTERN_COLORS['ACTION_ELEMENT']),
            ("DATA", PATTERN_COLORS['DATA_INPUT']),
            ("CTX", PATTERN_COLORS['CONTEXT_ELEMENT']),
            ("STR", PATTERN_COLORS['STRUCTURAL']),
            ("NEX", PATTERN_COLORS['NEXUS']),
            ("UNK", PATTERN_COLORS['UNKNOWN']),
        ]
        
        # Calculate columns for patterns
        patterns_per_column = (len(patterns) + 1) // 2
        pattern_col_width = column_width
        
        for i, (pattern_name, color) in enumerate(patterns):
            col = 0 if i < patterns_per_column else 1
            row = i if col == 0 else i - patterns_per_column
            
            pattern_x = panel_x + 20 + (col * pattern_col_width)
            pattern_y = y_offset + row * 25
            
            # Draw neuron example
            circle_radius = 6
            pygame.draw.circle(self.screen, color, (pattern_x, pattern_y + circle_radius), circle_radius)
            pygame.draw.circle(self.screen, (255, 255, 255), (pattern_x, pattern_y + circle_radius), circle_radius, 1)
            
            # Draw gray inner dot (standard)
            inner_radius = circle_radius * 0.4
            pygame.draw.circle(self.screen, (150, 150, 150), (pattern_x, pattern_y + circle_radius), int(inner_radius))
            
            # Pattern abbreviation only
            name_surf = self.small_font.render(pattern_name, True, (200, 220, 255))
            self.screen.blit(name_surf, (pattern_x + 15, pattern_y + 3))
        
        y_offset += patterns_per_column * 25 + 15
        
        # HASH CONFIDENCE SECTION
        axon_title = self.small_font.render("HASH CONFIDENCE (Axon Colors):", True, (255, 255, 180))
        self.screen.blit(axon_title, (panel_x + 15, y_offset))
        y_offset += 25
        
        confidence_levels = [
            ("0-20%", AXON_COLORS['HASH_CONF_0']),
            ("20-40%", AXON_COLORS['HASH_CONF_1']),
            ("40-60%", AXON_COLORS['HASH_CONF_2']),
            ("60-80%", AXON_COLORS['HASH_CONF_3']),
            ("80-100%", AXON_COLORS['HASH_CONF_4']),
        ]
        
        for i, (label, color) in enumerate(confidence_levels):
            axon_y = y_offset + i * 20
            
            # Draw axon color dot
            pygame.draw.circle(self.screen, color, (panel_x + 20, axon_y + 10), 5)
            pygame.draw.circle(self.screen, (255, 255, 255), (panel_x + 20, axon_y + 10), 5, 1)
            
            # Confidence label
            label_surf = self.small_font.render(label, True, (200, 220, 240))
            self.screen.blit(label_surf, (panel_x + 35, axon_y + 3))
        
        y_offset += len(confidence_levels) * 20 + 10
        
        # SPECIAL ANIMATIONS SECTION - SIMPLIFIED
        special_title = self.small_font.render("SPECIAL ANIMATIONS:", True, (255, 255, 180))
        self.screen.blit(special_title, (panel_x + 15, y_offset))
        y_offset += 25
        
        special_animations = [
            ('⚡ Neighbor', (183, 110, 121)),  # Rose gold
            ('✱ Void', (180, 100, 255)),      # Purple
        ]
        
        for i, (symbol, color) in enumerate(special_animations):
            anim_y = y_offset + i * 24
            
            if symbol.startswith('⚡'):
                # Simple lightning bolt
                bolt_points = [
                    (panel_x + 20, anim_y + 5),
                    (panel_x + 24, anim_y + 10),
                    (panel_x + 22, anim_y + 10),
                    (panel_x + 26, anim_y + 15),
                    (panel_x + 22, anim_y + 15),
                    (panel_x + 24, anim_y + 20),
                ]
                pygame.draw.lines(self.screen, color, False, bolt_points, 3)
            elif symbol.startswith('✱'):
                # Simple void star
                for angle in [0, 72, 144, 216, 288]:
                    rad = math.radians(angle)
                    end_x = panel_x + 20 + math.cos(rad) * 6
                    end_y = anim_y + 10 + math.sin(rad) * 6
                    pygame.draw.line(self.screen, color,
                                (panel_x + 20, anim_y + 10),
                                (end_x, end_y), 2)
            
            # Label
            label = symbol.split()[1]  # Get "Neighbor" or "Void"
            label_surf = self.small_font.render(label, True, (180, 200, 220))
            self.screen.blit(label_surf, (panel_x + 40, anim_y))
        
        y_offset += len(special_animations) * 24 + 10
        
        # STATISTICS SECTION (if in replay mode)
        if self.mode == self.MODE_REPLAY and self.animation_sequences and y_offset < panel_y + panel_height - 50:
            stats_title = self.small_font.render("FRAME STATISTICS:", True, (255, 255, 180))
            self.screen.blit(stats_title, (panel_x + 15, y_offset))
            y_offset += 25
            
            stats = [
                f"Frame: {self.current_sequence_index + 1}/{len(self.animation_sequences)}",
                f"Neurons: {len(self.active_neurons)}",
                f"Axons: {len(self.active_axon_beams)}",
                f"Playback: {'▶' if self.timeline.is_playing else '‖'} {self.timeline.playback_speed:.1f}x",
                f"Zoom: {self.zoom:.1f}x",
            ]
            
            for stat in stats:
                stat_surf = self.small_font.render(stat, True, (200, 220, 255))
                self.screen.blit(stat_surf, (panel_x + 25, y_offset))
                y_offset += 20

    def _draw_browser(self):
        """Draw session browser with clickable sessions"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        panel_width = 800
        panel_height = 600
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        pygame.draw.rect(self.screen, (30, 30, 50), 
                        (panel_x, panel_y, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, (80, 80, 120), 
                        (panel_x, panel_y, panel_width, panel_height), 3, border_radius=10)
        
        title = self.title_font.render("NEXUS SESSION BROWSER", True, (255, 255, 200))
        title_rect = title.get_rect(center=(self.screen_width // 2, panel_y + 40))
        self.screen.blit(title, title_rect)
        
        refresh_rect = pygame.Rect(panel_x + panel_width - 100, panel_y + 30, 80, 30)
        
        if self.hovered_button == 'browser_refresh':
            refresh_color = (70, 90, 170)
            border_color = (100, 120, 200)
            text_color = (240, 240, 255)
        else:
            refresh_color = (60, 80, 160)
            border_color = (80, 100, 180)
            text_color = (220, 220, 240)
        
        pygame.draw.rect(self.screen, refresh_color, refresh_rect, border_radius=5)
        pygame.draw.rect(self.screen, border_color, refresh_rect, 1, border_radius=5)
        
        refresh_text = self.small_font.render("REFRESH", True, text_color)
        refresh_text_rect = refresh_text.get_rect(center=refresh_rect.center)
        self.screen.blit(refresh_text, refresh_text_rect)
        
        self.ui_buttons['browser_refresh'] = {
            'rect': refresh_rect,
            'label': 'REFRESH',
            'tooltip': 'Refresh session list'
        }
        
        instructions = [
            "UP/DOWN: Navigate sessions",
            "ENTER or Double-Click: Load session for replay",
            "Click: Select session",
            "ESC: Back to live view",
            "R: Refresh list",
        ]
        
        for i, text in enumerate(instructions):
            instr_surf = self.small_font.render(text, True, (180, 200, 255))
            instr_rect = instr_surf.get_rect(topleft=(panel_x + 20, panel_y + panel_height - 100 + i * 20))
            self.screen.blit(instr_surf, instr_rect)
        
        if not self.browser.sessions:
            no_sessions = self.font.render("No Nexus sessions found", True, (200, 200, 200))
            no_rect = no_sessions.get_rect(center=(self.screen_width // 2, panel_y + 150))
            self.screen.blit(no_sessions, no_rect)
            return
        
        start_idx = self.browser.scroll_offset
        end_idx = min(start_idx + self.browser.visible_items, len(self.browser.sessions))
        
        list_y = panel_y + 100
        item_height = 50
        
        for i in range(start_idx, end_idx):
            session = self.browser.sessions[i]
            is_selected = (i == self.browser.selected_index)
            is_hovered = (i == self.hovered_session_index)
            
            item_rect = pygame.Rect(panel_x + 30, list_y, panel_width - 60, item_height - 5)
            
            if is_hovered and not is_selected:
                item_color = (70, 90, 140)
            elif is_selected:
                item_color = (80, 100, 180)
            else:
                item_color = (40, 50, 80)
            
            pygame.draw.rect(self.screen, item_color, item_rect, border_radius=5)
            
            if is_selected:
                pygame.draw.rect(self.screen, (100, 180, 255), item_rect, 2, border_radius=5)
            
            if is_hovered and not is_selected:
                pygame.draw.rect(self.screen, (100, 120, 180, 50), item_rect, 1, border_radius=5)
            
            id_text = session['id'][:40] + ("..." if len(session['id']) > 40 else "")
            id_color = (220, 220, 255) if is_selected else (180, 180, 220)
            id_surf = self.font.render(id_text, True, id_color)
            id_rect = id_surf.get_rect(topleft=(panel_x + 40, list_y + 8))
            self.screen.blit(id_surf, id_rect)
            
            info_parts = []
            if session.get('neuron_count', 0) > 0:
                info_parts.append(f"{session['neuron_count']} neurons")
            if session.get('frame_count', 0) > 0:
                info_parts.append(f"{session['frame_count']} frames")
            
            if session.get('last_modified', 0) > 0:
                time_str = time.strftime("%m/%d %H:%M", time.localtime(session['last_modified']))
                info_parts.append(time_str)
            
            if info_parts:
                info_text = " | ".join(info_parts)
                info_surf = self.small_font.render(info_text, True, (150, 180, 220))
                info_rect = info_surf.get_rect(bottomleft=(panel_x + 40, list_y + item_height - 10))
                self.screen.blit(info_surf, info_rect)
            
            list_y += item_height
        
        if start_idx > 0:
            up_arrow = self.font.render("↑", True, (200, 200, 200))
            up_rect = up_arrow.get_rect(center=(panel_x + panel_width // 2, panel_y + 90))
            self.screen.blit(up_arrow, up_rect)
        
        if end_idx < len(self.browser.sessions):
            down_arrow = self.font.render("↓", True, (200, 200, 200))
            down_rect = down_arrow.get_rect(center=(panel_x + panel_width // 2, 
                                                   panel_y + panel_height - 30))
            self.screen.blit(down_arrow, down_rect)
        
        selection_text = f"{self.browser.selected_index + 1}/{len(self.browser.sessions)}"
        selection_surf = self.small_font.render(selection_text, True, (180, 200, 255))
        selection_rect = selection_surf.get_rect(topright=(panel_x + panel_width - 20, panel_y + 75))
        self.screen.blit(selection_surf, selection_rect)
    
    
    def _draw_timeline_controls(self):
        """Draw timeline controls"""
        if not self.timeline.frames:
            return
        
        terminal_width = self.screen_width // 3
        terminal_height = 150
        terminal_x = 20
        terminal_y = self.screen_height - terminal_height - 5
        
        panel_height = 80
        timeline_y = terminal_y - panel_height - 15
        timeline_x = terminal_x
        panel_width = terminal_width
        
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (25, 25, 50, 220), 
                        panel_surf.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surf, (70, 90, 140, 120),
                        panel_surf.get_rect(), 2, border_radius=8)
        self.screen.blit(panel_surf, (timeline_x, timeline_y))
        
        title = self.small_font.render("TIMELINE CONTROLS", True, (200, 220, 255))
        self.screen.blit(title, (timeline_x + 10, timeline_y + 8))
        
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
        
        handle_x = bar_x + int(bar_width * progress)
        handle_y = bar_y + bar_height // 2
        handle_radius = 8
        
        handle_rect = pygame.Rect(handle_x - handle_radius, handle_y - handle_radius, 
                                handle_radius * 2, handle_radius * 2)
        self.timeline_handle_rect = handle_rect
        
        pygame.draw.circle(self.screen, (150, 200, 255), (handle_x, handle_y), handle_radius)
        pygame.draw.circle(self.screen, (80, 120, 200), (handle_x, handle_y), handle_radius, 2)
        
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
                pressed_rect = rect.copy()
                pressed_rect.y += 1
                pygame.draw.rect(self.screen, (40, 60, 140, 150), pressed_rect, border_radius=4)
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
            
            if btn_id == self.hovered_button and tooltip:
                tooltip_surf = self.small_font.render(tooltip, True, (240, 240, 255))
                tooltip_bg = pygame.Surface((tooltip_surf.get_width() + 10, 
                                            tooltip_surf.get_height() + 6), 
                                            pygame.SRCALPHA)
                pygame.draw.rect(tooltip_bg, (40, 40, 60, 220), 
                                tooltip_bg.get_rect(), border_radius=3)
                tooltip_rect = tooltip_bg.get_rect(midtop=(rect.centerx, rect.bottom + 5))
                
                self.screen.blit(tooltip_bg, tooltip_rect)
                self.screen.blit(tooltip_surf, 
                            (tooltip_rect.x + 5, tooltip_rect.y + 3))
        
        if self.timeline.current_frame_index < len(self.timeline.frames):
            frame_num = self.timeline.current_frame_index
            total_frames = len(self.timeline.frames)
            
            frame_text = f"{frame_num}/{total_frames}"
            frame_surf = self.small_font.render(frame_text, True, (180, 220, 255))
            frame_rect = frame_surf.get_rect(midleft=(bar_x + bar_width + 10, bar_y + bar_height//2))
            self.screen.blit(frame_surf, frame_rect)
            
            speed_text = f"{self.timeline.playback_speed:.1f}x"
            speed_surf = self.small_font.render(speed_text, True, (180, 255, 180))
            speed_rect = speed_surf.get_rect(topright=(timeline_x + panel_width - 10, timeline_y + 8))
            self.screen.blit(speed_surf, speed_rect)
            
            status = "▶ PLAY" if self.timeline.is_playing else "‖ PAUSE"
            status_color = (100, 255, 100) if self.timeline.is_playing else (255, 200, 100)
            status_surf = self.small_font.render(status, True, status_color)
            status_rect = status_surf.get_rect(topright=(timeline_x + panel_width - 40, timeline_y + 8))
            self.screen.blit(status_surf, status_rect)

        
    def _init_ui_buttons(self):
        """Initialize UI buttons"""
        button_width = 100
        button_height = 30
        
        self.ui_buttons = {
            'mode_live': {
                'rect': pygame.Rect(20, 120, 80, 30),
                'label': 'LIVE',
                'tooltip': 'Switch to Live Mode'
            },
            'mode_replay': {
                'rect': pygame.Rect(110, 120, 80, 30),
                'label': 'REPLAY',
                'tooltip': 'Switch to Replay Mode'
            },
            'mode_browser': {
                'rect': pygame.Rect(200, 120, 90, 30),
                'label': 'BROWSE',
                'tooltip': 'Browse Sessions'
            },
            'toggle_legend': {
                'rect': pygame.Rect(self.screen_width - 120, 130, 110, 25),
                'label': '[?] LEGEND',
                'tooltip': 'Toggle Legend'
            },
            'toggle_axons': {
                'rect': pygame.Rect(self.screen_width - 120, 160, 110, 25),
                'label': '~ AXONS',
                'tooltip': 'Toggle Axons'
            },
            'toggle_grid': {
                'rect': pygame.Rect(self.screen_width - 120, 190, 110, 25),
                'label': '# GRID',
                'tooltip': 'Toggle Grid'
            },
            'toggle_changes': {
                'rect': pygame.Rect(self.screen_width - 120, 220, 110, 25),
                'label': '* CHANGES',
                'tooltip': 'Toggle Change Highlights'
            },
            'toggle_processing': {
                'rect': pygame.Rect(self.screen_width - 120, 250, 110, 25),
                'label': '↻ STATES',
                'tooltip': 'Toggle Processing States'
            },
        }
    

    def _handle_mousemotion(self, event):
        """Mouse motion handling"""
        mouse_pos = event.pos
        
        # Handle legend dragging
        if self.legend_dragging:
            dx = mouse_pos[0] - self.legend_drag_start[0]
            dy = mouse_pos[1] - self.legend_drag_start[1]
            self.legend_position = (
                max(0, min(self.screen_width - self.legend_size[0], self.legend_original_pos[0] + dx)),
                max(0, min(self.screen_height - self.legend_size[1], self.legend_original_pos[1] + dy))
            )
            return
        
        # Handle legend resizing
        if self.legend_resizing:
            dx = mouse_pos[0] - self.legend_resize_start[0]
            dy = mouse_pos[1] - self.legend_resize_start[1]
            
            # Calculate new size with minimum constraints
            new_width = max(300, min(800, self.legend_original_size[0] + dx))
            new_height = max(400, min(self.screen_height - self.legend_position[1] - 20, 
                                    self.legend_original_size[1] + dy))
            
            self.legend_size = (new_width, new_height)
            return
        
        # Check for hover over UI elements
        self.hovered_button = self._check_ui_button_hover(mouse_pos)
        
        if self.hovered_button:
            self.hovered_neuron_id = None
            return
        
        if self.mode == self.MODE_BROWSER:
            self.hovered_session_index = self._check_browser_session_click(mouse_pos)
            return
        
        # Check for hover over neurons
        hovered_neuron = self._get_neuron_at_pos(mouse_pos)
        
        if hovered_neuron:
            self.hovered_neuron_id = hovered_neuron.get('neuron_id')
        else:
            if not self.dragging_view:
                self.hovered_neuron_id = None
        
        # Handle timeline dragging in replay mode
        if self.mode == self.MODE_REPLAY and hasattr(self.timeline, 'is_dragging') and self.timeline.is_dragging:
            bar_width = self.screen_width // 3 - 120
            bar_x = 20 + 10
            
            new_progress = max(0, min(1, (mouse_pos[0] - bar_x) / bar_width))
            new_frame_index = int(new_progress * (len(self.timeline.frames) - 1))
            
            if new_frame_index != self.timeline.current_frame_index:
                frame = self.timeline.jump_to_frame(new_frame_index)
                if frame:
                    self._load_current_sequence(frame)
                    self.current_sequence_index = new_frame_index
        
        # Handle view dragging
        if self.dragging_view:
            dx = mouse_pos[0] - self.drag_start_pos[0]
            dy = mouse_pos[1] - self.drag_start_pos[1]
            
            self.pan_x = self.drag_start_pan[0] + dx
            self.pan_y = self.drag_start_pan[1] + dy
            
    def _handle_mouseup(self, event):
        """Mouse up handling"""
        if event.button == 1:
            self.active_button = None
            self.dragging_view = False
            
            # Stop legend interactions
            self.legend_dragging = False
            self.legend_resizing = False
            
            if self.mode == self.MODE_REPLAY and hasattr(self.timeline, 'is_dragging') and self.timeline.is_dragging:
                self.timeline.is_dragging = False
                
    def _handle_mousewheel(self, event):
        """Mouse wheel zoom at mouse position"""
        mouse_pos = pygame.mouse.get_pos()
        
        zoom_factor = 1.1 if event.y > 0 else 0.9
        
        mouse_world_x = (mouse_pos[0] - self.screen_width//2 - self.pan_x) / (self.cell_size * self.zoom)
        mouse_world_y = (mouse_pos[1] - self.screen_height//2 - self.pan_y) / (self.cell_size * self.zoom)
        
        old_zoom = self.zoom
        if event.y > 0:
            self.zoom = min(5.0, self.zoom * zoom_factor)
        else:
            self.zoom = max(0.1, self.zoom * zoom_factor)
        
        new_mouse_screen_x = self.screen_width//2 + self.pan_x + mouse_world_x * self.cell_size * self.zoom
        new_mouse_screen_y = self.screen_height//2 + self.pan_y + mouse_world_y * self.cell_size * self.zoom
        
        self.pan_x += (mouse_pos[0] - new_mouse_screen_x)
        self.pan_y += (mouse_pos[1] - new_mouse_screen_y)
        
        # CLEAR CACHE - zoom changed
        self._clear_frame_cache()
        
        direction = "in" if event.y > 0 else "out"
        self._add_log(f"🔍 Zoom {direction}: {self.zoom:.1f}x")

    # ===== HELPER METHODS =====
    def _get_neuron_at_pos(self, pos):
        """Get neuron at screen position - USING WORLD COORDS"""
        if not self.active_neurons:
            return None
        
        mouse_x, mouse_y = pos
        
        # Convert mouse to world coordinates
        center_x = self.screen_width // 2 + self.pan_x
        center_y = self.screen_height // 2 + self.pan_y
        
        # Mouse in world space (reverse of screen transform)
        world_mouse_x = (mouse_x - center_x) / (self.cell_size * self.zoom)
        world_mouse_y = (mouse_y - center_y) / (self.cell_size * self.zoom)
        
        closest_neuron = None
        closest_distance = float('inf')
        
        for coord, neuron_data in self.active_neurons.items():
            # Get world position from cached data
            if 'world_x' in neuron_data and 'world_y' in neuron_data:
                world_x = neuron_data['world_x'] / self.cell_size  # Convert back to coord units
                world_y = neuron_data['world_y'] / self.cell_size
            else:
                # Fallback: calculate from coord
                depth = len(coord) - 1
                sibling_index = coord[-1] if len(coord) > 0 else 0
                world_x = sibling_index
                world_y = depth
            
            dx = world_mouse_x - world_x
            dy = world_mouse_y - world_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            hit_radius = 1.0 / self.zoom  # Hit radius in world units
            
            if distance < hit_radius and distance < closest_distance:
                closest_distance = distance
                closest_neuron = neuron_data
        
        return closest_neuron

    def _check_ui_button_click(self, mouse_pos):
        """Check if a UI button was clicked"""
        for button_name, button_info in self.ui_buttons.items():
            if button_info['rect'].collidepoint(mouse_pos):
                return button_name
        
        if self.mode == self.MODE_REPLAY and hasattr(self, 'timeline_button_rects'):
            for btn_id, rect in self.timeline_button_rects.items():
                if rect.collidepoint(mouse_pos):
                    return btn_id
        
        if self.mode == self.MODE_REPLAY and hasattr(self, 'timeline_handle_rect'):
            if self.timeline_handle_rect.collidepoint(mouse_pos):
                return 'timeline_handle'
        
        return None

    def _check_browser_session_click(self, mouse_pos):
        """Check if mouse clicked on a browser session item"""
        if self.mode != self.MODE_BROWSER or not self.browser.sessions:
            return None
        
        panel_width = 800
        panel_height = 600
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        list_y = panel_y + 100
        item_height = 50
        
        start_idx = self.browser.scroll_offset
        visible_items = min(self.browser.visible_items, len(self.browser.sessions) - start_idx)
        
        for i in range(visible_items):
            item_rect = pygame.Rect(
                panel_x + 30,
                list_y + i * item_height,
                panel_width - 60,
                item_height - 5
            )
            
            if item_rect.collidepoint(mouse_pos):
                return start_idx + i
        
        return None

    def _check_ui_button_hover(self, mouse_pos):
        """Check if mouse is hovering over a UI button"""
        for button_name, button_info in self.ui_buttons.items():
            if button_info['rect'].collidepoint(mouse_pos):
                return button_name
        
        if self.mode == self.MODE_REPLAY and hasattr(self, 'timeline_button_rects'):
            for btn_id, rect in self.timeline_button_rects.items():
                if rect.collidepoint(mouse_pos):
                    return btn_id
        
        if self.mode == self.MODE_REPLAY and hasattr(self, 'timeline_handle_rect'):
            if self.timeline_handle_rect.collidepoint(mouse_pos):
                return 'timeline_handle'
        
        if self.mode == self.MODE_BROWSER:
            panel_width = 800
            panel_height = 600
            panel_x = (self.screen_width - panel_width) // 2
            panel_y = (self.screen_height - panel_height) // 2
            refresh_rect = pygame.Rect(panel_x + panel_width - 100, panel_y + 30, 80, 30)
            if refresh_rect.collidepoint(mouse_pos):
                return 'browser_refresh'
        
        return None

    def _draw_ui_panel(self):
        """Draw UI panel with session info - ONLY IN LIVE/REPLAY MODE"""
        if self.mode == self.MODE_BROWSER or self.mode == self.MODE_LOADING:
            return  # Don't draw UI panel in browser/loading modes
        
        # Draw mode indicator
        mode_text = f"MODE: {self.mode.upper()}"
        mode_surf = self.title_font.render(mode_text, True, (255, 255, 200))
        mode_rect = mode_surf.get_rect(center=(self.screen_width // 2, 30))
        
        # Background for mode indicator
        bg_rect = mode_rect.inflate(20, 10)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 20, 40, 200), bg_surf.get_rect(), border_radius=8)
        self.screen.blit(bg_surf, bg_rect)
        self.screen.blit(mode_surf, mode_rect)
        
        # Session info
        session_text = f"Session: {self.session_id[:20]}{'...' if len(self.session_id) > 20 else ''}"
        session_surf = self.small_font.render(session_text, True, (180, 200, 255))
        self.screen.blit(session_surf, (20, 70))
        
        # Frame info
        frame_text = f"Frame: {self.current_sequence_index if self.current_sequence else 0}"
        frame_surf = self.small_font.render(frame_text, True, (180, 200, 255))
        self.screen.blit(frame_surf, (20, 90))
        
        # Draw statistics panel
        self._draw_statistics()

    def _draw_statistics(self):
        """Draw statistics panel - ONLY IN LIVE/REPLAY MODE"""
        if self.mode == self.MODE_BROWSER or self.mode == self.MODE_LOADING:
            return
        
        panel_width = 300
        panel_height = 180
        panel_x = 20
        panel_y = 170
        
        # Create semi-transparent panel
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 20, 40, 220), 
                        panel_surf.get_rect(), border_radius=8)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        y_offset = panel_y + 15
        
        # Statistics - only show relevant ones for current mode
        stats = [
            f"Neurons: {len(self.active_neurons)}",
            f"Active Axons: {len(self.active_axon_beams)}",
            f"Sequence: {self.current_sequence_index + 1}/{len(self.animation_sequences) if self.animation_sequences else 0}",
            f"FPS: {self.clock.get_fps():.1f}",
            f"Zoom: {self.zoom:.1f}x",
        ]
        
        if self.mode == self.MODE_REPLAY:
            stats.append(f"Playback: {'▶' if self.timeline.is_playing else '‖'} {self.timeline.playback_speed:.1f}x")
        
        for stat in stats:
            stat_surf = self.small_font.render(stat, True, (200, 220, 255))
            self.screen.blit(stat_surf, (panel_x + 10, y_offset))
            y_offset += 20

    def _draw_focused_info(self):
        """Draw focused neuron info panel"""
        if not self.focused_neuron_id:
            return
        
        # Find neuron by coordinate
        focused_neuron = None
        focused_coord = None
        for coord, neuron_data in self.active_neurons.items():
            if neuron_data.get('neuron_id') == self.focused_neuron_id:
                focused_neuron = neuron_data
                focused_coord = coord
                break
        
        if not focused_neuron:
            return
        
        panel_width = 380
        panel_height = 240
        panel_x = self.screen_width - panel_width - 20
        panel_y = 500
        
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 20, 40, 240), 
                        panel_surf.get_rect(), border_radius=8)
        pygame.draw.rect(panel_surf, (100, 150, 200, 200),
                        panel_surf.get_rect(), 2, border_radius=8)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        y_offset = panel_y + 15
        
        title = self.font.render("NEURON DETAILS", True, (255, 255, 200))
        self.screen.blit(title, (panel_x + 15, y_offset))
        y_offset += 35
        
        col1_width = 120
        col2_x = panel_x + col1_width
        
        details = [
            ("ID:", self.focused_neuron_id[:18], (220, 220, 255)),
            ("Coordinate:", str(focused_coord), (200, 220, 255)),
            ("Pattern:", focused_neuron.get('pattern', 'UNKNOWN'), 
             PATTERN_COLORS.get(focused_neuron.get('pattern', 'UNKNOWN'), (255, 255, 255))),
            ("State:", focused_neuron.get('current_state', 'UNKNOWN'), 
             STATE_COLORS.get(focused_neuron.get('current_state', 'UNKNOWN'), (255, 255, 255))),
            ("Confidence:", f"{focused_neuron.get('confidence', 0):.1%}", 
             self._get_similarity_color(focused_neuron.get('confidence', 0))),
            ("Phase:", focused_neuron.get('processing_phase', 'UNKNOWN'), (200, 220, 255)),
        ]
        
        for label, value, color in details:
            label_surf = self.small_font.render(label, True, (180, 200, 220))
            self.screen.blit(label_surf, (panel_x + 15, y_offset))
            
            value_str = str(value)
            if len(value_str) > 25:
                value_str = value_str[:22] + "..."
            
            value_surf = self.small_font.render(value_str, True, color)
            self.screen.blit(value_surf, (col2_x, y_offset))
            
            y_offset += 22
    
    # ===== MISSING HELPER METHODS =====
    def _get_similarity_color(self, similarity: float) -> Tuple[int, int, int]:
        """Get color based on similarity value"""
        if similarity > 0.8:
            return (100, 255, 100)
        elif similarity > 0.5:
            return (255, 255, 100)
        else:
            return (255, 100, 100)
    
    def _add_log(self, message: str):
        """Add message to terminal logs"""
        self.logs.append({
            'timestamp': time.time(),
            'message': message,
            'type': 'info'
        })
        print(f"📝 {message}")
    
    def _draw_loading_screen(self):
        """Draw loading screen"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        panel_width = 600
        panel_height = 300
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        pygame.draw.rect(self.screen, (30, 30, 60), 
                        (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(self.screen, (80, 100, 180), 
                        (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)
        
        title = self.title_font.render("BUILDING ANIMATION SEQUENCES", True, (255, 255, 200))
        title_rect = title.get_rect(center=(self.screen_width // 2, panel_y + 50))
        self.screen.blit(title, title_rect)
        
        session_text = f"Session: {self.session_id}"
        session_surf = self.font.render(session_text, True, (180, 200, 255))
        session_rect = session_surf.get_rect(center=(self.screen_width // 2, panel_y + 90))
        self.screen.blit(session_surf, session_rect)
        
        # Progress bar
        bar_width = 400
        bar_height = 25
        bar_x = (self.screen_width - bar_width) // 2
        bar_y = panel_y + 140
        
        pygame.draw.rect(self.screen, (40, 50, 80), 
                        (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        
        if len(self.animation_sequences) > 0:
            progress = min(1.0, len(self.animation_sequences) / 100)  # Approximate
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                fill_color = (
                    int(100 + 155 * progress),
                    int(180 + 75 * progress),
                    255
                )
                pygame.draw.rect(self.screen, fill_color,
                                (bar_x, bar_y, fill_width, bar_height), border_radius=5)
        
        pygame.draw.rect(self.screen, (100, 120, 200), 
                        (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)
        
        progress_text = f"Sequences built: {len(self.animation_sequences)}"
        progress_surf = self.font.render(progress_text, True, (200, 220, 255))
        progress_rect = progress_surf.get_rect(center=(self.screen_width // 2, bar_y + bar_height + 25))
        self.screen.blit(progress_surf, progress_rect)
        
        if hasattr(self, 'loading_message') and self.loading_message:
            msg_surf = self.small_font.render(self.loading_message, True, (180, 200, 255))
            msg_rect = msg_surf.get_rect(center=(self.screen_width // 2, bar_y + bar_height + 55))
            self.screen.blit(msg_surf, msg_rect)
    
    # ===== MISSING EVENT HANDLING METHODS =====
    
    def _handle_keydown(self, event):
        """Keyboard handling"""
        # Fullscreen toggle
        if event.key == pygame.K_f:
            self._toggle_fullscreen()
            return
        
        # Screen switching
        if event.key == pygame.K_RIGHT and self.screen_mode == "neuron_view":
            self.screen_mode = "stats_view"
            self._init_stats_surface()
            self._add_log("📊 Switched to statistics view")
            return
        
        if event.key == pygame.K_LEFT and self.screen_mode == "stats_view":
            self.screen_mode = "neuron_view"
            self._add_log("🧠 Returned to neuron view")
            return
        
        if event.key == pygame.K_ESCAPE:
            if self.mode == self.MODE_BROWSER:
                self.mode = self.MODE_LIVE
                self._add_log("🔙 Returned to live mode")
            elif self.screen_mode == "stats_view":
                self.screen_mode = "neuron_view"
                self._add_log("🔙 Returned to neuron view")
            else:
                self.running = False
            return
        
        if self.mode == self.MODE_BROWSER:
            if self.browser.handle_keydown(event.key):
                return
            elif event.key == pygame.K_RETURN:
                self._load_selected_session()
                return
            elif event.key == pygame.K_r:
                self.browser.scan_sessions()
                self._add_log("🔄 Refreshed session list")
                return
        
        if event.key == pygame.K_c:
            self.pan_x, self.pan_y = 0, 0
            self._add_log("🎯 Centered view")
            return
        
        if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            self.zoom = min(3.0, self.zoom * 1.1)
            self._clear_frame_cache()
            self._add_log(f"🔍 Zoom: {self.zoom:.1f}x")
        
        elif event.key == pygame.K_MINUS:
            self.zoom = max(0.3, self.zoom * 0.9)
            self._clear_frame_cache()
            self._add_log(f"🔍 Zoom: {self.zoom:.1f}x")
        
        elif event.key == pygame.K_l:
            self.show_legend = not self.show_legend
            self._add_log(f"📖 Legend: {'ON' if self.show_legend else 'OFF'}")
        
        elif event.key == pygame.K_g:
            self.show_grid = not self.show_grid
            self._add_log(f"📐 Grid: {'ON' if self.show_grid else 'OFF'}")

        elif event.key == pygame.K_h:
            self.show_change_highlights = not self.show_change_highlights
            self._add_log(f"✨ Change highlights: {'ON' if self.show_change_highlights else 'OFF'}")
        
        elif event.key == pygame.K_p:
            self.show_processing_states = not self.show_processing_states
            self._add_log(f"🔄 Processing states: {'ON' if self.show_processing_states else 'OFF'}")
        
        elif event.key == pygame.K_1:
            self.mode = self.MODE_LIVE
            self._add_log("🔴 Switched to live mode")
        
        elif event.key == pygame.K_2:
            self.mode = self.MODE_REPLAY
            if self.animation_sequences:
                self.timeline.load_frames(self.animation_sequences)
            self._add_log("🎬 Switched to replay mode")
        
        elif event.key == pygame.K_3:
            self.mode = self.MODE_BROWSER
            self.browser.scan_sessions()
            self._add_log("📁 Switched to browser mode")
        
        elif event.key == pygame.K_0:  # Fullscreen toggle alternative
            self._toggle_fullscreen()
            return
        
        elif event.key == pygame.K_LEFTBRACKET:
            if self.mode == self.MODE_REPLAY:
                self.timeline.playback_speed = max(0.1, self.timeline.playback_speed * 0.8)
                self._add_log(f"🐌 Speed: {self.timeline.playback_speed:.1f}x")
        
        elif event.key == pygame.K_RIGHTBRACKET:
            if self.mode == self.MODE_REPLAY:
                self.timeline.playback_speed = min(5.0, self.timeline.playback_speed * 1.25)
                self._add_log(f"🚀 Speed: {self.timeline.playback_speed:.1f}x")
        
        elif event.key == pygame.K_LEFT:
            self.keys_held[pygame.K_LEFT] = True
        elif event.key == pygame.K_RIGHT:
            self.keys_held[pygame.K_RIGHT] = True
        elif event.key == pygame.K_UP:
            self.keys_held[pygame.K_UP] = True
        elif event.key == pygame.K_DOWN:
            self.keys_held[pygame.K_DOWN] = True
        elif event.key == pygame.K_a:
            self.keys_held[pygame.K_a] = True
        elif event.key == pygame.K_d:
            self.keys_held[pygame.K_d] = True
        elif event.key == pygame.K_w:
            self.keys_held[pygame.K_w] = True
        elif event.key == pygame.K_s:
            self.keys_held[pygame.K_s] = True
        elif event.key == pygame.K_LSHIFT:
            self.keys_held[pygame.K_LSHIFT] = True
        elif event.key == pygame.K_RSHIFT:
            self.keys_held[pygame.K_RSHIFT] = True
        
        elif self.mode == self.MODE_REPLAY:
            if event.key == pygame.K_SPACE:
                self.timeline.is_playing = not self.timeline.is_playing
                status = "PLAYING" if self.timeline.is_playing else "PAUSED"
                self._add_log(f"⏯️ Playback: {status}")
            elif event.key == pygame.K_COMMA:
                self.timeline.playback_speed = max(0.1, self.timeline.playback_speed * 0.8)
                self._add_log(f"🐌 Speed: {self.timeline.playback_speed:.1f}x")
            elif event.key == pygame.K_PERIOD:
                self.timeline.playback_speed = min(5.0, self.timeline.playback_speed * 1.25)
                self._add_log(f"🚀 Speed: {self.timeline.playback_speed:.1f}x")
            elif event.key == pygame.K_HOME:
                if self.timeline.frames:
                    frame = self.timeline.jump_to_frame(0)
                    if frame:
                        self._load_current_sequence(frame)
                        self.current_sequence_index = 0
                        self._add_log(f"⏮️ Jumped to frame 0")
            elif event.key == pygame.K_END:
                if self.timeline.frames:
                    frame = self.timeline.jump_to_frame(len(self.timeline.frames) - 1)
                    if frame:
                        self._load_current_sequence(frame)
                        self.current_sequence_index = len(self.timeline.frames) - 1
                        self._add_log(f"⏭️ Jumped to last frame")

    def _handle_keyup(self, event):
        """Handle key up events"""
        if event.key == pygame.K_LEFT:
            self.keys_held[pygame.K_LEFT] = False
        elif event.key == pygame.K_RIGHT:
            self.keys_held[pygame.K_RIGHT] = False
        elif event.key == pygame.K_UP:
            self.keys_held[pygame.K_UP] = False
        elif event.key == pygame.K_DOWN:
            self.keys_held[pygame.K_DOWN] = False
        elif event.key == pygame.K_a:
            self.keys_held[pygame.K_a] = False
        elif event.key == pygame.K_d:
            self.keys_held[pygame.K_d] = False
        elif event.key == pygame.K_w:
            self.keys_held[pygame.K_w] = False
        elif event.key == pygame.K_s:
            self.keys_held[pygame.K_s] = False
        elif event.key == pygame.K_LSHIFT:
            self.keys_held[pygame.K_LSHIFT] = False
        elif event.key == pygame.K_RSHIFT:
            self.keys_held[pygame.K_RSHIFT] = False
    
    def handle_events_single(self, event):
        """Handle single event"""
        if event.type == pygame.QUIT:
            self.running = False
        
        elif event.type == pygame.KEYDOWN:
            if self.screen_mode == "stats_view":
                self._handle_stats_keydown(event)
            else:
                self._handle_keydown(event)
        
        elif event.type == pygame.KEYUP:
            if self.screen_mode != "stats_view":
                self._handle_keyup(event)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.screen_mode == "stats_view":
                self._handle_stats_mousedown(event)
            else:
                self._handle_mousedown(event)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.screen_mode == "stats_view":
                pass  # Handle stats view mouse up if needed
            else:
                self._handle_mouseup(event)
        
        elif event.type == pygame.MOUSEMOTION:
            if self.screen_mode == "stats_view":
                self._update_stats_hover(event.pos)
            else:
                self._handle_mousemotion(event)
        
        elif event.type == pygame.MOUSEWHEEL:
            if self.screen_mode == "stats_view":
                # Cycle graphs in stats view
                if event.y > 0:  # Scroll up
                    modes = list(self.graph_sets.keys())
                    current_idx = modes.index(self.stats_graph_mode) if self.stats_graph_mode in modes else 0
                    self.stats_graph_mode = modes[(current_idx - 1) % len(modes)]
                    self.current_graph_index = 0
                elif event.y < 0:  # Scroll down
                    modes = list(self.graph_sets.keys())
                    current_idx = modes.index(self.stats_graph_mode) if self.stats_graph_mode in modes else 0
                    self.stats_graph_mode = modes[(current_idx + 1) % len(modes)]
                    self.current_graph_index = 0
            else:
                self._handle_mousewheel(event)

    def handle_events(self):
        """Handle all events - NO SUPER CALLS"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.screen_mode == "stats_view":
                    self._handle_stats_keydown(event)  # Call our method
                else:
                    self._handle_keydown(event)  # Call our method
            
            elif event.type == pygame.KEYUP:
                if self.screen_mode != "stats_view":  # Only handle in neuron view
                    self._handle_keyup(event)  # Call our method
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.screen_mode == "stats_view":
                    self._handle_stats_mousedown(event)  # Call our method
                else:
                    self._handle_mousedown(event)  # Call our method
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.screen_mode == "stats_view":
                    # In stats view, only handle mouse up for resizing if needed
                    if event.button == 1:
                        # Stop any dragging/resizing in stats view
                        pass
                else:
                    self._handle_mouseup(event)  # Call our method
            
            elif event.type == pygame.MOUSEMOTION:
                if self.screen_mode == "stats_view":
                    # Update hover info for graphs
                    self._update_stats_hover(event.pos)  # Call our method
                else:
                    self._handle_mousemotion(event)  # Call our method
            
            elif event.type == pygame.MOUSEWHEEL:
                if self.screen_mode == "stats_view":
                    # Use mouse wheel to cycle graphs in stats view
                    if event.y > 0:  # Scroll up - previous graph
                        modes = list(self.graph_sets.keys())
                        current_idx = modes.index(self.stats_graph_mode) if self.stats_graph_mode in modes else 0
                        self.stats_graph_mode = modes[(current_idx - 1) % len(modes)]
                        self.current_graph_index = 0
                    elif event.y < 0:  # Scroll down - next graph
                        modes = list(self.graph_sets.keys())
                        current_idx = modes.index(self.stats_graph_mode) if self.stats_graph_mode in modes else 0
                        self.stats_graph_mode = modes[(current_idx + 1) % len(modes)]
                        self.current_graph_index = 0
                else:
                    self._handle_mousewheel(event)  # Call our method

    def _handle_stats_keydown(self, event):
        """Handle keydown in stats view"""
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_LEFT:
            self.screen_mode = "neuron_view"
            self._add_log("🔙 Returned to neuron view")
        elif event.key == pygame.K_RIGHT:
            # Cycle to next graph set
            modes = list(self.graph_sets.keys())
            current_idx = modes.index(self.stats_graph_mode) if self.stats_graph_mode in modes else 0
            self.stats_graph_mode = modes[(current_idx + 1) % len(modes)]
            self.current_graph_index = 0
        elif event.key == pygame.K_LEFTBRACKET:
            # Previous graph in set
            graph_set = self.graph_sets.get(self.stats_graph_mode, [])
            if graph_set:
                self.current_graph_index = (self.current_graph_index - 1) % len(graph_set)
        elif event.key == pygame.K_RIGHTBRACKET:
            # Next graph in set
            graph_set = self.graph_sets.get(self.stats_graph_mode, [])
            if graph_set:
                self.current_graph_index = (self.current_graph_index + 1) % len(graph_set)

    def _handle_stats_mousedown(self, event):
        """Handle mouse down in stats view"""
        mouse_pos = event.pos
        
        # Check for back button click
        if hasattr(self, 'stats_back_button') and self.stats_back_button.collidepoint(mouse_pos):
            self.screen_mode = "neuron_view"
            self._add_log("🔙 Returned to neuron view")
            return
        
        # Check for mode button clicks
        if hasattr(self, 'stats_mode_buttons'):
            for mode, button_rect in self.stats_mode_buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    self.stats_graph_mode = mode
                    self.current_graph_index = 0
                    self._add_log(f"📊 Switched to {mode.replace('_', ' ')} view")
                    return

    def _update_stats_hover(self, mouse_pos):
        """Update hover info for graphs"""
        # Check for button hovers
        if hasattr(self, 'stats_back_button') and self.stats_back_button.collidepoint(mouse_pos):
            self.hovered_button = 'stats_back'
        elif hasattr(self, 'stats_mode_buttons'):
            for mode, button_rect in self.stats_mode_buttons.items():
                if button_rect.collidepoint(mouse_pos):
                    self.hovered_button = f'stats_mode_{mode}'
                    return
        else:
            self.hovered_button = None

    def _handle_mousedown(self, event):
            """Mouse down handling"""
            mouse_pos = event.pos
            
            # Handle stats screen clicks
            if self.screen_mode == "stats_view":
                if event.button == 1:
                    # Check for fullscreen button click
                    if hasattr(self, 'stats_fullscreen_button'):
                        if self.stats_fullscreen_button.collidepoint(mouse_pos):
                            self._toggle_fullscreen()
                            return
                return  # Skip other handling for stats screen
            
            # Handle legend interactions first (only in neuron view)
            if self.screen_mode == "neuron_view" and self.show_legend and hasattr(self, 'legend_rect') and self.legend_rect.collidepoint(mouse_pos):
                if event.button == 1:  # Left click
                    # Check for close button
                    if hasattr(self, 'legend_close_button') and self.legend_close_button.collidepoint(mouse_pos):
                        self.show_legend = False
                        self._add_log("📖 Legend closed")
                        return
                    
                    # Check for change button
                    if hasattr(self, 'legend_change_button') and self.legend_change_button.collidepoint(mouse_pos):
                        self.legend_change_mode = not self.legend_change_mode
                        self._add_log(f"📖 Legend change mode: {'ON' if self.legend_change_mode else 'OFF'}")
                        return
                    
                    # Check for resize handle
                    if hasattr(self, 'legend_resize_rect') and self.legend_resize_rect.collidepoint(mouse_pos):
                        self.legend_resizing = True
                        self.legend_resize_start = mouse_pos
                        self.legend_original_size = self.legend_size
                        return
                    
                    # Check for title bar drag
                    if hasattr(self, 'legend_title_rect') and self.legend_title_rect.collidepoint(mouse_pos):
                        self.legend_dragging = True
                        self.legend_drag_start = mouse_pos
                        self.legend_original_pos = self.legend_position
                        return
                
                # Don't process other clicks inside legend
                return
            
            if self.mode == self.MODE_BROWSER:
                if event.button == 1:
                    clicked_session = self._check_browser_session_click(mouse_pos)
                    if clicked_session is not None:
                        self.browser.selected_index = clicked_session
                        self._add_log(f"📁 Selected session {clicked_session + 1}")
                        
                        current_time = time.time()
                        if hasattr(self, 'last_click_time') and current_time - self.last_click_time < 0.5:
                            self._load_selected_session()
                        self.last_click_time = current_time
                        return
                    
                    if 'browser_refresh' in self.ui_buttons:
                        refresh_rect = self.ui_buttons['browser_refresh']['rect']
                        if refresh_rect.collidepoint(mouse_pos):
                            self.browser.scan_sessions()
                            self._add_log("🔄 Refreshed session list")
                            return
                
                clicked_button = self._check_ui_button_click(mouse_pos)
                if clicked_button:
                    self._handle_button_click(clicked_button)
                    self.active_button = clicked_button
                    return
            
            if event.button == 1 and self.mode != self.MODE_BROWSER:
                clicked_button = self._check_ui_button_click(mouse_pos)
                if clicked_button:
                    self._handle_button_click(clicked_button)
                    self.active_button = clicked_button
                    return
                
                if self.mode == self.MODE_REPLAY:
                    if hasattr(self, 'timeline_handle_rect') and self.timeline_handle_rect:
                        bar_width = self.screen_width // 3 - 120
                        bar_x = 20 + 10
                        bar_y = self.screen_height - 150 - 40 + 15 + 30
                        
                        bar_rect = pygame.Rect(bar_x, bar_y - 10, bar_width, 15 + 20)
                        if bar_rect.collidepoint(mouse_pos):
                            self.timeline.is_dragging = True
                            
                            new_progress = max(0, min(1, (mouse_pos[0] - bar_x) / bar_width))
                            new_frame_index = int(new_progress * (len(self.timeline.frames) - 1))
                            
                            frame = self.timeline.jump_to_frame(new_frame_index)
                            if frame:
                                self._load_current_sequence(frame)
                                self.current_sequence_index = new_frame_index
                            return
                
                # Check for neuron click
                clicked_neuron = self._get_neuron_at_pos(mouse_pos)
                if clicked_neuron:
                    self.focused_neuron_id = clicked_neuron.get('neuron_id')
                    self._add_log(f"🎯 Focused on neuron at {clicked_neuron.get('coordinate')}")
                    return
                
                if not clicked_neuron and not clicked_button:
                    self.hovered_neuron_id = None
                    self.focused_neuron_id = None
                    self.selected_neurons.clear()
                
                self.dragging_view = True
                self.drag_start_pos = mouse_pos
                self.drag_start_pan = (self.pan_x, self.pan_y)
            
            elif event.button == 3:
                clicked_neuron = self._get_neuron_at_pos(mouse_pos)
                if clicked_neuron:
                    neuron_id = clicked_neuron.get('neuron_id')
                    if neuron_id in self.selected_neurons:
                        self.selected_neurons.remove(neuron_id)
                    else:
                        self.selected_neurons.add(neuron_id)
                elif not self._check_ui_button_click(mouse_pos):
                    self.hovered_neuron_id = None
                    
    def _handle_button_click(self, button_name):
        """Handle UI button clicks"""
        self._add_log(f"🖱️ Button clicked: {button_name}")
        
        button_map = {
            'timeline_play': 'play_pause',
            'timeline_prev': 'prev_frame',
            'timeline_next': 'next_frame',
            'timeline_slower': 'speed_down',
            'timeline_faster': 'speed_up',
            'timeline_handle': None,
            'browser_refresh': 'browser_refresh',
        }
        
        mapped_button = button_map.get(button_name, button_name)
        
        if mapped_button == "toggle_fullscreen":
            self._toggle_fullscreen()
        
        elif mapped_button == "switch_stats":
            self.screen_mode = "stats_view"
            self._init_stats_surface()
            self._add_log("📊 Switched to statistics view")
        
        elif mapped_button == "mode_live":
            self.mode = self.MODE_LIVE
            self._add_log("🔴 Switched to live mode")
        
        elif mapped_button == "mode_replay":
            self.mode = self.MODE_REPLAY
            if self.animation_sequences:
                self.timeline.load_frames(self.animation_sequences)
            self._add_log("🎬 Switched to replay mode")
        
        elif mapped_button == "mode_browser":
            self.mode = self.MODE_BROWSER
            self.browser.scan_sessions()
            self._add_log("📁 Switched to browser mode")
        
        elif mapped_button == "toggle_legend":
            self.show_legend = not self.show_legend
            # Reset legend to default position when reopened
            if self.show_legend:
                self.legend_position = (self.screen_width - 420, 90)
                self.legend_size = (400, 720)
                self.legend_change_mode = False
        
        elif mapped_button == "toggle_axons":
            self.show_axons = not self.show_axons
        
        elif mapped_button == "toggle_grid":
            self.show_grid = not self.show_grid
        
        elif mapped_button == "toggle_changes":
            self.show_change_highlights = not self.show_change_highlights
        
        elif mapped_button == "toggle_processing":
            self.show_processing_states = not self.show_processing_states
        
        elif mapped_button == "play_pause" and self.mode == self.MODE_REPLAY:
            self.timeline.is_playing = not self.timeline.is_playing
            status = "PLAYING" if self.timeline.is_playing else "PAUSED"
            self._add_log(f"⏯️ Playback: {status}")
        
        elif mapped_button == "prev_frame" and self.mode == self.MODE_REPLAY:
            if self.timeline.frames:
                new_index = max(0, self.timeline.current_frame_index - 1)
                frame = self.timeline.jump_to_frame(new_index)
                if frame:
                    self._load_current_sequence(frame)
                    self.current_sequence_index = new_index
                    self._add_log(f"⏪ Frame: {new_index}")
        
        elif mapped_button == "next_frame" and self.mode == self.MODE_REPLAY:
            if self.timeline.frames:
                new_index = min(len(self.timeline.frames) - 1, 
                            self.timeline.current_frame_index + 1)
                frame = self.timeline.jump_to_frame(new_index)
                if frame:
                    self._load_current_sequence(frame)
                    self.current_sequence_index = new_index
                    self._add_log(f"⏩ Frame: {new_index}")
        
        elif mapped_button == "speed_down" and self.mode == self.MODE_REPLAY:
            self.timeline.playback_speed = max(0.1, self.timeline.playback_speed * 0.8)
            self._add_log(f"🐌 Speed: {self.timeline.playback_speed:.1f}x")
        
        elif mapped_button == "speed_up" and self.mode == self.MODE_REPLAY:
            self.timeline.playback_speed = min(5.0, self.timeline.playback_speed * 1.25)
            self._add_log(f"🚀 Speed: {self.timeline.playback_speed:.1f}x")
        
        elif mapped_button == "browser_refresh":
            self.browser.scan_sessions()
            self._add_log("🔄 Refreshed session list")
            
    def _draw_ui_buttons(self):
        """Draw all UI buttons"""
        for button_name, button_info in self.ui_buttons.items():
            rect = button_info['rect'].copy()
            label = button_info['label']
            
            if button_name == self.active_button:
                bg_color = (80, 100, 180)
                border_color = (120, 140, 220)
                text_color = (255, 255, 255)
                pressed_rect = rect.copy()
                pressed_rect.y += 1
                pygame.draw.rect(self.screen, (40, 60, 140, 150), pressed_rect, border_radius=4)
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
            
            if button_name == self.active_button:
                inner_rect = rect.inflate(-4, -4)
                pygame.draw.rect(self.screen, (40, 60, 140, 150), inner_rect, border_radius=4)
            
            label_surf = self.small_font.render(label, True, text_color)
            label_rect = label_surf.get_rect(center=rect.center)
            self.screen.blit(label_surf, label_rect)
            
            if button_name == self.hovered_button and 'tooltip' in button_info:
                tooltip = button_info['tooltip']
                tooltip_surf = self.small_font.render(tooltip, True, (240, 240, 255))
                tooltip_bg = pygame.Surface((tooltip_surf.get_width() + 10, 
                                        tooltip_surf.get_height() + 6), 
                                        pygame.SRCALPHA)
                pygame.draw.rect(tooltip_bg, (40, 40, 60, 220), 
                            tooltip_bg.get_rect(), border_radius=3)
                tooltip_rect = tooltip_bg.get_rect(midtop=(rect.centerx, rect.bottom + 5))
                
                self.screen.blit(tooltip_bg, tooltip_rect)
                self.screen.blit(tooltip_surf, 
                            (tooltip_rect.x + 5, tooltip_rect.y + 3))
    
    def _draw_logs(self):
        """Draw terminal logs - ONLY IN LIVE/REPLAY MODE"""
        if self.mode == self.MODE_BROWSER or self.mode == self.MODE_LOADING:
            return
        
        terminal_width = self.screen_width // 3
        terminal_height = 150
        terminal_x = 20
        terminal_y = self.screen_height - terminal_height - 5
        
        # Create terminal panel
        panel_surf = pygame.Surface((terminal_width, terminal_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (8, 8, 20, 240), 
                        (0, 0, terminal_width, terminal_height), border_radius=5)
        pygame.draw.rect(panel_surf, (40, 80, 120, 100),
                        (0, 0, terminal_width, terminal_height), 1, border_radius=5)
        self.screen.blit(panel_surf, (terminal_x, terminal_y))
        
        # Terminal title
        title = self.small_font.render("TERMINAL LOG", True, (180, 240, 255))
        self.screen.blit(title, (terminal_x + 10, terminal_y + 8))
        
        # Status indicator
        status_color = (100, 255, 100) if self.running else (255, 100, 100)
        pygame.draw.circle(self.screen, status_color, 
                        (terminal_x + terminal_width - 15, terminal_y + 12), 4)
        
        # Display recent logs
        log_start_y = terminal_y + 30
        visible_logs = 5
        
        recent_logs = list(self.logs)[-visible_logs:]
        
        for i, log in enumerate(recent_logs):
            log_y = log_start_y + i * 22
            
            if 'timestamp' in log:
                timestamp = time.strftime("%H:%M", time.localtime(log['timestamp']))
                time_surf = self.small_font.render(timestamp, True, (150, 180, 200))
                self.screen.blit(time_surf, (terminal_x + 8, log_y))
            
            msg = log.get('message', '')
            
            if len(msg) > 0:
                chars_to_show = min(len(msg), 60)
                if len(msg) > chars_to_show:
                    msg = msg[:chars_to_show - 3] + "..."
            
            # Color code messages
            if 'Error' in msg or '❌' in msg or '⚠️' in msg:
                msg_color = (255, 150, 150)
            elif 'Success' in msg or '✅' in msg or '✓' in msg:
                msg_color = (150, 255, 150)
            elif 'Loading' in msg or '🔄' in msg:
                msg_color = (150, 200, 255)
            else:
                msg_color = (220, 240, 220)
            
            msg_surf = self.small_font.render(msg, True, msg_color)
            self.screen.blit(msg_surf, (terminal_x + 65, log_y))
        
        # Show more logs indicator
        if len(self.logs) > visible_logs:
            scroll_text = f"... {len(self.logs) - visible_logs} more"
            scroll_surf = self.small_font.render(scroll_text, True, (120, 150, 180))
            scroll_rect = scroll_surf.get_rect(bottomright=(terminal_x + terminal_width - 10, 
                                                            terminal_y + terminal_height - 8))
            self.screen.blit(scroll_surf, scroll_rect)

    #====== NEW IMPLEMENTATIONS - SECOND WINDOW FOR GRAPHICAL STATISTICAL ANALYSIS VIA MATLAB  ========== 

    def _draw_statistics_screen(self):
            """Draw statistics screen using NEW export data"""
            self.screen.fill((10, 15, 25))
            
            # Draw header
            self._draw_stats_header()
            
            # Get current sequence data for graphs
            current_sequence = None
            if (hasattr(self, 'timeline_builder') and 
                hasattr(self, 'current_sequence_index') and
                self.current_sequence_index < len(self.timeline_builder.animation_sequences)):
                current_sequence = self.timeline_builder.animation_sequences[self.current_sequence_index]
            
            # Draw 4 graphs in grid
            margin = 30
            graph_spacing = 20
            graph_width = (self.screen_width - 2 * margin - graph_spacing) // 2
            graph_height = (self.screen_height - 150 - graph_spacing) // 2
            
            self.graph_positions = []
            for i in range(4):
                row = i // 2
                col = i % 2
                x = margin + col * (graph_width + graph_spacing)
                y = 140 + row * (graph_height + graph_spacing)
                self.graph_positions.append(pygame.Rect(x, y, graph_width, graph_height))
            
            # Draw graphs based on current mode
            graph_types = self.graph_sets.get(self.stats_graph_mode, [])
            
            for i, graph_type in enumerate(graph_types[:4]):
                if i < len(self.graph_positions):
                    self._draw_single_graph(
                        graph_type=graph_type,
                        position=self.graph_positions[i],
                        graph_index=i,
                        current_sequence=current_sequence
                    )
            
            # Draw navigation if needed
            if len(graph_types) > 4:
                self._draw_graph_navigation()
            
            # Draw hover info
            self._draw_graph_hover_info()
        
    def _draw_single_graph(self, graph_type: str, position: pygame.Rect, 
                          graph_index: int, current_sequence: Dict = None):
        """Draw a single graph using NEW export data"""
        # Draw graph background
        pygame.draw.rect(self.screen, (20, 25, 40), position, border_radius=10)
        pygame.draw.rect(self.screen, (60, 80, 120, 100), position, 2, border_radius=10)
        
        # Draw title
        title = graph_type.replace('_', ' ').title()
        title_surf = self.font.render(title, True, (220, 230, 255))
        title_rect = title_surf.get_rect(center=(position.centerx, position.y + 20))
        self.screen.blit(title_surf, title_rect)
        
        # Call appropriate graph method
        graph_method_name = f"_draw_{graph_type}_graph"
        if hasattr(self, graph_method_name):
            graph_method = getattr(self, graph_method_name)
            graph_area = pygame.Rect(
                position.x + 10,
                position.y + 40,
                position.width - 20,
                position.height - 60
            )
            try:
                graph_method(graph_area, current_sequence)
            except Exception as e:
                error_text = f"Error: {str(e)[:30]}"
                error_surf = self.small_font.render(error_text, True, (255, 100, 100))
                error_rect = error_surf.get_rect(center=position.center)
                self.screen.blit(error_surf, error_rect)
        else:
            no_impl = self.font.render(f"No {graph_type} graph", True, (150, 150, 180))
            no_rect = no_impl.get_rect(center=position.center)
            self.screen.blit(no_impl, no_rect)
    
    # ===== NEW GRAPHING METHODS USING 3 EIGEN SYSTEM =====
    
    def _draw_3_eigen_system_graph(self, graph_area, current_sequence):
        """Draw 3 eigen system visualization"""
        if not current_sequence or not current_sequence.get('eigen_system_data'):
            no_data = self.small_font.render("No 3 eigen data", True, (150, 150, 180))
            no_rect = no_data.get_rect(center=graph_area.center)
            self.screen.blit(no_data, no_rect)
            return
        
        eigen_data = current_sequence['eigen_system_data']
        
        # Create 3D scatter plot
        padding = 15
        plot_area = pygame.Rect(
            graph_area.x + padding,
            graph_area.y + 40,
            graph_area.width - 2 * padding,
            graph_area.height - 80
        )
        
        # Draw axes
        pygame.draw.line(self.screen, (150, 150, 180),  # Alpha axis (y)
                        (plot_area.x, plot_area.bottom),
                        (plot_area.x, plot_area.y), 2)
        pygame.draw.line(self.screen, (150, 150, 180),  # Beta axis (x)
                        (plot_area.x, plot_area.bottom),
                        (plot_area.right, plot_area.bottom), 2)
        pygame.draw.line(self.screen, (150, 150, 180),  # Zeta axis (diagonal)
                        (plot_area.x, plot_area.bottom),
                        (plot_area.right, plot_area.y), 2)
        
        # Plot neurons
        for neuron in eigen_data[:20]:  # Limit for clarity
            alpha = neuron.get('eigen_alpha', 0)
            beta = neuron.get('eigen_beta', 0)
            zeta = neuron.get('eigen_zeta', 0)
            health = neuron.get('health_status', 'UNKNOWN')
            
            # Map to plot coordinates
            x = plot_area.x + beta * plot_area.width
            y = plot_area.bottom - alpha * plot_area.height
            z_offset = zeta * 20  # Visualize zeta
            
            # Color by health status
            color = STATE_COLORS.get(health, (200, 200, 200))
            
            # Size by confidence
            size = max(2, int(neuron.get('confidence', 0.5) * 8))
            
            pygame.draw.circle(self.screen, color, 
                            (int(x + z_offset), int(y - z_offset)), size)
        
        # Axis labels
        alpha_label = self.small_font.render("α", True, (100, 255, 100))
        beta_label = self.small_font.render("β", True, (100, 200, 255))
        zeta_label = self.small_font.render("ζ", True, (255, 100, 255))
        
        self.screen.blit(alpha_label, (plot_area.x - 15, plot_area.y))
        self.screen.blit(beta_label, (plot_area.right + 5, plot_area.bottom - 10))
        self.screen.blit(zeta_label, (plot_area.right, plot_area.y - 15))
        
        # Statistics
        avg_alpha = np.mean([n.get('eigen_alpha', 0) for n in eigen_data])
        avg_beta = np.mean([n.get('eigen_beta', 0) for n in eigen_data])
        avg_zeta = np.mean([n.get('eigen_zeta', 0) for n in eigen_data])
        
        stats_text = f"α:{avg_alpha:.2f} β:{avg_beta:.2f} ζ:{avg_zeta:.2f}"
        stats_surf = self.small_font.render(stats_text, True, (200, 220, 255))
        stats_rect = stats_surf.get_rect(center=(graph_area.centerx, graph_area.bottom - 15))
        self.screen.blit(stats_surf, stats_rect)
    
    def _draw_matrix_evolution_graph(self, graph_area, current_sequence):
        """Draw matrix evolution over time"""
        if not hasattr(self, 'timeline_builder') or not self.timeline_builder.matrix_registry:
            no_data = self.small_font.render("No matrix evolution data", True, (150, 150, 180))
            no_rect = no_data.get_rect(center=graph_area.center)
            self.screen.blit(no_data, no_rect)
            return
        
        # Find neuron with most matrix history
        max_history = 0
        selected_neuron = None
        
        for neuron_id, registry in self.timeline_builder.matrix_registry.items():
            history_len = len(registry.get('eigen_history', []))
            if history_len > max_history:
                max_history = history_len
                selected_neuron = neuron_id
        
        if not selected_neuron or max_history < 2:
            return
        
        # Get eigen history
        registry = self.timeline_builder.matrix_registry[selected_neuron]
        eigen_history = registry.get('eigen_history', [])
        
        # Draw evolution lines
        padding = 15
        plot_area = pygame.Rect(
            graph_area.x + padding,
            graph_area.y + 40,
            graph_area.width - 2 * padding,
            graph_area.height - 80
        )
        
        # Plot each eigen value
        colors = [(100, 255, 100), (100, 200, 255), (255, 100, 255)]  # α, β, ζ
        labels = ['α', 'β', 'ζ']
        
        for eigen_idx in range(3):  # 0=α, 1=β, 2=ζ
            values = [entry[eigen_idx + 1] for entry in eigen_history]  # +1 for cycle index
            
            if len(values) < 2:
                continue
            
            points = []
            for i, value in enumerate(values):
                x = plot_area.x + (i / max(len(values) - 1, 1)) * plot_area.width
                y = plot_area.bottom - value * plot_area.height
                points.append((x, y))
            
            # Draw line
            if len(points) > 1:
                pygame.draw.lines(self.screen, colors[eigen_idx], False, points, 2)
            
            # Draw current value indicator
            if values:
                last_x = points[-1][0]
                last_y = points[-1][1]
                pygame.draw.circle(self.screen, colors[eigen_idx], 
                                (int(last_x), int(last_y)), 4)
                
                # Label
                label_text = f"{labels[eigen_idx]}:{values[-1]:.2f}"
                label_surf = self.small_font.render(label_text, True, colors[eigen_idx])
                label_rect = label_surf.get_rect(midleft=(last_x + 10, last_y))
                self.screen.blit(label_surf, label_rect)
        
        # Title with neuron info
        neuron_short = selected_neuron[-8:] if len(selected_neuron) > 8 else selected_neuron
        title = f"Matrix Evolution: {neuron_short} ({max_history} cycles)"
        title_surf = self.small_font.render(title, True, (220, 230, 255))
        title_rect = title_surf.get_rect(center=(graph_area.centerx, graph_area.y + 15))
        self.screen.blit(title_surf, title_rect)
    
    def _draw_pattern_bias_graph(self, graph_area, current_sequence):
        """Draw pattern bias vector visualization"""
        if not current_sequence or not current_sequence.get('matrix_relationship_data'):
            no_data = self.small_font.render("No pattern bias data", True, (150, 150, 180))
            no_rect = no_data.get_rect(center=graph_area.center)
            self.screen.blit(no_data, no_rect)
            return
        
        matrix_data = current_sequence['matrix_relationship_data']
        
        # Aggregate pattern probabilities across neurons
        pattern_names = ['DATA_INPUT', 'ACTION_ELEMENT', 'CONTEXT_ELEMENT', 
                        'STRUCTURAL', 'UNKNOWN']
        pattern_totals = {name: [] for name in pattern_names}
        
        for neuron in matrix_data:
            b_vector = neuron.get('b_vector', [])
            if len(b_vector) == 5:  # Should match pattern_names length
                for i, prob in enumerate(b_vector):
                    if i < len(pattern_names):
                        pattern_totals[pattern_names[i]].append(prob)
        
        # Calculate averages
        pattern_avgs = {}
        for pattern, probs in pattern_totals.items():
            pattern_avgs[pattern] = np.mean(probs) if probs else 0
        
        # Draw radial distribution
        center_x = graph_area.centerx
        center_y = graph_area.centery
        radius = min(70, min(graph_area.width, graph_area.height) // 3)
        
        # Draw pie chart
        start_angle = 0
        for i, pattern in enumerate(pattern_names):
            prob = pattern_avgs.get(pattern, 0)
            angle = prob * 360
            
            pattern_color = PATTERN_COLORS.get(pattern, (200, 200, 200))
            
            if angle > 0:
                # Convert to radians
                start_rad = math.radians(start_angle - 90)
                end_rad = math.radians(start_angle + angle - 90)
                
                # Draw segment
                points = [(center_x, center_y)]
                for rad in [start_rad + i * (end_rad - start_rad) / 20 for i in range(21)]:
                    x = center_x + radius * math.cos(rad)
                    y = center_y + radius * math.sin(rad)
                    points.append((x, y))
                
                pygame.draw.polygon(self.screen, pattern_color, points)
                pygame.draw.polygon(self.screen, (255, 255, 255), points, 1)
            
            start_angle += angle
        
        # Draw center circle
        pygame.draw.circle(self.screen, (20, 25, 40), (center_x, center_y), radius // 2)
        
        # Title
        title = "Pattern Bias Distribution"
        title_surf = self.small_font.render(title, True, (220, 230, 255))
        title_rect = title_surf.get_rect(center=(graph_area.centerx, graph_area.y + 15))
        self.screen.blit(title_surf, title_rect)
        
        # Legend
        legend_y = graph_area.bottom - 50
        for i, pattern in enumerate(pattern_names[:3]):  # Show first 3
            label = pattern[:3]
            prob = pattern_avgs.get(pattern, 0)
            label_text = f"{label}: {prob:.2f}"
            
            # Color box
            box_x = graph_area.x + 20 + i * 80
            box_y = legend_y
            pygame.draw.rect(self.screen, PATTERN_COLORS.get(pattern, (200, 200, 200)), 
                           (box_x, box_y, 10, 10))
            
            # Text
            label_surf = self.small_font.render(label_text, True, (200, 220, 255))
            self.screen.blit(label_surf, (box_x + 15, box_y - 3))
    
    def _draw_position_bias_graph(self, graph_area, current_sequence):
        """Draw position bias matrix heatmap"""
        if not current_sequence or not hasattr(self, 'timeline_builder'):
            no_data = self.small_font.render("No position bias data", True, (150, 150, 180))
            no_rect = no_data.get_rect(center=graph_area.center)
            self.screen.blit(no_data, no_rect)
            return
        
        # Find a neuron with matrix data
        matrix_neurons = []
        for neuron in current_sequence.get('neuron_animations', []):
            if neuron.get('matrix_relationships'):
                matrix_neurons.append(neuron)
        
        if not matrix_neurons:
            return
        
        # Use first neuron with matrix data
        neuron = matrix_neurons[0]
        matrix_data = neuron.get('matrix_relationships', {})
        dot_products = matrix_data.get('dot_products', {})
        
        if not dot_products:
            return
        
        # Create 5x5 grid for position biases
        positions = ['parent', 'up', 'down', 'left', 'right']
        padding = 20
        cell_size = min(
            (graph_area.width - 2 * padding) // 6,
            (graph_area.height - 2 * padding) // 6
        )
        
        start_x = graph_area.x + padding
        start_y = graph_area.y + 40
        
        # Draw grid
        for i in range(6):  # 5 positions + labels
            # Horizontal lines
            pygame.draw.line(self.screen, (80, 100, 120),
                           (start_x, start_y + i * cell_size),
                           (start_x + 5 * cell_size, start_y + i * cell_size), 1)
            # Vertical lines
            pygame.draw.line(self.screen, (80, 100, 120),
                           (start_x + i * cell_size, start_y),
                           (start_x + i * cell_size, start_y + 5 * cell_size), 1)
        
        # Draw position labels
        for i, pos in enumerate(positions):
            # Row labels (expectations)
            label_surf = self.small_font.render(pos[:1], True, (200, 220, 255))
            label_rect = label_surf.get_rect(center=(
                start_x + (i + 1) * cell_size + cell_size // 2,
                start_y + cell_size // 2
            ))
            self.screen.blit(label_surf, label_rect)
            
            # Column labels (positions)
            label_surf = self.small_font.render(pos[:1], True, (200, 220, 255))
            label_rect = label_surf.get_rect(center=(
                start_x + cell_size // 2,
                start_y + (i + 1) * cell_size + cell_size // 2
            ))
            self.screen.blit(label_surf, label_rect)
        
        # Fill cells with dot product values
        for i, exp_pos in enumerate(positions):
            for j, obs_pos in enumerate(positions):
                key = f'D_{i}_{j}'
                value = dot_products.get(key, 0.0)
                
                # Color based on value
                if value >= 0.8:
                    color = (100, 255, 100)  # Green
                elif value >= 0.6:
                    color = (150, 255, 150)  # Light Green
                elif value >= 0.4:
                    color = (255, 255, 100)  # Yellow
                elif value >= 0.2:
                    color = (255, 150, 100)  # Orange
                else:
                    color = (255, 100, 100)  # Red
                
                # Draw cell
                cell_rect = pygame.Rect(
                    start_x + (j + 1) * cell_size,
                    start_y + (i + 1) * cell_size,
                    cell_size, cell_size
                )
                
                pygame.draw.rect(self.screen, color, cell_rect)
                
                # Draw value text
                value_text = f"{value:.1f}"
                text_surf = self.small_font.render(value_text, True, (20, 20, 40))
                text_rect = text_surf.get_rect(center=cell_rect.center)
                self.screen.blit(text_surf, text_rect)
        
        # Title
        title = "Position Bias Matrix (Dot Products)"
        title_surf = self.small_font.render(title, True, (220, 230, 255))
        title_rect = title_surf.get_rect(center=(graph_area.centerx, graph_area.y + 15))
        self.screen.blit(title_surf, title_rect)
    
    def _draw_health_states_graph(self, graph_area, current_sequence):
        """Draw health states distribution"""
        if not current_sequence or not current_sequence.get('neuron_animations'):
            no_data = self.small_font.render("No neuron data", True, (150, 150, 180))
            no_rect = no_data.get_rect(center=graph_area.center)
            self.screen.blit(no_data, no_rect)
            return
        
        neurons = current_sequence['neuron_animations']
        
        # Count health states
        state_counts = {}
        for neuron in neurons:
            state = neuron.get('current_state', 'UNKNOWN')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        if not state_counts:
            return
        
        # Draw bar chart
        states = list(state_counts.keys())
        max_count = max(state_counts.values())
        
        bar_width = graph_area.width / max(len(states), 1) * 0.7
        bar_spacing = graph_area.width / max(len(states), 1) * 0.3
        
        for i, state in enumerate(states):
            count = state_counts[state]
            bar_height = (count / max_count) * (graph_area.height - 60)
            
            bar_x = graph_area.x + i * (bar_width + bar_spacing) + bar_spacing / 2
            bar_y = graph_area.bottom - bar_height - 20
            
            # Color by state
            state_color = STATE_COLORS.get(state, (200, 200, 200))
            
            pygame.draw.rect(self.screen, state_color,
                           (bar_x, bar_y, bar_width, bar_height))
            
            # State label
            label = state[:3]
            label_surf = self.small_font.render(label, True, (255, 255, 255))
            label_rect = label_surf.get_rect(center=(
                bar_x + bar_width / 2,
                graph_area.bottom - 10
            ))
            self.screen.blit(label_surf, label_rect)
            
            # Count label
            count_surf = self.small_font.render(str(count), True, (200, 220, 255))
            count_rect = count_surf.get_rect(center=(
                bar_x + bar_width / 2,
                bar_y - 10
            ))
            self.screen.blit(count_surf, count_rect)
        
        # Title
        title = f"Health States: {len(neurons)} neurons"
        title_surf = self.small_font.render(title, True, (220, 230, 255))
        title_rect = title_surf.get_rect(center=(graph_area.centerx, graph_area.y + 15))
        self.screen.blit(title_surf, title_rect)
    
    def _draw_confidence_trend_graph(self, graph_area, current_sequence):
        """Draw confidence trend over recent frames"""
        if not hasattr(self, 'animation_sequences') or len(self.animation_sequences) < 2:
            no_data = self.small_font.render("Need more frames", True, (150, 150, 180))
            no_rect = no_data.get_rect(center=graph_area.center)
            self.screen.blit(no_data, no_rect)
            return
        
        # Extract confidence from last N frames
        frame_count = min(20, len(self.animation_sequences))
        confidences = []
        
        start_idx = max(0, len(self.animation_sequences) - frame_count)
        for i in range(start_idx, len(self.animation_sequences)):
            sequence = self.animation_sequences[i]
            neuron_confs = [n.get('confidence', 0.5) for n in sequence.get('neuron_animations', [])]
            if neuron_confs:
                confidences.append(np.mean(neuron_confs))
        
        if len(confidences) < 2:
            return
        
        # Draw line graph
        points = []
        max_conf = max(confidences) if confidences else 1
        
        padding = 10
        plot_area = pygame.Rect(
            graph_area.x + padding,
            graph_area.y + 40,
            graph_area.width - 2 * padding,
            graph_area.height - 70
        )
        
        for i, conf in enumerate(confidences):
            x = plot_area.x + (i / max(len(confidences) - 1, 1)) * plot_area.width
            y = plot_area.bottom - (conf / max_conf) * plot_area.height
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, (100, 200, 255), False, points, 2)
        
        # Draw confidence points
        for i, point in enumerate(points):
            conf = confidences[i]
            if conf >= 0.8:
                color = (100, 255, 100)
            elif conf >= 0.6:
                color = (150, 255, 150)
            elif conf >= 0.4:
                color = (255, 255, 100)
            elif conf >= 0.2:
                color = (255, 150, 100)
            else:
                color = (255, 100, 100)
            
            pygame.draw.circle(self.screen, color, (int(point[0]), int(point[1])), 3)
        
        # Title with current confidence
        current_conf = confidences[-1] if confidences else 0
        title = f"Confidence Trend: {current_conf:.2f} ({len(confidences)} frames)"
        title_surf = self.small_font.render(title, True, (220, 230, 255))
        title_rect = title_surf.get_rect(center=(graph_area.centerx, graph_area.y + 15))
        self.screen.blit(title_surf, title_rect)
    
    def _draw_pattern_dist_graph(self, graph_area, current_sequence):
        """Draw pattern distribution"""
        if not current_sequence:
            return
        
        neurons = current_sequence.get('neuron_animations', [])
        
        # Count patterns
        pattern_counts = {}
        for neuron in neurons:
            pattern = neuron.get('pattern', 'UNKNOWN')
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        if not pattern_counts:
            return
        
        # Draw radial distribution
        total = sum(pattern_counts.values())
        center_x = graph_area.centerx
        center_y = graph_area.centery
        radius = min(60, min(graph_area.width, graph_area.height) // 3)
        
        # Draw pie segments
        start_angle = 0
        for pattern, count in pattern_counts.items():
            percentage = count / total
            angle = percentage * 360
            
            pattern_color = PATTERN_COLORS.get(pattern, (200, 200, 200))
            
            if angle > 0:
                end_angle = start_angle + angle
                start_rad = math.radians(start_angle - 90)
                end_rad = math.radians(end_angle - 90)
                
                points = [(center_x, center_y)]
                for rad in [start_rad + i * (end_rad - start_rad) / 20 for i in range(21)]:
                    x = center_x + radius * math.cos(rad)
                    y = center_y + radius * math.sin(rad)
                    points.append((x, y))
                
                pygame.draw.polygon(self.screen, pattern_color, points)
                pygame.draw.polygon(self.screen, (255, 255, 255), points, 1)
            
            start_angle += angle
        
        # Draw center circle
        pygame.draw.circle(self.screen, (20, 25, 40), (center_x, center_y), radius // 2)
        
        # Title
        title = f"Pattern Distribution: {total} neurons"
        title_surf = self.small_font.render(title, True, (220, 230, 255))
        title_rect = title_surf.get_rect(center=(graph_area.centerx, graph_area.y + 15))
        self.screen.blit(title_surf, title_rect)
        
        # Legend
        legend_y = graph_area.bottom - 40
        patterns_to_show = list(pattern_counts.keys())[:3]  # Show first 3
        
        for i, pattern in enumerate(patterns_to_show):
            label = pattern[:4]
            count = pattern_counts[pattern]
            
            # Color box
            box_x = graph_area.x + 20 + i * 80
            box_y = legend_y
            pygame.draw.rect(self.screen, PATTERN_COLORS.get(pattern, (200, 200, 200)), 
                           (box_x, box_y, 12, 12))
            
            # Label
            label_text = f"{label}: {count}"
            label_surf = self.small_font.render(label_text, True, (200, 220, 255))
            self.screen.blit(label_surf, (box_x + 15, box_y - 2))
    
    def _draw_axon_activity_graph(self, graph_area, current_sequence):
        """Draw axon activity over time"""
        if not hasattr(self, 'animation_sequences') or len(self.animation_sequences) < 2:
            no_data = self.small_font.render("Need more frames", True, (150, 150, 180))
            no_rect = no_data.get_rect(center=graph_area.center)
            self.screen.blit(no_data, no_rect)
            return
        
        # Count axon types across recent frames
        frame_count = min(15, len(self.animation_sequences))
        axon_types = ['HASH_EXTRACTED', 'NEIGHBOR_DETECTED', 'COORDINATE_VOID', 'HEARTBEAT']
        axon_counts = {atype: [] for atype in axon_types}
        
        start_idx = max(0, len(self.animation_sequences) - frame_count)
        for i in range(start_idx, len(self.animation_sequences)):
            sequence = self.animation_sequences[i]
            axons = sequence.get('axon_animations', [])
            
            for atype in axon_types:
                count = sum(1 for axon in axons if axon.get('axon_type') == atype)
                axon_counts[atype].append(count)
        
        # Find max count for scaling
        max_count = 1
        for counts in axon_counts.values():
            if counts:
                max_count = max(max_count, max(counts))
        
        # Draw lines for each axon type
        colors = {
            'HASH_EXTRACTED': (100, 200, 255),    # Blue
            'NEIGHBOR_DETECTED': (183, 110, 121), # Rose Gold
            'COORDINATE_VOID': (180, 100, 255),   # Purple
            'HEARTBEAT': (150, 150, 150)          # Gray
        }
        
        padding = 10
        plot_area = pygame.Rect(
            graph_area.x + padding,
            graph_area.y + 40,
            graph_area.width - 2 * padding,
            graph_area.height - 70
        )
        
        for atype in axon_types:
            counts = axon_counts[atype]
            if len(counts) < 2:
                continue
            
            points = []
            for i, count in enumerate(counts):
                x = plot_area.x + (i / max(len(counts) - 1, 1)) * plot_area.width
                y = plot_area.bottom - (count / max_count) * plot_area.height
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(self.screen, colors[atype], False, points, 2)
        
        # Title
        current_axons = len(current_sequence.get('axon_animations', [])) if current_sequence else 0
        title = f"Axon Activity: {current_axons} current"
        title_surf = self.small_font.render(title, True, (220, 230, 255))
        title_rect = title_surf.get_rect(center=(graph_area.centerx, graph_area.y + 15))
        self.screen.blit(title_surf, title_rect)
        
        # Legend
        legend_y = graph_area.bottom - 30
        for i, atype in enumerate(axon_types[:2]):  # Show first 2
            label = atype.split('_')[0][:3]
            label_surf = self.small_font.render(label, True, colors[atype])
            self.screen.blit(label_surf, (graph_area.x + 20 + i * 60, legend_y))
    
    # ===== UPDATED GRAPH SETS FOR NEW EXPORTS =====
    
    @property
    def graph_sets(self):
        return {
            "3_eigen_analysis": [
                '3_eigen_system',
                'matrix_evolution',
                'pattern_bias',
                'position_bias'
            ],
            "health_monitoring": [
                'health_states',
                'confidence_trend',
                'pattern_dist',
                'axon_activity'
            ],
            "pattern_analysis": [
                'pattern_bias',
                'pattern_dist',
                'position_bias',
                'health_states'
            ],
            "matrix_analysis": [
                'matrix_evolution',
                'position_bias',
                'pattern_bias',
                '3_eigen_system'
            ]
        }
    
    # ===== HELPER METHODS =====
    
    def _init_stats_surface(self):
        """Initialize statistics surface"""
        self.stats_surface = pygame.Surface((self.screen_width, self.screen_height))
    
    def _draw_stats_header(self):
        """Draw statistics screen header"""
        pygame.draw.rect(self.screen, (20, 25, 40), (0, 0, self.screen_width, 120))
        pygame.draw.rect(self.screen, (60, 80, 120), (0, 118, self.screen_width, 2))
        
        # Title
        title = self.title_font.render("NEXUS 3 EIGEN SYSTEM DASHBOARD", True, (255, 255, 200))
        title_rect = title.get_rect(center=(self.screen_width // 2, 30))
        self.screen.blit(title, title_rect)
        
        # Session info
        session_text = f"Session: {self.session_id[:30]}{'...' if len(self.session_id) > 30 else ''}"
        session_surf = self.font.render(session_text, True, (180, 200, 255))
        self.screen.blit(session_surf, (20, 70))
        
        # Mode info
        mode_text = f"Mode: {self.stats_graph_mode.replace('_', ' ').upper()}"
        mode_surf = self.font.render(mode_text, True, (180, 255, 180))
        mode_rect = mode_surf.get_rect(right=self.screen_width - 20, top=70)
        self.screen.blit(mode_surf, mode_rect)
        
        # Graph info
        graph_set = self.graph_sets.get(self.stats_graph_mode, [])
        graph_text = f"Graphs: {self.current_graph_index + 1}/{len(graph_set)}"
        graph_surf = self.small_font.render(graph_text, True, (200, 220, 255))
        graph_rect = graph_surf.get_rect(right=self.screen_width - 20, top=95)
        self.screen.blit(graph_surf, graph_rect)
        
        # Draw mode buttons
        button_width = 120
        button_height = 30
        button_spacing = 10
        button_y = 70
        
        if not hasattr(self, 'stats_mode_buttons'):
            self.stats_mode_buttons = {}
        
        graph_modes = list(self.graph_sets.keys())
        
        for i, mode in enumerate(graph_modes):
            button_x = 250 + i * (button_width + button_spacing)
            
            if button_x + button_width > self.screen_width - 200:
                continue
            
            is_active = (mode == self.stats_graph_mode)
            button_color = (80, 100, 180) if is_active else (40, 50, 90)
            border_color = (120, 140, 220) if is_active else (60, 80, 120)
            text_color = (255, 255, 255) if is_active else (180, 190, 220)
            
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            self.stats_mode_buttons[mode] = button_rect
            
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
            pygame.draw.rect(self.screen, border_color, button_rect, 2, border_radius=5)
            
            mode_label = mode.replace('_', ' ').title()
            label_surf = self.small_font.render(mode_label, True, text_color)
            label_rect = label_surf.get_rect(center=button_rect.center)
            self.screen.blit(label_surf, label_rect)
        
        # Back button
        back_button = pygame.Rect(20, 70, 80, 30)
        self.stats_back_button = back_button
        
        pygame.draw.rect(self.screen, (60, 80, 160), back_button, border_radius=5)
        pygame.draw.rect(self.screen, (80, 100, 180), back_button, 1, border_radius=5)
        
        back_text = self.small_font.render("← BACK", True, (220, 220, 240))
        back_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_rect)

#==== Main Entry ===== 
def main():
    """
    Main entry point that ALWAYS starts the visualizer in browser mode.
    """
    print("🧠 NEXUS NEURAL VISUALIZER - MAIN LAUNCHER")
    print("=" * 50)
    print("🚀 Starting in BROWSER mode by default...")
    
    # Create Cognition directory if it doesn't exist
    if not os.path.exists("Cognition"):
        os.makedirs("Cognition")
        print("📁 Created Cognition directory")
    
    # Always start in browser mode - ignore any command line arguments
    print("🔍 Initializing visualizer in browser mode...")
    
    try:
        # Force browser mode by passing None as session_id
        visualizer = NexusVisualizer(session_id=None)
        print(f"✅ Visualizer initialized. Mode: {visualizer.mode}")
        
        # Ensure it's in browser mode
        visualizer.mode = visualizer.MODE_BROWSER
        
        # Run the main loop
        visualizer.run()
    except Exception as e:
        print(f"❌ ERROR initializing visualizer: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  If there's a Pygame initialization error, try:")
        print("1. Make sure pygame is installed: pip install pygame-ce")
        print("2. Check your display is available (if running on server/headless)")
        print("3. Try running with: DISPLAY=:0 python cosmic_visualizer.py")

if __name__ == "__main__":
    main()
