type PageIntroProps = {
  title: string;
  description: string;
  actionLabel?: string;
  actionNote?: string;
  onActionClick?: () => void;
};

export function PageIntro({ title, description, actionLabel, actionNote, onActionClick }: PageIntroProps) {
  return (
    <header className="page-header">
      <div>
        <h1 className="page-title">{title}</h1>
        <p className="muted">{description}</p>
      </div>
      {actionLabel ? (
        <div className="page-actions">
          <button className="button primary" type="button" onClick={onActionClick}>
            {actionLabel}
          </button>
          {actionNote ? <span className="helper-note">{actionNote}</span> : null}
        </div>
      ) : null}
    </header>
  );
}
