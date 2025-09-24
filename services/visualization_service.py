from typing import List, Dict, Any, Optional
import networkx as nx
from pyvis.network import Network

class VisualizationService:
    @staticmethod
    async def create_visual_map(
        papers: List[Dict[str, Any]],
        max_related: int = 5
    ) -> str:
        try:
            G = nx.Graph()
            for i, paper in enumerate(papers):
                G.add_node(
                    f"paper_{i}",
                    label=paper.get('title', f'Paper {i+1}'),
                    title=paper.get('abstract', ''),
                    group=1
                )
            
            for i in range(len(papers)):
                for j in range(i + 1, len(papers)):
                    if i != j:
                        G.add_edge(f"paper_{i}", f"paper_{j}", value=1)
            
            net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
            net.from_nx(G)
            net.force_atlas_2based()
            net.show_buttons(filter_=['physics'])
            return net.generate_html()
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate visualization: {str(e)}")

    @staticmethod
    async def generate_methodology_flowchart(
        methods_text: str,
        format: str = 'png'
    ) -> str:
        """
        Generate a flowchart from methodology text.
        
        Args:
            methods_text: Text describing the methodology
            format: Output format ('png', 'svg', etc.)
            
        Returns:
            Path to the generated flowchart file
        """
        try:
            import tempfile
            from graphviz import Digraph
            
            dot = Digraph(comment='Methodology Flowchart')
            steps = [s.strip() for s in methods_text.split('.') if s.strip()]
            
            for i, step in enumerate(steps[:10]):
                dot.node(f'step_{i}', step[:50] + '...' if len(step) > 50 else step)
                if i > 0:
                    dot.edge(f'step_{i-1}', f'step_{i}')
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{format}') as tmp:
                dot.render(tmp.name, format=format, cleanup=True)
                return tmp.name + f'.{format}'
                
        except ImportError:
            raise ImportError("Graphviz is required for flowchart generation. Please install it first.")
        except Exception as e:
            raise RuntimeError(f"Failed to generate methodology flowchart: {str(e)}")
