import { useEffect, useMemo, useState } from 'react';
import styles from './App.module.css';
import ThemeToggle from './components/ThemeToggle/ThemeToggle.jsx';
import PromptForm from './components/PromptForm/PromptForm.jsx';
import ResultsGrid from './components/ResultsGrid/ResultsGrid.jsx';
import { STYLE_ORDER, useRephrase } from './hooks/useRephrase.js';

const getInitialTheme = () => {
  if (typeof window === 'undefined') {
    return 'light';
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const App = () => {
  const [theme, setTheme] = useState(() => getInitialTheme());
  const [prompt, setPrompt] = useState('');
  const { outputs, state, process, cancel, isProcessing, activeStyle, reset } = useRephrase();

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('theme-light', 'theme-dark');
    root.classList.add(`theme-${theme}`);
  }, [theme]);

  useEffect(() => {
    if (!prompt.trim() && state !== 'idle' && !isProcessing) {
      reset();
    }
  }, [prompt, reset, state, isProcessing]);

  const handleSubmit = (text) => {
    process(text);
  };

  const handleCancel = () => {
    cancel();
  };

  const heroBadge = useMemo(() => {
    const modeLabel = state === 'processing' ? 'Streaming' : 'Ready';
    return `${STYLE_ORDER.length} Styles · Instant · ${modeLabel}`;
  }, [state]);


  return (
    <div className={styles.appShell}>
      <div className={styles.inner}>
        <section className={styles.hero}>
          <div className={styles.heroHeader}>
            <h1 className={styles.heroTitle}>AI Writing Assistant</h1>
            <p className={styles.heroSubtitle}>Transform text into multiple formats</p>
          </div>
          <ThemeToggle value={theme} onChange={setTheme} disabled={isProcessing} />
        </section>

        <div className={styles.panelCluster}>
          <PromptForm
            value={prompt}
            onChange={setPrompt}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isProcessing={isProcessing}
            state={state}
          />

          <ResultsGrid outputs={outputs} state={state} activeStyle={activeStyle} />
        </div>
      </div>
    </div>
  );
};

export default App;
