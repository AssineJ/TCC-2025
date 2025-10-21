import { useEffect, useState } from 'react';
import { FiMoon, FiSun } from 'react-icons/fi';
import VerificationForm from './components/VerificationForm.jsx';
import VerificationResult from './components/VerificationResult.jsx';
import useNewsVerification from './hooks/useNewsVerification.js';
import './App.css';

const THEME_STORAGE_KEY = 'newstrust:theme';

const getInitialTheme = () => {
  if (typeof window === 'undefined') {
    return { theme: 'light', manual: false };
  }

  const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === 'light' || stored === 'dark') {
    return { theme: stored, manual: true };
  }

  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  return { theme: prefersDark ? 'dark' : 'light', manual: false };
};

export default function App() {
  const {
    verifyNews,
    result,
    status,
    reset,
    lastRequest
  } = useNewsVerification();
  const initialTheme = getInitialTheme();
  const [theme, setTheme] = useState(initialTheme.theme);
  const [isManualTheme, setIsManualTheme] = useState(initialTheme.manual);

  useEffect(() => {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    if (isManualTheme) {
      window.localStorage.setItem(THEME_STORAGE_KEY, theme);
    } else {
      window.localStorage.removeItem(THEME_STORAGE_KEY);
    }
  }, [theme, isManualTheme]);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = (event) => {
      if (!isManualTheme) {
        setTheme(event.matches ? 'dark' : 'light');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [isManualTheme]);

  const toggleTheme = () => {
    setTheme((current) => (current === 'light' ? 'dark' : 'light'));
    setIsManualTheme(true);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header__bar">
          <div className="header__content">
            <h1 className="header__title">ConfereAí!</h1>
            <p className="header__subtitle">
              Verificador de Veracidade de Notícias com IA
            </p>
          </div>

          <div className="header__actions">
            <button
              type="button"
              className={`theme-toggle theme-toggle--${theme}`}
              onClick={toggleTheme}
              aria-label={`Alternar para tema ${theme === 'light' ? 'escuro' : 'claro'}`}
            >
              <FiSun className="theme-toggle__icon theme-toggle__icon--sun" aria-hidden />
              <FiMoon className="theme-toggle__icon theme-toggle__icon--moon" aria-hidden />
              <span className="theme-toggle__label">{theme === 'light' ? 'Tema claro' : 'Tema escuro'}</span>
            </button>
          </div>
        </div>
      </header>

      <main className="main">
        <div className="container">
          <section className="verifier">
            <VerificationForm 
              status={status} 
              onSubmit={verifyNews} 
              onReset={reset} 
              lastRequest={lastRequest} 
            />
            <VerificationResult status={status} result={result} />
          </section>

          <section className="how-to">
            <h2>Como utilizar</h2>
            <ol className="how-to__list">
              <li>
                Escolha <strong>URL</strong> ou <strong>Texto</strong> e cole o conteúdo.
              </li>
              <li>
                Clique em <strong>Verificar notícia</strong>.
              </li>
              <li>
                Veja o percentual, confiança e fontes à direita.
              </li>
              <li>
                Abra as fontes para checar os detalhes.
              </li>
            </ol>
          </section>
        </div>
      </main>

      <footer className="footer">
        <p>
          ConfereAí {new Date().getFullYear()} - Verificação com IA e Fontes Confiáveis
        </p>
      </footer>
    </div>
  );
}
