import styles from './PromptForm.module.css';

const STATUS_COPY = {
  idle: 'Ready to rephrase your writing.',
  processing: 'Streaming rephrased versions from OpenAI...',
  done: 'Rephrase complete. Adjust your input and try again.',
  canceled: 'Streaming canceled. You can resume with a fresh prompt.',
};

const PromptForm = ({
  value,
  onChange,
  onSubmit,
  onCancel,
  isProcessing,
  state,
  maxLength = 600,
}) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    if (!value.trim() || isProcessing) {
      return;
    }

    onSubmit(value.trim());
  };

  const remaining = maxLength - value.length;
  const showCounter = maxLength > 0;

  return (
    <form className={styles.wrapper} onSubmit={handleSubmit}>
      <label className={styles.label} htmlFor="prompt">
        Enter the text you want rephrased
      </label>
      <textarea
        id="prompt"
        name="prompt"
        className={styles.area}
        placeholder="Paste your copy here. We will stream four rephrased versions in real-time."
        value={value}
        onChange={(event) => onChange(event.target.value)}
        maxLength={maxLength}
        disabled={isProcessing}
        rows={6}
        spellCheck
      />
      <div className={styles.controlBar}>
        <div className={styles.statusGroup}>
          <span className={styles.statusDot} aria-hidden="true" data-state={state} />
          <p className={styles.statusText}>{STATUS_COPY[state]}</p>
        </div>
        <div className={styles.actionGroup}>
          {showCounter ? (
            <span className={styles.counter} data-warning={remaining < 40}>
              {remaining} characters left
            </span>
          ) : null}
          <button
            type="button"
            className={styles.secondaryButton}
            onClick={onCancel}
            disabled={!isProcessing}
          >
            Cancel
          </button>
          <button type="submit" className={styles.primaryButton} disabled={isProcessing || !value.trim()}>
            {isProcessing ? 'Streaming...' : 'Process'}
          </button>
        </div>
      </div>
    </form>
  );
};

export default PromptForm;
