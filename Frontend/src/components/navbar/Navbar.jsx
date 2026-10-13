import {Link, useNavigate} from "react-router-dom";
import './Navbar.css';

const Navbar = () => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        // Here is going to be logging out
        // await signOut(auth); 
        
        // Back to main page
        navigate("/");
    };

    return (
        <nav className="navbar">
            <Link to="/">Translate</Link>
            <Link to="/saved">Saved instructions</Link>
            <Link to="/register">Register</Link>
            <Link to="/log-in">Log In</Link>
            <button onClick={handleLogout}>Log Out</button>
        </nav>
    );
}

export default Navbar;