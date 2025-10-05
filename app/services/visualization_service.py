# services/visualization_service.py
from typing import List, Dict, Any, Optional
import networkx as nx
from pyvis.network import Network
from datetime import datetime
import os

class VisualizationService:
    def __init__(self):
        """Initialize the VisualizationService."""
        pass

    def create_visual_map(
        self,
        paper_indices: List[int],
    ) -> Dict[str, Any]:
        """
        Create an interactive visualization map of papers.
        
        Args:
            paper_indices: List of paper indices to include in the visualization
            
        Returns:
            Dictionary containing visualization data
        """
        try:
            # Create a networkx graph
            G = nx.Graph()
            
            # Add nodes (papers)
            for idx in paper_indices:
                G.add_node(f"Paper {idx}", title=f"Paper {idx}", group=1)
            
            # Add some sample edges (in a real app, these would be based on paper relationships)
            for i in range(len(paper_indices) - 1):
                G.add_edge(f"Paper {paper_indices[i]}", f"Paper {paper_indices[i+1]}")
            
            # Create a pyvis network
            net = Network(notebook=True, height="500px", width="100%")
            net.from_nx(G)
            
            # Generate HTML string
            html = net.generate_html()
            
            return {
                "visualization_type": "paper_network",
                "format": "html",
                "data": html,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to create visual map: {str(e)}")

    def generate_methodology_flowchart(
        self,
        methods_text: str,
        format: str = 'png'
    ) -> Dict[str, Any]:
        """
        Generate a flowchart from methodology text.
        
        Args:
            methods_text: Text describing the methodology
            format: Output format ('png', 'svg', etc.)
            
        Returns:
            Dictionary containing flowchart data
        """
        try:
            from graphviz import Digraph
            import tempfile
            
            # Create a new Digraph
            dot = Digraph(comment='Methodology Flowchart')
            
            # Simple parsing of steps (this can be enhanced based on your needs)
            steps = [s.strip() for s in methods_text.split('.') if s.strip()]
            
            # Add nodes and edges
            for i, step in enumerate(steps):
                dot.node(str(i), step)
                if i > 0:
                    dot.edge(str(i-1), str(i))
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp:
                file_path = tmp.name
                
            dot.render(file_path, format=format, cleanup=True)
            
            # Read the generated file
            with open(f"{file_path}.{format}", "rb") as f:
                image_data = f.read()
            
            # Clean up
            os.unlink(f"{file_path}.{format}")
            
            return {
                "visualization_type": "methodology_flowchart",
                "format": format,
                "image_data": image_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except ImportError:
            raise RuntimeError("Graphviz is required for generating flowcharts")
        except Exception as e:
            raise RuntimeError(f"Failed to generate flowchart: {str(e)}")

# Singleton instance for easy import
visualization_service = VisualizationService()