# services/visualization_service.py
from typing import List, Dict, Any, Optional
import networkx as nx
from pyvis.network import Network
from datetime import datetime
from app_state import AppState
import tempfile
import os

class VisualizationService:
    def __init__(self, app_state: Optional[AppState] = None):
        """Initialize with optional app state injection."""
        self.app_state = app_state or AppState()

    async def create_visual_map(
        self,
        paper_indices: List[int],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an interactive visualization map of papers.
        
        Args:
            paper_indices: List of paper indices to include in the visualization
            session_id: Optional session ID for tracking
            
        Returns:
            Dictionary containing visualization data and session info
        """
        # Initialize session if needed
        if session_id:
            session_data = self.app_state.get_user_state(session_id)
            if not session_data:
                raise ValueError("No session data found for the provided session ID")
        else:
            session_id = f"viz_{int(datetime.now().timestamp())}"
            session_data = self.app_state.get_user_state(session_id)
            session_data.synthesis_storage.update({
                "created_at": datetime.now().isoformat(),
                "type": "visualization_map"
            })

        # Get papers from session data
        papers = [session_data.search_results[i] for i in paper_indices 
                 if 0 <= i < len(session_data.search_results)]

        if not papers:
            raise ValueError("No valid papers found for visualization")

        try:
            # Create graph
            G = nx.Graph()
            for i, paper in enumerate(papers):
                G.add_node(
                    f"paper_{i}",
                    label=paper.get('title', f'Paper {i+1}'),
                    title=paper.get('abstract', ''),
                    group=1
                )
            
            # Add edges between related papers
            for i in range(len(papers)):
                for j in range(i + 1, len(papers)):
                    if i != j:
                        G.add_edge(f"paper_{i}", f"paper_{j}", value=1)
            
            # Generate visualization
            net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
            net.from_nx(G)
            net.force_atlas_2based()
            net.show_buttons(filter_=['physics'])
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                net.save_graph(tmp.name)
                html_content = tmp.read().decode('utf-8')
                os.unlink(tmp.name)
            
            # Store results in session
            result = {
                "session_id": session_id,
                "visualization_type": "paper_network",
                "papers_included": [p.get("title") for p in papers],
                "html_content": html_content,
                "timestamp": datetime.now().isoformat()
            }
            
            session_data.synthesis_storage["latest_visualization"] = result
            session_data.synthesis_storage["last_activity"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate visualization: {str(e)}")

    async def generate_methodology_flowchart(
        self,
        methods_text: str,
        session_id: Optional[str] = None,
        format: str = 'png'
    ) -> Dict[str, Any]:
        """
        Generate a flowchart from methodology text.
        
        Args:
            methods_text: Text describing the methodology
            session_id: Optional session ID for tracking
            format: Output format ('png', 'svg', etc.)
            
        Returns:
            Dictionary containing flowchart data and session info
        """
        # Initialize session if needed
        if session_id:
            session_data = self.app_state.get_user_state(session_id)
            if not session_data:
                raise ValueError("No session data found for the provided session ID")
        else:
            session_id = f"flowchart_{int(datetime.now().timestamp())}"
            session_data = self.app_state.get_user_state(session_id)
            session_data.synthesis_storage.update({
                "created_at": datetime.now().isoformat(),
                "type": "methodology_flowchart"
            })

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
            
            # Store results in session
            result = {
                "session_id": session_id,
                "visualization_type": "methodology_flowchart",
                "format": format,
                "image_data": image_data,
                "timestamp": datetime.now().isoformat()
            }
            
            session_data.synthesis_storage["latest_visualization"] = result
            session_data.synthesis_storage["last_activity"] = datetime.now().isoformat()
            
            return result
            
        except ImportError:
            raise RuntimeError("Graphviz is required for generating flowcharts")
        except Exception as e:
            raise RuntimeError(f"Failed to generate flowchart: {str(e)}")

# Singleton instance for easy import
visualization_service = VisualizationService()