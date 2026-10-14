import { useState } from "react";
import {
  Upload,
  FileText,
  Sparkles,
  CheckCircle,
  XCircle,
  Lightbulb,
} from "lucide-react";
import Login from "./login";
import Signup from "./signup";

import "./index.css";

function App() {

  const [showLogin, setShowLogin] = useState(true);
  const [user, setUser] = useState(null);

  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  const loadHistory = async () => {
  try {
    const response = await fetch(
      "http://127.0.0.1:5000/history"
    );

    const data = await response.json();

    if (data.success) {
      setHistory(data.history);
    } else {
      setError("Could not load analysis history.");
    }

  } catch (error) {
    console.error("Error fetching history:", error);
    setError("Could not connect to the history API.");
  }
};
  // --------------------------------
  // Select resume
  // --------------------------------
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);
      setError("");
      setResult(null);
    }
  };

  // --------------------------------
  // Analyze resume
  // --------------------------------
  const handleAnalyze = async () => {
    if (!file) {
      setError("Please upload your resume first.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Create form data
      const formData = new FormData();

      formData.append("resume", file);
      formData.append("job_description", jobDescription);

      // Send request to Flask
      const response = await fetch(
        "http://127.0.0.1:5000/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      console.log("Response status:", response.status);

      const data = await response.json();

      console.log("Backend response:", data);

      if (!response.ok) {
        throw new Error(data.error || "Analysis failed");
      }

      setResult(data.result);

    } catch (error) {
      console.error("FULL ERROR:", error);

      if (error instanceof TypeError) {
        setError(
          error.message ||
          "Could not connect to the backend."
        );

      }
      else {
        setError(error.message);
      }

    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!result) {
      setError("Please analyze your resume first.");
      return;
    }

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/download_report",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(result),
        }
      );

      if (!response.ok) {
        
        const data = await response.json();

        throw new Error(
          data.error || "Failed to generate report"
        );
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = "AI_Resume_Analysis_Report.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch(error){
      console.error(
        "Download error:", error
      );

      setError(
        error.message || "Could not download report."
      );
    }
  };

  if (!user) {
    if (showLogin) {
      return (
        <Login
          onLogin={(userData) => {
            setUser(userData);
          }}
          onSwitch={() => setShowLogin(false)}
        />
      );
    }
    return (
      <Signup
        onSwitch={() => setShowLogin(true)}
      />
    );
  }

  return (
    
    <div className="app">

      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">
          <Sparkles size={25} />
          <span>AI Resume Analyzer</span>
        </div>

        <div className="nav-links">
          <a href="#home">Home</a>
          <a href="#analyzer">Analyzer</a>
          <a href="#about">About</a>
        </div>
      </nav>

      {/* Hero */}
      <section className="hero" id="home">
        <div className="hero-content">

          <p className="badge">
            AI-Powered Resume Analysis
          </p>

          <h1>
            Make Your Resume
            <span> Job Ready</span>
          </h1>

          <p className="hero-text">
            Upload your resume and compare it with a
            job description to discover matching skills,
            missing skills and improvement opportunities.
          </p>

          <a
            href="#analyzer"
            className="hero-button"
          >
            Analyze My Resume
          </a>

        </div>
      </section>

      {/* Analyzer */}
      <section
        className="analyzer-section"
        id="analyzer"
      >

        <div className="section-heading">
          <h2>Resume Analyzer</h2>

          <p>
            Upload your resume and enter the job
            description.
          </p>
        </div>

        <div className="analyzer-container">

          {/* Resume Upload */}
          <div className="card">

            <div className="card-title">
              <FileText />
              <h3>Upload Resume</h3>
            </div>

            <label className="upload-box">

              <Upload size={40} />

              <p>
                {file
                  ? file.name
                  : "Click to upload your resume"}
              </p>

              <span>
                PDF or DOCX
              </span>

              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileChange}
              />

            </label>

          </div>

          {/* Job Description */}
          <div className="card">

            <div className="card-title">
              <FileText />
              <h3>Job Description</h3>
            </div>

            <textarea
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(e) =>
                setJobDescription(e.target.value)
              }
            />

            {/* Error */}
            {error && (
              <p className="error-message">
                {error}
              </p>
            )}

            {/* Analyze Button */}
            <button
              className="analyze-button"
              onClick={handleAnalyze}
              disabled={loading}
            >

              <Sparkles size={20} />

              {loading
                ? "Analyzing..."
                : "Analyze Resume"}

            </button>

            <button
              type="button"
              onClick={loadHistory}
              className="history-button"
            >
              View Analysis History
            </button>

          </div>

        </div>

      </section>

      {/* Results */}
      {result && (

        <section className="results-section">



          <div className="section-heading">

            <h2>
              Analysis Result
            </h2>

            <p>
              Your resume has been analyzed successfully.
            </p>

          </div>

          {/* Score */}
          <div className="score-card">

            <div className="score">

              <strong>
                {result.score}
              </strong>

              <span>
                /100
              </span>

            </div>
            
            <button className="download-report-button" onClick={handleDownloadReport}>
              Download Analysis Report
            </button>


            <div>

              <h3>
                Resume Score
              </h3>

              <p>
                Suggested Job Role:
                <strong>{result.job_role}</strong>
              </p>

            </div>

          </div>

          <div className="score-breakdown">

            <h3>Score Breakdown</h3>

            <div className="score-item">

              <div>
                <span>Semantic Match</span>
                <strong>
                  {result.semantic_score}%
                </strong>
              </div>

              <div className="progress">
                <div
                  style={{
                    width: `${result.semantic_score}%`
                  }}
                ></div>
              </div>

            </div>

            <div className="score-item">
              <div>
                <span>Skill Match</span>
                <strong>{result.skill_score}%</strong>
              </div>
              <div className="progress">
                <div style={{ width: `${result.skill_score}%` }}></div>
              </div>
            </div>

            <div className="score-item">
              <div>
                <span>Resume Length</span>
                <strong>{result.length_score}%</strong>
              </div>
              <div className="progress">
                <div style={{ width: `${result.length_score}%` }}></div>
              </div>
            </div>

            <div className="score-item">
              <div>
                <span>Resume Sections</span>
                <strong>{result.section_score}%</strong>
              </div>
              <div className="progress">
                <div style={{ width: `${result.section_score}%` }}></div>
              </div>
            </div>


          </div>

          <div className="resume-information">

            <h2>Resume Information</h2>

            <div className="info-grid">
              <div className="info-card">
                <h3>Personal Information</h3>
                <p><strong>Name:</strong> {result.resume_information.name}</p>
                <p><strong>Email:</strong> {result.resume_information.email}</p>
                <p><strong>Phone:</strong> {result.resume_information.phone}</p>
              </div>

              <div className="info-card">
                <h3>Education</h3>
                {result.resume_information.education.length > 0 ? (

                  <ul>
                    {result.resume_information.education.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>
                ) : (
                  <p>No education information available.</p>
                )}
              </div>

              <div className="info-card">
                <h3>Experience</h3>
                {result.resume_information.experience.length > 0 ? (

                  <ul>
                    {result.resume_information.experience.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>

                ) : (
                  <p>No experience information available.</p>
                )}
              </div>

              <div className="info-card">
                <h3>Projects</h3>
                {result.resume_information.projects.length > 0 ? (

                  <ul>
                    {result.resume_information.projects.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>

                ) : (
                  <p>No project information available.</p>
                )}
              </div>

              <div className="info-card">
                <h3>Certifications</h3>

                {result.resume_information.certifications.length > 0 ? (

                  <ul>
                    {result.resume_information.certifications.map(
                      (item, index) => (
                        <li key={index}>{item}</li>
                      )
                    )}
                  </ul>

                ) : (
                  <p>No certification information available.</p>
                )}
              </div>
            </div>
          </div>

          <section className="ats-report">

            <div className="section-heading">
              <h2>ATS Report</h2>
              <p>
                Review how your resume aligns with the
                selected job description.
              </p>
            </div>

            <div className="ats-card">
              <h3>Resume Strengths</h3>
              {result.ats_report.strengths.length > 0 ? (

                <ul>
                  {result.ats_report.strengths.map(
                    (item, index) => (
                      <li key={index}>{item}</li>
                    )
                  )}
                </ul>

              ) : (
                <p>No strengths identified.</p>
              )}
            </div>

            <div className="ats-card">

              <h3>Areas to Improve</h3>

              {result.ats_report.improvements.length > 0 ? (

                <ul>

                  {result.ats_report.improvements.map(
                    (item, index) => (
                      <li key={index}>{item}</li>
                    )
                  )}

                </ul>

              ) : (
                <p>No areas for improvement identified.</p>
              )}

            </div>

            <div className="ats-card">
              <h3>ATS Checklist</h3>
              <div className="checklist">

                {Object.entries(result.ats_report.checklist).map(
                  ([name, passed]) => (
                    <div className="checklist-item" key={name}>
                      <span>{name}</span>
                      <strong>
                        {passed ? "✅" : "❌"}
                      </strong>
                    </div>
                  )
                )}
              </div>
            </div>
          </section>

          {/* Result Cards */}
          <div className="result-grid">

            {/* Matching */}
            <div className="result-card">

              <h3>
                <CheckCircle />
                Matching Skills
              </h3>

              <ul>

                {result.matching_skills.length > 0 ? (

                  result.matching_skills.map(
                    (skill, index) => (
                      <li key={index}>
                        {skill}
                      </li>
                    )
                  )

                ) : (

                  <li>
                    No matching skills found.
                  </li>

                )}

              </ul>

            </div>

            {/* Missing */}
            <div className="result-card">

              <h3>
                <XCircle />
                Missing Skills
              </h3>

              <ul>

                {result.missing_skills.length > 0 ? (

                  result.missing_skills.map(
                    (skill, index) => (
                      <li key={index}>
                        {skill}
                      </li>
                    )
                  )

                ) : (

                  <li>
                    No missing skills found.
                  </li>

                )}

              </ul>

            </div>

            {/* Suggestions */}
            <div className="result-card">

              <h3>
                <Lightbulb />
                Suggestions
              </h3>
              <ul>
                {result.suggestions.map((suggestion, index) => (
                  <li key={index}>
                    {suggestion}
                  </li>
                ))}
              </ul>

            </div>

          </div>

          <div className="resume-info">
            <h3>Resume Information</h3>

            <p>
              Word Count:
              <strong>{result.word_count}</strong>
            </p>

            <p>
              Detected Job Role:
              <strong>{result.job_role}</strong>
            </p>
          </div>

        </section>
      )}

      {history.length > 0 && (
        <section className="history-section">

          <div className="section-heading">
            <h2>Analysis History</h2>
            <p>
              Your previous resume analyses
            </p>
          </div>
          <div className="history-grid">
            {history.map((item) => (
              <div className="history-card" key={item.id}>

                <h3>{item.resume_filename}</h3>
                <p>
                  <strong>Score:</strong>{" "}
                  {item.score} / 100
                </p>
                <p>
                  <strong>Job Role:</strong>{" "}
                  {item.job_role}
                </p>
                <p>
                  <strong>Semantic Match:</strong>{" "}
                  {item.semantic_score}%
                </p>
                <p>
                  <strong>Skill Match:</strong>{" "}
                  {item.skill_score}%
                </p>
                <p>
                  <strong>Word Count:</strong>{" "}
                  {item.word_count}
                </p>
                <p>
                  <strong>Date:</strong>{" "}
                  {item.created_at}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Footer */}
      <footer id="about">

        <p>
          © 2026 AI Resume Analyzer |
          Built with React + Flask
        </p>

      </footer>

    </div>
  );
}

export default App;