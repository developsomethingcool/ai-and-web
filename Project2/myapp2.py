from flask import Flask, request, render_template_string
from whoosh.index import open_dir, create_in
from whoosh.fields import Schema, TEXT, ID
from bs4 import BeautifulSoup  # For cleaning up highlight HTML
import os 

app = Flask(__name__)

# Open the Whoosh index
index_dir = "indexdir"

def initialize_index(index_dir):
    """Initialize Whoosh index if it does not exist."""
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    if not os.listdir(index_dir):  # Check if directory is empty
        schema = Schema(
            url=ID(stored=True, unique=True),
            title=TEXT(stored=True),
            content=TEXT(stored=True)
        )
        create_in(index_dir, schema)

# Ensure the index directory exists before opening it
initialize_index(index_dir)

# Open the existing Whoosh index
ix = open_dir(index_dir)

# HTML Templates
search_form_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Easy Search</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(5deg); }
        }

        @keyframes slideIn {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        :root {
            --primary: #00ff9d;
            --secondary: #00cf81;
            --dark: #001a1a;
            --light: #ffffff;
            --accent: #ff3e6c;
        }

        body {
            min-height: 100vh;
            background: linear-gradient(-45deg, #001a1a, #003333, #004d4d, #006666);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 10vh;
            overflow-x: hidden;
        }

        .particle {
            position: fixed;
            pointer-events: none;
            opacity: 0.5;
            z-index: 0;
        }

        .cursor-glow {
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(0, 255, 157, 0.2), transparent 70%);
            position: fixed;
            pointer-events: none;
            transform: translate(-50%, -50%);
            z-index: 1;
            mix-blend-mode: screen;
        }

        .logo-container {
            position: relative;
            margin-bottom: 3rem;
            text-align: center;
            z-index: 2;
        }

        .logo {
            font-size: 4rem;
            font-weight: 900;
            background: linear-gradient(45deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);
            animation: pulse 3s infinite ease-in-out;
        }

        .logo-glow {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 120%;
            height: 120%;
            background: radial-gradient(circle, rgba(0, 255, 157, 0.2), transparent 70%);
            filter: blur(20px);
            z-index: -1;
        }

        .subtitle {
            color: var(--light);
            font-size: 1.2rem;
            margin-top: 1rem;
            opacity: 0.8;
            letter-spacing: 2px;
        }

        .search-container {
            position: relative;
            width: 90%;
            max-width: 700px;
            z-index: 2;
            animation: slideIn 1s ease-out;
        }

        .search-bar {
            position: relative;
            display: flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 30px;
            padding: 0.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2),
                        inset 0 0 10px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .search-bar:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        }

        .search-icon {
            padding: 0.8rem;
            color: var(--dark);
            font-size: 1.2rem;
            animation: float 3s infinite ease-in-out;
        }

        .search-input {
            flex: 1;
            padding: 1rem 1.5rem;
            border: none;
            background: transparent;
            font-size: 1.1rem;
            color: var(--dark);
            outline: none;
        }

        .search-button {
            background: linear-gradient(45deg, var(--secondary), var(--primary));
            color: var(--dark);
            border: none;
            padding: 1rem 2.5rem;
            border-radius: 25px;
            font-weight: 600;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .search-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
            transition: 0.5s;
        }

        .search-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 207, 129, 0.4);
        }

        .search-button:hover::before {
            left: 100%;
        }

        .category-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 2rem;
            margin-top: 3rem;
            z-index: 2;
        }

        .category-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            color: var(--light);
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .category-card:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-5px);
        }

        .category-card i {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: var(--primary);
        }

        .suggestions {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.95);
            margin-top: 1rem;
            border-radius: 15px;
            padding: 1rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            display: none;
        }

        .suggestion-item {
            padding: 0.8rem 1rem;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.2s ease;
        }

        .suggestion-item:hover {
            background: rgba(0, 207, 129, 0.1);
        }

        @media (max-width: 768px) {
            .category-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
            }

            .logo {
                font-size: 3rem;
            }

            .search-bar {
                flex-direction: column;
                padding: 1rem;
            }

            .search-button {
                width: 100%;
                margin-top: 1rem;
            }
        }

        /* Add animated particles */
        .particles-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }

        .particle {
            position: absolute;
            background: var(--primary);
            border-radius: 50%;
            opacity: 0.3;
            animation: particleFloat 20s infinite linear;
        }

        @keyframes particleFloat {
            0% {
                transform: translateY(0) rotate(0deg);
            }
            100% {
                transform: translateY(-100vh) rotate(360deg);
            }
        }
    </style>
