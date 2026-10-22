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
            <div className="navbar-left">
                <Link to="/">Translate</Link>
            </div>

            <div className="navbar-center">
                <Link to="/saved">Saved instructions</Link>
            </div>
            
            <div className="navbar-right">
                <Link to="/register">Register</Link>
                <Link to="/log-in">Log In</Link>
                <button onClick={handleLogout}>Log Out</button>
            </div>
        </nav>
    );
}

export default Navbar;