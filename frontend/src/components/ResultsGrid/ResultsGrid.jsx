import { STYLE_META, STYLE_ORDER } from '../../hooks/useRephrase.js';
import StyleCard from '../StyleCard/StyleCard.jsx';
import styles from './ResultsGrid.module.css';

const ResultsGrid = ({ outputs, state, activeStyle }) => {
  return (
    <section className={styles.wrapper}>
      <header className={styles.header}>
        <div>
          <h2 className={styles.title}>Rephrased styles</h2>
          <p className={styles.subtitle}>
            Each writing style streams in real-time from OpenAI. You can cancel mid-stream and restart with a new idea whenever you are ready.
          </p>
        </div>
      </header>

      <div className={styles.grid}>
        {STYLE_ORDER.map((styleKey) => (
          <StyleCard
            key={styleKey}
            style={styleKey}
            label={STYLE_META[styleKey].label}
            helper={STYLE_META[styleKey].helper}
            content={outputs[styleKey]}
            isActive={activeStyle === styleKey}
            state={state}
          />
        ))}
      </div>
    </section>
  );
};

export default ResultsGrid;