</head>
<body>
    <!-- Animated background particles -->
    <div class="particles-container" id="particles"></div>
    
    <!-- Cursor glow effect -->
    <div class="cursor-glow"></div>

    <div class="logo-container">
        <div class="logo-glow"></div>
        <h1 class="logo">EASY SEARCH</h1>
        <p class="subtitle">You search it, we find it.</p>
    </div>

    <div class="search-container">
        <form class="search-bar" action="/search" method="get">
            <i class="fas fa-search search-icon"></i>
            <input 
                type="text" 
                class="search-input" 
                placeholder="What are you looking for?" 
                name="q" 
                autocomplete="off"
                required
            >
            <button type="submit" class="search-button">
                <i class="fas fa-arrow-right"></i> SEARCH
            </button>
        </form>
        <div class="suggestions">
            <!-- Dynamic suggestions will be inserted here -->
        </div>
    </div>

    <div class="category-grid">
        <div class="category-card">
            <i class="fas fa-gamepad"></i>
            <h3>Games</h3>
        </div>
        <div class="category-card">
            <i class="fas fa-music"></i>
            <h3>Music</h3>
        </div>
        <div class="category-card">
            <i class="fas fa-video"></i>
            <h3>Videos</h3>
        </div>
        <div class="category-card">
            <i class="fas fa-camera"></i>
            <h3>Photos</h3>
        </div>
    </div>

    <script>
        // Add floating particles
        function createParticles() {
            const container = document.getElementById('particles');
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.width = Math.random() * 5 + 'px';
                particle.style.height = particle.style.width;
                particle.style.left = Math.random() * 100 + 'vw';
                particle.style.animationDuration = Math.random() * 10 + 10 + 's';
                particle.style.animationDelay = Math.random() * 5 + 's';
                container.appendChild(particle);
            }
        }

        // Cursor glow effect
        document.addEventListener('mousemove', (e) => {
            const cursor = document.querySelector('.cursor-glow');
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });

        // Initialize
        createParticles();
    </script>
</body>
</html>
"""
search_results_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results</title>
    <style>
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        @keyframes slideIn {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        @keyframes particleFloat {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-100vh) rotate(360deg); }
        }

        body {
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(120deg, #001a1a, #004d4d);
            background-size: 200% 200%;
            animation: gradientBG 10s ease infinite;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .cursor-glow {
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(0, 255, 157, 0.3), transparent 70%);
            position: fixed;
            pointer-events: none;
            transform: translate(-50%, -50%);
            z-index: 10;
            mix-blend-mode: screen;
        }

        .container {
            width: 90%;
            max-width: 800px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
            padding: 20px 30px;
            animation: slideIn 0.8s ease;
        }

        h1 {
            font-size: 2.5rem;
            text-align: center;
            color: #00ff9d;
            margin-bottom: 15px;
            animation: float 3s ease-in-out infinite;
        }

        p {
            text-align: center;
            font-size: 1.2rem;
            color: #e0f7fa;
            margin-bottom: 20px;
        }

        .result-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            color: #333;
            transition: all 0.3s ease;
        }

        .result-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }

        .result-card a {
            color: #00cf81;
            font-weight: bold;
            font-size: 1.2rem;
            text-decoration: none;
        }

        .result-card a:hover {
            color: #ff3e6c;
            text-decoration: underline;
        }

        .result-snippet {
            font-size: 1rem;
            margin-top: 10px;
            color: #555;
        }

        .back-link {
            display: block;
            text-align: center;
            font-size: 1rem;
            color: #00ff9d;
            margin-top: 20px;
            text-decoration: none;
            transition: all 0.3s ease;
        }

        .back-link:hover {
            color: #ff3e6c;
            text-shadow: 0 0 5px #00ff9d;
        }

        .particles-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }

        .particle {
            position: absolute;
            background: #00ff9d;
            border-radius: 50%;
            opacity: 0.6;
            animation: particleFloat 10s infinite linear;
        }
    </style>
</head>
<body>
    <!-- Cursor Glow -->
    <div class="cursor-glow"></div>

    <div class="particles-container" id="particles"></div>

    <div class="container">
        <h1>Search Results</h1>
        <p>Query: <b>{{ query }}</b></p>
        <div>
        {% for result in results %}
            <div class="result-card">
                <a href="{{ result['url'] }}" target="_blank"><b>{{ result['title'] }}</b></a>
                <p class="result-snippet">{{ result['content'] }}</p>
            </div>
        {% endfor %}
        </div>
        <a href="/" class="back-link">Go back to search</a>
    </div>

    <script>
        // Create floating particles
        function createParticles() {
            const container = document.getElementById('particles');
            for (let i = 0; i < 50; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.width = Math.random() * 6 + 'px';
                particle.style.height = particle.style.width;
                particle.style.left = Math.random() * 100 + 'vw';
                particle.style.animationDuration = Math.random() * 10 + 5 + 's';
                particle.style.animationDelay = Math.random() * 5 + 's';
                container.appendChild(particle);
            }
        }

        // Cursor glow effect
        document.addEventListener('mousemove', (e) => {
            const cursor = document.querySelector('.cursor-glow');
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });

        createParticles();
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(search_form_template)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()  # Strip whitespace
    if not query:
        return render_template_string("""
        <h1>Error</h1>
        <p>Please enter a valid search query.</p>
        <a href="/">Go back to search</a>
        """), 400  # Return 400 Bad Request

    results = []
    try:
        with ix.searcher() as searcher:  # Query the Whoosh index
            parser = QueryParser("content", ix.schema)
            parsed_query = parser.parse(query)
            hits = searcher.search(parsed_query, limit=10)
            for hit in hits:
                results.append({
                    "url": hit["url"],  # The page URL
                    "title": hit["title"],  # The page title
                    "content": BeautifulSoup(hit.highlights("content"), "html.parser").get_text()
                })

        if not results:
            return render_template_string("""
            <h1>No Results Found</h1>
            <p>No pages matched your query: <b>{{ query }}</b>.</p>
            <a href="/">Go back to search</a>
            """, query=query)

    except Exception as e:
        print(f"Search error: {e}")
        return render_template_string("""
        <h1>Error</h1>
        <p>An error occurred while processing your search query. Please try again later.</p>
        <a href="/">Go back to search</a>
        """), 500  # Return 500 Internal Server Error

    return render_template_string(search_results_template, query=query, results=results)

if __name__ == "__main__":
    app.run(debug=True)
