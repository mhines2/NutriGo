import React from "react";
import { PreferencesProvider } from "./context/PreferencesContext";
import PreferencesForm from "./components/PreferencesForm";
import "./App.css";

const App: React.FC = () => {
  return (
    <PreferencesProvider>
      <div className="app-container">
        <header className="header">
          <div className="container">
            <h1>NutriGo</h1>
            <p>
              Discover restaurants that match your dietary goals — powered by
              AI, built for you.
            </p>
          </div>
        </header>

        <main className="main-content">
          <div className="container">
            <PreferencesForm />
          </div>
        </main>

        <footer className="footer">
          <div className="container">
            <p>
              &copy; {new Date().getFullYear()} Team John Cena. All rights
              reserved.
            </p>
          </div>
        </footer>
      </div>
    </PreferencesProvider>
  );
};

export default App;
