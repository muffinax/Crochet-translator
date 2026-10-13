import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/navbar/Navbar";
import Translator from "./pages/translator/Translator";
import Saved from "./pages/Saved";
import Register from "./pages/Register";
import LogIn from "./pages/LogIn";

function App() {

  return (
    <BrowserRouter>
      <Navbar />
      <div className="container">
      <Routes>
        <Route path="/" element={<Translator />} />
        <Route path="/saved" element={<Saved />} />
        <Route path="/register" element={<Register />} />
        <Route path="/log-in" element={<LogIn />} />
      </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
