import { useState } from "react";

function Signup({ onSwitch }) {

    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const handleSignup = async (e) => {
        e.preventDefault();

        try 
        {
            const response = await fetch("http://127.0.0.1:5000/signup", {
                method: "POST",
                headers: 
                {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name, email, password }),
            });
            const data = await response.json();

            if (data.success) 
            {
                setMessage("Account created successfully!");

                setTimeout(() => {
                    onSwitch();
                }, 1000);
            }
            else 
            {
                setMessage(data.error);
            }
        } 
        catch (error) 
        {
            setMessage("Unable to connect to server");
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">

                <h1>Create Account</h1>

                <p> Create your AI Resume Analyzer account</p>

                <form onSubmit={handleSignup}>
                    <input
                        type="text"
                        placeholder="Full Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit">Sign Up</button>
                </form>
                {message && <p className="auth-message">{message}</p>}
                <p className="switch-auth">
                    Already have an account?

                    <button
                        type="button"
                        onClick={onSwitch}
                    >
                        Login
                    </button>
                </p>
            </div>
        </div>
    );
}

export default Signup;