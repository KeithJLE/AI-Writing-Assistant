import styles from "./StyleCard.module.css";

const statusLabel = (state, isActive, hasContent, isError) => {
  if (isError) {
    return "Error";
  }
  
  if (state === "processing") {
    if (isActive) {
      return "Streaming";
    }
    return hasContent ? "Ready" : "Pending";
  }

  if (state === "canceled") {
    return hasContent ? "Ready" : "Canceled";
  }

  if (state === "done") {
    return "Ready";
  }

  return "Idle";
};

const StyleCard = ({ style, label, helper, content, isActive, state }) => {
  const hasText = content.trim().length > 0;
  const isError = hasText && content.includes("Content blocked due to security concerns");
  const status = statusLabel(state, isActive, hasText, isError);

  return (
    <article
      className={styles.card}
      data-style={style}
      data-state={state}
      data-active={isActive}>
      <header className={styles.header}>
        <div>
          <h3 className={styles.title}>{label}</h3>
          <p className={styles.helper}>{helper}</p>
        </div>
        <span className={styles.badge} data-status={status.toLowerCase()}>
          {status}
        </span>
      </header>
      <div className={styles.body}>
        {hasText ? (
          <p className={`${styles.output} ${isError ? styles.error : ''}`}>{content}</p>
        ) : (
          <p className={styles.placeholder} data-loading={state === 'processing'}>
            {state === 'idle' 
              ? 'Ready to process your text.' 
              : state === 'processing' 
                ? 'Waiting for OpenAI response...' 
                : state === 'canceled'
                  ? 'Processing was canceled.'
                  : 'No content yet.'}
          </p>
        )}
      </div>
    </article>
  );
};

export default StyleCard;
