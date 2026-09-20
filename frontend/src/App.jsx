import { useState } from "react"; 
import {
  Upload,
  FileText,
  Sparkles,
  CheckCircle,
  XCircle,
  Lightbulb,
} from "lucide-react";
import "./index.css";

function App()
{
  const [file,setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analyzed, setAnalyzed] = useState(false);

  const handleFileChange = (Event) => {
    const selectedFile = Event.target.files[0];

    if(selectedFile) 
    {
      setFile(selectedFile);
    }
  };

  const handleAnalyze = () => {
    if(!file)
    {
      alert("Please upload your resume first.");
      return;
    }
    setAnalyzed(true);
  };
  return (
    <div className="app">
      <nav className="navbar">
        <div className="logo">
          <Sparkles size={25} />
          <span>AI Resumme Analyzer</span>
        </div>

        <div className="nav-links">
          <a href="#home">Home</a>
          <a href="#analyzer">Analyzer</a>
          <a href="#about">About</a>
        </div>
      </nav>

      <section className="hero" id="home">
        <div className="hero-content">
          <p className="badge">AI-Powered Resume Analysis</p>

          <h1>
            Make Your Resume
            <span>Job Ready</span>
          </h1>

          <p className="hero-text">
            Upload your resume and compare it with a job description.
            Get an AI-powered score, missing skills, and improvement
            suggestion.
          </p>

          <a href="#analyzer" className="hero-button">
            Analyze My Resume
          </a>
        </div>
      </section>

      <section className="analyzer-section" id="analyzer">
        <div className="section-heading">
          <h2>Resume Analyzer</h2>
          <p>
            Upload your resume and enter the job description below.
          </p>
        </div>

        <div className="analyzer-container">
          <div className="card">
            <div className="card-title">
              <FileText />
              <h3>Upload Resume</h3>
            </div>

            <label className="upload-box">
              <Upload size={40} />

              <p>
                {file ? file.name : "Click to upload your resume"}
              </p>

              <span>PDF or DOCX</span>

              <input type="text" accept=".pdf,.doc,.docx" onChange={handleFileChange} />
            </label>
          </div>

          <div className="card">
            <div className="card-title">
              <FileText />
              <h3>Job Description</h3>
            </div>

            <textarea placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}/>

            <button className="analyze-button" onClick={handleAnalyze}>
              <Sparkles size={20} />
              Analyze Resume
            </button>
          </div>
        </div>
      </section>

      {analyzed && (
        <section className="result-section">
          <div className="section-heading">
            <h2>Analysis Result</h2>
            <p>Your resume analysis is ready.</p>
          </div>

          <div className="score-card">
            <div className="score">
              <strong>82</strong>
              <span>/100</span>
            </div>

            <div>
              <h3>Good Resume!</h3>
              <p>Your resume matches many of the required skills.</p>
            </div>
          </div>

          <div className="result-grid">
            <div className="result-card">
              <h3>
                <CheckCircle />
                Matching Skills
              </h3>

              <ul>
                <li>Python</li>
                <li>SQL</li>
                <li>Machine Learning</li>
                <li>Pandas</li>
                <li>Data Analysis</li>
              </ul>
            </div>

            <div className="result-card">
              <h3>
                <XCircle />
                Missing Skills
              </h3>

              <ul>
                <li>Docker</li>
                <li>REST API</li>
                <li>Git</li>
              </ul>
            </div>

            <div className="result-card">
              <h3>
                <Lightbulb />
                Suggestions
              </h3>

              <ul>
                <li>Add measurable project achievements.</li>
                <li>Include relevant technical skills.</li>
                <li>Improve project description.</li>
              </ul>
            </div>
          </div>
        </section>
      )}

      <footer id="about">
        <p>
          © 2026 AI Resume Analyzer | Built with React
        </p>
      </footer>
    </div>
  );
}

export default App;