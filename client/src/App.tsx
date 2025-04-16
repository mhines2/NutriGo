import React from "react";
import { PreferencesProvider } from "./context/PreferencesContext";
import PreferencesForm from "./components/PreferencesForm";
import "./App.css";

const App: React.FC = () => {
  return (
    <PreferencesProvider>
      <div className="app">
        <header className="app-header">
          <h1>NutriGo</h1>
          <p>Find restaurants that match your dietary preferences</p>
        </header>
        <main>
          <PreferencesForm />
        </main>
      </div>
    </PreferencesProvider>
  );
};

export default App;
