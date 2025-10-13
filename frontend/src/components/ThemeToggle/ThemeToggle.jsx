import styles from './ThemeToggle.module.css';

const ThemeToggle = ({ value, onChange, disabled = false }) => {
  return (
    <div className={styles.wrapper}>
      <div className={styles.toggle} data-mode={value}>
        <span className={styles.highlight} aria-hidden="true" />
        <button
          type="button"
          className={`${styles.option} ${value === 'light' ? styles.optionActive : ''}`}
          onClick={() => onChange('light')}
          aria-pressed={value === 'light'}
          disabled={disabled || value === 'light'}
        >
          Light
        </button>
        <button
          type="button"
          className={`${styles.option} ${value === 'dark' ? styles.optionActive : ''}`}
          onClick={() => onChange('dark')}
          aria-pressed={value === 'dark'}
          disabled={disabled || value === 'dark'}
        >
          Dark
        </button>
      </div>
    </div>
  );
};

export default ThemeToggle;
