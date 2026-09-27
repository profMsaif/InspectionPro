type ErrorStateProps = {
  message: string;
};

export function ErrorState({ message }: ErrorStateProps) {
  return (
    <div className="page-card glass-card">
      <p className="error-text">{message}</p>
    </div>
  );
}

