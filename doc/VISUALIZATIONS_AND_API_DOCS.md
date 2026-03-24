# Visualizations and API Documentation

This document describes the new visualization and API documentation features added to the RAG Demo.

## 📖 Swagger API Documentation

We've integrated **Swagger/OpenAPI** documentation for all REST API endpoints using **Flasgger**.

### Accessing API Docs

Open your browser and navigate to:
```
http://localhost:5000/api/docs
```

### Features

- **Interactive API explorer** - Test all endpoints directly from the browser
- **Complete request/response schemas** - See exact data formats for all endpoints
- **Try it out** - Execute API calls with sample data
- **Organized by tags** - Endpoints grouped by functionality:
  - Documents - Add, list, delete documents
  - Query - Ask questions to the RAG system
  - Configuration - Manage sample documents
  - Conversations - Save and load conversation history
  - Visualizations - Get visualization data

### Example Usage

1. Navigate to http://localhost:5000/api/docs
2. Click on any endpoint (e.g., "POST /api/query")
3. Click "Try it out"
4. Enter your request data
5. Click "Execute" to see the response

### Documented Endpoints

All major endpoints are fully documented:

- `POST /api/add` - Add a document to the knowledge base
- `GET /api/documents` - Get all documents
- `POST /api/query` - Query the RAG system with a question
- `GET /api/config` - Get current configuration
- `GET /api/conversations` - List saved conversations
- `POST /api/conversations` - Save a conversation
- `GET /api/visualizations/data` - Get visualization data

## 📊 Knowledge Base Visualizations

Interactive visualizations of your document embeddings and similarities using **Plotly.js**.

### Accessing Visualizations

Open your browser and navigate to:
```
http://localhost:5000/visualizations
```

Or click the **"📊 Visualizations"** link in the main UI header.

### Available Visualizations

#### 1. Statistics Dashboard

Quick overview of your knowledge base:
- Total number of documents
- Embedding dimensions (default: 384)
- Average document length
- Maximum document length

#### 2. 2D Document Embeddings (t-SNE)

**What it shows:**
- Each document as a point in 2D space
- Documents plotted using t-SNE dimensionality reduction
- Color-coded by document index
- Interactive hover to see document text

**What it means:**
- Points close together = semantically similar documents
- Points far apart = different topics/content
- Clusters indicate groups of related documents

**Use cases:**
- Identify duplicate or very similar documents
- Discover topic clusters in your knowledge base
- Find outliers or unique documents

#### 3. 3D Document Embeddings (t-SNE)

**What it shows:**
- Same as 2D but with an additional dimension
- Interactive 3D rotation and zoom
- Better separation of document clusters

**Benefits over 2D:**
- More accurate representation of document relationships
- Better visualization of complex document spaces
- Clearer cluster boundaries

#### 4. Cosine Similarity Heatmap

**What it shows:**
- Matrix showing similarity between every pair of documents
- Values range from 0 (completely different) to 1 (identical)
- Color-coded: white (low similarity) to red (high similarity)
- Similarity values displayed in each cell

**How to read it:**
- Diagonal is always 1.0 (document similarity to itself)
- Symmetric matrix (similarity is bidirectional)
- High values (>0.8) = very similar documents
- Low values (<0.3) = unrelated documents

**Use cases:**
- Find duplicate or near-duplicate content
- Identify which documents are most related
- Discover unexpected similarities
- Validate document diversity in your knowledge base

### Technical Details

#### Dimensionality Reduction

The original embeddings have 384 dimensions (from the sentence-transformers model). We use:

1. **PCA (Principal Component Analysis)** - First reduce to 50 dimensions if needed
2. **t-SNE (t-Distributed Stochastic Neighbor Embedding)** - Then reduce to 2D or 3D for visualization

**Why t-SNE?**
- Preserves local structure (similar documents stay close)
- Better for visualization than PCA alone
- Creates distinct clusters

**Parameters used:**
- Perplexity: min(30, num_docs - 1)
- Random state: 42 (for reproducibility)

#### Cosine Similarity

Measures the cosine of the angle between two document vectors:

```
similarity = (doc1 · doc2) / (||doc1|| × ||doc2||)
```

- Range: 0 to 1 for normalized vectors
- 1.0 = identical direction (very similar)
- 0.0 = perpendicular (unrelated)

### Limitations

- **Minimum documents**: Need at least 2 documents for meaningful visualizations
- **t-SNE requirements**: Works best with 3+ documents
- **Performance**: Large knowledge bases (1000+ docs) may take a few seconds to compute
- **Non-deterministic**: t-SNE results may vary slightly between runs (despite random_state)

### Tips for Best Results

1. **Add diverse documents** - Too similar documents won't show interesting patterns
2. **Meaningful clusters** - 10+ documents work better for cluster visualization
3. **Refresh after changes** - Click "🔄 Refresh" after adding/removing documents
4. **Explore 3D view** - Click and drag to rotate, scroll to zoom
5. **Hover for details** - Mouse over points to see document text

## Implementation Details

### Dependencies Added

```toml
"flasgger>=0.9.7"  # Swagger/OpenAPI integration for Flask
"plotly>=5.14.0"   # Interactive visualizations
"scikit-learn>=1.3.0"  # t-SNE and PCA for dimensionality reduction
```

### New Files

- `templates/visualizations.html` - Visualization page template
- `doc/VISUALIZATIONS_AND_API_DOCS.md` - This file

### New Routes

- `GET /visualizations` - Render visualization page
- `GET /api/visualizations/data` - API endpoint returning visualization data
- `GET /api/docs` - Swagger UI (configured via Flasgger)

### Code Structure

**app.py additions:**
```python
from flasgger import Swagger

# Swagger configuration
swagger_config = {...}
swagger_template = {...}
swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Visualization endpoint
@app.route("/api/visualizations/data")
def get_visualization_data():
    # Compute t-SNE projections
    # Calculate similarity matrix
    # Return JSON data
```

**templates/visualizations.html:**
```html
<!-- Uses Plotly.js for interactive charts -->
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

<!-- Charts rendered via JavaScript -->
Plotly.newPlot('plot-2d', data2d, layout2d)
Plotly.newPlot('plot-3d', data3d, layout3d)
Plotly.newPlot('plot-heatmap', heatmap, layoutHeatmap)
```

## Future Enhancements

Potential improvements:

1. **More visualization types:**
   - Document length distribution histogram
   - Query-document similarity over time
   - Embedding drift visualization

2. **Interactive features:**
   - Click document to highlight in all charts
   - Filter documents by similarity threshold
   - Export charts as images

3. **Performance optimizations:**
   - Cache t-SNE results
   - Incremental updates for new documents
   - WebGL rendering for large datasets

4. **Additional algorithms:**
   - UMAP as alternative to t-SNE
   - Hierarchical clustering dendrograms
   - Topic modeling (LDA) visualization

## Troubleshooting

### Visualizations not loading

1. Check browser console for errors
2. Ensure JavaScript is enabled
3. Try refreshing the page
4. Verify documents exist in knowledge base

### API docs not accessible

1. Ensure Flask app is running
2. Check that flasgger is installed: `uv run pip list | grep flasgger`
3. Verify no port conflicts on 5000

### t-SNE taking too long

- Expected for 500+ documents
- Consider reducing perplexity
- Use PCA-only for very large datasets

## Resources

- [Flasgger Documentation](https://github.com/flasgger/flasgger)
- [Plotly Python Documentation](https://plotly.com/python/)
- [t-SNE Explained](https://distill.pub/2016/misread-tsne/)
- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
