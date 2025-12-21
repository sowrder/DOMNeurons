```markdown
# DOMNeurons: Autonomous DOM Neural Unit

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A Python-based system for DOM element pattern recognition using neural processing units with mathematical transformations and eigen updates.

## 🎯 Overview

Each neuron operates at specific DOM coordinates and uses mathematical workflows to classify elements into one of five patterns. The system features relational encoding, eigen updates, and membrane-based void handling.

## 🧩 Pattern Types

| Pattern | Description |
|---------|-------------|
| **DATA_INPUT** | Input elements (text fields, checkboxes) |
| **ACTION_ELEMENT** | Interactive elements (buttons, links) |
| **CONTEXT_ELEMENT** | Structural elements (headers, containers) |
| **STRUCTURAL** | Layout elements (divs, spans) |
| **UNKNOWN** | Fallback pattern with special eigen workflow |

## 🧮 Core Mathematics

### T-Transformation
```
T: ℝ^(n×25) → ℝ^(n×87)
```
Converts 25-dimensional attribute vectors to 87-dimensional relational space.

**Dimension breakdown:**
- 15 combination features
- 9 base dimensions × 8 questions each
- **Total:** 87 dimensions

### Attribute Space
```
𝔸 = ℝ^25 = Base 9 + Coverage + 10 dual + 5 triple
```

### Eigen Update Sequences

**Standard patterns:**
```
α → β → ζ
```

**UNKNOWN pattern:**
```
α → γ → β → ζ
```

**Where:**
- **α** = Self-identity certainty
- **γ** = Neighbor relation consistency (UNKNOWN only)
- **β** = Position assignment quality  
- **ζ** = Global pattern consistency

## 🌀 Void Handling

When DOM elements are missing, the system implements membrane-based rerouting:

1. **Detect** void at coordinate
2. **Register** in membrane state
3. **Search** for 4 candidate alternatives
4. **Select** best match using T-transform similarity
5. **Reroute** observations through alternative coordinate

**Similarity scoring:**
```
sim_k = q_k · p_orig
```
Where `q_k` is transformed observation at candidate k, and `p_orig` is original expectation.

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/yourusername/DOMNeurons.git
cd DOMNeurons
pip install -r requirements.txt
```

### Basic Usage
```python
from src.neuron import Neuron
from src.dom_driver import DOMDriver

# Initialize neuron
driver = DOMDriver()
neuron = Neuron(
    priori_pattern="UNKNOWN",
    coordinate=(0, 1, 2), 
    driver=driver
)

# Process element
result = neuron.process()
print(f"Pattern: {result['pattern']}")
print(f"Confidence: {result['confidence']:.2f}")
```

## 📁 Project Structure
```
DOMNeurons/
├── src/
│   ├── neuron.py          # Main Neuron class
│   ├── transformations.py # T-transformation logic
│   ├── void_handling.py   # Membrane system
│   ├── eigen_updates.py   # α, β, γ, ζ calculations
│   └── dom_driver.py      # DOM interface
├── examples/              # Usage examples
├── tests/                 # Test suite
├── paper.pdf              # Full documentation
└── README.md              # This file
```

## 🔧 Configuration

### Custom Patterns
```python
custom_patterns = {
    "CUSTOM_TYPE": {
        "base_dims": [0.8, 0.2, 0.5, ...],  # 25D vector
        "neighbor_expectations": [...]      # 5x25 tensor
    }
}
```

### Void Parameters
```python
neuron.configure_void_handling(
    max_reroute_distance=2,
    similarity_threshold=0.7,
    timeout_seconds=5
)
```

## 📊 Performance

| Operation | Complexity | Notes |
|-----------|------------|-------|
| T-transformation | O(n×225) | n ≤ 5 vectors |
| Eigen decomposition | O(125) | Constant (5×5 matrices) |
| Void search | O(4×d²) | d = search depth |

**Memory:**
- Expectation tensors: ~6KB
- T-transformed: ~21KB
- Matrix storage: ~2KB

## 📚 Documentation

**[Download Full PDF Documentation](paper.pdf)** - Complete mathematical specification including:
- Phase-by-phase workflow (0-5b)
- Normalization operations
- Competitive assignment algorithm
- Tensor fallback mechanism

## 🧪 Testing
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

