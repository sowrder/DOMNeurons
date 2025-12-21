```markdown
# DOMNeurons: Autonomous DOM Neural Unit

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![PDF](https://img.shields.io/badge/Download-Full_PDF_Documentation-red)](paper.pdf)

A 3-part Python-based system for neural pattern recognition in DOM structures, implementing hierarchical transformations, eigen updates, and void handling through membrane-based rerouting.

## 🎯 Overview

DOMNeurons implements an autonomous neural processing unit for DOM element pattern recognition. Each neuron operates at specific coordinates in the DOM tree and follows an exact mathematical workflow to determine which of five patterns best describes its element.

### Core Innovation
- **Relational Encoding**: 25D → 87D transformation preserving structural relationships
- **Eigen Updates**: $\alpha$, $\beta$, $\gamma$, $\zeta$ eigenvalues for pattern certainty
- **Void Handling**: Membrane-based rerouting system for missing DOM elements
- **Tensor Operations**: Multi-dimensional pattern matching with fallback mechanisms

## 🧩 Pattern Definitions

| Pattern | Description | Example Elements |
|---------|-------------|------------------|
| **DATA_INPUT** | Input elements | Text fields, checkboxes, select elements |
| **ACTION_ELEMENT** | Interactive elements | Buttons, links, clickable items |
| **CONTEXT_ELEMENT** | Structural elements | Headers, containers, sections |
| **STRUCTURAL** | Layout elements | Divs, spans, basic structural tags |
| **UNKNOWN** | Fallback pattern | Elements requiring eigen workflow updates |

## 🧮 Mathematical Framework

### Core Transformation: $T$-Encoding
\[
T: \mathbb{R}^{n \times 25} \to \mathbb{R}^{n \times 87}
\]
**Purpose**: Converts attribute vectors to binary relational space with 87 dimensions.

### Dimension Breakdown
\[
87 = \underbrace{15}_{\text{combination features}} + \underbrace{9 \times 8}_{\text{base dimensions} \times \text{questions}}
\]

### Attribute Space $\mathbb{A}$
\[
\mathbb{A} = \mathbb{R}^{25} = \text{Base 9} \cup \{\text{Coverage}\} \cup \text{10 dual} \cup \text{5 triple}
\]

## 🔄 Eigen Update Workflow

### Standard Patterns
```
α (Self-identity) → β (Position assignment) → ζ (Global consistency)
```

### UNKNOWN Pattern
```
α → γ (Neighbor relations) → β → ζ
```

### Eigenvalue Meanings
| Eigenvalue | Symbol | Interpretation |
|------------|--------|----------------|
| **Self-identity** | $\alpha$ | How well element matches self-expectations |
| **Neighbor relations** | $\gamma$ | Consistency with void rerouting support |
| **Position assignment** | $\beta$ | Neighbor expectations vs observations |
| **Global consistency** | $\zeta$ | Across all positions with reroutes |

## 📊 Matrix & Tensor Dimensions

| Data Structure | Dimensions | Description |
|----------------|------------|-------------|
| **Expectation Tensor** | $5 \times 6 \times 25$ | All patterns, all positions |
| **$T$-Transformed** | $5 \times 6 \times 87$ | Relational encoded expectations |
| **Bias Matrix** | $5 \times 5$ | Current position bias |
| **Covariance** | $5 \times 5$ | Position covariance matrix |
| **Gamma Tensor** | $5 \times 5 \times 87$ | Neighbor relations (UNKNOWN only) |

## 🌀 Void Handling System

### Membrane-Based Rerouting
When encountering DOM voids (missing elements), the system:
1. **Registers** void coordinates in membrane state
2. **Searches** for 4 candidate alternatives
3. **Selects** best match using $T$-transform similarity
4. **Reroutes** observations through alternative coordinates

### Similarity Scoring
\[
\text{sim}_k = q_k \cdot p_{\text{orig}}
\]
Where $q_k$ is transformed observation at candidate $k$, and $p_{\text{orig}}$ is original expectation.

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/DOMNeurons.git
cd DOMNeurons

# Install dependencies
pip install -r requirements.txt

# Run basic example
python examples/basic_scan.py
```

### Basic Usage
```python
from src.neuron import Neuron
from src.dom_driver import DOMDriver

# Initialize with DOM driver
driver = DOMDriver()
neuron = Neuron(priori_pattern="UNKNOWN", 
                coordinate=(0, 1, 2), 
                driver=driver)

# Run recognition cycle
result = neuron.process()
print(f"Detected pattern: {result['pattern']}")
print(f"Confidence: {result['confidence']:.2f}")
```

## 📁 Project Structure
```
DOMNeurons/
├── README.md              # This documentation
├── paper.pdf             # Complete mathematical specification
├── requirements.txt      # Python dependencies
├── src/
│   ├── neuron.py         # Main Neuron class implementation
│   ├── transformations.py # T-transformation logic
│   ├── void_handling.py  # Membrane system & rerouting
│   ├── eigen_updates.py  # α, β, γ, ζ calculations
│   └── dom_driver.py     # DOM interaction interface
├── latex/                # LaTeX source documentation
│   ├── main.tex
│   ├── sections/
│   └── figures/
├── examples/             # Usage examples
│   ├── basic_scan.py
│   ├── void_handling_demo.py
│   └── visualization.py
└── tests/               # Test suite
    ├── test_neuron.py
    ├── test_transformations.py
    └── test_void_handling.py
```

## 🔧 Advanced Configuration

### Custom Pattern Definitions
```python
# Define custom pattern expectations
custom_patterns = {
    "CUSTOM_INPUT": {
        "base_dims": [0.8, 0.2, 0.5, ...],  # 25D vector
        "neighbor_expectations": [...]      # 5x25 tensor
    }
}
```

### Void Handling Parameters
```python
# Configure membrane system
neuron.configure_void_handling(
    max_reroute_distance=2,
    similarity_threshold=0.7,
    timeout_seconds=5
)
```

## 📈 Performance

### Time Complexity
| Operation | Complexity | Notes |
|-----------|------------|-------|
| $T$ transformation | $O(n \cdot 225)$ | $n \leq 5$ vectors |
| Eigen decomposition | $O(125)$ | Constant (5×5 matrices) |
| Void candidate search | $O(4 \cdot d^2)$ | $d$ = search depth |
| DOM observation | Variable | Browser-dependent |

### Memory Usage
- Expectation tensors: ~6KB
- $T$-transformed: ~21KB
- Matrix storage: ~2KB
- Void state: Variable (scales with voids)

## 📚 Complete Documentation

### Full Mathematical Specification
For complete details including:
- Phase-by-phase workflow (0-5b)
- Normalization operations
- Competitive assignment algorithm
- Tensor fallback mechanism
- Numerical stability considerations

**[📄 Download Complete PDF Documentation](paper.pdf)**

### LaTeX Source
View and modify the mathematical documentation in [`latex/`](latex/) directory.

## 🧪 Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test module
python -m pytest tests/test_neuron.py -v

# With coverage report
python -m pytest --cov=src tests/
```


- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/DOMNeurons/issues)
- **Documentation**: See [`paper.pdf`](paper.pdf) for complete mathematical details

## 🔗 Related Projects

- [DOMNeuralNet](https://github.com/example/domneuralnet) - Extended neural network for DOM structures
- [WebPatternML](https://github.com/example/webpatternml) - Machine learning for web element classification
- [EigenDOM](https://github.com/example/eigendom) - Spectral methods for DOM analysis

